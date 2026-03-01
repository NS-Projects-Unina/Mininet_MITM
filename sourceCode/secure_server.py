import socket, ssl, sqlite3, json, hashlib, os, sys
from datetime import datetime

IP, PORT = '10.0.0.1', 8443
DB_NAME = "arcade.db"

# Verifica esistenza DB
if not os.path.exists(DB_NAME):
    print(f"Database non trovato!")
    sys.exit(1)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.maximum_version = ssl.TLSVersion.TLSv1_2
context.load_cert_chain("server_cert/server.crt", "server_cert/server.key")

def handle_request(conn, data):
    try:
        req = json.loads(data)
        action = req.get("action")
        
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        response = {"status": "ERROR", "msg": "Invalid Request"}

        if action == "REGISTER":
            user = req['username']
            pwd_hash = hashlib.sha256(req['password'].encode()).hexdigest()
            try:
                cursor.execute("INSERT INTO users (username, password_hash, total_score) VALUES (?, ?, 0)", 
                               (user, pwd_hash))
                db.commit()
                response = {"status": "OK", "msg": "Registrazione OK!"}
            except sqlite3.IntegrityError:
                response = {"status": "FAIL", "msg": "Username occupato."}

        elif action == "LOGIN":
            user = req['username']
            pwd_hash = hashlib.sha256(req['password'].encode()).hexdigest()
            cursor.execute("SELECT total_score FROM users WHERE username=? AND password_hash=?", (user, pwd_hash))
            result = cursor.fetchone()
            if result:
                response = {"status": "OK", "msg": f"Bentornato! Saldo: {result[0]}"}
            else:
                response = {"status": "FAIL", "msg": "Credenziali errate."}

        elif action == "SCORE":
            user = req['username']
            game = req['game']
            new_points = int(req['score'])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log punteggio e aggiornamento saldo
            cursor.execute("INSERT INTO scores (username, game, score, timestamp) VALUES (?, ?, ?, ?)", 
                           (user, game, new_points, timestamp))
            cursor.execute("UPDATE users SET total_score = total_score + ? WHERE username = ?", 
                           (new_points, user))
            db.commit()
            
            cursor.execute("SELECT total_score FROM users WHERE username=?", (user,))
            new_total = cursor.fetchone()[0]
            print(f"[DB] {user} (+{new_points}) -> Nuovo Saldo: {new_total}")
            response = {"status": "OK", "msg": f"Punti salvati. Totale: {new_total}"}

        db.close()
        return json.dumps(response).encode()

    except Exception as e:
        print(f"[ERROR] {e}")
        return json.dumps({"status": "ERROR", "msg": str(e)}).encode()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
# Con la prima costante dichiaro che userò indirizzi IPv4, con la seconda che il protocollo di livello trasporto è TCP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 'SO_REUSEADDR' evita l'errore "Address already in use", permettendo di riavviare lo script riutilizzando la porta 
# "congelata", ignorando il blocco "TIME_WAIT"
sock.bind((IP, PORT))
sock.listen(5)
print(f"[*] GAME SERVER listening on {IP}:{PORT}")

while True:
    newsocket, fromaddr = sock.accept()
    try:
        conn = context.wrap_socket(newsocket, server_side=True)
        data = conn.recv(4096).decode()
        if data:
            conn.send(handle_request(conn, data))
        conn.close()
    except Exception as e:
        print(f"[Errore TLS] {e}")
