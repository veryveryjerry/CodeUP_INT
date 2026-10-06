# PowerShell setup script for RepoGuard AI
# Run: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  REPOGUARD AI - Setup Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Check prerequisites
Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow

# Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js not found. Install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "  Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Git not found. Install Git" -ForegroundColor Red
    exit 1
}

# Ollama
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "  Ollama: Available" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Ollama not found. Install from https://ollama.ai" -ForegroundColor Yellow
}

# Create directories
Write-Host ""
Write-Host "[2/8] Creating directories..." -ForegroundColor Yellow
$dirs = @("workspace", "data", "demo")
foreach ($dir in $dirs) {
    $path = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "  Created: $dir/" -ForegroundColor Green
    }
}

# Setup environment file
Write-Host ""
Write-Host "[3/8] Setting up environment..." -ForegroundColor Yellow
$envFile = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "  Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host "  .env already exists, skipping" -ForegroundColor Gray
}

# Setup Python virtual environment
Write-Host ""
Write-Host "[4/8] Setting up Python virtual environment..." -ForegroundColor Yellow
$backendDir = Join-Path $ProjectRoot "backend"
$venvDir = Join-Path $backendDir "venv"

if (-not (Test-Path $venvDir)) {
    Push-Location $backendDir
    python -m venv venv
    Pop-Location
    Write-Host "  Created virtual environment" -ForegroundColor Green
} else {
    Write-Host "  Virtual environment already exists" -ForegroundColor Gray
}

# Install Python dependencies
Write-Host ""
Write-Host "[5/8] Installing Python dependencies..." -ForegroundColor Yellow
$pipExe = Join-Path $venvDir "Scripts\pip.exe"
$requirements = Join-Path $backendDir "requirements.txt"
& $pipExe install -r $requirements --quiet
Write-Host "  Python dependencies installed" -ForegroundColor Green

# Install Node.js dependencies
Write-Host ""
Write-Host "[6/8] Installing Node.js dependencies..." -ForegroundColor Yellow
$frontendDir = Join-Path $ProjectRoot "frontend"
Push-Location $frontendDir
npm install --silent 2>&1 | Out-Null
Pop-Location
Write-Host "  Node.js dependencies installed" -ForegroundColor Green

# Pull Ollama model
Write-Host ""
Write-Host "[7/8] Pulling Ollama model..." -ForegroundColor Yellow
try {
    Write-Host "  Pulling qwen2.5-coder:7b (this may take a while)..." -ForegroundColor Gray
    ollama pull qwen2.5-coder:7b
    Write-Host "  Model pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Could not pull model. Ensure Ollama is running." -ForegroundColor Yellow
}

# Initialize database
Write-Host ""
Write-Host "[8/8] Initializing database..." -ForegroundColor Yellow
$pythonExe = Join-Path $venvDir "Scripts\python.exe"
Push-Location $backendDir
& $pythonExe -c "from app.database import init_db; import asyncio; asyncio.run(init_db())" 2>&1 | Out-Null
Pop-Location
Write-Host "  Database initialized" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "    cd backend" -ForegroundColor Gray
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "    python -m uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "    cd frontend" -ForegroundColor Gray
Write-Host "    npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  Open: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
