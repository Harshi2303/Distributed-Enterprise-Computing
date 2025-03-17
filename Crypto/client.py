import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Configure the database path (use an absolute path or relative path as needed)
DB_PATH = 'crypto.db'

class CryptoClient:
    def __init__(self, root):
        self.root = root
        self.root.title('Crypto Client')
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_widgets()

    def create_widgets(self):
        self.username_label = tk.Label(self.root, text='Username')
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.root, text='Password')
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.root, show='*')
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.root, text='Login', command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = self.cursor.fetchone()

        if user:
            messagebox.showinfo('Success', 'Login successful')
            self.user_id = user[0]
            self.username = username
            self.password = password
            self.purchase_power = user[3]
            self.create_trading_interface()
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def create_trading_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f'Crypto Client - {self.username}')

        self.coin_label = tk.Label(self.root, text='Coin (Abbr)')
        self.coin_label.grid(row=0, column=0, padx=5, pady=5)
        self.coin_entry = tk.Entry(self.root)
        self.coin_entry.grid(row=0, column=1, padx=5, pady=5)

        self.quantity_label = tk.Label(self.root, text='Quantity')
        self.quantity_label.grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        self.buy_button = tk.Button(self.root, text='Buy', command=self.buy_coin)
        self.buy_button.grid(row=2, column=0, padx=5, pady=5)

        self.sell_button = tk.Button(self.root, text='Sell', command=self.sell_coin)
        self.sell_button.grid(row=2, column=1, padx=5, pady=5)

        self.view_coins_button = tk.Button(self.root, text='View All Coins', command=self.view_coins)
        self.view_coins_button.grid(row=3, column=0, padx=5, pady=5)

        self.view_transactions_button = tk.Button(self.root, text='View Transactions', command=self.view_transactions)
        self.view_transactions_button.grid(row=3, column=1, padx=5, pady=5)

        self.balance_label = tk.Label(self.root, text=f'Purchase Power: ${self.purchase_power:.2f}')
        self.balance_label.grid(row=4, column=0, columnspan=2, pady=5)

    def buy_coin(self):
        try:
            coin = self.coin_entry.get().strip().upper()
            quantity = float(self.quantity_entry.get())

            self.cursor.execute('SELECT * FROM crypto WHERE abbreviation=?', (coin,))
            crypto = self.cursor.fetchone()

            if not crypto:
                messagebox.showerror('Error', 'Invalid coin abbreviation')
                return

            total_cost = crypto[6] * quantity
            if self.purchase_power >= total_cost:
                self.cursor.execute('''INSERT INTO transactions (user_id, crypto_id, quantity, purchase_price, timestamp)
                                    VALUES (?, ?, ?, ?, ?)''', 
                                    (self.user_id, crypto[0], quantity, crypto[6], '2025-03-12'))
                self.purchase_power -= total_cost
                self.cursor.execute('UPDATE users SET purchase_power=? WHERE id=?', 
                                  (self.purchase_power, self.user_id))
                self.conn.commit()
                self.balance_label.config(text=f'Purchase Power: ${self.purchase_power:.2f}')
                messagebox.showinfo('Success', f'Bought {quantity} {coin} for ${total_cost:.2f}')
                self.coin_entry.delete(0, tk.END)
                self.quantity_entry.delete(0, tk.END)
            else:
                messagebox.showerror('Error', 'Insufficient funds')
        except ValueError:
            messagebox.showerror('Error', 'Please enter a valid quantity')
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {e}')

    def sell_coin(self):
        try:
            coin = self.coin_entry.get().strip().upper()
            quantity = float(self.quantity_entry.get())

            self.cursor.execute('SELECT * FROM crypto WHERE abbreviation=?', (coin,))
            crypto = self.cursor.fetchone()

            if not crypto:
                messagebox.showerror('Error', 'Invalid coin abbreviation')
                return

            self.cursor.execute('''SELECT id, quantity FROM transactions 
                                WHERE user_id=? AND crypto_id=?''', 
                              (self.user_id, crypto[0]))
            transactions = self.cursor.fetchall()
            
            total_owned = sum(trans[1] for trans in transactions)
            
            if total_owned < quantity:
                messagebox.showerror('Error', f'You only own {total_owned} {coin}')
                return
            
            transaction_to_sell = None
            for trans_id, trans_quantity in transactions:
                if trans_quantity >= quantity:
                    transaction_to_sell = (trans_id, trans_quantity)
                    break
            
            if transaction_to_sell:
                trans_id, trans_quantity = transaction_to_sell
                if trans_quantity == quantity:
                    self.cursor.execute('DELETE FROM transactions WHERE id=?', (trans_id,))
                else:
                    new_quantity = trans_quantity - quantity
                    self.cursor.execute('UPDATE transactions SET quantity=? WHERE id=?', 
                                      (new_quantity, trans_id))
                
                total_value = crypto[6] * quantity
                self.purchase_power += total_value
                self.cursor.execute('UPDATE users SET purchase_power=? WHERE id=?', 
                                  (self.purchase_power, self.user_id))
                self.conn.commit()
                self.balance_label.config(text=f'Purchase Power: ${self.purchase_power:.2f}')
                messagebox.showinfo('Success', f'Sold {quantity} {coin} for ${total_value:.2f}')
                self.coin_entry.delete(0, tk.END)
                self.quantity_entry.delete(0, tk.END)
            else:
                messagebox.showerror('Error', 'No suitable transaction found to sell')
        except ValueError:
            messagebox.showerror('Error', 'Please enter a valid quantity')
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {e}')

    def view_coins(self):
        self.cursor.execute('SELECT abbreviation, name, opening_price FROM crypto')
        coins = self.cursor.fetchall()
        coins_str = '\n'.join([f'{coin[0]} ({coin[1]}) - ${coin[2]:.2f}' for coin in coins])
        messagebox.showinfo('All Coins', coins_str if coins_str else 'No coins available')

    def view_transactions(self):
        trans_window = tk.Toplevel(self.root)
        trans_window.title(f'Transaction History - {self.username}')
        trans_window.geometry('800x400')

        columns = ('ID', 'Coin', 'Quantity', 'Price', 'Total', 'Timestamp')
        tree = ttk.Treeview(trans_window, columns=columns, show='headings')

        tree.heading('ID', text='ID')
        tree.heading('Coin', text='Coin Name')
        tree.heading('Quantity', text='Quantity')
        tree.heading('Price', text='Price per Unit')
        tree.heading('Total', text='Total Value')
        tree.heading('Timestamp', text='Timestamp')

        tree.column('ID', width=50)
        tree.column('Coin', width=150)
        tree.column('Quantity', width=100)
        tree.column('Price', width=120)
        tree.column('Total', width=120)
        tree.column('Timestamp', width=150)

        self.cursor.execute('''SELECT t.id, c.name, t.quantity, t.purchase_price, 
                            (t.quantity * t.purchase_price) as total, t.timestamp
                            FROM transactions t
                            JOIN crypto c ON t.crypto_id = c.id
                            WHERE t.user_id=?''', (self.user_id,))
        transactions = self.cursor.fetchall()

        if transactions:
            for trans in transactions:
                tree.insert('', tk.END, values=trans)
        else:
            tree.insert('', tk.END, values=('No transactions', '', '', '', '', ''))

        scrollbar = ttk.Scrollbar(trans_window, orient='vertical', command=tree.yview)
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
    app = CryptoClient(root)
    root.mainloop()