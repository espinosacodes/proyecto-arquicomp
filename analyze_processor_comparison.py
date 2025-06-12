import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import os
import re

def load_and_process_data(file_path):
    """Load and process data from Excel file"""
    print(f"Processing file: {file_path}")
    version_info = []
    for sheet in pd.ExcelFile(file_path).sheet_names:
        # More flexible regex pattern that handles various formats
        match = re.match(r'(Codigo\s*C|Cpp|Java|python)[\s-]+(float|double)[\s-]+ver\(?([a-f])\)?', sheet, re.IGNORECASE)
        if match:
            lang = match.group(1).strip()
            # Normalize language names
            if lang.lower() == 'codigo c':
                lang = 'Cpp'
            dtype = match.group(2).strip().lower()
            version = match.group(3).strip().lower()
            version_info.append({
                'version': version,
                'language': lang,
                'data_type': dtype,
                'sheet_name': sheet
            })
        # Special case for Python combined sheet in tr5.xlsx
        elif 'python' in sheet.lower() and 'float & double' in sheet.lower():
            version_info.append({
                'version': None,  # Will be extracted from data
                'language': 'python',
                'data_type': 'float',
                'sheet_name': sheet
            })
            version_info.append({
                'version': None,  # Will be extracted from data
                'language': 'python',
                'data_type': 'double',
                'sheet_name': sheet
            })
        # Special case for Java combined sheets in tr5.xlsx
        elif 'java' in sheet.lower():
            version_info.append({
                'version': None,  # Will be extracted from data
                'language': 'java',
                'data_type': 'float' if 'float' in sheet.lower() else 'double',
                'sheet_name': sheet
            })
    
    # Combine data from all sheets
    all_data = []
    skipped_sheets = []
    for info in version_info:
        try:
            # Read Excel sheet
            df = pd.read_excel(file_path, sheet_name=info['sheet_name'])
            
            # Try to find the normalized time column
            possible_names = [
                'normalized(ns)', 'normalized_ns', 'normalized', 'normalized (ns)',
                'Normalized(ns)', 'Normalized_ns', 'Normalized', 'Normalized (ns)',
                'time(s)', 'time', 'Time(s)', 'Time'
            ]
            found_col = None
            for col in df.columns:
                col_clean = col.lower().replace(' ', '').replace('_', '')
                for name in possible_names:
                    name_clean = name.lower().replace(' ', '').replace('_', '')
                    if col_clean == name_clean:
                        found_col = col
                        break
                if found_col:
                    break
            if found_col is None:
                print(f"Could not find normalized time column in sheet {info['sheet_name']}. Columns found: {list(df.columns)}")
                skipped_sheets.append(info['sheet_name'])
                continue
            # Rename the found column
            df = df.rename(columns={found_col: 'Normalized_ns'})
            
            # Normalize other columns
            df = df.rename(columns={
                'ver': 'version',
                'Ver': 'version',
                'TypeData': 'data_type',
                'typedata': 'data_type',
                'version': 'version'
            })
            
            # Add metadata
            df['language'] = info['language']
            if 'data_type' not in df.columns:
                df['data_type'] = info['data_type']
            else:
                # If data_type is in the sheet, use it to filter
                df = df[df['data_type'].str.lower() == info['data_type'].lower()]
            
            # For Python in tr5.xlsx (combined sheet), use 'version' and 'data_type' columns directly
            if info['language'].lower() == 'python' and 'float & double' in info['sheet_name'].lower():
                if 'version' not in df.columns and 'Ver' in df.columns:
                    df = df.rename(columns={'Ver': 'version'})
                if 'data_type' not in df.columns and 'TypeData' in df.columns:
                    df = df.rename(columns={'TypeData': 'data_type'})
                df['version'] = df['version'].astype(str).str.lower().str.strip()
                df['data_type'] = df['data_type'].astype(str).str.lower().str.strip()
                # Filter for the correct data_type
                df = df[df['data_type'] == info['data_type']]
                # Only keep versions a-f
                df = df[df['version'].isin(['a', 'b', 'c', 'd', 'e', 'f'])]
            # For Java in tr5.xlsx, extract version from the 'version' column
            elif info['language'].lower() == 'java' and file_path.endswith('tr5.xlsx'):
                if 'version' not in df.columns and 'Ver' in df.columns:
                    df = df.rename(columns={'Ver': 'version'})
                df['version'] = df['version'].astype(str).str.lower().str.strip()
                # Only keep versions a-f
                df = df[df['version'].isin(['a', 'b', 'c', 'd', 'e', 'f'])]
            # For Java and Python in tr9.xlsx, extract version letter from the 'version' column
            elif info['language'].lower() in ['java', 'python']:
                if 'version' not in df.columns:
                    print(f"No 'version' column found in sheet {info['sheet_name']}. Columns found: {list(df.columns)}")
                    skipped_sheets.append(info['sheet_name'])
                    continue
                # Extract version from the version column (e.g., "Java_ver(A)" or "Py_ver(A)" -> "a")
                df['version'] = df['version'].astype(str).str.extract(r'[A-Za-z_]+\(([A-Fa-f])\)', expand=False)
                # Convert to lowercase and strip whitespace
                df['version'] = df['version'].str.lower().str.strip()
                # Filter out any rows where version extraction failed
                df = df.dropna(subset=['version'])
                # Only keep versions a-f
                df = df[df['version'].isin(['a', 'b', 'c', 'd', 'e', 'f'])]
            else:
                # For C/C++, use the version from the sheet name
                if info['version']:
                    df['version'] = info['version']
                elif 'version' in df.columns:
                    df['version'] = df['version'].astype(str).str.strip().str.lower()
            
            # Clean version column
            df['version'] = df['version'].astype(str).str.strip().str.lower()
            
            # Convert time columns to numeric
            if 'time' in df.columns:
                df['time'] = pd.to_numeric(df['time'].astype(str).str.replace(',', '.'), errors='coerce')
            if 'Normalized_ns' in df.columns:
                df['Normalized_ns'] = pd.to_numeric(df['Normalized_ns'].astype(str).str.replace(',', '.'), errors='coerce')
            
            # Drop rows with missing values
            df = df.dropna(subset=['Normalized_ns', 'version', 'language', 'data_type'])
            
            if not df.empty:
                all_data.append(df)
            else:
                print(f"No valid data found in sheet {info['sheet_name']}")
                skipped_sheets.append(info['sheet_name'])
                
        except Exception as e:
            print(f"Error processing sheet {info['sheet_name']}: {str(e)}. Columns found: {list(df.columns) if 'df' in locals() else 'N/A'}")
            skipped_sheets.append(info['sheet_name'])
            continue
    
    if not all_data:
        raise ValueError(f"No valid data found in any sheets of {file_path}")
    
    # Combine all data
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Print summary of processed data
    print("\nProcessed data summary:")
    print(f"Total rows: {len(final_df)}")
    print("\nVersions by language and data type:")
    print(final_df.groupby(['language', 'data_type'])['version'].value_counts())
    
    return final_df

def create_high_contrast_palette():
    # High contrast colors for processors
    return ['#FF0000', '#0000FF']  # Red for R5, Blue for R9

def plot_all_versions_comparison(r5_df, r9_df):
    """Create boxplots comparing all versions between R5 and R9"""
    # Create plots directory if it doesn't exist
    os.makedirs('plots', exist_ok=True)
    
    # Get unique combinations of language and data type
    languages = sorted(r5_df['language'].unique())
    data_types = sorted(r5_df['data_type'].unique())
    
    # Create a separate plot for each language and data type
    for lang in languages:
        for dtype in data_types:
            # Filter data for this language and data type
            r5_subset = r5_df[(r5_df['language'].str.lower() == lang.lower()) & 
                              (r5_df['data_type'].str.lower() == dtype.lower())]
            r9_subset = r9_df[(r9_df['language'].str.lower() == lang.lower()) & 
                              (r9_df['data_type'].str.lower() == dtype.lower())]
            
            if r5_subset.empty or r9_subset.empty:
                print(f"No data available for {lang} {dtype}")
                continue
            
            # Create figure
            plt.figure(figsize=(12, 6))
            
            # Create boxplot
            plot_df = pd.concat([
                r5_subset.assign(Processor='R5'),
                r9_subset.assign(Processor='R9')
            ])
            
            # Use high contrast colors
            sns.boxplot(x='version', y='Normalized_ns', hue='Processor', data=plot_df,
                       palette=['#1f77b4', '#ff7f0e'])
            
            plt.title(f'Performance Comparison - {lang} {dtype}')
            plt.xlabel('Algorithm Version')
            plt.ylabel('Normalized Time (ns)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save plot
            plt.savefig(f'plots/performance_comparison_{lang}_{dtype}.png')
            plt.close()
    
    # Create performance summary
    summary = []
    for lang in languages:
        for dtype in data_types:
            r5_subset = r5_df[(r5_df['language'].str.lower() == lang.lower()) & 
                              (r5_df['data_type'].str.lower() == dtype.lower())]
            r9_subset = r9_df[(r9_df['language'].str.lower() == lang.lower()) & 
                              (r9_df['data_type'].str.lower() == dtype.lower())]
            
            if not r5_subset.empty and not r9_subset.empty:
                r5_stats = r5_subset.groupby('version')['Normalized_ns'].agg(['mean', 'std', 'count']).reset_index()
                r9_stats = r9_subset.groupby('version')['Normalized_ns'].agg(['mean', 'std', 'count']).reset_index()
                
                for _, row in r5_stats.iterrows():
                    version = row['version']
                    r9_row = r9_stats[r9_stats['version'] == version]
                    if not r9_row.empty:
                        summary.append({
                            'Language': lang,
                            'Data Type': dtype,
                            'Version': version,
                            'R5 Mean': row['mean'],
                            'R5 Std': row['std'],
                            'R5 Count': row['count'],
                            'R9 Mean': r9_row['mean'].iloc[0],
                            'R9 Std': r9_row['std'].iloc[0],
                            'R9 Count': r9_row['count'].iloc[0]
                        })
    
    # Save summary to CSV
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv('plots/performance_summary.csv', index=False)
    print("Performance summary saved to plots/performance_summary.csv")

def print_insights(summary):
    print("\n==== Performance Insights ====")
    for lang, dtype, r5_mean, r9_mean, improvement in summary:
        print(f"\n{lang} {dtype}:")
        print(f"R5 5600X average: {r5_mean:.2f} ns")
        print(f"R9 5900X average: {r9_mean:.2f} ns")
        print(f"Performance improvement: {improvement:.2f}%")
    
    print("\n==== Value Analysis ====")
    avg_improvement = np.mean([imp for *_, imp in summary]) if summary else 0
    if avg_improvement > 10:
        print(f"\nThe R9 5900X shows significant performance gains:")
        print(f"- Average improvement: {avg_improvement:.1f}%")
        print("- Worth the upgrade if you need maximum performance and parallel processing")
        print("- Particularly beneficial for multi-threaded applications")
    elif avg_improvement > 0:
        print(f"\nThe R9 5900X shows modest performance gains:")
        print(f"- Average improvement: {avg_improvement:.1f}%")
        print("- R5 5600X offers better value for most users")
        print("- Consider R9 only if you need the extra cores for specific workloads")
    else:
        print("\nThe R9 5900X shows minimal performance gains in these workloads:")
        print("- No significant improvement in single-threaded performance")
        print("- R5 5600X is the better value choice")
        print("- Consider R9 only if you need the additional cores for other tasks")

def main():
    try:
        # Load data
        r5_data = load_and_process_data('data/tr5.xlsx')
        r9_data = load_and_process_data('data/tr9.xlsx')
        
        # Create comparison plots
        plot_all_versions_comparison(r5_data, r9_data)
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 