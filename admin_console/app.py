from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Настройки подключения к базе данных
DB_CONFIG = {
    'dbname': 'your_dbname',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем данные из таблицы reg_requests
    cur.execute('SELECT id, username, req_type, text, status, date FROM webplatform.reg_requests')
    reg_requests = cur.fetchall()

    # Получаем данные из таблицы users
    cur.execute('SELECT id, username, first_name, last_name, fathers_name, mail, status, last_login, grants FROM webplatform.users')
    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        'reg_requests': reg_requests,
        'users': users
    })

@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    if data['table'] == 'reg_requests':
        cur.execute('''
            UPDATE webplatform.reg_requests
            SET status = %s
            WHERE id = %s
        ''', (data['status'], data['id']))
    elif data['table'] == 'users':
        cur.execute('''
            UPDATE webplatform.users
            SET mail = %s, status = %s, grants = %s
            WHERE id = %s
        ''', (data['mail'], data['status'], data['grants'], data['id']))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
