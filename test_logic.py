import time
import coreLogic
from coreLogic import AppLogic, ExportDB, UpdateDB, Settings
logic = AppLogic()
export = ExportDB()
update = UpdateDB
setting = Settings()
#print(export.get_actives())
#print(setting.get_current_fps())
#print(setting.set_current_fps(30))
#print(setting.get_current_fps)
print('hi')
time.sleep(2)
coreLogic.quit()