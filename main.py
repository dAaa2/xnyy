from flask import *
import os
# from flask_login import LoginManager, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# import microexp.test as micro_ext_test
import json
import jwt
import datetime
import uuid
import subprocess
import shutil
import sys
from utils import logger
import uuid
# import microexp_processing
# import mr_processing

import random
from mysql_manager import MysqlManager
from dict_format import EmployeeBody, ResultBody, PatientBody, DiagnosisBody
from utils import db_config_debug, parser, md5_encrypt, check_is_valid, generate_unique_filename

mysql_manager = MysqlManager(**db_config_debug)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 生成24字节的随机密钥
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'gz'}
# UPLOAD_FOLDER = 'uploads'
# if not os.path.isdir(UPLOAD_FOLDER):
#     os.mkdir(UPLOAD_FOLDER)


# app.secret_key = 'secret!'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def cur_function_name() -> str:
    return sys._getframe(1).f_code.co_name if sys._getframe(1) else "<unknown>"

#判断传入文件的格式是否符合要求
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_image_path(line):
    start_idx = line.find('(') + 1
    end_idx = line.rfind(')')
    path = line[start_idx:end_idx]
    return path

# 判断是否可以登录
@app.route('/employee/login', methods=['POST'])
def login():
    #获取用户名和密码
    response_data = make_response()
    form = request.get_json()
    user_name = form.get("userName")
    user_name = form.get("userName")
    user_password = form.get("password")
    # user_password = md5_encrypt(user_password)
    # 验证输入
    # if not user_name or not user_password:
    #     return jsonify(ResultBody(400, msg="用户名和密码必填").to_dict()), 400

    # 通过用户名查询用户
    user_data = mysql_manager.query_fields(parser.parse_known_args()[0].employee_db,
                                              parser.parse_known_args()[0].employee_info,
                                              ["id", "password", "name", "userName", "phone", "role"],
                                              {"username" : f"= '{user_name}'"})
    if user_data == []:
        logger.info(f"{cur_function_name()}  用户不存在，登录失败")
        return jsonify(ResultBody(401, msg="用户不存在").to_dict()), 401

    # 验证密码
    if not user_data[0][1]==user_password:
        logger.info(f"{cur_function_name()}  密码错误，登录失败")
        return jsonify(ResultBody(401, msg="密码错误").to_dict()), 401

    # 生成JWT Token
    token = jwt.encode({
        'user_id': user_data[0][0],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8) #8小时后过期
    }, app.config['SECRET_KEY'], algorithm='HS256')

    response_data = ResultBody(1)
    response_data.data = {
        'id': user_data[0][0],
        'name': user_data[0][2],
        'userName': user_data[0][3],
        'phone': user_data[0][4],
        'role': user_data[0][5],
        'token': token
    }
    
    logger.info(f"{cur_function_name()}  用户：{user_data[0][0]} 姓名{user_data[0][2]}登录成功")
    return jsonify(response_data.to_dict())


@app.route('/employee/logout', methods=['post'])
def logout():
    data = {"code" : 1}
    data.update({"data":None, "msg":None})
    data = json.dumps(data)
    logger.info(f"{cur_function_name()}  用户登出")
    return data

#分页查询
@app.route('/employee/page', methods=['POST'])
def employee_getinfo_by_page():
    form = request.get_json()
    name = form.get("name")
    page = form.get("page")
    page_size = form.get("pageSize")
    start_idx = (page - 1) * page_size
    end_idx = page * page_size
    
    db_name = parser.parse_known_args()[0].employee_db
    table_name = parser.parse_known_args()[0].employee_info
    
    result = mysql_manager.query_fields(db_name, table_name, EmployeeBody.GetQueryFieldsList(), \
        {"name" : f"LIKE '%{name if name else str()}%'"})
    response_data = make_response()
    
    if result == [] or len(result) < start_idx + 1:
         return jsonify(ResultBody(9, msg = "未查询到用户").to_dict()) 
    
    if end_idx > len(result):
        end_idx = len(result)
    response_data = ResultBody(1)
    records = [(EmployeeBody(*result[i][1:]).GetAsDict()) for i in range(start_idx, end_idx)]
    for i in range(len(records)):
        records[i].update({"id" : result[i + start_idx][0]})
    response_data.data = {"total" : len(result), "records" : records}
    logger.info(f"{cur_function_name()} 第{page}页查询到{end_idx - start_idx}条数据")
    return jsonify(response_data.to_dict())

#用户注册
@app.route('/employee/register', methods=['POST'])
def employee_register():
    response_data = make_response()
    form = request.get_json()
    username = form.get("userName")
    name = form.get("name")
    password = form.get("password")
    phone = form.get("phone")
    role = "user"
    valid = check_is_valid(username, name, password, phone)
    if valid[0]:
        password = md5_encrypt(password)
    else:
        msg = "参数不全"
        response_data = ResultBody(0, msg=msg)
    body = EmployeeBody(username, name, password, phone, role).GetAsDict()
    # db_name = parser.parse_args().employee_db
    # table_name = parser.parse_args().employee_info
    # 参数和flask run冲突，所以修改了
    db_name = parser.parse_known_args()[0].employee_db
    table_name = parser.parse_known_args()[0].employee_info

    result = mysql_manager.insert_data(db_name, table_name, body)

    msg = "注册失败" if not result else "注册成功"
    response_data = ResultBody(int(result), msg = msg)

    logger.info(f"用户:{username} ，名字:{name}, {msg}")
    
    return jsonify(response_data.to_dict())

@app.route('/employee/<id>', methods=['POST'])
def employee_query_by_id(id):
    form = request.get_json()
    id = form.get("id")
    db_name = parser.parse_args().employee_db
    table_name = parser.parse_args().employee_info
    result = mysql_manager.query_fields(db_name, table_name, EmployeeBody.GetQueryFieldsList(), {"id" : f"= {id}"})
    
    response_data = make_response()
    response_data = ResultBody(int(result != []))
    msg = "查询成功" if result != [] else "查询失败"
    data = {"id" : id}
    data.update(EmployeeBody(*result[0][1:]).GetAsDict())
    response_data.data = data
    response_data.msg = msg
    logger.info(f"{cur_function_name()}  查询用户: {id} {msg}")
    
    return jsonify(response_data.to_dict())

@app.route('/employee', methods=['PUT'])
def employee_edit_info():
    form = request.get_json()
    id = form.get("id")
    username = form.get("userName")
    name = form.get("name")
    password = md5_encrypt(form.get("password"))
    phone = form.get("phone")
    role = form.get("role")
    
    body = EmployeeBody(username, name, password, phone, role).GetAsDict()
    db_name = parser.parse_args().employee_db
    table_name = parser.parse_args().employee_info
    
    result = mysql_manager.update_data(db_name, table_name, "id", id, body)
    msg = "修改成功" if result else "修改失败"
    response_data = make_response()
    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()}  修改用户: {id} {msg}")

    return jsonify(response_data.to_dict())

@app.route('/employee/editPassword', methods=['PUT'])
def employee_edit_password():
    form = request.get_json()
    id = form.get("id")

    # old_password = md5_encrypt(form.get("oldPassword"))
    # new_password = md5_encrypt(form.get("newPassword"))

    old_password = form.get("oldPassword")
    new_password = form.get("newPassword")
    response_data = make_response()
    
    db_name = parser.parse_args().employee_db
    table_name = parser.parse_args().employee_info
    
    result = mysql_manager.query_fields(db_name, table_name, ["password"], {"id" : f"= {id}"})
    if result == [] or old_password != result[0][0]:
        response_data = ResultBody(0)
        return jsonify(response_data.to_dict())
        
    result = mysql_manager.update_data(db_name, table_name, "id", id, {"password" : new_password})
    msg = "修改成功" if result else "修改失败"
    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()}  修改用户: {id} {msg}")
    return jsonify(response_data.to_dict())
    
@app.route('/employee/<id>', methods=['DELETE'])
def employee_delete_user(id):
    response_data = make_response()
    if not check_is_valid(id)[0]:
        response_data = ResultBody(0, msg="无效的id")
        return jsonify(response_data.to_dict())
    db_name = parser.parse_args().employee_db
    table_name = parser.parse_args().employee_info
    
    result = mysql_manager.delete_data(db_name, table_name, "id", id)
    msg = "删除成功" if result else "删除失败"

    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()}  删除用户: {id} {msg}")
    
    return jsonify(response_data.to_dict())

#用户注册
@app.route('/employee', methods=['POST'])
def employee_add():
    response_data = make_response()
    form = request.get_json()
    username = form.get("userName")
    name = form.get("name")
    password = form.get("password")
    phone = form.get("phone")
    role = form.get("role")
    valid = check_is_valid(username, name, password, phone)
    if valid[0]:
        password = md5_encrypt(password)
    else:
        msg = "参数不全"
        response_data = ResultBody(0, msg=msg)
    body = EmployeeBody(username, name, password, phone, role).GetAsDict()
    # db_name = parser.parse_args().employee_db
    # table_name = parser.parse_args().employee_info
    # 参数和flask run冲突，所以修改了
    db_name = parser.parse_known_args()[0].employee_db
    table_name = parser.parse_known_args()[0].employee_info

    result = mysql_manager.insert_data(db_name, table_name, body)

    msg = "注册失败" if not result else "注册成功"
    response_data = ResultBody(int(result), msg = msg)

    logger.info(f"用户:{username} ，名字:{name}, {msg}")

    return jsonify(response_data.to_dict())

#患者分页查询
@app.route('/patient/page', methods=['POST'])
def patient_getinfo_by_page():
    form = request.get_json()
    patient_id = form.get("patientId")
    name = form.get("name")
    page = form.get("page")
    page_size = form.get("pageSize")
    start_idx = (page - 1) * page_size
    end_idx = page * page_size
    
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_info
    
    result = mysql_manager.query_fields(db_name, table_name, PatientBody.GetQueryFieldsList(), \
        {"name" : f"LIKE '%{name if name else str()}%'", "patientId" : f"LIKE '%{patient_id if patient_id else str()}%'"})
    response_data = make_response()
    
    if result == [] or len(result) < start_idx + 1:
         return jsonify(ResultBody(9, msg = "未查询到用户").to_dict()) 
    
    if end_idx > len(result):
        end_idx = len(result)
    response_data = ResultBody(1)
    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = [PatientBody(*result[i][1:]).GetAsDict() for i in range(start_idx, end_idx)]
    for i in range(len(records)):
        records[i].update({"id" : result[i + start_idx][0], "updateTime" : update_time})
    response_data.data = {"total" : len(result), "records" : records}
    
    logger.info(f"{cur_function_name()} 第{page}页查询到{end_idx - start_idx}条数据")

    return jsonify(response_data.to_dict())

@app.route('/patient/upload', methods=['POST'])
def patient_image_upload():
    id = request.form.get("id")
    diagnosis_type = request.form.get("diagnosisType")
    image = request.files["file"]
    if not image or not allowed_file(image.filename):
        return jsonify(ResultBody(400, msg="无效文件类型").to_dict()), 400
    
    # 保存原始文件
    response_data = make_response()
    original_filename = generate_unique_filename(image.filename)
    original_filepath = os.path.join(".", app.config['UPLOAD_FOLDER'])
    original_filepath = os.path.join(original_filepath, original_filename)
    print(original_filepath)
    image.save(original_filepath)
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_info
    result = mysql_manager.query_fields(db_name, table_name, ['id'], {"id" : f"= {id}"})
    if result == []:
        response_data = ResultBody(0, msg="无效的id")
    table_name = parser.parse_args().patient_diagnosis
    download_url = url_for('download_file', filename = original_filename, _external = True)

    result = mysql_manager.insert_data(db_name, table_name, DiagnosisBody(download_url, id, diagnosis_type).GetAsDict())
    
    msg = "上传成功" if result else "上传失败"
    response_data = ResultBody(int(result))
    response_data.msg = msg
    if result:
        response_data.data = {"url" : download_url}
    logger.info(f"{cur_function_name()}  用户: {id} {msg}")
    return jsonify(response_data.to_dict())

#获取图片 
@app.route('/patient/<id>', methods=['POST'])
def patient_query_by_id(id):
    # form = request.get_json()
    # id = form.get("id")
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_info
    id = int(id)
    result_patient_info = mysql_manager.query_fields(db_name, table_name, PatientBody.GetQueryFieldsList(), {"id" : f"= {id}"})
    
    table_name = parser.parse_args().patient_diagnosis
    result_image_list = mysql_manager.query_fields(db_name, table_name, ["image_path"], {"id" : f"= '{id}'"})
    
    response_data = make_response()
    response_data = ResultBody(int(result_patient_info != []))
    data = {"id" : id}
    if result_patient_info != []:
        data.update(PatientBody(*(result_patient_info[0][1:])).GetAsDict())
    if result_image_list:
        data.update({"imageList" : [image[0] for image in result_image_list]})
    response_data.data = data
    return jsonify(response_data.to_dict())

#图片删除依据图片的地址
@app.route('/patient/deleteImage', methods=['DELETE'])
def patient_diagnosis_delete_image():
    form = request.get_json()
    image_path = form.get("imageUrl")

    id = form.get("id")
    
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_diagnosis
    
    response_data = make_response()
    response_data = ResultBody(0)
    
    result = mysql_manager.delete_data(db_name, table_name, "image_path", image_path)

    image_path = os.sep.join(image_path.rsplit("\\", 2)[1:])

    if result and os.path.exists(image_path):
        os.remove(image_path)

    msg = "删除成功" if result else "删除失败"
    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()}  患者: {id} {msg}")
    
    return jsonify(response_data.to_dict())

#批量删除患者
@app.route('/patient', methods=['DELETE'])
def patients_delete():
    form = request.get_json()
    ids = form.get("ids")
    if type(ids) is str:
        ids = ids.split(",")
    elif type(ids) is int:
        ids = [ids]
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_info
    
    response_data = make_response()
    response_data = ResultBody(0)
    result = 1
    
    for id in ids:
        result &= mysql_manager.delete_data(db_name, table_name, "id", int(id))
    msg = "删除成功" if result else "删除失败"
    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()} 批量{msg}")
    
    return jsonify(response_data.to_dict())


@app.route('/patient', methods=['PUT'])
def patient_edit_info():
    form = request.get_json()
    id = form.get("id")
    patient_id = form.get("patientId")
    name = form.get("name")
    sex = form.get("sex")
    age = form.get("age")
    description = form.get("description")
    
    body = PatientBody(patient_id, name, sex, age, description).GetAsDict()
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_info
    
    result = mysql_manager.update_data(db_name, table_name, "id", id, body)
    
    response_data = make_response()
    msg = "修改成功" if result else "修改失败"
    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()} 患者：{id} {msg}")
    return jsonify(response_data.to_dict())

@app.route('/patient', methods=['POST'])
def patient_add():
    form = request.get_json()
    patient_id = form.get("patientId")
    name = form.get("name")
    sex = form.get("sex")
    age = form.get("age")
    description = form.get("description")
    
    body = PatientBody(patient_id, name, sex, age, description).GetAsDict()
    db_name = parser.parse_args().patient_db
    table_name = parser.parse_args().patient_info
    
    result = mysql_manager.insert_data(db_name, table_name, body)

    response_data = make_response()
    msg = "添加成功" if result else "添加失败"
    response_data = ResultBody(int(result))
    response_data.msg = msg
    logger.info(f"{cur_function_name()} 患者：{name} {msg}")
    return jsonify(response_data.to_dict())

#测试返回类型，返回一个可以在前端下载图片的地址
@app.route('/algorithm', methods=['GET', 'POST'])
def upload_file():
    #判断传入数据是否合法：
    if 'file' not in request.files or 'algo' not in request.form:
        return jsonify(ResultBody(400, msg="缺少文件或算法参数").to_dict()), 400

    file = request.files['file']
    algo = request.form['algo']

    # 保存原始文件
    original_filename = secure_filename(file.filename)
    original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    file.save(original_filepath)

    # 处理文件
    if algo == "micro_exp":
        # 生成保存结果的文件名
        save_filename = f"{uuid.uuid4()}_processed.{original_filename.rsplit('.', 1)[1]}"
        save_filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_filename)

        # 构造命令行调用
        exe_path = "/home/ff/CZW/xnyy/microexp/detection/predict"

        # 假设 final_predict.exe 支持两个参数：img1 和 img2
        cmd = [
            exe_path,
            "--video", original_filepath,
            "--weights", "/home/ff/CZW/xnyy/microexp/detection/s1.hdf5"
        ]

        # 执行外部程序
        result = subprocess.run(
            cmd,
            capture_output=True,  # 捕获 stdout 和 stderr
            encoding='utf-8',  # 设置编码格式
            errors='replace'  # 防止乱码
        )

        # 解析输出
        # 获取标准输出的所有行
        stdout_lines = result.stdout.strip().split('\n')

        # 只取最后两行
        last_two_lines = stdout_lines[-2:] if len(stdout_lines) >= 2 else stdout_lines

        onset_path, apex_path = None, None

        if len(last_two_lines) >= 2:
            onset_line, apex_line = last_two_lines

            onset_path = extract_image_path(onset_line)  # tmp_frames\xx\img23.jpg
            apex_path = extract_image_path(apex_line)  # tmp_frames\xx\img31.jpg

        print("Onset Path: ", onset_path)
        print("Apex Path: ", apex_path)

        exe_path = "/home/ff/CZW/xnyy/microexp/identify/final_predict"

        cmd = [
            exe_path,
            onset_path,
            apex_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,  # 捕获 stdout 和 stderr
            encoding='utf-8',  # 设置编码格式
            errors='replace'  # 防止乱码
        )

        # 提取 output image path
        for line in result.stdout.strip().split('\n'):
            if line.startswith('output image path:'):
                output_image_path = line.split(':', 1)[1].strip()
                break
            else:
                output_image_path = None

        if output_image_path:
            # 提取文件名
            output_filename = os.path.basename(output_image_path)

            # 将文件复制到 uploads 目录
            shutil.copy(output_image_path, os.path.join(app.config['UPLOAD_FOLDER'], output_filename))

            # 构造正确的 download_url
            download_url = url_for('download_file', filename=output_filename, _external=True)

            return jsonify(ResultBody(200, data={'download_url': download_url}).to_dict())
        else:
            return jsonify(ResultBody(500, msg="无法解析输出图像路径").to_dict()), 500


    elif algo in ("mr1", "mr2"):
        # 确保上传的是图片
        if not allowed_file(file.filename):
            return jsonify(ResultBody(400, msg="无效的图片格式").to_dict()), 400

        # 创建临时目录
        unique_id = f"{random.randint(0, 9999):04d}"
        input_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'input', unique_id)
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output', unique_id)

        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # 保存原始图像到 input_dir
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1]
        input_image_path = os.path.join(input_dir, f"brain_{unique_id}.nii.{file_extension}")
        file.save(input_image_path)

        # 构造算法命令行（假设是 Python 脚本）
        script_path = "/home/ff/CZW/xnyy/mr/nnUNet/predicet_braints.py"  # 替换为你的实际脚本路径
        cmd = [
            sys.executable,  # 使用当前 Python 解释器
            script_path,
            "--input", input_dir,
            "--output", output_dir
        ]

        # 执行算法
        result = subprocess.run(
            cmd,
            capture_output=True,
            encoding='utf-8',
            errors='replace'
        )

        print(result)

        # result = predicet_braints.predict_segmentation(
        #     input_image_dir=input_dir,  # 输入图像目录
        # )

        if result.returncode != 0:
            return jsonify(ResultBody(500, msg="算法执行失败", data={"error": result.stderr}).to_dict()), 500

        # 获取输出图片路径（假设输出两张图）
        output_files = sorted(os.listdir(output_dir))
        if len(output_files) < 2:
            return jsonify(ResultBody(500, msg="算法未生成足够的输出图像").to_dict()), 500

        output1_path = os.path.join(output_dir, output_files[0])
        output2_path = os.path.join(output_dir, output_files[1])

        # 构造 download_url（第一张图）
        output1_filename = os.path.basename(output1_path)
        download_url = url_for('download_file', filename=os.path.join(unique_id, output1_filename), _external=True)

        # 第二张图存入数据库
        db_name = parser.parse_args().patient_db
        table_name = parser.parse_args().patient_diagnosis

        diagnosis_data = DiagnosisBody(image_path=output2_path, patient_id=id, diagnosis_type=algo).GetAsDict()
        insert_result = mysql_manager.insert_data(db_name, table_name, diagnosis_data)

        if not insert_result:
            return jsonify(ResultBody(500, msg="写入数据库失败").to_dict()), 500

        return jsonify(ResultBody(200, data={'download_url': download_url}).to_dict())
    else:
        return jsonify(ResultBody(400, msg="未知算法").to_dict()), 400

#拿到前端返回的图片
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port="5000", threaded=False)