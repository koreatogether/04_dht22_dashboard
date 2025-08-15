# PowerShell 프로필 설정 스크립트
# 이 스크립트는 PowerShell 시작 시 자동으로 환경을 설정합니다

Write-Host "Setting up PowerShell profile for pre-commit..." -ForegroundColor Green

# PowerShell 프로필 경로 확인
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path $profilePath -Parent

# 프로필 디렉토리가 없으면 생성
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force
    Write-Host "Created profile directory: $profileDir" -ForegroundColor Yellow
}

# 프로필 내용 작성
$profileContent = @"
# DHT22 프로젝트 환경 설정
# Git Bash 경로 추가
`$env:PATH += ";C:\Program Files\Git\bin"

# Python Scripts 경로 추가
`$env:PATH += ";C:\Users\h\AppData\Roaming\Python\Python313\Scripts"

# Pre-commit bash 경로 설정
`$env:PRE_COMMIT_BASH = "C:\Program Files\Git\bin\bash.exe"

Write-Host "DHT22 development environment loaded" -ForegroundColor Green
"@

# 프로필 파일에 내용 추가 (기존 내용 보존)
if (Test-Path $profilePath) {
    $existingContent = Get-Content $profilePath -Raw
    if ($existingContent -notlike "*DHT22 프로젝트 환경 설정*") {
        Add-Content -Path $profilePath -Value "`n$profileContent"
        Write-Host "Added DHT22 environment to existing profile" -ForegroundColor Green
    } else {
        Write-Host "DHT22 environment already configured in profile" -ForegroundColor Yellow
    }
} else {
    Set-Content -Path $profilePath -Value $profileContent
    Write-Host "Created new PowerShell profile with DHT22 environment" -ForegroundColor Green
}

Write-Host "Profile path: $profilePath" -ForegroundColor Cyan
Write-Host "Please restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
