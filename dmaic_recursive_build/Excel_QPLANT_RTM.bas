Option Explicit
Sub RTM_InsertAndRenumber(Optional ByVal insertAt As Long = 0)
    Dim ws As Worksheet: Set ws = Sheets("RTM_Traceability")
    Dim lastRow As Long: lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    If insertAt <= 1 Or insertAt > lastRow + 1 Then insertAt = lastRow + 1
    ws.Rows(insertAt).Insert
    Dim i As Long
    For i = 2 To ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
        ws.Cells(i, 1).Value = i - 1
    Next i
    MsgBox "Inserted at row " & insertAt & " and renumbered.", vbInformation
End Sub

Sub RTM_CheckMeasurability()
    Dim ws As Worksheet: Set ws = Sheets("RTM_Traceability")
    Dim lastRow As Long: lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    Dim i As Long
    For i = 2 To lastRow
        If Trim(ws.Cells(i, 4).Value) = "" Then
            ws.Cells(i, 5).Value = "❌ Missing Measurability"
        Else
            ws.Cells(i, 5).Value = "✔ OK"
        End If
    Next i
    MsgBox "Measurability check complete.", vbInformation
End Sub
