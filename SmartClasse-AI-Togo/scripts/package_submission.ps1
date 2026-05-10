param()

$rootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& "$rootDir\venv\Scripts\python.exe" "$rootDir\scripts\package_submission.py"