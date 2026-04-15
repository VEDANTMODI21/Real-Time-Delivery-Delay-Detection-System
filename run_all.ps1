# Start the infrastructure (Redis, Postgres)
Write-Host "Updating infrastructure with Docker Compose... (Using Redis)" -ForegroundColor Cyan
docker-compose up -d

Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -s 10

# Open 4 terminals for the 4 components
Write-Host "Launching system components..." -ForegroundColor Green

# 1. Backend 
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn main:app --reload --port 8000" -WindowStyle Normal

# 2. Consumer
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python consumer/consumer.py" -WindowStyle Normal

# 3. Producer
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python producer/producer.py" -WindowStyle Normal

# 4. Dashboard
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run dashboard/app.py" -WindowStyle Normal

Write-Host "All components launched! Check the new windows." -ForegroundColor Cyan
