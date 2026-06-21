#include <iostream>
#include <math.h>
#include "glissando.h"
#include "keyvalue.h"
#include "instrument.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

/*
  GLISSANDO (efecte de pitch slide, estil trombo).

  El senyal d'entrada conte la nota REAL (la frequencia correcta). L'efecte
  fa que, durant els primers 't' segons, el to comenci 'I' semitons per sota
  i pugi de forma continua fins a la nota real; despres es mante fixe.

  Per modificar el pitch recorrem el senyal a velocitat variable: si volem
  multiplicar el pitch per un factor K, avancem K mostres per cada mostra de
  sortida. Com que el factor de pitch va de 2^(-I/12) (avall) fins a 1, sempre
  tenim K <= 1: avancem MENYS d'una mostra per sortida, de manera que mai ens
  quedem sense mostres d'entrada (el sistema es causal sense buffer inicial).
  Igualment, guardem en un buffer les mostres d'entrada que no consumim, per
  no perdre continuitat entre blocs.

  Factor de pitch en funcio del temps (rampa lineal en semitons):
      semitons(n) = -I * (1 - n/n_total)      per n < n_total   (de -I cap a 0)
      semitons(n) =  0                         per n >= n_total
      K(n) = 2^(semitons(n)/12)
*/

Glissando::Glissando(const std::string &param) {
  KeyValue kv(param);

  if (!kv.to_float("I", I))
    I = 4;          // per defecte, comenca 4 semitons per sota

  if (!kv.to_float("t", t_gliss))
    t_gliss = 0.3;  // durada del lliscament per defecte (s)

  if (!kv.to_float("fm", fm))
    fm = 0;         // no s'usa, nomes per compatibilitat

  fase_sen = 0;
  n_global = 0;
  n_total = (long double) t_gliss * SamplingRate;
  if (n_total < 1) n_total = 1;
}

void Glissando::command(unsigned int cmd) {
  // En posar-se en marxa l'efecte (o en reiniciar-lo) tornem a comencar
  // el lliscament des del principi.
  fase_sen = 0;
  n_global = 0;
  if (cmd == 0) buffer.resize(0);
}

void Glissando::operator()(std::vector<float> &x) {
  std::vector<float> xout(x.size());
  unsigned int tot = 0;
  float xant, xpos, rho;

  // Factor de pitch actual segons el comptador global de mostres
  // (es recalcula mostra a mostra perque varia amb el temps).
  // Mentre fase_sen apunti dins del buffer, llegim del buffer.
  for (tot = 0; fase_sen < buffer.size() && tot < x.size(); tot++) {
    xant = buffer[(int) fase_sen];
    xpos = ((unsigned int)(fase_sen + 1) < buffer.size()
              ? buffer[(int) fase_sen + 1] : x[0]);
    rho = fase_sen - (int) fase_sen;
    xout[tot] = xant + rho * (xpos - xant);

    // Factor de pitch K(n)
    long double semis = (n_global < n_total)
                          ? -I * (1.0L - n_global / n_total) : 0.0L;
    long double K = pow(2.0L, semis / 12.0L);

    fase_sen += K;
    n_global += 1;
  }

  // Quan hem consumit el buffer, ajustem index i el buidem
  if (fase_sen >= buffer.size() && buffer.size() > 0) {
    fase_sen -= buffer.size();
    buffer.resize(0);
  }

  // Completem la sortida amb mostres del vector actual
  while (tot < x.size()) {
    if (fase_sen < x.size() - 1) {
      xant = x[(int) fase_sen];
      xpos = x[(int) fase_sen + 1];
      rho = fase_sen - (int) fase_sen;
    }
    else {
      // a prop del final, extrapolem amb les dues ultimes mostres
      xant = x[(int) fase_sen - 1];
      xpos = x[(int) fase_sen];
      rho = fase_sen - (int) fase_sen + 1;
    }
    xout[tot] = xant + rho * (xpos - xant);

    long double semis = (n_global < n_total)
                          ? -I * (1.0L - n_global / n_total) : 0.0L;
    long double K = pow(2.0L, semis / 12.0L);

    if (++tot < x.size()) {
      fase_sen += K;
      n_global += 1;
    }
  }

  // Guardem al buffer les mostres del vector actual que no hem consumit,
  // per mantenir la continuitat al seguent bloc.
  if ((int) fase_sen < (int) x.size())
    buffer.insert(buffer.end(), x.begin() + (int) fase_sen, x.end());
  fase_sen -= (int) fase_sen;

  // Copiem el resultat a x
  x = xout;
}
