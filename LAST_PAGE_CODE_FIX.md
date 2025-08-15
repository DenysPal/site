# Виправлення проблеми з last_page_code

## Проблема
Після 6+ циклів навігації між виставкою та головною сторінкою дані переставали підгружатися. Основна причина полягала в тому, що коли користувач натискав кнопку Home, код очищав кеш для поточного `page_code`, але потім переходив на головну сторінку, де `page_code` відсутній. Це означало, що функції завантаження даних не могли працювати.

## Рішення
Впроваджено систему `last_page_code`, яка зберігає останній `page_code` у `sessionStorage` перед переходом на головну сторінку.

### 1. Збереження last_page_code
```javascript
// У функції stableNavigation
if (pageCode) {
    // ... очищення кешу ...
    
    // Зберігаємо page_code для використання на головній сторінці
    sessionStorage.setItem('last_page_code', pageCode);
    
    // ... видалення флагу очищення ...
}
```

### 2. Використання last_page_code на головній сторінці
Всі функції завантаження даних тепер перевіряють `last_page_code`, якщо `page_code` відсутній в URL:

```javascript
// У fetchAndDisplayPrice, updateMainPageEvents, refreshData
let pageCode = new URLSearchParams(window.location.search).get('page');

// Якщо немає page_code в URL, але ми на головній сторінці, використовуємо last_page_code
if (!pageCode && window.location.pathname === '/') {
    pageCode = sessionStorage.getItem('last_page_code');
    if (pageCode) {
        console.log('Using last_page_code:', pageCode);
    }
}
```

### 3. Автоматичне очищення last_page_code
Після успішного завантаження даних `last_page_code` автоматично очищається:

```javascript
// У stablePageLoad
Promise.all([
    fetchAndDisplayPrice(),
    updateMainPageEvents()
]).then(() => {
    console.log('Page data loaded successfully');
    clearLastPageCode(); // Очищаємо last_page_code після успішного завантаження
}).catch((error) => {
    // ... обробка помилок ...
});
```

### 4. Функція clearLastPageCode
```javascript
function clearLastPageCode() {
    const lastPageCode = sessionStorage.getItem('last_page_code');
    if (lastPageCode) {
        console.log('Clearing last_page_code after successful data load:', lastPageCode);
        sessionStorage.removeItem('last_page_code');
    }
}
```

## Оновлені файли

### events-art.com/js/stability-fixes.js
- Додано збереження `last_page_code` у `stableNavigation`
- Оновлено `stablePageLoad` для використання `last_page_code`
- Додано функцію `clearLastPageCode`
- Оновлено `refreshData` та `forceRefresh` для роботи з `last_page_code`

### events-art.com/js/event-loader.js
- Оновлено `fetchAndDisplayPrice` для використання `last_page_code`
- Оновлено `updateMainPageEvents` для використання `last_page_code`

## Як це працює

1. **Користувач заходить на виставку** з `page_code` (наприклад, `?page=1-1`)
2. **Користувач натискає кнопку Home**
3. **Код очищає кеш** для поточного `page_code`
4. **Код зберігає `page_code`** як `last_page_code` у `sessionStorage`
5. **Користувач переходить на головну сторінку** (без `page_code` в URL)
6. **Функції завантаження даних** використовують `last_page_code` для отримання даних
7. **Дані успішно завантажуються** на головній сторінці
8. **`last_page_code` автоматично очищається** після успішного завантаження

## Переваги

- **Стабільність**: Дані завжди доступні на головній сторінці
- **Автоматичне очищення**: `last_page_code` не накопичується
- **Зворотна сумісність**: Логіка працює як з `page_code` в URL, так і без нього
- **Відладка**: Додано логування для відстеження використання `last_page_code`

## Тестування

Створено оновлений тестовий скрипт `test_navigation_stability_v2.py`, який:
- Тестує логіку роботи з `last_page_code`
- Імітує сценарій навігації між виставкою та головною
- Перевіряє стабільність даних після багаторазових циклів

## Очікуваний результат

Тепер після 6+ циклів навігації дані повинні залишатися стабільними та доступними на головній сторінці, оскільки функції завантаження даних можуть використовувати `last_page_code` для отримання необхідних даних. 