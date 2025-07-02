# 🌐 Настройка домена artpullse.com

## 📋 Ваши данные
- **Домен:** `artpullse.com`
- **IP сервера:** `37.52.208.109`
- **Порт:** `8080`
- **Папка с сайтом:** `events-art.com`

## 🔧 Настройка DNS записей

В панели управления доменом `artpullse.com` создайте:

### A запись (основная):
- **Имя:** `@` (или оставить пустым)
- **Тип:** `A`
- **Значение:** `37.52.208.109`
- **TTL:** `3600`

### CNAME запись (для www):
- **Имя:** `www`
- **Тип:** `CNAME`
- **Значение:** `artpullse.com`
- **TTL:** `3600`

## 🚀 Запуск сервера

### Вариант 1: Специальный сервер для домена
```powershell
python server_artpullse.py
```

### Вариант 2: Обычный сервер
```powershell
python server_8080.py
```

## 🤖 Запуск Telegram бота
```powershell
python bot.py
```

## 🌐 Доступ к сайту

После настройки DNS (может занять до 24 часов):

- **Основной сайт:** `http://artpullse.com:8080`
- **С www:** `http://www.artpullse.com:8080`
- **Локально:** `http://localhost:8080`

## 📱 Telegram бот

Бот теперь генерирует ссылки вида:
```
http://artpullse.com:8080/events-art.com/terroir-and-traditions/index.html?event=ID&item=1
```

## 🔍 Проверка настройки

### Проверка DNS:
```powershell
nslookup artpullse.com
```
Должен вернуть: `37.52.208.109`

### Проверка доступности:
```powershell
Invoke-WebRequest -Uri "http://artpullse.com:8080" -UseBasicParsing
```

## ⚠️ Важные моменты

1. **DNS обновление** может занять до 24 часов
2. **Порт 8080** должен быть открыт в файрволе
3. **Сервер должен работать** постоянно для доступности сайта
4. **Для продакшена** рекомендуется:
   - Использовать nginx/Apache
   - Настроить SSL сертификат
   - Использовать порт 80/443

## 🔒 Безопасность

### Открытие порта в файрволе Windows:
```powershell
# Открыть порт 8080
netsh advfirewall firewall add rule name="Events Art Server" dir=in action=allow protocol=TCP localport=8080
```

### SSL сертификат (рекомендуется):
Для HTTPS используйте Let's Encrypt или Cloudflare.

## 📞 Поддержка

Если сайт не открывается:
1. Проверьте что сервер запущен
2. Проверьте DNS записи
3. Проверьте файрвол
4. Проверьте доступность порта 8080

## 🎯 Готово!

После настройки DNS ваш сайт будет доступен по адресу:
**http://artpullse.com:8080** 