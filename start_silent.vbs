Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' Uruchomienie aplikacji w tle bez wyskakujacych okien
cmdLine = "%comspec% /c """ & currentDir & "\start_background.bat"""
WshShell.Run cmdLine, 0, False
