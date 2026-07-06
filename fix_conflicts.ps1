$file = 'frontend/src/pages/Index.js'
$content = Get-Content $file -Raw

# Supprimer les marqueurs de conflit en gardant la version de main (=======  à >>>>>>> main)
$pattern = '(?s)<<<<<<< HEAD.*?=======\s*(.*?)>>>>>>> main'
$cleaned = [regex]::Replace($content, $pattern, { param($m) $m.Groups[1].Value })

Set-Content $file $cleaned -Encoding UTF8
Write-Host 'Fichier nettoyé'
