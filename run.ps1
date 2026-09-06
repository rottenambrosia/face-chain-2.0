# FaceChain 2.0 Startup Script for PowerShell
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  FaceChain 2.0 — Biometric Web3 Provenance Pipeline   " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Resolve Python path
$PythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host ""
Write-Host "Starting FastAPI Backend on port 8000..." -ForegroundColor Green
$BackendJob = Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -PassThru

Start-Sleep -Seconds 2

Write-Host "Starting Streamlit Frontend on port 8501..." -ForegroundColor Green
$FrontendJob = Start-Process -FilePath $PythonExe -ArgumentList "-m streamlit run frontend/streamlit_app.py --server.port 8501" -PassThru

Write-Host ""
Write-Host "FaceChain 2.0 is running!" -ForegroundColor Cyan
Write-Host "• Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "• API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "• Health:   http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host ""
Write-Host "Both processes have been launched in background windows." -ForegroundColor Yellow
Write-Host "Close those windows or terminate the processes to stop."
