# 🚀 Швидкий запуск системи квитків

## ⚡ Швидка перевірка

### 1. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 2. Тестування системи
```bash
python test_ticket_system.py
```

### 3. Демонстрація генерації
```bash
python demo_ticket_generation.py
```

## 🎯 Як використовувати

### Через Telegram бота:
1. Запустіть бота: `python main.py`
2. Натисніть кнопку **"🎫Билеты"**
3. Введіть дані у форматі:
   ```
   Ім'я Прізвище
   21:00
   23.05
   40 €
   Адрес події
   ```

### Результат:
- ✅ PDF квиток створено
- 🔗 Посилання на квиток
- 📱 Файл відправлено в чат

## 📁 Структура файлів
```
├── main.py                    # Основний бот
├── requirements.txt           # Залежності
├── test_ticket_system.py     # Тестування
├── demo_ticket_generation.py # Демонстрація
├── tickets/                  # Локальні квитки
└── events-art.com/           # Веб-файли
    ├── file/ticket/          # Веб-доступні квитки
    └── image/                # Зображення для квитків
```

## 🔧 Якщо щось не працює

1. **Перевірте залежності**: `python test_ticket_system.py`
2. **Створіть папки**: `mkdir -p tickets events-art.com/file/ticket`
3. **Додайте зображення** в `events-art.com/image/`
4. **Перевірте логи** бота

## 📞 Підтримка
- Детальна документація: `TICKET_SYSTEM_README.md`
- Тестування: `test_ticket_system.py`
- Демонстрація: `demo_ticket_generation.py`

---

**Готово! 🎉** Система квитків налаштована та готова до роботи.
