# 🔄 Оновлення файлів на сервері

## 📋 Файли для оновлення

### 🔧 Основні серверні файли (ОБОВ'ЯЗКОВО оновити):

1. **`server.py`** - Основний сервер (порт 80) ✅ **ОНОВЛЕНО**
2. **`server_8080.py`** - Альтернативний сервер (порт 8080) ✅ **ОНОВЛЕНО** 
3. **`server_artpullse.py`** - Спеціальний сервер для домену artpullse.com ✅ **ОНОВЛЕНО**

### 🆕 Нові файли (додати):

4. **`test_server.py`** - Тестування сервера
5. **`start_all.py`** - Запуск всіх сервісів
6. **`README.md`** - Інструкції
7. **`SERVER_UPDATE.md`** - Ця інструкція

### 🤖 Бот (залишити як є):

8. **`main.py`** - Telegram бот (НЕ змінювати)

## 🚀 Як зараз запускається проект

### Поточний спосіб запуску:

```bash
# Запуск сервера (один з варіантів):
python server_8080.py          # Порт 8080
python server.py               # Порт 80 (потребує адмін прав)
python server_artpullse.py     # Спеціальний для artpullse.com

# Запуск бота (окремо):
python main.py

# Або запуск всього разом:
python start_all.py
```

## ✅ Що виправлено в цьому оновленні

### 🔧 Виправлення дублювання логів:

**Проблема:** При відкритті однієї сторінки надсилалося кілька логів у Telegram (для HTML, CSS, JS, картинок тощо).

**Рішення:** Додано фільтр логування:
- ✅ **Логується тільки:** відкриття основних сторінок (`/`, `/terroir-and-traditions/`, тощо)
- ❌ **НЕ логується:** CSS, JS, картинки, favicon, та інші ресурси

### 📝 Як працює нове логування:

```python
# Список розширень, які НЕ логувати
skip_ext = (
    '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.webp', '.json',
    '.woff', '.ttf', '.eot', '.otf', '.mp4', '.mp3', '.wav', '.ogg', '.zip', '.pdf',
    '.gif', '.bmp', '.tiff', '.map', '.txt', '.xml', '.html', '.htm'
)

# Логувати тільки якщо це основна сторінка
should_log = True
if any(path.endswith(ext) for ext in skip_ext):
    should_log = False
elif path == '/' or path.endswith('/'):
    should_log = True  # Логуємо головну сторінку
elif '/index.html' in path:
    should_log = True  # Логуємо index.html сторінки
```

## 🌐 Налаштування домену

### Для домену artpullse.com:

1. **A-запис:** `artpullse.com` → `37.52.208.109`
2. **CNAME-запис:** `www.artpullse.com` → `artpullse.com`
3. **Порт:** 8080 (додати до URL: `http://artpullse.com:8080/`)

### Альтернативні варіанти:

- **Порт 80:** `http://artpullse.com/` (потребує root-прав)
- **Локальний тест:** `http://localhost:8080/`

## 📊 Тестування

### Перевірка роботи:

1. **Запустіть сервер:**
   ```bash
   python server_8080.py
   ```

2. **Відкрийте сайт у браузері:**
   ```
   http://localhost:8080/
   ```

3. **Перевірте Telegram:**
   - Має прийти **один лог** на відкриття сторінки
   - НЕ має бути логів для CSS/JS файлів

### Якщо логи все ще дублюються:

1. Перевірте, чи оновлені всі серверні файли
2. Перезапустіть сервер
3. Очистіть кеш браузера

## 🔧 Діагностика проблем

### Сервер не запускається:
```bash
# Перевірте права
sudo python server.py

# Або використайте порт 8080
python server_8080.py
```

### Логи не надходять:
1. Перевірте BOT_TOKEN та GROUP_ID
2. Перевірте підключення до Інтернету
3. Перевірте, чи не заблокований Telegram

### Сайт не відкривається:
1. Перевірте, чи існує папка `events-art.com`
2. Перевірте, чи є файл `index.html`
3. Перевірте логи сервера

## 📞 Підтримка

Якщо виникли проблеми:
1. Перевірте логи сервера
2. Перевірте логи бота
3. Перевірте налаштування домену
4. Зверніться за допомогою з детальним описом проблеми 