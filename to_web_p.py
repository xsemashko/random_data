from flask import Flask, render_template
import oracledb

app = Flask(__name__)

# Конфигурация подключения к базе данных Oracle
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'dsn': 'your_dsn'
}

def get_data_from_db():
    # Подключение к базе данных
    connection = oracledb.connect(**db_config)
    cursor = connection.cursor()

    # Ваш SQL-запрос
    sql_query = """
    WITH A AS (
        SELECT TO_CHAR(AMND_DATE_first, 'YYYY.MM') as "Месяц в котором была выполнена первая токенизация по карте",
        sum (case when (target_number like '9112388002%' or target_number like '9112388050%' or target_number like '9112388053%'
        or target_number like '9112388051%' or target_number like '9112388052%') then + 1 else 0 end) as "Белкарт Сберкарты",
        sum (case when target_channel = 'z' then + 1 else 0 end) as "Белкарт",
        sum (case when target_channel = 'v' then + 1 else 0 end) as "Visa",
        sum (case when target_channel = 'e' then + 1 else 0 end) as "Mastercard",
        count (1) as "Все карты Банка" from 
        (
            select DISTINCT TARGET_NUMBER, target_channel, FIRST_VALUE (AMND_DATE) OVER (PARTITION BY TARGET_NUMBER ORDER BY AMND_DATE asc) as AMND_DATE_first from lpc.tokenizations_arch 
        )
        GROUP BY TO_CHAR(AMND_DATE_first, 'YYYY.MM')
        ORDER BY 1 desc
    )
    SELECT 'За всё время' as "Месяц в котором была выполнена первая токенизация по карте", sum ("Белкарт Сберкарты") as "Белкарт Сберкарты", sum ("Белкарт") as "Белкарт", sum ("Visa") as "Visa",
    sum ("Mastercard") as "Mastercard", sum ("Все карты Банка") as "Все карты Банка"  FROM A
    UNION ALL
    SELECT * FROM A
    """

    # Выполнение запроса
    cursor.execute(sql_query)
    result = cursor.fetchall()

    # Закрытие соединения
    cursor.close()
    connection.close()

    return result

@app.route('/')
def index():
    # Получение данных из базы данных
    data = get_data_from_db()

    # Передача данных в шаблон
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
