# Ejecuta los programas de los problemas 1, 2 y 3 con cada valor de n
# y guarda los tiempos medidos en problemaX/salida/tiempos.csv
#
# Uso:  python profiling.py            (los tres problemas)
#       python profiling.py 2 3        (solo los problemas indicados)

import csv
import ctypes
import os
import statistics
import subprocess
import sys

VALORES_N = [1, 10, 100, 1000, 10000, 100000, 1000000]

# Si una corrida tarda menos de 1 s se repite 5 veces y se usa la mediana,
# porque los tiempos muy pequenos varian bastante entre ejecuciones
REPETICIONES = 5
UMBRAL_REPETIR = 1.0

# En el problema 3 con printf, n = 1000000 son ~8.3 * 10^10 llamadas a printf
# (~12 horas con la salida a NUL), asi que ese caso no se ejecuta
MAX_N_PRINTF = {2: 1000000, 3: 100000}

# Si en una corrida de mas de 1 s el tiempo de reloj supera al de CPU en mas
# de un 5 %, el proceso estuvo detenido (suspension, otra carga, etc.)
TOLERANCIA_CPU = 0.05

CARPETA = os.path.dirname(os.path.abspath(__file__))


def evitar_suspension(activar):
    # Le pide a Windows que no suspenda el equipo ni apague la pantalla mientras
    # se mide (en equipos con Modern Standby, apagar la pantalla ya pone el
    # sistema en espera y congela los programas). No cambia la configuracion
    # de energia; se quita al terminar.
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    if activar:
        estado = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    else:
        estado = ES_CONTINUOUS
    ctypes.windll.kernel32.SetThreadExecutionState(estado)


def ejecutar(problema, n, modo):
    exe = os.path.join(CARPETA, f"problema{problema}", f"problema{problema}.exe")
    args = [exe, str(n)]
    if modo == "contador":
        args.append("contador")

    # Los "Sequence" de printf se mandan a NUL; el resultado del programa
    # sale por stdout en el problema 1 y por stderr en los problemas 2 y 3
    if problema == 1:
        r = subprocess.run(args, stdout=subprocess.PIPE, text=True, check=True)
        linea = r.stdout
    else:
        r = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                           text=True, check=True)
        linea = r.stderr

    # La linea tiene la forma "n=10 modo=contador conteo=9 tiempo_s=0.000000100 cpu_s=0.000000"
    datos = dict(parte.split("=") for parte in linea.split())
    return datos.get("conteo", ""), float(datos["tiempo_s"]), float(datos["cpu_s"])


def medir(problema, n, modo):
    conteo, t, cpu = ejecutar(problema, n, modo)
    tiempos = [t]
    cpus = [cpu]
    if t < UMBRAL_REPETIR:
        for _ in range(REPETICIONES - 1):
            _, t, cpu = ejecutar(problema, n, modo)
            tiempos.append(t)
            cpus.append(cpu)
    return conteo, statistics.median(tiempos), statistics.median(cpus), len(tiempos)


def perfilar(problema):
    salida = os.path.join(CARPETA, f"problema{problema}", "salida")
    os.makedirs(salida, exist_ok=True)
    ruta_csv = os.path.join(salida, "tiempos.csv")

    modos = ["sin_printf"] if problema == 1 else ["printf", "contador"]

    with open(ruta_csv, "w", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["n", "modo", "conteo", "tiempo_s", "cpu_s", "repeticiones"])

        for modo in modos:
            for n in VALORES_N:
                if modo == "printf" and n > MAX_N_PRINTF[problema]:
                    print(f"Problema {problema}  modo={modo:<10} n={n:<8} no se ejecuta (no viable)", flush=True)
                    continue
                conteo, tiempo, cpu, reps = medir(problema, n, modo)
                escritor.writerow([n, modo, conteo, f"{tiempo:.9f}", f"{cpu:.6f}", reps])
                f.flush()  # para no perder resultados si se interrumpe
                print(f"Problema {problema}  modo={modo:<10} n={n:<8} tiempo={tiempo:.9f} s  "
                      f"cpu={cpu:.3f} s  ({reps} rep.)", flush=True)
                if tiempo >= UMBRAL_REPETIR and (tiempo - cpu) / tiempo > TOLERANCIA_CPU:
                    print(f"  AVISO: el reloj supera al tiempo de CPU en mas de un "
                          f"{TOLERANCIA_CPU:.0%}; la medicion pudo incluir pausas externas", flush=True)

    print(f"Resultados guardados en {ruta_csv}", flush=True)


if __name__ == "__main__":
    problemas = [int(p) for p in sys.argv[1:]] or [1, 2, 3]
    evitar_suspension(True)
    try:
        for p in problemas:
            perfilar(p)
    finally:
        evitar_suspension(False)
