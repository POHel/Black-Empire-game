import sqlite3
connect = sqlite3.connect('data/business_data.db')
cursor = connect.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS wallet(
               id INTEGER PRIMARY KEY,
               all_moneys FLOAT NOT NULL,
               moneys FLOAT NOT NULL,
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
connect = sqlite3.connect('data/shops.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS white_shop(
               id INTEGER PRIMARY KEY,
               items_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS black_shop(
               id INTEGER PRIMARY KEY,
               black_items_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS cars_shop(
               id INTEGER PRIMARY KEY,
               cars_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS airplane_shop(
               id INTEGER PRIMARY KEY,
               airplane_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS yacht_shop(
               id INTEGER PRIMARY KEY,
               yacht_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );           
CREATE TABLE IF NOT EXISTS monet_shop(
               id INTEGER PRIMARY KEY,
               monet_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS NFT_shop(
               id INTEGER PRIMARY KEY,
               NFT_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS retro_cars_shop(
               id INTEGER PRIMARY KEY,
               retro_cars_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS pictures_shop(
               id INTEGER PRIMARY KEY,
               picture_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS islands_shop(
               id INTEGER PRIMARY KEY,
               island_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS jewelry_shop(
               id INTEGER PRIMARY KEY,
               jewelry_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS unique_items_shop(
               id INTEGER PRIMARY KEY,
               unique_item_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
''')
connect.commit()
connect.close()

connect = sqlite3.connect('data/items.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS white_shop(
               id INTEGER PRIMARY KEY,
               items_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS black_shop(
               id INTEGER PRIMARY KEY,
               black_items_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS cars_shop(
               id INTEGER PRIMARY KEY,
               cars_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS airplane_shop(
               id INTEGER PRIMARY KEY,
               airplane_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS yacht_shop(
               id INTEGER PRIMARY KEY,
               yacht_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );           
CREATE TABLE IF NOT EXISTS monet_shop(
               id INTEGER PRIMARY KEY,
               monet_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS NFT_shop(
               id INTEGER PRIMARY KEY,
               NFT_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS retro_cars_shop(
               id INTEGER PRIMARY KEY,
               retro_cars_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS pictures_shop(
               id INTEGER PRIMARY KEY,
               picture_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS islands_shop(
               id INTEGER PRIMARY KEY,
               island_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS jewelry_shop(
               id INTEGER PRIMARY KEY,
               jewelry_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
CREATE TABLE IF NOT EXISTS unique_items_shop(
               id INTEGER PRIMARY KEY,
               unique_item_name TEXT NOT NULL,
               price FLOAT NOT NULL
               );
''')
connect.commit()
connect.close()