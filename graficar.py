# Lee problemaX/salida/tiempos.csv y genera para cada problema:
#   - problemaX/salida/tabla.md     (tabla n vs tiempo)
#   - problemaX/salida/grafica.png  (grafica n vs tiempo, escala lineal y log-log)
#
# Uso:  python graficar.py            (los tres problemas)
#       python graficar.py 1          (solo los problemas indicados)

import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VALORES_N = [1, 10, 100, 1000, 10000, 100000, 1000000]
CARPETA = os.path.dirname(os.path.abspath(__file__))

COMPLEJIDAD = {1: "O(n² log n)", 2: "O(n)", 3: "O(n²)"}
NOMBRE_MODO = {
    "sin_printf": "tiempo medido",
    "printf": "original (con printf)",
    "contador": "printf reemplazado por contador",
}
# color y marcador por modo (dos formas distintas para no depender solo del color)
ESTILO = {
    "sin_printf": ("#2a78d6", "o"),
    "printf": ("#2a78d6", "o"),
    "contador": ("#eb6834", "s"),
}
FONDO = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
REJILLA = "#e4e3df"

# Mismo criterio que profiling.py: si en una corrida de 1 s o mas el reloj
# supera al tiempo de CPU en mas de un 5 %, el proceso estuvo detenido
# (por ejemplo, el equipo entro en espera) y se reporta el tiempo de CPU
UMBRAL_REPETIR = 1.0
TOLERANCIA_CPU = 0.05


def tiempo_reportado(tiempo, cpu):
    # Devuelve (tiempo que se reporta, True si se uso el tiempo de CPU)
    if tiempo >= UMBRAL_REPETIR and (tiempo - cpu) / tiempo > TOLERANCIA_CPU:
        return cpu, True
    return tiempo, False


def leer_csv(problema):
    ruta = os.path.join(CARPETA, f"problema{problema}", "salida", "tiempos.csv")
    datos = {}  # modo -> {n: (tiempo, conteo, repeticiones, cpu)}
    with open(ruta, newline="") as f:
        for fila in csv.DictReader(f):
            datos.setdefault(fila["modo"], {})[int(fila["n"])] = (
                float(fila["tiempo_s"]), fila["conteo"], fila["repeticiones"],
                float(fila["cpu_s"]))
    return datos


def escribir_tabla(problema, datos):
    modos = list(datos.keys())
    lineas = [f"# Problema {problema}: tamaño de input vs. tiempo de ejecución", ""]
    lineas.append(f"Complejidad teórica: **{COMPLEJIDAD[problema]}**. "
                  "Tiempos en segundos. El tiempo reportado es el de reloj, medido con "
                  "QueryPerformanceCounter (resolución 0.1 µs). El tiempo de CPU se mide con "
                  "GetProcessTimes (resolución ~15.6 ms) y sirve para comprobar que el proceso "
                  "no estuvo detenido durante la medición.")
    lineas.append("")

    encabezado = "| n |"
    separador = "|---:|"
    for modo in modos:
        encabezado += f" Tiempo (s) — {NOMBRE_MODO[modo]} | Tiempo CPU (s) |"
        separador += "---:|---:|"
    encabezado += " Iteraciones del ciclo interno |"
    separador += "---:|"
    lineas += [encabezado, separador]

    notas_cpu = []
    for n in VALORES_N:
        fila = f"| {n:,} |".replace(",", " ")
        conteo = ""
        for modo in modos:
            if n in datos[modo]:
                tiempo, c, _, cpu = datos[modo][n]
                valor, usa_cpu = tiempo_reportado(tiempo, cpu)
                if usa_cpu:
                    fila += f" {valor:.7f} (CPU)\\* | {cpu:.3f} |"
                    notas_cpu.append((n, tiempo, cpu))
                else:
                    fila += f" {valor:.7f} | {cpu:.3f} |"
                conteo = c or conteo
            else:
                fila += " no ejecutado (no viable) | — |"
        if conteo:
            conteo = f"{int(conteo):,}".replace(",", " ")
        fila += f" {conteo} |"
        lineas.append(fila)

    lineas.append("")
    lineas.append("Cuando la corrida tardó menos de 1 s se repitió 5 veces y se reporta la mediana. "
                  "Un tiempo de 0.0000000 significa que fue menor a la resolución del temporizador.")
    for n, tiempo, cpu in notas_cpu:
        n_texto = f"{n:,}".replace(",", " ")
        lineas.append("")
        lineas.append(f"\\* Para n = {n_texto} se reporta el **tiempo de CPU** ({cpu:.2f} s). "
                      f"El reloj marcó {tiempo:.2f} s porque durante la corrida el equipo entró "
                      f"en modo de espera unos {tiempo - cpu:.0f} s y el programa quedó congelado; "
                      "ese tiempo no corresponde al algoritmo. En los demás n el reloj y la CPU "
                      "coinciden, así que los valores son comparables.")
    if "printf" in modos and len(datos["printf"]) < len(VALORES_N):
        lineas.append("")
        lineas.append("La versión con printf y n = 1 000 000 no se ejecutó: son más de 8 × 10¹⁰ "
                      "llamadas a printf (~0.5 µs cada una con la salida a NUL), unas 12 horas.")

    ruta = os.path.join(CARPETA, f"problema{problema}", "salida", "tabla.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Tabla guardada en {ruta}")


def preparar_ejes(ax, titulo):
    ax.set_facecolor(FONDO)
    ax.set_title(titulo, color=TEXTO, fontsize=11)
    ax.set_xlabel("Tamaño de input n", color=TEXTO_2)
    ax.set_ylabel("Tiempo de ejecución (segundos)", color=TEXTO_2)
    ax.grid(True, color=REJILLA, linewidth=0.8)
    ax.tick_params(colors=TEXTO_2)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)


def graficar(problema, datos):
    fig, (lineal, loglog) = plt.subplots(1, 2, figsize=(13, 5.2), facecolor=FONDO)
    fig.suptitle(f"Problema {problema}: tamaño de input vs. tiempo de ejecución "
                 f"(complejidad teórica {COMPLEJIDAD[problema]})",
                 color=TEXTO, fontsize=13, fontweight="bold")

    preparar_ejes(lineal, "Escala lineal")
    preparar_ejes(loglog, "Escala logarítmica (ambos ejes)")

    hay_ceros = False
    hay_cpu = False
    for modo, puntos in datos.items():
        color, marcador = ESTILO[modo]
        ns = sorted(puntos)
        reportados = [tiempo_reportado(puntos[n][0], puntos[n][3]) for n in ns]
        ts = [valor for valor, _ in reportados]
        etiqueta = NOMBRE_MODO[modo]

        lineal.plot(ns, ts, color=color, marker=marcador, markersize=8,
                    linewidth=2, label=etiqueta)

        # En escala log no se puede dibujar un tiempo de 0
        ns_log = [n for n, t in zip(ns, ts) if t > 0]
        ts_log = [t for t in ts if t > 0]
        hay_ceros = hay_ceros or len(ns_log) < len(ns)
        loglog.plot(ns_log, ts_log, color=color, marker=marcador, markersize=8,
                    linewidth=2, label=etiqueta)

        # Los puntos donde se uso el tiempo de CPU se marcan con un anillo y una nota
        for n, (valor, usa_cpu) in zip(ns, reportados):
            if usa_cpu:
                hay_cpu = True
                for ax in (lineal, loglog):
                    ax.plot([n], [valor], marker="o", markersize=15, fillstyle="none",
                            color=TEXTO_2, linewidth=0)
                    ax.annotate("tiempo de CPU *", (n, valor), textcoords="offset points",
                                xytext=(-12, -4), ha="right", va="top", color=TEXTO_2, fontsize=9)

    lineal.set_xticks([0, 200000, 400000, 600000, 800000, 1000000])
    lineal.set_xticklabels(["0", "200 000", "400 000", "600 000", "800 000", "1 000 000"])

    loglog.set_xscale("log")
    loglog.set_yscale("log")
    loglog.set_xticks(VALORES_N)
    loglog.set_xticklabels(["1", "10", "100", "1 000", "10 000", "100 000", "1 000 000"])
    loglog.minorticks_off()

    if len(datos) > 1:
        lineal.legend(frameon=False, labelcolor=TEXTO_2)
        loglog.legend(frameon=False, labelcolor=TEXTO_2)

    nota = "Valores de n medidos: 1, 10, 100, 1 000, 10 000, 100 000 y 1 000 000."
    if "printf" in datos and len(datos["printf"]) < len(VALORES_N):
        nota += " La versión con printf no se midió con n = 1 000 000 (no viable)."
    if hay_cpu:
        nota += ("\n* En ese punto se usa el tiempo de CPU: el equipo entró en espera durante "
                 "la corrida y el reloj incluye ese tiempo (ver tabla.md).")
    if hay_ceros:
        nota += " En escala log se omiten los tiempos iguales a 0 (menores a 0.1 µs)."
    fig.text(0.5, 0.01, nota, ha="center", color=TEXTO_2, fontsize=9)

    fig.tight_layout(rect=(0, 0.07 if hay_cpu else 0.04, 1, 0.94))
    ruta = os.path.join(CARPETA, f"problema{problema}", "salida", "grafica.png")
    fig.savefig(ruta, dpi=150, facecolor=FONDO)
    plt.close(fig)
    print(f"Grafica guardada en {ruta}")


if __name__ == "__main__":
    problemas = [int(p) for p in sys.argv[1:]] or [1, 2, 3]
    for p in problemas:
        datos = leer_csv(p)
        escribir_tabla(p, datos)
        graficar(p, datos)
