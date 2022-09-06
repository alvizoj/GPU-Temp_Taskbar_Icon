Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "PATH_TO_BAT_FILE" & Chr(34), 0
'Example: WshShell.Run chr(34) & "C:\Users\Jessica\Desktop\GPU_Temp\launch_GPU_Temp.bat" & Chr(34), 0
Set WshShell = Nothing
