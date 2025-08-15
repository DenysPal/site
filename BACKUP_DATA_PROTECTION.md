# Система захисту даних з backup механізмами

## Проблема
Після 5+ циклів навігації між виставкою та головною сторінкою дані знову пропадали, незважаючи на попередні виправлення з `last_page_code`.

## Аналіз причини
Основна проблема полягала в тому, що дані очищалися занадто агресивно, а механізми відновлення не були достатньо надійними для багаторазових циклів навігації.

## Нові механізми захисту

### 1. Система backup даних
Перед очищенням кешу при натисканні кнопки Home, всі поточні дані зберігаються як backup:

```javascript
// Зберігаємо поточні дані як backup перед очищенням
const currentData = sessionStorage.getItem(`events_data_${pageCode}`);
const currentPrice = sessionStorage.getItem(`price_${pageCode}`);
const currentCurrency = sessionStorage.getItem(`currency_${pageCode}`);

if (currentData) {
    sessionStorage.setItem(`backup_events_data_${pageCode}`, currentData);
}
if (currentPrice) {
    sessionStorage.setItem(`backup_price_${pageCode}`, currentPrice);
}
if (currentCurrency) {
    sessionStorage.setItem(`backup_currency_${pageCode}`, currentCurrency);
}
```

### 2. Покращена функція відновлення даних
Функція `recoverData` тепер спочатку намагається відновити дані з backup, а потім використовує fallback:

```javascript
function recoverData(pageCode) {
    // Спочатку спробуємо відновити з backup даних
    const backupData = sessionStorage.getItem(`backup_events_data_${pageCode}`);
    const backupPrice = sessionStorage.getItem(`backup_price_${pageCode}`);
    const backupCurrency = sessionStorage.getItem(`backup_currency_${pageCode}`);
    
    if (backupData && backupPrice && backupCurrency) {
        // Відновлюємо основні дані з backup
        // ... логіка відновлення ...
        return parsedData;
    }
    
    // Якщо backup недоступний, використовуємо fallback дані
    // ... fallback логіка ...
}
```

### 3. Автоматичне відновлення даних на головній сторінці
Нова функція `autoRecoverHomePageData` автоматично перевіряє та відновлює дані на головній сторінці:

```javascript
function autoRecoverHomePageData() {
    const lastPageCode = sessionStorage.getItem('last_page_code');
    if (!lastPageCode) return;
    
    // Перевіряємо чи є дані для цього page_code
    const hasEventsData = sessionStorage.getItem(`events_data_${lastPageCode}`);
    const hasPriceData = sessionStorage.getItem(`price_${lastPageCode}`);
    const hasCurrencyData = sessionStorage.getItem(`currency_${lastPageCode}`);
    
    if (!hasEventsData || !hasPriceData || !hasCurrencyData) {
        // Спробуємо відновити дані
        const recoveredData = recoverData(lastPageCode);
        // ... оновлення UI ...
    }
}
```

### 4. Періодична перевірка та відновлення
Додано автоматичну перевірку кожні 30 секунд на головній сторінці:

```javascript
// Перевіряємо та відновлюємо дані на головній сторінці кожні 30 секунд
setInterval(() => {
    if (window.location.pathname === '/') {
        autoRecoverHomePageData();
    }
}, 30 * 1000);
```

### 5. Покращена логіка блокування запитів
Зменшено мінімальний інтервал між запитами з 1000мс до 500мс для більш швидкого відновлення:

```javascript
function canFetchData(pageCode) {
    // Зменшуємо мінімальний інтервал між запитами до 500мс
    if (lastFetch && (now - parseInt(lastFetch)) < 500) {
        return false;
    }
    return true;
}
```

## Оновлені файли

### events-art.com/js/stability-fixes.js
- Додано систему backup даних
- Покращено функцію `recoverData`
- Додано `autoRecoverHomePageData`
- Додано періодичну перевірку даних
- Покращено `canFetchData`

## Як це працює

1. **Користувач заходить на виставку** з `page_code`
2. **Користувач натискає кнопку Home**
3. **Код зберігає поточні дані як backup** перед очищенням
4. **Код очищає основний кеш** та зберігає `last_page_code`
5. **Користувач переходить на головну сторінку**
6. **Функції завантаження використовують `last_page_code`**
7. **Якщо дані відсутні, автоматично відновлюються з backup**
8. **Періодично перевіряється наявність даних** та відновлюються при необхідності

## Переваги

- **Подвійний захист**: Основні дані + backup дані
- **Автоматичне відновлення**: Дані відновлюються без втручання користувача
- **Періодична перевірка**: Постійний моніторинг стану даних
- **Швидше відновлення**: Зменшений інтервал між запитами
- **Надійність**: Кілька рівнів захисту даних

## Тестування

Створено оновлений тестовий скрипт `test_navigation_stability_v3.py`, який:
- Тестує логіку backup даних
- Перевіряє автоматичне відновлення
- Імітує багаторазові цикли навігації
- Аналізує стабільність даних

## Очікуваний результат

Тепер після 5+ циклів навігації дані повинні залишатися стабільними завдяки:
- Backup системі даних
- Автоматичному відновленню
- Періодичній перевірці
- Покращеній логіці блокування запитів 