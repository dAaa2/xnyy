from utils import md5_encrypt
class EmployeeBody:
    def __init__(self, username=None, name=None, password=None, phone=None, role=None):
        self.username = username
        self.name = name
        self.phone = phone
        self.password = password
        self.role = role
    
    def GetAsDict(self) -> dict:
        ret = {
            "username" : self.username,
            "name" : self.name,
            "phone" : self.phone,
            "password" : self.password,
            "role" : self.role
        }
        return ret
    
    def GetQueryFieldsList() -> list:
        return ["id", "username", "name", "password", "phone", "role"]

class PatientBody:
    def __init__(self, name, sex, age, description):
        self.name = name
        self.sex = sex
        self.age = age
        self.description = description
    
    def GetAsDict(self) -> dict:
        ret = {
            "name" : self.name,
            "sex" : self.sex,
            "age" : self.age,
            "description" : self.description
        }
        return ret

    def GetQueryFieldsList() -> list:
        return ["id", "name", "age", "description"]
   
class DiagnosisBody:
    def __init__(self, image_path, image_index, id, name, diagnosis_type):
        self.image_path = image_path
        self.image_index = image_index
        self.id = id
        self.name = name
        self.diagnosis_type = diagnosis_type    
    def GetAsDict(self) -> dict:
        ret = {
            "image_path" : self.image_path,
            "image_index" : self.image_index,
            "id" : self.id,
            "name" : self.name,
            "diagnosis_type" : self.diagnosis_type,
        }
        return ret
    
    def GetQueryFieldsList() -> list:
        return ["image_path", "iamge_index", "id", "name", "diagnosis_type"]
        
class ResultBody:
    def __init__(self, code, data=None, msg=None):
        self.code = code
        self.data = data or {}
        self.msg = msg or (f"Code {code} 错误" if code != 200 else None)

    def to_dict(self):
        return {
            'code': self.code,
            'data': self.data,
            'msg': self.msg
        }
