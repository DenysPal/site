#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# Додаємо поточну директорію до шляху
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_channel_access():
    """Тестує доступ бота до каналу"""
    try:
        from config import PAYOUT_GROUP_ID
        from main import bot
        
        print(f"🔍 Тестуємо доступ бота до каналу...")
        print(f"PAYOUT_GROUP_ID: {PAYOUT_GROUP_ID}")
        
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
            print(f"   Перевірте, чи додано бота в канал як адміністратора")
            return False
        
        # Спробуємо надіслати тестове повідомлення
        try:
            test_msg = await bot.send_message(
                PAYOUT_GROUP_ID, 
                "🧪 Тестове повідомлення для перевірки доступу бота"
            )
            print(f"✅ Тестове повідомлення надіслано: {test_msg.message_id}")
            
            # Видаляємо тестове повідомлення
            await bot.delete_message(PAYOUT_GROUP_ID, test_msg.message_id)
            print(f"✅ Тестове повідомлення видалено")
            
        except Exception as e:
            print(f"❌ Не вдалося надіслати тестове повідомлення: {e}")
            return False
        
        print(f"\n✅ Тест доступу до каналу пройдено успішно!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка тесту: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_channel_access())
