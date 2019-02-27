import sqlite3

def add_user(id, nick, nimi, saldo):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?,?,?,?)", (id, nick, nimi, saldo))
    conn.commit()
    conn.close()


def add_transaction(user, tuote, aika, hinta):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions VALUES (?,?,?,?)", (user, tuote, hinta, aika))
    conn.commit()
    conn.close()


def add_item(nimi, hinta, maara):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    c.execute("INSERT INTO inventory VALUES (?,?,?)", (nimi, hinta, maara))
    conn.commit()
    conn.close()


def update_balance(user, delta):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    saldo = c.execute("SELECT saldo FROM users WHERE id = ?", (user,)).fetchone()[0]
    c.execute("UPDATE users SET saldo = ? WHERE id = ?", (saldo + delta, user))
    conn.commit()
    conn.close()


def delete_inventory():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    c.execute("DELETE FROM inventory")
    conn.commit()
    conn.close()


def get_user(id):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    cur = c.execute("SELECT * from users WHERE id=?", (id,)).fetchall()
    conn.close()
    return cur

def get_balance(id):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    cur = c.execute("SELECT saldo FROM users WHERE id=?", (id,)).fetchall()[0][0]
    conn.close()
    return cur

def get_price(nimi):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    cur = c.execute("SELECT hinta FROM inventory WHERE nimi=?", (nimi,)).fetchall()[0][0]
    conn.close()
    return cur

def get_items():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    cur = c.execute("SELECT * FROM inventory").fetchall()
    conn.close()
    return cur

def update_stock(nimi, delta):
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    cur = c.execute("SELECT maara FROM inventory WHERE nimi=?", (nimi,)).fetchone()[0]
    c.execute("UPDATE inventory SET maara = ? WHERE nimi = ?", (cur + delta, nimi))
    conn.commit()
    conn.close()


def print_users():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    for row in c.execute("SELECT * FROM users"):
        print(row)
    conn.close()


def print_inventory():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    for row in c.execute("SELECT * FROM inventory"):
        print(row)
    conn.close()


def print_transactions():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    for row in c.execute("SELECT * FROM transactions"):
        print(row)
    conn.close()



def create_database():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    c.execute("CREATE TABLE inventory (nimi text, hinta int, maara int)")
    c.execute("CREATE TABLE users (id int, nick text, nimi text, saldo int)")
    c.execute("CREATE TABLE transactions (user int, tuote text, hinta int, aika text)")
    conn.commit()
    conn.close()

def add_candy():
    conn = sqlite3.connect('kiltis.db')
    c = conn.cursor()
    tuotteet = [('Tupla', 60, 20),
                ('Limu', 100, 40),
                ('Nuudelit', 70, 7),
                ('Snickers', 70, 10)]

    c.executemany("INSERT INTO inventory VALUES (?,?,?)", tuotteet)
    conn.commit()
    conn.close()