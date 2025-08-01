# API Fixes - Виправлення проблем з відображенням даних подій

## Проблема
Коли створювалася нова силка, старі посилання починали показувати неправильні дані (дата, час, адреса, ціна). Це відбувалося через те, що API-ендпоінти повертали останній запис з бази даних замість даних, специфічних для конкретного `page_code`.

## Виправлення

### 1. Backend (main.py)

#### Функція `latest_event_data` (рядки 1941-1964)
**Було:**
```python
@log_function
async def latest_event_data(request):
    c = conn.cursor()
    c.execute('SELECT date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price FROM site_users ORDER BY created_at DESC LIMIT 1')
    # ...
```

**Стало:**
```python
@log_function
async def latest_event_data(request):
    page_code = request.query.get('page', '') or request.query.get('e', '')
    if not page_code:
        print("[API] No page_code provided")
        return web.json_response({'error': 'missing page or e parameter'}, status=400)
    
    print(f"[API] Requesting data for page_code: {page_code}")
    c = conn.cursor()
    c.execute('SELECT date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price FROM site_users WHERE page_code=?', (page_code,))
    # ...
```

#### Функція `event_places_api` (рядки 2139-2156)
**Додано перевірку `page_code`:**
```python
if not page_code:
    print("[API] No page_code provided for event_places_api")
    return web.json_response({'error': 'missing page parameter'}, status=400)
```

#### Функція `event_date_api` (рядки 2157-2176)
**Додано перевірку `page_code`:**
```python
if not page_code:
    print("[API] No page_code provided for event_date_api")
    return web.json_response({'error': 'missing page parameter'}, status=400)
```

#### Функція `event_time_api` (рядки 2177-2198)
**Додано перевірку `page_code`:**
```python
if not page_code:
    print("[API] No page_code provided for event_time_api")
    return web.json_response({'error': 'missing page parameter'}, status=400)
```

### 2. Frontend (HTML файли)

#### Виправлені файли:
- `events-art.com/collection-co–selection/index.html`
- `events-art.com/anna-konik/index.html`
- `events-art.com/jacek-adamas/index.html`
- `events-art.com/uncensored/index.html`
- `events-art.com/snucie/index.html`

#### Зміна в кожному файлі:
**Було:**
```javascript
fetch('/api/latest_event_data')
```

**Стало:**
```javascript
const params = new URLSearchParams(window.location.search);
let page_code = params.get('page');
if (!page_code) {
    page_code = sessionStorage.getItem('page_code');
}

if (!page_code) {
    console.error('No page_code found, cannot load event data');
    return;
}

fetch('/api/latest_event_data?page=' + encodeURIComponent(page_code))
```

## Результат

Тепер кожна силка:
1. **Завжди передає свій унікальний `page_code`** у всі API-запити
2. **Отримує тільки свої дані** з бази даних
3. **Не залежить від інших силок** - створення нової силки не впливає на старі

## Перевірка

Після цих змін:
- ✅ Кожна силка показує свої унікальні дані
- ✅ Створення нової силки не порушує старі
- ✅ API повертає помилку 400, якщо `page_code` не передано
- ✅ Всі запити до API містять `page_code` параметр 