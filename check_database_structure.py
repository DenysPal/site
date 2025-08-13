#!/usr/bin/env python3
import sqlite3
import json

def check_database():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check site_users table structure
        if ('site_users',) in tables:
            cursor.execute("PRAGMA table_info(site_users);")
            columns = cursor.fetchall()
            print("\nsite_users table structure:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Check data in site_users
            cursor.execute("SELECT COUNT(*) FROM site_users;")
            count = cursor.fetchone()[0]
            print(f"\nTotal records in site_users: {count}")
            
            if count > 0:
                cursor.execute("SELECT page_code, price, currency, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, ip, created_at FROM site_users LIMIT 3;")
                rows = cursor.fetchall()
                print("\nSample data from site_users:")
                for row in rows:
                    page_code, price, currency, d1, d2, d3, d4, d5, d6, d7, d8, ip, created = row
                    print(f"  page_code: {page_code}")
                    print(f"  price: {price}")
                    print(f"  currency: {currency}")
                    print(f"  dates: {d1}, {d2}, {d3}, {d4}, {d5}, {d6}, {d7}, {d8}")
                    print(f"  ip: {ip}")
                    print(f"  created: {created}")
                    print("  ---")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database() 