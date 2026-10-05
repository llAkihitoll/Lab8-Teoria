# Genera respuestas/respuestas.pdf con el desarrollo teorico del laboratorio:
#   - Problemas 1, 2 y 3: parte a (Big-O) y resumen de la parte b (tabla y grafica)
#   - Problema 4: mejor, promedio y peor caso
#   - Problema 5: verdadero / falso
#
# Uso:  python respuestas/generar_pdf.py
# Requiere: pip install fpdf2  (y haber corrido profiling.py y graficar.py antes)

import logging
import os
import sys

from fpdf import FPDF
from fpdf.fonts import FontFace

CARPETA = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(CARPETA)
sys.path.insert(0, RAIZ)
from graficar import leer_csv, tiempo_reportado, NOMBRE_MODO  # noqa: E402

FUENTES = r"C:\Windows\Fonts"

# fontTools avisa de tablas que no recorta al incrustar las fuentes; no afecta al PDF
logging.getLogger("fontTools.subset").setLevel(logging.ERROR)


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("texto", "", 8)
            self.set_text_color(110)
            self.cell(0, 6, "Teoría de la Computación — Laboratorio 8", align="R")
            self.ln(8)
            self.set_text_color(0)

    def footer(self):
        self.set_y(-14)
        self.set_font("texto", "", 8)
        self.set_text_color(110)
        self.cell(0, 6, f"{self.page_no()}", align="C")
        self.set_text_color(0)


pdf = PDF(format="A4")
pdf.set_margins(20, 18, 20)
pdf.set_auto_page_break(True, margin=18)
pdf.add_font("texto", "", os.path.join(FUENTES, "calibri.ttf"))
pdf.add_font("texto", "B", os.path.join(FUENTES, "calibrib.ttf"))
pdf.add_font("texto", "I", os.path.join(FUENTES, "calibrii.ttf"))
pdf.add_font("mono", "", os.path.join(FUENTES, "consola.ttf"))
pdf.add_font("mono", "B", os.path.join(FUENTES, "consolab.ttf"))
# Para los simbolos que no tienen Calibri ni Consolas (⌊ ⌋ ⌈ ⌉ ∎ ⇔)
pdf.add_font("simbolos", "", os.path.join(FUENTES, "seguisym.ttf"))
pdf.set_fallback_fonts(["simbolos"], exact_match=False)


# ---------- funciones para escribir ----------

def h1(texto):
    pdf.add_page()
    pdf.set_font("texto", "B", 18)
    pdf.cell(0, 10, texto, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(42, 120, 214)
    pdf.set_line_width(0.6)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)


def espacio_minimo(mm):
    # Evita que un titulo quede solo al final de la pagina
    if pdf.get_y() + mm > pdf.h - pdf.b_margin:
        pdf.add_page()


def h2(texto):
    espacio_minimo(35)
    pdf.ln(2)
    pdf.set_font("texto", "B", 14)
    pdf.set_text_color(28, 92, 171)
    pdf.multi_cell(0, 7, texto, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0)
    pdf.ln(1)


def h3(texto):
    espacio_minimo(28)
    pdf.ln(1)
    pdf.set_font("texto", "B", 12)
    pdf.multi_cell(0, 6, texto, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)


def p(texto):
    pdf.set_font("texto", "", 11)
    pdf.multi_cell(0, 5.6, texto, markdown=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def bloque(texto):
    # Bloque de codigo o de desarrollo matematico, con fondo gris
    pdf.set_font("mono", "", 9.5)
    pdf.set_fill_color(244, 244, 242)
    lineas = texto.strip("\n").split("\n")
    alto = 4.6
    if pdf.get_y() + alto * min(len(lineas), 8) > pdf.h - pdf.b_margin:
        pdf.add_page()
    pdf.ln(0.5)
    for linea in lineas:
        pdf.cell(0, alto, "  " + linea, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2.5)


def tabla(encabezado, filas, anchos=None):
    pdf.set_font("texto", "", 9.5)
    pdf.set_draw_color(200)
    with pdf.table(col_widths=anchos, text_align="CENTER", line_height=5.2,
                   first_row_as_headings=True,
                   headings_style=FontFace(emphasis="BOLD", fill_color=(232, 240, 251))) as t:
        fila = t.row()
        for celda in encabezado:
            fila.cell(celda)
        for f in filas:
            fila = t.row()
            for celda in f:
                fila.cell(str(celda))
    pdf.ln(3)


def imagen(ruta):
    ancho = pdf.w - pdf.l_margin - pdf.r_margin
    alto = ancho * 780 / 1950  # proporcion de las graficas generadas
    if pdf.get_y() + alto > pdf.h - pdf.b_margin:
        pdf.add_page()
    pdf.image(ruta, w=ancho)
    pdf.ln(3)


def miles(x):
    return f"{int(x):,}".replace(",", " ")


def tabla_profiling(problema):
    # Tabla n vs tiempo leida directamente de problemaX/salida/tiempos.csv
    datos = leer_csv(problema)
    modos = list(datos.keys())
    encabezado = ["n"]
    for modo in modos:
        if modo == "sin_printf":
            encabezado.append("Tiempo (s)")
        else:
            encabezado.append(f"Tiempo (s)\n{NOMBRE_MODO[modo]}")
    encabezado.append("Iteraciones del\nciclo interno")
    filas = []
    hay_cpu = False
    for n in [1, 10, 100, 1000, 10000, 100000, 1000000]:
        fila = [miles(n)]
        conteo = ""
        for modo in modos:
            if n in datos[modo]:
                tiempo, c, _, cpu = datos[modo][n]
                valor, usa_cpu = tiempo_reportado(tiempo, cpu)
                hay_cpu = hay_cpu or usa_cpu
                fila.append(f"{valor:.7f}" + (" (CPU)*" if usa_cpu else ""))
                conteo = c or conteo
            else:
                fila.append("no ejecutado (no viable)")
        fila.append(miles(conteo) if conteo else "")
        filas.append(fila)
    tabla(encabezado, filas)
    return datos, hay_cpu


# =====================================================================
# Portada
# =====================================================================
pdf.add_page()
pdf.ln(50)
pdf.set_font("texto", "B", 26)
pdf.cell(0, 14, "Laboratorio 8", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("texto", "", 16)
pdf.cell(0, 9, "Teoría de la Computación", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)
pdf.set_font("texto", "", 12)
pdf.cell(0, 7, "Respuestas: análisis de complejidad (Problemas 1–3, parte a),",
         align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "resultados de profiling (parte b) y Problemas 4 y 5",
         align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(70)
pdf.set_font("texto", "", 11)
pdf.multi_cell(0, 6,
               "Notación: en C, n/2 con enteros es división entera, es decir ⌊n/2⌋. "
               "T(n) es el número de veces que se ejecuta la instrucción del ciclo más interno. "
               "En todos los casos se suponen funciones positivas para n suficientemente grande.",
               align="C")


# =====================================================================
# Problema 1
# =====================================================================
h1("Problema 1")
bloque("""
void function(int n) {
    int i, j, k, counter = 0;
    for (i = n/2; i <= n; i++) {
        for (j = 1; j+n/2 <= n; j++) {
            for (k = 1; k <= n; k = k*2) {
                counter++;
            }
        }
    }
}
""")

h2("Parte a: complejidad en Big-O")

h3("Primer ciclo (i)")
bloque("""
i = ⌊n/2⌋, ⌊n/2⌋+1, ..., n
→ n − ⌊n/2⌋ + 1 = ⌈n/2⌉ + 1 iteraciones
""")
p("Ejemplo con n = 10: i = 5, 6, 7, 8, 9, 10 → 6 iteraciones (⌈10/2⌉ + 1 = 6).")

h3("Segundo ciclo (j)")
p("Se despeja la condición del ciclo:")
bloque("""
j + ⌊n/2⌋ ≤ n
j ≤ n − ⌊n/2⌋
j ≤ ⌈n/2⌉

j = 1, 2, ..., ⌈n/2⌉
→ ⌈n/2⌉ iteraciones
""")
p("No depende de i, así que se repite igual en cada vuelta del primer ciclo.")

h3("Tercer ciclo (k)")
p("k se duplica en cada paso:")
bloque("""
k = 1, 2, 4, 8, ..., 2^m        con 2^m ≤ n

2^m ≤ n  →  m ≤ log₂ n  →  m = ⌊log₂ n⌋

Como m empieza en 0:
→ ⌊log₂ n⌋ + 1 iteraciones
""")
p("Ejemplo con n = 10: k = 1, 2, 4, 8 → 4 iteraciones (⌊log₂ 10⌋ + 1 = 3 + 1 = 4). "
  "Este ciclo tampoco depende de i ni de j.")

h3("Combinación de los ciclos anidados")
p("Ningún ciclo depende de las variables de los otros, así que el total es el producto:")
bloque("""
T(n) = (⌈n/2⌉ + 1) · ⌈n/2⌉ · (⌊log₂ n⌋ + 1)
""")

h3("Simplificación")
p("Para n grande, los pisos, techos y el \"+1\" no cambian el orden de crecimiento:")
bloque("""
T(n) ≈ (n/2) · (n/2) · log₂ n
T(n) ≈ (1/4) · n² · log₂ n

Se elimina la constante 1/4:

T(n) = O(n² log n)
""")

h3("Comprobación formal")
p("**Cota superior.** Para n ≥ 2: ⌈n/2⌉ + 1 ≤ n, ⌈n/2⌉ ≤ n y ⌊log₂ n⌋ + 1 ≤ 2·log₂ n.")
bloque("""
T(n) ≤ n · n · 2 log₂ n = 2 · n² log₂ n     (c = 2, n₀ = 2)
""")
p("**Cota inferior.** Cada factor es al menos n/2, n/2 y log₂ n:")
bloque("""
T(n) ≥ (1/4) · n² log₂ n
""")
p("Por lo tanto la cota es justa: **T(n) = Θ(n² log n)**, y en particular **T(n) = O(n² log n)**.")

h3("Valores exactos de counter")
p("El programa implementado imprime el valor final de counter; coincide exactamente con la fórmula:")
tabla(["n", "⌈n/2⌉+1", "⌈n/2⌉", "⌊log₂n⌋+1", "T(n)"], [
    ["1", "2", "1", "1", "2"],
    ["10", "6", "5", "4", "120"],
    ["100", "51", "50", "7", "17 850"],
    ["1 000", "501", "500", "10", "2 505 000"],
    ["10 000", "5 001", "5 000", "14", "350 070 000"],
    ["100 000", "50 001", "50 000", "17", "42 500 850 000"],
    ["1 000 000", "500 001", "500 000", "20", "5 000 010 000 000"],
])

h2("Parte b: profiling")
p("Implementación en C (problema1/problema1.c), compilada con gcc -O0. El tiempo se mide con "
  "QueryPerformanceCounter alrededor de la llamada a function(n). Las corridas de menos de 1 s se "
  "repitieron 5 veces y se reporta la mediana.")
datos1, hay_cpu1 = tabla_profiling(1)
if hay_cpu1:
    p("* Para n = 1 000 000 se reporta el **tiempo de CPU** (GetProcessTimes). Durante esa corrida el "
      "equipo entró en modo de espera unos 607 s y el programa quedó congelado; el reloj marcó "
      "6873.10 s, que no corresponde al algoritmo. En los demás n el reloj y la CPU coinciden.")
imagen(os.path.join(RAIZ, "problema1", "salida", "grafica.png"))
p("**Comparación con la teoría.** Al pasar de n = 10⁵ a n = 10⁶ el tiempo creció ×116.4 "
  "(6265.64 / 53.83). La fórmula predice 5 000 010 000 000 / 42 500 850 000 ≈ ×117.6. "
  "En la gráfica log-log la recta tiene pendiente ≈ 2 (más el leve aporte del log n), "
  "lo que concuerda con O(n² log n).")


# =====================================================================
# Problema 2
# =====================================================================
h1("Problema 2")
bloque("""
void function(int n) {
    if (n <= 1) return;
    int i, j;
    for (i = 1; i <= n; i++) {
        for (j = 1; j <= n; j++) {
            printf("Sequence\\n");
            break;
        }
    }
}
""")

h2("Parte a: complejidad en Big-O")

h3("Caso n ≤ 1")
p("La función retorna de inmediato. Solo se hace una comparación: T(n) = 1 = O(1).")

h3("Primer ciclo (i), para n ≥ 2")
bloque("""
i = 1, 2, ..., n
→ n iteraciones
""")

h3("Segundo ciclo (j): efecto del break")
p("En cada vuelta del ciclo externo, el ciclo interno hace:")
bloque("""
j = 1
¿1 ≤ n?  sí (porque n ≥ 2)
printf("Sequence\\n")
break   → sale del ciclo interno, sin llegar a j++ ni a j = 2
""")
p("El ciclo interno **no** hace n iteraciones: hace **exactamente 1**, sin importar n. "
  "El break solo sale del ciclo interno; el externo continúa con i++.")

h3("Combinación de los ciclos")
p("Cada iteración externa cuesta una cantidad constante c (inicializar j, una comparación, "
  "un printf y el break):")
bloque("""
T(n) = Σ (i=1..n) c
T(n) = c · n

Se elimina la constante c:

T(n) = O(n)
""")
p("Aunque hay dos ciclos anidados, la complejidad **no** es O(n²): el break reduce el ciclo "
  "interno a costo constante. Para n ≥ 2 el printf se ejecuta exactamente n veces, así que "
  "c₁·n ≤ T(n) ≤ c₂·n y **T(n) = Θ(n)**.")

h2("Parte b: profiling")
p("Implementación en C (problema2/problema2.c). Se midieron dos versiones:")
p("• **Original (con printf):** el código del enunciado sin cambios, con la salida estándar "
  "redirigida a NUL para no medir la velocidad de la consola.\n"
  "• **printf reemplazado por contador:** la misma estructura de ciclos, pero el printf se "
  "cambia por contador++. Así se mide el costo de los ciclos sin el costo de entrada/salida.")
tabla_profiling(2)
imagen(os.path.join(RAIZ, "problema2", "salida", "grafica.png"))
p("**Comparación con la teoría.** En ambas versiones el tiempo se multiplica por ≈10 cada vez que n "
  "se multiplica por 10 (por ejemplo 0.0512 s → 0.528 s con printf entre n = 10⁵ y 10⁶). "
  "En la gráfica log-log son rectas de pendiente ≈ 1, que corresponde a O(n).")


# =====================================================================
# Problema 3
# =====================================================================
h1("Problema 3")
bloque("""
void function(int n) {
    int i, j;
    for (i = 1; i <= n/3; i++) {
        for (j = 1; j <= n; j += 4) {
            printf("Sequence\\n");
        }
    }
}
""")

h2("Parte a: complejidad en Big-O")

h3("Primer ciclo (i): efecto de n/3")
bloque("""
i = 1, 2, ..., ⌊n/3⌋
→ ⌊n/3⌋ iteraciones
""")
p("El límite n/3 solo divide el número de iteraciones por 3, una constante, así que el ciclo sigue "
  "siendo lineal. Si n < 3, ⌊n/3⌋ = 0 y el ciclo no se ejecuta (con n = 1 hay 0 impresiones).")

h3("Segundo ciclo (j): efecto de j += 4")
bloque("""
j = 1, 5, 9, ..., 1 + 4t        con 1 + 4t ≤ n

1 + 4t ≤ n  →  t ≤ (n − 1)/4  →  t_max = ⌊(n − 1)/4⌋

Como t empieza en 0:
→ ⌊(n − 1)/4⌋ + 1 iteraciones  ≈  n/4
""")
p("Ejemplo con n = 10: j = 1, 5, 9 → 3 iteraciones (⌊9/4⌋ + 1 = 3). "
  "El paso de 4 también divide el trabajo por una constante; el ciclo sigue siendo lineal.")

h3("Combinación de los ciclos anidados")
p("El ciclo interno no depende de i, así que se multiplica:")
bloque("""
T(n) = ⌊n/3⌋ · (⌊(n − 1)/4⌋ + 1)
""")

h3("Simplificación")
bloque("""
T(n) ≈ (n/3) · (n/4)
T(n) ≈ n²/12

Se elimina la constante 1/12:

T(n) = O(n²)
""")

h3("Comprobación formal")
p("**Cota superior.** ⌊n/3⌋ ≤ n/3 y ⌊(n−1)/4⌋ + 1 ≤ (n+3)/4 ≤ n para n ≥ 1:")
bloque("""
T(n) ≤ (n/3) · n = (1/3) · n²        (c = 1/3, n₀ = 1)
""")
p("**Cota inferior.** Para n ≥ 6: ⌊n/3⌋ ≥ n/6 y ⌊(n−1)/4⌋ + 1 ≥ n/4:")
bloque("""
T(n) ≥ n²/24
""")
p("Por lo tanto **T(n) = Θ(n²)**, y en particular **T(n) = O(n²)**.")

h3("Número exacto de printf")
tabla(["n", "⌊n/3⌋", "⌊(n−1)/4⌋+1", "T(n)"], [
    ["1", "0", "1", "0"],
    ["10", "3", "3", "9"],
    ["100", "33", "25", "825"],
    ["1 000", "333", "250", "83 250"],
    ["10 000", "3 333", "2 500", "8 332 500"],
    ["100 000", "33 333", "25 000", "833 325 000"],
    ["1 000 000", "333 333", "250 000", "83 333 250 000"],
])

h2("Parte b: profiling")
p("Implementación en C (problema3/problema3.c), con las mismas dos versiones que el Problema 2: "
  "original con printf (salida a NUL) y printf reemplazado por contador.")
tabla_profiling(3)
p("La versión con printf y n = 1 000 000 no se ejecutó: son 83 333 250 000 llamadas a printf. "
  "Cada una tarda ≈ 0.5 µs aun con la salida a NUL, lo que da unas 12 horas. "
  "La versión con contador sí se midió con todos los valores de n.")
imagen(os.path.join(RAIZ, "problema3", "salida", "grafica.png"))
p("**Comparación con la teoría.** Cada vez que n se multiplica por 10, el tiempo se multiplica por "
  "≈100 (×98.9 con printf entre n = 10⁴ y 10⁵; ×99.8 con contador entre n = 10⁵ y 10⁶). "
  "En la gráfica log-log son rectas de pendiente ≈ 2, que corresponde a O(n²).")


# =====================================================================
# Problema 4
# =====================================================================
h1("Problema 4")
p("Unidad de costo: en las búsquedas, número de comparaciones con el elemento buscado x; "
  "en Quick Sort, número de comparaciones entre elementos.")

h2("4.1 Búsqueda lineal")
bloque("""
for i = 0 .. n-1:
    if A[i] == x: return i
return -1
""")
p("Cada iteración hace 1 comparación. El costo depende de en qué posición está x.")

h3("Mejor caso")
p("x está en la primera posición, A[0]:")
bloque("""
comparaciones = 1
T(n) = 1 = Θ(1)
""")

h3("Peor caso")
p("x está en la última posición, o no está en el arreglo. Se recorren los n elementos:")
bloque("""
comparaciones = n
T(n) = n = Θ(n)
""")

h3("Caso promedio")
p("Se supone que x está en el arreglo y que cada posición tiene probabilidad 1/n. "
  "Si x está en la posición i (contando desde 1), se hacen i comparaciones:")
bloque("""
E[T(n)] = Σ (i=1..n) i · (1/n)
        = (1/n) · n(n+1)/2
        = (n+1)/2

Se elimina la constante 1/2:

E[T(n)] = Θ(n)
""")
p("En promedio se revisa la mitad del arreglo, que sigue siendo lineal. Si x puede no estar "
  "(con probabilidad q), el promedio es (1−q)(n+1)/2 + q·n, que también es Θ(n).")
tabla(["Caso", "Comparaciones", "Complejidad"], [
    ["Mejor", "1", "Θ(1)"],
    ["Promedio", "(n+1)/2", "Θ(n)"],
    ["Peor", "n", "Θ(n)"],
])

h2("4.2 Búsqueda binaria (arreglo ordenado)")
bloque("""
izq = 0, der = n-1
while izq <= der:
    mid = (izq + der) / 2
    if A[mid] == x: return mid
    if A[mid] < x: izq = mid + 1
    else:          der = mid - 1
return -1
""")

h3("Mejor caso")
p("x está justo en el centro: 1 comparación, T(n) = Θ(1).")

h3("Peor caso")
p("x se encuentra al final de la búsqueda, o no está. En cada paso el rango se reduce a la mitad:")
bloque("""
paso 1: n elementos
paso 2: n/2
paso 3: n/4
...
paso k: n/2^(k−1)

Termina cuando queda 1 elemento:
n/2^(k−1) = 1  →  2^(k−1) = n  →  k = log₂ n + 1
""")
p("Lo mismo con la recurrencia T(n) = T(n/2) + 1, T(1) = 1, desenrollándola:")
bloque("""
T(n) = T(n/2) + 1
     = T(n/4) + 2
     = T(n/8) + 3
     ...
     = T(n/2^k) + k

Con n/2^k = 1, es decir k = log₂ n:

T(n) = 1 + log₂ n = Θ(log n)
""")
p("**Por qué aparece el logaritmo:** log₂ n cuenta cuántas veces se puede dividir n entre 2 hasta "
  "llegar a 1. Cada comparación descarta la mitad de los elementos restantes, así que el número "
  "de comparaciones es ese número de divisiones.")

h3("Caso promedio")
p("Las búsquedas forman un árbol binario de decisión balanceado: el elemento de la raíz se "
  "encuentra con 1 comparación, los 2 del nivel 2 con 2 comparaciones y, en general, los "
  "2^(d−1) elementos del nivel d con d comparaciones. Con n = 2^k − 1 (árbol lleno de k niveles) "
  "y cada elemento igual de probable:")
bloque("""
E[T(n)] = (1/n) · Σ (d=1..k) d · 2^(d−1)

Identidad:  Σ (d=1..k) d·2^(d−1) = (k−1)·2^k + 1

E[T(n)] = [(k−1)·2^k + 1] / n
        = [(k−1)(n+1) + 1] / n
        ≈ k − 1
        = log₂(n+1) − 1
""")
p("Ejemplo con n = 7 (k = 3): (1·1 + 2·2 + 3·4)/7 = 17/7 ≈ 2.43 comparaciones. "
  "Por lo tanto E[T(n)] = **Θ(log n)**. Más de la mitad de los elementos están en el último "
  "nivel, por eso el promedio queda a solo ~1 comparación del peor caso.")
tabla(["Caso", "Comparaciones", "Complejidad"], [
    ["Mejor", "1", "Θ(1)"],
    ["Promedio", "≈ log₂(n+1) − 1", "Θ(log n)"],
    ["Peor", "⌊log₂ n⌋ + 1", "Θ(log n)"],
])

h2("4.3 Quick Sort")
bloque("""
quicksort(A, izq, der):
    if izq < der:
        p = particion(A, izq, der)   // pivote en su lugar final
        quicksort(A, izq, p-1)
        quicksort(A, p+1, der)
""")
p("La partición de un subarreglo de m elementos compara cada elemento con el pivote: "
  "m − 1 comparaciones, es decir Θ(m). El costo total depende de cómo divide el pivote el arreglo:")
bloque("""
T(n) = T(izquierda) + T(derecha) + (n − 1)
""")

h3("Peor caso: el pivote siempre es el mínimo o el máximo")
p("Ocurre, por ejemplo, si el arreglo ya está ordenado y se toma el último elemento como pivote. "
  "Un lado queda vacío y el otro con n − 1 elementos:")
bloque("""
T(n) = T(n−1) + T(0) + (n−1)
T(n) = T(n−1) + (n−1)

Desenrollando:

T(n) = (n−1) + (n−2) + ... + 1 + 0
     = n(n−1)/2

Se eliminan la constante 1/2 y el término de menor orden:

T(n) = Θ(n²)
""")

h3("Mejor caso: el pivote siempre es la mediana")
p("Cada partición deja dos mitades iguales:")
bloque("""
T(n) = 2T(n/2) + (n−1)

Árbol de recursión:
nivel 0: 1 subproblema de tamaño n          → costo ≈ n
nivel 1: 2 subproblemas de tamaño n/2       → costo ≈ 2·(n/2) = n
nivel 2: 4 subproblemas de tamaño n/4       → costo ≈ n
...
nivel j: 2^j subproblemas de tamaño n/2^j   → costo ≈ n

Los subproblemas llegan a tamaño 1 cuando n/2^j = 1  →  j = log₂ n

T(n) ≈ n · log₂ n = Θ(n log n)
""")
p("Lo confirma el Teorema Maestro: a = 2, b = 2, f(n) = Θ(n) = Θ(n^(log₂2)), caso 2 → Θ(n log n).")

h3("Caso promedio: pivote aleatorio (o entrada en orden aleatorio)")
p("El pivote termina en la posición i con probabilidad 1/n. Si queda en la posición i, deja "
  "i − 1 elementos a la izquierda y n − i a la derecha:")
bloque("""
T(n) = (n−1) + (1/n) · Σ (i=1..n) [T(i−1) + T(n−i)]

Cada T(k) aparece dos veces:

T(n) = (n−1) + (2/n) · Σ (k=0..n−1) T(k)

Multiplicando por n:
n·T(n) = n(n−1) + 2 · Σ (k=0..n−1) T(k)                    (1)

La misma ecuación para n − 1:
(n−1)·T(n−1) = (n−1)(n−2) + 2 · Σ (k=0..n−2) T(k)          (2)

Restando (1) − (2):
n·T(n) − (n−1)·T(n−1) = 2(n−1) + 2·T(n−1)
n·T(n) = (n+1)·T(n−1) + 2(n−1)

Dividiendo entre n(n+1):
T(n)/(n+1) = T(n−1)/n + 2(n−1)/(n(n+1))

Con 2(n−1)/(n(n+1)) = 4/(n+1) − 2/n  y  S(n) = T(n)/(n+1), S(1) = 0:

S(n) = Σ (k=2..n) [4/(k+1) − 2/k] = 2·H_n + 4/(n+1) − 4

donde H_n = 1 + 1/2 + ... + 1/n  (número armónico)

T(n) = (n+1)·S(n) = 2(n+1)·H_n − 4n
""")
p("Verificación: con n = 2 la fórmula da 2·3·(3/2) − 8 = 1 y el cálculo directo da "
  "(2−1) + (2/2)(0+0) = 1. Con n = 3 da 2·4·(11/6) − 12 = 8/3 y el directo 2 + (2/3)(0+0+1) = 8/3.")
bloque("""
Como H_n ≈ ln n:

T(n) ≈ 2n·ln n ≈ 1.39 · n·log₂ n = Θ(n log n)
""")

h3("Cómo influye el pivote")
p("• **Pivote balanceado:** cada nivel de recursión cuesta Θ(n) y hay Θ(log n) niveles → Θ(n log n).\n"
  "• **Pivote extremo:** solo se elimina un elemento por nivel; hay n niveles con costos n−1, n−2, … → Θ(n²).\n"
  "• Aun particiones desbalanceadas, como 1/10 y 9/10, dan profundidad log_{10/9} n = Θ(log n) "
  "y costo total Θ(n log n). Por eso el caso promedio se parece al mejor caso.\n"
  "• Elegir el pivote al azar, o con la mediana de tres, hace muy improbable el peor caso, "
  "aunque no lo elimina.")
tabla(["Caso", "Recurrencia", "Comparaciones", "Complejidad"], [
    ["Mejor", "T(n) = 2T(n/2) + (n−1)", "≈ n log₂ n", "Θ(n log n)"],
    ["Promedio", "T(n) = (n−1) + (2/n)ΣT(k)", "2(n+1)H_n − 4n", "Θ(n log n)"],
    ["Peor", "T(n) = T(n−1) + (n−1)", "n(n−1)/2", "Θ(n²)"],
], anchos=(18, 42, 30, 22))


# =====================================================================
# Problema 5
# =====================================================================
h1("Problema 5")

h2("a) Si f(n) = Θ(g(n)) y g(n) = Θ(h(n)), entonces h(n) = Θ(f(n)).")
p("**Respuesta: VERDADERO.**")
p("Por definición, existen constantes positivas tales que:")
bloque("""
c₁·g(n) ≤ f(n) ≤ c₂·g(n)     para n ≥ n₁          (1)
c₃·h(n) ≤ g(n) ≤ c₄·h(n)     para n ≥ n₂          (2)
""")
p("**Transitividad (f = Θ(h)).** Sustituyendo (2) en (1), para n ≥ n₀ = max(n₁, n₂):")
bloque("""
f(n) ≥ c₁·g(n) ≥ c₁·c₃·h(n)
f(n) ≤ c₂·g(n) ≤ c₂·c₄·h(n)

→ (c₁c₃)·h(n) ≤ f(n) ≤ (c₂c₄)·h(n)      es decir  f = Θ(h)
""")
p("**Simetría (h = Θ(f)).** Despejando h(n) de ambas desigualdades:")
bloque("""
f(n) ≤ c₂c₄·h(n)  →  h(n) ≥ (1/(c₂c₄))·f(n)
f(n) ≥ c₁c₃·h(n)  →  h(n) ≤ (1/(c₁c₃))·f(n)

→ (1/(c₂c₄))·f(n) ≤ h(n) ≤ (1/(c₁c₃))·f(n)     para n ≥ n₀
""")
p("Las constantes 1/(c₂c₄) y 1/(c₁c₃) son positivas, así que **h(n) = Θ(f(n))**. ∎ "
  "En general, Θ es una relación de equivalencia (reflexiva, simétrica y transitiva). "
  "Ejemplo: f = 3n² + n, g = n², h = 5n²; las tres son Θ(n²) y cada una es Θ de las otras.")

h2("b) Si f(n) = O(g(n)) y g(n) = O(h(n)), entonces h(n) = Ω(f(n)).")
p("**Respuesta: VERDADERO.**")
bloque("""
f(n) ≤ c₁·g(n)     para n ≥ n₁
g(n) ≤ c₂·h(n)     para n ≥ n₂
""")
p("**Paso 1, transitividad de O.** Para n ≥ n₀ = max(n₁, n₂):")
bloque("""
f(n) ≤ c₁·g(n) ≤ c₁·c₂·h(n)     →  f(n) = O(h(n))   con c = c₁c₂
""")
p("**Paso 2, simetría transpuesta de O y Ω.** Despejando h(n):")
bloque("""
f(n) ≤ c₁c₂·h(n)  →  h(n) ≥ (1/(c₁c₂))·f(n)     para n ≥ n₀
""")
p("Esa es la definición de Ω con constante c' = 1/(c₁c₂) > 0, así que **h(n) = Ω(f(n))**. ∎")
p("Ejemplo: f = n, g = n², h = n³. Se cumple n = O(n²) y n² = O(n³), y en efecto n³ = Ω(n). "
  "La conclusión no se puede reforzar a Θ: con el mismo ejemplo, n³ ≠ O(n), así que n³ ≠ Θ(n).")

h2("c) f(n) = Θ(n²), donde f(n) es el tiempo de ejecución de A(n).")
bloque("""
def A(n):
    atupla = tuple(range(0, n))
    S = set()
    for i in range(0, n):
        for j in range(i + 1, n):
            S.add(atupla[i:j])
""")
p("**Respuesta: FALSO.** En realidad f(n) = Θ(n³).")

h3("Costo de cada parte")
p("• tuple(range(0, n)) construye una tupla de n elementos: **Θ(n)**.\n"
  "• set() crea un conjunto vacío: **Θ(1)**.")

h3("Número de iteraciones de los ciclos")
bloque("""
i = 0, 1, ..., n−1
j = i+1, ..., n−1      →  n−1−i iteraciones

Σ (i=0..n−1) (n−1−i) = (n−1) + (n−2) + ... + 0 = n(n−1)/2
""")
p("Si cada iteración costara O(1), el total sería Θ(n²) y la afirmación sería verdadera. "
  "**Pero cada iteración no cuesta O(1).**")

h3("Costo de una iteración: S.add(atupla[i:j])")
p("Sea L = j − i la longitud del slice:\n"
  "1. atupla[i:j] **crea una tupla nueva** copiando L elementos: Θ(L).\n"
  "2. S.add(...) debe calcular el **hash de la tupla**. En CPython el hash de una tupla recorre "
  "todos sus elementos (y no se guarda en caché): Θ(L).\n"
  "3. La inserción en el set es O(1) esperado. Todos los slices son distintos (cada par (i, j) da "
  "la secuencia distinta i, …, j−1), así que no hay comparaciones de igualdad completas, "
  "salvo colisiones de hash poco probables.\n"
  "Por lo tanto cada iteración cuesta Θ(j − i).")

h3("Costo total")
bloque("""
f(n) = Σ (i=0..n−1) Σ (j=i+1..n−1) (j − i)
     = Σ (i=0..n−1) Σ (L=1..n−1−i) L

Con m = n − 1 − i  (m = 0, 1, ..., n−1):

f(n) = Σ (m=0..n−1) m(m+1)/2
     = (1/2) · [ Σ m² + Σ m ]
     = (1/2) · [ (n−1)n(2n−1)/6 + (n−1)n/2 ]
     = (1/2) · (n−1)n(2n−1+3)/6
     = (n−1)·n·(n+1) / 6
     = (n³ − n) / 6

Más el Θ(n) de construir atupla:

f(n) = (n³ − n)/6 + Θ(n) = Θ(n³)
""")

h3("Por qué no es Θ(n²)")
p("Si fuera f(n) = O(n²), existiría c tal que (n³ − n)/6 ≤ c·n² para todo n grande. "
  "Dividiendo entre n²:")
bloque("""
(n − 1/n)/6 ≤ c
""")
p("El lado izquierdo crece sin límite, así que ninguna constante c funciona. Entonces "
  "f(n) ≠ O(n²) y, por lo tanto, **f(n) ≠ Θ(n²)**.")
p("La afirmación solo cuenta las n(n−1)/2 iteraciones de los ciclos y omite que el slice y su hash "
  "cuestan un tiempo proporcional a la longitud de la tupla. La cota Ω(n²) sí se cumple, pero la "
  "cota O(n²) no. Además, el set termina guardando (n³ − n)/6 elementos en total, así que la "
  "memoria también es Θ(n³).")

h2("Resumen del Problema 5")
tabla(["Inciso", "Respuesta", "Razón"], [
    ["a", "Verdadero", "Θ es transitiva y simétrica"],
    ["b", "Verdadero", "O es transitiva, y f = O(h) ⇔ h = Ω(f)"],
    ["c", "Falso", "Cada iteración cuesta Θ(j−i); f(n) = (n³−n)/6 + Θ(n) = Θ(n³)"],
], anchos=(14, 22, 76))


ruta = os.path.join(CARPETA, "respuestas.pdf")
pdf.output(ruta)
print(f"PDF guardado en {ruta}")
