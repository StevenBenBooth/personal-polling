import os
import pickle
import subprocess

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
REL_VENV_PATH = os.path.join(".venv", "Scripts", "Activate.ps1")


def register_task(filename, dt, taskname):
    # TODO: Come up with a less messy approach than this
    # Ensures the task name is unique

    # why broken?
    pickle_path = os.path.join("cache", "unique_int.pk")
    with open(pickle_path, "rb") as f:
        i = pickle.load(f)
    with open(pickle_path, "wb") as f:
        pickle.dump(i + 1, f)

    task_trigger = (
        f"New-ScheduledTaskTrigger -Once -At {dt.replace(microsecond=0).isoformat()}"
    )
    task_action = rf"New-ScheduledTaskAction -Execute \"PowerShell\" -Argument \"{REL_VENV_PATH}; python {filename};\""
    # TODO: find some way to fix this so that it can be run as a localservice rather than SYSTEM (which is awful big)
    principal = r"New-ScheduledTaskPrincipal -UserID \"NT AUTHORITY\SYSTEM\" -LogonType ServiceAccount -RunLevel Highest"
    settings = r"New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries"

    ps_command = rf'$taskPrincipal = {principal}; $taskSettings={settings}; $taskTrigger = {task_trigger}; $taskAction = {task_action} -WorkingDirectory \"{BASE_PATH}\"; Register-ScheduledTask \"{taskname + " " + str(i)}\" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Principal $taskPrincipal -TaskPath \"PersonalPolling\";'

    with open("cache/log.txt", "a") as f:
        f.write(
            rf"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe {ps_command}"
        )
        f.write("\n")

    subprocess.call(
        rf"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe {ps_command}"
    )
