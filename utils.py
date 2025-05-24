import os
import logging
import argparse
import hashlib
import sys

base_path = os.path.abspath(__file__).rsplit('/', 1)[0]
print(base_path)
log_file = os.path.join(base_path, "xnyy_server_log.log")
logger = logging.getLogger("system logger")
if not logger.handlers:  
            logger.setLevel(logging.INFO)  
            # 控制台处理器
            if 0:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)
            # 文件处理器
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            

parser = argparse.ArgumentParser(description="Global Setting")
parser.add_argument('--employee_db', type=str,  help='user datadb name', default="employee")
parser.add_argument('--employee_info', type=str,  help='user datadb name', default="employee_info")
parser.add_argument('--patient_db', type=str,  help='patient information', default="patient")
parser.add_argument('--patient_info', type=str,  help='patient information', default="patient_info")
parser.add_argument('--patient_diagnosis', type=str,  help='patient diagnosis results', default="patient_diagnosis")
parser.add_argument('--port', type=int,  help='flask port', default=5000)

db_config_debug = {
    'host': '10.17.242.16',
    'user': 'linux_remote',  # mysql用户，未更改默认为root
    'password': '123456',  # mysql连接密码，自己设置的
    'pool_name': 'connection_pool', #连接池名字
    'pool_size': 5 #连接池大小
}

def md5_encrypt(text: str) -> str:
    bytes_text = text.encode('utf-8')
    md5_obj = hashlib.md5()
    md5_obj.update(bytes_text)
    return md5_obj.hexdigest()

def check_is_valid(*values) -> tuple[bool, list[int]]:
    invalid_indices = [i for i, value in enumerate(values) if value is None]
    return (len(invalid_indices) == 0, invalid_indices)

