#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

// counter es global y long long porque con n = 100000 el conteo llega a
// 4.25 * 10^10, que no cabe en un int. Asi tambien se puede imprimir al final.
long long counter = 0;

// Programa del enunciado (Problema 1)
void function(int n) {
    int i, j, k;
    counter = 0;
    for (i = n/2; i <= n; i++) {
        for (j = 1; j+n/2 <= n; j++) {
            for (k = 1; k <= n; k = k*2) {
                counter++;
            }
        }
    }
}

// Tiempo de CPU del proceso (usuario + kernel) en segundos.
// A diferencia del reloj, solo avanza mientras el proceso se esta ejecutando,
// asi que sirve para comprobar que la medicion no incluye pausas externas.
// Su resolucion es de ~15.6 ms, por eso no se usa para los n pequenos.
double tiempo_cpu(void) {
    FILETIME creacion, salida, kernel, usuario;
    ULARGE_INTEGER k, u;
    GetProcessTimes(GetCurrentProcess(), &creacion, &salida, &kernel, &usuario);
    k.LowPart = kernel.dwLowDateTime;
    k.HighPart = kernel.dwHighDateTime;
    u.LowPart = usuario.dwLowDateTime;
    u.HighPart = usuario.dwHighDateTime;
    return (k.QuadPart + u.QuadPart) / 1e7; // viene en unidades de 100 ns
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Uso: problema1.exe <n>\n");
        return 1;
    }
    int n = atoi(argv[1]);

    // Temporizador de alta resolucion de Windows
    LARGE_INTEGER freq, inicio, fin;
    QueryPerformanceFrequency(&freq);

    double cpu_inicio = tiempo_cpu();
    QueryPerformanceCounter(&inicio);
    function(n);
    QueryPerformanceCounter(&fin);
    double cpu = tiempo_cpu() - cpu_inicio;

    double tiempo = (double)(fin.QuadPart - inicio.QuadPart) / freq.QuadPart;
    printf("n=%d conteo=%lld tiempo_s=%.9f cpu_s=%.6f\n", n, counter, tiempo, cpu);
    return 0;
}
