param(
    [Parameter(Mandatory=$true)][string]$Owner,
    [Parameter(Mandatory=$true)][string]$Repo,
    [Parameter(Mandatory=$true)][string]$Path,
    [string]$Branch
)

if (-not $Branch) {
    $Branch = (& git rev-parse --abbrev-ref HEAD).Trim()
}

try {
    git add -A
    git commit -m "Prepare notebook for Colab" -ErrorAction Stop
} catch {
    Write-Host "No changes to commit or commit failed: $_"
}

git push origin $Branch

$url = "https://colab.research.google.com/github/$Owner/$Repo/blob/$Branch/$Path"
Write-Host "Opening: $url"
Start-Process $url
