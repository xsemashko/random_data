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
