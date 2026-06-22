#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafiques teoriques dels efectes Tremolo i Vibrato sobre una sinusoide.

Reprodueix les formules implementades als fitxers de la practica:

  TREMOLO (tremolo.cpp):
      x[n] = x[n] * ((2 - A) + A*sin(fase)) / 2
      fase += 2*pi*fm/fs
    -> modulacio d'AMPLITUD: l'envolvent oscil-la entre (1-A) i 1 a fm Hz.

  VIBRATO (vibrato.cpp):
      modula la FREQUENCIA (pitch) recorrent el senyal a velocitat variable.
      I es la maxima desviacio cap avall en semitons; fm la freq de modulacio.
"""

import numpy as np
import matplotlib.pyplot as plt

FS = 44100.0          # frequencia de mostreig
F0 = 220.0            # frequencia de la portadora (nota greu per veure-ho millor)
DUR = 0.5             # durada del fragment (s)


# ---------------------------------------------------------------------------
#  TREMOLO
# ---------------------------------------------------------------------------
def grafica_tremolo(A=0.5, fm=10.0):
    t = np.arange(int(DUR * FS)) / FS
    portadora = np.sin(2 * np.pi * F0 * t)

    # Envolvent del tremolo (formula de tremolo.cpp)
    fase = 2 * np.pi * fm * t
    envolvent = ((2 - A) + A * np.sin(fase)) / 2
    senyal = portadora * envolvent

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(t, senyal, color="#1f5fbf", linewidth=0.8, label="senyal amb tremolo")
    # Dibuixem l'envolvent (a dalt i a baix) per veure la modulacio d'amplitud
    ax.plot(t, envolvent, color="#c0392b", linewidth=1.8, label="envolvent")
    ax.plot(t, -envolvent, color="#c0392b", linewidth=1.8)

    # Anotacions dels parametres sobre la propia grafica
    # Periode de modulacio Tm = 1/fm
    Tm = 1 / fm
    ax.annotate("", xy=(0.05 + Tm, 1.12), xytext=(0.05, 1.12),
                arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.3))
    ax.text(0.05 + Tm / 2, 1.16, "Tm = 1/fm = %.0f ms" % (Tm * 1000),
            ha="center", fontsize=9, color="#444444")

    # Profunditat A: distancia entre el maxim (1) i el minim (1-A) de l'envolvent
    ax.annotate("", xy=(0.46, 1.0), xytext=(0.46, 1 - A),
                arrowprops=dict(arrowstyle="<->", color="#2e7d32", lw=1.3))
    ax.text(0.452, 1 - A / 2, "profunditat A = %.2f" % A,
            ha="right", va="center", fontsize=9, color="#2e7d32")

    ax.set_title("Tremolo: modulacio d'AMPLITUD  (A=%.2f, fm=%.0f Hz)" % (A, fm),
                 fontsize=12, fontweight="bold")
    ax.set_xlabel("temps (s)")
    ax.set_ylabel("amplitud")
    ax.set_ylim(-1.3, 1.3)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig("efecte_tremolo.png", dpi=150)
    plt.close(fig)
    print("Guardat: efecte_tremolo.png")


# ---------------------------------------------------------------------------
#  VIBRATO
# ---------------------------------------------------------------------------
def grafica_vibrato(I=1.0, fm=8.0):
    t = np.arange(int(DUR * FS)) / FS

    # Frequencia instantania: el vibrato fa oscil-lar el pitch al voltant de F0.
    # I (semitons) es la maxima desviacio; la convertim a factor linial.
    # Desviacio cap avall maxima -> f varia entre F0*2^(-I/12) i, simetricament,
    # cap amunt. Modulem la frequencia de forma sinusoidal a fm Hz.
    desv = F0 * (1 - 2 ** (-I / 12.))         # excursio en Hz (aprox.)
    f_inst = F0 + desv * np.sin(2 * np.pi * fm * t)

    # Fase = integral de la frequencia instantania
    fase = 2 * np.pi * np.cumsum(f_inst) / FS
    senyal = np.sin(fase)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

    # A dalt: el senyal (es veu com canvia la "densitat" dels cicles)
    ax1.plot(t, senyal, color="#1f5fbf", linewidth=0.7)
    ax1.set_title("Vibrato: modulacio de FREQUENCIA (pitch)  (I=%.1f semitons, fm=%.0f Hz)"
                  % (I, fm), fontsize=12, fontweight="bold")
    ax1.set_ylabel("amplitud")
    ax1.set_ylim(-1.3, 1.3)
    ax1.grid(True, alpha=0.2)

    # A baix: la frequencia instantania, on es veuen fm i I directament
    ax2.plot(t, f_inst, color="#c0392b", linewidth=1.8, label="freq. instantania")
    ax2.axhline(F0, color="gray", linestyle="--", linewidth=1, label="F0 = %.0f Hz" % F0)
    ax2.set_xlabel("temps (s)")
    ax2.set_ylabel("frequencia (Hz)")
    ax2.grid(True, alpha=0.2)

    # Anotacions: periode de modulacio i excursio
    Tm = 1 / fm
    ax2.annotate("", xy=(0.05 + Tm, F0 + desv * 1.15), xytext=(0.05, F0 + desv * 1.15),
                 arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.3))
    ax2.text(0.05 + Tm / 2, F0 + desv * 1.25, "Tm = 1/fm = %.0f ms" % (Tm * 1000),
             ha="center", fontsize=9, color="#444444")
    ax2.annotate("", xy=(0.012, F0 + desv), xytext=(0.012, F0 - desv),
                 arrowprops=dict(arrowstyle="<->", color="#2e7d32", lw=1.3))
    ax2.text(0.02, F0 - desv * 0.6, "excursio ~%.1f Hz (I=%.1f st)" % (desv, I),
             ha="left", va="center", fontsize=8, color="#2e7d32")
    ax2.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    fig.savefig("efecte_vibrato.png", dpi=150)
    plt.close(fig)
    print("Guardat: efecte_vibrato.png")


if __name__ == "__main__":
    grafica_tremolo(A=0.5, fm=10.0)
    grafica_vibrato(I=1.0, fm=8.0)
    print("Llest.")
