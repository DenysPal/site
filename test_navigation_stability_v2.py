#!/usr/bin/env python3
"""
Оновлений тестовий скрипт для перевірки стабільності навігації з новою логікою last_page_code
"""

import requests
import time
import json
import sqlite3
from urllib.parse import urljoin

class NavigationStabilityTestV2:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def test_server_health(self):
        """Перевіряє чи сервер працює"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Сервер не доступний: {e}")
            return False
    
    def test_api_endpoint(self, page_code="1-1"):
        """Тестує API endpoint для отримання даних"""
        try:
            api_url = f"{self.base_url}/api/events_data_for_main_page?page={page_code}"
            response = self.session.get(api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API endpoint працює для page_code: {page_code}")
                print(f"   Отримано: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True, data
            else:
                print(f"❌ API endpoint повернув статус: {response.status_code}")
                return False, None
        except Exception as e:
            print(f"❌ Помилка API endpoint: {e}")
            return False, None
    
    def test_database_connection(self):
        """Перевіряє підключення до бази даних"""
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Перевіряємо структуру таблиці
            cursor.execute("PRAGMA table_info(site_users)")
            columns = cursor.fetchall()
            
            print("✅ База даних доступна")
            print(f"   Структура таблиці site_users:")
            for col in columns:
                print(f"     {col[1]} ({col[2]})")
            
            # Перевіряємо дані
            cursor.execute("SELECT COUNT(*) FROM site_users")
            count = cursor.fetchone()[0]
            print(f"   Кількість записів: {count}")
            
            if count > 0:
                cursor.execute("SELECT page_code, price, currency, date_1, date_2 FROM site_users LIMIT 1")
                sample = cursor.fetchone()
                print(f"   Приклад даних: {sample}")
            
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Помилка бази даних: {e}")
            return False
    
    def simulate_navigation_cycle(self, page_code="1-1", cycle_num=1):
        """Імітує один цикл навігації: виставка -> головна"""
        print(f"\n🔄 Цикл {cycle_num}: Навігація з page_code={page_code}")
        
        # Крок 1: Заходимо на сторінку виставки
        exhibition_url = f"{self.base_url}/?page={page_code}"
        print(f"   Крок 1: Переходимо на виставку: {exhibition_url}")
        
        try:
            response = self.session.get(exhibition_url, timeout=5)
            if response.status_code == 200:
                print("   ✅ Сторінка виставки завантажена")
                
                # Перевіряємо чи є дані про події
                if 'event-date' in response.text and 'event-time' in response.text:
                    print("   ✅ Дані про події присутні на сторінці")
                else:
                    print("   ⚠️ Дані про події відсутні на сторінці")
            else:
                print(f"   ❌ Помилка завантаження виставки: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Помилка при переході на виставку: {e}")
            return False
        
        # Крок 2: Повертаємося на головну сторінку
        home_url = f"{self.base_url}/"
        print(f"   Крок 2: Повертаємося на головну: {home_url}")
        
        try:
            response = self.session.get(home_url, timeout=5)
            if response.status_code == 200:
                print("   ✅ Головна сторінка завантажена")
                
                # Перевіряємо чи є дані про події на головній
                if 'event-date' in response.text and 'event-time' in response.text:
                    print("   ✅ Дані про події присутні на головній")
                else:
                    print("   ⚠️ Дані про події відсутні на головній")
            else:
                print(f"   ❌ Помилка завантаження головної: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Помилка при поверненні на головну: {e}")
            return False
        
        # Крок 3: Перевіряємо API після навігації
        print(f"   Крок 3: Перевіряємо API після навігації")
        api_success, api_data = self.test_api_endpoint(page_code)
        
        if api_success and api_data:
            # Перевіряємо структуру даних
            if 'dates' in api_data and 'events' in api_data:
                dates_count = len(api_data['dates']) if api_data['dates'] else 0
                events_count = len(api_data['events']) if api_data['events'] else 0
                print(f"   ✅ API дані коректні: {dates_count} дат, {events_count} подій")
                
                # Зберігаємо результат для аналізу
                self.test_results.append({
                    'cycle': cycle_num,
                    'page_code': page_code,
                    'api_success': True,
                    'dates_count': dates_count,
                    'events_count': events_count,
                    'data_integrity': dates_count == events_count
                })
                
                return True
            else:
                print(f"   ❌ API дані мають неправильну структуру: {list(api_data.keys())}")
                self.test_results.append({
                    'cycle': cycle_num,
                    'page_code': page_code,
                    'api_success': True,
                    'data_integrity': False,
                    'error': 'Неправильна структура даних'
                })
                return False
        else:
            print(f"   ❌ API не працює після навігації")
            self.test_results.append({
                'cycle': cycle_num,
                'page_code': page_code,
                'api_success': False,
                'error': 'API не відповідає'
            })
            return False
    
    def test_last_page_code_logic(self):
        """Тестує логіку роботи з last_page_code"""
        print(f"\n🧪 Тестування логіки last_page_code")
        
        # Тест 1: Переходимо на виставку
        page_code = "1-1"
        exhibition_url = f"{self.base_url}/?page={page_code}"
        print(f"   Тест 1: Переходимо на виставку {page_code}")
        
        try:
            response = self.session.get(exhibition_url, timeout=5)
            if response.status_code == 200:
                print("   ✅ Сторінка виставки завантажена")
            else:
                print(f"   ❌ Помилка завантаження виставки: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Помилка при переході на виставку: {e}")
            return False
        
        # Тест 2: Переходимо на головну (імітуємо натискання кнопки Home)
        home_url = f"{self.base_url}/"
        print(f"   Тест 2: Переходимо на головну (імітуємо кнопку Home)")
        
        try:
            response = self.session.get(home_url, timeout=5)
            if response.status_code == 200:
                print("   ✅ Головна сторінка завантажена")
                
                # Перевіряємо чи є дані про події на головній
                if 'event-date' in response.text and 'event-time' in response.text:
                    print("   ✅ Дані про події присутні на головній після переходу")
                else:
                    print("   ⚠️ Дані про події відсутні на головній після переходу")
            else:
                print(f"   ❌ Помилка завантаження головної: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Помилка при поверненні на головну: {e}")
            return False
        
        # Тест 3: Перевіряємо API на головній сторінці
        print(f"   Тест 3: Перевіряємо API на головній сторінці")
        api_success, api_data = self.test_api_endpoint(page_code)
        
        if api_success and api_data:
            print("   ✅ API працює на головній сторінці")
            return True
        else:
            print("   ❌ API не працює на головній сторінці")
            return False
    
    def run_stability_test(self, cycles=10, page_codes=None):
        """Запускає тест стабільності для кількох циклів"""
        print(f"\n🚀 Запуск тесту стабільності навігації")
        print(f"   Кількість циклів: {cycles}")
        
        if page_codes is None:
            page_codes = ["1-1", "2-1", "3-1", "4-1", "5-1"]
        
        print(f"   Тестові page_codes: {page_codes}")
        
        successful_cycles = 0
        failed_cycles = 0
        
        for cycle in range(1, cycles + 1):
            # Використовуємо різні page_codes для різноманітності
            page_code = page_codes[(cycle - 1) % len(page_codes)]
            
            if self.simulate_navigation_cycle(page_code, cycle):
                successful_cycles += 1
                print(f"   ✅ Цикл {cycle} завершено успішно")
            else:
                failed_cycles += 1
                print(f"   ❌ Цикл {cycle} завершено з помилками")
            
            # Невелика пауза між циклами
            if cycle < cycles:
                time.sleep(1)
        
        # Аналіз результатів
        print(f"\n📊 Результати тестування:")
        print(f"   Успішних циклів: {successful_cycles}")
        print(f"   Невдалих циклів: {failed_cycles}")
        print(f"   Загальна успішність: {(successful_cycles/cycles)*100:.1f}%")
        
        # Аналіз цілісності даних
        successful_results = [r for r in self.test_results if r.get('api_success', False)]
        if successful_results:
            data_integrity_count = sum(1 for r in successful_results if r.get('data_integrity', False))
            print(f"   Цілісність даних: {data_integrity_count}/{len(successful_results)} ({data_integrity_count/len(successful_results)*100:.1f}%)")
        
        return successful_cycles, failed_cycles
    
    def analyze_failures(self):
        """Аналізує невдалі цикли"""
        failed_results = [r for r in self.test_results if not r.get('api_success', False)]
        
        if failed_results:
            print(f"\n🔍 Аналіз невдач:")
            for result in failed_results:
                print(f"   Цикл {result['cycle']}: {result.get('error', 'Невідома помилка')}")
        else:
            print(f"\n✅ Всі цикли завершилися успішно")
    
    def run_comprehensive_test(self):
        """Запускає комплексний тест"""
        print("🧪 КОМПЛЕКСНИЙ ТЕСТ СТАБІЛЬНОСТІ НАВІГАЦІЇ V2")
        print("=" * 60)
        
        # Перевірка сервера
        if not self.test_server_health():
            print("❌ Тест зупинено: сервер не доступний")
            return False
        
        # Перевірка бази даних
        if not self.test_database_connection():
            print("⚠️ Попередження: проблеми з базою даних")
        
        # Тест API
        print(f"\n🔌 Тестування API endpoints...")
        api_success, api_data = self.test_api_endpoint("1-1")
        if not api_success:
            print("❌ API не працює, тест зупинено")
            return False
        
        # Тест логіки last_page_code
        print(f"\n🔑 Тестування логіки last_page_code...")
        if not self.test_last_page_code_logic():
            print("⚠️ Попередження: проблеми з логікою last_page_code")
        
        # Тест стабільності навігації
        print(f"\n🧭 Тестування стабільності навігації...")
        successful, failed = self.run_stability_test(cycles=10)
        
        # Аналіз результатів
        self.analyze_failures()
        
        # Загальний результат
        if failed == 0:
            print(f"\n🎉 ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
            return True
        else:
            print(f"\n⚠️ Тест виявив {failed} проблем")
            return False

def main():
    print("🚀 Запуск оновленого тесту стабільності навігації...")
    
    # Створюємо тестер
    tester = NavigationStabilityTestV2()
    
    # Запускаємо комплексний тест
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ Тест завершено успішно - всі проблеми вирішено!")
    else:
        print("\n❌ Тест виявив проблеми, які потребують додаткового виправлення")
    
    return success

if __name__ == "__main__":
    main() 