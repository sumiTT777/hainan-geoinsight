$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
try {
  if (!(Test-Path '.venv\Scripts\python.exe')) {
    python --version
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11+ from python.org and enable PATH.' }
    python -m venv .venv
  }
  & .venv\Scripts\python.exe -m pip --version 2>$null
  if ($LASTEXITCODE -ne 0) { & .venv\Scripts\python.exe -m ensurepip }
  & .venv\Scripts\python.exe -m pip install -r requirements-lock.txt
  if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check network and Python version.' }
  & .venv\Scripts\python.exe -m streamlit run app.py
} catch { Write-Host $_ -ForegroundColor Red; Read-Host 'Press Enter to close'; exit 1 }

