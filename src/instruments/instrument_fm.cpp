#include <iostream>
#include <math.h>
#include "instrument_fm.h"
#include "keyvalue.h"

#include <stdlib.h>

using namespace upc;
using namespace std;


InstrumentFM::InstrumentFM(const std::string &param)
  : adsr(SamplingRate, param) {
  bActive = false;
  x.resize(BSIZE);

  KeyValue kv(param);

  if (!kv.to_float("N1", N1)) N1 = 1;
  if (!kv.to_float("N2", N2)) N2 = 1;
  if (!kv.to_float("I", I))   I  = 1;     // index maxim (semitons)
  if (!kv.to_float("Imin", Imin)) Imin = 0; // index minim (semitons)

  fase_c = fase_m = 0;
}


void InstrumentFM::command(long cmd, long note, long vel) {
  if (cmd == 9) {       //'Key' pressed: comenca l'atac
    bActive = true;
    adsr.start();
    A = vel / 127.;
    fase_c = fase_m = 0;

    // Frequencia fonamental de la nota MIDI
    float f0 = 440. * pow(2, (note - 69) / 12.);

    // Portadora i moduladora segons la relacio N1:N2
    fc = f0 * N1;
    fm = f0 * N2;

    // Indexs de modulacio lineals (maxim i minim) a partir dels semitons:
    //   I_lin = (fc/fm) * (2^(I/12) - 1)
    if (fm > 0) {
      Imax_lin = (fc / fm) * (pow(2, I    / 12.) - 1);
      Imin_lin = (fc / fm) * (pow(2, Imin / 12.) - 1);
    }
    else {
      Imax_lin = Imin_lin = 0;
    }

    // Increments de fase per mostra
    inc_c = 2 * M_PI * fc / SamplingRate;
    inc_m = 2 * M_PI * fm / SamplingRate;
  }
  else if (cmd == 8) {  //'Key' released: comenca el release
    adsr.stop();
  }
  else if (cmd == 0) {  //Final immediat de la nota
    adsr.end();
  }
}


const vector<float> & InstrumentFM::synthesize() {
  if (not adsr.active()) {
    x.assign(x.size(), 0);
    bActive = false;
    return x;
  }
  else if (not bActive)
    return x;

  // 1) Obtenim la forma de l'envolvent ADSR per a aquest bloc.
  //    Passant un vector de uns a adsr(), el resultat es la propia envolvent
  //    (perque adsr multiplica el vector per la forma ADSR).
  vector<float> env(x.size(), 1.0);
  adsr(env);  

  // 2) Sintesi FM amb index variable segons l'envolvent
  for (unsigned int i = 0; i < x.size(); ++i) {
    // Index instantani: interpola entre Imin_lin i Imax_lin segons env[i]
    float I_inst = Imin_lin + env[i] * (Imax_lin - Imin_lin);

    // Senyal FM, escalat per amplitud i per la propia envolvent
    x[i] = A * env[i] * sin(fase_c + I_inst * sin(fase_m));

    fase_c += inc_c;
    fase_m += inc_m;
    while (fase_c >= 2 * M_PI) fase_c -= 2 * M_PI;
    while (fase_m >= 2 * M_PI) fase_m -= 2 * M_PI;
  }

  return x;
}
