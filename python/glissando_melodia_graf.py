import numpy as np
import matplotlib.pyplot as plt

FS = 44100.0
I_semis = 4.0      # semitons per sota a l'inici de cada nota
t_gliss = 0.3      # durada del lliscament

def midi_to_freq(note):
    return 440.0 * 2**((note-69)/12)

# Notes de glissando_melodia.sco (canal 1): 53, 57, 60, 65
# durades aproximades en segons (240 i 360 ticks a ~4.17 ms/tick)
notes = [53, 57, 60, 65]
durades = [0.5, 0.5, 0.5, 0.75]

f_target = [midi_to_freq(n) for n in notes]

# Construim la frequencia instantania al llarg del temps
fs_list = []
t_list = []
t_acum = 0
for f0, dur in zip(f_target, durades):
    n = int(dur*FS)
    tt = np.arange(n)/FS
    n_total = t_gliss*FS
    semis = np.where(np.arange(n) < n_total,
                     -I_semis*(1 - np.arange(n)/n_total), 0.0)
    f_inst = f0 * 2**(semis/12)
    fs_list.append(f_inst)
    t_list.append(tt + t_acum)
    t_acum += dur

t_all = np.concatenate(t_list)
f_all = np.concatenate(fs_list)

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(t_all, f_all, color="#c0392b", linewidth=2, label="freq. instantania")

# Marquem les notes objectiu amb linies puntejades
for f0, n in zip(f_target, notes):
    ax.axhline(f0, color="gray", ls=":", linewidth=0.8, alpha=0.6)
    ax.text(t_all[-1]*1.01, f0, "nota %d"%n, fontsize=8, va="center", color="gray")

ax.set_title("Glissando en melodia: el to llisca des de 4 semitons avall fins a cada nota",
             fontsize=12, fontweight="bold")
ax.set_xlabel("temps (s)")
ax.set_ylabel("frequencia (Hz)")
ax.legend(loc="upper left", fontsize=9)
ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig("efecte_glissando_melodia.png", dpi=150)
print("Guardat: efecte_glissando_melodia.png")
