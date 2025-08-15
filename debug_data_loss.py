#!/usr/bin/env python3
"""
Скрипт для діагностики втрати даних в реальному часі
Моніторить стан даних та виявляє, коли саме вони пропадають
"""

import requests
import time
import json
import sqlite3
from datetime import datetime

class DataLossDebugger:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.data_history = []
        self.error_count = 0
        
    def check_page_data(self, page_code="1-1"):
        """Перевіряє наявність даних на сторінці"""
        try:
            # Перевіряємо головну сторінку
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}"
            
            # Перевіряємо наявність даних про події
            has_event_date = 'event-date' in response.text
            has_event_time = 'event-time' in response.text
            has_price = '45' in response.text or 'FFF' in response.text
            
            # Перевіряємо API
            api_response = self.session.get(f"{self.base_url}/api/events_data_for_main_page?page={page_code}", timeout=5)
            api_working = api_response.status_code == 200
            
            if api_working:
                try:
                    api_data = api_response.json()
                    has_dates = 'dates' in api_data and len(api_data.get('dates', [])) > 0
                    has_events = 'events' in api_data and len(api_data.get('events', [])) > 0
                    has_price_api = 'price' in api_data and api_data['price']
                    has_currency_api = 'currency' in api_data and api_data['currency']
                except:
                    has_dates = False
                    has_events = False
                    has_price_api = False
                    has_currency_api = False
            else:
                has_dates = False
                has_events = False
                has_price_api = False
                has_currency_api = False
            
            # Формуємо результат
            result = {
                'timestamp': datetime.now().isoformat(),
                'page_code': page_code,
                'page_loaded': True,
                'has_event_date': has_event_date,
                'has_event_time': has_event_time,
                'has_price': has_price,
                'api_working': api_working,
                'has_dates': has_dates,
                'has_events': has_events,
                'has_price_api': has_price_api,
                'has_currency_api': has_currency_api,
                'all_data_present': has_event_date and has_event_time and has_price and has_dates and has_events and has_price_api and has_currency_api
            }
            
            return True, result
            
        except Exception as e:
            return False, str(e)
    
    def simulate_navigation_cycle(self, page_code="1-1", cycle_num=1):
        """Імітує цикл навігації та перевіряє стан даних"""
        print(f"\n🔄 Цикл {cycle_num}: Навігація з page_code={page_code}")
        
        # Крок 1: Перевіряємо початковий стан
        print("   Крок 1: Перевіряємо початковий стан даних")
        success, result = self.check_page_data(page_code)
        if not success:
            print(f"   ❌ Помилка перевірки: {result}")
            return False
        
        initial_state = result
        print(f"   ✅ Початковий стан: {'OK' if result['all_data_present'] else 'ПРОБЛЕМА'}")
        
        # Крок 2: Переходимо на виставку
        print("   Крок 2: Переходимо на виставку")
        exhibition_url = f"{self.base_url}/?page={page_code}"
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
        
        # Крок 3: Повертаємося на головну
        print("   Крок 3: Повертаємося на головну")
        home_url = f"{self.base_url}/"
        try:
            response = self.session.get(home_url, timeout=5)
            if response.status_code == 200:
                print("   ✅ Головна сторінка завантажена")
            else:
                print(f"   ❌ Помилка завантаження головної: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Помилка при поверненні на головну: {e}")
            return False
        
        # Крок 4: Перевіряємо стан даних після навігації
        print("   Крок 4: Перевіряємо стан даних після навігації")
        time.sleep(2)  # Даємо час на завантаження даних
        
        success, result = self.check_page_data(page_code)
        if not success:
            print(f"   ❌ Помилка перевірки після навігації: {result}")
            return False
        
        final_state = result
        
        # Аналізуємо зміни
        data_lost = initial_state['all_data_present'] and not final_state['all_data_present']
        
        if data_lost:
            print("   ❌ ДАНІ ВТРАЧЕНО!")
            self.error_count += 1
            
            # Детальний аналіз що саме втрачено
            if not final_state['has_event_date']:
                print("     - Втрачено дати подій на сторінці")
            if not final_state['has_event_time']:
                print("     - Втрачено час подій на сторінці")
            if not final_state['has_price']:
                print("     - Втрачено ціну на сторінці")
            if not final_state['has_dates']:
                print("     - Втрачено дати в API")
            if not final_state['has_events']:
                print("     - Втрачено події в API")
            if not final_state['has_price_api']:
                print("     - Втрачено ціну в API")
            if not final_state['has_currency_api']:
                print("     - Втрачено валюту в API")
        else:
            print("   ✅ Дані збережені")
        
        # Зберігаємо історію
        self.data_history.append({
            'cycle': cycle_num,
            'page_code': page_code,
            'initial_state': initial_state,
            'final_state': final_state,
            'data_lost': data_lost
        })
        
        return not data_lost
    
    def run_debug_test(self, cycles=10, page_codes=None):
        """Запускає тест діагностики"""
        print("🔍 ДІАГНОСТИКА ВТРАТИ ДАНИХ")
        print("=" * 50)
        
        if page_codes is None:
            page_codes = ["1-1", "2-1", "3-1", "4-1", "5-1"]
        
        successful_cycles = 0
        failed_cycles = 0
        
        for cycle in range(1, cycles + 1):
            page_code = page_codes[(cycle - 1) % len(page_codes)]
            
            if self.simulate_navigation_cycle(page_code, cycle):
                successful_cycles += 1
            else:
                failed_cycles += 1
            
            # Пауза між циклами
            if cycle < cycles:
                time.sleep(1)
        
        # Аналіз результатів
        print(f"\n📊 РЕЗУЛЬТАТИ ДІАГНОСТИКИ:")
        print(f"   Успішних циклів: {successful_cycles}")
        print(f"   Невдалих циклів: {failed_cycles}")
        print(f"   Загальна успішність: {(successful_cycles/cycles)*100:.1f}%")
        print(f"   Кількість втрат даних: {self.error_count}")
        
        # Аналіз коли саме втрачаються дані
        if self.error_count > 0:
            print(f"\n🔍 АНАЛІЗ ВТРАТ ДАНИХ:")
            for entry in self.data_history:
                if entry['data_lost']:
                    print(f"   Цикл {entry['cycle']} ({entry['page_code']}): дані втрачено")
                    print(f"     Початковий стан: {'OK' if entry['initial_state']['all_data_present'] else 'ПРОБЛЕМА'}")
                    print(f"     Кінцевий стан: {'OK' if entry['final_state']['all_data_present'] else 'ПРОБЛЕМА'}")
        
        return successful_cycles, failed_cycles
    
    def generate_report(self):
        """Генерує детальний звіт"""
        if not self.data_history:
            return "Немає даних для аналізу"
        
        report = []
        report.append("ДЕТАЛЬНИЙ ЗВІТ ДІАГНОСТИКИ")
        report.append("=" * 40)
        
        for entry in self.data_history:
            report.append(f"\nЦикл {entry['cycle']} ({entry['page_code']}):")
            report.append(f"  Початковий стан: {'✅' if entry['initial_state']['all_data_present'] else '❌'}")
            report.append(f"  Кінцевий стан: {'✅' if entry['final_state']['all_data_present'] else '❌'}")
            report.append(f"  Дані втрачено: {'❌ ТАК' if entry['data_lost'] else '✅ НІ'}")
            
            if entry['data_lost']:
                report.append("  Деталі втрати:")
                final = entry['final_state']
                if not final['has_event_date']:
                    report.append("    - Дати подій на сторінці")
                if not final['has_event_time']:
                    report.append("    - Час подій на сторінці")
                if not final['has_price']:
                    report.append("    - Ціна на сторінці")
                if not final['has_dates']:
                    report.append("    - Дати в API")
                if not final['has_events']:
                    report.append("    - Події в API")
                if not final['has_price_api']:
                    report.append("    - Ціна в API")
                if not final['has_currency_api']:
                    report.append("    - Валюта в API")
        
        return "\n".join(report)

def main():
    print("🚀 Запуск діагностики втрати даних...")
    
    debugger = DataLossDebugger()
    
    # Запускаємо тест
    successful, failed = debugger.run_debug_test(cycles=10)
    
    # Генеруємо звіт
    report = debugger.generate_report()
    print(f"\n{report}")
    
    # Зберігаємо звіт у файл
    with open('data_loss_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Звіт збережено у файл 'data_loss_report.txt'")
    
    if failed == 0:
        print("\n✅ Діагностика завершена - проблем не виявлено!")
    else:
        print(f"\n⚠️ Діагностика виявила {failed} проблем")
        print("   Перевірте звіт для детального аналізу")
    
    return successful, failed

if __name__ == "__main__":
    main() 