Write-Host "Installing Buddy CLI..." -ForegroundColor Cyan

# 1. Ensure Folder exists
$buddyDir = "$HOME\.buddy"
if (!(Test-Path $buddyDir)) { New-Item -ItemType Directory -Path $buddyDir }

# 2. BUILD THE RAW URL (Corrected)
$base = "https://raw.githubusercontent.com"
$repo = "/ABHYUDAY2011/buddy-cli/main/buddy.py"
$finalUrl = $base + $repo

# 3. DOWNLOAD THE ACTUAL CODE
Write-Host "Downloading Buddy code from GitHub..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $finalUrl -OutFile "$buddyDir\buddy.py" -ErrorAction Stop

# 4. Set up the command
$profilePath = if ($PROFILE.CurrentUserAllHosts) { $PROFILE.CurrentUserAllHosts } else { $PROFILE }
if (!(Test-Path $profilePath)) { New-Item -Type File -Path $profilePath -Force }

$aliasFunc = "`nfunction buddy { python `"$buddyDir\buddy.py`" `$args }`n"
if ((Get-Content $profilePath) -notcontains "function buddy") {
    Add-Content -Path $profilePath -Value $aliasFunc
}

Write-Host "[✓] Buddy installed successfully! Restart PowerShell and type 'buddy'." -ForegroundColor Green
