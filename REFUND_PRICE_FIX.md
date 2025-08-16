# 🔧 Виправлення проблеми з ціною на сторінці Refund

## ❌ **Проблема:**
Після оновлення сторінки refund ціна збивається та не відображається правильно.

## 🔍 **Причини проблеми:**
1. **Втрата стану при оновленні**: При оновленні сторінки localStorage зберігається, але заголовок не відновлюється
2. **Одноразове виконання**: Функція виконується тільки при завантаженні сторінки
3. **Відсутність обробки подій**: Немає обробки подій оновлення сторінки та переключення вкладок

## ✅ **Рішення:**

### 1. **Додано функцію відновлення ціни** 🔄
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
  
  // Якщо заголовок не знайдено, відновлюємо з інших джерелів
  const savedPrice = localStorage.getItem('event_price') || localStorage.getItem('current_refund_price');
  const savedCurrency = localStorage.getItem('event_currency') || localStorage.getItem('current_refund_currency');
  const savedTotal = localStorage.getItem('refund_total');
  
  if (savedPrice && savedCurrency) {
    document.getElementById('payment-title').textContent = `Refund ${savedPrice} ${savedCurrency}`;
    document.querySelectorAll('.event-price').forEach(el => el.textContent = savedPrice + ' ' + savedCurrency);
  } else if (savedTotal) {
    const match = savedTotal.match(/(\d+[\.,]?\d*)([A-Za-z]+)/);
    if (match) {
      const price = match[1].replace(',', '.');
      const currency = match[2];
      document.getElementById('payment-title').textContent = `Refund ${price} ${currency}`;
      document.querySelectorAll('.event-price').forEach(el => el.textContent = price + ' ' + currency);
    }
  } else if (savedCurrency) {
    document.getElementById('payment-title').textContent = `Refund ${savedCurrency}`;
    document.querySelectorAll('.event-price').forEach(el => el.textContent = savedCurrency);
  }
}
```

### 2. **Додано збереження стану перед оновленням** 💾
```javascript
window.addEventListener('beforeunload', function() {
  const currentTitle = document.getElementById('payment-title').textContent;
  if (currentTitle && currentTitle !== 'Refund ...') {
    localStorage.setItem('last_refund_title', currentTitle);
  }
});
```

### 3. **Додано відновлення стану після оновлення** 🔄
```javascript
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

### 4. **Додано обробку переключення вкладок** 📱
```javascript
document.addEventListener('visibilitychange', function() {
  if (!document.hidden) {
    // Користувач повернувся на вкладку
    setTimeout(restorePriceFromStorage, 100); // Невелика затримка для надійності
  }
});
```

### 5. **Покращено збереження поточного стану** 💾
```javascript
// Зберігаємо останній заголовок для відновлення
localStorage.setItem('last_refund_title', title);

// Зберігаємо поточний стан для відновлення
if (price && currency) {
  localStorage.setItem('current_refund_price', price);
  localStorage.setItem('current_refund_currency', currency);
}
```

## 🎯 **Результат:**
Тепер сторінка refund:
- ✅ **Зберігає ціну при оновленні** - ціна не збивається
- ✅ **Відновлює стан з localStorage** - автоматично відновлює останню ціну
- ✅ **Обробляє переключення вкладок** - ціна залишається при поверненні
- ✅ **Має резервні джерела даних** - використовує кілька джерел для відновлення
- ✅ **Зберігає всі елементи** - оновлює як заголовок, так і .event-price елементи

## 📁 **Файли, які оновлено:**
- ✅ **events-art.com/refund/index.html** - додано функції відновлення ціни

## 🔧 **Як це працює:**
1. **При завантаженні**: викликається `restorePriceFromStorage()` для відновлення ціни
2. **При зміні ціни**: зберігається в `last_refund_title` та інших ключах
3. **Перед оновленням**: зберігається поточний заголовок
4. **Після оновлення**: автоматично відновлюється остання ціна
5. **При переключенні вкладок**: ціна відновлюється з затримкою

**Тепер ціна на сторінці refund не збивається при оновленні сторінки!** 🎫✨
