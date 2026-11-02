import sqlite3, hashlib
from datetime import datetime
import flet as ft

DB = "fashion_marketplace.db"


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    con = connect()
    con.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'buyer'
    );
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        quantity INTEGER NOT NULL CHECK(quantity >= 0),
        description TEXT,
        image_url TEXT,
        FOREIGN KEY(seller_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY(buyer_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    ''')
    demo = [
        ('Demo Buyer', 'buyer@example.com', password_hash('buyer123'), 'buyer'),
        ('Demo Seller', 'seller@example.com', password_hash('seller123'), 'seller'),
        ('Administrator', 'admin@example.com', password_hash('admin123'), 'admin')
    ]
    for row in demo:
        con.execute('INSERT OR IGNORE INTO users(name,email,password,role) VALUES(?,?,?,?)', row)
    seller = con.execute("SELECT id FROM users WHERE email='seller@example.com'").fetchone()
    if seller and con.execute('SELECT COUNT(*) c FROM products').fetchone()['c'] == 0:
        products = [
            (seller['id'], 'Classic Handbag', 'Bags', 18500, 12, 'Elegant everyday handbag.', ''),
            (seller['id'], 'Casual Dress', 'Dresses', 22000, 8, 'Comfortable casual fashion dress.', ''),
            (seller['id'], 'Leather Sandals', 'Shoes', 12500, 15, 'Simple and comfortable sandals.', ''),
            (seller['id'], 'Modest Abaya', 'Abaya', 30000, 6, 'Flowing modest abaya.', '')
        ]
        con.executemany('INSERT INTO products(seller_id,name,category,price,quantity,description,image_url) VALUES(?,?,?,?,?,?,?)', products)
    con.commit(); con.close()


def money(n):
    return f"₦{n:,.2f}"


def main(page: ft.Page):
    init_db()
    page.title = 'Aji Fashion Marketplace'
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    # Keep the interface usable on smaller phone screens when the app is
    # opened through a mobile browser.
    page.adaptive = True
    state = {'user': None, 'cart': {}}

    def notify(message):
        page.snack_bar = ft.SnackBar(ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def login():
        email = ft.TextField(label='Email', width=360)
        pwd = ft.TextField(label='Password', password=True, can_reveal_password=True, width=360)
        msg = ft.Text()
        def submit(e):
            con = connect()
            user = con.execute('SELECT * FROM users WHERE email=? AND password=?',
                               (email.value.strip().lower(), password_hash(pwd.value))).fetchone()
            con.close()
            if user:
                state['user'] = dict(user); marketplace()
            else:
                msg.value = 'Invalid email or password.'; msg.color = ft.Colors.RED; page.update()
        def demo(e):
            email.value = 'buyer@example.com'; pwd.value = 'buyer123'; page.update()
        page.controls.clear()
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("AJI FASHION MARKETPLACE", size=28, weight=ft.FontWeight.BOLD),
                ft.Text('Buyer • Seller • Administrator'), email, pwd,
                ft.Row([ft.ElevatedButton('Login', on_click=submit), ft.OutlinedButton('Demo Buyer', on_click=demo)]), msg
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
            alignment=ft.alignment.center, padding=40, expand=True))
        page.update()

    def header(title):
        role = state['user']['role']
        buttons = [
            ft.ElevatedButton('Marketplace', on_click=lambda e: marketplace()),
            ft.ElevatedButton('Cart', on_click=lambda e: cart()),
            ft.ElevatedButton('Orders', on_click=lambda e: orders())
        ]
        if role in ('seller','admin'):
            buttons.append(ft.ElevatedButton('Seller', on_click=lambda e: seller_dashboard()))
        if role == 'admin':
            buttons.append(ft.ElevatedButton('Admin', on_click=lambda e: admin_dashboard()))
        buttons.append(ft.OutlinedButton('Logout', on_click=lambda e: login()))
        return ft.Container(ft.Column([
            ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"Signed in as {state['user']['name']} ({role})"),
            ft.Row(buttons, wrap=True)
        ]), padding=15)

    def get_products(search=''):
        con = connect()
        if search:
            rows = con.execute('''SELECT p.*, u.name seller FROM products p JOIN users u ON p.seller_id=u.id
                                  WHERE p.name LIKE ? OR p.category LIKE ? ORDER BY p.id DESC''',
                               (f'%{search}%', f'%{search}%')).fetchall()
        else:
            rows = con.execute('''SELECT p.*, u.name seller FROM products p JOIN users u ON p.seller_id=u.id
                                  ORDER BY p.id DESC''').fetchall()
        con.close(); return rows

    def marketplace():
        search = ft.TextField(label='Search by product or category', expand=True)
        listing = ft.Column()
        def refresh(e=None):
            listing.controls = []
            for p in get_products(search.value.strip()):
                pid = p['id']
                def add(e, pid=pid, name=p['name'], stock=p['quantity']):
                    if stock <= 0: notify('Product is out of stock.'); return
                    state['cart'][pid] = state['cart'].get(pid, 0) + 1
                    notify(f'{name} added to cart.')
                listing.controls.append(ft.Card(ft.Container(ft.Column([
                    ft.Text(p['name'], size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{p['category']} • Seller: {p['seller']}"),
                    ft.Text(money(p['price']), size=16),
                    ft.Text(p['description'] or ''),
                    ft.Text(f"Available: {p['quantity']}"),
                    ft.ElevatedButton('Add to Cart', on_click=add)
                ]), padding=14)))
            page.update()
        search.on_submit = refresh
        page.controls.clear(); page.add(header('Fashion Marketplace'), ft.Container(ft.Column([
            ft.Row([search, ft.ElevatedButton('Search', on_click=refresh)]), listing
        ]), padding=20)); refresh()

    def cart():
        con = connect(); ids = list(state['cart'].keys()); rows = []
        if ids:
            q = ','.join('?'*len(ids)); rows = con.execute(f'SELECT * FROM products WHERE id IN ({q})', ids).fetchall()
        con.close(); controls=[]; total=0
        for p in rows:
            qty = state['cart'][p['id']]; sub=qty*p['price']; total+=sub
            def remove(e,pid=p['id']): state['cart'].pop(pid,None); cart()
            controls.append(ft.Row([ft.Text(f"{p['name']} × {qty}", expand=True), ft.Text(money(sub)), ft.IconButton(ft.Icons.DELETE,on_click=remove)]))
        if not controls: controls=[ft.Text('Your cart is empty.')]
        else:
            controls += [ft.Divider(), ft.Text(f'Total: {money(total)}',size=20,weight=ft.FontWeight.BOLD),
                         ft.ElevatedButton('Checkout',on_click=lambda e: checkout(rows,total))]
        page.controls.clear(); page.add(header('Shopping Cart'),ft.Container(ft.Column(controls),padding=20)); page.update()

    def checkout(rows,total):
        con=connect()
        try:
            for p in rows:
                if p['quantity'] < state['cart'][p['id']]:
                    con.close(); notify(f"Insufficient stock for {p['name']}."); return
            cur=con.execute('INSERT INTO orders(buyer_id,total,status,created_at) VALUES(?,?,?,?)',
                            (state['user']['id'],total,'Pending',datetime.now().isoformat(timespec='seconds')))
            oid=cur.lastrowid
            for p in rows:
                qty=state['cart'][p['id']]
                con.execute('INSERT INTO order_items(order_id,product_id,quantity,unit_price) VALUES(?,?,?,?)',(oid,p['id'],qty,p['price']))
                con.execute('UPDATE products SET quantity=quantity-? WHERE id=?',(qty,p['id']))
            con.commit(); state['cart'].clear(); con.close(); notify(f'Order #{oid} placed successfully.'); orders()
        except Exception as ex:
            con.rollback(); con.close(); notify(f'Checkout error: {ex}')

    def orders():
        con=connect()
        if state['user']['role']=='buyer':
            rows=con.execute('SELECT * FROM orders WHERE buyer_id=? ORDER BY id DESC',(state['user']['id'],)).fetchall()
        else:
            rows=con.execute('SELECT o.*,u.name buyer FROM orders o JOIN users u ON o.buyer_id=u.id ORDER BY o.id DESC').fetchall()
        con.close(); controls=[ft.Text('Orders',size=24,weight=ft.FontWeight.BOLD)]
        for o in rows:
            buyer=f" • Buyer: {o['buyer']}" if 'buyer' in o.keys() else ''
            controls.append(ft.Card(ft.Container(ft.Column([
                ft.Text(f"Order #{o['id']} — {money(o['total'])}",weight=ft.FontWeight.BOLD),
                ft.Text(f"Status: {o['status']}{buyer}"), ft.Text(f"Date: {o['created_at']}")
            ]),padding=12)))
        page.controls.clear(); page.add(header('Order Management'),ft.Container(ft.Column(controls),padding=20)); page.update()

    def seller_dashboard():
        name=ft.TextField(label='Product name'); category=ft.TextField(label='Category'); price=ft.TextField(label='Price'); qty=ft.TextField(label='Quantity'); desc=ft.TextField(label='Description',multiline=True); msg=ft.Text()
        def add(e):
            try:
                con=connect(); con.execute('INSERT INTO products(seller_id,name,category,price,quantity,description,image_url) VALUES(?,?,?,?,?,?,?)',
                    (state['user']['id'],name.value,category.value,float(price.value),int(qty.value),desc.value,'')); con.commit(); con.close()
                msg.value='Product added successfully.'; msg.color=ft.Colors.GREEN
                for x in (name,category,price,qty,desc): x.value=''
            except Exception: msg.value='Please enter valid product information.'; msg.color=ft.Colors.RED
            page.update()
        page.controls.clear(); page.add(header('Seller Dashboard'),ft.Container(ft.Column([
            ft.Text('Add Product',size=22,weight=ft.FontWeight.BOLD),name,category,price,qty,desc,ft.ElevatedButton('Add Product',on_click=add),msg
        ]),padding=20)); page.update()

    def admin_dashboard():
        con=connect(); u=con.execute('SELECT COUNT(*) c FROM users').fetchone()['c']; p=con.execute('SELECT COUNT(*) c FROM products').fetchone()['c']; o=con.execute('SELECT COUNT(*) c FROM orders').fetchone()['c']; con.close()
        page.controls.clear(); page.add(header('Administrator Dashboard'),ft.Container(ft.Column([
            ft.Text(f'Users: {u}',size=20),ft.Text(f'Products: {p}',size=20),ft.Text(f'Orders: {o}',size=20)
        ]),padding=20)); page.update()

    login()

if __name__ == '__main__':
    ft.app(target=main)
