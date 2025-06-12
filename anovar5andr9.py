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

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

def boxplot_version(df_data, plot_name=None):
    """Create and save a boxplot of normalized execution times by version"""
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='version', y='Normalized_ns', data=df_data)
    plt.xlabel('Versión del Algoritmo')
    plt.ylabel('Tiempo Normalizado (ns)')
    plt.title('Distribución de Tiempos de Ejecución')
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

# Main analysis
excel_file = "data/tr5.xlsx"
print(f"Processing Excel file: {excel_file}")

# Get list of available sheets
available_sheets = pd.ExcelFile(excel_file).sheet_names
print(f"Available sheets: {available_sheets}")

# Process each sheet
for sheet in available_sheets:
    print(f"\nProcessing sheet: {sheet}")
    df = pd.read_excel(excel_file, sheet_name=sheet)
    
    # Clean and prepare data
    df = df.rename(columns={"normalized(ns)": "Normalized_ns", "Ver": "version"})
    df['version'] = df['version'].str.strip()
    df['Normalized_ns'] = pd.to_numeric(df['Normalized_ns'].str.replace(',', '.', regex=False), errors='coerce')
    
    print("\nData Summary:")
    print(df.info())
    print("\nFirst few rows:")
    print(df.head())
    
    # Run ANOVA and create boxplot
    boxplot_version(df, f'boxplot_{sheet}.png')
    anova_results = run_anova_analysis(df)
    
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

# Process FourFactors sheet if it exists
if "FourFactors" in available_sheets:
    print("\nProcessing FourFactors sheet...")
    df2f = pd.read_excel("data/tr5.xlsx", "FourFactors")
    df2f = df2f.rename(columns={"normalized(ns)": "Normalized_ns", "Ver": "version"})
    df2f['version'] = df2f['version'].str.strip()
    df2f['Normalized_ns'] = pd.to_numeric(df2f['Normalized_ns'].str.replace(',', '.', regex=False), errors='coerce')

    print("\nFourFactors Data Summary:")
    print(df2f.info())
    print("\nFirst few rows:")
    print(df2f.head())

    # Run two-way ANOVA
    two_way_results = run_two_way_anova(df2f)
else:
    print("\nFourFactors sheet not found in the Excel file. Skipping two-way ANOVA analysis.")
