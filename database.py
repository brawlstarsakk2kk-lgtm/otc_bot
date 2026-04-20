import sqlite3

conn = sqlite3.connect("otc_bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    wallet TEXT,
    wallet_network TEXT,
    ref_by INTEGER,
    balance REAL DEFAULT 0
)
""")

cur.execute(""""
CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    currency TEXT,
    status TEXT DEFAULT 'pending',
    counterparty INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS referrals (
    user_id INTEGER,
    ref_count INTEGER DEFAULT 0,
    earned REAL DEFAULT 0
)
""")

conn.commit()

def add_user(user_id, ref_by=None):
    cur.execute("INSERT OR IGNORE INTO users (id, ref_by) VALUES (?, ?)", (user_id, ref_by))
    conn.commit()

def set_wallet(user_id, network, address):
    cur.execute("UPDATE users SET wallet=?, wallet_network=? WHERE id=?", (address, network, user_id))
    conn.commit()

def create_deal(user_id, amount, currency):
    cur.execute("INSERT INTO deals (user_id, amount, currency) VALUES (?, ?, ?)", (user_id, amount, currency))
    conn.commit()
    return cur.lastrowid

def get_deal(deal_id):
    cur.execute("SELECT * FROM deals WHERE id=?", (deal_id,))
    return cur.fetchone()