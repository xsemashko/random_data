from flask import Flask, render_template, request, jsonify
import psycopg2
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Настройки подключения к базе данных


def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Функция для отправки email
def send_email(addr_to, msg_subj, msg_text):
    addr_from = "viy@sber-bank.by"
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = msg_subj
    body = msg_text
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('10.244.216.42', 25)
    server.send_message(msg)
    server.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем параметры сортировки и поиска из запроса
    sort_order = request.args.get('sort', 'DESC')  # По умолчанию сортировка по убыванию
    search_username = request.args.get('search', '')

    # Получаем данные из таблицы reg_requests
    cur.execute(f'''
        SELECT id, username, req_type, text, status, date 
        FROM webplatform.reg_requests
        WHERE username ILIKE %s
        ORDER BY id {sort_order}
    ''', (f'%{search_username}%',))
    reg_requests = cur.fetchall()

    # Получаем данные из таблицы users
    cur.execute(f'''
        SELECT id, username, first_name, last_name, fathers_name, mail, status, last_login, grants 
        FROM webplatform.users
        WHERE username ILIKE %s
        ORDER BY id {sort_order}
    ''', (f'%{search_username}%',))
    users = cur.fetchall()

    # Получаем данные из таблицы apps
    cur.execute(f'''
        SELECT id, app, alias 
        FROM webplatform.apps
        ORDER BY id {sort_order}
    ''')
    apps = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        'reg_requests': reg_requests,
        'users': users,
        'apps': apps
    })

@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if data['table'] == 'reg_requests':
            cur.execute('''
                UPDATE webplatform.reg_requests
                SET status = %s
                WHERE id = %s
            ''', (data.get('status'), data['id']))
        elif data['table'] == 'users':
            cur.execute('''
                UPDATE webplatform.users
                SET mail = %s, status = %s, grants = %s
                WHERE id = %s
            ''', (data.get('mail'), data.get('status'), data.get('grants'), data['id']))

        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/send_notifications', methods=['POST'])
def send_notifications():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Выбираем пользователей, которым нужно отправить уведомления
        sql = """
            SELECT u.mail, u.username 
            FROM webplatform.users u, webplatform.reg_requests r 
            WHERE 
                u.grants IS NOT NULL
                AND u.status = 'I'
                AND r.req_type = 'REGISTER'
                AND r.status = 'A'
                AND r.username = u.username
        """
        cur.execute(sql)
        emails_usernames = cur.fetchall()

        # Отправляем уведомления и обновляем статусы
        for email_username in emails_usernames:
            mail_text = """
Приветствую!
        
Рады сообщить, что Ваша заявка на регистрацию в Веб-платформе ВИЮ одобрена.
Можете повторить попытку входа.

Данное сообщение сгенерировано автоматически, пожалуйста не отвечайте на него."""
            send_email(email_username[0], 'Одобрение заявки на Веб-платформе ВИЮ', mail_text)

            # Обновляем статусы
            cur.execute(f"UPDATE webplatform.users SET status = 'A' WHERE username = '{email_username[1]}'")
            cur.execute(f"UPDATE webplatform.reg_requests SET status = 'I' WHERE username = '{email_username[1]}' AND req_type = 'REGISTER'")
            conn.commit()

        return jsonify({'success': True, 'message': 'Уведомления отправлены успешно!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
