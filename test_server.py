#!/usr/bin/env python
"""
Test script to diagnose server issues
"""

import requests
import sys

def test_server(port=8001):
    """Test if the server is responding correctly"""
    url = f"http://127.0.0.1:{port}"
    
    print(f"Testing server at {url}")
    print("=" * 50)
    
    try:
        # Test basic connectivity
        response = requests.get(url, timeout=10)
        print(f"✅ Server is responding!")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Check if it's HTML content
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Server is returning HTML content")
            
            # Check for common Django patterns
            content = response.text
            if 'AAHAARA 360' in content:
                print("✅ Django application is working - found 'AAHAARA 360' in content")
            if 'csrf' in content.lower():
                print("✅ Django CSRF protection is active")
            if 'bootstrap' in content.lower():
                print("✅ Bootstrap CSS is loaded")
                
        else:
            print("❌ Server is not returning HTML content")
            print(f"Actual content type: {response.headers.get('content-type')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to server")
        print("Make sure the server is running on the specified port")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_different_ports():
    """Test common ports to see which ones are available"""
    ports = [8000, 8001, 8002, 8003, 8080, 3000]
    
    print("\nTesting different ports:")
    print("=" * 30)
    
    for port in ports:
        try:
            response = requests.get(f"http://127.0.0.1:{port}", timeout=2)
            print(f"Port {port}: ✅ Active (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"Port {port}: ❌ Not in use")
        except Exception as e:
            print(f"Port {port}: ❌ Error - {e}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    test_server(port)
    test_different_ports()

Test script to diagnose server issues
"""

import requests
import sys

def test_server(port=8001):
    """Test if the server is responding correctly"""
    url = f"http://127.0.0.1:{port}"
    
    print(f"Testing server at {url}")
    print("=" * 50)
    
    try:
        # Test basic connectivity
        response = requests.get(url, timeout=10)
        print(f"✅ Server is responding!")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Check if it's HTML content
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Server is returning HTML content")
            
            # Check for common Django patterns
            content = response.text
            if 'AAHAARA 360' in content:
                print("✅ Django application is working - found 'AAHAARA 360' in content")
            if 'csrf' in content.lower():
                print("✅ Django CSRF protection is active")
            if 'bootstrap' in content.lower():
                print("✅ Bootstrap CSS is loaded")
                
        else:
            print("❌ Server is not returning HTML content")
            print(f"Actual content type: {response.headers.get('content-type')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to server")
        print("Make sure the server is running on the specified port")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_different_ports():
    """Test common ports to see which ones are available"""
    ports = [8000, 8001, 8002, 8003, 8080, 3000]
    
    print("\nTesting different ports:")
    print("=" * 30)
    
    for port in ports:
        try:
            response = requests.get(f"http://127.0.0.1:{port}", timeout=2)
            print(f"Port {port}: ✅ Active (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"Port {port}: ❌ Not in use")
        except Exception as e:
            print(f"Port {port}: ❌ Error - {e}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    test_server(port)
    test_different_ports()
