# Instalación de librerías
# Importar librerías
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import researchpy as rp
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from scipy.stats import f_oneway
import numpy as np
import random
import os
import glob
import re

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

def extract_version_info(sheet_name):
    """Extract version, language, and data type from sheet name"""
    # Example: "Cpp - float - ver(a)" -> ("Cpp", "float", "a")
    match = re.match(r'([A-Za-z]+)\s*-\s*([a-z]+)\s*-\s*ver\(([a-z])\)', sheet_name)
    if match:
        return {
            'language': match.group(1),
            'data_type': match.group(2),
            'version': match.group(3)
        }
    return None

def normalize_column_name(df):
    """Normalize column names to handle different naming patterns"""
    # Dictionary of possible column name mappings
    column_mappings = {
        'normalized(ns)': 'Normalized_ns',
        'normalized_ns': 'Normalized_ns',
        'normalized': 'Normalized_ns',
        'Ver': 'version',
        'version': 'version',
        'time(s)': 'time',
        'time': 'time'
    }
    
    # Rename columns if they exist
    for old_name, new_name in column_mappings.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    return df

def convert_to_numeric(df, column):
    """Convert a column to numeric values, handling different formats"""
    if column not in df.columns:
        return df
        
    # If already numeric, return as is
    if pd.api.types.is_numeric_dtype(df[column]):
        return df
        
    # Try to convert to numeric, replacing commas with dots
    try:
        df[column] = pd.to_numeric(df[column].astype(str).str.replace(',', '.'), errors='coerce')
    except:
        print(f"Warning: Could not convert {column} to numeric")
        
    return df

def boxplot_version(df_data, plot_name=None, title=None):
    """Create and save a boxplot of normalized execution times by version"""
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='version', y='Normalized_ns', data=df_data)
    plt.xlabel('Versión del Algoritmo')
    plt.ylabel('Tiempo Normalizado (ns)')
    plt.title(title or 'Distribución de Tiempos de Ejecución')
    plt.tight_layout()
    if plot_name:
        plt.savefig(f'plots/{plot_name}')
        plt.close()
    else:
        plt.show()

def detectar_outliers(data, umbral=3):
    """Detect outliers using standard deviation method"""
    media = np.mean(data)
    desviacion = np.std(data)
    outliers = [x for x in data if abs(x - media) > umbral * desviacion]
    return outliers

def run_anova_analysis(df):
    """Run ANOVA analysis and print results"""
    if df['version'].nunique() < 2:
        print("Not enough unique versions for ANOVA analysis")
        return None
        
    formula = 'Q("Normalized_ns") ~ C(version)'
    modelo1Factor = ols(formula, data=df).fit()
    anova_table = sm.stats.anova_lm(modelo1Factor, typ=2)
    
    print("===========          TABLA ANOVA one way         ================")
    print(anova_table)
    print(" ")
    print("Valor p para C(version):", anova_table.loc['C(version)', 'PR(>F)'])
    print("alpha: 0.05")
    print("")
    
    if anova_table.loc['C(version)', 'PR(>F)'] < 0.05:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        tukey = pairwise_tukeyhsd(df['Normalized_ns'], df['version'], alpha=0.05)
        print("Prueba Post-hoc (Tukey HSD):")
        print(tukey)
    
    return anova_table

def run_two_way_anova(df):
    """Run two-way ANOVA analysis and print results"""
    if df['version'].nunique() < 2 or df['n'].nunique() < 2:
        print("Not enough unique values in factors for Two-Way ANOVA")
        return None
        
    modeloTwoWay = ols('Q("Normalized_ns") ~ C(version) + C(n) + C(version) * C(n)', data=df).fit()
    tabla_anova = anova_lm(modeloTwoWay, typ=2)
    
    print("===========          TABLA ANOVA Two ways         ================")
    print(tabla_anova)
    print(" ")
    print("Valor p para C(version):", tabla_anova.loc['C(version)', 'PR(>F)'])
    print("Valor p para C(n):", tabla_anova.loc['C(n)', 'PR(>F)'])
    print("Valor p para la interacción:", tabla_anova.loc['C(version):C(n)', 'PR(>F)'])
    print("alpha: 0.05")
    
    # Gráfica de interacciones
    g = sns.catplot(x='n', y='Normalized_ns', hue='version', kind='point', data=df, ci=None)
    g.fig.suptitle('Gráfico de Interacción')
    g.savefig('plots/interaction_plot.png')
    plt.close('all')
    
    return tabla_anova

def analyze_array_size_effects(df):
    """Analyze the effect of array size on execution time"""
    if 'n' not in df.columns:
        return None
        
    # Group by array size and calculate statistics
    size_stats = df.groupby('n')['Normalized_ns'].agg(['mean', 'std', 'count'])
    
    # Run ANOVA for array size effect
    formula = 'Q("Normalized_ns") ~ C(n)'
    modelo = ols(formula, data=df).fit()
    anova_table = sm.stats.anova_lm(modelo, typ=2)
    
    print("\n=========== Array Size Effect Analysis ===============")
    print("\nArray Size Statistics:")
    print(size_stats)
    print("\nANOVA Results for Array Size Effect:")
    print(anova_table)
    
    return anova_table

def process_excel_file(excel_file):
    """Process a single Excel file and its sheets"""
    print(f"\n{'='*80}")
    print(f"Processing Excel file: {excel_file}")
    print(f"{'='*80}")
    
    # Get list of available sheets
    available_sheets = pd.ExcelFile(excel_file).sheet_names
    print(f"Available sheets: {available_sheets}")
    
    # Group sheets by language and data type
    sheet_groups = {}
    for sheet in available_sheets:
        info = extract_version_info(sheet)
        if info:
            key = (info['language'], info['data_type'])
            if key not in sheet_groups:
                sheet_groups[key] = []
            sheet_groups[key].append((sheet, info['version']))
    
    # Process each group of sheets
    for (language, data_type), sheets in sheet_groups.items():
        print(f"\nProcessing {language} {data_type} versions...")
        
        # Combine data from all versions
        combined_data = []
        for sheet, version in sheets:
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                print(f"\nColumns in {sheet}: {df.columns.tolist()}")
                
                # Normalize column names
                df = normalize_column_name(df)
                
                # Add version information
                df['version'] = version
                df['language'] = language
                df['data_type'] = data_type
                
                # Convert time columns to numeric
                df = convert_to_numeric(df, 'time')
                df = convert_to_numeric(df, 'Normalized_ns')
                
                # Convert time to normalized nanoseconds if needed
                if 'time' in df.columns and 'Normalized_ns' not in df.columns:
                    df['Normalized_ns'] = df['time'] * 1e9
                
                combined_data.append(df)
            except Exception as e:
                print(f"Error reading sheet {sheet}: {str(e)}")
                continue
        
        if not combined_data:
            continue
            
        # Combine all data
        df = pd.concat(combined_data, ignore_index=True)
        
        # Clean and prepare data
        df['version'] = df['version'].str.strip()
        
        print("\nData Summary:")
        print(df.info())
        print("\nFirst few rows:")
        print(df.head())
        
        # Run ANOVA and create boxplot
        plot_name = f'boxplot_{language}_{data_type}.png'
        title = f'Distribución de Tiempos de Ejecución - {language} {data_type}'
        boxplot_version(df, plot_name, title)
        anova_results = run_anova_analysis(df)
        
        # Analyze array size effects
        size_anova = analyze_array_size_effects(df)
        
        # Print version statistics
        print("\n================= Resumen de Estadísticas por Versión=============")
        print(rp.summary_cont(df['Normalized_ns'].groupby(df['version'])))
        
        # Calculate sample size
        Stat_data = df[["Normalized_ns", "version"]].groupby("version").agg({
            "Normalized_ns": ["min", "max", "median", "mean", "std", "var"]
        })
        Stat_data = Stat_data.Normalized_ns
        
        Er = 3  # 3%
        Error_abs = Stat_data['mean'] * (Er/100)
        Z = 1.96  # 95% confidence
        
        print("\nCálculo del Error absoluto equivalente a Er=3%")
        print(Error_abs)
        print("\nCálculo del Tamaño de Muestra")
        print(Stat_data['var'] * (Z*Z) / (Error_abs*Error_abs))

def main():
    # Find all Excel files in the workspace
    excel_files = glob.glob("*.xlsx") + glob.glob("data/*.xlsx")
    
    if not excel_files:
        print("No Excel files found in the workspace or data directory")
        return
        
    print(f"Found {len(excel_files)} Excel files to process")
    
    # Process each Excel file
    for excel_file in excel_files:
        try:
            process_excel_file(excel_file)
        except Exception as e:
            print(f"Error processing {excel_file}: {str(e)}")
            continue

if __name__ == "__main__":
    main() 