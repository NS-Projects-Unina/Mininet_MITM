from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'supercalifragilistichespiralidoso'
DB_NAME = "arcade.db"

PRODUCTS = [
    {"id": 1, "name": "Pacchetto Caramelle", "price": 50, "desc": "Premio più scadente (gioca di piu'!)."},
    {"id": 2, "name": "T-Shirt Arcade", "price": 500, "desc": "Cotone 100%."},
    {"id": 3, "name": "Playstation 4", "price": 5000, "desc": "Usata, come nuova."},
    {"id": 4, "name": "LAMBORGHINI", "price": 1000000, "desc": "Solo per veri HACKER."}
]

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row	
    # Dico a SQLite di restituire i risultati come se fossero dei dizionari, così posso accedere 
    # ai campi usando il loro nome effettivo, e non l'indice della colonna della tabella!
    return conn

@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_db().execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', 
                                (request.form['username'], 
                                 hashlib.sha256(request.form['password'].encode()).hexdigest())).fetchone()
        if user:
            session['user'] = user['username']
            session['score'] = user['total_score']
            return redirect(url_for('index'))
        flash('Errore Login', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password_hash, total_score) VALUES (?, ?, 0)",
                         (request.form['username'], 
                          hashlib.sha256(request.form['password'].encode()).hexdigest()))
            conn.commit()
            flash('Registrato! Ora accedi.', 'success')
            return redirect(url_for('login'))
        except: flash('Username esistente', 'danger')
    return render_template('register.html')

@app.route('/buy/<int:pid>')
def buy(pid):
    if 'user' not in session: return redirect(url_for('login'))
    prod = next((p for p in PRODUCTS if p['id'] == pid), None)
    
    conn = get_db()
    curr_score = conn.execute('SELECT total_score FROM users WHERE username=?', (session['user'],)).fetchone()[0]
    
    if curr_score >= prod['price']:
        conn.execute('UPDATE users SET total_score = ? WHERE username = ?', (curr_score - prod['price'], session['user']))
        conn.commit()
        session['score'] = curr_score - prod['price']
        flash(f"Acquistato: {prod['name']}!", 'success')
    else:
        flash("Fondi insufficienti!", 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Porta 80 richiede permessi root (!!Mininet li ha!!)
    app.run(host='0.0.0.0', port=80, debug=False)
