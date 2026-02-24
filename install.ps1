
Write-Host "Installing Buddy CLI..." -ForegroundColor Cyan
$buddyDir = "$HOME\.buddy"
if (!(Test-Path $buddyDir)) { New-Item -ItemType Directory -Path $buddyDir }

# THIS IS THE CRITICAL FIX: The full RAW URL to your python code
$rawUrl = "https://raw.githubusercontent.com"
Invoke-WebRequest -Uri $rawUrl -OutFile "$buddyDir\buddy.py"

# Setup the global command (User Profile)
$profilePath = if ($PROFILE.CurrentUserAllHosts) { $PROFILE.CurrentUserAllHosts } else { $PROFILE }
if (!(Test-Path $profilePath)) { New-Item -Type File -Path $profilePath -Force }

$aliasFunc = "`nfunction buddy { python `"$buddyDir\buddy.py`" `$args }`n"
$currentProfile = Get-Content $profilePath
if ($currentProfile -notcontains "function buddy") {
    Add-Content -Path $profilePath -Value $aliasFunc
}
Write-Host "[✓] Installation complete! Restart PowerShell." -ForegroundColor Green

