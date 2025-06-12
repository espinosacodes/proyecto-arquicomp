import sys
import time
import numpy as np

# Adaptado del código C++: https://inst.eecs.berkeley.edu/~cs61c/fa12/labs/07/
# Se implementan las 6 versiones de multiplicación de matrices con diferentes órdenes de bucles.
# Usamos numpy para definir explícitamente float32 y float64, manteniendo equivalencia con C++.
# time.perf_counter() se usa para medir tiempos con alta precisión, similar a chrono.

# Versión ijk
def product_mat_a(n, A, B, C, dtype):
    for i in range(n):
        for j in range(n):
            sum_val = dtype(0)  # Inicializar sum_val según el tipo de dato
            for k in range(n):
                sum_val += A[i + k * n] * B[k + j * n]  # C[i][j] += A[i][k] * B[k][j]
            C[i + j * n] += sum_val

# Versión jik
def product_mat_b(n, A, B, C, dtype):
    for j in range(n):
        for i in range(n):
            sum_val = dtype(0)
            for k in range(n):
                sum_val += A[i + k * n] * B[k + j * n]  # C[i][j] += A[i][k] * B[k][j]
            C[i + j * n] += sum_val

# Versión jki
def product_mat_c(n, A, B, C, dtype):
    for j in range(n):
        for k in range(n):
            r = B[k + j * n]
            for i in range(n):
                C[i + j * n] += A[i + k * n] * r  # C[i][j] += A[i][k] * B[k][j]

# Versión kji
def product_mat_d(n, A, B, C, dtype):
    for k in range(n):
        for j in range(n):
            r = B[k + j * n]
            for i in range(n):
                C[i + j * n] += A[i + k * n] * r  # C[i][j] += A[i][k] * B[k][j]

# Versión kij
def product_mat_e(n, A, B, C, dtype):
    for k in range(n):
        for i in range(n):
            r = A[i + k * n]
            for j in range(n):
                C[i + j * n] += r * B[k + j * n]  # C[i][j] += A[i][k] * B[k][j]

# Versión ikj
def product_mat_f(n, A, B, C, dtype):
    for i in range(n):
        for k in range(n):
            r = A[i + k * n]
            for j in range(n):
                C[i + j * n] += r * B[k + j * n]  # C[i][j] += A[i][k] * B[k][j]

# Función para imprimir matrices (solo para depuración opcional)
def print_mat(n, M):
    for j in range(n):
        row = [f"{M[i + j * n]:.3f}" for i in range(n)]
        print(" ".join(row) + ";")
    print("\n")

# Función principal
def main():
    # Leer argumentos de línea de comandos
    if len(sys.argv) < 3:
        print("Uso: python script.py <n> <samples>")
        return

    n = int(sys.argv[1])  # Tamaño de la matriz
    samples = int(sys.argv[2])  # Número de muestras

    # Mapeo de versiones a funciones
    versions = {
        'A': product_mat_a,
        'B': product_mat_b,
        'C': product_mat_c,
        'D': product_mat_d,
        'E': product_mat_e,
        'F': product_mat_f
    }

    # Tipos de datos a probar
    dtypes = {
        'float': np.float32,
        'double': np.float64
    }

    print("ver\ttypeData\tISA\t#sample\tn\ttime(s)\tNormalized(ns)")
    
    # Ejecutar experimentos para cada tipo de dato y versión
    for dtype_name, dtype in dtypes.items():
        for ver, func in versions.items():
            # Crear matrices como arreglos numpy con el tipo de dato especificado
            A = np.full((n * n), 2.0, dtype=dtype)
            B = np.full((n * n), 4.0, dtype=dtype)

            for s in range(samples):
                # Reiniciar matriz C a ceros antes de cada ejecución
                C = np.zeros((n * n), dtype=dtype)

                # Medir tiempo con alta precisión usando time.perf_counter()
                start = time.perf_counter()
                func(n, A, B, C, dtype)
                end = time.perf_counter()

                # Calcular tiempo en segundos y normalizado en ns
                seconds = end - start
                time_normalized = (seconds * 1.0e9) / (n * n * n)

                # Formatear y escribir resultados
                result = f"Py_ver({ver})\t{dtype_name}\tx64\t{s:05d}\t{n:05d}\t{seconds:.4f}\t{time_normalized:.4f}"
                print(result)

            # Imprimir matrices si hay un tercer argumento (opcional)
            if len(sys.argv) > 3:
                print_mat(n, A)
                print_mat(n, B)
                print_mat(n, C)

if __name__ == "__main__":
    main()
