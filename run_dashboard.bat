@echo off
REM Cross-platform batch script for building and running the artista-dashboard Docker image

REM 1. Clean previous Docker builds (optional)
echo Cleaning previous Docker builds...
docker system prune -f

REM 2. Build the Docker image
echo Building Docker image...
docker build -f docker/Dockerfile.ml-api -t artista-dashboard:latest .

REM 3. Verify the image was created
echo Listing artista-dashboard images...
docker images | findstr artista-dashboard

REM 4. Run the container (port 8080 mapped to 80 in the container)
echo Running the dashboard container...
docker run -p 8080:80 -e DASHBOARD_ADMIN_PASS=Bac2317 --name artista-dashboard-test artista-dashboard:latest

REM 5. Instructions
echo.
echo Accede a http://localhost:8080 en tu navegador para ver el dashboard interactivo.
echo Para detener el contenedor: docker stop artista-dashboard-test
