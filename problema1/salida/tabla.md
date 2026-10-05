# Problema 1: tamaño de input vs. tiempo de ejecución

Complejidad teórica: **O(n² log n)**. Tiempos en segundos. El tiempo reportado es el de reloj, medido con QueryPerformanceCounter (resolución 0.1 µs). El tiempo de CPU se mide con GetProcessTimes (resolución ~15.6 ms) y sirve para comprobar que el proceso no estuvo detenido durante la medición.

| n | Tiempo (s) — tiempo medido | Tiempo CPU (s) | Iteraciones del ciclo interno |
|---:|---:|---:|---:|
| 1 | 0.0000001 | 0.000 | 2 |
| 10 | 0.0000003 | 0.000 | 120 |
| 100 | 0.0000226 | 0.000 | 17 850 |
| 1 000 | 0.0031283 | 0.000 | 2 505 000 |
| 10 000 | 0.4426432 | 0.438 | 350 070 000 |
| 100 000 | 54.1365546 | 53.828 | 42 500 850 000 |
| 1 000 000 | 6265.6406250 (CPU)\* | 6265.641 | 5 000 010 000 000 |

Cuando la corrida tardó menos de 1 s se repitió 5 veces y se reporta la mediana. Un tiempo de 0.0000000 significa que fue menor a la resolución del temporizador.

\* Para n = 1 000 000 se reporta el **tiempo de CPU** (6265.64 s). El reloj marcó 6873.10 s porque durante la corrida el equipo entró en modo de espera unos 607 s y el programa quedó congelado; ese tiempo no corresponde al algoritmo. En los demás n el reloj y la CPU coinciden, así que los valores son comparables.
