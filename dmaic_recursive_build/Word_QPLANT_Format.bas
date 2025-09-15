Sub QPLANT_ApplyStylesAndNumbering()
    ' Set up multilevel list for headings 1..3
    Dim ml As ListTemplate
    Set ml = ListGalleries(wdOutlineNumberGallery).ListTemplates(1)
    With ml.ListLevels(1)
        .NumberFormat = "%1."
        .NumberStyle = wdListNumberStyleArabic
        .LinkedStyle = "Heading 1"
    End With
    With ml.ListLevels(2)
        .NumberFormat = "%1.%2."
        .NumberStyle = wdListNumberStyleArabic
        .LinkedStyle = "Heading 2"
    End With
    With ml.ListLevels(3)
        .NumberFormat = "%1.%2.%3"
        .NumberStyle = wdListNumberStyleArabic
        .LinkedStyle = "Heading 3"
    End With

    Dim p As Paragraph
    For Each p In ActiveDocument.Paragraphs
        If p.Range.Text Like "#.*" Then p.Range.Style = "Heading 1"
        If p.Range.Text Like "#.#*" Then p.Range.Style = "Heading 2"
        If p.Range.Text Like "#.#.#*" Then p.Range.Style = "Heading 3"
    Next p

    Dim sel As Range
    Set sel = Selection.Range
    sel.ListFormat.ApplyListTemplate ListTemplate:=ListGalleries(wdNumberGallery).ListTemplates(3)
    Selection.Range.ListFormat.ListType = wdListSimpleNumbering
End Sub
