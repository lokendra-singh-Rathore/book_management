# Frontend Setup Script - Run this in PowerShell from the frontend directory

Write-Host "Creating React Frontend Structure..." -ForegroundColor Green

# Create directories
$dirs = @(
    "src/lib",
    "src/services", 
    "src/store",
    "src/components/common",
    "src/components/layout",
    "src/pages"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "Created $dir" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Creating source files..." -ForegroundColor Green

# Create .env file
$envContent = @"
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/chat/ws
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8

Write-Host ""
Write-Host "Directory structure created!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy the code from COMPLETE_FRONTEND_CODE.md to create the source files"  
Write-Host "2. Run: npm install"
Write-Host "3. Run: npm run dev"
Write-Host "4. Open: http://localhost:3000"
Write-Host ""
