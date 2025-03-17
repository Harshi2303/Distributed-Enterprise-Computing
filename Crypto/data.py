import sqlite3
import datetime

# Configure the database path (use an absolute path or relative path as needed)
DB_PATH = 'crypto.db'

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS crypto (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        abbreviation TEXT UNIQUE,
                        description TEXT,
                        market_cap REAL,
                        trading_volume REAL,
                        opening_price REAL,
                        timestamp TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        purchase_power REAL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        crypto_id INTEGER,
                        quantity REAL,
                        purchase_price REAL,
                        timestamp TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(crypto_id) REFERENCES crypto(id))''')

    # Add a test user
    username = 'testuser'
    password = 'testpass'
    purchase_power = 10000.0

    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    if not cursor.fetchone():
        cursor.execute('''INSERT INTO users (username, password, purchase_power)
                         VALUES (?, ?, ?)''', (username, password, purchase_power))
        print(f"Test user '{username}' added with ${purchase_power} purchase power.")

    # Add sample cryptocurrencies if table is empty
    cursor.execute('SELECT COUNT(*) FROM crypto')
    if cursor.fetchone()[0] == 0:
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        sample_coins = [
            ('Bitcoin', 'BTC', 'First decentralized cryptocurrency', 1000000000.0, 50000000.0, 50000.0, current_date),
            ('Ethereum', 'ETH', 'Smart contract platform', 500000000.0, 30000000.0, 3000.0, current_date),
            ('Ripple', 'XRP', 'Payment protocol', 100000000.0, 10000000.0, 0.5, current_date),
            ('Indu', 'I', 'Sample cryptocurrency', 10000000.0, 5000000.0, 1.0, current_date)
        ]
        cursor.executemany('''INSERT INTO crypto (name, abbreviation, description, market_cap, trading_volume, opening_price, timestamp)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''', sample_coins)
        print("Sample cryptocurrencies added.")

    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    setup_database()