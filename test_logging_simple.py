#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def test_logging():
    """Test page logging"""
    
    base_url = "http://127.0.0.1:8080"
    
    # Test real pages (should be logged)
    test_pages = [
        "/",
        "/jacek-adamas/",
        "/terroir-and-traditions/"
    ]
    
    print("Testing page logging...")
    
    for page in test_pages:
        try:
            print("\nTesting page: {}".format(page))
            
            # Make request to page
            response = requests.get("{}{}".format(base_url, page), timeout=10)
            
            if response.status_code == 200:
                print("Page {} loaded successfully".format(page))
                print("Response size: {} bytes".format(len(response.content)))
            else:
                print("Error loading {}: {}".format(page, response.status_code))
                
        except Exception as e:
            print("Error testing {}: {}".format(page, e))
        
        # Delay between requests
        time.sleep(2)
    
    print("\nTesting completed!")
    print("Check Telegram bot for logs")

if __name__ == "__main__":
    test_logging()
