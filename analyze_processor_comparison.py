import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def load_and_process_data(file_path):
    """Load and process data from Excel file"""
    df = pd.read_excel(file_path)
    
    # Extract version info from sheet names
    version_info = []
    for sheet in pd.ExcelFile(file_path).sheet_names:
        if 'ver' in sheet:
            version = sheet.split('ver(')[1].split(')')[0]
            lang = sheet.split(' - ')[0]
            dtype = sheet.split(' - ')[1].split(' - ')[0]
            version_info.append({'version': version, 'language': lang, 'data_type': dtype})
    
    # Combine data from all sheets
    all_data = []
    for info in version_info:
        sheet_name = f"{info['language']} - {info['data_type']} - ver({info['version']})"
        try:
            sheet_data = pd.read_excel(file_path, sheet_name=sheet_name)
            sheet_data['version'] = info['version']
            sheet_data['language'] = info['language']
            sheet_data['data_type'] = info['data_type']
            all_data.append(sheet_data)
        except:
            continue
    
    return pd.concat(all_data, ignore_index=True)

def create_comparison_plots(r5_data, r9_data):
    """Create comparison plots between R5 and R9 data"""
    plt.style.use('seaborn')
    
    # 1. Box plot comparing overall performance
    plt.figure(figsize=(12, 6))
    data = pd.DataFrame({
        'R5 5600X': r5_data['Normalized_ns'],
        'R9 5900X': r9_data['Normalized_ns']
    })
    sns.boxplot(data=data)
    plt.title('Performance Comparison: R5 5600X vs R9 5900X')
    plt.ylabel('Normalized Execution Time (ns)')
    plt.savefig('plots/processor_comparison_boxplot.png')
    plt.close()
    
    # 2. Performance by version
    plt.figure(figsize=(15, 8))
    versions = sorted(set(r5_data['version']))
    x = np.arange(len(versions))
    width = 0.35
    
    r5_means = [r5_data[r5_data['version'] == v]['Normalized_ns'].mean() for v in versions]
    r9_means = [r9_data[r9_data['version'] == v]['Normalized_ns'].mean() for v in versions]
    
    plt.bar(x - width/2, r5_means, width, label='R5 5600X')
    plt.bar(x + width/2, r9_means, width, label='R9 5900X')
    
    plt.xlabel('Algorithm Version')
    plt.ylabel('Average Normalized Time (ns)')
    plt.title('Performance Comparison by Algorithm Version')
    plt.xticks(x, versions)
    plt.legend()
    plt.savefig('plots/processor_comparison_by_version.png')
    plt.close()

def perform_statistical_analysis(r5_data, r9_data):
    """Perform statistical analysis on the data"""
    # T-test for overall performance
    t_stat, p_value = stats.ttest_ind(r5_data['Normalized_ns'], r9_data['Normalized_ns'])
    
    # Calculate performance improvement percentage
    r5_mean = r5_data['Normalized_ns'].mean()
    r9_mean = r9_data['Normalized_ns'].mean()
    improvement = ((r5_mean - r9_mean) / r5_mean) * 100
    
    print("\nStatistical Analysis Results:")
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Average R5 5600X time: {r5_mean:.2f} ns")
    print(f"Average R9 5900X time: {r9_mean:.2f} ns")
    print(f"Performance improvement: {improvement:.2f}%")
    
    # Analysis by version
    print("\nPerformance by Version:")
    for version in sorted(set(r5_data['version'])):
        r5_version_mean = r5_data[r5_data['version'] == version]['Normalized_ns'].mean()
        r9_version_mean = r9_data[r9_data['version'] == version]['Normalized_ns'].mean()
        version_improvement = ((r5_version_mean - r9_version_mean) / r5_version_mean) * 100
        print(f"\nVersion {version}:")
        print(f"R5 5600X: {r5_version_mean:.2f} ns")
        print(f"R9 5900X: {r9_version_mean:.2f} ns")
        print(f"Improvement: {version_improvement:.2f}%")

def main():
    # Load data
    r5_data = load_and_process_data('data/tr5.xlsx')
    r9_data = load_and_process_data('data/tr9.xlsx')
    
    # Create comparison plots
    create_comparison_plots(r5_data, r9_data)
    
    # Perform statistical analysis
    perform_statistical_analysis(r5_data, r9_data)

if __name__ == "__main__":
    main() 