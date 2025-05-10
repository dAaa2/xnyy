import sys
sys.path.append(__file__.rsplit("\\", 2)[0])

from mysql_manager import MysqlManager

employee_db = "employee"
employee_info = "employee_info"

db_config = {
    'host': 'localhost',
    'user': 'root',  # mysql用户，未更改默认为root
    'password': '629629',  # mysql连接密码，自己设置的
    'pool_name': 'connection_pool', #连接池名字
    'pool_size': 5 #连接池大小
}

employee_info_columns = {
    "id" : "INT AUTO_INCREMENT PRIMARY KEY",
    "username" : "VARCHAR(20) UNIQUE NOT NULL",
    "name" : "VARCHAR(20) NOT NULL",
    "password" : "VARCHAR(100)",
    "phone" : "VARCHAR(50)",
    "role" : "VARCHAR(10) NOT NULL"
}

patient_db = "patient"
patient_info = "patient_info"
patient_diagnosis = "patient_diagnosis"

patient_info_columns = {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "patient_id" : "VARCHAR(20) UNIQUE NOT NULL",
            "name": "VARCHAR(20) NOT NULL",
            "sex": "ENUM('Male', 'Female', 'Other')",
            "age": "INT",
            "description": "TEXT"
        }

diagnosis_columns = {
            "image_path": "VARCHAR(255) PRIMARY KEY",
            "image_index" : "VARCHAR(50)",
            "id": "INT",
            "name": "VARCHAR(20) NOT NULL",
            "diagnosis_type":"VARCHAR(20) NOT NULL"
        }

data1 = {
    "username" : "VARCHAR(20) NOT NULL",
    "name" : "VARCHAR(20) NOT NULL",
    "password" : "VARCHAR(100)",
    "phone" : "VARCHAR(50)",
    "role" : "m"
}

mysql_manager = MysqlManager(**db_config)

mysql_manager.create_database(patient_db)
mysql_manager.create_table(patient_db, patient_info,patient_info_columns)
mysql_manager.create_table(patient_db, patient_diagnosis, diagnosis_columns)
mysql_manager.SetAutoIncrement(patient_db, patient_info)


mysql_manager.create_database(employee_db)
mysql_manager.create_table(employee_db, employee_info,employee_info_columns)
mysql_manager.SetAutoIncrement(employee_db, employee_info)

mysql_manager.insert_data(employee_db, employee_info, data1)