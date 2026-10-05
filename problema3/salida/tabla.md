# Problema 3: tamaño de input vs. tiempo de ejecución

Complejidad teórica: **O(n²)**. Tiempos en segundos. El tiempo reportado es el de reloj, medido con QueryPerformanceCounter (resolución 0.1 µs). El tiempo de CPU se mide con GetProcessTimes (resolución ~15.6 ms) y sirve para comprobar que el proceso no estuvo detenido durante la medición.

| n | Tiempo (s) — original (con printf) | Tiempo CPU (s) | Tiempo (s) — printf reemplazado por contador | Tiempo CPU (s) | Iteraciones del ciclo interno |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.0000002 | 0.000 | 0.0000001 | 0.000 | 0 |
| 10 | 0.0000160 | 0.000 | 0.0000001 | 0.000 | 9 |
| 100 | 0.0004361 | 0.000 | 0.0000012 | 0.000 | 825 |
| 1 000 | 0.0438704 | 0.047 | 0.0001047 | 0.000 | 83 250 |
| 10 000 | 4.3685680 | 4.359 | 0.0103014 | 0.016 | 8 332 500 |
| 100 000 | 431.9627476 | 430.297 | 1.0515676 | 1.062 | 833 325 000 |
| 1 000 000 | no ejecutado (no viable) | — | 104.9981057 | 104.609 | 83 333 250 000 |

Cuando la corrida tardó menos de 1 s se repitió 5 veces y se reporta la mediana. Un tiempo de 0.0000000 significa que fue menor a la resolución del temporizador.

La versión con printf y n = 1 000 000 no se ejecutó: son más de 8 × 10¹⁰ llamadas a printf (~0.5 µs cada una con la salida a NUL), unas 12 horas.
