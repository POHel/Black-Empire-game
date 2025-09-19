import time
import coreLogic
import sqlite3
from coreLogic import AppLogic, ExportDB, UpdateDB, Settings
logic = AppLogic()
export = ExportDB()
update = UpdateDB
setting = Settings()

#print(export.get_actives())
#print(setting.get_current_fps())
#print(setting.set_current_fps(30))
#print(setting.get_current_fps)
#export.get_actives()
print('start')
"""
connect = sqlite3.connect("data/invest.db")
cursor = connect.cursor()
cursor.execute('SELECT name_actives FROM actives')
result = [row[0] for row in cursor.fetchall()]
print(result)
connect.close()
"""
export.get_actives()
print('end')