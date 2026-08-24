# PITCH Build & Packaging Script

Write-Host "[1/2] Building PyInstaller package (onedir)..." -ForegroundColor Cyan
pyinstaller -y Pitch.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "[Error] PyInstaller build failed." -ForegroundColor Red
    exit 1
}

Write-Host "[2/2] Checking for Inno Setup Compiler (ISCC.exe)..." -ForegroundColor Cyan
$isccPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)

$isccPath = $isccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($isccPath) {
    Write-Host "[2/2] Compiling Inno Setup installer..." -ForegroundColor Green
    & $isccPath installer.iss
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[Success] PITCH installer built in dist/PITCH_Setup_v1.54.exe!" -ForegroundColor Green
    }
} else {
    Write-Host "`n[Info] PyInstaller build complete in 'dist/PITCH/' folder." -ForegroundColor Yellow
    Write-Host "[Info] Install Inno Setup 6 (https://jrsoftware.org/isdl.php) to automatically generate PITCH_Setup.exe installer." -ForegroundColor Yellow
}
