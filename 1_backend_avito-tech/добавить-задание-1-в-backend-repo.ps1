# Запускать ПОСЛЕ того как:
# 1. Клонирован backend-repo и запушена ветка new-main с одним README
# 2. На GitHub new-main сделана default, старый main удалён, new-main переименован в main
# 3. Локально: cd backend-repo; git fetch; git checkout main; git pull

$backendRepo = "C:\Users\yulia\Desktop\backend-repo"
$avitoSource = "C:\Users\yulia\Desktop\1_backend_avito-tech"
$targetFolder = Join-Path $backendRepo "1_backend_avito-tech"

if (-not (Test-Path $backendRepo)) {
    Write-Host "Сначала выполни в Git Bash: cd /c/Users/yulia/Desktop; git clone https://github.com/ka1icc/backend.git backend-repo"
    exit 1
}

# Создать папку задания
New-Item -ItemType Directory -Force -Path $targetFolder | Out-Null

# Копировать только нужные файлы (без __pycache__, .db, .idea)
robocopy $avitoSource $targetFolder /E /XD __pycache__ .idea .venv /XF *.db *.pyc uv.lock /NFL /NDL /NJH /NJS
if ($LASTEXITCODE -ge 8) { exit $LASTEXITCODE }

Write-Host "Файлы скопированы в $targetFolder"
Write-Host "Дальше в Git Bash:"
Write-Host "  cd /c/Users/yulia/Desktop/backend-repo"
Write-Host "  git checkout -b 1-avito"
Write-Host "  git add 1_backend_avito-tech"
Write-Host "  git commit -m \"Задание 1: Avito-tech URL Shortener\""
Write-Host "  git push -u origin 1-avito"
