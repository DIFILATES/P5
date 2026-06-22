#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafica de "pelotitas" para el instrumento Seno (sintesis por tabla).

Muestra, con puntos (no lineas):
  - los valores almacenados en la tabla (un periodo de sinusoide, N puntos)
  - los valores de la senal generada al recorrer la tabla con paso 'step'
    usando redondeo al indice entero mas cercano (lo que hace seno.cpp).

Reproduce exactamente la logica de seno.cpp:
    step = 440 * 2**((note-69)/12) * N / fs
    x[i] = tbl[ round(fase) ]   ; fase += step  (con envolvente de indice)
"""

import numpy as np
import matplotlib.pyplot as plt

FS = 44100  # frecuencia de muestreo (Hz)


def generar(N, note, n_muestras):
    """Devuelve (tabla, indices_tabla, idx_usados, senal) replicando seno.cpp."""
    # Tabla: un periodo de sinusoide en N posiciones enteras
    tabla = np.sin(2 * np.pi * np.arange(N) / N)

    # Paso de lectura segun la nota (formula de seno.cpp)
    f0 = 440 * 2 ** ((note - 69) / 12.)
    step = f0 * N / FS

    # Recorrido con redondeo al entero mas cercano
    fase = 0.0
    idx_usados = []
    senal = []
    for _ in range(n_muestras):
        idx = int(fase + 0.5)
        if idx >= N:
            idx -= N
        idx_usados.append(idx)
        senal.append(tabla[idx])
        fase += step
        while fase >= N:
            fase -= N

    return tabla, np.arange(N), np.array(idx_usados), np.array(senal), f0, step


def dibujar(N, note, n_muestras, nombre):
    tabla, idx_tabla, idx_usados, senal, f0, step = generar(N, note, n_muestras)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7))

    # --- A dalt: la taula emmagatzemada (un període) ---
    ax1.plot(idx_tabla, tabla, 'o', color="#1f5fbf", markersize=7,
             label="valors de la taula (N=%d)" % N)
    # Sinusoide ideal contínua de referència (línia fina)
    t_cont = np.linspace(0, N, 500)
    ax1.plot(t_cont, np.sin(2 * np.pi * t_cont / N), '-', color="#cccccc",
             linewidth=1, zorder=0, label="sinusoide ideal")
    ax1.set_title("Taula: un període de sinusoide emmagatzemat (N=%d punts)" % N)
    ax1.set_xlabel("índex de la taula")
    ax1.set_ylabel("amplitud")
    ax1.legend(fontsize=9, loc="upper right")
    ax1.grid(True, alpha=0.25)
    ax1.axhline(0, color="gray", linewidth=0.6)

    # --- A baix: el senyal generat (mostres consecutives) ---
    n = np.arange(len(senal))
    ax2.plot(n, senal, 'o', color="#c0392b", markersize=6,
             label="senyal generat (arrodoniment al veí)")
    # Sinusoide ideal que s'hauria d'haver generat, per comparar
    senal_ideal = np.sin(2 * np.pi * f0 * n / FS)
    ax2.plot(n, senal_ideal, '-', color="#cccccc", linewidth=1, zorder=0,
             label="sinusoide ideal (f0=%.1f Hz)" % f0)
    ax2.set_title("Senyal generat: mostres preses de la taula (step=%.3f)" % step)
    ax2.set_xlabel("índex de mostra n")
    ax2.set_ylabel("amplitud")
    ax2.legend(fontsize=9, loc="upper right")
    ax2.grid(True, alpha=0.25)
    ax2.axhline(0, color="gray", linewidth=0.6)

    fig.suptitle("Síntesi per taula - %s  (note=%d, N=%d)"
                 % (nombre, note, N), fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    fname = "pelotitas_%s.png" % nombre
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print("Guardado:", fname, " (f0=%.2f Hz, step=%.4f)" % (f0, step))


if __name__ == "__main__":
    # Version 1: N=40, La central (note=69, 440 Hz). step "comodo".
    dibujar(N=40, note=69, n_muestras=40, nombre="N40_La440")

    # Version 2: N=20, nota mas aguda (note=84, ~1046 Hz). step grande:
    # se aprecia mejor que la senal NO cae sobre los puntos de la tabla.
    dibujar(N=20, note=84, n_muestras=40, nombre="N20_agudo")

    print("\nListo.")
