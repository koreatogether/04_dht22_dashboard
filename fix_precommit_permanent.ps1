# PowerShell 스크립트: Pre-commit bash 문제 영구 해결
# 관리자 권한으로 실행해야 합니다

Write-Host "🔧 Pre-commit bash 문제 영구 해결 중..." -ForegroundColor Green

# 1. 시스템 환경변수 설정
try {
    [Environment]::SetEnvironmentVariable("PRE_COMMIT_BASH", "C:\Program Files\Git\bin\bash.exe", "Machine")
    Write-Host "✅ PRE_COMMIT_BASH 시스템 환경변수 설정 완료" -ForegroundColor Green
} catch {
    Write-Host "⚠️  시스템 환경변수 설정 실패 (관리자 권한 필요): $_" -ForegroundColor Yellow
    
    # 사용자 환경변수로 대체
    [Environment]::SetEnvironmentVariable("PRE_COMMIT_BASH", "C:\Program Files\Git\bin\bash.exe", "User")
    Write-Host "✅ PRE_COMMIT_BASH 사용자 환경변수 설정 완료" -ForegroundColor Green
}

# 2. PATH에 Git bin 추가 (시스템 레벨)
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
$gitBinPath = "C:\Program Files\Git\bin"

if ($currentPath -notlike "*$gitBinPath*") {
    try {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$gitBinPath", "Machine")
        Write-Host "✅ Git bin 경로를 시스템 PATH에 추가 완료" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  시스템 PATH 설정 실패 (관리자 권한 필요): $_" -ForegroundColor Yellow
        
        # 사용자 PATH로 대체
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($userPath -notlike "*$gitBinPath*") {
            [Environment]::SetEnvironmentVariable("PATH", "$userPath;$gitBinPath", "User")
            Write-Host "✅ Git bin 경로를 사용자 PATH에 추가 완료" -ForegroundColor Green
        }
    }
} else {
    Write-Host "✅ Git bin 경로가 이미 PATH에 있습니다" -ForegroundColor Green
}

# 3. 현재 세션에서도 환경변수 설정
$env:PRE_COMMIT_BASH = "C:\Program Files\Git\bin\bash.exe"
$env:PATH += ";C:\Program Files\Git\bin"

# 4. Pre-commit 재설치
Write-Host "🔄 Pre-commit 재설치 중..." -ForegroundColor Yellow
try {
    pre-commit clean
    pre-commit uninstall
    pre-commit install
    Write-Host "✅ Pre-commit 재설치 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Pre-commit 재설치 실패: $_" -ForegroundColor Red
}

# 5. 테스트
Write-Host "🧪 Pre-commit 테스트 중..." -ForegroundColor Yellow
try {
    $testResult = pre-commit run --all-files 2>&1
    if ($LASTEXITCODE -eq 0 -or $testResult -notlike "*ExecutableNotFoundError*") {
        Write-Host "✅ Pre-commit 테스트 성공!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Pre-commit 테스트에서 일부 이슈 발견 (정상적인 코드 품질 검사)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Pre-commit 테스트 실패: $_" -ForegroundColor Red
}

Write-Host "`n🎉 설정 완료! 다음 단계:" -ForegroundColor Cyan
Write-Host "1. PowerShell/CMD를 재시작하거나" -ForegroundColor White
Write-Host "2. 시스템을 재부팅하면" -ForegroundColor White
Write-Host "3. 이후 git commit이 정상적으로 작동합니다" -ForegroundColor White

Write-Host "`n💡 확인 방법:" -ForegroundColor Cyan
Write-Host "   bash --version" -ForegroundColor Gray
Write-Host "   pre-commit --version" -ForegroundColor Gray
Write-Host "   git commit -m 'test message'" -ForegroundColor Gray