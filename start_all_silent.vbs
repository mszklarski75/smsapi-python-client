Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' 1. Uruchom aplikacje Flask w tle (cichy tryb bez czarnego okna)
WshShell.Run "pythonw.exe launcher.pyw", 0, False

' 2. Poczekaj 2 sekundy na uruchomienie serwera Flask na porcie 5000
WScript.Sleep 2000

' 3. Sprawdz czy istnieje plik ze stala domena ngrok_domain.txt
ngrokCmd = "ngrok.exe http 5000"
If fso.FileExists(currentDir & "\ngrok_domain.txt") Then
    Set domainFile = fso.OpenTextFile(currentDir & "\ngrok_domain.txt", 1)
    If Not domainFile.AtEndOfStream Then
        domainVal = Trim(domainFile.ReadLine())
        If Len(domainVal) > 0 Then
            ngrokCmd = "ngrok.exe http --domain=" & domainVal & " 5000"
        End If
    End If
    domainFile.Close
End If

' 4. Uruchom tunel ngrok w ukrytym oknie w tle
If fso.FileExists(currentDir & "\ngrok.exe") Then
    WshShell.Run ngrokCmd, 0, False
End If
