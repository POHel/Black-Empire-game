# -*- coding: utf-8 -*-
#import colorama
#from colorama import Fore
import sys
import os
import sqlite3
#colorama.init()
class AppLogic:
	def __init__(self):
		self.balance()
		self.earn_one_click()
		self.earn_click()

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

	#functions
	def my_cars():
		cars = open('my_cars.dat', 'r')
		rez = sorted(cars.read().splitlines())
		print('MY CARS:\n')
		for n, item in enumerate(rez):
			print(n+1, item)
		start()

	def up():
		print(f'{MAG}Ваши ачивки:{YE}')
		xp_up = open('xp.dat', 'r')
		rez_up = sorted(xp_up.read().splitlines())
		for n, item in enumerate(rez_up):
			print(n+1, item)
		xp_up.close()
		print('\n0 - EXIT')
		what = int(input('-> '))
		if what == 0:
			start()


	def klic():
		print(f'{GR}Balance: {RES}{balance()}$')
		kl = int(input('1 - начать кликать\n2 - остановить кликер\n-> '))
		if kl == 1:
			try:
				data = open('all.dat', 'r')
				data_line = data.read().splitlines()
				data.close()
				data_money = int(data_line[0])
				money = balance()
				tap = ''
				print('Тапай на клавижу ENTER!')
				while tap != '2':
					tap = input('>')
					print(f'+{config.tap}$')
					money += config.tap
					if money == 50000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 50.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 50.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('1')
						lvl.close()
					elif money == 100000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 100.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N1 Вы заработали 100.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('2')
						lvl.close()

					elif money == 500000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 500.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N2 Вы заработали 500.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('3')
						lvl.close()
					elif money == 1000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 1.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 1.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('4')
						lvl.close()
					elif money == 5000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 5.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 5.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('5')
						lvl.close()
					elif money == 10000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 10.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 10.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('6')
						lvl.close()
					elif money == 50000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 50.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 50.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('7')
						lvl.close()
					elif money == 100000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 100.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 100.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('8')
						lvl.close()
					elif money == 150000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 150.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 150.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('9')
						lvl.close()
					elif money == 500000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 500.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 500.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('10')
						lvl.close()
					elif money == 1000000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 1.000.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 1.000.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('11')
						lvl.close()
					elif money == 1500000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 1.500.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 1.500.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('12')
						lvl.close()
					elif money == 10000000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 10.000.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 10.000.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('13')
						lvl.close()
					elif money == 100000000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 100.000.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 100.000.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('14')
						lvl.close()
					elif money == 1000000000000:
						bonus = money // 2
						money += bonus
						print(f'{YE}Новая ачивка!\nВы заработали 1.000.000.000.000${RES}')
						print(f'{GR}Начисление бонуса в размере: {bonus}${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Ачивка N3 Вы заработали 1.000.000.000.000$\n')
						xp.close()
						lvl = open('lvl.dat', 'w')
						lvl.write('15')
						lvl.close()
					elif money == 666:
						money += 666
						print(f'{YE}Вы нашли посхалку!{RES}')
						print(f'{GR}Начисление бонуса в размере: 666${RES}')
						xp = open('xp.dat', 'a+')
						xp.write('Вы заработали 666$\n')
						xp.close()
					data_money += config.tap
					print(f'{GR}Balance: {RES}{money}$')
					data = open('all.dat', 'w')
					data.write(f'{data_money}\n{data_line[1]}\n{data_line[2]}\n{data_line[3]}')
					data.close()
					all_money = open('money.wallet', 'w')
					all_money.write(str(money))
				all_money.close()
				os.system('cls')
				start()
			except KeyboardInterrupt:
				all_money.close()
				os.system('cls')

				start()

		elif kl == 2:
			print('Ok!')
		else:
			print('log: error_num')

	def bank():
		print()

	def business():
		print()

	#display
	def start():
		print(f'''
		{GR}Tunder Game{RED} {config.ver}{RES}
		{GR}Баланс: {WH}{balance()}${RES}
		{BL}LVL: {WH}{level()}{RES}
		{YE}
		Меню:
		1) Кликер
		2) Магазин
		{RES}
		--3) Банк---{RED}не работает(в разработке){RES}
		--4) Бизнесы---{RED}не работает(в разработке){RES}
		{YE}
		5) Мои Машины
		6) Мои Самолёты
		7) Сведения
		8) Ачивки
		9) Выйти
		{RES}
		''')
		num = int(input('-> '))
		if num == 1:
			klic()
		elif num == 2:
			import shop_tool
			shop_tool.shop()
		elif num == 3:
			bank()
		elif num == 4:
			business()
		elif num == 5:
			my_cars()
			
		elif num == 7:
			import all_data
			all_data.data()
			start()
		elif num == 8:
			up()
		elif num == 9:
			sys.exit()

		else:
			print('log: error_num')
		