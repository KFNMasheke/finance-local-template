param([string]$RepoName = 'finance-local-template')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Install Git first: https://git-scm.com/download/win' }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'Install GitHub CLI first: https://cli.github.com/' }
$html = Get-Content 'index.html' -Raw
$match = [regex]::Match($html, 'id="seed">([\s\S]*?)</script>')
if (-not $match.Success) { throw 'Cannot verify blank app seed. Publication stopped.' }
$seed = $match.Groups[1].Value | ConvertFrom-Json
foreach ($field in @('transactions','income','budgets','debts','audits','evidence','imports')) {
    if (@($seed.$field).Count -gt 0) { throw "Personal data found in $field. Use the clean template ZIP, not the private app." }
}
$allowed = @('index.html','app.js','core.js','style.css','server.py','analyse.py','Start-Finance.bat','Install-PDF-Support.bat','README.md','LICENSE','requirements-pdf.txt','test_core.js','test_views.js','test_server.py','Publish-GitHub.ps1','.gitignore','.github')
Get-ChildItem -Force | Where-Object { $_.Name -notin ($allowed + @('.git')) } | ForEach-Object { throw "Unexpected file $($_.Name). Use a fresh clean template folder." }
$owner = gh api user --jq '.login'
if ($LASTEXITCODE -ne 0) { throw 'Authenticate first: gh auth login' }
if (-not (Test-Path '.git')) { git init -b main; if ($LASTEXITCODE -ne 0) { throw 'Git initialization failed' } }
$remotes = @(git remote)
if ($remotes -contains 'origin') { throw 'This folder already has an origin. Publication stopped to avoid publishing to the wrong repository.' }
git add --all
if ($LASTEXITCODE -ne 0) { throw 'Git staging failed' }
git diff --cached --quiet
if ($LASTEXITCODE -eq 1) {
    git -c user.name='Finance Local contributors' -c user.email='noreply@localhost' commit -m 'Initial blank local finance app template'
    if ($LASTEXITCODE -ne 0) { throw 'Git commit failed' }
}
gh repo create "$owner/$RepoName" --public --source . --remote origin --push --description 'Free local-first budgeting, debt plans, statement reconciliation and South African tax scenarios. Blank reusable app template.'
if ($LASTEXITCODE -ne 0) { throw 'GitHub repository creation or push failed. Inspect the remote and GitHub before retrying; do not create a duplicate.' }
gh api --method PATCH "repos/$owner/$RepoName" -F is_template=true
if ($LASTEXITCODE -ne 0) { throw 'Repository was created, but enabling the template flag failed. Enable Template repository in GitHub Settings.' }
Write-Host "Template ready: https://github.com/$owner/$RepoName"
