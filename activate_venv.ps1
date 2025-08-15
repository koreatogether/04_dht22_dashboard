# DHT22 프로젝트 가상환경 활성화 PowerShell 스크립트
# PowerShell 실행 정책 문제를 해결하고 안전하게 가상환경을 활성화합니다

Write-Host "[INFO] DHT22 프로젝트 가상환경 활성화 중..." -ForegroundColor Cyan

# 현재 디렉토리가 프로젝트 루트인지 확인
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] 가상환경을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "[INFO] 현재 위치: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "[INFO] .venv 디렉토리가 있는 프로젝트 루트에서 실행해주세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# PowerShell 실행 정책 확인 및 임시 변경
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "[INFO] 현재 실행 정책: $currentPolicy" -ForegroundColor Yellow

if ($currentPolicy -eq "Restricted") {
    Write-Host "[INFO] 실행 정책을 임시로 변경합니다..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "[SUCCESS] 실행 정책이 RemoteSigned로 변경되었습니다." -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] 실행 정책 변경에 실패했습니다: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "[TIP] 관리자 권한으로 PowerShell을 실행하거나 activate_venv.bat 파일을 사용하세요." -ForegroundColor Yellow
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
}

# 가상환경 활성화
try {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "[SUCCESS] 가상환경이 활성화되었습니다!" -ForegroundColor Green

    # Python 버전 확인
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python 버전: $pythonVersion" -ForegroundColor Cyan

    # 설치된 패키지 목록 (주요 패키지만)
    Write-Host "[INFO] 주요 설치 패키지:" -ForegroundColor Cyan
    pip list --format=columns | Select-String -Pattern "(fastapi|uvicorn|ruff|black|mypy|pytest)"

}
catch {
    Write-Host "[ERROR] 가상환경 활성화에 실패했습니다: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[TIP] activate_venv.bat 파일을 대신 사용해보세요." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[TIP] 가상환경을 비활성화하려면 'deactivate' 명령을 입력하세요." -ForegroundColor Yellow
Write-Host "[TIP] 프로젝트 작업을 시작할 준비가 완료되었습니다!" -ForegroundColor Green
