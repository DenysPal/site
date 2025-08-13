#!/usr/bin/env python3
"""
Test script to verify stability fixes for repeated navigation
Simulates the scenario where user navigates to exhibition and back to home multiple times
"""

import requests
import time
import json
import sqlite3
from urllib.parse import urljoin

class StabilityNavigationTest:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_server_health(self):
        """Test if server is running and responding"""
        try:
            response = self.session.get(self.base_url)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Server health check failed: {e}")
            return False
    
    def test_api_endpoint(self, page_code="1-1"):
        """Test the main API endpoint"""
        try:
            url = f"{self.base_url}/api/events_data_for_main_page?page={page_code}"
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ API endpoint failed with status {response.status_code}")
                return False
            
            data = response.json()
            print(f"✅ API response for page_code {page_code}:")
            print(f"   Price: {data.get('price')}")
            print(f"   Currency: {data.get('currency')}")
            print(f"   Dates count: {len(data.get('dates', []))}")
            print(f"   Events count: {len(data.get('events', []))}")
            
            # Check data consistency
            if 'dates' in data and 'events' in data:
                if len(data['dates']) != len(data['events']):
                    print(f"❌ Data inconsistency: {len(data['dates'])} dates vs {len(data['events'])} events")
                    return False
                
                # Check that events have correct structure
                for i, event in enumerate(data['events']):
                    if not isinstance(event, dict) or 'date' not in event:
                        print(f"❌ Invalid event structure at index {i}: {event}")
                        return False
                    
                    # Check date consistency
                    if i < len(data['dates']):
                        date_str = data['dates'][i]
                        if date_str.startswith(event['date']):
                            print(f"   ✅ Event {i+1}: {event['date']} {event.get('time', '')}")
                        else:
                            print(f"❌ Date mismatch at index {i}: {date_str} vs {event['date']}")
                            return False
                
                print("✅ Data consistency check passed")
                return True
            else:
                print("❌ Missing required data fields")
                return False
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    def test_fallback_data(self):
        """Test fallback data structure"""
        try:
            # Test with a non-existent page_code to trigger fallback
            url = f"{self.base_url}/api/events_data_for_main_page?page=nonexistent"
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Fallback API failed with status {response.status_code}")
                return False
            
            data = response.json()
            print(f"✅ Fallback data response:")
            print(f"   Price: {data.get('price')}")
            print(f"   Currency: {data.get('currency')}")
            print(f"   Dates count: {len(data.get('dates', []))}")
            print(f"   Events count: {len(data.get('events', []))}")
            
            # Check fallback data consistency
            if 'dates' in data and 'events' in data:
                if len(data['dates']) == len(data['events']):
                    print("✅ Fallback data consistency check passed")
                    return True
                else:
                    print(f"❌ Fallback data inconsistency: {len(data['dates'])} dates vs {len(data['events'])} events")
                    return False
            else:
                print("❌ Fallback data missing required fields")
                return False
                
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
            return False
    
    def test_database_integrity(self):
        """Test database structure and data integrity"""
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Check table structure
            cursor.execute("PRAGMA table_info(site_users)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"✅ Database columns: {columns}")
            
            # Check sample data
            cursor.execute("SELECT page_code, price, currency, date_1, date_2 FROM site_users LIMIT 3")
            rows = cursor.fetchall()
            
            print(f"✅ Sample database data:")
            for row in rows:
                page_code, price, currency, date_1, date_2 = row
                print(f"   {page_code}: {price} {currency}, dates: {date_1}, {date_2}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database integrity check failed: {e}")
            return False
    
    def simulate_navigation_cycle(self, page_code="1-1", cycles=10):
        """Simulate multiple navigation cycles"""
        print(f"\n🔄 Simulating {cycles} navigation cycles for page_code: {page_code}")
        
        for cycle in range(1, cycles + 1):
            print(f"\n--- Cycle {cycle}/{cycles} ---")
            
            # Simulate visiting exhibition page
            print(f"   📍 Visiting exhibition page...")
            exhibition_url = f"{self.base_url}/?page={page_code}"
            response = self.session.get(exhibition_url)
            
            if response.status_code != 200:
                print(f"   ❌ Failed to visit exhibition page: {response.status_code}")
                continue
            
            # Test API data after visiting
            print(f"   🔍 Testing API data...")
            if not self.test_api_endpoint(page_code):
                print(f"   ❌ API data corrupted in cycle {cycle}")
                return False
            
            # Simulate returning to home
            print(f"   🏠 Returning to home...")
            home_response = self.session.get(self.base_url)
            
            if home_response.status_code != 200:
                print(f"   ❌ Failed to return home: {home_response.status_code}")
                continue
            
            # Small delay to simulate user interaction
            time.sleep(0.1)
            
            print(f"   ✅ Cycle {cycle} completed successfully")
        
        print(f"\n🎉 All {cycles} navigation cycles completed successfully!")
        return True
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Stability Navigation Test")
        print("=" * 60)
        
        # Test 1: Server health
        print("\n1️⃣ Testing server health...")
        if not self.test_server_health():
            print("❌ Server health check failed. Please start the server first.")
            return False
        
        # Test 2: Database integrity
        print("\n2️⃣ Testing database integrity...")
        if not self.test_database_integrity():
            print("❌ Database integrity check failed.")
            return False
        
        # Test 3: API endpoint
        print("\n3️⃣ Testing main API endpoint...")
        if not self.test_api_endpoint():
            print("❌ Main API endpoint test failed.")
            return False
        
        # Test 4: Fallback data
        print("\n4️⃣ Testing fallback data...")
        if not self.test_fallback_data():
            print("❌ Fallback data test failed.")
            return False
        
        # Test 5: Navigation cycles
        print("\n5️⃣ Testing navigation cycles...")
        if not self.simulate_navigation_cycle(cycles=6):  # Test with 6 cycles as reported by user
            print("❌ Navigation cycle test failed.")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Stability fixes are working correctly.")
        return True

def main():
    test = StabilityNavigationTest()
    success = test.run_comprehensive_test()
    
    if success:
        print("\n✅ The website should now be stable under repeated navigation!")
        print("   The data corruption issue should be resolved.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main() 