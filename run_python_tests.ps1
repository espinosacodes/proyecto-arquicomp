# Matrix sizes to test
$matrixSizes = @(91, 128, 157, 181, 200, 256, 362, 400, 512, 836, 1182, 1672)
$samples = 5

# Delete previous results file if it exists
if (Test-Path results_python.txt) { Remove-Item results_python.txt }

# Rename the output file in the Python script
(Get-Content matrixProduct_Six_versions_python.py) -replace 'ReportS2_LHW00.txt', 'results_python.txt' | Set-Content matrixProduct_Six_versions_python.py

# Run Python version for all matrix sizes
Write-Host "Running Python tests for all matrix sizes..."
foreach ($size in $matrixSizes) {
    Write-Host "`nTesting matrix size: $size"
    python matrixProduct_Six_versions_python.py $size $samples
}

Write-Host "`nAll tests completed! Results are saved in results_python.txt" 