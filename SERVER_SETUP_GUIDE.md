# Server Setup Guide

This guide explains how to run your Django project on a different server/port to avoid conflicts with other projects.

## Quick Start

### Option 1: Use the Python Script (Recommended)
```bash
# Automatically find an available port (8001-8010)
python run_server.py

# Or specify a specific port
python run_server.py 8002
```

### Option 2: Use the Batch File (Windows)
```cmd
# Double-click run_server.bat or run from command prompt
run_server.bat
```

### Option 3: Use PowerShell (Windows)
```powershell
# Run with default port 8001
.\run_server.ps1

# Run with specific port
.\run_server.ps1 -Port 8002
```

### Option 4: Manual Django Command
```bash
# Run on specific port
python manage.py runserver 127.0.0.1:8001

# Run on all interfaces (accessible from other devices)
python manage.py runserver 0.0.0.0:8001
```

## Port Configuration

The server will automatically find an available port starting from 8001. If you want to use a different port range, edit the `find_available_port()` function in `run_server.py`.

## Common Ports to Avoid

- 8000 (default Django port)
- 3000 (common React/Node.js port)
- 5000 (common Flask port)
- 8080 (common alternative web server port)

## Accessing Your Application

Once the server starts, you can access your application at:
- `http://127.0.0.1:PORT` (local access only)
- `http://localhost:PORT` (local access only)
- `http://YOUR_IP:PORT` (if using 0.0.0.0, accessible from other devices)

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
1. The script will automatically try the next available port
2. Or manually specify a different port: `python run_server.py 8003`

### Permission Denied
If you get permission errors:
1. Try running as administrator (Windows)
2. Or use a port above 1024 (like 8001, 8002, etc.)

### Firewall Issues
If you can't access the server from other devices:
1. Make sure Windows Firewall allows Python
2. Or use `0.0.0.0:PORT` instead of `127.0.0.1:PORT`

## Environment Configuration

You can also set environment variables in `server_config.env`:
```
SERVER_PORT=8001
SERVER_HOST=127.0.0.1
```

## Production Deployment

For production, consider using:
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- Docker containers
- Cloud platforms (AWS, Heroku, etc.)

This setup is only for development purposes.

This guide explains how to run your Django project on a different server/port to avoid conflicts with other projects.

## Quick Start

### Option 1: Use the Python Script (Recommended)
```bash
# Automatically find an available port (8001-8010)
python run_server.py

# Or specify a specific port
python run_server.py 8002
```

### Option 2: Use the Batch File (Windows)
```cmd
# Double-click run_server.bat or run from command prompt
run_server.bat
```

### Option 3: Use PowerShell (Windows)
```powershell
# Run with default port 8001
.\run_server.ps1

# Run with specific port
.\run_server.ps1 -Port 8002
```

### Option 4: Manual Django Command
```bash
# Run on specific port
python manage.py runserver 127.0.0.1:8001

# Run on all interfaces (accessible from other devices)
python manage.py runserver 0.0.0.0:8001
```

## Port Configuration

The server will automatically find an available port starting from 8001. If you want to use a different port range, edit the `find_available_port()` function in `run_server.py`.

## Common Ports to Avoid

- 8000 (default Django port)
- 3000 (common React/Node.js port)
- 5000 (common Flask port)
- 8080 (common alternative web server port)

## Accessing Your Application

Once the server starts, you can access your application at:
- `http://127.0.0.1:PORT` (local access only)
- `http://localhost:PORT` (local access only)
- `http://YOUR_IP:PORT` (if using 0.0.0.0, accessible from other devices)

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
1. The script will automatically try the next available port
2. Or manually specify a different port: `python run_server.py 8003`

### Permission Denied
If you get permission errors:
1. Try running as administrator (Windows)
2. Or use a port above 1024 (like 8001, 8002, etc.)

### Firewall Issues
If you can't access the server from other devices:
1. Make sure Windows Firewall allows Python
2. Or use `0.0.0.0:PORT` instead of `127.0.0.1:PORT`

## Environment Configuration

You can also set environment variables in `server_config.env`:
```
SERVER_PORT=8001
SERVER_HOST=127.0.0.1
```

## Production Deployment

For production, consider using:
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- Docker containers
- Cloud platforms (AWS, Heroku, etc.)

This setup is only for development purposes.
