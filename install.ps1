Write-Host "Installing Buddy CLI..." -ForegroundColor Cyan

# 1. Create the hidden folder if it doesn't exist
$buddyDir = "$HOME\.buddy"
if (!(Test-Path $buddyDir)) { New-Item -ItemType Directory -Path $buddyDir }

# 2. DOWNLOAD the actual python file from your GitHub (CRITICAL STEP)
# Use your RAW URL here:
$rawUrl = "https://raw.githubusercontent.com"
Invoke-WebRequest -Uri $rawUrl -OutFile "$buddyDir\buddy.py"

# 3. Register global command in PowerShell Profile
$profilePath = if ($PROFILE.CurrentUserAllHosts) { $PROFILE.CurrentUserAllHosts } else { $PROFILE }
if (!(Test-Path $profilePath)) { New-Item -Type File -Path $profilePath -Force }

$aliasFunc = "`nfunction buddy { python `"$buddyDir\buddy.py`" `$args }`n"
if ((Get-Content $profilePath) -notcontains "function buddy") {
    Add-Content -Path $profilePath -Value $aliasFunc
}

Write-Host "[✓] Command 'buddy' is now active." -ForegroundColor Green
Write-Host "Restart PowerShell and type 'buddy' to start." -ForegroundColor White
