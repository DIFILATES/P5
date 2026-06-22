#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dibuja la envolvente ADSR teorica de un instrumento de la practica P5.

Reproduce la forma de la envolvente segun los parametros del fichero .orc
(ADSR_A, ADSR_D, ADSR_S, ADSR_R). Pensado para acompanar en la memoria a
las capturas reales de wavesurfer.

Uso:
    python3 dibujar_adsr.py

Edita el diccionario INSTRUMENTOS de abajo para anadir o cambiar curvas.
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# PARAMETROS DE CADA INSTRUMENTO  (los mismos que en tus ficheros .orc)
#
#   A, D, R  -> tiempos en segundos
#   S        -> nivel de mantenimiento (0..1)
#   t_on     -> instante en que se suelta la tecla (NoteOff). Marca el inicio
#               del release. Ajustalo para reproducir cada "final" de la nota.
#   t_total  -> duracion total del eje de tiempo en el dibujo (s)
# ---------------------------------------------------------------------------
INSTRUMENTOS = {
    # General: ADSR clasico con los cuatro tramos visibles
    "general": dict(A=0.01, D=0.1, S=0.6, R=0.1, t_on=1.0, t_total=1.6),

    # Corda fregada (plano): ataque rapido, sustain alto, release rapido.
    "corda_fregada": dict(A=0.05, D=0.05, S=0.8, R=0.05, t_on=1.0, t_total=1.3),
}

# Instrumentos percusivos (S=0). Se dibujan con DOBLE curva:
#   - solido = envolvente real (la nota se corta en el NoteOff t_on)
#   - punteado = continuacion ideal si la nota durase hasta extinguirse sola
#
# PIANO: la nota se ACABA ANTES de que deje de sonar.
#   -> el NoteOff (t_on) llega mientras el decay aun tiene amplitud.
#      Se ve el release real (solido) y, en puntos, lo que habria seguido
#      bajando el decay si no se hubiera soltado.
# GUITARRA: deja de sonar ANTES de que se acabe la nota.
#   -> el decay llega a 0 por si solo; el NoteOff llega despues, sin efecto.
#      El solido completa toda la curva; el punteado apenas aporta.
PERCUSIVOS = {
    "piano":    dict(A=0.03, D=5.0, S=0.0, R=0.05, t_on=2.0, t_total=5.4),
    "guitarra": dict(A=0.03, D=0.4, S=0.0, R=0.05, t_on=0.6, t_total=0.8),
}

# Si tu envelope_adsr.cpp usa tramos curvos (exponenciales), pon True.
# Si usa rectas, deja False. Por defecto el esquema clasico es a rectas.
CURVO = False
FACTOR_SLOPE = 1.5  # solo se usa si CURVO=True (valor por defecto del codigo)

FS = 44100  # frecuencia de muestreo, solo para discretizar el dibujo


def _ramp(n, y0, y1, curvo):
    """Genera un tramo de n muestras de y0 a y1, recto o curvo."""
    if n <= 0:
        return np.array([])
    t = np.linspace(0, 1, n)
    if not curvo:
        return y0 + (y1 - y0) * t
    # Curva tipo exponencial saturante (aproximacion del factor_slope).
    k = FACTOR_SLOPE
    shape = (1 - np.exp(-k * t)) / (1 - np.exp(-k))
    return y0 + (y1 - y0) * shape


def construir_envolvente(A, D, S, R, t_on, t_total, curvo=False):
    """Devuelve (t, env) con la envolvente muestreada."""
    nA = int(A * FS)
    nD = int(D * FS)
    nR = int(R * FS)
    n_on = int(t_on * FS)      # muestra en la que llega el NoteOff
    n_total = int(t_total * FS)

    env = np.zeros(n_total)

    # 1) Fase de "tecla pulsada": Attack -> Decay -> Sustain, recortada en n_on.
    #    Construimos la curva completa de esta fase y luego la cortamos en n_on.
    attack = _ramp(nA, 0.0, 1.0, curvo)
    decay = _ramp(nD, 1.0, S, curvo)
    pre = np.concatenate([attack, decay])  # curva mientras la tecla esta pulsada

    # El NoteOff (n_on) puede caer en cualquier punto: durante attack, decay
    # o ya en sustain. Tomamos lo que haya hasta n_on; si n_on cae despues de
    # attack+decay, se prolonga con el nivel de sustain S.
    held = np.zeros(n_on)
    m = min(len(pre), n_on)
    held[:m] = pre[:m]
    if n_on > len(pre):
        held[len(pre):] = S  # prolongacion en sustain

    i = min(n_on, n_total)
    env[:i] = held[:i]

    # Nivel exacto desde el que arranca el release (el valor en el NoteOff)
    nivel_release = env[i - 1] if i > 0 else 0.0

    # 2) Release: desde nivel_release hasta 0
    seg = _ramp(nR, nivel_release, 0.0, curvo)
    end = min(i + len(seg), n_total)
    env[i:end] = seg[:end - i]

    # 3) Resto a cero (ya inicializado)
    t = np.arange(n_total) / FS
    return t, env


def dibujar(nombre, p, curvo=False, guardar=True, mostrar=False):
    t, env = construir_envolvente(p["A"], p["D"], p["S"], p["R"],
                                  p["t_on"], p["t_total"], curvo)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t, env, linewidth=2, color="#1f5fbf")
    ax.fill_between(t, env, alpha=0.12, color="#1f5fbf")

    # Lineas de tiempo de cada fase.
    # El NoteOff (t_on) interrumpe lo que haya: si llega durante el decay,
    # el decay visible se corta ahi y no hay sustain.
    tA = p["A"]
    tD_full = tA + p["D"]          # fin teorico del decay si no se soltara
    t_on = p["t_on"]
    tD = min(tD_full, t_on)        # fin del decay realmente visible
    tR = t_on + p["R"]
    hay_sustain = t_on > tD_full   # solo hay meseta si se suelta tras el decay

    for x in (tA, tD, t_on, tR):
        ax.axvline(x, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

    # Nivel de sustain
    ax.axhline(p["S"], color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
    ax.text(t_total_margen(p), p["S"], " S = %.2f" % p["S"],
            va="center", ha="left", fontsize=9, color="gray")

    # Flechas de duracion de cada tramo (estilo esquema clasico ADSR)
    _flecha_tramo(ax, 0,  tA, "A", y=-0.09)
    _flecha_tramo(ax, tA, tD, "D", y=-0.09)
    _flecha_tramo(ax, t_on, tR, "R", y=-0.09)
    if hay_sustain:
        _flecha_tramo(ax, tD_full, t_on, "S", y=p["S"] + 0.06, color="#1f5fbf")

    # Letras grandes de cada fase encima de la curva (referencia rapida)
    y_lab = 1.08
    _fase_label(ax, 0,  tA, "A", y_lab)
    _fase_label(ax, tA, tD, "D", y_lab)
    if hay_sustain:
        _fase_label(ax, tD_full, t_on, "S", y_lab)
    _fase_label(ax, t_on, tR, "R", y_lab)

    ax.set_xlim(0, p["t_total"])
    ax.set_ylim(-0.15, 1.2)
    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel("amplitud (normalizada)")
    ax.set_title("Envolvente ADSR - %s\n(A=%.3g  D=%.3g  S=%.3g  R=%.3g)"
                 % (nombre, p["A"], p["D"], p["S"], p["R"]), fontsize=11)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()

    if guardar:
        fname = "envolvente_%s.png" % nombre
        fig.savefig(fname, dpi=150)
        print("Guardado:", fname)
    if mostrar:
        plt.show()
    plt.close(fig)


def _fase_label(ax, x0, x1, txt, y):
    if x1 > x0:
        ax.text((x0 + x1) / 2, y, txt, ha="center", va="bottom",
                fontsize=12, fontweight="bold", color="#333333")


def _flecha_tramo(ax, x0, x1, txt, y, color="#444444"):
    """Dibuja una flecha doble <-> entre x0 y x1 con su etiqueta encima."""
    if x1 <= x0:
        return
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.3))
    ax.text((x0 + x1) / 2, y + 0.02, txt, ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=color)


def t_total_margen(p):
    return p["t_total"] * 0.5


def dibujar_percusivo(nombre, p, curvo=False, guardar=True, mostrar=False):
    """Dibuja un percusivo (S=0) con doble curva:
       - solido: envolvente real, cortada por el NoteOff (t_on) + release
       - punteado: continuacion ideal del decay si la nota fuera infinita
    """
    A, D, S, R = p["A"], p["D"], p["S"], p["R"]
    t_on, t_total = p["t_on"], p["t_total"]

    # Curva IDEAL: attack + decay completo hasta 0 (sin soltar nunca)
    t_id, env_id = construir_envolvente(A, D, S, R, t_on=t_total + 10,
                                        t_total=t_total, curvo=curvo)
    # Curva REAL: attack + decay cortado en t_on + release
    t_re, env_re = construir_envolvente(A, D, S, R, t_on=t_on,
                                        t_total=t_total, curvo=curvo)

    fig, ax = plt.subplots(figsize=(8, 4))

    # Ideal en punteado/tenue
    ax.plot(t_id, env_id, linestyle=":", linewidth=2, color="#999999",
            label="ideal (nota infinita)")
    # Real en solido
    ax.plot(t_re, env_re, linewidth=2.2, color="#1f5fbf",
            label="real (nota recortada)")
    ax.fill_between(t_re, env_re, alpha=0.10, color="#1f5fbf")

    # Marca del NoteOff (donde se suelta la tecla)
    ax.axvline(t_on, color="#c0392b", linestyle="--", linewidth=1.2, alpha=0.8)
    nivel_noteoff = env_id[min(int(t_on * FS), len(env_id) - 1)]
    if nivel_noteoff > 0.02:
        # La nota se corta con senal aun audible: el release es relevante
        ax.annotate("NoteOff\n(se suelta)", xy=(t_on, nivel_noteoff),
                    xytext=(t_on, 1.18), ha="center", va="bottom",
                    fontsize=9, color="#c0392b")
        tR = t_on + R
        _flecha_tramo(ax, t_on, tR, "R", y=-0.09)
    else:
        # La nota ya estaba extinguida al soltar: el release no tiene efecto
        ax.annotate("NoteOff\n(ya extinguida)", xy=(t_on, 0.02),
                    xytext=(t_on, 0.25), ha="center", va="bottom",
                    fontsize=9, color="#c0392b")

    # Etiquetas de fase A y D (siempre visibles)
    tA = A
    tD = min(tA + D, t_on)
    _flecha_tramo(ax, 0,  tA, "A", y=-0.09)
    _flecha_tramo(ax, tA, tD, "D", y=-0.09)

    ax.set_xlim(0, t_total)
    ax.set_ylim(-0.15, 1.35)
    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel("amplitud (normalizada)")
    ax.set_title("Envolvente ADSR - %s (percusivo)\n(A=%.3g  D=%.3g  S=%.3g  R=%.3g)"
                 % (nombre, A, D, S, R), fontsize=11)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9,
              bbox_to_anchor=(1.0, 0.92))
    ax.grid(True, alpha=0.2)
    fig.tight_layout()

    if guardar:
        fname = "envolvente_%s.png" % nombre
        fig.savefig(fname, dpi=150)
        print("Guardado:", fname)
    if mostrar:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    for nombre, p in INSTRUMENTOS.items():
        dibujar(nombre, p, curvo=CURVO, guardar=True, mostrar=False)
    for nombre, p in PERCUSIVOS.items():
        dibujar_percusivo(nombre, p, curvo=CURVO, guardar=True, mostrar=False)
    print("\nListo. Edita INSTRUMENTOS/PERCUSIVOS o CURVO/FACTOR_SLOPE para ajustar.")
