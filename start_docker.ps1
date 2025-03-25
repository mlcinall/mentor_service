# Start Docker Desktop (if it's installed)
try {
    $dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopPath) {
        Write-Host "Starting Docker Desktop..."
        Start-Process -FilePath $dockerDesktopPath
        Write-Host "Waiting for Docker to start (30 seconds)..."
        Start-Sleep -Seconds 30
    } else {
        Write-Host "Docker Desktop not found at default location. Please start Docker Desktop manually."
        exit 1
    }
} catch {
    Write-Host "Failed to start Docker Desktop: $_"
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker is not running. Please start Docker Desktop manually and try again."
        exit 1
    }
    Write-Host "Docker is running."
} catch {
    Write-Host "Docker is not running or not installed. Please make sure Docker Desktop is running."
    exit 1
}

# Start the application with Docker Compose
Write-Host "Starting the application with Docker Compose..."
docker-compose down -v
docker-compose build
docker-compose up 