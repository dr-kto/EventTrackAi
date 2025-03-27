$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} | 
    ForEach-Object {
        $message = $_.Message -replace "`r`n", " "
        $ip = "N/A"
        $port = "N/A"

        if ($message -match "Сетевой адрес источника:\s+([\d\.:]+)") {
            $ip = $matches[1]
        }
        
        if ($message -match "Порт источника:\s+(\d+)") {
            $port = $matches[1]
        }

        [PSCustomObject]@{
            TimeCreated = $_.TimeCreated
            IPAddress = $ip
            SourcePort = $port
            Message = $message
        }
    } | ConvertTo-Json -Depth 3

$LogFile = "C:\EventTrackAI\events_4625.json"
$Events | Out-File $LogFile -Encoding utf8

Write-Host "Логи сохранены в $LogFile"
