import pandas as pd
import os

# Read the Excel files
file_n10 = "tiempos de ejecucion ryzen 9 n=10.xlsx"
file_n5 = "tiempos de ejecucion ryzen 9 n=5.xlsx"

# Create Excel writer for the output file
output_file = "tiempos de ejecucion ryzen 9 n=15_combined.xlsx"

# Read both Excel files
excel_n10 = pd.ExcelFile(file_n10)
excel_n5 = pd.ExcelFile(file_n5)

# Normalize sheet names for matching (lowercase, strip spaces)
def normalize_sheet_name(name):
    return name.lower().replace(' ', '')

# Get normalized sheet names from both files
sheets_n10_norm = {normalize_sheet_name(sheet): sheet for sheet in excel_n10.sheet_names}
sheets_n5_norm = {normalize_sheet_name(sheet): sheet for sheet in excel_n5.sheet_names}

# Find common normalized sheets
common_sheets_norm = set(sheets_n10_norm.keys()) & set(sheets_n5_norm.keys())

if not common_sheets_norm:
    print("No matching sheets found between the two files!")
    exit(1)

print("Found matching sheets:")
for sheet_norm in common_sheets_norm:
    print(f"- {sheets_n10_norm[sheet_norm]} (from n=10) matches {sheets_n5_norm[sheet_norm]} (from n=5)")

# Define the desired order and pattern
languages = ['Cpp', 'Java', 'python']
types = ['float', 'double']
versions = ['a', 'b', 'c', 'd', 'e', 'f']
ordered_sheet_names = []
for t in types:
    for lang in languages:
        for v in versions:
            ordered_sheet_names.append(f"{lang} - {t} - ver({v})")

# Lowercase, no-space mapping for matching
ordered_sheet_names_norm = [normalize_sheet_name(s) for s in ordered_sheet_names]

# Only process sheets that match the pattern and exist in both files
filtered_common_sheets = [s for s in ordered_sheet_names_norm if s in common_sheets_norm]

processed_dfs = {}
for sheet_norm in filtered_common_sheets:
    sheet_n10 = sheets_n10_norm[sheet_norm]
    sheet_n5 = sheets_n5_norm[sheet_norm]
    print(f"\nProcessing sheet: {sheet_n10}")
    
    # Read data from both files for the current sheet
    df_n10 = pd.read_excel(file_n10, sheet_name=sheet_n10)
    df_n5 = pd.read_excel(file_n5, sheet_name=sheet_n5, header=None)
    
    # Remove empty columns from n=5
    df_n5 = df_n5.dropna(axis=1, how='all')
    
    # Get the headers from n=10
    headers = df_n10.columns.tolist()
    
    # Check if column counts match
    if len(df_n5.columns) != len(headers):
        print(f"Warning: Column count mismatch in sheet {sheet_n10}")
        print(f"n=10 has {len(headers)} columns: {headers}")
        print(f"n=5 has {len(df_n5.columns)} columns")
        
        # If n=5 has fewer columns, add empty columns to match
        if len(df_n5.columns) < len(headers):
            missing_cols = len(headers) - len(df_n5.columns)
            for i in range(missing_cols):
                df_n5[len(df_n5.columns)] = None
        # If n=5 has more columns, drop extra columns
        else:
            df_n5 = df_n5.iloc[:, :len(headers)]
    
    # Assign headers to n=5 data
    df_n5.columns = headers
    
    # Convert #sample column to numeric in both dataframes
    if '#sample' in df_n10.columns:
        df_n10['#sample'] = pd.to_numeric(df_n10['#sample'], errors='coerce')
    if '#sample' in df_n5.columns:
        df_n5['#sample'] = pd.to_numeric(df_n5['#sample'], errors='coerce')
    
    # For Cpp float versions, always combine n=10 samples 0-9 and n=5 samples 0-4 (relabelled as 10-14)
    if sheet_n10.startswith('Cpp - float - ver('):
        df_n10_0_9 = df_n10[df_n10['#sample'].isin(range(10))] if '#sample' in df_n10.columns else df_n10
        df_n5_0_4 = df_n5[df_n5['#sample'].isin(range(5))].copy() if '#sample' in df_n5.columns else pd.DataFrame(columns=df_n5.columns)
        if not df_n5_0_4.empty:
            df_n5_0_4['#sample'] = df_n5_0_4['#sample'] + 10
        df_combined = pd.concat([df_n10_0_9, df_n5_0_4], ignore_index=True)
    else:
        # Only keep samples 0-9 from n=10
        if '#sample' in df_n10.columns:
            df_n10 = df_n10[df_n10['#sample'].isin([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])]
        # Only keep samples 0-4 from n=5, then relabel as 10-14
        if '#sample' in df_n5.columns:
            df_n5 = df_n5[df_n5['#sample'].isin([0, 1, 2, 3, 4])].copy()
            df_n5['#sample'] = df_n5['#sample'] + 10
        df_combined = pd.concat([df_n10, df_n5], ignore_index=True)
    
    # Sort by n and #sample if these columns exist
    if 'n' in df_combined.columns and '#sample' in df_combined.columns:
        df_combined = df_combined.sort_values(['n', '#sample']).reset_index(drop=True)
        
        # Ensure we have all samples from 0 to 14
        expected_samples = list(range(15))  # 0 to 14
        if '#sample' in df_combined.columns:
            actual_samples = sorted(df_combined['#sample'].dropna().unique())
            missing_samples = set(expected_samples) - set(actual_samples)
            if missing_samples:
                print(f"Warning: Missing samples in sheet {sheet_n10}: {missing_samples}")
    
    # Store the processed dataframe
    processed_dfs[sheet_n10] = df_combined
    print(f"Sheet {sheet_n10} has {len(df_combined)} rows after blending.")
    print(f"Successfully processed sheet: {sheet_n10}")

if not processed_dfs:
    print("No data was processed successfully!")
    exit(1)

# Write all processed dataframes to the Excel file in the specified order
non_empty_sheets = []
for sheet_name in ordered_sheet_names:
    if sheet_name in processed_dfs:
        df = processed_dfs[sheet_name]
        if not df.empty:
            non_empty_sheets.append((sheet_name, df))
        else:
            print(f"Skipping empty sheet: {sheet_name}")

if not non_empty_sheets:
    print("No non-empty sheets to write! Output file will not be created.")
    exit(1)

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    for sheet_name, df in non_empty_sheets:
        print(f"Writing sheet: {sheet_name}")
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\nNew Excel file created: {output_file}")

# Verify the file was created and has content
if os.path.exists(output_file):
    file_size = os.path.getsize(output_file)
    print(f"File size: {file_size} bytes")
    if file_size == 0:
        print("Warning: The file was created but is empty!")
    else:
        print("File was created successfully with content.")
else:
    print("Error: File was not created!") 