Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' Uruchomienie skryptu start_background.bat w 100% ukrytym procesie (okno = 0)
cmdLine = "%comspec% /c """ & currentDir & "\start_background.bat"""
WshShell.Run cmdLine, 0, False
