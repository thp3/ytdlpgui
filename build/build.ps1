param([string]$Version = "0.1.1")

# Builds dist\VideoDownloader, the installer and the portable zip.
# Needs: .venv with requirements installed, bin\ (ffmpeg), Inno Setup 6.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot)
$env:PYTHONUTF8 = "1"

function Run($exe, $argList) {
    & $exe @argList
    if ($LASTEXITCODE -ne 0) { throw "$exe failed with exit code $LASTEXITCODE" }
}

Run ".\.venv\Scripts\python.exe" @("-m", "pytest", "-q")
Run ".\.venv\Scripts\python.exe" @("-m", "PyInstaller", "build\ytdlpgui.spec", "--noconfirm", "--distpath", "dist", "--workpath", "build\work")

Copy-Item LICENSE, THIRD_PARTY_NOTICES.md "dist\VideoDownloader\" -Force

$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
Run $iscc @("/DAppVersion=$Version", "build\installer.iss")

$zip = "dist\VideoDownloader-$Version-portable-win64.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path "dist\VideoDownloader" -DestinationPath $zip -CompressionLevel Optimal

Get-ChildItem "dist\*$Version*" | Select-Object Name, @{n = "MB"; e = { [math]::Round($_.Length / 1MB) } }
