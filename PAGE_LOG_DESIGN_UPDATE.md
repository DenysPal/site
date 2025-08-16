# 🔔 Оновлення дизайну логів сторінок

## 🎯 Проблема

**Опис:** Логи "Мамонт открыл страницу" були простими та неінформативними, показували тільки технічну інформацію без зрозумілої назви сторінки.

**Результат:** 
- ❌ Простий текст без емодзі
- ❌ Не зрозуміло, яку саме сторінку відкрив користувач
- ❌ Відсутність назви події
- ❌ Не структуровані дані

## 🔧 Виправлення

### 1. **Створено функцію `get_page_name(path)` - для визначення назви сторінки**

```python
def get_page_name(path):
    """Визначає назву сторінки за шляхом"""
    if path == '/' or path == '/index.html':
        return "Главная страница"
    elif '/buy-tickets/' in path:
        if '/code/' in path:
            return "Оформление заказа (код)"
        elif '/quantity/' in path:
            return "Оформление заказа (количество)"
        elif '/payment/' in path:
            return "Оформление заказа (оплата)"
        else:
            return "Оформление заказа"
    elif '/events/' in path:
        if '/overview/' in path:
            return "Обзор события"
        elif '/details/' in path:
            return "Детали события"
        else:
            return "События"
    elif '/about/' in path:
        return "О нас"
    elif '/contact/' in path:
        return "Контакты"
    elif '/gallery/' in path:
        return "Галерея"
    else:
        # Спробуємо витягнути назву з шляху
        clean_path = path.strip('/').replace('-', ' ').replace('_', ' ').title()
        if clean_path:
            return clean_path
        return "Неизвестная страница"
```

### 2. **Створено функцію `get_event_name_from_page_code(page_code)` - для визначення назви події**

```python
def get_event_name_from_page_code(page_code):
    """Визначає назву події за page_code"""
    if not page_code:
        return "Выставка"
    
    try:
        # Шукаємо page_code в URL
        import re
        match = re.search(r'page=(\d+-\d+)', page_code)
        if match:
            series = int(match.group(1).split('-')[0])
            event_names = [
                "Terroir and Traditions",
                "Collection Co–selection", 
                "Snucie",
                "Art that saves lives",
                "Gotong Royong",
                "Anna Konik",
                "Uncensored",
                "Jacek Adamas"
            ]
            if 1 <= series <= len(event_names):
                return event_names[series - 1]
    except:
        pass
    
    return "Выставка"
```

### 3. **Оновлено функцію `send_telegram_log` - для красивого логування**

```python
@log_function
def send_telegram_log(page, link, ip, country="", extra_user_id=None, important=False):
    # ... existing code ...
    
    # Визначаємо назву сторінки
    page_name = get_page_name(page)
    
    # Визначаємо назву події з page_code
    event_name = get_event_name_from_page_code(link)
    
    msg = (
        f"🔔 Мамонт открыл страницу ({event_name})\n\n"
        f"📎 Страница: {page_name}\n"
        f"#️⃣ Ссылка: {link}\n"
        f"📶 IP: {ip}\n"
        f"🌎 Страна: {country_full}"
    )
```

### 4. **Виправлено функцію `send_telegram_log_async` - для коректної передачі параметрів**

```python
def send_telegram_log_async(page, link, ip, country="", extra_user_id=None, important=False):
    try:
        threading.Thread(
            target=send_telegram_log,
            args=(page, link, ip, country, extra_user_id, important),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[async_log] Failed to start log thread: {e}")
        # Якщо асинхронне логування не вдалося, спробуємо синхронно
        try:
            send_telegram_log(page, link, ip, country, extra_user_id, important)
        except Exception as e2:
            print(f"[async_log] Failed to send log synchronously: {e2}")
```

## ✅ Результат

### **Раніше:**
```
⚠️ Мамонт открыл страницу
📄 Страница: /buy-tickets/code/
🔗 Ссылка: /buy-tickets/code/?page=1-83
🌍 IP: 37.52.215.105
🌏 Страна: Ukraine
```

### **Тепер:**
```
🔔 Мамонт открыл страницу (Terroir and Traditions)

📎 Страница: Оформление заказа (код)
#️⃣ Ссылка: /buy-tickets/code/?page=1-83
📶 IP: 37.52.215.105
🌎 Страна: Ukraine
```

## 🎨 Структура нового логу

### **Заголовок:**
- 🔔 **"Мамонт открыл страницу (Назва події)"** - показує, яку подію переглядає користувач

### **Деталі:**
- 📎 **Страница** - зрозуміла назва сторінки (не технічний шлях)
- #️⃣ **Ссылка** - повне посилання з параметрами
- 📶 **IP** - IP адреса користувача
- 🌎 **Страна** - країна користувача

## 🔍 Логіка визначення назви сторінки

### **Головні сторінки:**
- `/` → "Главная страница"
- `/index.html` → "Главная страница"

### **Оформлення замовлення:**
- `/buy-tickets/code/` → "Оформление заказа (код)"
- `/buy-tickets/quantity/` → "Оформление заказа (количество)"
- `/buy-tickets/payment/` → "Оформление заказа (оплата)"
- `/buy-tickets/` → "Оформление заказа"

### **Події:**
- `/events/overview/` → "Обзор события"
- `/events/details/` → "Детали события"
- `/events/` → "События"

### **Інші сторінки:**
- `/about/` → "О нас"
- `/contact/` → "Контакты"
- `/gallery/` → "Галерея"

### **Автоматичне визначення:**
- `/terroir-and-traditions/` → "Terroir And Traditions"
- `/collection-co-selection/` → "Collection Co Selection"

## 🎯 Логіка визначення назви події

Назва події автоматично визначається за першою цифрою `page_code`:

```python
# page_code = "1-83" → series = 1 → "Terroir and Traditions"
# page_code = "2-45" → series = 2 → "Collection Co–selection"
# page_code = "3-12" → series = 3 → "Snucie"
# і т.д.

event_names = [
    "Terroir and Traditions",      # series 1
    "Collection Co–selection",     # series 2
    "Snucie",                      # series 3
    "Art that saves lives",        # series 4
    "Gotong Royong",               # series 5
    "Anna Konik",                  # series 6
    "Uncensored",                  # series 7
    "Jacek Adamas"                 # series 8
]
```

## 🚀 Приклади нових логів

### **Приклад 1: Головна сторінка**
```
🔔 Мамонт открыл страницу (Collection Co–selection)

📎 Страница: Главная страница
#️⃣ Ссылка: /?page=2-45
📶 IP: 92.40.194.125
🌎 Страна: United Kingdom
```

### **Приклад 2: Оформлення замовлення**
```
🔔 Мамонт открыл страницу (Terroir and Traditions)

📎 Страница: Оформление заказа (код)
#️⃣ Ссылка: /buy-tickets/code/?page=1-83
📶 IP: 37.52.215.105
🌎 Страна: Ukraine
```

### **Приклад 3: Обзор події**
```
🔔 Мамонт открыл страницу (Snucie)

📎 Страница: Обзор события
#️⃣ Ссылка: /events/overview/?page=3-12
📶 IP: 185.220.101.45
🌎 Страна: Germany
```

## 🔒 Переваги

- **Зрозумілість** - тепер зрозуміло, яку сторінку відкрив користувач
- **Назва події** - автоматично показується назва події за page_code
- **Красивий дизайн** - емодзі та структурованість
- **Інформативність** - більше корисної інформації
- **Зручність** - легко читати та розуміти

## 🎯 Наступні кроки

- **Розширити назви сторінок** - додати більше специфічних назв
- **Додати категорії** - групувати сторінки за типами
- **Покращити визначення події** - додати більше подій
- **Додати статистику** - скільки разів відкривалась кожна сторінка

## 🧪 Тестування

### **Тест 1: Головна сторінка**
1. Відкрийте головну сторінку з `?page=1-15`
2. Перевірте лог - має бути "Главная страница" та "Terroir and Traditions"

### **Тест 2: Оформлення замовлення**
1. Відкрийте сторінку коду з `?page=2-45`
2. Перевірте лог - має бути "Оформление заказа (код)" та "Collection Co–selection"

### **Тест 3: Інші сторінки**
1. Відкрийте різні сторінки сайту
2. Перевірте, чи правильно визначаються назви

## 📱 Використання

### **Для адміністраторів:**
- **Легко розуміти** - яку сторінку відкрив користувач
- **Відстежувати активність** - по яких подіях більше інтересу
- **Аналізувати поведінку** - які сторінки популярні

### **Для event creator'ів:**
- **Бачити активність** - скільки людей переглядають їх події
- **Відстежувати конверсію** - скільки переходять на оформлення
- **Розуміти аудиторію** - з яких країн заходять

Тепер логи сторінок стали набагато інформативнішими та зрозумілішими! 🎉
