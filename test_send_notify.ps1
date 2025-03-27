$botToken = "7688031766:AAHdy2pFPEqXCYaV0LyvCL5FiKKHRr-sRNU"
$chatID = "728491010"

function Send-TelegramMessage($message) {
    $url = "https://api.telegram.org/bot$botToken/sendMessage"
    $body = @{ chat_id = $chatID; text = $message } | ConvertTo-Json -Compress
    Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body $body
}
Send-TelegramMessage "hello world"
# $events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 1
# $lastEvent = $events | Select-Object -First 1
# if ($lastEvent) {
#     $ip = ($lastEvent.Message -match 'Source Network Address:\s+(\S+)' | Out-Null; $matches[1])
#     Send-TelegramMessage "Обнаружена попытка взлома с IP: $ip"
# }
