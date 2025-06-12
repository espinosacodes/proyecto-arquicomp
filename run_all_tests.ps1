# Matrix sizes to test - only remaining size
$matrixSizes = @(1672)
$samples = 10
$versions = @('A', 'B', 'C', 'D', 'E', 'F')

# Create results directory if it doesn't exist
$resultsDir = "results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir
}

# Function to run Python tests
function Run-PythonTests {
    Write-Host "Running Python tests..."
    foreach ($n in $matrixSizes) {
        Write-Host "Running tests for matrix size $n..."
        $output = python matrixProduct_Six_versions_python.py $n $samples
        
        # Process output and distribute to appropriate files
        $output | ForEach-Object {
            $line = $_
            if ($line -match "Py_ver\(([A-F])\).*?(double|float)") {
                $ver = $matches[1]
                $type = $matches[2]
                $filePath = Join-Path $resultsDir "Py_ver_${ver}_${type}.txt"
                
                # Create file with header if it doesn't exist
                if (-not (Test-Path $filePath)) {
                    "ver`ttypeData`tISA`t#sample`tn`ttime(s)`tNormalized(ns)" | Out-File -FilePath $filePath
                }
                
                $line | Out-File -FilePath $filePath -Append
            }
        }
        Write-Host "Completed tests for matrix size $n"
    }
}

# Main execution
Write-Host "Starting Python tests for remaining matrix sizes..."
Write-Host "This may take a while, please be patient..."

Run-PythonTests

Write-Host "All tests completed. Results have been appended to existing files in the 'results' directory." 