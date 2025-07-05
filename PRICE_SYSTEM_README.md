# Система Динамічних Цін для Events Art

## Огляд

Система дозволяє динамічно змінювати ціни квитків через Telegram бота та автоматично оновлювати їх на сайті та в системі оплати.

## Як це працює

### 1. Створення події з ціною

Коли ви створюєте подію через бота, вказуєте ціну в останньому рядку шаблону:

```
28.06.2025 10:00-22:00
29.06.2025 10:00-22:00
30.06.2025 10:00-22:00
01.07.2025 10:00-22:00
02.07.2025 10:00-22:00
03.07.2025 10:00-22:00
04.07.2025 10:00-22:00
05.07.2025 10:00-22:00
EUR
plac Stanisława Małachowskiego 3, 00-916 Warszawa
50  ← Це ціна
```

### 2. Генерація посилань з ціною

Бот автоматично генерує посилання з параметрами ціни:

```
http://artpullse.com/?e=abc123&price=50&currency=EUR
http://artpullse.com/terroir-and-traditions/?e=abc123&p=1&price=50&currency=EUR
```

### 3. Збереження в events.json

Ціна зберігається в файлі `events-art.com/events.json`:

```json
{
  "event_id": {
    "title": "Выставка",
    "price": "50",
    "currency": "EUR",
    "address": "plac Stanisława Małachowskiego 3, 00-916 Warszawa",
    "events": [...]
  }
}
```

### 4. Автоматичне оновлення на сайті

JavaScript код автоматично:
- Отримує ціну з URL параметрів
- Зберігає її в sessionStorage
- Оновлює всі елементи з ціною на сторінці
- Передає ціну в систему оплати

## Функції адміністратора

### Зміна ціни існуючої події

1. Відкрийте адмін панель в боті
2. Натисніть "💰 Изменить цену события"
3. Введіть код події (6 символів)
4. Введіть нову ціну

### Команди в боті

- `/start` - початок роботи
- `📎Ссылки` - створення нової події з ціною
- `🛠️ Админ панель` → `💰 Изменить цену события` - зміна ціни

## Технічна реалізація

### Файли які були змінені:

1. **main.py** - додано функції для роботи з цінами
2. **events-art.com/js/event-loader.js** - обробка цін з URL
3. **events-art.com/buy-tickets/index.html** - динамічна ціна в оплаті
4. **events-art.com/events.json** - зберігання цін

### JavaScript функції:

```javascript
// Отримання ціни з URL або sessionStorage
function getTicketPrice() {
    const urlParams = new URLSearchParams(window.location.search);
    const priceFromUrl = urlParams.get('price');
    if (priceFromUrl) return parseFloat(priceFromUrl);
    
    const priceFromStorage = sessionStorage.getItem('ticket_price');
    if (priceFromStorage) return parseFloat(priceFromStorage);
    
    return 45; // за замовчуванням
}

// Оновлення ціни на сторінці
function updateTicketPrice() {
    const price = getTicketPrice();
    const currency = getTicketCurrency();
    
    // Оновлюємо елементи з ціною
    const priceElements = document.querySelectorAll('.ticket-price, .price, [data-price]');
    priceElements.forEach(element => {
        element.textContent = `${price} ${currency}`;
    });
    
    // Оновлюємо посилання
    const buyTicketLinks = document.querySelectorAll('a[href*="/buy-tickets/"]');
    buyTicketLinks.forEach(link => {
        const url = new URL(link.href);
        url.searchParams.set('price', price);
        url.searchParams.set('currency', currency);
        link.href = url.toString();
    });
}
```

## Тестування

Використовуйте файл `test_price_system.html` для тестування:

1. Відкрийте файл в браузері
2. Перевірте як працюють посилання з різними цінами
3. Тестуйте sessionStorage функції

## Приклади використання

### Створення події з ціною 70 USD:

```
28.06.2025 10:00-22:00
29.06.2025 10:00-22:00
30.06.2025 10:00-22:00
01.07.2025 10:00-22:00
02.07.2025 10:00-22:00
03.07.2025 10:00-22:00
04.07.2025 10:00-22:00
05.07.2025 10:00-22:00
USD
plac Stanisława Małachowskiego 3, 00-916 Warszawa
70
```

### Зміна ціни існуючої події:

1. Код події: `abc123`
2. Нова ціна: `80`
3. Результат: ціна змінюється на 80 EUR

## Важливі моменти

1. **Ціна передається через URL параметри** - `?price=50&currency=EUR`
2. **Зберігається в sessionStorage** для збереження між сторінками
3. **Автоматично оновлюється** в системі оплати
4. **Підтримує різні валюти** - EUR, USD, PLN, AUD тощо
5. **Зворотна сумісність** - якщо ціна не вказана, використовується 45 EUR

## Безпека

- Ціни зберігаються в JSON файлі
- Валідація введених даних
- Логування змін цін адміністратором
- Захист від XSS через валідацію URL параметрів 