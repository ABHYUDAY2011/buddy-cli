Write-Host "Installing Buddy CLI..." -ForegroundColor Cyan

# 1. Folder Setup
$buddyDir = "$HOME\.buddy"
if (!(Test-Path $buddyDir)) { New-Item -ItemType Directory -Path $buddyDir }

# 2. BUILD THE RAW URL (Corrected to avoid HTML error)
$base = "https://raw.githubusercontent.com"
$path = "/ABHYUDAY2011/buddy-cli/main/buddy.py"
$finalUrl = $base + $path

# 3. DOWNLOAD THE REAL PYTHON CODE
Write-Host "Downloading Buddy code from GitHub..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $finalUrl -OutFile "$buddyDir\buddy.py"

# 4. Create the 'buddy' command
$profilePath = if ($PROFILE.CurrentUserAllHosts) { $PROFILE.CurrentUserAllHosts } else { $PROFILE }
if (!(Test-Path $profilePath)) { New-Item -Type File -Path $profilePath -Force }

$aliasFunc = "`nfunction buddy { python `"$buddyDir\buddy.py`" `$args }`n"
if ((Get-Content $profilePath) -notcontains "function buddy") {
    Add-Content -Path $profilePath -Value $aliasFunc
}

Write-Host "[✓] Buddy is installed! Restart PowerShell and type 'buddy'." -ForegroundColor Green



