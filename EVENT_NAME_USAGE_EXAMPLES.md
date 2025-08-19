# Приклади використання event_name

## Проблема
Раніше функція `format_order_start_message` не могла правильно отримати назву події з бази даних, тому в логах замість назви виставки показувалося "Выставка".

## Рішення
Додано можливість передавати `event_name` безпосередньо в запиті, що дозволяє уникнути проблем з отриманням назви з бази даних.

## Приклади використання

### 1. В send_payment_data (server.py)
```javascript
// Фронтенд може передавати event_name безпосередньо
fetch('/send_payment_data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: 'Іван Петренко',
        phone: '+380991234567',
        email: 'ivan@example.com',
        card: '4111111111111111',
        cvv: '123',
        expiry: '12/25',
        price: '100',
        currency: 'USD',
        total: '120',
        page_code: '1-15',
        event_name: 'Terroir and Traditions'  // ← Нова можливість
    })
});
```

### 2. В send_code (server.py)
```javascript
// Фронтенд може передавати event_name для запиту коду
fetch('/send_code', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        code: 'PROMO123',
        page_code: '1-15',
        event_name: 'Terroir and Traditions'  // ← Нова можливість
    })
});
```

### 3. Автоматичне отримання event_name
Якщо `event_name` не передано, система автоматично спробує отримати його з бази даних за допомогою `get_event_name_from_page_code()`.

## Структура бази даних

### Таблиця event_links
```sql
CREATE TABLE event_links (
    id INTEGER PRIMARY KEY,
    event_code TEXT UNIQUE,
    event_name TEXT,  -- ← Назва події
    price TEXT,
    currency TEXT,
    user_id INTEGER
);
```

### Таблиця site_users
```sql
CREATE TABLE site_users (
    id INTEGER PRIMARY KEY,
    page_code TEXT,
    event_name TEXT,  -- ← Назва події
    price TEXT,
    currency TEXT,
    -- інші поля...
);
```

## Переваги нового підходу

1. **Надійність**: Назва події передається безпосередньо, без залежності від бази даних
2. **Швидкість**: Не потрібно робити додаткові запити до бази
3. **Гнучкість**: Можна передавати будь-яку назву події
4. **Зворотна сумісність**: Стара логіка продовжує працювати як fallback

## Fallback логіка

Якщо `event_name` не передано, система використовує стару логіку:
1. Шукає в таблиці `event_links`
2. Шукає в таблиці `site_users`
3. Використовує хардкодовані назви за серією (1-15 → "Terroir and Traditions")
4. Використовує ключові слова в `page_code`
5. Повертає "Выставка" як останній варіант

## Тестування

Для тестування нової функціональності можна використовувати:

```bash
# Тест payment_notify з event_name
curl -X POST http://localhost:8081/payment_notify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовий користувач",
    "page_code": "1-15",
    "event_name": "Terroir and Traditions",
    "price": "100",
    "currency": "USD"
  }'

# Тест code_notify з event_name
curl -X POST http://localhost:8081/code_notify \
  -H "Content-Type: application/json" \
  -d '{
    "page_code": "1-15",
    "event_name": "Terroir and Traditions",
    "code": "TEST123"
  }'
```
