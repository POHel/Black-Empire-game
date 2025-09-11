import sqlite3
class AppLogic:
	def __init__(self):
		self.balance()
		self.earn_one_click()
		self.earn_click()
		self.earn_click_level()

	def balance(self):
		connect_balance = sqlite3.connect('data/business_data.db')
		cursor_balance = connect_balance.cursor()
		cursor_balance.execute('SELECT moneys FROM wallet')
		result = cursor_balance.fetchone()[0]
		connect_balance.close()
		return result
	def earn_one_click(self):
		connect_earn_one_click = sqlite3.connect('data/business_data.db')
		cursor_earn_one_click = connect_earn_one_click.cursor()
		cursor_earn_one_click.execute('SELECT moneys_one_click FROM wallet')
		result = cursor_earn_one_click.fetchone()[0]
		connect_earn_one_click.close()
		return result
	def earn_click(self):
		balance = self.balance()
		balance += self.earn_one_click()
		connect_earn_click = sqlite3.connect('data/business_data.db')
		cursor_earn_click = connect_earn_click.cursor()
		cursor_earn_click.execute('UPDATE wallet set moneys = ?', (balance,))
		connect_earn_click.commit()
		connect_earn_click.close()
		all_money_status = sqlite3.connect('data/business_data.db')
		all_money = all_money_status.cursor()
		all_money.execute('UPDATE status set all_moneys = ?', (balance,))
		all_money_status.commit()
		all_money_status.close()
	def earn_click_level(self):
		connect_earn_one_click = sqlite3.connect('data/business_data.db')
		cursor_earn_one_click = connect_earn_one_click.cursor()
		cursor_earn_one_click.execute('SELECT earn_click_level FROM wallet')
		result_level = cursor_earn_one_click.fetchone()[0]
		connect_earn_one_click.close()
		click_level = '1'
		return click_level
