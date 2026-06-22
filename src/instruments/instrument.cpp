#include <iostream>
#include "instrument_dumb.h"
#include "seno.h" 
#include "instrument_fm.h"

/*
  For each new instrument:
  - Add the header in this file
  - Add the call to the constructor in get_instrument() (also in this file)
  - Add the source file to src/meson.build
*/

using namespace std;

namespace upc {
  Instrument * get_instrument(const string &name,
			      const string &parameters) {
    Instrument * pInst = 0;
    //    cout << name << ": " << parameters << endl;
    if (name == "dumb") {
      pInst = (Instrument *) new InstrumentDumb(parameters);
    }
    else if (name == "seno") {              // <-- AÑADIR
      pInst = (Instrument *) new Seno(parameters);   // <-- AÑADIR
    }
    else if (name == "fm") {
      pInst = (Instrument *) new InstrumentFM(parameters);
    }
    return pInst;
  }
}
