@echo off
REM Railway deploy automation script for Windows PowerShell
REM Set your Railway token here
set RAILWAY_TOKEN=359f26c1-d5f2-4254-9423-a38f0d6d1d2d

REM Deploy using the Dockerfile
railway up --dockerfile docker/Dockerfile.ml-api

REM Clean up the token (optional)
set RAILWAY_TOKEN=359f26c1-d5f2-4254-9423-a38f0d6d1d2d
