# Laboratorio 8 - Teoría de la Computación

Análisis de complejidad de algoritmos (notación Big-O) y medición real de tiempos
de ejecución mediante profiling.

| Problema | Contenido | Dónde está |
|---|---|---|
| 1 | Big-O de tres ciclos anidados + implementación y profiling | `problema1/`, PDF |
| 2 | Big-O de dos ciclos con `break` + implementación y profiling | `problema2/`, PDF |
| 3 | Big-O de dos ciclos con `n/3` y `j += 4` + implementación y profiling | `problema3/`, PDF |
| 4 | Mejor, promedio y peor caso de búsqueda lineal, búsqueda binaria y Quick Sort | PDF |
| 5 | Verdadero/falso con justificación | PDF |

Las respuestas teóricas (parte a de los problemas 1–3 y los problemas 4 y 5) están en
[`respuestas/respuestas.pdf`](respuestas/respuestas.pdf).

## Video

https://youtu.be/Djp8UFTu-d8

## Requisitos

- Windows 10/11 (los programas usan `QueryPerformanceCounter` y `GetProcessTimes` de `windows.h`).
- **gcc** (probado con gcc 16.1 de MSYS2 UCRT64), que incluye **gprof** (GNU Binutils 2.46).
- **Python 3** (probado con 3.14) con **matplotlib**, para las tablas y gráficas.
- **fpdf2** (`pip install fpdf2`), solo si se quiere regenerar el PDF de respuestas.

Todos los comandos de este README se ejecutan en **PowerShell** desde la carpeta raíz
del repositorio.

> En Git Bash, gcc puede fallar sin mostrar ningún error si `/mingw64/bin` de Git
> aparece en el PATH antes que MSYS2. En ese caso hay que poner MSYS2 primero:
> `PATH="/c/msys64/ucrt64/bin:$PATH" gcc ...`

## Estructura

```
Lab8/
├── README.md
├── profiling.py            ejecuta los programas con cada n y guarda los tiempos (CSV)
├── graficar.py             genera las tablas y gráficas a partir de los CSV
├── problema1/
│   ├── problema1.c
│   └── salida/             tiempos.csv, tabla.md, grafica.png, gprof.txt
├── problema2/
│   ├── problema2.c
│   └── salida/             tiempos.csv, tabla.md, grafica.png, gprof_printf.txt, gprof_contador.txt
├── problema3/
│   ├── problema3.c
│   └── salida/             (igual que problema2)
└── respuestas/
    ├── respuestas.pdf      desarrollo teórico + resultados
    └── generar_pdf.py      script que genera el PDF
```

## Compilación

```
gcc -Wall -O0 problema1\problema1.c -o problema1\problema1.exe
gcc -Wall -O0 problema2\problema2.c -o problema2\problema2.exe
gcc -Wall -O0 problema3\problema3.c -o problema3\problema3.exe
```

Se compila con `-O0` a propósito: con optimización, gcc puede eliminar o simplificar
los ciclos (por ejemplo, el del problema 1 no produce ninguna salida) y el tiempo
medido ya no correspondería al algoritmo.

## Ejecución

Cada programa recibe `n` como argumento, ejecuta `function(n)` y muestra el tiempo.

```
.\problema1\problema1.exe <n>
.\problema2\problema2.exe <n> [contador]
.\problema3\problema3.exe <n> [contador]
```

Ejemplos:

```
.\problema1\problema1.exe 1000
.\problema2\problema2.exe 3
.\problema2\problema2.exe 1000000 contador
.\problema3\problema3.exe 10
.\problema3\problema3.exe 1000 contador
```

Salida de ejemplo:

```
> .\problema1\problema1.exe 1000
n=1000 conteo=2505000 tiempo_s=0.003125600 cpu_s=0.000000

> .\problema2\problema2.exe 3
Sequence
Sequence
Sequence
n=3 modo=printf tiempo_s=0.000040600 cpu_s=0.000000
```

- `conteo`: veces que se ejecutó el cuerpo del ciclo más interno. Coincide con la
  fórmula exacta obtenida en el análisis (ver PDF).
- `tiempo_s`: tiempo de reloj de `function(n)`, medido con `QueryPerformanceCounter`
  (resolución 0.1 µs).
- `cpu_s`: tiempo de CPU del proceso, medido con `GetProcessTimes` (resolución ~15.6 ms).
  Sirve para comprobar que el proceso no estuvo detenido durante la medición.

### Modos de los problemas 2 y 3

Los programas 2 y 3 imprimen `"Sequence"` dentro del ciclo. Para que el profiling mida
el algoritmo y no la velocidad de la consola, cada programa tiene dos versiones:

- **Sin argumento extra (original):** ejecuta el código del enunciado sin cambios, con
  `printf`. Al hacer profiling, la salida estándar se manda a `NUL`.
- **Con `contador`:** misma estructura de ciclos, pero el `printf` se reemplaza por
  `contador++`. Mide el costo de los ciclos sin entrada/salida.

En estos programas el resultado (`n=... tiempo_s=...`) se escribe en `stderr` para no
mezclarse con los `"Sequence"` de `stdout`.

## Profiling

### Tiempos de las tablas y gráficas

```
python profiling.py          # los tres problemas
python profiling.py 2 3      # solo los problemas indicados
python graficar.py           # genera tablas y gráficas desde los CSV
```

`profiling.py` ejecuta cada programa con n = 1, 10, 100, 1 000, 10 000, 100 000 y
1 000 000, manda los `"Sequence"` a `NUL` y guarda los resultados en
`problemaX/salida/tiempos.csv`:

- Si una corrida tarda menos de 1 s, se repite 5 veces y se guarda la mediana.
- Mientras mide, le pide a Windows que no suspenda el equipo ni apague la pantalla.
  Aun así, hay que dejar el equipo conectado y con la tapa abierta.
- Si en una corrida de más de 1 s el reloj supera al tiempo de CPU en más de un 5 %,
  muestra un aviso: el proceso estuvo detenido y el tiempo de reloj no es confiable.

**Duración aproximada:** problema 1 ≈ 1 h 50 min (n = 1 000 000 hace 5 × 10¹² iteraciones),
problema 3 ≈ 10 min, problema 2 unos segundos.

La versión con `printf` del problema 3 no se ejecuta con n = 1 000 000: serían
83 333 250 000 llamadas a `printf` (≈ 0.5 µs cada una aun con la salida a `NUL`),
unas 12 horas. La versión con contador sí se mide con todos los valores de n.

### gprof

gprof se usó como profiler complementario. Ejemplo para el problema 1, desde su carpeta:

```
cd problema1
gcc -O0 -pg -no-pie problema1.c -o problema1_pg.exe
.\problema1_pg.exe 100000
gprof -b problema1_pg.exe gmon.out | Out-File -Encoding utf8 salida\gprof.txt
cd ..
```

Para los problemas 2 y 3 en modo `printf`, la salida se manda a `NUL` con `cmd`:

```
cd problema3
gcc -O0 -pg -no-pie problema3.c -o problema3_pg.exe
cmd /c ".\problema3_pg.exe 10000 > NUL"
gprof -b problema3_pg.exe gmon.out | Out-File -Encoding utf8 salida\gprof_printf.txt
.\problema3_pg.exe 100000 contador
gprof -b problema3_pg.exe gmon.out | Out-File -Encoding utf8 salida\gprof_contador.txt
cd ..
```

Notas sobre gprof en Windows:

- Es necesario `-no-pie`; sin esa opción el reporte sale vacío.
- gprof muestrea cada 10 ms, así que no sirve para los n pequeños y en Windows
  subestima el tiempo (con n = 100 000 en el problema 1 muestreó 32 s contra 53.6 s
  reales). Por eso las tablas usan `QueryPerformanceCounter`.
- En modo `printf`, gprof atribuye 0 s a `function`: casi todo el tiempo se pasa dentro
  de `printf`, que está en una DLL del sistema que gprof no muestrea.

Reportes usados: problema 1 con n = 100 000; problema 2 con n = 1 000 000 (ambos modos);
problema 3 con n = 10 000 (`printf`) y n = 100 000 (contador).

## Resultados

| Problema | Complejidad | Tabla | Gráfica | gprof |
|---|---|---|---|---|
| 1 | O(n² log n) | [tabla.md](problema1/salida/tabla.md) | [grafica.png](problema1/salida/grafica.png) | [gprof.txt](problema1/salida/gprof.txt) |
| 2 | O(n) | [tabla.md](problema2/salida/tabla.md) | [grafica.png](problema2/salida/grafica.png) | [printf](problema2/salida/gprof_printf.txt), [contador](problema2/salida/gprof_contador.txt) |
| 3 | O(n²) | [tabla.md](problema3/salida/tabla.md) | [grafica.png](problema3/salida/grafica.png) | [printf](problema3/salida/gprof_printf.txt), [contador](problema3/salida/gprof_contador.txt) |

Cada gráfica muestra los mismos datos en escala lineal y en escala log-log. En la escala
log-log la pendiente de la recta indica el exponente: ≈ 1 en el problema 2, ≈ 2 en el
problema 3 y ≈ 2 (más el aporte del log n) en el problema 1.

**Nota sobre el problema 1 con n = 1 000 000:** durante esa corrida el equipo entró en
modo de espera unos 607 s y el programa quedó congelado. El reloj marcó 6 873.10 s,
pero el tiempo de CPU fue 6 265.64 s. La tabla y la gráfica reportan el tiempo de CPU
para ese punto y lo indican con un asterisco. En el CSV se conservan ambos valores.

## Regenerar el PDF

```
pip install fpdf2
python respuestas\generar_pdf.py
```

Las tablas de tiempos del PDF se leen de los CSV, así que hay que correr
`profiling.py` antes. El script usa las fuentes Calibri, Consolas y Segoe UI Symbol
de Windows.
