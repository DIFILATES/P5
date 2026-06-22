import numpy as np
import matplotlib.pyplot as plt

FS = 44100.0

def envelope_adsr(n_total, A, D, S, R, n_release):
    """Envolvent ADSR simplificada (rampes lineals)."""
    env = np.zeros(n_total)
    nA, nD, nR = int(A*FS), int(D*FS), int(R*FS)
    i = 0
    # attack
    e = min(nA, n_total); env[i:e] = np.linspace(0,1,e-i) if e>i else env[i:e]; i=e
    # decay
    e = min(i+nD, n_total); 
    if e>i: env[i:e] = np.linspace(1,S,e-i)
    i=e
    # sustain fins release
    e = min(n_release, n_total)
    if e>i: env[i:e] = S
    i=e
    # release
    e = min(i+nR, n_total)
    if e>i: env[i:e] = np.linspace(env[i-1] if i>0 else S, 0, e-i)
    return env

def fm_campana(f0, N1, N2, Imax_s, Imin_s, dur=3.0):
    fc, fm = f0*N1, f0*N2
    Imax = (fc/fm)*(2**(Imax_s/12)-1)
    Imin = (fc/fm)*(2**(Imin_s/12)-1)
    n_total = int(dur*FS)
    # envolvent campana: atac rapid, S=0, decay llarg
    env = envelope_adsr(n_total, 0.005, dur*0.95, 0.0, 0.1, n_total)
    t = np.arange(n_total)/FS
    I_inst = Imin + env*(Imax-Imin)
    x = env * np.sin(2*np.pi*fc*t + I_inst*np.sin(2*np.pi*fm*t))
    return t, x, env, fc, fm

f0 = 261.6  # Do central
t, x, env, fc, fm = fm_campana(f0, 5, 7, 10, 0, dur=3.0)

fig, axs = plt.subplots(3,1, figsize=(9,8))
# Forma d'ona completa
axs[0].plot(t, x, color="#1f5fbf", linewidth=0.4)
axs[0].plot(t, env, color="#c0392b", linewidth=1.5, label="envolvent (= index)")
axs[0].set_title("Campana FM (N1=5, N2=7): l'index segueix l'envolvent",
                 fontweight="bold")
axs[0].set_ylabel("amplitud"); axs[0].legend(fontsize=9); axs[0].grid(alpha=0.2)

# Espectre a l'INICI (index alt -> ric)
seg_ini = x[int(0.02*FS):int(0.12*FS)]
X = np.abs(np.fft.rfft(seg_ini*np.hanning(len(seg_ini)))); X/=X.max()
fr = np.fft.rfftfreq(len(seg_ini),1/FS)
axs[1].plot(fr, X, color="#2e7d32"); axs[1].set_xlim(0,4000)
axs[1].set_title("Espectre a l'INICI (index alt -> moltes components, so ric)",
                 fontsize=10)
axs[1].set_ylabel("magnitud"); axs[1].grid(alpha=0.2)

# Espectre al FINAL (index baix -> pur)
seg_fin = x[int(2.0*FS):int(2.1*FS)]
X2 = np.abs(np.fft.rfft(seg_fin*np.hanning(len(seg_fin)))); 
if X2.max()>0: X2/=X2.max()
axs[2].plot(fr[:len(X2)], X2, color="#2e7d32"); axs[2].set_xlim(0,4000)
axs[2].set_title("Espectre al FINAL (index baix -> poques components, so pur)",
                 fontsize=10)
axs[2].set_xlabel("frequencia (Hz)"); axs[2].set_ylabel("magnitud"); axs[2].grid(alpha=0.2)

fig.tight_layout()
fig.savefig("fm_campana.png", dpi=150)
print("Guardat: fm_campana.png")
