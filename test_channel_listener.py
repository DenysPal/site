#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# Додаємо поточну директорію до шляху
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_channel_listener():
    """Тестує, чи може бот слухати канал"""
    try:
        from config import PAYOUT_GROUP_ID
        from main import bot, router
        
        print(f"🔍 Тестуємо слухання каналу...")
        print(f"PAYOUT_GROUP_ID: {PAYOUT_GROUP_ID}")
        print(f"Type: {type(PAYOUT_GROUP_ID)}")
        
        # Перевіряємо, чи правильно налаштований router
        print(f"Router handlers count: {len(router.message.handlers)}")
        
        # Перевіряємо, чи є handler для каналу
        channel_handlers = [h for h in router.message.handlers if hasattr(h, 'filters')]
        print(f"Channel handlers: {len(channel_handlers)}")
        
        # Спробуємо отримати інформацію про канал
        try:
            chat = await bot.get_chat(PAYOUT_GROUP_ID)
            print(f"✅ Бот має доступ до каналу:")
            print(f"   Назва: {chat.title}")
            print(f"   Тип: {chat.type}")
            print(f"   ID: {chat.id}")
            
            # Перевіряємо права бота
            try:
                member = await bot.get_chat_member(PAYOUT_GROUP_ID, bot.id)
                print(f"   Права бота: {member.status}")
                print(f"   Може читати повідомлення: {member.can_read_messages if hasattr(member, 'can_read_messages') else 'Unknown'}")
            except Exception as e:
                print(f"   ⚠️ Не вдалося перевірити права бота: {e}")
                
        except Exception as e:
            print(f"❌ Бот не має доступу до каналу: {e}")
            return False
        
        # Тестуємо, чи може бот отримувати оновлення
        print(f"\n🧪 Тестуємо отримання оновлень...")
        
        # Створюємо простий handler для тесту
        @router.message(lambda m: m.chat.id == PAYOUT_GROUP_ID)
        async def test_channel_handler(message):
            print(f"🎯 [TEST] Отримано повідомлення з каналу: {message.text}")
            return True
        
        print(f"✅ Тестовий handler створено")
        print(f"Тепер надішліть будь-яке повідомлення в канал 'Выплаты'")
        print(f"Якщо бот його прочитає, то з'явиться лог: [TEST] Отримано повідомлення з каналу: ...")
        
        # Запускаємо polling для тесту
        print(f"\n🚀 Запускаємо polling для тесту...")
        await bot.session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тесту: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_channel_listener())
