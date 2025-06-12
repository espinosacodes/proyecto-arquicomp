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

# Gráfico de Cajas y Bigotes
# Save plot as image
def boxplot_version(df_data, plot_name):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='version', y='Normalized_ns', data=df_data)
    plt.xlabel('Versión del Algoritmo')
    plt.ylabel('Tiempo Normalizado (ns)')
    plt.title('Distribución de Tiempos de Ejecución')
    plt.tight_layout()
    plt.savefig(f'plots/{plot_name}')
    plt.close()

#boxplot_version(df)

#  Detección de Valores Atípicos
def detectar_outliers(data, umbral=3):
    media = np.mean(data)
    desviacion = np.std(data)
    outliers = [x for x in data if abs(x - media) > umbral * desviacion]
    return outliers

def boxplot_version(df_data):
  # Crear el gráfico de cajas y bigotes
  print("===========          Gráfico de cajas y bigotes         ================")
  # Suponiendo que 'Normalized (ns)' es la columna que contiene los datos de tiempo normalizado y 'version' es la columna que indica la versión del algoritmo
  sns.set(style="whitegrid")  # Establecer el estilo del gráfico
  plt.figure(figsize=(10, 6))  # Tamaño del gráfico
  sns.boxplot(x='version', y='Normalized_ns', data=df_data)
    # Etiquetas y título
  plt.xlabel('Algoritmo')
  plt.ylabel('Tiempo normalizado(ns)')
  plt.title('Gráfico de Cajas y Bigotes para Tiempos de Ejecución')
  # Mostrar el gráfico
  plt.show()

def detectar_outliers_desviacion_estandar(data, umbral=3):
    media = np.mean(data)
    desviacion_estandar = np.std(data)
    outliers = [x for x in data if abs(x - media) > umbral * desviacion_estandar]
    return outliers
# Cargar datos de la Semana 2
#need to do a loop to read all sheets in the excel file
excel_file = "data/tr5.xlsx"
print(f"Processing Excel file: {excel_file}")
for sheet in pd.read_excel(excel_file, sheet_name=None):
    print(f"  Processing sheet: {sheet}")
    df = pd.read_excel(excel_file, sheet_name=sheet)
    df = df.rename(columns={"normalized(ns)": "Normalized_ns", "Ver": "version"})
    df['version'] = df['version'].str.strip()
    df['Normalized_ns'] = pd.to_numeric(df['Normalized_ns'].str.replace(',', '.', regex=False), errors='coerce')
    df.info()
    print(df.head())
    # Only run ANOVA and plots if there are at least 2 unique versions
    if df['version'].nunique() >= 2:
        # Crear el gráfico de cajas y bigotes
        boxplot_version(df, f'boxplot_{sheet}.png')
        # ANOVA de una vía
        formula = 'Q("Normalized_ns") ~ C(version) '
        modelo1Factor = ols(formula, data=df).fit() # alpha is not a valid kwarg
        anova_table = sm.stats.anova_lm(modelo1Factor, typ=2)
        print("===========          TABLA ANOVA one way         ================")
        print(anova_table)
        print(" ")
        print("Valor p para C(version):", anova_table.loc['C(version)', 'PR(>F)'])
        print("alpha: 0.05")
        print("")
        # Prueba Post-hoc (Tukey HSD si ANOVA es significativo)
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        if anova_table.loc['C(version)', 'PR(>F)'] < 0.05:
            tukey = pairwise_tukeyhsd(df['Normalized_ns'], df['version'], alpha=0.05)
            print(tukey)
    else:
        print(f"  Skipping ANOVA and boxplot for sheet '{sheet}' (not enough unique versions)")
    
#Verificar el número de niveles del factor Version
print(df['version'].unique())
print(rp.summary_cont(df['Normalized_ns']))
print("   ")
print("================= Resumen de Estadísticas por Versión=============")
print(rp.summary_cont(df['Normalized_ns'].groupby(df['version'])))
print("   ")

Stat_data=df[["Normalized_ns", "version"]].groupby("version").agg({"Normalized_ns":["min", "max", "median", "mean" ,np.std,np.var]})
Stat_data=Stat_data.Normalized_ns
print(Stat_data)
Er=3 # 1%
Error_abs=Stat_data['mean']*(Er/100)
print("")
print("Cálculo del Error absoluto equivalente a Er=3%")
print(Error_abs)
print("")
print("Cálculo del Tamaño de Muestra ")
Z=1.96 #95%
print(Stat_data['var']*(Z*Z)/(Error_abs*Error_abs))
print("")

# Crear el gráfico de cajas y bigotes
boxplot_version(df)

# ANOVA de una vía
# Realizamos el análisis de un factor usando ANOVA
formula = 'Q("Normalized_ns") ~ C(version) '  # Indicamos que queremos evaluar el impacto de version
modelo1Factor = ols(formula, alpha=0.05, data=df).fit() # La fórmula 'Normalized_ns ~ C(version)' indica que se está evaluando el efecto de la variable 'version' sobre la variable 'Normalized_ns'.
anova_table = sm.stats.anova_lm(modelo1Factor, typ=2) #anova_lm() para calcular la tabla ANOVA a partir del modelo ajustado. El argumento typ=2 especifica que se debe utilizar el tipo 2 (El orden de las variables en el modelo no afecta el cálculo) de suma de cuadrados.
print("===========          TABLA ANOVA one way         ================")
print(anova_table)
print(" ")

print("Valor p para C(version):", anova_table.loc['C(version)', 'PR(>F)'])
print("alpha: 0.05")
print("")

# Prueba Post-hoc (Tukey HSD si ANOVA es significativo)
from statsmodels.stats.multicomp import pairwise_tukeyhsd

if anova_table.loc['C(version)', 'PR(>F)'] < 0.05:
    tukey = pairwise_tukeyhsd(df['Normalized_ns'], df['version'], alpha=0.05)
    print(tukey)
    
# Filtrar solo las versiones ver(a) y ver(b)
df_ab = df[df["version"].isin(["C++ver(a)", "C++ver(b)"])]

# Crear el gráfico de cajas y bigotes
plt.figure(figsize=(8, 6))
sns.boxplot(x="version", y="Normalized_ns", data=df_ab)
plt.xlabel("Versión del Algoritmo")
plt.ylabel("Tiempo Normalizado (ns)")
plt.title("Diagrama de Cajas y Bigotes: C++ver(a) vs C++ver(b)")

# Mostrar el gráfico
plt.show()

modelo_ab = ols('Normalized_ns ~ C(version)', data=df_ab).fit() # La fórmula 'Normalized_ns ~ C(version)' indica que se está evaluando el efecto de la variable 'version' sobre la variable 'Normalized_ns'.
# Calcular la tabla ANOVA
tabla_anova_ab = anova_lm(modelo_ab, typ=2) #anova_lm() para calcular la tabla ANOVA a partir del modelo ajustado. El argumento typ=2 especifica que se debe utilizar el tipo 2 (El orden de las variables en el modelo no afecta el cálculo) de suma de cuadrados.
# Mostrar la tabla ANOVA
print(tabla_anova_ab)
# Imprimir el valor p para C(version)
print("Valor p para C(version):", tabla_anova_ab.loc['C(version)', 'PR(>F)'])

print("================= Análisis de valores atípicos =========================")

data_ver_a=df[df['version'].isin(['ver(a)'])]
datos = data_ver_a['Normalized_ns']  # Reemplaza con la columna de datos que deseas analizar
outliers = detectar_outliers_desviacion_estandar(datos,1)
print("Outliers detectados ver(b):", outliers)

data_ver_b=df[df['version'].isin(['ver(b)'])]
datos = data_ver_a['Normalized_ns']  # Reemplaza con la columna de datos que deseas analizar
outliers = detectar_outliers_desviacion_estandar(datos,1)
print("Outliers detectados ver(b):", outliers)

#change to 4 factors 
#df2f = pd.read_excel("../data/tr5.xlsx","")
df2f = pd.read_excel("data/tr5.xlsx","FourFactors")
#df2f= df2f.drop(columns=['typeData', 'ISA'])
df2f = df2f.rename(columns={"normalized(ns)":"Normalized_ns", "Ver":"version"})
df2f['version'] = df2f['version'].str.strip()
df2f['Normalized_ns'] = pd.to_numeric(df2f['Normalized_ns'].str.replace(',', '.', regex=False), errors='coerce')
df2f.info()
print(df2f.head())
# Only run Two-Way ANOVA if there are at least 2 unique values in both factors
if df2f['version'].nunique() >= 2 and df2f['n'].nunique() >= 2:
    modeloTwoWay = ols('Q("Normalized_ns") ~ C(version) + C(n) + C(version) * C(n)', data=df2f).fit()
    print("===========          TABLA ANOVA Two ways         ================")
    tabla_anova = anova_lm(modeloTwoWay , typ=2)
    print(tabla_anova)
    print(" ")
    print("Valor p para C(version):", tabla_anova.loc['C(version)', 'PR(>F)'])
    print("Valor p para C(n):", tabla_anova.loc['C(n)', 'PR(>F)'])
    print("Valor p para la interacción:", tabla_anova.loc['C(version):C(n)', 'PR(>F)'])
    print("alpha: 0.05")
    print("================= -------------- =========================")
    print("")
    # Gráfica de interacciones
    g = sns.catplot(x='n', y='Normalized_ns', hue='version', kind='point', data=df2f, ci=None)
    g.fig.suptitle('Gráfico de Interacción')
    g.savefig('plots/interaction_plot.png')
    plt.close('all')
else:
    print("Skipping Two-Way ANOVA and interaction plot (not enough unique values in factors)")
