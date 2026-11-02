$ErrorActionPreference='Stop'
$project=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $project
& "$project/.venv/Scripts/python.exe" scripts/build_report.py
if($LASTEXITCODE){throw 'Falha ao preparar relatorio'}
& "$project/.venv/Scripts/python.exe" scripts/prepare_figures.py
if($LASTEXITCODE){throw 'Falha ao preparar figuras'}
$sizes=Get-Content .private/image-sizes.json | ConvertFrom-Json
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
try{
 $doc=$word.Documents.Open("$project\.private\relatorio-final.html")
 $doc.PageSetup.PaperSize=7
 $doc.PageSetup.TopMargin=56.7
 $doc.PageSetup.BottomMargin=56.7
 $doc.PageSetup.LeftMargin=56.7
 $doc.PageSetup.RightMargin=56.7
 $doc.Content.Font.Name='Arial'
 $doc.Content.Font.Color=0
 $first=$doc.Paragraphs.Item(1)
 $first.Range.Style=-63
 $first.Range.Font.Name='Arial'
 $first.Range.Font.Size=18
 $first.Range.Font.Color=0
 $first.Range.Font.Bold=-1
 $first.Format.Alignment=1
 $first.Borders.Enable=0
 $i=0
 foreach($shape in $doc.InlineShapes){
  $ratio=$sizes[$i].height/$sizes[$i].width
  $width=475
  if($width*$ratio -gt 540){$width=540/$ratio}
  $shape.LockAspectRatio=0
  $shape.Width=[single]$width
  $shape.Height=[single]($width*$ratio)
  $shape.Range.ParagraphFormat.KeepWithNext=-1
  try{$shape.LinkFormat.SavePictureWithDocument=$true;$shape.LinkFormat.BreakLink()}catch{}
  $i++
 }
 foreach($table in $doc.Tables){
  $table.AllowAutoFit=$false
  $table.PreferredWidthType=3
  $table.PreferredWidth=481
  $count=$table.Columns.Count
  if($count -eq 4){$widths=@(96,138,131,116);$table.Range.Font.Size=9}
  elseif($count -eq 3){$widths=@(125,135,221);if($table.Cell(1,1).Range.Text.StartsWith('Requisito')){$widths=@(155,80,246)}}
  else{$widths=@(145,336)}
  for($c=1;$c -le $count;$c++){$table.Columns.Item($c).Width=[single]$widths[$c-1]}
  $table.Rows.AllowBreakAcrossPages=0
  $table.Rows.Item(1).HeadingFormat=-1
  $table.Rows.Item(1).Shading.BackgroundPatternColor=15132390
 }
 $doc.RemoveDocumentInformation(99)
 $doc.SaveAs2("$project\docs\relatorio-academico.docx",16)
 $doc.ExportAsFixedFormat("$project\docs\relatorio-academico.pdf",17)
 Write-Output ('Paginas: '+$doc.ComputeStatistics(2))
 $doc.Close(0)
}finally{if($doc){try{$doc.Close(0)}catch{}};$word.Quit()}
& "$project/.venv/Scripts/python.exe" -c "import pymupdf;from pathlib import Path;Path('qa').mkdir(exist_ok=True);d=pymupdf.open('docs/relatorio-academico.pdf');print('PDF',len(d));[(p.get_pixmap().save(f'qa/final-{i+1}.png')) for i,p in enumerate(d)]"
