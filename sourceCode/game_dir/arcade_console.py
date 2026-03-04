import socket, ssl, json, time, curses, sys
from random import randint

SERVER_IP, SERVER_PORT = '10.0.0.1', 8443

context = ssl.create_default_context()
context.maximum_version = ssl.TLSVersion.TLSv1_2
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE 

CURRENT_USER = None


def send_request(payload):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_sock = context.wrap_socket(sock, server_hostname=SERVER_IP)
        secure_sock.connect((SERVER_IP, SERVER_PORT))
        secure_sock.send(json.dumps(payload).encode())
        response = secure_sock.recv(4096).decode()
        secure_sock.close()
        return json.loads(response)
    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}

def auth_menu():
    global CURRENT_USER
    while True:
        print("\n" + "="*32)
        print(" Ciao giocatore! Seleziona l'azione preliminare: ")
        print("="*32)
        print("1. Accedi")
        print("2. Esci")
        choice = input("Scelta: ")
        
        if choice == '2': sys.exit()
        elif choice != '1': continue
        
        user = input("Username: ")
        pwd = input("Password: ")
        action = "LOGIN"
        
        resp = send_request({"action": action, "username": user, "password": pwd})
        print(f"\n>> {resp.get('msg')}")
        
        if resp.get('status') == 'OK':
            CURRENT_USER = user
            break

def send_score(score, game_name):
    if not CURRENT_USER: return
    print(f"\nInvio punteggio per {CURRENT_USER}...")
    resp = send_request({"action": "SCORE", "username": CURRENT_USER, "game": game_name, "score": score})
    print(f"Server: {resp.get('msg')}")

# --- LOGICA SNAKE ---
def snake_game(stdscr):
    try: curses.curs_set(0)
    except: pass
    stdscr.nodelay(1); stdscr.timeout(100)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0); w.keypad(1); w.timeout(100) 
    
    snake = [[sh//2, sw//2], [sh//2, sw//2-1]]
    food = [sh//2, sw//2+5]
    try: w.addch(food[0], food[1], 'O')
    except: pass
    
    key = curses.KEY_RIGHT; score = 0

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key
        new_head = [snake[0][0], snake[0][1]]
        
        if key == curses.KEY_DOWN: new_head[0] += 1
        if key == curses.KEY_UP: new_head[0] -= 1
        if key == curses.KEY_LEFT: new_head[1] -= 1
        if key == curses.KEY_RIGHT: new_head[1] += 1

        if new_head[0] in [0, sh] or new_head[1] in [0, sw] or new_head in snake:
            curses.endwin()
            print(f"\nGAME OVER! Score: {score}")
            send_score(score, "SNAKE")
            time.sleep(2)
            break
            
        snake.insert(0, new_head)
        if snake[0] == food:
            score += 10; food = None
            while food is None:
                nf = [randint(1, sh-2), randint(1, sw-2)]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], 'O')
        else:
            tail = snake.pop(); w.addch(tail[0], tail[1], ' ')
        try: w.addch(snake[0][0], snake[0][1], '#')
        except: pass

# --- LOGICA DODGE ---
def dodge_game(stdscr):
    try: curses.curs_set(0)
    except: pass
    
    stdscr.nodelay(1); stdscr.timeout(100)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0); w.keypad(1); w.timeout(100) 
    
    px = sw // 2
    py = sh - 2
    asteroids = []
    score = 0

    while True:
        key = w.getch()
        if key == curses.KEY_LEFT and px > 1: px -= 1
        if key == curses.KEY_RIGHT and px < sw - 2: px += 1
        
        w.clear()
        
        if randint(1, 100) < 15: 
            asteroids.append([1, randint(1, sw-2)])
            
        new_asteroids = []
        for a in asteroids:
            a[0] += 1 
            if a[0] == py and a[1] == px: 
                curses.endwin()
                print(f"\nGAME OVER! Scontrato con un asteroide. Score: {score}")
                send_score(score, "DODGE")
                time.sleep(2)
                return 
            
            if a[0] < sh - 1:
                new_asteroids.append(a)
                try: w.addch(a[0], a[1], '*')
                except: pass
            else:
                score += 10 
                
        asteroids = new_asteroids
        try: w.addch(py, px, '^') 
        except: pass

# --- HUB PRINCIPALE ---
def main_menu():
    while True:
        print("\n" + "="*32)
        print(f" BENVENUTO {CURRENT_USER}")
        print("="*32)
        print("Seleziona un gioco:")
        print("1. Snake")
        print("2. Dodge")
        print("3. Esci dalla Console")
        choice = input("Scelta: ")
        
        if choice == '1':
            curses.wrapper(snake_game)
        elif choice == '2':
            curses.wrapper(dodge_game)
        elif choice == '3':
            print("Alla prossima!")
            sys.exit()
        else:
            print("Scelta non valida.")

if __name__ == "__main__":
    try: 
        auth_menu()
        main_menu()
    except KeyboardInterrupt: 
        print("\nChiusura forzata :(")
