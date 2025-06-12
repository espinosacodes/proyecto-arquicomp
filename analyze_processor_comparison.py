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
        # Special case for Python versions b to f in tr5.xlsx (Hoja 7 to Hoja 11)
        elif sheet in ['Hoja 7', 'Hoja 8', 'Hoja 9', 'Hoja 10', 'Hoja 11']:
            # Map sheet names to versions: Hoja 7 -> b, Hoja 8 -> c, etc.
            version_map = {'Hoja 7': 'b', 'Hoja 8': 'c', 'Hoja 9': 'd', 'Hoja 10': 'e', 'Hoja 11': 'f'}
            version = version_map[sheet]
            # Read the sheet to determine data_type
            df = pd.read_excel(file_path, sheet_name=sheet)
            if 'TypeData' in df.columns:
                if df['TypeData'].str.lower().str.contains('double').any():
                    version_info.append({
                        'version': version,
                        'language': 'python',
                        'data_type': 'double',
                        'sheet_name': sheet
                    })
                if df['TypeData'].str.lower().str.contains('float').any():
                    version_info.append({
                        'version': version,
                        'language': 'python',
                        'data_type': 'float',
                        'sheet_name': sheet
                    })
            else:
                # Default to float if TypeData column is missing
                version_info.append({
                    'version': version,
                    'language': 'python',
                    'data_type': 'float',
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
                'typeData': 'data_type',
                'version': 'version'
            })
            
            # If 'data_type' is not in columns but 'TypeData' is, copy it
            if 'data_type' not in df.columns and 'TypeData' in df.columns:
                df['data_type'] = df['TypeData']
            
            # Set the version column for all rows if info['version'] is set
            if info['version']:
                df['version'] = info['version']
            
            # Add metadata
            df['language'] = info['language']
            
            # Debug print for data_type values
            if 'data_type' in df.columns:
                df['data_type'] = df['data_type'].astype(str).str.strip().str.lower()
                print(f"\nSheet {info['sheet_name']} - Before filtering:")
                print(f"Unique data_type values: {df['data_type'].unique()}")
                print(f"Filtering for: {info['data_type']}")
                print(f"First few rows:\n{df.head()}")
                
                # If data_type is in the sheet, use it to filter
                filtered = df[df['data_type'] == info['data_type'].strip().lower()]
                print(f"\nAfter filtering for {info['data_type']}:")
                print(f"Number of rows: {len(filtered)}")
                if not filtered.empty:
                    print(f"First few rows:\n{filtered.head()}")
                df = filtered
            else:
                df['data_type'] = info['data_type']
            
            # Convert time columns to numeric, handling both comma and dot decimal separators
            if 'Normalized_ns' in df.columns:
                df['Normalized_ns'] = df['Normalized_ns'].astype(str).str.replace(',', '.').astype(float)
                print(f"\nAfter converting Normalized_ns to numeric:")
                print(f"Number of rows: {len(df)}")
                print(f"Number of NaN values: {df['Normalized_ns'].isna().sum()}")
                if not df.empty:
                    print(f"First few rows:\n{df.head()}")
            
            # Drop rows with missing values
            df = df.dropna(subset=['Normalized_ns', 'version', 'language', 'data_type'])
            print(f"\nAfter dropping NaN values:")
            print(f"Number of rows: {len(df)}")
            if not df.empty:
                print(f"First few rows:\n{df.head()}")
            
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
    
    # Set the style for better visualization
    plt.style.use('default')
    
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
            
            # Create figure with larger size
            plt.figure(figsize=(15, 8))
            
            # Create boxplot
            plot_df = pd.concat([
                r5_subset.assign(Processor='R5 5600X'),
                r9_subset.assign(Processor='R9 5900X')
            ])
            
            # Create the boxplot with improved styling
            ax = sns.boxplot(x='version', y='Normalized_ns', hue='Processor', data=plot_df,
                           palette=['#1f77b4', '#ff7f0e'], width=0.7)
            
            # Add individual data points with some jitter
            sns.stripplot(x='version', y='Normalized_ns', hue='Processor', data=plot_df,
                         palette=['#1f77b4', '#ff7f0e'], dodge=True, size=4, alpha=0.3)
            
            # Customize the plot
            plt.title(f'Performance Comparison - {lang} {dtype}', fontsize=16, pad=20)
            plt.xlabel('Algorithm Version', fontsize=12)
            plt.ylabel('Normalized Time (ns)', fontsize=12)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')
            
            # Add grid for better readability
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Adjust legend
            plt.legend(title='Processor', title_fontsize=12, fontsize=10)
            
            # Add mean values as text above each box
            for i, processor in enumerate(['R5 5600X', 'R9 5900X']):
                for j, version in enumerate(sorted(plot_df['version'].unique())):
                    subset = plot_df[(plot_df['Processor'] == processor) & (plot_df['version'] == version)]
                    mean_val = subset['Normalized_ns'].mean()
                    std_val = subset['Normalized_ns'].std()
                    plt.text(j + (i-0.5)*0.4, mean_val, f'{mean_val:.1f}\n±{std_val:.1f}', 
                            ha='center', va='bottom', fontsize=8)
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Save plot with high DPI for better quality
            plt.savefig(f'plots/performance_comparison_{lang}_{dtype}.png', dpi=300, bbox_inches='tight')
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