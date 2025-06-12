<#
.SYNOPSIS
Script to automate the execution of a 4-factor matrix multiplication experiment.

.DESCRIPTION
This script generates a full factorial design for a matrix multiplication experiment
with factors Algorithm, Matrix Size (N), Data Type, and Language. It includes
10 repetitions per combination and randomizes the execution order. It then
executes the specified C++, Python, and Java programs/scripts with the
corresponding parameters, captures the execution time, and logs the results
to a CSV file.

.NOTES
Author: Your Name/Group Name
Date: May 17, 2025 (or current date)
Version: 1.0

Requires:
- PowerShell 5.1 or higher
- Compiled C++ executables, Python script, Java classes or JAR file that accept
  command-line arguments for Algorithm, N, Repetition, and Data Type, and
  output only the execution time to standard output.
#>

# Requires -Version 5.1 # Uncomment if you want to enforce a minimum PowerShell version

# --- Configuration ---
# Define the levels for each factor
$Algorithms = @('a', 'b', 'c', 'd', 'e', 'f')
# >>> IMPORTANT: Replace these with YOUR calculated matrix sizes based on cache <<<
# You need at least 12 levels. Example values are provided below.
$MatrixSizes = @(64, 128, 256, 512, 1024, 1500, 2048, 3000, 4096, 5000, 6000, 8192, 10000)
$DataTypes = @('float', 'double')
$Languages = @('C++', 'Python', 'Java')
$RepetitionsPerCombination = 10

# --- Paths to your executables/scripts ---
# >>> IMPORTANT: UPDATE THESE PATHS <<<
# Example: Assume C++ generates two exes, one for float and one for double
$CppExeDir = ".\cpp_build" # Directory containing your C++ executables
$PythonScriptPath = ".\python\matrix_mult.py" # Full path to your Python script
# Example: Assume Java compiled classes are in 'java_classes' directory, and the main class is 'MatrixMultiplierMain'
$JavaClassPath = ".\java_classes" # Directory containing your Java compiled classes
$JavaMainClass = "MatrixMultiplierMain" # The name of the main class to execute

# --- Output File ---
$OutputCsvPath = ".\experiment_results.csv" # Path for the output CSV file

# --- Script Logic ---

Write-Host "Generating experimental design matrix..."

$DesignMatrix = @()
$OrderStandardCounter = 1

# Generate all unique combinations
foreach ($alg in $Algorithms) {
    foreach ($n in $MatrixSizes) {
        foreach ($dataType in $DataTypes) {
            foreach ($lang in $Languages) {
                # Add repetitions for this unique combination
                for ($rep = 1; $rep -le $RepetitionsPerCombination; $rep++) {
                    $run = [PSCustomObject]@{
                        'Order Standard' = $OrderStandardCounter
                        'Algoritmo'      = $alg
                        'Tamaño N'       = $n
                        'Tipo Dato'      = $dataType
                        'Lenguaje'       = $lang
                        'Repeticion'     = $rep
                        'Order Ejecucion'= 0 # Placeholder, will be filled after randomization
                        'Tiempo (ms)'    = $null # Placeholder for measured time
                        'Status'         = 'Pending' # Execution status
                    }
                    $DesignMatrix += $run
                }
                # Increment standard order only after all repetitions for a unique comb.
                # Wait, the standard order is per UNIQUE combination, not per run including repetitions.
                # Let's correct this. The standard order should be for the 6*N*2*3 combinations.
            }
        }
    }
}

# Correcting Order Standard counter logic - it should be per unique combo (Alg, N, Type, Lang)
$DesignMatrix = @()
$UniqueCombinationCounter = 1

foreach ($alg in $Algorithms) {
    foreach ($n in $MatrixSizes) {
        foreach ($dataType in $DataTypes) {
            foreach ($lang in $Languages) {
                for ($rep = 1; $rep -le $RepetitionsPerCombination; $rep++) {
                     $run = [PSCustomObject]@{
                        'Order Standard UniqueCombo' = $UniqueCombinationCounter # Let's clarify this column name
                        'Algoritmo'                  = $alg
                        'Tamaño N'                   = $n
                        'Tipo Dato'                  = $dataType
                        'Lenguaje'                   = $lang
                        'Repeticion'                 = $rep
                        'Order Ejecucion'            = 0 # Placeholder
                        'Tiempo (ms)'                = $null # Placeholder
                        'Status'                     = 'Pending' # Status
                    }
                    $DesignMatrix += $run
                }
                $UniqueCombinationCounter++ # Increment after adding all reps for a unique combo
            }
        }
    }
}


Write-Host "Randomizing execution order..."

# Randomize the design matrix
$RandomizedDesignMatrix = $DesignMatrix | Get-Random -Count $DesignMatrix.Count

# Assign the execution order
for ($i = 0; $i -lt $RandomizedDesignMatrix.Count; $i++) {
    $RandomizedDesignMatrix[$i].'Order Ejecucion' = $i + 1
}

Write-Host "Generated $(($Algorithms.Count * $MatrixSizes.Count * $DataTypes.Count * $Languages.Count * $RepetitionsPerCombination)) total runs."
Write-Host "Starting experiment execution..."

$results = @()
$totalRuns = $RandomizedDesignMatrix.Count
$currentRun = 0

# Execute each run in the randomized order
foreach ($run in $RandomizedDesignMatrix) {
    $currentRun++
    $alg = $run.Algoritmo
    $n = $run.'Tamaño N'
    $dataType = $run.'Tipo Dato'
    $lang = $run.Lenguaje
    $rep = $run.Repeticion
    $orderExec = $run.'Order Ejecucion'

    Write-Progress -Activity "Running Experiment" -Status "Executing run $currentRun of $totalRuns (Order Ejecucion: $orderExec)" -PercentComplete (($currentRun / $totalRuns) * 100)

    $command = ""
    $arguments = @()
    $executionSuccessful = $false
    $measuredTime = $null
    $status = "Error" # Default status

    try {
        switch ($lang) {
            'C++' {
                # Assumes C++ executables are named like cpp_float.exe, cpp_double.exe
                # And accept parameters: Algorithm N Repetition DataType
                $command = Join-Path -Path $CppExeDir -ChildPath "cpp_$($dataType).exe"
                # >>> Check/Adjust C++ arguments based on your implementation <<<
                # Assuming parameters are passed as: <Algorithm> <N> <Repetition>
                # DataType might be implicit in the executable name, but pass it anyway if your C++ code reads it.
                $arguments = @($alg, $n.ToString(), $rep.ToString(), $dataType) # Pass N and Repetition as strings
            }
            'Python' {
                # Assumes your Python script is executed with 'python <script_path>'
                # And accepts parameters: Algorithm N Repetition DataType
                $command = "python"
                # >>> Check/Adjust Python arguments based on your implementation <<<
                # Assuming parameters are passed as: <script_path> <Algorithm> <N> <Repetition> <DataType>
                $arguments = @($PythonScriptPath, $alg, $n.ToString(), $rep.ToString(), $dataType) # Pass N and Repetition as strings
            }
            'Java' {
                # Assumes your Java code is executed via '-cp <classpath> <main_class>' or '-jar <jar_path>'
                # And accepts parameters: Algorithm N Repetition DataType
                $command = "java"
                # >>> Check/Adjust Java arguments based on your implementation <<<
                # Example using classpath: java -cp <classpath> <main_class> <Algorithm> <N> <Repetition> <DataType>
                $arguments = @('-cp', $JavaClassPath, $JavaMainClass, $alg, $n.ToString(), $rep.ToString(), $dataType) # Pass N and Repetition as strings
                # Example using jar (if you build a runnable jar):
                # $command = "java"
                # $arguments = @('-jar', $JavaJarPath, $alg, $n.ToString(), $rep.ToString(), $dataType)
            }
            default {
                throw "Unknown language specified: $lang"
            }
        }

        # --- Execute the command and capture output ---
        # Use the call operator '&' to execute and capture stdout
        # Add redirection of stderr to stdout or null if you don't want to capture errors in $output
        $executionOutput = & $command $arguments 2>&1 # Redirect stderr to stdout

        # Parse the output - Assumes only the time (a number) is printed to stdout
        # You might need to adjust this parsing based on your program's exact output format
        $measuredTime = [double]$executionOutput | Where-Object { $_ -is [double] }

        if ($measuredTime -ne $null) {
            $executionSuccessful = $true
            $status = "Completed"
        } else {
             $status = "Output Error" # Program ran but output wasn't a number
             Write-Warning "Run failed to output a valid number for time: $command $arguments"
             Write-Warning "Output was: $executionOutput"
        }

    } catch {
        $status = "Execution Error" # Program failed to run or threw an exception
        Write-Error "Error executing command for run $orderExec ($lang, Alg:$alg, N:$n, Type:$dataType, Rep:$rep): $($_.Exception.Message)"
        $measuredTime = -1 # Indicate error with a specific value
    }

    # Create a result object for this run
    $resultRow = [PSCustomObject]@{
        'Order Standard UniqueCombo' = $run.'Order Standard UniqueCombo'
        'Algoritmo'                  = $alg
        'Tamaño N'                   = $n
        'Tipo Dato'                  = $dataType
        'Lenguaje'                   = $lang
        'Repeticion'                 = $rep
        'Order Ejecucion'            = $orderExec
        'Tiempo (ms)'                = $measuredTime # Store the captured time (in ms as per column name)
        'Status'                     = $status
        'CommandExecuted'            = "$command $arguments" # Log the full command for debugging
        'OutputRaw'                  = $executionOutput # Log raw output in case of errors
    }

    $results += $resultRow
}

Write-Host "Experiment execution finished."

# --- Save Results to CSV ---
Write-Host "Saving results to $($OutputCsvPath)..."

# Check if the directory exists, create if not
$outputDir = Split-Path -Path $OutputCsvPath -Parent
if (-not (Test-Path -Path $outputDir -PathType Container)) {
    New-Item -Path $outputDir -ItemType Directory | Out-Null
}

# Export results. Use -NoTypeInformation to keep the CSV clean.
$results | Export-Csv -Path $OutputCsvPath -NoTypeInformation -Delimiter "," # Use comma delimiter

Write-Host "Results saved successfully."
Write-Host "Total runs: $($results.Count)"
$errorRuns = $results | Where-Object { $_.Status -ne 'Completed' }
Write-Host "Runs with errors or output issues: $($errorRuns.Count)"
if ($errorRuns.Count -gt 0) {
    Write-Host "Check the 'Status' column and 'CommandExecuted'/'OutputRaw' for details on failed runs."
}
