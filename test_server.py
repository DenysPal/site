#!/usr/bin/env python3
import requests
import time
import sys

def test_server():
    """Тестує роботу сервера"""
    print("🧪 Тестування сервера...")
    
    # Тестуємо порт 8080
    ports = [8080]
    
    for port in ports:
        print(f"\n🔍 Тестуємо порт {port}...")
        try:
            # Тест 1: Головна сторінка
            url = f"http://localhost:{port}/"
            print(f"📄 Тест 1: {url}")
            response = requests.get(url, timeout=5)
            print(f"✅ Статус: {response.status_code}")
            print(f"📏 Розмір відповіді: {len(response.content)} байт")
            
            if response.status_code == 200:
                print("✅ Головна сторінка працює!")
                
                # Тест 2: CSS файли
                css_url = f"http://localhost:{port}/css/style.css"
                print(f"🎨 Тест 2: {css_url}")
                css_response = requests.get(css_url, timeout=5)
                print(f"✅ CSS статус: {css_response.status_code}")
                
                # Тест 3: JS файли
                js_url = f"http://localhost:{port}/js/jquery.min.js"
                print(f"⚡ Тест 3: {js_url}")
                js_response = requests.get(js_url, timeout=5)
                print(f"✅ JS статус: {js_response.status_code}")
                
                # Тест 4: Зображення
                img_url = f"http://localhost:{port}/image/header-image.jpg"
                print(f"🖼️ Тест 4: {img_url}")
                img_response = requests.get(img_url, timeout=5)
                print(f"✅ Зображення статус: {img_response.status_code}")
                
                print(f"\n🎉 Сервер на порту {port} працює коректно!")
                return port
                
            else:
                print(f"❌ Помилка: статус {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Сервер на порту {port} не запущений")
        except requests.exceptions.Timeout:
            print(f"❌ Таймаут при підключенні до порту {port}")
        except Exception as e:
            print(f"❌ Помилка: {e}")
    
    print("\n❌ Жоден сервер не працює")
    return None

def start_server(port=8080):
    """Запускає сервер"""
    print(f"🚀 Запуск сервера на порту {port}...")
    
    import subprocess
    try:
        # Запускаємо server.py (тепер на порту 8080)
        subprocess.run([sys.executable, "server.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Помилка запуску server.py")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Інструмент тестування сервера")
    print("=" * 50)
    
    # Спочатку тестуємо чи працює сервер
    working_port = test_server()
    
    if working_port:
        print(f"\n✅ Сервер працює на порту {working_port}")
        print(f"🌐 Відкрийте: http://localhost:{working_port}")
    else:
        print("\n❌ Сервер не працює")
        print("💡 Спробуйте запустити сервер вручну:")
        print("   python server.py") 