import sys
sys.path.append(__file__.rsplit("\\", 2)[0])

from mysql_manager import MysqlManager
from dict_format import EmployeeBody, ResultBody
from utils import db_config_debug, parser

mysql_manager = MysqlManager(**db_config_debug)

id = 10000
db_name = parser.parse_args().employee_db
table_name = parser.parse_args().employee_info
result = mysql_manager.query_fields(db_name, table_name, EmployeeBody.GetQueryFieldsList(), {"id" : f"= {id}"})
print(result)