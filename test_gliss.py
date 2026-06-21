import numpy as np
import matplotlib.pyplot as plt

FS = 44100.0
F0 = 220.0
I = 4.0          # semitons per sota a l'inici
t_gliss = 0.3    # durada del lliscament
DUR = 0.6

n_total = t_gliss * FS

# Senyal d'entrada: sinusoide pura a F0 (la nota real)
t = np.arange(int(DUR*FS))/FS
entrada = np.sin(2*np.pi*F0*t)

# Simulem l'algorisme del glissando (recorregut a velocitat variable)
xout = np.zeros(len(entrada))
fase = 0.0
n = 0
for i in range(len(entrada)):
    idx = int(fase)
    if idx >= len(entrada)-1:
        break
    rho = fase - idx
    xout[i] = entrada[idx] + rho*(entrada[idx+1]-entrada[idx])
    semis = -I*(1 - n/n_total) if n < n_total else 0.0
    K = 2**(semis/12)
    fase += K
    n += 1

# Frequencia instantania teorica per comprovar
n_arr = np.arange(len(t))
semis_arr = np.where(n_arr < n_total, -I*(1 - n_arr/n_total), 0.0)
f_inst = F0 * 2**(semis_arr/12)

fig, (ax1, ax2) = plt.subplots(2,1, figsize=(9,6.5), sharex=True)
ax1.plot(t, xout, color="#1f5fbf", linewidth=0.7)
ax1.set_title("Glissando: el to puja fins a la nota real (I=%.0f st, t=%.1f s)"%(I,t_gliss),
              fontweight="bold")
ax1.set_ylabel("amplitud"); ax1.grid(alpha=0.2); ax1.set_ylim(-1.3,1.3)

ax2.plot(t, f_inst, color="#c0392b", linewidth=2, label="freq. instantania")
ax2.axhline(F0, color="gray", ls="--", label="nota real F0=%.0f Hz"%F0)
ax2.axhline(F0*2**(-I/12), color="gray", ls=":", label="inici (-%.0f st)"%I)
ax2.axvline(t_gliss, color="#2e7d32", ls="--", alpha=0.7)
ax2.text(t_gliss+0.01, F0*0.97, "fi del\nlliscament", fontsize=8, color="#2e7d32")
ax2.set_xlabel("temps (s)"); ax2.set_ylabel("frequencia (Hz)")
ax2.legend(fontsize=8, loc="lower right"); ax2.grid(alpha=0.2)
fig.tight_layout()
fig.savefig("efecte_glissando.png", dpi=150)
print("OK")
