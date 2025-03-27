# Start-Sleep -Seconds 2
# Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} | Format-Table TimeCreated, Message | Format-Table -AutoSize | Export-Csv -Path C:\EventTrackAI\events_4625.csv -NoTypeInformation
# Get-WinEvent -FilterHashtable @{ LogName="Security"; ID=4625 } | Select-Object TimeCreated, Message | Format-Table -AutoSize | Export-Csv -Path C:\EventTrackAI\events_4625.csv -NoTypeInformation
# $events = Get-WinEvent -FilterHashtable @{ LogName="Security"; ID=4625 } | Select-Object TimeCreated, Message
# Get-WinEvent -LogName System -MaxEvents 100 | Export-Csv -Path C:\EventTrackAi\events_4625.csv -NoTypeInformation -Encoding UTF8
# Get-EventLog -LogName Security | Where-Object { $_.EventID -eq 4625 } | Select-Object TimeGenerated, Message | Export-Csv -Path "C:\EventTrackAI\events_4625.csv" 

# Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} | 
# Select-Object TimeCreated, Message | 
# Export-Csv -Path C:\EventTrackAI\events_4625.csv -NoTypeInformation -Encoding UTF8

Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} | 
Select-Object TimeCreated, @{Name="Message";Expression={$_.Message -replace "`r`n"," "}} | 
Export-Csv -Path C:\EventTrackAI\events_4625.csv -NoTypeInformation -Encoding UTF8
