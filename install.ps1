Write-Host "Installing Buddy CLI..." -ForegroundColor Cyan
$buddyDir = "$HOME\.buddy"
if (!(Test-Path $buddyDir)) { New-Item -ItemType Directory -Path $buddyDir }

# CRITICAL FIX: The direct link to your raw python code
$rawUrl = "https://raw.githubusercontent.com"
Invoke-WebRequest -Uri $rawUrl -OutFile "$buddyDir\buddy.py"

# Setup the global command
$profilePath = if ($PROFILE.CurrentUserAllHosts) { $PROFILE.CurrentUserAllHosts } else { $PROFILE }
if (!(Test-Path $profilePath)) { New-Item -Type File -Path $profilePath -Force }
$aliasFunc = "`nfunction buddy { python `"$buddyDir\buddy.py`" `$args }`n"
if ((Get-Content $profilePath) -notcontains "function buddy") { Add-Content -Path $profilePath -Value $aliasFunc }

Write-Host "[✓] Buddy installed successfully! Restart PowerShell and type 'buddy'." -ForegroundColor Green

