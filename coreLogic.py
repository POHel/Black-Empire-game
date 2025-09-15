import sqlite3
import json
#работа с логикой приложения
class AppLogic:
	def __init__(self):
		self.name = 'Black Empire'
		self.company_name = 'SOFT.corp'
		self.version = '0.0.1'

#класс для экспортирование из базы данных
class ExportDB:
	def __init__(self):
		self.balance()
		self.earn_one_click()
		self.show_earn_click_level()
		self.show_earn_business_in_hour()
		self.show_earn_rent_in_hour()
		self.taxes()

	#работа с таблицой wallet
	#отображение баланса
	def balance(self):
		connect_balance = sqlite3.connect('data/data.db')
		cursor_balance = connect_balance.cursor()
		cursor_balance.execute('SELECT balance FROM wallet')
		result = cursor_balance.fetchone()[0]
		connect_balance.close()
		return result
	#возвращаем значение заработка за 1 клик
	def earn_one_click(self):
		connect_earn_one_click = sqlite3.connect('data/data.db')
		cursor_earn_one_click = connect_earn_one_click.cursor()
		cursor_earn_one_click.execute('SELECT moneys_one_click FROM wallet')
		result = cursor_earn_one_click.fetchone()[0]
		connect_earn_one_click.close()
		return result

	#отображение уровня кликера(заработок за 1 клик)
	def show_earn_click_level(self):
		connect_earn_one_click = sqlite3.connect('data/data.db')
		cursor_earn_one_click = connect_earn_one_click.cursor()
		cursor_earn_one_click.execute('SELECT moneys_one_click FROM wallet')
		result_level = cursor_earn_one_click.fetchone()[0]
		connect_earn_one_click.close()
		return result_level
	
	#отображение заработка с бизнеса в час
	def show_earn_business_in_hour(self):
		connect_earn_business_in_hour = sqlite3.connect('data/data.db')
		cursor_earn_business_in_hour = connect_earn_business_in_hour.cursor()
		cursor_earn_business_in_hour.execute('SELECT moneys_in_hour FROM wallet')
		result_earn_business_in_hour = cursor_earn_business_in_hour.fetchone()[0]
		connect_earn_business_in_hour.close()
		return result_earn_business_in_hour
	
	#отображение заработка с аренды в час
	def show_earn_rent_in_hour(self):
		connect_earn_rent_in_hour = sqlite3.connect('data/data.db')
		cursor_earn_rent_in_hour = connect_earn_rent_in_hour.cursor()
		cursor_earn_rent_in_hour.execute('SELECT moneys_rent_in_hour FROM wallet')
		result_earn_rent_in_hour = cursor_earn_rent_in_hour.fetchone()[0]
		connect_earn_rent_in_hour.close()
		return result_earn_rent_in_hour
	
	#отображение налогов в месяц
	def taxes(self):
		connect_taxes = sqlite3.connect('data/data.db')
		cursor_taxes = connect_taxes.cursor()
		cursor_taxes.execute('SELECT taxes FROM wallet')
		result_taxes = cursor_taxes.fetchone()[0]
		connect_taxes.close()
		return result_taxes

#класс для обновления в базе данных	
class UpdateDB:
	def __init__(self):
		self.export = ExportDB()
		self.update_balance_and_condition()
	
	#обновляем данные о балансе в базе данных
	def update_balance_and_condition(self):
		balance = self.export.balance()
		balance += self.export.earn_one_click()
		with sqlite3.connect('data/data.db') as connection:
			cursor = connection.cursor()
			cursor.execute('UPDATE wallet SET balance = ?', (balance,))
			cursor.execute('UPDATE status SET balance = ?', (balance,))
			cursor.execute('UPDATE status SET all_money = ?', (balance,))
			cursor.execute('UPDATE wallet SET all_moneys = ?', (balance,))
			connection.commit()

	
class Settings:
	def __init__(self):
		self.get_current_theme()
		self.get_current_window_size()
		self.get_current_fps()
		self.get_current_lang()
		self.show_fps()
		self.show_langs()
		self.show_themes()
		self.show_window_sizes()

	#импортирование текущей темы
	def get_current_theme(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_current_theme = json.load(file)
		return config_current_theme["current_theme"]
	
	#импортирование текущей размера экрана
	def get_current_window_size(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_current_window_size = json.load(file)
		return config_current_window_size["current_window_size"]
	
	#импортирование текущего фпс
	def get_current_fps(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_current_fps = json.load(file)
		return config_current_fps["current_fps"]
	
	#импортирование текущего языка
	def get_current_lang(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_current_lang = json.load(file)
		return config_current_lang["current_lang"]
	
	#установка выбранной темы
	def set_current_theme(self, theme: str):
		with open("data/config.json", "r", encoding="utf-8") as file:
			config = json.load(file)
			config["current_theme"] = theme
			file.seek(0)
			json.dump(config, file, ensure_ascii=False, indent=4)
			file.truncate()

	#установка размера экрана
	def set_current_window_size(self, height: int, width: int):
		with open("data/config.json", "r", encoding="utf-8") as file:
			config = json.load(file)
			config["current_window_size"] = [height, width]
			file.seek(0)
			json.dump(config, file, ensure_ascii=False, indent=4)
			file.truncate()

	#установка фпс
	def set_current_fps(self, fps: int):
		with open("data/config.json", "r", encoding="utf-8") as file:
			config = json.load(file)
			config["current_fps"] = fps
			file.seek(0)
			json.dump(config, file, ensure_ascii=False, indent=4)
			file.truncate()

	#установка языка
	def set_current_lang(self, lang: str):
		with open("data/config.json", "r", encoding="utf-8") as file:
			config = json.load(file)
			config["current_lang"] = lang
			file.seek(0)
			json.dump(config, file, ensure_ascii=False, indent=4)
			file.truncate()

	#показ всех тем
	def show_themes(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_themes = json.load(file)
		return config_themes["themes"]

	#показ всех размеров экрана
	def show_window_sizes(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_window_sizes = json.load(file)
		return config_window_sizes["window_size"]

	#показ всех фпс
	def show_fps(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_fps = json.load(file)
		return config_fps["FPS"]

	#показ всех языков
	def show_langs(self):
		with open("data/config.json", 'r', encoding='utf-8') as file:
			config_langs = json.load(file)
		return config_langs["languages"]