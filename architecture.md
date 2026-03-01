| Directory / File | Descrizione |
| :--- | :--- |
| `atk_dir/` | Contiene gli script di attacco utilizzati dall'attaccante (ARP Spoofing e TLS MITM proxy). |
| `game_dir/` | Ospita la console di gioco arcade_console.py. |
| `static/` e `templates/` | Contengono rispettivamente i fogli di stile (file CSS) e le pagine HTML utilizzate da Flask per l'interfaccia web del sito web. |
| `server_cert/` e `atk_cert/` | Contiene i certificati e le chiavi private. La prima contiene quelli legittimi del server, la seconda quelli contraffatti dall'attaccante. |
| `topology.py` | Lo script per istanziare l'ambiente di rete virtuale tramite Mininet. |
| `secure_server.py` e `shop_server.py` | I due script eseguiti dal Server (rispettivamente, il backend di gioco sulla porta 8443 e il portale web sulla porta 80). |
| `setup_db.py` e `arcade.db` | Lo script di inizializzazione e il file fisico del database SQLite in cui risiedono gli account e i saldi degli utenti. |
| `certs_creation.sh` | Script Bash per la generazione automatica dei certificati. |
