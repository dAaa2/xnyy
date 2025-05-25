import sys
sys.path.append(__file__.rsplit("\\", 2)[0])


from mysql_manager import MysqlManager

db_config = {
    'host': 'localhost',
    'user': 'root',  # mysql用户，未更改默认为root
    'password': '12345678',  # mysql连接密码，自己设置的
    'pool_name': 'connection_pool', #连接池名字
    'pool_size': 5 #连接池大小
}

manager = MysqlManager(**db_config)

# 创建数据库样例
db_name = "school"
manager.drop_database(db_name)
manager.create_database(db_name)

# 创建表样例
table_name = "students"
columns = {
    "id": "INT AUTO_INCREMENT PRIMARY KEY",
    "name": "VARCHAR(255) NOT NULL",
    "age": "INT"
}
manager.create_table(db_name, table_name, columns)

# 插入单条数据
single_data = {"name": "张三", "age": 20}
manager.insert_data(db_name, table_name, single_data)

# 插入多条数据
multiple_data = [
    {"name": "李四", "age": 22},
    {"name": "王五", "age": 19}
]
manager.insert_data(db_name, table_name, multiple_data)

# 查询单个字段
ret = manager.query_fields(db_name, table_name, ["name"])

# 查询多个字段，带条件
ret = manager.query_fields(db_name, table_name, ["name"], {"name": "= '张三'"})
for iter in ret:
    print(iter)
    
