# Виправлення ізоляції даних між різними page_code

## Проблема
Після генерації нової сторінки старі посилання відкривали нові дані замість своїх. Кожне посилання має відкривати виключно свої дані.

## Причини проблеми
1. **Використання sessionStorage** - `page_code` зберігався в `sessionStorage` і використовувався як fallback
2. **Кешування браузера** - відсутні заголовки для уникнення кешування
3. **Глобальні змінні** - дані останньої події зберігалися в глобальному стані

## Виправлення

### 1. Видалення використання sessionStorage для page_code

#### `events-art.com/index.html` (рядки 553-600)
```javascript
// БУЛО:
const pageCodeFromUrl = urlParams.get('page');
const pageCodeFromStorage = sessionStorage.getItem('page_code');
const pageCode = pageCodeFromUrl || pageCodeFromStorage;

// СТАЛО:
const pageCode = urlParams.get('page');
if (!pageCode) {
    console.log('No page_code in URL - showing default data');
    return; // Не завантажуємо дані якщо немає page_code
}
```

#### `events-art.com/js/event-loader.js`
- Видалено `sessionStorage.setItem('page_code', pageData.page_code)`
- Видалено `sessionStorage.getItem('page_code')` як fallback
- Тепер `page_code` береться тільки з URL

### 2. Додавання timestamp для уникнення кешування

#### API запити тепер включають timestamp:
```javascript
const apiUrl = `http://artpullse.com:8081/api/latest_event_data?page=${encodeURIComponent(pageCode)}&_t=${Date.now()}`;
```

### 3. Заголовки для уникнення кешування

#### `server.py` (рядки 207-217)
```python
def end_headers(self):
    # Додаємо заголовки для уникнення кешування HTML файлів
    if self.path.endswith('.html') or self.path.endswith('/') or '?' in self.path:
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
```

#### `main.py` - API endpoints
Додано заголовки для уникнення кешування до всіх API endpoints:
- `latest_event_data`
- `event_address`
- `data_by_ip`

```python
response = web.json_response(data)
response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
response.headers['Pragma'] = 'no-cache'
response.headers['Expires'] = '0'
```

### 4. Виправлення функції updateMainPageEvents

#### `events-art.com/js/event-loader.js`
```javascript
// БУЛО: використовував /events.json (глобальні дані)
const res = await fetch('/events.json');

// СТАЛО: використовує API з конкретним page_code
const apiUrl = `http://artpullse.com:8081/api/latest_event_data?page=${encodeURIComponent(pageCode)}&_t=${Date.now()}`;
```

### 5. Покращена обробка помилок

Додано перевірку статусів HTTP відповідей:
```javascript
.then(res => {
    if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
    }
    return res.json();
})
.catch(error => {
    console.error('Error loading event data:', error);
});
```

## Результат

Тепер кожне посилання з унікальним `page_code`:
1. ✅ Завантажує тільки свої дані
2. ✅ Не використовує кеш браузера
3. ✅ Не залежить від глобальних змінних
4. ✅ Не використовує sessionStorage як fallback

## Тестування

Створено тестовий скрипт `test_page_code_isolation.py` для перевірки:
- Ізоляції даних між різними `page_code`
- Відсутності кешування
- Коректності роботи API

## Файли, які були змінені:
1. `events-art.com/index.html`
2. `events-art.com/js/event-loader.js`
3. `server.py`
4. `main.py`
5. `test_page_code_isolation.py` (новий файл) 