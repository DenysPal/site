# Виправлення проблеми з ціною на Refund сторінці

## Опис проблеми
Після оновлення сторінки на refund, ціна зникала, хоча на payment сторінці все працювало коректно.

## Аналіз проблеми
На payment сторінці була реалізована логіка збереження та відновлення ціни:
1. Збереження ціни в localStorage при завантаженні
2. Відновлення ціни при оновленні сторінки
3. Збереження заголовка перед оновленням

На refund сторінці ця логіка була неповна або відсутня.

## Реалізоване рішення

### 1. Основна логіка збереження ціни
Додано скрипт, який зберігає ціну в localStorage при завантаженні сторінки:

```javascript
// Зберігаємо заголовок для відновлення
localStorage.setItem('last_refund_title', title);
// Зберігаємо також в інших ключах для сумісності
if (price && currency) {
  localStorage.setItem('event_price', price);
  localStorage.setItem('event_currency', currency);
}
```

### 2. Відновлення ціни при завантаженні
Додано функцію `restorePriceFromStorage()`, яка відновлює ціну з localStorage:

```javascript
function restorePriceFromStorage() {
  // Спочатку перевіряємо останній збережений заголовок
  const lastTitle = localStorage.getItem('last_refund_title');
  if (lastTitle && lastTitle !== 'Refund ...') {
    document.getElementById('payment-title').textContent = lastTitle;
    // Оновлюємо також .event-price елементи
    const match = lastTitle.match(/Refund ([\d.,]+) ([A-Za-z]+)/);
    if (match) {
      const price = match[1];
      const currency = match[2];
      document.querySelectorAll('.event-price').forEach(el => el.textContent = price + ' ' + currency);
      return;
    }
  }
  
  // Якщо заголовок не знайдено, відновлюємо з інших джерел
  const savedPrice = localStorage.getItem('event_price') || localStorage.getItem('current_refund_price');
  const savedCurrency = localStorage.getItem('event_currency') || localStorage.getItem('current_refund_currency');
  const savedTotal = localStorage.getItem('refund_total');
  
  if (savedPrice && savedCurrency) {
    document.getElementById('payment-title').textContent = `Refund ${savedPrice} ${savedCurrency}`;
    document.querySelectorAll('.event-price').forEach(el => el.textContent = savedPrice + ' ' + savedCurrency);
  }
}
```

### 3. Збереження стану перед оновленням
Додано обробники подій для збереження стану:

```javascript
// Зберігаємо стан перед оновленням сторінки
window.addEventListener('beforeunload', function() {
  const currentTitle = document.getElementById('payment-title').textContent;
  if (currentTitle && currentTitle !== 'Refund ...') {
    localStorage.setItem('last_refund_title', currentTitle);
  }
});

// Відновлюємо стан після оновлення сторінки
window.addEventListener('load', function() {
  const lastTitle = localStorage.getItem('last_refund_title');
  if (lastTitle && lastTitle !== 'Refund ...') {
    document.getElementById('payment-title').textContent = lastTitle;
    // Оновлюємо також .event-price елементи
    const match = lastTitle.match(/Refund ([\d.,]+) ([A-Za-z]+)/);
    if (match) {
      const price = match[1];
      const currency = match[2];
      document.querySelectorAll('.event-price').forEach(el => el.textContent = price + ' ' + currency);
    }
  }
});
```

### 4. Відновлення при поверненні на вкладку
Додано обробник для відновлення ціни при поверненні на вкладку:

```javascript
// Відновлюємо ціну при поверненні на вкладку
document.addEventListener('visibilitychange', function() {
  if (!document.hidden) {
    // Користувач повернувся на вкладку
    setTimeout(restorePriceFromStorage, 100); // Невелика затримка для надійності
  }
});
```

## Ключі localStorage, які використовуються

- `last_refund_title` - останній збережений заголовок з ціною
- `event_price` - збережена ціна
- `event_currency` - збережена валюта
- `refund_total` - збережений total параметр
- `current_refund_price` - поточна ціна для відновлення
- `current_refund_currency` - поточна валюта для відновлення

## Тестування
Створено тестовий файл `test_refund_price_fix.html` для перевірки функціональності:
1. Тест збереження ціни в localStorage
2. Тест відновлення ціни з localStorage
3. Тест симуляції оновлення сторінки
4. Показ поточного стану localStorage
5. Очищення тестових даних

## Результат
Тепер на refund сторінці ціна зберігається та відновлюється при оновленні сторінки так само, як на payment сторінці. Користувачі більше не будуть бачити порожню ціну після оновлення сторінки.

## Файли, які були змінені
- `events-art.com/refund/index.html` - основна refund сторінка
- `test_refund_price_fix.html` - тестовий файл
- `REFUND_PRICE_PERSISTENCE_FIX.md` - ця документація
