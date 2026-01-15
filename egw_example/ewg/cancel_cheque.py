import base64
import json
from urllib.parse import unquote, urlparse

@app.route('/cancellationCheque.aspx')
def cancellation_cheque():
    """
    Страница отмены операции с чеком
    Получает данные в параметре data (base64 encoded JSON)
    """
    # Получаем данные из параметра
    data_base64 = request.args.get('data')
    
    if not data_base64:
        return "Данные не указаны", 400
    
    try:
        # Декодируем URL-encoded строку
        data_base64 = unquote(data_base64)
        
        # Декодируем Base64
        # Добавляем padding если нужно
        missing_padding = len(data_base64) % 4
        if missing_padding:
            data_base64 += '=' * (4 - missing_padding)
        
        # Декодируем Base64
        data_bytes = base64.b64decode(data_base64)
        
        # Декодируем JSON
        data = json.loads(data_bytes.decode('utf-8'))
        
        # Извлекаем данные
        error_code = data.get('RC', '')  # Код ошибки
        error_text = data.get('RC_TRANS_CRYPT', '')  # Текст ошибки
        back_url = data.get('BACKREF', '/')  # URL для возврата
        
        # Исправляем кодировку текста ошибки если нужно
        if error_text:
            # Проверяем, содержит ли строка UTF-8 байты как текст
            if any(ord(c) > 127 for c in error_text):
                try:
                    error_text = error_text.encode('latin-1').decode('utf-8')
                except:
                    pass
        
        # Проверяем валидность back_url
        if not is_valid_url(back_url):
            back_url = '/'
        
        # Подготавливаем контекст для шаблона
        context = {
            'error_code': error_code,
            'error_text': error_text,
            'back_url': back_url,
            'current_year': datetime.now().year,
            'site_name': 'Платежный шлюз'
        }
        
        return render_template('cancellation_cheque.html', **context)
        
    except Exception as e:
        print(f"Error processing cancellation cheque: {e}")
        # В случае ошибки показываем простую страницу
        return render_template('cancellation_cheque.html', 
                             error_code='ERROR',
                             error_text='Ошибка обработки запроса',
                             back_url='/',
                             current_year=datetime.now().year,
                             site_name='Платежный шлюз')

def is_valid_url(url):
    """Проверка валидности URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
