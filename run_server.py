#!/usr/bin/env python
"""
Script to run Django development server on a different port
to avoid conflicts with other projects.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def find_available_port(start_port=8001, max_port=8010):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port  # Fallback to start_port if none available

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()
    
    # Get port from command line argument or find available port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            port = find_available_port()
    else:
        port = find_available_port()
    
    print(f"Starting Django server on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server")
    
    sys.argv = ['manage.py', 'runserver', f'127.0.0.1:{port}']
    execute_from_command_line(sys.argv)

Script to run Django development server on a different port
to avoid conflicts with other projects.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def find_available_port(start_port=8001, max_port=8010):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port  # Fallback to start_port if none available

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()
    
    # Get port from command line argument or find available port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            port = find_available_port()
    else:
        port = find_available_port()
    
    print(f"Starting Django server on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server")
    
    sys.argv = ['manage.py', 'runserver', f'127.0.0.1:{port}']
    execute_from_command_line(sys.argv)
