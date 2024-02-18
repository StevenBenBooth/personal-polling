$taskTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek "Sunday" -At 1:05am
$taskAction = New-ScheduledTaskAction -Execute "PowerShell" -Argument '.venv\Scripts\Activate.ps1; python scheduler.py' -WorkingDirectory $PSScriptRoot 
Register-ScheduledTask 'Generate Polling Events' -Action $taskAction -Trigger $taskTrigger -TaskPath "PersonalPolling"
