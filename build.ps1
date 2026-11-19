Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TwitchTTS Windows Exe Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Checking dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

Write-Host ""
Write-Host "[2/3] Building standalone TwitchTTS.exe..." -ForegroundColor Yellow
pyinstaller --clean TwitchTTS.spec

Write-Host ""
if (Test-Path "dist\TwitchTTS.exe") {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "   Location: dist\TwitchTTS.exe" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Build failed. Please inspect the PyInstaller output above." -ForegroundColor Red
}
