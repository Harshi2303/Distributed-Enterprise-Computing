import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Configure the database path (use an absolute path or relative path as needed)
DB_PATH = 'crypto.db'

class CryptoServer:
    def __init__(self, root):
        self.root = root
        self.root.title('Crypto Server')
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        # Create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS crypto
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             name TEXT,
                             abbreviation TEXT,
                             description TEXT,
                             market_cap REAL,
                             trading_volume REAL,
                             opening_price REAL,
                             timestamp TEXT)''')
        self.conn.commit()
        self.create_widgets()

    def create_widgets(self):
        self.name_label = tk.Label(self.root, text='Name')
        self.name_label.grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.abbr_label = tk.Label(self.root, text='Abbreviation')
        self.abbr_label.grid(row=1, column=0, padx=5, pady=5)
        self.abbr_entry = tk.Entry(self.root)
        self.abbr_entry.grid(row=1, column=1, padx=5, pady=5)

        self.desc_label = tk.Label(self.root, text='Description')
        self.desc_label.grid(row=2, column=0, padx=5, pady=5)
        self.desc_entry = tk.Entry(self.root)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)

        self.market_cap_label = tk.Label(self.root, text='Market Cap')
        self.market_cap_label.grid(row=3, column=0, padx=5, pady=5)
        self.market_cap_entry = tk.Entry(self.root)
        self.market_cap_entry.grid(row=3, column=1, padx=5, pady=5)

        self.trading_volume_label = tk.Label(self.root, text='Trading Volume')
        self.trading_volume_label.grid(row=4, column=0, padx=5, pady=5)
        self.trading_volume_entry = tk.Entry(self.root)
        self.trading_volume_entry.grid(row=4, column=1, padx=5, pady=5)

        self.opening_price_label = tk.Label(self.root, text='Opening Price')
        self.opening_price_label.grid(row=5, column=0, padx=5, pady=5)
        self.opening_price_entry = tk.Entry(self.root)
        self.opening_price_entry.grid(row=5, column=1, padx=5, pady=5)

        self.timestamp_label = tk.Label(self.root, text='Timestamp')
        self.timestamp_label.grid(row=6, column=0, padx=5, pady=5)
        self.timestamp_entry = tk.Entry(self.root)
        self.timestamp_entry.grid(row=6, column=1, padx=5, pady=5)

        self.add_button = tk.Button(self.root, text='Add Coin', command=self.add_coin)
        self.add_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.view_button = tk.Button(self.root, text='View All Coins', command=self.view_coins)
        self.view_button.grid(row=8, column=0, columnspan=2, pady=10)

    def add_coin(self):
        try:
            name = self.name_entry.get()
            abbreviation = self.abbr_entry.get().strip().upper()
            description = self.desc_entry.get()
            market_cap = float(self.market_cap_entry.get())
            trading_volume = float(self.trading_volume_entry.get())
            opening_price = float(self.opening_price_entry.get())
            timestamp = self.timestamp_entry.get()

            self.cursor.execute('''INSERT INTO crypto (name, abbreviation, description, market_cap, trading_volume, opening_price, timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                (name, abbreviation, description, market_cap, trading_volume, opening_price, timestamp))

            self.conn.commit()
            messagebox.showinfo('Success', 'Coin added successfully')
            for entry in [self.name_entry, self.abbr_entry, self.desc_entry, 
                         self.market_cap_entry, self.trading_volume_entry, 
                         self.opening_price_entry, self.timestamp_entry]:
                entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror('Error', 'Please enter valid numeric values for Market Cap, Trading Volume, and Opening Price')
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {e}')

    def view_coins(self):
        view_window = tk.Toplevel(self.root)
        view_window.title('All Cryptocurrencies')
        view_window.geometry('800x400')

        columns = ('ID', 'Name', 'Abbr', 'Description', 'Market Cap', 'Volume', 'Price', 'Timestamp')
        tree = ttk.Treeview(view_window, columns=columns, show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('Abbr', text='Abbreviation')
        tree.heading('Description', text='Description')
        tree.heading('Market Cap', text='Market Cap')
        tree.heading('Volume', text='Trading Volume')
        tree.heading('Price', text='Opening Price')
        tree.heading('Timestamp', text='Timestamp')

        tree.column('ID', width=50)
        tree.column('Name', width=100)
        tree.column('Abbr', width=80)
        tree.column('Description', width=150)
        tree.column('Market Cap', width=100)
        tree.column('Volume', width=100)
        tree.column('Price', width=80)
        tree.column('Timestamp', width=120)

        self.cursor.execute('SELECT * FROM crypto')
        coins = self.cursor.fetchall()

        if coins:
            for coin in coins:
                tree.insert('', tk.END, values=coin)
        else:
            tree.insert('', tk.END, values=('No coins available', '', '', '', '', '', '', ''))

        scrollbar = ttk.Scrollbar(view_window, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass

if __name__ == '__main__':
    root = tk.Tk()
    app = CryptoServer(root)
    root.mainloop()