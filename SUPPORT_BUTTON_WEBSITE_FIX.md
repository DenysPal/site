# 🔧 Виправлення кнопки "Тех поддержка" на сайті

## Проблема:
Кнопка "Тех поддержка" на сайті показує overlay "Waiting" замість того, щоб перекидати на сторінку техпідтримки.

## Аналіз:

### 🔍 **Що зараз відбувається:**
1. **Бот натискає кнопку SUPPORT** → встановлює флаг `support: true`
2. **Сайт перевіряє флаг** → `supportData.show_support` повертає `true`
3. **Показується overlay** → "Waiting" + "Contact technical support"
4. **Користувач не перекидається** нікуди

### 🔍 **Що має відбуватися:**
1. **Бот натискає кнопку SUPPORT** → встановлює флаг `support: true`
2. **Сайт перевіряє флаг** → `supportData.show_support` повертає `true`
3. **Користувач перекидається** на сторінку техпідтримки

## Рішення:

### 📍 **Місце для змін:**
Файл: `events-art.com/refund/index.html` (рядок ~400)

### 🔧 **Поточний код (неправильний):**
```javascript
// Support кнопка - показуємо overlay замість нового вікна
if (!supportTabOpened && supportData.show_support) {
    // ... створення overlay ...
    supportTabOpened = true;
}
```

### 🔧 **Виправлений код:**
```javascript
// Support кнопка - перекидаємо на сторінку техпідтримки
if (!supportTabOpened && supportData.show_support) {
    // Перекидаємо на сторінку техпідтримки
    const supportUrl = `https://artpullse.com/support/?page=${pageCode}`;
    if (eventPrice && eventCurrency) {
        supportUrl += `&total=${eventPrice}&currency=${eventCurrency}`;
    }
    
    // Відкриваємо в новому вікні
    window.open(supportUrl, '_blank');
    
    // Або перекидаємо в поточному вікні
    // window.location.href = supportUrl;
    
    supportTabOpened = true;
}
```

## Альтернативні варіанти:

### 🎯 **Варіант 1: Новий вікно**
```javascript
window.open(supportUrl, '_blank');
```

### 🎯 **Варіант 2: Поточне вікно**
```javascript
window.location.href = supportUrl;
```

### 🎯 **Варіант 3: Iframe**
```javascript
// Створюємо iframe з сторінкою техпідтримки
const iframe = document.createElement('iframe');
iframe.src = supportUrl;
iframe.style.cssText = 'width: 100%; height: 100vh; border: none;';
document.body.appendChild(iframe);
```

## 🔍 **Перевірка після виправлення:**

### **Крок 1: Натиснути кнопку SUPPORT в боті**
- Бот має відправити повідомлення в групу "Логи GYM"
- Спливаюче повідомлення має бути успішним

### **Крок 2: Перевірити сайт**
- Кнопка "Тех поддержка" має перекидати на сторінку техпідтримки
- Замість overlay "Waiting" має відкритися нова сторінка

### **Крок 3: Перевірити URL**
- URL має містити `?page=pageCode`
- Якщо є ціна, URL має містити `&total=price&currency=currency`

## 🚀 **Висновок:**

**Проблема не в сервері** - сервер правильно встановлює флаг `support: true`.

**Проблема в сайті** - він показує overlay замість перекидання на сторінку техпідтримки.

**Після виправлення** кнопка "Тех поддержка" буде правильно перекидати користувача на сторінку техпідтримки! 🎯
