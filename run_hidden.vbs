' Script khoi chay Antigravity Remote Bot co Widget goc man hinh an terminal 100%
Set FSO = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

ScriptPath = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ScriptPath

' Chay an CMD window (0 = SW_HIDE) va khoi tao Floating Widget
WshShell.Run "cmd /c python main.py", 0, False
