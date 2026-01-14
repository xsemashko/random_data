#!/usr/bin/env python3
"""
Минимальный Flask сервер для платежного шлюза
Только декодирование JWT и подстановка в шаблон
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for
import jwt
from flask_talisman import Talisman

app = Flask(__name__)

# Базовые настройки безопасности
Talisman(app, content_security_policy=None)  # Отключаем CSP для внешних ресурсов

# Конфигурация (вынести в config.py для production)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-me'),
    EGW_URL=os.environ.get('EGW_URL', 'https://egw.smartpro.best'),
    SITE_NAME='Платежный шлюз',
    DEBUG=os.environ.get('DEBUG', 'False').lower() == 'true'
)

def decode_jwt_token(token):
    """
    Декодирует JWT токен без проверки подписи (как в примере)
    """
    try:
        # Разделяем токен на части
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Декодируем payload (вторая часть)
        payload_b64 = parts[1]
        
        # Добавляем padding если нужно
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        
        # Декодируем и парсим JSON
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        return payload
        
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def format_amount(amount):
    """Форматирование суммы (10.0 -> '10,00')"""
    try:
        if isinstance(amount, (int, float)):
            return f"{amount:.2f}".replace('.', ',')
        elif isinstance(amount, str):
            # Пробуем преобразовать строку
            return f"{float(amount.replace(',', '.')):.2f}".replace('.', ',')
        return str(amount)
    except:
        return str(amount)

def is_valid_url(url):
    """Проверка валидности URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.route('/form.aspx')
def payment_page():
    """
    Главная страница оплаты
    Получает JWT токен из query string, декодирует и показывает форму
    """
    token = request.args.get('token')
    
    if not token:
        return "Токен не указан", 400
    
    # Декодируем JWT
    token_data = decode_jwt_token(token)
    
    if not token_data:
        return "Неверный токен", 400
    
    # Извлекаем обязательные поля
    order_number = token_data.get('ORDER', '')
    amount = format_amount(token_data.get('AMOUNT', 0))
    currency = token_data.get('CURRENCY', 'BYN')
    merchant = token_data.get('MERCHANT', '')
    back_url = token_data.get('BACKREF', '')
    trtype = token_data.get('TRTYPE', 1)
    
    # Проверяем валидность back_url
    if not is_valid_url(back_url):
        back_url = '/'  # Дефолтный URL если невалидный
    
    # Генерируем HASH_KEY (можно сделать более сложную логику)
    # В примере используется xcydWtdG1dFoRPyUkw2pXQ==
    # Для простоты оставим как в примере, но в production генерируйте свой
    hash_key = 'xcydWtdG1dFoRPyUkw2pXQ=='
    
    # Опциональные поля для отображения
    merchant_name = token_data.get('MERCHANT_NAME', '')
    merchant_org_name = token_data.get('MERCHANT_ORG_NAME', '')
    merchant_addr = token_data.get('MERCHANT_ADDR', '')
    description = token_data.get('DESC', f'Заказ № {order_number}')
    is_show_cheque = token_data.get('isShowCheque', True)
    
    # Подготавливаем контекст для шаблона
    context = {
        # Обязательные технические поля
        'order_number': order_number,
        'amount': amount,
        'currency': currency,
        'merchant': merchant,
        'back_url': back_url,
        'trtype': trtype,
        'hash_key': hash_key,
        'is_show_cheque': is_show_cheque,
        
        # Поля для отображения
        'merchant_name': merchant_name,
        'merchant_org_name': merchant_org_name,
        'merchant_addr': merchant_addr,
        'description': description,
        
        # URL платежного шлюза из конфига
        'egw_url': app.config['EGW_URL'],
        
        # Текущая дата для футера
        'current_year': datetime.now().year,
        
        # Флаг для отладки
        'debug': app.config['DEBUG']
    }
    
    return render_template('payment.html', **context)

@app.route('/cancel', methods=['POST'])
def cancel_payment():
    """
    Отмена операции - редирект на back_url
    """
    back_url = request.form.get('BACKREF', '/')
    return redirect(back_url)

@app.route('/health')
def health_check():
    """Проверка работоспособности"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'payment-gateway'
    })

@app.errorhandler(404)
def page_not_found(e):
    return "Страница не найдена", 404

@app.errorhandler(500)
def internal_error(e):
    return "Внутренняя ошибка сервера", 500

if __name__ == '__main__':
    # В production используйте gunicorn!
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
