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
            "userName" : self.username,
            "name" : self.name,
            "phone" : self.phone,
            "password" : self.password,
            "role" : self.role
        }
        return ret
    
    def GetQueryFieldsList() -> list:
        return ["id", "userName", "name", "password", "phone", "role"]

class PatientBody:
    def __init__(self, patient_id, name, sex, age, description = None):
        self.patient_id = patient_id
        self.name = name
        self.sex = sex
        self.age = age
        self.description = description
    
    def GetAsDict(self) -> dict:
        ret = {
            "patientId" : self.patient_id,
            "name" : self.name,
            "sex" : self.sex,
            "age" : self.age,
            "description" : self.description
        }
        return ret

    def GetQueryFieldsList() -> list:
        return ["id", "patientId" ,"name", "sex", "age", "description"]
   
class DiagnosisBody:
    def __init__(self, image_path, id, diagnosis_type = None):
        self.image_path = image_path
        self.id = id
        self.diagnosis_type = diagnosis_type    
    def GetAsDict(self) -> dict:
        ret = {
            "image_path" : self.image_path,
            "id" : self.id,
            "diagnosis_type" : self.diagnosis_type,
        }
        return ret
    
    def GetQueryFieldsList() -> list:
        return ["image_path", "id", "diagnosis_type"]
        
class ResultBody:
    def __init__(self, code, data=None, msg=None):
        self.code = code
        self.data = data or {}
        self.msg = msg or (f"Code {code} 错误" if code not in [200, True, 1] else None)

    def to_dict(self):
        return {
            'code': self.code,
            'data': self.data,
            'msg': self.msg
        }