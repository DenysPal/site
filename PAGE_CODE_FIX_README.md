# Виправлення системи page_code

## Проблема
Кожне посилання з унікальним `page_code` повинно відкривати свої власні дані, але після генерації нової сторінки стара відкривала нові дані замість своїх.

## Виправлення

### 1. Оновлено `index.html`
- **Замінено параметр `event` на `page_code`** в JavaScript коді
- **Додано очищення sessionStorage** при зміні `page_code`
- **Додано логування** для відстеження завантаження даних
- **Оновлено логіку посилань** для використання `page_code` замість `event`

### 2. Оновлено `events-art.com/js/event-loader.js`
- **Оновлено функцію `updateMainPageEvents`** для використання `page_code`
- **Оновлено функцію `loadEvent`** для використання `page_code`
- **Оновлено функцію `refreshEventDataIfNeeded`** з примусовим перезавантаженням сторінки
- **Додано логування** для відстеження змін
- **Позначено `getEventIdFromUrl` як застарілу**

### 3. Ключові зміни

#### Очищення кешу при зміні page_code:
```javascript
if (currentPageCode !== pageCode) {
    sessionStorage.clear();
    sessionStorage.setItem('page_code', pageCode);
    window.location.reload(); // Примусове перезавантаження
}
```

#### Використання page_code замість event:
```javascript
function getPageCodeFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('page') || params.get('e');
}
```

#### Пошук правильного event_id через API:
```javascript
const eventLinksRes = await fetch(`/api/event_links?page=${encodeURIComponent(pageCode)}`);
```

## Тестування

### 1. Використовуйте тестовий файл `test_page_code_system.html`
- Відкрийте файл у браузері
- Перевірте роботу з різними `page_code`
- Подивіться на логування в консолі

### 2. Тестування основного сайту
1. Відкрийте сайт з різними `page_code`:
   - `?page=1-1`
   - `?page=1-2`
   - `?page=2-1`
   - `?e=old-format` (старий формат)

2. Перевірте:
   - Чи кожне посилання показує свої дані
   - Чи очищається кеш при зміні `page_code`
   - Чи правильно оновлюються посилання

### 3. Перевірка в консолі браузера
Відкрийте Developer Tools (F12) і подивіться на логи:
- `Loading event data for page_code: X`
- `Page code changed from X to Y, clearing session storage`
- `Updated events for page_code: X, event_id: Y`

## Структура даних

### API endpoints:
- `/api/event_links?page=X` - отримання site_user_id за page_code
- `/events.json` - дані подій

### Session Storage:
- `page_code` - поточний page_code
- Всі інші дані очищаються при зміні page_code

### URL формати:
- Новий: `?page=1-1`
- Старий: `?e=old-format` (підтримується для зворотної сумісності)

## Відомі обмеження
- При зміні `page_code` сторінка перезавантажується для уникнення кешування
- Старий формат `?e=` підтримується для зворотної сумісності
- Логування додано для відстеження, можна видалити в продакшені 