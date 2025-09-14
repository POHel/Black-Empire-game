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
               name_island TEXT NOT NULL,
               money_island FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS boosters(
               id INTEGER PRIMARY KEY,
               name_boosters TEXT NOT NULL,
               money_boosters FLOAT NOT NULL,
               time_boosters FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS NFT(
               id INTEGER PRIMARY KEY,
               name_NFT TEXT NOT NULL,
               money_NFT FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS cars(
               id INTEGER PRIMARY KEY,
               name_cars TEXT NOT NULL,
               money_cars FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS unique_items(
               id INTEGER PRIMARY KEY,
               name_unique_items TEXT NOT NULL,
               money_unique_items FLOAT NOT NULL,
               ); 
                                         
CREATE TABLE IF NOT EXISTS yacht(
               id INTEGER PRIMARY KEY,
               name_yacht TEXT NOT NULL,
               money_yacht FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS airplanes(
               id INTEGER PRIMARY KEY,
               name_airplanes TEXT NOT NULL,
               money_airplanes FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS residence(
               id INTEGER PRIMARY KEY,
               name_residence TEXT NOT NULL,
               money_residence FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS jewelry(
               id INTEGER PRIMARY KEY,
               name_jewelry TEXT NOT NULL,
               money_jewelry FLOAT NOT NULL,
               );

''')
connect.commit()
connect.close()
connect = sqlite3.connect('data/black_shop.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS guns(
               id INTEGER PRIMARY KEY,
               name_guns TEXT NOT NULL,
               money_guns FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS substances(
               id INTEGER PRIMARY KEY,
               name_substances TEXT NOT NULL,
               money_substances FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS medication(
               id INTEGER PRIMARY KEY,
               name_medication TEXT NOT NULL,
               money_medication FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS contraband(
               id INTEGER PRIMARY KEY,
               name_contraband TEXT NOT NULL,
               money_contraband FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS dangerous_services(
               id INTEGER PRIMARY KEY,
               name_dangerous_services TEXT NOT NULL,
               money_dangerous_services FLOAT NOT NULL,
               );   
                                       
CREATE TABLE IF NOT EXISTS cyber_implants(
               id INTEGER PRIMARY KEY,
               name_cyber_implants TEXT NOT NULL,
               money_cyber_implants FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS gamble(
               id INTEGER PRIMARY KEY,
               name_gamble TEXT NOT NULL,
               money_gamble FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS exotic(
               id INTEGER PRIMARY KEY,
               name_exotic TEXT NOT NULL,
               money_exotic FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS rarities(
               id INTEGER PRIMARY KEY,
               name_rarities TEXT NOT NULL,
               money_rarities FLOAT NOT NULL,
               );
                     
CREATE TABLE IF NOT EXISTS legendaries(
               id INTEGER PRIMARY KEY,
               name_legendaries TEXT NOT NULL,
               money_legendaries FLOAT NOT NULL,
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