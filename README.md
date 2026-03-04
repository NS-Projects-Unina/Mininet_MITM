# Mininet MiTM: Arcade Heist

**Descrizione**: Simulazione in Mininet di un'infrastruttura Arcade comprendente un Server (h1) che ospita un backend di gioco (secure_server.py), un database per i punteggi (arcade.db) e un portale web di e-commerce "arcade.shop". L'utente gioca tramite una console client (h2). L'applicativo client, tuttavia, non valida correttamente i certificati SSL del server (CWE-295: Improper Certificate Validation). Sfruttando ciò, un attaccante (h3) è in grado di eseguire un attacco ARP Spoofing seguito da un TLS MITM (Entity-On-The-Path), intercettando la connessione e iniettando un punteggio alterato a proprio vantaggio da spendere nel negozio.

---


## 1. L'Architettura (Topologia Mininet)

Questa è la rete LAN realizzata con 3 nodi.

| Host | Ruolo | IP | Descrizione |
| --- | --- | --- | --- |
| **h1** | **Server** | `10.0.0.1` | Ospita il backend dei giochi su porta 8443 (alternativa a 443), il database SQLite per i punteggi e il portale e-commerce ""Arcade Shop"" su porta 80. |
| **h2** | **Console** | `10.0.0.2` | Naviga sullo shop ed esegue la console di gioco (arcade_console.py), si connette al server **ma non valida il certificato SSL** (CWE-295: Improper Certificate Validation). |
| **h3** | **Attaccante** | `10.0.0.3` | Esegue ARP Spoofing (lvl 2) e un Proxy TLS MITM (lvl 7) per intercettare il traffico della console e iniettare punteggi falsificati nel payload JSON |

*P.S: È stato scelto SQLite poiché è un database serverless, cioé salva l'intera struttura in un unico file locale (arcade.db) gestito direttamente dal programma Python, a differenza di DBMS tradizionali come MySQL o PostgreSQL che richiedono l'installazione e l'esecuzione di un demone server separato.*

---


## 2. Guida all'uso

Di seguito sono riportati i passi da seguire per configurare l'ambiente Mininet, avviare la simulazione ed eseguire la catena d'attacco completa per alterare il punteggio di gioco ed acquistare la fantomatica "Lamborghini" (~~boot-to-root~~ --> *broke-to-Lamborghini*).

### Prerequisiti

* OS: Kali Linux
* Mininet
* Python 3 con le librerie `scapy` e `flask`

### Step 1: Avvio della Topologia di Rete

Avviare un terminale come root nella cartella principale del progetto e avviare la topologia Mininet

```bash
sudo python3 topology.py
```

*Verrà avviata la CLI di Mininet e gli xterm dei tre host: h1 (Server), h2 (Client) e h3 (Attaccante).*

---

### Step 2: Configurazione del Server (su h1)

Aprire un terminale per l'host **h1** e inizializzare il database e i servizi backend.

**Nel terminale di h1:**

```bash
python3 setup_db.py    
python3 secure_server.py &    # Avvio del Server di gioco in background, porta 8443
python3 shop_server.py    # Avvio del Server Web dello shop "arcade.shop", porta 80
```

---

### Step 3: Baseline della Vittima (su h2)

Registrare un utente, osservare successiamente che il saldo sia zero.

**Nel terminale di h2:**

```bash
# Avvio di Firefox in background come utente non-root
su kali -c "firefox http://arcade.shop" &
```

1. Nel browser aperto, cliccare su **Registrati**.
2. Creare un nuovo utente (es. `pippo` / `pwd`).
3. Effettuare il login. Notare che il saldo punti è **0** e non è possibile acquistare la Lamborghini.
4. Chiudere o minimizzare Firefox.


---

### Step 4: Avvio dell'Attacco (su h3)

*OSS: Prima di questo Step, è possibile effettuare prima lo Step 5 per verificare il funzionamento nominale della comunicazione tra gioco e Server SENZA alterazione da parte dell'attaccante.*

L'attaccante deve eseguire tre azioni simultanee: avvelenare la rete, reindirizzare il traffico e avviare il proxy MITM.

**Aprire DUE terminali per h3.**

**Terminale h3 #1 (ARP Spoofing):**

```bash
python3 atk_dir/arpspoof.py
# Lasciare questo script in esecuzione per avvelenare le cache ARP di h1 e h2.

```

**Terminale h3 #2 (Redirezione e Proxy MITM):**

```bash
# 1. Configurare iptables per reindirizzare il traffico HTTPS (8443) verso il proxy (9000)
iptables -t nat -A PREROUTING -p tcp --dport 8443 -j REDIRECT --to-port 9000

# 2. Avviare il Proxy TLS MITM
python3 atk_dir/tls_mitm.py

```

*Quando richiesto dal proxy, inserire il punteggio che si desidera iniettare (es. `1000000`).*

---

### Step 5: Esecuzione del gioco (su h2)

La vittima gioca una partita. Il client vulnerabile si connetterà al proxy dell'attaccante senza validare il certificato, permettendo l'iniezione del punteggio.

**Nel terminale di h2:**

```bash
# Avviare la console di gioco
python3 game_dir/arcade_console.py

```

1. Effettuare il login con l'utente creato allo Step 3 (`pippo`).
2. Scegliere un gioco.
3. Giocare fino a che non si vuole terminare (a questo punto bisogna perdere) per inviare il punteggio.

*Nel terminale del proxy di h3 sarà visibile il log dell'intercettazione e della modifica del JSON.*

---

### Step 6: Verifica del Profitto (su h2)

Ritornando sul browser della vittima, sarà possibile confermare il successo dell'attacco.

1. Riaprire la finestra di Firefox su **h2** (`http://arcade.shop`).
2. Provare ad acquistare la **LAMBORGHINI**.
3. **SUCCESSO $$$!**


---


## 3. Le Fasi dell'Attacco

In questa sezione del documento sono riportate e descritte esclusivamente le fasi operative che portano alla compromissione del sistema e all'alterazione dei dati nel database:

**1. Posizionamento (ARP Spoofing):** L'attaccante (h3) avvelena le tabelle ARP del client (h2) e del server (h1). Questo costringe il traffico scambiato tra i due host a transitare fisicamente attraverso la macchina dell'attaccante (qui si predispone l'Entity-On-The-Path).

**2. Intercettazione (TLS Proxying):** L'attaccante instrada il traffico intercettato sulla porta 8443 verso un proprio script proxy. Sfruttando la debolezza del client (h2), che non verifica l'autenticità dei certificati, il proxy riesce a presentare un certificato contraffatto, il quale viene accettato dal client, permettendo all'attaccante di decifrare il tunnel SSL in chiaro.

**3. Manipolazione del Payload JSON:** Quando l'utente conclude una partita legittima, la console tenta di inviare il punteggio al server. Il proxy intercetta la richiesta "on-the-fly", legge il payload JSON e sovrascrive il campo "score" con un valore scelto dall'attaccante, per poi re-incapsulare il pacchetto e inoltrarlo al server vero.

**4. Conclusione:** Il backend del server riceve il pacchetto alterato e aggiorna il database incrementando i fondi dell'utente. A questo punto l'attaccante (o l'utente "complice") accede all'interfaccia web dell'e-commerce e sfrutta il credito ottenuto per acquistare ciò che desidera.


---



