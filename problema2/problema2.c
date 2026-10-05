#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

// Solo se usa en el modo "contador"
long long contador = 0;

// Programa del enunciado (Problema 2), sin cambios
void function(int n) {
    if (n <= 1) return;
    int i, j;
    for (i = 1; i <= n; i++) {
        for (j = 1; j <= n; j++) {
            printf("Sequence\n");
            break;
        }
    }
}

// Misma estructura, pero el printf se cambia por contador++
// para medir el costo de los ciclos sin la escritura en pantalla
void function_contador(int n) {
    contador = 0;
    if (n <= 1) return;
    int i, j;
    for (i = 1; i <= n; i++) {
        for (j = 1; j <= n; j++) {
            contador++;
            break;
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
        fprintf(stderr, "Uso: problema2.exe <n> [contador]\n");
        return 1;
    }
    int n = atoi(argv[1]);
    int modo_contador = (argc >= 3 && strcmp(argv[2], "contador") == 0);

    LARGE_INTEGER freq, inicio, fin;
    QueryPerformanceFrequency(&freq);

    double cpu_inicio = tiempo_cpu();
    QueryPerformanceCounter(&inicio);
    if (modo_contador) {
        function_contador(n);
    } else {
        function(n);
        fflush(stdout); // que el tiempo incluya vaciar el buffer de salida
    }
    QueryPerformanceCounter(&fin);
    double cpu = tiempo_cpu() - cpu_inicio;

    double tiempo = (double)(fin.QuadPart - inicio.QuadPart) / freq.QuadPart;

    // El resultado va a stderr para no mezclarse con los "Sequence" de stdout
    if (modo_contador)
        fprintf(stderr, "n=%d modo=contador conteo=%lld tiempo_s=%.9f cpu_s=%.6f\n", n, contador, tiempo, cpu);
    else
        fprintf(stderr, "n=%d modo=printf tiempo_s=%.9f cpu_s=%.6f\n", n, tiempo, cpu);
    return 0;
}
