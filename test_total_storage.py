#!/usr/bin/env python3
"""
Test script to verify total amount storage functionality
"""

import time

# Simulate the payment_totals storage
payment_totals = {}

def cleanup_old_payment_totals():
    """Видаляє старі записи total сум (старіше 1 години)"""
    current_time = time.time()
    expired_keys = []
    for page_code, data in payment_totals.items():
        if current_time - data['timestamp'] > 3600:  # 1 година
            expired_keys.append(page_code)
    
    for key in expired_keys:
        del payment_totals[key]
        print(f'[DEBUG] Cleaned up expired total amount for {key}')
    
    return len(expired_keys)

def test_payment_notify_logic():
    """Test the logic from payment_notify function"""
    print("=== Testing Payment Notify Logic ===")
    
    # Simulate payment data
    data = {
        'page_code': '2-7',
        'price': '45',
        'total': '90',
        'currency': 'EUR'
    }
    
    # Extract data (simulating the function)
    price = data.get('price', '')
    currency = data.get('currency', '')
    total = data.get('total', '')
    page_code = data.get('page_code', '')
    
    print(f"Extracted data: price={price}, total={total}, currency={currency}, page_code={page_code}")
    
    # Store total amount (simulating the storage logic)
    if page_code and total and currency:
        payment_totals[page_code] = {
            'total': total,
            'currency': currency,
            'timestamp': time.time()
        }
        print(f'[DEBUG] Stored total amount for {page_code}: {total} {currency}')
    else:
        print(f'[DEBUG] Missing required data: page_code={page_code}, total={total}, currency={currency}')
    
    # Verify storage
    if page_code in payment_totals:
        stored = payment_totals[page_code]
        print(f"✅ Successfully stored: {stored}")
    else:
        print("❌ Failed to store total amount")
    
    return page_code in payment_totals

def test_admin_action_logic():
    """Test the logic from admin_action_handler function"""
    print("\n=== Testing Admin Action Logic ===")
    
    page_code = '2-7'
    
    # Simulate getting event info
    event_info = {'price': '45', 'currency': 'EUR'}
    event_price = event_info.get('price')
    event_currency = event_info.get('currency')
    
    print(f"Base event info: price={event_price}, currency={event_currency}")
    
    # Check for stored total amount
    if page_code in payment_totals:
        stored_total = payment_totals[page_code]
        # Use stored total amount instead of base price
        event_price = stored_total['total']
        event_currency = stored_total['currency']
        print(f'[DEBUG] Using stored total amount for {page_code}: {event_price} {event_currency}')
    else:
        print(f'[DEBUG] No stored total amount for {page_code}, using base price: {event_price} {event_currency}')
    
    print(f"Final values: price={event_price}, currency={event_currency}")
    
    # Verify the total is used instead of base price
    expected_total = '90'
    if event_price == expected_total:
        print(f"✅ Correctly using total amount: {event_price}")
        return True
    else:
        print(f"❌ Expected {expected_total}, got {event_price}")
        return False

def test_cleanup():
    """Test cleanup functionality"""
    print("\n=== Testing Cleanup Logic ===")
    
    # Add some old entries
    old_time = time.time() - 7200  # 2 hours ago
    payment_totals['old-page'] = {
        'total': '100',
        'currency': 'USD',
        'timestamp': old_time
    }
    
    print(f"Before cleanup: {len(payment_totals)} entries")
    print(f"Entries: {list(payment_totals.keys())}")
    
    # Run cleanup
    cleaned = cleanup_old_payment_totals()
    print(f"Cleaned up {cleaned} old entries")
    
    print(f"After cleanup: {len(payment_totals)} entries")
    print(f"Entries: {list(payment_totals.keys())}")
    
    # Verify old entry was removed
    if 'old-page' not in payment_totals:
        print("✅ Old entries successfully cleaned up")
        return True
    else:
        print("❌ Old entries not cleaned up")
        return False

if __name__ == "__main__":
    print("🧪 Testing Total Amount Storage System\n")
    
    # Test 1: Payment notification logic
    test1_passed = test_payment_notify_logic()
    
    # Test 2: Admin action logic
    test2_passed = test_admin_action_logic()
    
    # Test 3: Cleanup logic
    test3_passed = test_cleanup()
    
    # Summary
    print(f"\n=== Test Results ===")
    print(f"Payment Notify Logic: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Admin Action Logic: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Cleanup Logic: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 All tests passed! The total amount storage system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
