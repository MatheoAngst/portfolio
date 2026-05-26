from flask import Flask, render_template, request, jsonify
import sqlite3
import json

app = Flask(__name__)
DB_FILE = 'zina_lounge.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tables 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL, 
                  is_active INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  table_id INTEGER, 
                  item_name TEXT, 
                  price REAL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(table_id) REFERENCES tables(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL, 
                  res_date TEXT NOT NULL,
                  res_time TEXT NOT NULL,
                  guests INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  table_name TEXT,
                  amount REAL,
                  method TEXT,
                  items_json TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

@app.route('/api/tables', methods=['GET', 'POST'])
def manage_tables():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Nom manquant'}), 400
        c.execute('INSERT INTO tables (name) VALUES (?)', (name,))
        conn.commit()
        table_id = c.lastrowid
        conn.close()
        return jsonify({'id': table_id, 'name': name})
    else:
        tables = c.execute('SELECT * FROM tables WHERE is_active = 1').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in tables])

@app.route('/api/tables/<int:table_id>', methods=['DELETE'])
def delete_table(table_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM orders WHERE table_id = ?', (table_id,))
    c.execute('DELETE FROM tables WHERE id = ?', (table_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/tables/<int:table_id>/orders', methods=['GET'])
def get_table_orders(table_id):
    conn = get_db_connection()
    c = conn.cursor()
    orders = c.execute('SELECT * FROM orders WHERE table_id = ? ORDER BY timestamp DESC', (table_id,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in orders])

@app.route('/api/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    table_id = data.get('table_id')
    item_name = data.get('item_name')
    price = data.get('price')
    if not table_id or not item_name:
        return jsonify({'error': 'Donnees invalides'}), 400
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO orders (table_id, item_name, price) VALUES (?, ?, ?)', (table_id, item_name, price))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/pay', methods=['POST'])
def pay_orders():
    data = request.get_json()
    table_id = data.get('table_id')
    table_name = data.get('table_name')
    method = data.get('method')
    order_ids = data.get('order_ids')
    
    if not table_id or not method or not order_ids:
        return jsonify({'error': 'Donnees manquantes'}), 400
        
    conn = get_db_connection()
    c = conn.cursor()
    
    placeholders = ','.join('?' for _ in order_ids)
    query = f'SELECT * FROM orders WHERE id IN ({placeholders}) AND table_id = ?'
    params = order_ids + [table_id]
    
    orders = c.execute(query, params).fetchall()
    
    if not orders:
        conn.close()
        return jsonify({'error': 'Commandes introuvables'}), 400
        
    total_amount = sum(o['price'] for o in orders)
    items_list = [{'item_name': o['item_name'], 'price': o['price']} for o in orders]
    items_json = json.dumps(items_list)
    
    c.execute('INSERT INTO payments (table_name, amount, method, items_json) VALUES (?, ?, ?, ?)',
              (table_name, total_amount, method, items_json))
              
    c.execute(f'DELETE FROM orders WHERE id IN ({placeholders}) AND table_id = ?', params)
    
    remaining = c.execute('SELECT COUNT(*) FROM orders WHERE table_id = ?', (table_id,)).fetchone()[0]
    table_closed = False
    if remaining == 0:
        c.execute('UPDATE tables SET is_active = 0 WHERE id = ?', (table_id,))
        table_closed = True
        
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'table_closed': table_closed})

@app.route('/api/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    c = conn.cursor()
    total_revenue = c.execute('SELECT SUM(amount) FROM payments').fetchone()[0] or 0.0
    total_especes = c.execute('SELECT SUM(amount) FROM payments WHERE method="ESPECES"').fetchone()[0] or 0.0
    total_tpe = c.execute('SELECT SUM(amount) FROM payments WHERE method="TPE"').fetchone()[0] or 0.0
    payments = c.execute('SELECT * FROM payments ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify({
        'total_revenue': total_revenue,
        'total_especes': total_especes,
        'total_tpe': total_tpe,
        'payments': [dict(p) for p in payments]
    })

@app.route('/api/reservations', methods=['GET', 'POST'])
def manage_reservations():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        res_date = data.get('date')
        res_time = data.get('time')
        guests = data.get('guests')
        
        if not name or not res_date or not res_time or not guests:
            return jsonify({'error': 'Donnees manquantes'}), 400
            
        c.execute('INSERT INTO reservations (name, res_date, res_time, guests) VALUES (?, ?, ?, ?)', 
                  (name, res_date, res_time, guests))
        conn.commit()
        res_id = c.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': res_id})
    else:
        reservations = c.execute('SELECT * FROM reservations ORDER BY res_date ASC, res_time ASC').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in reservations])

@app.route('/api/reservations/<int:res_id>', methods=['DELETE'])
def delete_reservation(res_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM reservations WHERE id = ?', (res_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def reset_all():
    data = request.get_json()
    if data.get('code') == '1234':
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM orders')
        c.execute('DELETE FROM tables')
        c.execute('DELETE FROM reservations')
        c.execute('DELETE FROM payments')
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False}), 403

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)