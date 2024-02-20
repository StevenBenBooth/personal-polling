# NOTE: you need to add "Local service" to the permissions list for the proper folder
# see: https://stackoverflow.com/questions/45641880/workaround-for-access-is-denied-for-localservice
$taskTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek "Sunday" -At 1:05am
$taskAction = New-ScheduledTaskAction -Execute "PowerShell" -Argument ".venv\Scripts\Activate.ps1; python scheduler.py" -WorkingDirectory $PSScriptRoot 
# LocalService would be better but doesn't have the required permissions
$taskPrincipal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask 'Generate Polling Events' -Settings $taskSettings -Principal $taskPrincipal -Action $taskAction -Trigger $taskTrigger -TaskPath "PersonalPolling"
