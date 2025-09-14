import sqlite3
class AppLogic:
	def __init__(self):
		self.name = 'Black Empire'
		self.company_name = 'SOFT.corp'
		self.version = '0.0.1'
		self.balance()
		self.earn_one_click()
		self.earn_click()
		self.show_earn_click_level()
		self.taxes()

#работа с базой данных
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
	#обновляем данные о балансе в базе данных
	def earn_click(self):
		balance = self.balance()
		balance += self.earn_one_click()
		connect_earn_click = sqlite3.connect('data/data.db')
		cursor_earn_click = connect_earn_click.cursor()
		cursor_earn_click.execute('UPDATE wallet set balance = ?', (balance,))
		connect_earn_click.commit()
		connect_earn_click.close()
		all_money_status = sqlite3.connect('data/data.db')
		all_money = all_money_status.cursor()
		all_money.execute('UPDATE status set all_money = ?', (balance,))
		all_money_status.commit()
		all_money_status.close()
	#отображение уровня кликера(заработок за 1 клик)
	def show_earn_click_level(self):
		connect_earn_one_click = sqlite3.connect('data/data.db')
		cursor_earn_one_click = connect_earn_one_click.cursor()
		cursor_earn_one_click.execute('SELECT moneys_one_click FROM wallet')
		result_level = cursor_earn_one_click.fetchone()[0]
		connect_earn_one_click.close()
		return result_level
	#отображение налогов в месяц
	def taxes(self):
		connect_taxes = sqlite3.connect('data/data.db')
		cursor_taxes = connect_taxes.cursor()
		cursor_taxes.execute('SELECT taxes FROM wallet')
		result_taxes = cursor_taxes.fetchone()[0]
		connect_taxes.close()
		return result_taxes