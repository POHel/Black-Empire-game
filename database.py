import sqlite3
connect = sqlite3.connect('data/business_data.db')
cursor = connect.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS wallet(
               id INTEGER PRIMARY KEY,
               all_moneys FLOAT NOT NULL,
               balance FLOAT NOT NULL,
               moneys_one_click FLOAT NOT NULL,
               moneys_in_hour FLOAT NOT NULL,
               moneys_rent_in_hour FLOAT NOT NULL,
               taxes FLOAT NOT NULL,
               );
             
                     
CREATE TABLE IF NOT EXISTS my_bag(
               id INTEGER PRIMARY KEY,
               all_moneys_bag FLOAT NOT NULL,
               dividend_yield FLOAT NOT NULL,
               stable_income FLOAT NOT NULL,
               growth_potential FLOAT NOT NULL,
               rental_income FLOAT NOT NULL,
               );

CREATE TABLE IF NOT EXISTS actives(
            id INTEGER PRIMARY KEY,
               name_actives TEXT NOT NULL,
               money_actives FLOAT NOT NULL,
               amount_actives TEXT NOT NULL,
               profitability_actives FLOAT NOT NULL,
               );                     
CREATE TABLE IF NOT EXISTS homes(
            id INTEGER PRIMARY KEY,
               name_homes TEXT NOT NULL,
               money_homes FLOAT NOT NULL,
               profitability_homes FLOAT NOT NULL,
               );  
CREATE TABLE IF NOT EXISTS crypto(
            id INTEGER PRIMARY KEY,
               name_crypto TEXT NOT NULL,
               money_crypto FLOAT NOT NULL,
               amount_crypto TEXT NOT NULL,
               );                   

CREATE TABLE IF NOT EXISTS status(
               id INTEGER PRIMARY KEY,
               all_money FLOAT NOT NULL,
               balance FLOAT NOT NULL,
               income_business FLOAT NOT NULL,
               income_rent FLOAT NOT NULL,
               actives FLOAT NOT NULL,
               amount_business INTEGER NOT NULL,
               amount_homes INTEGER NOT NULL,
               amount_company INTEGER NOT NULL,
               amount_cars INTEGER NOT NULL,
               amount_airplanes INTEGER NOT NULL,
               amount_yachts INTEGER NOT NULL,
               amount_items INTEGER NOT NULL,
               amount_islands INTEGER NOT NULL,
               earn_clicks FLOAT NOT NULL,
               earn_business FLOAT NOT NULL,
               earn_rent FLOAT NOT NULL,
               earn_crypto FLOAT NOT NULL
               );

CREATE TABLE IF NOT EXISTS business(
               id INTEGER PRIMARY KEY,
               my_business_name TEXT NOT NULL,
               levels INTEGER NOT NULL,
               earn_in_hour FLOAT NOT NULL,
               type TEXT NOT NULL,
               all_moneys FLOAT NOT NULL,
               capitalization FLOAT NOT NULL,
               time TEXT NOT NULL
               );

''')
connect.commit()
connect.close()
connect = sqlite3.connect('data/white_shop.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS island(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS boosters(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS NFT(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS cars(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS unique_items(
               id INTEGER PRIMARY KEY,
               );                     
CREATE TABLE IF NOT EXISTS yacht(
               id INTEGER PRIMARY KEY,
               );

CREATE TABLE IF NOT EXISTS airplanes(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS residence(
               id INTEGER PRIMARY KEY,
               );

CREATE TABLE IF NOT EXISTS jewelry(
               id INTEGER PRIMARY KEY,
               );

''')
connect.commit()
connect.close()
connect = sqlite3.connect('data/black_shop.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS guns(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS substances(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS medication(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS contraband(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS dangerous_services(
               id INTEGER PRIMARY KEY,
               );                     
CREATE TABLE IF NOT EXISTS cyber_implants(
               id INTEGER PRIMARY KEY,
               );

CREATE TABLE IF NOT EXISTS gamble(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS exotic(
               id INTEGER PRIMARY KEY,
               );

CREATE TABLE IF NOT EXISTS rarities(
               id INTEGER PRIMARY KEY,
               );
CREATE TABLE IF NOT EXISTS legendaries(
               id INTEGER PRIMARY KEY,
               );
''')
connect.commit()
connect.close()
connect = sqlite3.connect('data/items.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS test(
               id INTEGER PRIMARY KEY,
               test_name TEXT NOT NULL,
               test_fl FLOAT NOT NULL,
               test_int INTEGER NOT NULL
               );
''')
connect.commit()
connect.close()