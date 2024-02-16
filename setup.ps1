$taskTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Thursday -At 8pm

$taskAction = New-ScheduledTaskAction -Execute "Powershell" -Argument "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force .venv/Scripts/Activate.ps1; python scheduler.py;"
-WorkingDirectory $PSScriptRoot

Register-ScheduledTask 'Generate Polling Events' -Action $taskAction -Trigger $taskTrigger -TaskPath "PersonalPolling"