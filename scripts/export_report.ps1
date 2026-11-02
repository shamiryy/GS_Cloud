$ErrorActionPreference='Stop'
$project=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $project
& "$project/.venv/Scripts/python.exe" scripts/build_report.py
if($LASTEXITCODE){throw 'Falha ao preparar relatório'}
& "$project/.venv/Scripts/python.exe" scripts/prepare_figures.py
if($LASTEXITCODE){throw 'Falha ao preparar figuras'}
$sizes=Get-Content .private/image-sizes.json | ConvertFrom-Json
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
try {
 $doc=$word.Documents.Open("$project\.private\relatorio-final.html")
 $doc.PageSetup.PaperSize=7
 $doc.PageSetup.TopMargin=56.7
 $doc.PageSetup.BottomMargin=56.7
 $doc.PageSetup.LeftMargin=56.7
 $doc.PageSetup.RightMargin=56.7
 $doc.Content.Font.Name='Arial'
 $doc.Content.Font.Color=0
 $i=0
 foreach($shape in $doc.InlineShapes){
  $ratio=$sizes[$i].height/$sizes[$i].width
  $width=475
  if($width*$ratio -gt 590){$width=590/$ratio}
  $shape.LockAspectRatio=0
  $shape.Width=[single]$width
  $shape.Height=[single]($width*$ratio)
  $i++
 }
 foreach($table in $doc.Tables){
  $table.AllowAutoFit=$false
  $table.PreferredWidthType=3
  $table.PreferredWidthType=3
  $table.PreferredWidth=481
  if($table.Columns.Count -eq 2){$table.Columns.Item(1).Width=145;$table.Columns.Item(2).Width=336}else{$table.Columns.Item(1).Width=155;$table.Columns.Item(2).Width=80;$table.Columns.Item(3).Width=246}
  $table.Rows.AllowBreakAcrossPages=0
  $table.Rows.Item(1).HeadingFormat=-1
  $table.Rows.Item(1).Shading.BackgroundPatternColor=15132390
 }
 foreach($shape in $doc.InlineShapes){try{$shape.LinkFormat.SavePictureWithDocument=$true;$shape.LinkFormat.BreakLink()}catch{}}
 foreach($shape in $doc.InlineShapes){try{$shape.LinkFormat.SavePictureWithDocument=$true;$shape.LinkFormat.BreakLink()}catch{}}
 foreach($p in $doc.Paragraphs){if($p.Range.Text.StartsWith('15 Requisitos')){$p.Format.PageBreakBefore=-1}}
 $doc.RemoveDocumentInformation(99)
 $doc.SaveAs2("$project\docs\relatorio-academico.docx",16)
 $doc.ExportAsFixedFormat("$project\docs\relatorio-academico.pdf",17)
 Write-Output ('Paginas: '+$doc.ComputeStatistics(2))
 $doc.Close(0)
} finally {if($doc){try{$doc.Close(0)}catch{}};$word.Quit()}
& "$project/.venv/Scripts/python.exe" -c "import pymupdf;from pathlib import Path;Path('qa').mkdir(exist_ok=True);d=pymupdf.open('docs/relatorio-academico.pdf');print('PDF',len(d));[(p.get_pixmap().save(f'qa/final-{i+1}.png')) for i,p in enumerate(d)]"


