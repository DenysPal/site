#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def test_country_detection():
    """Test country detection by IP"""
    
    # Test IP addresses
    test_ips = [
        "37.52.215.105",  # IP from your log
        "8.8.8.8",        # Google DNS
        "1.1.1.1",        # Cloudflare DNS
        "208.67.222.222"  # OpenDNS
    ]
    
    print("Testing country detection by IP...")
    
    for ip in test_ips:
        try:
            print("\nTesting IP: {}".format(ip))
            
            # Make request to ipinfo.io
            resp = requests.get("https://ipinfo.io/{}/json".format(ip), timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                print("Response: {}".format(data))
                
                country_code = data.get("country", "")
                city = data.get("city", "")
                region = data.get("region", "")
                
                print("Country (code): {}".format(country_code))
                print("City: {}".format(city))
                print("Region: {}".format(region))
                
            else:
                print("Error: status {}".format(resp.status_code))
                
        except Exception as e:
            print("Error testing {}: {}".format(ip, e))
    
    print("\nTesting completed!")

if __name__ == "__main__":
    test_country_detection()

if __name__ == "__main__":
    test_country_detection()
