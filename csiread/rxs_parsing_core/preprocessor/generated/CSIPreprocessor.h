#ifndef CSIPREPROCESSOR_H
#define CSIPREPROCESSOR_H

// Include Files
#include "rtwtypes.h"
#include "coder_array.h"
#include <cstddef>
#include <cstdlib>

// Function Declarations
extern void CSIPreprocessor(const coder::array<creal_T, 2U> &CSI, const coder::
  array<short, 1U> &subcarrierIndex_int16, coder::array<creal_T, 2U> &resultCSI,
  coder::array<double, 2U> &resultMag, coder::array<double, 2U> &resultPhase,
  coder::array<short, 1U> &interpedIndex_int16);
extern void CSIPreprocessor_initialize();
extern void CSIPreprocessor_terminate();

#endif

//
// File trailer for CSIPreprocessor.h
//
// [EOF]
//
