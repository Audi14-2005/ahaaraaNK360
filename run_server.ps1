# PowerShell script to run Django server on different port
param(
    [int]$Port = 8001
)

Write-Host "Starting Django server on port $Port..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:$Port" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan

python run_server.py $Port
