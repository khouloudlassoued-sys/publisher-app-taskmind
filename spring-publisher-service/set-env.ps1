$env:JWT_SECRET = "un-secret-de-developpement-local-au-moins-32-caracteres"
$env:POSTGRES_DB = "publisher_dev"
$env:POSTGRES_PORT = "5434"
Write-Host "Variables d'environnement definies : JWT_SECRET, POSTGRES_DB, POSTGRES_PORT" -ForegroundColor Green