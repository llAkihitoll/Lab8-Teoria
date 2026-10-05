# Problema 2: tamaño de input vs. tiempo de ejecución

Complejidad teórica: **O(n)**. Tiempos en segundos. El tiempo reportado es el de reloj, medido con QueryPerformanceCounter (resolución 0.1 µs). El tiempo de CPU se mide con GetProcessTimes (resolución ~15.6 ms) y sirve para comprobar que el proceso no estuvo detenido durante la medición.

| n | Tiempo (s) — original (con printf) | Tiempo CPU (s) | Tiempo (s) — printf reemplazado por contador | Tiempo CPU (s) | Iteraciones del ciclo interno |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.0000001 | 0.000 | 0.0000000 | 0.000 | 0 |
| 10 | 0.0000159 | 0.000 | 0.0000001 | 0.000 | 10 |
| 100 | 0.0000615 | 0.000 | 0.0000002 | 0.000 | 100 |
| 1 000 | 0.0005241 | 0.000 | 0.0000013 | 0.000 | 1 000 |
| 10 000 | 0.0051749 | 0.000 | 0.0000124 | 0.000 | 10 000 |
| 100 000 | 0.0511648 | 0.047 | 0.0001231 | 0.000 | 100 000 |
| 1 000 000 | 0.5279288 | 0.531 | 0.0012307 | 0.000 | 1 000 000 |

Cuando la corrida tardó menos de 1 s se repitió 5 veces y se reporta la mediana. Un tiempo de 0.0000000 significa que fue menor a la resolución del temporizador.
