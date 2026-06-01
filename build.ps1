# PowerShell Build Script for Markdown Opener

Write-Host "=== Building Markdown Opener ===" -ForegroundColor Cyan

# Step 1: Build frontend
Write-Host "`nStep 1: Building frontend with Vite..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Frontend build successful!" -ForegroundColor Green

# Step 2: Build Tauri app
Write-Host "`nStep 2: Building Tauri application..." -ForegroundColor Yellow
node node_modules/@tauri-apps/cli/tauri.js build --no-bundle

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "Executable location: src-tauri/target/release/markdown-opener.exe" -ForegroundColor Green
