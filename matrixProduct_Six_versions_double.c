#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

// Adaptado de https://inst.eecs.berkeley.edu/~cs61c/fa12/labs/07/
// Implementación en C++ para double (64 bits), con las 6 variantes del orden de bucles.

// Versión ijk
void ProductMat_a(int n, double* A, double* B, double* C) {
    int i, j, k;
    double sum;
    /* This is ijk loop order version. */
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            sum = 0;
            for (k = 0; k < n; k++) {
                sum += A[i + k * n] * B[k + j * n]; // C[i][j] += A[i][k] * B[k][j]
            }
            C[i + j * n] += sum;
        }
    }
}

// Versión jik
void ProductMat_b(int n, double* A, double* B, double* C) {
    int i, j, k;
    double sum;
    /* This is jik loop order version. */
    for (j = 0; j < n; j++) {
        for (i = 0; i < n; i++) {
            sum = 0;
            for (k = 0; k < n; k++) {
                sum += A[i + k * n] * B[k + j * n];
            }
            C[i + j * n] += sum;
        }
    }
}

// Versión jki
void ProductMat_c(int n, double* A, double* B, double* C) {
    int i, j, k;
    double r;
    /* This is jki loop order version. */
    for (j = 0; j < n; j++) {
        for (k = 0; k < n; k++) {
            r = B[k + j * n];
            for (i = 0; i < n; i++) {
                C[i + j * n] += A[i + k * n] * r;
            }
        }
    }
}

// Versión kji
void ProductMat_d(int n, double* A, double* B, double* C) {
    int i, j, k;
    double r;
    /* This is kji loop order. */
    for (k = 0; k < n; k++) {
        for (j = 0; j < n; j++) {
            r = B[k + j * n];
            for (i = 0; i < n; i++) {
                C[i + j * n] += A[i + k * n] * r;
            }
        }
    }
}

// Versión kij
void ProductMat_e(int n, double* A, double* B, double* C) {
    int i, j, k;
    double r;
    /* This is kij loop order version. */
    for (k = 0; k < n; k++) {
        for (i = 0; i < n; i++) {
            r = A[i + k * n];
            for (j = 0; j < n; j++) {
                C[i + j * n] += r * B[k + j * n];
            }
        }
    }
}

// Versión ikj
void ProductMat_f(int n, double* A, double* B, double* C) {
    int i, j, k;
    double r;
    /* This is ikj loop order version. */
    for (i = 0; i < n; i++) {
        for (k = 0; k < n; k++) {
            r = A[i + k * n];
            for (j = 0; j < n; j++) {
                C[i + j * n] += r * B[k + j * n];
            }
        }
    }
}

// Función para imprimir matrices
void PrintMat(int n, double* M) {
    int i, j;
    for (j = 0; j < n; j++) {
        for (i = 0; i < n; i++) {
            printf("%.3f ", M[i + j * n]);
        }
        printf(";\n");
    }
    printf("\n\n");
}

// Tipo de función para las operaciones de matriz
typedef void (*MatrixOperation)(int n, double* A, double* B, double* C);

int main(int argc, char* argv[]) {
    if (argc < 3) {
        printf("Uso: %s <n> <samples>\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]); // Tamaño de la matriz
    int samples = atoi(argv[2]); // Número de muestras

    // Definir las versiones y sus nombres
    MatrixOperation versions[] = {
        ProductMat_a,
        ProductMat_b,
        ProductMat_c,
        ProductMat_d,
        ProductMat_e,
        ProductMat_f
    };
    char versionNames[] = {'A', 'B', 'C', 'D', 'E', 'F'};
    int numVersions = sizeof(versionNames) / sizeof(versionNames[0]);

    // Asignación de memoria para matrices
    double* A = (double*)malloc(n * n * sizeof(double));
    double* B = (double*)malloc(n * n * sizeof(double));
    double* C = (double*)malloc(n * n * sizeof(double));

    if (!A || !B || !C) {
        printf("Error: No se pudo asignar memoria\n");
        return 1;
    }

    // Inicialización de matrices
    for (int i = 0; i < n * n; i++) {
        A[i] = 2.0;
        B[i] = 4.0;
    }

    printf("ver\ttypeData\tISA\t#sample\tn\ttime(s)\tNormalized(ns)\n");

    // Ejecutar todas las versiones
    for (int v = 0; v < numVersions; v++) {
        for (int s = 0; s < samples; s++) {
            // Reiniciar matriz C
            memset(C, 0, n * n * sizeof(double));

            clock_t start = clock();
            versions[v](n, A, B, C);
            clock_t end = clock();

            double seconds = (double)(end - start) / CLOCKS_PER_SEC;
            double timeNormalized = (seconds * 1.0e9) / ((double)n * n * n);

            printf("C++_ver(%c)\tdouble\tx64\t%05d\t%05d\t%.4f\t%.4f\n",
                   versionNames[v], s, n, seconds, timeNormalized);
        }
    }

    // Imprimir matrices si hay un tercer argumento
    if (argc > 3) {
        PrintMat(n, A);
        PrintMat(n, B);
        PrintMat(n, C);
    }

    // Liberar memoria
    free(A);
    free(B);
    free(C);

    return 0;
}