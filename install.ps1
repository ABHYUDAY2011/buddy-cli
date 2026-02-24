# 1. Clear out the broken file
$buddyPath = "$HOME\.buddy\buddy.py"
if (Test-Path $buddyPath) { Remove-Item $buddyPath -Force }

# 2. THE CORRECT FULL URL (CRITICAL: Do not cut this short)
$rawUrl = "https://raw.githubusercontent.com"

Write-Host "Downloading Buddy from ABHYUDAY2011 repository..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $rawUrl -OutFile $buddyPath

# 3. VERIFY
if (Test-Path $buddyPath) {
    $firstLine = Get-Content $buddyPath -TotalCount 1
    if ($firstLine -like "*import*") {
        Write-Host "[✓] SUCCESS! Real Python code installed." -ForegroundColor Green
        Write-Host "Type 'buddy' to start!" -ForegroundColor White
    } else {
        Write-Host "[X] ERROR: Still downloaded HTML. Ensure the full URL is copied." -ForegroundColor Red
    }
}
