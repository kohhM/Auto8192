#Requires AutoHotkey v2.0

; play0002.ahk: 分母2("1/2")-> 4("1/4")のレシピ
; MacroRecorder.ahkで記録した実際のキー入力タイミングをそのまま再生する。
; 決定論仮説(同じタイミング再現->同じ結果)のため、記録された待ち時間(Sleep)は削らずに残すこと。

try {
    SetKeyDelay(30)
    SendMode("Event")
    SetTitleMatchMode(2)

    tt := "L8192 ahk_class UnrealWindow"
    WinWait(tt)
    if (!WinActive(tt))
        WinActivate(tt)

    ;Sleep(300)

    SendEvent("{a down}")
    Sleep(2300)
    SendEvent("{a up}")

    try FileAppend("DONE`n", "*")
} catch as err {
    try FileAppend("ERROR:" err.Message "`n", "*")
}

ExitApp()

F1::ExitApp()
