import sqlite3
#работа с логикой приложения
class AppLogic:
	def __init__(self):
		self.name = 'Black Empire'
		self.company_name = 'SOFT.corp'
		self.version = '0.0.1'

#класс для экспортирование из базы данных
class export_db:
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
class update_db:
	def __init__(self):
		self.export = export_db()
		self.earn_click()
	
	#обновляем данные о балансе в базе данных
	def earn_click(self):
		balance = self.export.balance()
		balance += self.export.earn_one_click()

		#update in wallet
		connect_earn_click = sqlite3.connect('data/data.db')
		cursor_earn_click = connect_earn_click.cursor()
		cursor_earn_click.execute('UPDATE wallet set balance = ?', (balance,))
		connect_earn_click.commit()
		connect_earn_click.close()
		#update in status
		connect_earn_click = sqlite3.connect('data/data.db')
		cursor_earn_click = connect_earn_click.cursor()
		cursor_earn_click.execute('UPDATE status set balance = ?', (balance,))
		connect_earn_click.commit()
		connect_earn_click.close()

		#update in status
		all_money_status = sqlite3.connect('data/data.db')
		all_money = all_money_status.cursor()
		all_money.execute('UPDATE status set all_money = ?', (balance,))
		all_money_status.commit()
		all_money_status.close()

		#update in wallet
		all_money_wallet = sqlite3.connect('data/data.db')
		all_money_w = all_money_wallet.cursor()
		all_money_w.execute('UPDATE wallet set all_moneys = ?', (balance,))
		all_money_wallet.commit()
		all_money_wallet.close()