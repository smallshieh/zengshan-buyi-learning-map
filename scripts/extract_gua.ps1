param (
    [Parameter(Mandatory = $true)]
    [string]$Text
)

# 強制設定 PowerShell 輸出的編碼為 UTF-8，解決文言文亂碼問題
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 確保路徑正確 (基於腳本位置或當前目錄)
$PromptPath = Join-Path $PSScriptRoot "..\" | Join-Path -ChildPath "prompts\extract_case.md"
if (-not (Test-Path $PromptPath)) {
    $PromptPath = "prompts\extract_case.md" # Fallback to relative
}

if (-not (Test-Path $PromptPath)) {
    Write-Error "找不到提示詞檔案: $PromptPath"
    return
}

# 讀取系統提示詞
$SystemPrompt = Get-Content $PromptPath -Raw -Encoding UTF8

# 組合最終 Prompt：把目標文本放在一個明確的英文區塊中，避免轉碼損毀
$FullPrompt = "$SystemPrompt`n`n--- TARGET TEXT TO EXTRACT ---`n$Text"
$EscapedPrompt = $FullPrompt.Replace('"', '\"')

# 呼叫 codex exec
codex exec "$EscapedPrompt"
