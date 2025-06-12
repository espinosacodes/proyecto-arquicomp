import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols
import researchpy as rp
from scipy import stats
from statsmodels.stats.multicomp import MultiComparison
from scipy.stats import shapiro, levene, mannwhitneyu, kruskal
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

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
    
    return df

def check_assumptions(df):
    """Check ANOVA assumptions: normality and homogeneity of variances"""
    print("\nChecking ANOVA Assumptions:")
    
    # Normality test (Shapiro-Wilk)
    print("\nNormality Test (Shapiro-Wilk):")
    for group in df.groupby(['processor', 'version', 'data_type'], observed=True):
        stat, p_value = shapiro(group[1]['Normalized_ns'])
        print(f"Group {group[0]}: W={stat:.4f}, p={p_value:.4f}")
    
    # Homogeneity of variances (Levene's test)
    print("\nHomogeneity of Variances (Levene's test):")
    groups = [group for _, group in df.groupby(['processor', 'version', 'data_type'], observed=True)['Normalized_ns']]
    if len(groups) > 1:
        stat, p_value = levene(*groups)
        print(f"Levene's test: W={stat:.4f}, p={p_value:.4f}")
    else:
        print("Not enough groups for Levene's test")

def perform_statistical_analysis(df):
    """Perform both parametric and non-parametric analysis"""
    print("\nPerforming Statistical Analysis:")
    
    # One-way analysis for each factor
    print("\nOne-way Analysis Results:")
    for factor in ['processor', 'version', 'data_type']:
        if df[factor].nunique() > 1:
            groups = [group for _, group in df.groupby(factor, observed=True)['Normalized_ns']]
            
            # Parametric test (ANOVA)
            f_stat, p_val = stats.f_oneway(*groups)
            print(f"\n{factor.capitalize()} effect (ANOVA):")
            print(f"F={f_stat:.4f}, p={p_val:.4f}")
            
            # Calculate effect size (Eta-squared)
            ss_total = sum((df['Normalized_ns'] - df['Normalized_ns'].mean())**2)
            ss_between = sum(len(g) * ((g.mean() - df['Normalized_ns'].mean())**2) for g in groups)
            eta_squared = ss_between / ss_total
            print(f"Eta-squared: {eta_squared:.4f}")
            
            # Non-parametric test (Kruskal-Wallis)
            h_stat, p_val = kruskal(*groups)
            print(f"\n{factor.capitalize()} effect (Kruskal-Wallis):")
            print(f"H={h_stat:.4f}, p={p_val:.4f}")
            
            # Calculate effect size (Epsilon-squared)
            n = len(df)
            epsilon_squared = (h_stat - (len(groups) - 1)) / (n - len(groups))
            print(f"Epsilon-squared: {epsilon_squared:.4f}")
        else:
            print(f"\n{factor.capitalize()} effect: Only one level present, skipping analysis")

def perform_post_hoc_tests(df):
    """Perform both parametric and non-parametric post-hoc tests"""
    print("\nPost-hoc Analysis:")
    
    for factor in ['processor', 'version', 'data_type']:
        if df[factor].nunique() > 1:
            print(f"\nPost-hoc tests for {factor}:")
            
            # Parametric test (Tukey's HSD)
            print("\nTukey's HSD:")
            mc = MultiComparison(df['Normalized_ns'], df[factor])
            result = mc.tukeyhsd()
            print(result)
            
            # Non-parametric test (Mann-Whitney U with Bonferroni correction)
            print("\nMann-Whitney U (with Bonferroni correction):")
            groups = df.groupby(factor, observed=True)['Normalized_ns']
            group_names = list(groups.groups.keys())
            
            for i in range(len(group_names)):
                for j in range(i+1, len(group_names)):
                    group1 = groups.get_group(group_names[i])
                    group2 = groups.get_group(group_names[j])
                    stat, p_val = mannwhitneyu(group1, group2, alternative='two-sided')
                    # Bonferroni correction
                    p_val *= len(group_names) * (len(group_names) - 1) / 2
                    print(f"{group_names[i]} vs {group_names[j]}:")
                    print(f"U={stat:.4f}, p={p_val:.4f}")
        else:
            print(f"\nSkipping post-hoc tests for {factor} (only one level)")

def create_visualizations(df):
    """Create comprehensive visualizations"""
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
    
    # 2. Scatter plot with regression line
    plt.figure(figsize=(15, 8))
    sns.regplot(data=df, x='n', y='Normalized_ns', scatter_kws={'alpha':0.5})
    plt.title('Performance vs Matrix Size with Regression Line')
    plt.xlabel('Matrix Size (n)')
    plt.ylabel('Normalized Time (ns)')
    plt.tight_layout()
    plt.savefig('performance_vs_matrix_size.png')
    plt.close()
    
    # 3. Interaction plot (only if we have multiple levels for both factors)
    if df['version'].nunique() > 1 and df['processor'].nunique() > 1:
        plt.figure(figsize=(15, 8))
        sns.pointplot(data=df, x='version', y='Normalized_ns', hue='processor', 
                     markers=['o', 's'], linestyles=['-', '--'])
        plt.title('Interaction Plot: Version × Processor')
        plt.xlabel('Algorithm Version')
        plt.ylabel('Mean Normalized Time (ns)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('interaction_plot.png')
        plt.close()
    
    # 4. Violin plot
    plt.figure(figsize=(15, 8))
    sns.violinplot(data=df, x='version', y='Normalized_ns', hue='processor', 
                  split=True, inner='quart')
    plt.title('Performance Distribution (Violin Plot)')
    plt.xlabel('Algorithm Version')
    plt.ylabel('Normalized Time (ns)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('performance_violin_plot.png')
    plt.close()
    
    # 5. Q-Q plot for each group
    plt.figure(figsize=(15, 8))
    for i, (name, group) in enumerate(df.groupby(['processor', 'version', 'data_type'], observed=True)):
        plt.subplot(1, len(df.groupby(['processor', 'version', 'data_type'], observed=True)), i+1)
        sm.qqplot(group['Normalized_ns'], line='45')
        plt.title(f'Q-Q Plot: {name}')
    plt.tight_layout()
    plt.savefig('qq_plots.png')
    plt.close()

def main():
    # Load and prepare data
    print("Loading and preparing data...")
    df = load_and_prepare_data()
    
    # Print basic statistics
    print("\nBasic Statistics:")
    print(df.groupby(['processor', 'version', 'data_type'], observed=True)['Normalized_ns'].describe())
    
    # Check ANOVA assumptions
    check_assumptions(df)
    
    # Perform statistical analysis
    perform_statistical_analysis(df)
    
    # Perform post-hoc tests
    perform_post_hoc_tests(df)
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_visualizations(df)
    
    # Save results to file
    with open('statistical_analysis_results.txt', 'w') as f:
        f.write("Statistical Analysis Results\n")
        f.write("=========================\n\n")
        f.write("Basic Statistics:\n")
        f.write(str(df.groupby(['processor', 'version', 'data_type'], observed=True)['Normalized_ns'].describe()))
        f.write("\n\nAssumption Tests:\n")
        f.write("Normality and homogeneity of variances tests results are shown above.\n")
        f.write("\nStatistical Tests:\n")
        f.write("Both parametric (ANOVA) and non-parametric (Kruskal-Wallis) tests were performed.\n")
        f.write("Post-hoc tests include both Tukey's HSD and Mann-Whitney U with Bonferroni correction.\n")

if __name__ == "__main__":
    main() 