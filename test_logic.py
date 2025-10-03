import time
import coreLogic
import sqlite3
import json
from coreLogic import AppLogic, ExportDB, UpdateDB, Settings
logic = AppLogic()
export = ExportDB()
update = UpdateDB
settings = Settings()


print('start')
#print(export.get_actives())
#print(setting.get_current_fps())
#print(setting.set_current_fps(30))
#print(setting.get_current_fps)
#export.get_actives()
# Получаем текущие значения
#print(settings.current_theme)  # "dark"
#print(settings.current_window_size)  # ["1920", "1080"]
#print(settings.current_fps)  # 60
#print(settings.current_lang)  # "ru"

# Получаем доступные опции
#print(settings.themes)  # ["dark", "light"]
#print(settings.window_sizes)  # [["1280", "720"], ["1920", "1080"]]
#print(settings.fps_options)  # ["30", "60", "120"]
#print(settings.languages)  # ["ru", "en"]

# Изменяем настройки
#settings.set_current_theme("light")
#settings.set_current_fps(120)
print(export.get_bag())
print('end')