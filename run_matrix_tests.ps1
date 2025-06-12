# Matrix sizes to test
$matrixSizes = @(91, 128, 157, 181, 200, 256, 362, 400, 512, 836, 1182, 1672)
$samples = 5

# Delete previous results files if they exist
if (Test-Path results_float.txt) { Remove-Item results_float.txt }
if (Test-Path results_double.txt) { Remove-Item results_double.txt }

# Compile Java files
Write-Host "Compiling Java files..."
javac MatrixProductFloat.java
javac MatrixProductDouble.java

# Run float version for all matrix sizes
Write-Host "`nRunning float version..."
foreach ($size in $matrixSizes) {
    Write-Host "`nTesting matrix size: $size"
    java MatrixProductFloat $size $samples
}

# Run double version for all matrix sizes
Write-Host "`nRunning double version..."
foreach ($size in $matrixSizes) {
    Write-Host "`nTesting matrix size: $size"
    java MatrixProductDouble $size $samples
}

Write-Host "`nAll tests completed! Results are saved in results_float.txt and results_double.txt" 