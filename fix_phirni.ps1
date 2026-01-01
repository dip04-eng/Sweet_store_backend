# Fix Phirni to be a Festival Sweet
$body = @{
    sweetName = "Phirni"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/admin/fix-festival-sweets" -Method POST -Body $body -ContentType "application/json"
