import sqlite3

connect = sqlite3.connect('data/invest.db')
cursor = connect.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS actives(
            id INTEGER PRIMARY KEY,
               name_actives TEXT NOT NULL,
               money_actives FLOAT NOT NULL,
               amount_actives TEXT NOT NULL,
               profitability_actives FLOAT NOT NULL
               ); 
                                         
CREATE TABLE IF NOT EXISTS homes(
            id INTEGER PRIMARY KEY,
               name_homes TEXT NOT NULL,
               money_homes FLOAT NOT NULL,
               profitability_homes FLOAT NOT NULL
               );  
                     
CREATE TABLE IF NOT EXISTS crypto(
            id INTEGER PRIMARY KEY,
               name_crypto TEXT NOT NULL,
               money_crypto FLOAT NOT NULL,
               amount_crypto TEXT NOT NULL
               );                   

''')
connect.commit()
connect.close()