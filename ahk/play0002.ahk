#Requires AutoHotkey v2.0

; play0002.ahk: 分母2("1/2")-> 4("1/4")のレシピ
; MacroRecorder.ahkで記録した実際のキー入力タイミングをそのまま再生する。
; 決定論仮説(同じタイミング再現->同じ結果)のため、記録された待ち時間(Sleep)は削らずに残すこと。

try {
    SetTitleMatchMode(2)

    tt := "L8192 ahk_class UnrealWindow"
    WinWait(tt)
    if (!WinActive(tt))
        WinActivate(tt)

    Sleep(300)

    ; MacroRecorderはWキー押しっぱなしをOSのキーリピートで46回のタップとして記録していたため、
    ; タップ連打ではなく「押しっぱなし」として再生する(46回 x 約30ms ≒ 1380ms相当)。
    SendEvent("{w down}")
    Sleep(60 * 30)
    SendEvent("{w up}")

    ; 同様にDキーも84回分のタップ相当を押しっぱなしに変換(84回 x 約30ms ≒ 2520ms相当)。
    SendEvent("{d down}")
    Sleep(120 * 30)
    SendEvent("{d up}")

    try FileAppend("DONE`n", "*")
} catch as err {
    try FileAppend("ERROR:" err.Message "`n", "*")
}

ExitApp()

F1::ExitApp()
