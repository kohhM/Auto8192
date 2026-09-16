#Requires AutoHotkey v2.0

; play0004.ahk: 分母4("1/4")-> 8("1/8")のレシピ
; VS Codeのローカル履歴から復元した実際の記録データに基づく(キー列: d,w,a,s,d,w,a)。
; MacroRecorderはキー押しっぱなしをOSのキーリピートで連続タップとして記録するため、
; play0002.ahkと同様に「押しっぱなし」形式に変換している。保持時間はタップ数からの推定値(仮値)。
; debug_play.py play0004.ahk で実行しながら各Sleep値を調整すること。

try {
    SetTitleMatchMode(2)

    tt := "L8192 ahk_class UnrealWindow"
    WinWait(tt)
    if (!WinActive(tt))
        WinActivate(tt)

    Sleep(300)

    ; d x1
    SendEvent("{d down}")
    Sleep(20 * 30)
    SendEvent("{d up}")
    Sleep(150)

    ; w x1
    SendEvent("{w down}")
    Sleep(100 * 30)
    SendEvent("{w up}")
    Sleep(150)

    ; s x3
    SendEvent("{s down}")
    Sleep(100 * 30)
    SendEvent("{s up}")
    Sleep(150)

    ; w x3
    SendEvent("{w down}")
    Sleep(80 * 30)
    SendEvent("{w up}")
    Sleep(150)


    try FileAppend("DONE`n", "*")
} catch as err {
    try FileAppend("ERROR:" err.Message "`n", "*")
}

ExitApp()

F1::ExitApp()
