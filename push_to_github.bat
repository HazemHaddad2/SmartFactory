@echo off
echo ========================================
echo    Push vers GitHub
echo ========================================

echo.
echo INSTRUCTIONS:
echo 1. Créez un nouveau repository sur GitHub.com
echo 2. Copiez l'URL du repository (ex: https://github.com/username/SmartFactory-Monitor.git)
echo 3. Remplacez YOUR_GITHUB_URL ci-dessous par votre URL

echo.
set /p github_url="Entrez l'URL de votre repository GitHub: "

echo.
echo Ajout du remote GitHub...
git remote add origin %github_url%

echo.
echo Configuration de la branche principale...
git branch -M main

echo.
echo Push vers GitHub...
git push -u origin main

echo.
echo ========================================
echo ✅ Projet poussé vers GitHub avec succès !
echo ========================================
echo.
echo Votre projet est maintenant disponible sur:
echo %github_url%
echo.
pause