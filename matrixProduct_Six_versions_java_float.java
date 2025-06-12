import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;

// Implementación en Java para float (32 bits)
// Adaptado de https://inst.eecs.berkeley.edu/~cs61c/fa12/labs/07/

public class MatrixProductFloat {
    // Versión ijk
    public static void productMatA(int n, float[] A, float[] B, float[] C) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                float sum = 0;
                for (int k = 0; k < n; k++) {
                    sum += A[i + k * n] * B[k + j * n]; // C[i][j] += A[i][k] * B[k][j]
                }
                C[i + j * n] += sum;
            }
        }
    }

    // Versión jik
    public static void productMatB(int n, float[] A, float[] B, float[] C) {
        for (int j = 0; j < n; j++) {
            for (int i = 0; i < n; i++) {
                float sum = 0;
                for (int k = 0; k < n; k++) {
                    sum += A[i + k * n] * B[k + j * n];
                }
                C[i + j * n] += sum;
            }
        }
    }

    // Versión jki
    public static void productMatC(int n, float[] A, float[] B, float[] C) {
        for (int j = 0; j < n; j++) {
            for (int k = 0; k < n; k++) {
                float r = B[k + j * n];
                for (int i = 0; i < n; i++) {
                    C[i + j * n] += A[i + k * n] * r;
                }
            }
        }
    }

    // Versión kji
    public static void productMatD(int n, float[] A, float[] B, float[] C) {
        for (int k = 0; k < n; k++) {
            for (int j = 0; j < n; j++) {
                float r = B[k + j * n];
                for (int i = 0; i < n; i++) {
                    C[i + j * n] += A[i + k * n] * r;
                }
            }
        }
    }

    // Versión kij
    public static void productMatE(int n, float[] A, float[] B, float[] C) {
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                float r = A[i + k * n];
                for (int j = 0; j < n; j++) {
                    C[i + j * n] += r * B[k + j * n];
                }
            }
        }
    }

    // Versión ikj
    public static void productMatF(int n, float[] A, float[] B, float[] C) {
        for (int i = 0; i < n; i++) {
            for (int k = 0; k < n; k++) {
                float r = A[i + k * n];
                for (int j = 0; j < n; j++) {
                    C[i + j * n] += r * B[k + j * n];
                }
            }
        }
    }

    // Función para imprimir matrices (opcional)
    public static void printMat(int n, float[] M) {
        for (int j = 0; j < n; j++) {
            for (int i = 0; i < n; i++) {
                System.out.printf("%.3f ", M[i + j * n]);
            }
            System.out.println(";");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Uso: java MatrixProductFloat <n> <samples>");
            return;
        }

        int n = Integer.parseInt(args[0]); // Tamaño de la matriz
        int samples = Integer.parseInt(args[1]); // Número de muestras

        // Inicializar matrices
        float[] A = new float[n * n];
        float[] B = new float[n * n];
        float[] C = new float[n * n];
        Arrays.fill(A, 2.0f);
        Arrays.fill(B, 4.0f);
        Arrays.fill(C, 0.0f);

        try (FileWriter fw = new FileWriter("ReportS2_LHW00.txt", true)) {
            System.out.println("ver\ttypeData\tISA\t#sample\tn\ttime(s)\tNormalized(ns)");
            for (int s = 0; s < samples; s++) {
                Arrays.fill(C, 0.0f);
                long start = System.nanoTime();
                productMatF(n, A, B, C); // Usamos versión F como ejemplo
                long end = System.nanoTime();

                double seconds = (end - start) / 1.0e9;
                double timeNormalized = (seconds * 1.0e9) / (n * n * n);
                String result = String.format("Java_ver(f)\tfloat\tx64\t%05d\t%05d\t%.4f\t%.4f\n",
                        s, n, seconds, timeNormalized);
                System.out.print(result);
                fw.write(result);
            }

            // Imprimir matrices si hay un tercer argumento
            if (args.length > 2) {
                printMat(n, A);
                printMat(n, B);
                printMat(n, C);
            }
        } catch (IOException e) {
            System.out.println("Error al escribir en el archivo: " + e.getMessage());
        }
    }
}