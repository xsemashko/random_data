def fix_encoding(value):
    """
    Исправляет кодировку строки, если она содержит UTF-8 байты как текст
    """
    if not isinstance(value, str):
        return value
    
    # Проверяем, есть ли в строке байты > 127 (не-ASCII)
    try:
        # Если строка выглядит как UTF-8 байты, сохраненные в Latin-1
        if any(ord(c) > 127 for c in value):
            # Преобразуем: Latin-1 -> bytes -> UTF-8
            return value.encode('latin-1').decode('utf-8')
    except:
        pass
    
    return value
