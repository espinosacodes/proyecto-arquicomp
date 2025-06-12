import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols
import researchpy as rp
from scipy import stats

def load_and_prepare_data():
    # Load Ryzen 5 data
    df_r5 = pd.read_excel("data r5 and r9/Tiempos de ejecucion (Ryzen 5) - Tamano muestra total (15) - Lab Arquitectura computadores - Proyecto Final.xlsx")
    df_r5['processor'] = 'Ryzen 5'
    
    # Load Ryzen 9 data
    df_r9 = pd.read_excel("data r5 and r9/tiempos de ejecucion ryzen 9 n=15_combined.xlsx")
    df_r9['processor'] = 'Ryzen 9'
    
    # Combine datasets
    df = pd.concat([df_r5, df_r9], ignore_index=True)
    
    # Clean and prepare data
    df = df.rename(columns={
        "Normalized(ns)": "Normalized_ns",
        "ver": "version",
        "typeData": "data_type"
    })
    
    # Convert categorical variables
    df['version'] = df['version'].astype('category')
    df['processor'] = df['processor'].astype('category')
    df['data_type'] = df['data_type'].astype('category')
    
    # Drop rows with NaN in relevant columns
    df = df.dropna(subset=['Normalized_ns', 'version', 'processor', 'data_type'])
    
    # Print unique values for debugging
    print("\nUnique values in each category:")
    print("Versions:", df['version'].unique())
    print("Processors:", df['processor'].unique())
    print("Data types:", df['data_type'].unique())
    
    return df

def perform_anova_analysis(df):
    # First, perform one-way ANOVA for each factor (only if there are at least 2 groups)
    print("\nOne-way ANOVA Results:")
    
    # Processor effect
    if df['processor'].nunique() > 1:
        processor_groups = [group for _, group in df.groupby('processor')['Normalized_ns']]
        f_stat, p_val = stats.f_oneway(*processor_groups)
        print(f"Processor effect: F={f_stat:.4f}, p={p_val:.4f}")
    else:
        print("Processor effect: Only one group, skipping ANOVA.")
    
    # Version effect
    if df['version'].nunique() > 1:
        version_groups = [group for _, group in df.groupby('version')['Normalized_ns']]
        f_stat, p_val = stats.f_oneway(*version_groups)
        print(f"Version effect: F={f_stat:.4f}, p={p_val:.4f}")
    else:
        print("Version effect: Only one group, skipping ANOVA.")
    
    # Data type effect
    if df['data_type'].nunique() > 1:
        dtype_groups = [group for _, group in df.groupby('data_type')['Normalized_ns']]
        f_stat, p_val = stats.f_oneway(*dtype_groups)
        print(f"Data type effect: F={f_stat:.4f}, p={p_val:.4f}")
    else:
        print("Data type effect: Only one group, skipping ANOVA.")
    
    # Now perform multi-way ANOVA (only if all factors have at least 2 groups)
    print("\nMulti-way ANOVA Results:")
    if df['processor'].nunique() > 1 and df['version'].nunique() > 1 and df['data_type'].nunique() > 1:
        formula = 'Normalized_ns ~ processor + version + data_type + processor:version + processor:data_type + version:data_type'
        model = ols(formula, data=df).fit()
        anova_table = anova_lm(model, typ=2)
        return model, anova_table
    else:
        print("Not enough groups for multi-way ANOVA.")
        return None, None

def create_visualizations(df):
    # Set style
    sns.set(style="whitegrid")
    
    # 1. Box plot by processor and version
    plt.figure(figsize=(15, 8))
    sns.boxplot(x='version', y='Normalized_ns', hue='processor', data=df)
    plt.title('Performance Distribution by Processor and Algorithm Version')
    plt.xlabel('Algorithm Version')
    plt.ylabel('Normalized Time (ns)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('performance_by_processor_version.png')
    plt.close()
    
    # 2. Scatter plot of matrix size vs performance
    plt.figure(figsize=(15, 8))
    sns.scatterplot(data=df, x='n', y='Normalized_ns', hue='processor', style='version')
    plt.title('Performance vs Matrix Size')
    plt.xlabel('Matrix Size (n)')
    plt.ylabel('Normalized Time (ns)')
    plt.tight_layout()
    plt.savefig('performance_vs_matrix_size.png')
    plt.close()
    
    # 3. Heatmap of mean performance by processor and data type
    if df['data_type'].nunique() > 1:
        pivot_table = df.pivot_table(
            values='Normalized_ns',
            index='processor',
            columns='data_type',
            aggfunc='mean'
        )
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='YlOrRd')
        plt.title('Mean Performance by Processor and Data Type')
        plt.tight_layout()
        plt.savefig('performance_heatmap.png')
        plt.close()

def main():
    # Load and prepare data
    print("Loading and preparing data...")
    df = load_and_prepare_data()
    
    # Print basic statistics
    print("\nBasic Statistics:")
    print(df.groupby(['processor', 'version', 'data_type'])['Normalized_ns'].describe())
    
    # Perform ANOVA analysis
    print("\nPerforming ANOVA analysis...")
    model, anova_table = perform_anova_analysis(df)
    
    # Print ANOVA results
    if anova_table is not None:
        print("\nANOVA Results:")
        print(anova_table)
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_visualizations(df)
    
    # Save results to file
    if anova_table is not None and model is not None:
        with open('anova_results.txt', 'w') as f:
            f.write("ANOVA Analysis Results\n")
            f.write("=====================\n\n")
            f.write(str(anova_table))
            f.write("\n\nModel Summary:\n")
            f.write(str(model.summary()))

if __name__ == "__main__":
    main() 