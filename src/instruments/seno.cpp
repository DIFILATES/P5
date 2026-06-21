#include <iostream>
#include <math.h>
#include "seno.h"
#include "keyvalue.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

Seno::Seno(const std::string &param)
  : adsr(SamplingRate, param) {
  bActive = false;
  x.resize(BSIZE);

 
  KeyValue kv(param);
  int N;

  if (!kv.to_int("N", N))
    N = 40; 

  tbl.resize(N);
  float phase = 0, step_tbl = 2 * M_PI / (float) N;
  fase = 0;
  for (int i = 0; i < N; ++i) {
    tbl[i] = sin(phase);
    phase += step_tbl;
  }
}


void Seno::command(long cmd, long note, long vel) {
  if (cmd == 9) {      
    bActive = true;
    adsr.start();
    fase = 0;
    A = vel / 127.;
    step = 440 * pow(2, (note - 69) / 12.) * tbl.size() / SamplingRate;
  }
  else if (cmd == 8) {  
    adsr.stop();
  }
  else if (cmd == 0) {  
    adsr.end();
  }
}


const vector<float> & Seno::synthesize() {
  if (not adsr.active()) {
    x.assign(x.size(), 0);
    bActive = false;
    return x;
  }
  else if (not bActive)
    return x;

  for (unsigned int i = 0; i < x.size(); ++i) {
    int idx = (int)(fase + 0.5);
    if (idx >= (int)tbl.size()) idx -= tbl.size();   
    x[i] = A * tbl[idx];

    fase += step;
    while (fase >= tbl.size())
      fase -= tbl.size();   
  }
  adsr(x); 

  return x;
}
