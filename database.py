# database.py - Automated Local Cache
import sqlite3
import time

DB_NAME = "wallet_analysis.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet_profiles (
            address TEXT PRIMARY KEY,
            chain TEXT,
            win_rate REAL,
            avg_roi REAL,
            total_launches INTEGER,
            entry_timing_seconds INTEGER,
            holding_duration_minutes INTEGER,
            realized_profit_usd REAL,
            elite_score INTEGER,
            last_active INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            wallet TEXT,
            token TEXT,
            action TEXT,
            size_usd REAL
        )
    """)
    conn.commit()
    conn.close()

def seed_wallets():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    profiles = [
        ("6x7R8pQnKzM9L3v7x9vKpQmNzM", "solana", 0.79, 16.8, 42, 12, 180, 425000.0, 95, int(time.time())),
        ("Hj9s2wKz7mK91vX0x8bF2dE77a", "solana", 0.65, 12.1, 19, 45, 1440, 185000.0, 88, int(time.time())),
        ("0x7a58c59424135253365432b4b2", "ethereum", 0.82, 14.5, 31, 8, 90, 310000.0, 91, int(time.time()))
    ]
    for row in profiles:
        cursor.execute("INSERT OR REPLACE INTO wallet_profiles VALUES (?,?,?,?,?,?,?,?,?,?)", row)
    conn.commit()
    conn.close()

init_db()
seed_wallets()
