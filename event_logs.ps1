# Ensure Logs directory exists
$logPath = "C:\Logs"
if (!(Test-Path $logPath)) {
    New-Item -ItemType Directory -Path $logPath
}

# Export system event logs to CSV
Get-WinEvent -LogName System -MaxEvents 100 | Export-Csv -Path C:\EventTrackAi\event_logs.csv -NoTypeInformation -Encoding UTF8

# Get-WinEvent -LogName -MaxEvents 100 'Windows PowerShell', 'Setup' |
#   Group-Object -Property LevelDisplayName, LogName -NoElement | Format-Table -AutoSize
