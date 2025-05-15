from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from utils import logger
'''
封装Mysql数据库管理类，提供以下接口：
数据库创建：         create_database(bd_name:str) 
创建表：             create_table(self, db_name:str, table_name:str, columns:dict)
数据查询：           query_fields(self, db_name:str, table_name:str, fields:list, conditions:dict=None)
                    param:      fields: 列表，要查询的字段，如 ["name", "age"]
                                conditions: 字典，查询条件，如 {"age": "> 20", "name": "= '张三'"}
数据插入:            insert_data(self, db_name, table_name, data)
                    param:      data: 字典或字典列表，如 {"name": "张三", "age": 20} 或 [{"name": "张三", "age": 20}, ...]
获取连接：           get_connection(self, database:str)
删除提供 删除数据库、表、某一字段、某一项
'''     
class MysqlManager:
    def __init__(self, host, user, password, pool_name="connection_pool", pool_size=5):
        self.pool = None
        self.host = host
        self.user = user
        self.password = password
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.init_pool()
        
    """初始化连接池"""
    def init_pool(self):
        try:
            pool_config = {
                "pool_name": self.pool_name,
                "pool_size": self.pool_size,
                "host": self.host,
                "user": self.user,
                "password": self.password,
                "database": None  # 初始无默认数据库
            }
            self.pool = MySQLConnectionPool(**pool_config)
            logger.info(f"连接池 {self.pool_name} 创建成功，池大小: {self.pool_size}")
        except Error as e:
            logger.error(f"创建连接池错误: {e}")
            raise
        
    """从连接池获取连接"""
    def get_connection(self, database:str=None):
        try:
            connection = self.pool.get_connection()
            if connection.is_connected():
                if database:
                    cursor = connection.cursor()
                    cursor.execute(f"USE {database}")
                    cursor.close()
                return connection
        except Error as e:
            logger.error(f"获取连接错误: {e}")
        return None

    def create_database(self, db_name:str):
        """创建数据库"""
        connection = self.get_connection()
        if not connection:
            return False
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            logger.info(f"数据库 {db_name} 创建成功或已存在")
            self.pool.set_config(database=db_name)  # 更新连接池配置
            return True
        except Error as e:
            logger.error(f"创建数据库错误: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def create_table(self, db_name:str, table_name:str, columns:dict):
        connection = self.get_connection(db_name)
        if not connection:
            return False
        try:
            cursor = connection.cursor(prepared=True)
            # 构建字段定义
            column_definitions = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(column_definitions)}
            )
            """
            cursor.execute(create_table_query)
            logger.info(f"表 {db_name}.{table_name} 创建成功或已存在")
            return True
        except Error as e:
            logger.error(f"创建表错误: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def SetAutoIncrement(self, db_name:str, table_name:str, start:int=10000):
        connection = self.get_connection(db_name)
        if not connection:
            logger.info(f"设置起始值失败")
        try:
            cursor = connection.cursor(prepared=True)
            query = f"alter table {table_name} AUTO_INCREMENT={start}"
            cursor.execute(query)
            logger.info(f"表 {db_name}.{table_name} 设置起始主键为{start}")
            return True
        except Error as e:
            logger.error(f"创建表错误: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
            
    def query_fields(self, db_name:str, table_name:str, fields:list, conditions=None):
        connection = self.get_connection(db_name)
        if not connection:
            return []
        try:
            cursor = connection.cursor(prepared=True)
            # 构建查询字段
            fields_str = ", ".join(fields)
            query = f"SELECT {fields_str} FROM {table_name}"
            
            # 构建条件
            params = []
            if conditions:
                condition_clauses = []
                for key, value in conditions.items():
                    if value.startswith((">", "<", ">=", "<=", "!=", "=", "LIKE")):
                        condition_clauses.append(f"{key} {value}")
                    else:
                        condition_clauses.append(f"{key} = %s")
                        params.append(value)
                if condition_clauses:
                    query += " WHERE " + " AND ".join(condition_clauses)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            if results:
                logger.info(f"查询到 {len(results)} 条记录:")
            else:
                logger.info("没有查询到记录")
            return results
        except Error as e:
            logger.error(f"查询错误: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    '''插入数据'''
    def insert_data(self, db_name:str, table_name:str, data):
        connection = self.get_connection(db_name)
        if not connection:
            return False
        try:
            cursor = connection.cursor(prepared=True)
            # 统一处理单条和多条数据
            data_list = [data] if isinstance(data, dict) else data
            if not data_list:
                logger.info("没有提供数据")
                return False

            # 获取字段名
            fields = list(data_list[0].keys())
            fields_str = ", ".join(fields)
            placeholders = ", ".join(["%s"] * len(fields))
            insert_query = f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"

            # 插入数据
            for item in data_list:
                values = [item[field] for field in fields]
                cursor.execute(insert_query, values)
            connection.commit()
            logger.info(f"成功插入 {len(data_list)} 条数据到 {db_name}.{table_name}")
            return True
        except Error as e:
            logger.error(f"插入错误: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
         
    '''更新数据'''
    def update_data(self, db_name:str, table_name:str, key_field:str, key_value, update_data:dict):
        connection = self.get_connection(db_name)
        if not connection:
            logger.error(f"无法更新数据到 {db_name}.{table_name}: 无有效连接")
            return False
        try:
            cursor = connection.cursor(prepared=True)
            if not update_data:
                logger.info("没有提供更新数据")
                return False
            # 构建 SET 子句
            set_clauses = [f"{field} = %s" for field in update_data.keys()]
            set_clause = ", ".join(set_clauses)
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE {key_field} = %s"
            # 准备参数：更新值 + 主键值
            values = list(update_data.values()) + [key_value]
            cursor.execute(update_query, values)
            connection.commit()
            if cursor.rowcount > 0:
                logger.info(f"成功更新 {cursor.rowcount} 条记录在 {db_name}.{table_name}，{key_field} = {key_value}")
            else:
                logger.info(f"没有记录被更新在 {db_name}.{table_name}，{key_field} = {key_value}")
            return True
        except Error as e:
            logger.error(f"更新数据到 {db_name}.{table_name} 错误: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    """删除数据库"""
    def drop_database(self, db_name:str):
            connection = self.get_connection()
            if not connection:
                logger.error(f"无法删除数据库 {db_name}: 无有效连接")
                return False
            try:
                cursor = connection.cursor(prepared=True)
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                logger.info(f"数据库 {db_name} 删除成功或不存在")
                self.pool.set_config(database=None)  # 重置连接池配置
                return True
            except Error as e:
                logger.error(f"删除数据库 {db_name} 失败: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
                
    """删除表"""
    def drop_table(self, db_name:str, table_name:str):
        connection = self.get_connection(db_name)
        if not connection:
            logger.error(f"无法删除表 {db_name}.{table_name}: 无有效连接")
            return False
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            logger.info(f"表 {db_name}.{table_name} 删除成功或不存在")
            return True
        except Error as e:
            logger.error(f"删除表 {db_name}.{table_name} 失败: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    """删除表中的字段"""
    def drop_column(self, db_name:str, table_name:str, column_name:str):
        connection = self.get_connection(db_name)
        if not connection:
            logger.error(f"无法删除字段 {db_name}.{table_name}.{column_name}: 无有效连接")
            return False
        try:
            cursor = connection.cursor()
        
            if not column_name.isidentifier():
                logger.error(f"无效的字段名: {column_name}")
                return False
            drop_column_query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
            logger.debug(f"执行删除字段查询: {drop_column_query}")
            cursor.execute(drop_column_query)
            logger.info(f"字段 {db_name}.{table_name}.{column_name} 删除成功")
            return True
        except Error as e:
            logger.error(f"删除字段 {db_name}.{table_name}.{column_name} 失败: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
            
    """根据字段名和值删除记录"""
    def delete_data(self, db_name:str, table_name:str, field_name:str, field_value):
        connection = self.get_connection(db_name)
        if not connection:
            logger.error(f"无法删除数据从 {db_name}.{table_name}: 无有效连接")
            return False
        try:
            cursor = connection.cursor(prepared=True)
            delete_query = f"DELETE FROM {table_name} WHERE {field_name} = %s"
            logger.debug(f"执行删除查询: {delete_query}, 参数: [{field_value}]")
            cursor.execute(delete_query, [field_value])
            connection.commit()
            if cursor.rowcount > 0:
                logger.info(f"成功删除 {cursor.rowcount} 条记录从 {db_name}.{table_name}，字段 {field_name} = {field_value}")
            else:
                logger.info(f"没有记录被删除从 {db_name}.{table_name}，字段 {field_name} = {field_value}")
            return True
        except Error as e:
            logger.error(f"删除数据从 {db_name}.{table_name} 失败: {e}")
            return False
        finally:
            cursor.close()
            connection.close()