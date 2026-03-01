import sqlite3
import hashlib
import os

DB_NAME = "arcade.db"

def setup():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Vecchio database rimosso.")

    print(f"Creazione database '{DB_NAME}'...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Tabella Utenti (con total_score)
    c.execute('''CREATE TABLE users 
                 (username TEXT PRIMARY KEY, 
                  password_hash TEXT, 
                  total_score INTEGER DEFAULT 0)''')
    
    # Tabella Storico Punteggi
    c.execute('''CREATE TABLE scores 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, game TEXT, score INTEGER, timestamp TEXT)''')


    conn.commit()	# Salvo i risultati degli execute
    conn.close()
    print("[OK] Database pronto.")

if __name__ == "__main__":
    setup()
