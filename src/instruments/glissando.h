#ifndef GLISSANDO_H
#define GLISSANDO_H

#include <vector>
#include <string>
#include "effect.h"

namespace upc {
  class Glissando: public upc::Effect {
    private:
      float I;          // semitons d'extensio del lliscament (s'arriba des de -I)
      float t_gliss;    // durada del lliscament en segons
      float fm;         // (no usat aqui, reservat per compatibilitat de parametres)

      long double fase_sen;     // index de lectura (real) dins del senyal/buffer
      long double n_global;     // comptador de mostres des de l'inici de la nota
      long double n_total;      // mostres totals que dura el lliscament
      std::vector<float> buffer; // mostres pendents (com al vibrato)
    public:
      Glissando(const std::string &param = "");
      void operator()(std::vector<float> &x);
      void command(unsigned int);
  };
}

#endif
