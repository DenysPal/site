#!/usr/bin/env python3
import sqlite3
import json

def test_database_fixes():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Test the query that the server now uses
        page_code = '1-1'  # Use an existing page_code from the database
        
        print(f"Testing database query for page_code: {page_code}")
        
        cursor.execute('''
            SELECT price, currency, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8
            FROM site_users 
            WHERE page_code = ? AND (date_1 IS NOT NULL OR date_2 IS NOT NULL)
        ''', (page_code,))
        
        result = cursor.fetchone()
        
        if result:
            price, currency, d1, d2, d3, d4, d5, d6, d7, d8 = result
            print(f"Query successful!")
            print(f"Price: {price}")
            print(f"Currency: {currency}")
            print(f"Dates: {d1}, {d2}, {d3}, {d4}, {d5}, {d6}, {d7}, {d8}")
            
            # Test the data processing logic
            dates = []
            events = []
            
            for date_val in [d1, d2, d3, d4, d5, d6, d7, d8]:
                if date_val and date_val.strip():
                    dates.append(date_val)
                    if ' ' in date_val:
                        date_part, time_part = date_val.split(' ', 1)
                        events.append({
                            'name': f'Event {len(events) + 1}',
                            'date': date_part,
                            'time': time_part
                        })
                    else:
                        events.append({
                            'name': f'Event {len(events) + 1}',
                            'date': date_val,
                            'time': ''
                        })
            
            print(f"\nProcessed data:")
            print(f"Dates array: {dates}")
            print(f"Events array: {json.dumps(events, indent=2)}")
            
            # Test the response structure
            response_data = {
                'price': price or '45',
                'currency': currency or 'EUR',
                'dates': dates,
                'events': events
            }
            
            print(f"\nFinal response data:")
            print(json.dumps(response_data, indent=2))
            
        else:
            print(f"No data found for page_code: {page_code}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error testing database fixes: {e}")

if __name__ == "__main__":
    test_database_fixes() 