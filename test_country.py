#!/usr/bin/env python3

import requests

def test_country_detection():
    """Тестує визначення країни за IP"""
    
    # Тестові IP адреси
    test_ips = [
        "37.52.215.105",  # IP з вашого логу
        "8.8.8.8",        # Google DNS
        "1.1.1.1",        # Cloudflare DNS
        "208.67.222.222"  # OpenDNS
    ]
    
    print("🌍 Тестуємо визначення країни за IP...")
    
    for ip in test_ips:
        try:
            print(f"\n🔍 Тестуємо IP: {ip}")
            
            # Робимо запит до ipinfo.io
            resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Відповідь: {data}")
                
                country_code = data.get("country", "")
                city = data.get("city", "")
                region = data.get("region", "")
                
                print(f"🌍 Країна (код): {country_code}")
                print(f"🏙️ Місто: {city}")
                print(f"🏛️ Регіон: {region}")
                
            else:
                print(f"❌ Помилка: статус {resp.status_code}")
                
        except Exception as e:
            print(f"❌ Помилка при тестуванні {ip}: {e}")
    
    print("\n✅ Тестування завершено!")

if __name__ == "__main__":
    test_country_detection()
