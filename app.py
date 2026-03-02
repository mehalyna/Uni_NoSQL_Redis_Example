import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.ping()  # True якщо з'єднання ок

def db_read_product(product_id):
    """функція, яка симулює читання з бази даних"""
    # Симуляція затримки бази даних
    import time
    time.sleep(0.1)
    return f"Product {product_id}: Name, Price, Description"

def get_product(product_id):
    """Повертає дані продукту та інкрементує лічильник переглядів"""
    view_key = f"product:{product_id}:views"
    r.incr(view_key)
    
    key = f"product:{product_id}:data"
    cached = r.get(key)
    if cached is not None:
        return cached
    product = db_read_product(product_id)  # фейкова функція, яка читає з бази
    r.set(key, product, ex=60)  # TTL 60 секунд
    return product


def get_product_views(product_id):
    """Повертає кількість переглядів продукту"""
    view_key = f"product:{product_id}:views"
    views = r.get(view_key)
    return int(views) if views else 0  # type: ignore


def get_all_views():
    """Повертає статистику переглядів для всіх продуктів"""
    view_keys = r.keys('product:*:views')  # type: ignore
    stats = {}
    for key in view_keys:  # type: ignore
        product_id = key.split(':')[1]
        stats[product_id] = get_product_views(product_id)
    return stats


def seed_redis():
    """Заповнює Redis початковими даними"""
    products = {
        '1': 'Laptop HP: 15000 грн, 16GB RAM, 512GB SSD',
        '2': 'Mouse Logitech: 800 грн, Wireless, Ergonomic',
        '3': 'Keyboard Mechanical: 2500 грн, RGB, Cherry MX',
        '4': 'Monitor Dell: 8000 грн, 27 inch, 4K',
        '5': 'Headphones Sony: 3500 грн, Noise Cancelling, Bluetooth'
    }
    
    for product_id, product_data in products.items():
        key = f"product:{product_id}:data"
        r.set(key, product_data, ex=300)  # TTL 5 хвилин
    
    print(f"Засіяно {len(products)} продуктів в Redis")


if __name__ == "__main__":
    # Очистити всі ключі (опціонально)
    r.flushdb()
    
    # Засіяти дані
    seed_redis()
    
    # Тест кешування
    print("\n--- Перший запит (з 'бази данних') ---")
    import time
    start = time.time()
    product = get_product('1')
    print(f"Продукт: {product}")
    print(f"Час: {time.time() - start:.3f} сек")
    
    print("\n--- Другий запит (з кешу Redis) ---")
    start = time.time()
    product = get_product('1')
    print(f"Продукт: {product}")
    print(f"Час: {time.time() - start:.3f} сек")
    
    # Додаткові перегляди для тестування лічильника
    print("\n--- Тестування лічильника переглядів ---")
    get_product('2')
    get_product('2')
    get_product('3')
    get_product('3')
    get_product('3')
    
    # Показати статистику переглядів
    print("\n--- Статистика переглядів ---")
    views = get_all_views()
    for product_id, count in sorted(views.items()):
        print(f"Продукт {product_id}: {count} переглядів")
    
    # Показати всі ключі
    print("\n--- Всі ключі в Redis ---")
    keys = r.keys('product:*')  # type: ignore
    print(f"Знайдено {len(keys)} ключів: {keys}")  # type: ignore

