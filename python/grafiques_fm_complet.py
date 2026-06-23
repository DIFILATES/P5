#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera totes les grafiques de l'apartat de Sintesi FM de la practica P5.

Reprodueix la formula implementada a instrument_fm.cpp:
    x(t) = A * sin( 2*pi*fc*t + I_lin * sin(2*pi*fm*t) )
amb  fc = f0*N1,  fm = f0*N2  i  I_lin = (fc/fm)*(2^(I/12) - 1).

Genera quatre figures:
  1) fm_vibrato_clar.png : vibrato FM (fm baixa) i frequencia instantania.
  2) fm_n1n2.png         : efecte de la relacio N1:N2 sobre l'espectre.
  3) fm_vibrato.png      : forma d'ona segons creix l'index I (vibrato -> timbre).
  4) fm_espectre.png     : espectre segons creix l'index I.
  5) fm_campana.png      : campana amb index variable (segueix l'envolvent).
"""

import numpy as np
import matplotlib.pyplot as plt

FS = 44100.0


# ---------------------------------------------------------------------------
#  Funcio basica de sintesi FM (igual que instrument_fm.cpp)
# ---------------------------------------------------------------------------
def fm_signal(f0, N1, N2, I_semis, dur=0.2):
    """Genera un senyal FM. I_semis es l'index en semitons."""
    fc = f0 * N1
    fm = f0 * N2
    I_lin = (fc / fm) * (2 ** (I_semis / 12) - 1) if fm > 0 else 0
    t = np.arange(int(dur * FS)) / FS
    x = np.sin(2 * np.pi * fc * t + I_lin * np.sin(2 * np.pi * fm * t))
    return t, x, fc, fm, I_lin


# ---------------------------------------------------------------------------
#  1) Vibrato FM clar: senyal + frequencia instantania
# ---------------------------------------------------------------------------
def grafica_vibrato_clar():
    fc, fm, I_lin, dur = 440.0, 6.0, 3.0, 0.6
    t = np.arange(int(dur * FS)) / FS
    x = np.sin(2 * np.pi * fc * t + I_lin * np.sin(2 * np.pi * fm * t))
    f_inst = fc + I_lin * fm * np.cos(2 * np.pi * fm * t)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
    ax1.plot(t, x, color="#1f5fbf", linewidth=0.6)
    ax1.set_title("Vibrato per FM: senyal  x(t)=sin(2\u03c0·fc·t + I·sin(2\u03c0·fm·t))",
                  fontsize=11, fontweight="bold")
    ax1.set_ylabel("amplitud"); ax1.set_ylim(-1.3, 1.3); ax1.grid(alpha=0.2)

    ax2.plot(t, f_inst, color="#c0392b", linewidth=1.8, label="freq. instantania")
    ax2.axhline(fc, color="gray", ls="--", linewidth=1, label="fc = %.0f Hz" % fc)
    fd = I_lin * fm
    ax2.annotate("", xy=(0.30, fc + fd), xytext=(0.30, fc - fd),
                 arrowprops=dict(arrowstyle="<->", color="#2e7d32", lw=1.3))
    ax2.text(0.31, fc, "excursio de pic\n fd = I·fm = %.0f Hz" % fd,
             fontsize=8, color="#2e7d32", va="center")
    Tm = 1 / fm
    ax2.annotate("", xy=(0.05 + Tm, fc + fd * 1.2), xytext=(0.05, fc + fd * 1.2),
                 arrowprops=dict(arrowstyle="<->", color="#444", lw=1.3))
    ax2.text(0.05 + Tm / 2, fc + fd * 1.35, "Tm=1/fm=%.0f ms" % (Tm * 1000),
             ha="center", fontsize=8, color="#444")
    ax2.set_xlabel("temps (s)"); ax2.set_ylabel("frequencia (Hz)")
    ax2.legend(fontsize=9, loc="lower right"); ax2.grid(alpha=0.2)

    fig.suptitle("Vibrato amb l'instrument FM  (fc=%.0f Hz, fm=%.0f Hz, I_lin=%.1f)"
                 % (fc, fm, I_lin), fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig("fm_vibrato_clar.png", dpi=150)
    plt.close(fig)
    print("Guardat: fm_vibrato_clar.png")


# ---------------------------------------------------------------------------
#  2) Efecte de N1 i N2 sobre l'espectre (index fix)
# ---------------------------------------------------------------------------
def grafica_n1n2():
    f0, I_semis = 220.0, 6.0
    casos = [
        (1, 1, "N1=1, N2=1  (relacio 1:1 -> tots els multiples de f0)"),
        (1, 2, "N1=1, N2=2  (relacio 1:2 -> harmonics mes separats)"),
        (2, 1, "N1=2, N2=1  (relacio 2:1 -> portadora aguda)"),
    ]
    fig, axs = plt.subplots(3, 1, figsize=(9, 8))
    for ax, (N1, N2, titol) in zip(axs, casos):
        t, x, fc, fm, I_lin = fm_signal(f0, N1, N2, I_semis, dur=0.2)
        X = np.abs(np.fft.rfft(x * np.hanning(len(x)))); X /= X.max()
        fr = np.fft.rfftfreq(len(x), 1 / FS)
        ax.plot(fr, X, color="#c0392b", linewidth=1)
        ax.axvline(fc, color="#1f5fbf", ls="--", linewidth=1, alpha=0.7)
        ax.text(fc, 1.02, "fc=%.0f" % fc, color="#1f5fbf", fontsize=8, ha="center")
        ax.set_xlim(0, 2500); ax.set_ylim(0, 1.15)
        ax.set_title(titol + "   [fc=%.0f Hz, fm=%.0f Hz]" % (fc, fm), fontsize=9.5)
        ax.set_ylabel("magnitud"); ax.grid(alpha=0.2)
    axs[-1].set_xlabel("frequencia (Hz)")
    fig.suptitle("Correspondencia de N1 i N2 amb l'espectre (f0=%.0f Hz, I fix)" % f0,
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig("fm_n1n2.png", dpi=150)
    plt.close(fig)
    print("Guardat: fm_n1n2.png")


# ---------------------------------------------------------------------------
#  3) i 4) Forma d'ona i espectre segons l'index I
# ---------------------------------------------------------------------------
def grafiques_index():
    f0 = 220.0
    casos = [
        (1, 1, 1,  "N1=1, N2=1, I=1 st  (poc index: gairebe sinusoidal)"),
        (1, 1, 6,  "N1=1, N2=1, I=6 st  (index mitja: apareixen harmonics)"),
        (1, 2, 12, "N1=1, N2=2, I=12 st (index alt: so ric/brillant)"),
    ]
    # Forma d'ona
    fig, axs = plt.subplots(3, 1, figsize=(9, 8))
    for ax, (N1, N2, I_s, titol) in zip(axs, casos):
        t, x, fc, fm, I_lin = fm_signal(f0, N1, N2, I_s, dur=0.03)
        ax.plot(t * 1000, x, color="#1f5fbf", linewidth=0.9)
        ax.set_title(titol + "  ->  fc=%.0f Hz, fm=%.0f Hz, I_lin=%.2f"
                     % (fc, fm, I_lin), fontsize=10)
        ax.set_ylabel("amplitud"); ax.set_ylim(-1.2, 1.2); ax.grid(alpha=0.2)
    axs[-1].set_xlabel("temps (ms)")
    fig.suptitle("Sintesi FM: efecte de l'index I sobre el senyal (f0=%.0f Hz)" % f0,
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig("fm_vibrato.png", dpi=150)
    plt.close(fig)
    print("Guardat: fm_vibrato.png")

    # Espectre
    fig, axs = plt.subplots(3, 1, figsize=(9, 8))
    for ax, (N1, N2, I_s, titol) in zip(axs, casos):
        t, x, fc, fm, I_lin = fm_signal(f0, N1, N2, I_s, dur=0.2)
        X = np.abs(np.fft.rfft(x * np.hanning(len(x)))); X /= X.max()
        fr = np.fft.rfftfreq(len(x), 1 / FS)
        ax.plot(fr, X, color="#c0392b", linewidth=1)
        ax.set_xlim(0, 3000)
        ax.set_title(titol + "  (I_lin=%.2f)" % I_lin, fontsize=10)
        ax.set_ylabel("magnitud"); ax.grid(alpha=0.2)
    axs[-1].set_xlabel("frequencia (Hz)")
    fig.suptitle("Sintesi FM: espectre segons l'index de modulacio I",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig("fm_espectre.png", dpi=150)
    plt.close(fig)
    print("Guardat: fm_espectre.png")


# ---------------------------------------------------------------------------
#  5) Campana amb index variable (segueix l'envolvent)
# ---------------------------------------------------------------------------
def envelope_adsr(n_total, A, D, S, R, n_release):
    env = np.zeros(n_total)
    nA, nD, nR = int(A * FS), int(D * FS), int(R * FS)
    i = 0
    e = min(nA, n_total)
    if e > i: env[i:e] = np.linspace(0, 1, e - i)
    i = e
    e = min(i + nD, n_total)
    if e > i: env[i:e] = np.linspace(1, S, e - i)
    i = e
    e = min(n_release, n_total)
    if e > i: env[i:e] = S
    i = e
    e = min(i + nR, n_total)
    if e > i: env[i:e] = np.linspace(env[i - 1] if i > 0 else S, 0, e - i)
    return env


def grafica_campana():
    f0, N1, N2, Imax_s, Imin_s, dur = 261.6, 5, 7, 10, 0, 3.0
    fc, fm = f0 * N1, f0 * N2
    Imax = (fc / fm) * (2 ** (Imax_s / 12) - 1)
    Imin = (fc / fm) * (2 ** (Imin_s / 12) - 1)
    n_total = int(dur * FS)
    env = envelope_adsr(n_total, 0.005, dur * 0.95, 0.0, 0.1, n_total)
    t = np.arange(n_total) / FS
    I_inst = Imin + env * (Imax - Imin)
    x = env * np.sin(2 * np.pi * fc * t + I_inst * np.sin(2 * np.pi * fm * t))

    fig, axs = plt.subplots(3, 1, figsize=(9, 8))
    axs[0].plot(t, x, color="#1f5fbf", linewidth=0.4)
    axs[0].plot(t, env, color="#c0392b", linewidth=1.5, label="envolvent (= index)")
    axs[0].set_title("Campana FM (N1=5, N2=7): l'index segueix l'envolvent",
                     fontweight="bold")
    axs[0].set_ylabel("amplitud"); axs[0].legend(fontsize=9); axs[0].grid(alpha=0.2)

    seg = x[int(0.02 * FS):int(0.12 * FS)]
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); X /= X.max()
    fr = np.fft.rfftfreq(len(seg), 1 / FS)
    axs[1].plot(fr, X, color="#2e7d32"); axs[1].set_xlim(0, 4000)
    axs[1].set_title("Espectre a l'INICI (index alt -> moltes components, so ric)",
                     fontsize=10)
    axs[1].set_ylabel("magnitud"); axs[1].grid(alpha=0.2)

    seg2 = x[int(2.0 * FS):int(2.1 * FS)]
    X2 = np.abs(np.fft.rfft(seg2 * np.hanning(len(seg2))))
    if X2.max() > 0: X2 /= X2.max()
    axs[2].plot(fr[:len(X2)], X2, color="#2e7d32"); axs[2].set_xlim(0, 4000)
    axs[2].set_title("Espectre al FINAL (index baix -> poques components, so pur)",
                     fontsize=10)
    axs[2].set_xlabel("frequencia (Hz)"); axs[2].set_ylabel("magnitud")
    axs[2].grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig("fm_campana.png", dpi=150)
    plt.close(fig)
    print("Guardat: fm_campana.png")


if __name__ == "__main__":
    grafica_vibrato_clar()
    grafica_n1n2()
    grafiques_index()
    grafica_campana()
    print("\nTotes les grafiques FM generades.")
