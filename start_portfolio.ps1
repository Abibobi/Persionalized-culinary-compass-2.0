param (
    [switch]$SkipTests = $false,
    [switch]$UseDocker = $false
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🚀 Personalized Culinary Compass 2.0 - Portfolio Demo" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if ($UseDocker) {
    Write-Host "`n[1/3] 🐳 Starting Docker Database Services..." -ForegroundColor Yellow
    docker-compose up -d db redis
    
    Write-Host "`n[2/3] 🔄 Running Migrations & Seeding Data in Docker..." -ForegroundColor Yellow
    docker-compose run --rm web python manage.py migrate
    docker-compose run --rm web python manage.py import_recipes pccrecipes.csv
    docker-compose run --rm web python manage.py seed_demo_users
    
    Write-Host "`n[3/3] 🚀 Starting Full Application Stack..." -ForegroundColor Yellow
    docker-compose up
    exit
}

Write-Host "`n[1/5] 🔍 Checking Environment..." -ForegroundColor Yellow
# Ensure we run using the correct conda environment if present
$condaEnv = "pcc"

if (-not $SkipTests) {
    Write-Host "`n[2/5] 🧪 Running Full Project Test Suite..." -ForegroundColor Yellow
    conda run -n $condaEnv python manage.py test tests.test_full_project
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests failed. Please fix issues before running the demo." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ All tests passed successfully." -ForegroundColor Green
} else {
    Write-Host "`n[2/5] ⏩ Skipping Tests..." -ForegroundColor Yellow
}

Write-Host "`n[3/5] 🔄 Applying Database Migrations..." -ForegroundColor Yellow
conda run -n $condaEnv python manage.py makemigrations
conda run -n $condaEnv python manage.py migrate

Write-Host "`n[4/5] 🌱 Seeding High-Quality Portfolio Data..." -ForegroundColor Yellow
Write-Host "Importing improved recipes..."
conda run -n $condaEnv python manage.py import_recipes pccrecipes.csv
Write-Host "Seeding demo users (Vegan, Diabetic, Athlete)..."
conda run -n $condaEnv python manage.py seed_demo_users
Write-Host "✅ Database is fully seeded with portfolio data." -ForegroundColor Green

Write-Host "`n[5/5] 🚀 Starting the Application Servers..." -ForegroundColor Yellow
Write-Host "Starting Django Backend Server on port 8000..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "conda" -ArgumentList "run -n $condaEnv python manage.py runserver"

Write-Host "Starting Next.js Frontend Server on port 3000..." -ForegroundColor Cyan
Set-Location -Path "frontend"
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev"

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " 🎉 Application is starting in the background!" -ForegroundColor Green
Write-Host " Backend API: http://localhost:8000" -ForegroundColor White
Write-Host " Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host " Demo Credentials: testuser / password123" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
