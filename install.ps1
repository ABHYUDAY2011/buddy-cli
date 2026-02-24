Write-Host "Installing Buddy CLI..." -ForegroundColor Cyan
$buddyDir = "$HOME\.buddy"
if (!(Test-Path $buddyDir)) { New-Item -ItemType Directory -Path $buddyDir }

# CRITICAL: Build the full Raw URL to bypass HTML download
$rawUrl = "https://raw.githubusercontent.com"
Invoke-WebRequest -Uri $rawUrl -OutFile "$buddyDir\buddy.py"

# Setup global 'buddy' command
$profilePath = if ($PROFILE.CurrentUserAllHosts) { $PROFILE.CurrentUserAllHosts } else { $PROFILE }
if (!(Test-Path $profilePath)) { New-Item -Type File -Path $profilePath -Force }
$aliasFunc = "`nfunction buddy { python `"$buddyDir\buddy.py`" `$args }`n"
if ((Get-Content $profilePath) -notcontains "function buddy") { Add-Content -Path $profilePath -Value $aliasFunc }

Write-Host "[✓] Buddy installed successfully! Restart PowerShell and type 'buddy'." -ForegroundColor Green

