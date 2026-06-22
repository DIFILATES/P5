#ifndef INSTRUMENT_FM_H
#define INSTRUMENT_FM_H

#include <vector>
#include <string>
#include "instrument.h"
#include "envelope_adsr.h"

namespace upc {
  class InstrumentFM: public upc::Instrument {
    EnvelopeADSR adsr;

    float N1, N2;     // relacio portadora/moduladora respecte la fonamental
    float I;          // index de modulacio MAXIM en semitons (a l'atac)
    float Imin;       // index de modulacio MINIM en semitons (al final)

    float A;          // amplitud (velocity)
    float fc, fm;     // frequencies de portadora i moduladora (Hz) de la nota
    float Imax_lin;   // index lineal maxim (calculat a partir d'I i la nota)
    float Imin_lin;   // index lineal minim (calculat a partir d'Imin i la nota)

    float fase_c;     // fase de la portadora
    float fase_m;     // fase de la moduladora
    float inc_c;      // increment de fase de la portadora per mostra
    float inc_m;      // increment de fase de la moduladora per mostra

  public:
    InstrumentFM(const std::string &param = "");
    void command(long cmd, long note, long velocity = 1);
    const std::vector<float> & synthesize();
    bool is_active() const {return bActive;}
  };
}

#endif
