import sqlite3
connect = sqlite3.connect('data/business_data.db')
cursor = connect.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS wallet(
               id INTEGER PRIMARY KEY,
               moneys INTEGER NOT NULL,
               moneys_one_click INTEGER NOT NULL,
               moneys_in_hour INTEGER NOT NULL,
               moneys_rent_in_hour INTEGER NOT NULL,
               moneys_bag INTEGER NOT NULL
               );
             
CREATE TABLE IF NOT EXISTS invertory(
               id INTEGER PRIMARY KEY,
               my_items TEXT NOT NULL
               );

CREATE TABLE IF NOT EXISTS status(
               id INTEGER PRIMARY KEY,
               all_moneys INTEGER NOT NULL,
               money_balance INTEGER NOT NULL,
               moneys_business INTEGER NOT NULL,
               moneys_homes INTEGER NOT NULL,
               moneys_crypto_actives INTEGER NOT NULL,
               moneys_transport INTEGER NOT NULL,
               amount_business INTEGER NOT NULL,
               amount_homes INTEGER NOT NULL,
               amount_company INTEGER NOT NULL,
               amount_cars INTEGER NOT NULL,
               amount_airplanes INTEGER NOT NULL,
               amount_yachts INTEGER NOT NULL,
               amount_collections_items INTEGER NOT NULL,
               amount_islands INTEGER NOT NULL,
               earn_clicks INTEGER NOT NULL,
               earn_business INTEGER NOT NULL,
               earn_rent INTEGER NOT NULL,
               earn_crypto INTEGER NOT NULL
               );

CREATE TABLE IF NOT EXISTS business(
               id INTEGER PRIMARY KEY,
               my_business_name TEXT NOT NULL,
               levels INTEGER NOT NULL,
               earn_in_hour INTEGER NOT NULL,
               type TEXT NOT NULL,
               all_moneys INTEGER NOT NULL,
               capitalization INTEGER NOT NULL,
               time TEXT NOT NULL
               );

CREATE TABLE IF NOT EXISTS crypto_wallet(
               id INTEGER PRIMARY KEY,
               crypto_name TEXT NOT NULL,
               capitalization INTEGER NOT NULL,
               price INTEGER NOT NULL
               );

CREATE TABLE IF NOT EXISTS my_homes(
               id INTEGER PRIMARY KEY,
               my_homes_name TEXT NOT NULL,
               earn_in_hour INTEGER NOT NULL,
               location TEXT NOT NULL,
               price INTEGER NOT NULL
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
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS black_shop(
               id INTEGER PRIMARY KEY,
               black_items_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS cars_shop(
               id INTEGER PRIMARY KEY,
               cars_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS airplane_shop(
               id INTEGER PRIMARY KEY,
               airplane_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS yacht_shop(
               id INTEGER PRIMARY KEY,
               yacht_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );           
CREATE TABLE IF NOT EXISTS monet_shop(
               id INTEGER PRIMARY KEY,
               monet_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS NFT_shop(
               id INTEGER PRIMARY KEY,
               NFT_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS retro_cars_shop(
               id INTEGER PRIMARY KEY,
               retro_cars_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS pictures_shop(
               id INTEGER PRIMARY KEY,
               picture_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS islands_shop(
               id INTEGER PRIMARY KEY,
               island_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS jewelry_shop(
               id INTEGER PRIMARY KEY,
               jewelry_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
CREATE TABLE IF NOT EXISTS unique_items_shop(
               id INTEGER PRIMARY KEY,
               unique_item_name TEXT NOT NULL,
               price INTEGER NOT NULL
               );
''')
connect.commit()
connect.close()