# Matrix sizes to test
$matrixSizes = @(91, 128, 157, 181, 200, 256, 362, 400, 512, 836, 1182, 1672)
$samples = 10

# Compile Java files
Write-Host "Compiling Java files..."
javac matrixProduct_Six_versions_java_float.java
javac matrixProduct_Six_versions_java_double.java

# Run float version
Write-Host "`nRunning float version..."
foreach ($size in $matrixSizes) {
    Write-Host "`nTesting matrix size: $size"
    java MatrixProductFloat $size $samples
}

# Run double version
Write-Host "`nRunning double version..."
foreach ($size in $matrixSizes) {
    Write-Host "`nTesting matrix size: $size"
    java MatrixProductDouble $size $samples
}

Write-Host "`nAll tests completed!" 