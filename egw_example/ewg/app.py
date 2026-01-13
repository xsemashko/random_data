from flask import Flask, render_template, request, jsonify, redirect, url_for
import jwt
import base64
import json
from urllib.parse import unquote
from datetime import datetime
import traceback
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class JWTDecoder:
    """Класс для декодирования JWT токена"""
    
    @staticmethod
    def decode_token(token):
        """
        Декодирует JWT токен без проверки подписи
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            payload_b64 = parts[1]
            # Добавляем padding если нужно
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += '=' * padding
            
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_bytes.decode('utf-8'))
            
            return payload
            
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None

def format_amount(amount):
    """Форматирование суммы с запятой"""
    if isinstance(amount, (int, float)):
        return f"{amount:.2f}".replace('.', ',')
    return str(amount).replace('.', ',')

@app.route('/form.aspx')
def payment_form():
    """
    Главная страница оплаты
    """
    token = request.args.get('token')
    
    if not token:
        return "Token is required", 400
    
    # Декодируем токен
    token_data = JWTDecoder.decode_token(token)
    
    if not token_data:
        return "Invalid token", 400
    
    # Извлекаем все необходимые данные из токена
    # Основные поля
    order_number = token_data.get('ORDER', '')
    amount = format_amount(token_data.get('AMOUNT', 0))
    currency = token_data.get('CURRENCY', 'BYN')
    
    # Информация о мерчанте
    merchant_name = token_data.get('MERCHANT_NAME', 'FAINEX')
    merchant_org_name = token_data.get('MERCHANT_ORG_NAME', 'ООО «Файнекс»')
    merchant_addr = token_data.get('MERCHANT_ADDR', 
        'Республика Беларусь, 223056, Минская область, Минский район, с/с Сеницкий, аг. Сеница, ул. Армейская, д. 8, пом. 4 (офис 2)')
    
    # Описание и ссылки
    description = token_data.get('DESC', f'Заявка на пополнение № {order_number}')
    back_url = token_data.get('BACKREF', 'https://app.fainex.by/home/wallet/my_balance')
    merchant_url = token_data.get('MERCHANT_URL', 'https://app.fainex.by')
    
    # Технические поля
    merchant = token_data.get('MERCHANT', 'E0100004')
    trtype = token_data.get('TRTYPE', 1)
    is_show_cheque = token_data.get('isShowCheque', True)
    
    # Дополнительная информация
    merchant_info = token_data.get('M_INFO', '')
    merchant_add_info = token_data.get('MERCH_ADD_INFO', '')
    
    # Генерируем hash_key
    hash_key = base64.b64encode(
        hashlib.sha256(token.encode()).digest()[:16]
    ).decode()
    
    # Форматируем данные для шаблона
    context = {
        'order_number': order_number,
        'amount': amount,
        'currency': currency,
        'merchant_name': merchant_name,
        'merchant_org_name': merchant_org_name,
        'merchant_addr': merchant_addr,
        'description': description,
        'back_url': back_url,
        'merchant_url': merchant_url,
        'merchant': merchant,
        'trtype': trtype,
        'is_show_cheque': is_show_cheque,
        'hash_key': hash_key,
        'token': token,
        'merchant_info': merchant_info,
        'merchant_add_info': merchant_add_info,
    }
    
    return render_template('payment.html', **context)

@app.route('/process-payment', methods=['POST'])
def process_payment():
    """
    Обработка платежа
    """
    try:
        form_data = request.form.to_dict()
        
        # Логирование полученных данных
        print("Payment data received:", form_data)
        
        # Здесь должна быть реальная обработка платежа
        # и интеграция с платежным шлюзом
        
        return jsonify({
            'status': 'success',
            'message': 'Платеж обработан',
            'redirect_url': form_data.get('BACKREF', '/'),
            'data': form_data
        })
        
    except Exception as e:
        print(f"Payment processing error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/cancel', methods=['POST'])
def cancel_payment():
    """
    Отмена операции
    """
    back_url = request.form.get('BACKREF', '/')
    return redirect(back_url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
