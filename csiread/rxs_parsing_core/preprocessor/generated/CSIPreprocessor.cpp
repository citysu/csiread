// Include Files
#include "CSIPreprocessor.h"
#include "rt_nonfinite.h"
#include "coder_array.h"
#include "rt_defines.h"
#include <cfloat>
#include <cmath>
#include <cstring>

// Function Declarations
namespace coder
{
  static void angle(const ::coder::array<creal_T, 2U> &x, ::coder::array<double,
                    2U> &y);
  static void b_abs(const ::coder::array<double, 1U> &x, ::coder::array<double,
                    1U> &y);
  static double b_abs(double x);
  static void b_abs(const ::coder::array<creal_T, 2U> &x, ::coder::array<double,
                    2U> &y);
  static void b_exp(::coder::array<creal_T, 2U> &x);
  static void b_fix(double *x);
  static void b_floor(double *x);
  static boolean_T b_isfinite(double x);
  static boolean_T b_isinf(double x);
  static boolean_T b_isnan(double x);
  static double b_rem(double x);
  static void b_round(double *x);
  static void eml_find(const ::coder::array<boolean_T, 1U> &x, int i_data[], int
                       i_size[1]);
  static void eml_float_colon(double a, double b, ::coder::array<double, 2U> &y);
  static void flip(::coder::array<double, 2U> &x);
  static void flip(::coder::array<double, 1U> &x);
  static void float_colon_length(double a, double b, int *n, double *anew,
    double *bnew, boolean_T *n_too_large);
  namespace internal
  {
    static int b_bsearch(const ::coder::array<double, 1U> &x, double xi);
    static int computeDimsData(int nx, double varargin_1);
    static void merge(::coder::array<int, 1U> &idx, ::coder::array<double, 1U>
                      &x, int offset, int np, int nq, ::coder::array<int, 1U>
                      &iwork, ::coder::array<double, 1U> &xwork);
    static void merge_block(::coder::array<int, 1U> &idx, ::coder::array<double,
      1U> &x, int offset, int n, int preSortLevel, ::coder::array<int, 1U>
      &iwork, ::coder::array<double, 1U> &xwork);
    static void merge_pow2_block(::coder::array<int, 1U> &idx, ::coder::array<
      double, 1U> &x, int offset);
    static double minimum(const ::coder::array<double, 1U> &x);
    static int nonSingletonDim(const ::coder::array<double, 1U> &x);
    static int nonSingletonDim(const ::coder::array<double, 2U> &x);
    static void num2cell_vector(const int num[2], int cell_vector[2]);
    namespace scalar
    {
      static double b_angle(const creal_T x);
      static double b_atan2(double y, double x);
      static double c_abs(const creal_T x);
      static double c_abs(double x);
      static void c_exp(creal_T *x);
      static void c_fix(double *x);
      static void c_floor(double *x);
      static double c_rem(double x);
      static void c_round(double *x);
    }

    static void sort(::coder::array<double, 1U> &x);
    static void sortIdx(::coder::array<double, 1U> &x, ::coder::array<int, 1U>
                        &idx);
    static double xdlapy2(double x1, double x2);
  }

  static void interp1(const ::coder::array<double, 1U> &varargin_1, const ::
                      coder::array<double, 2U> &varargin_2, const ::coder::array<
                      double, 1U> &varargin_3, ::coder::array<double, 2U> &Vq);
  static void interp1(const ::coder::array<double, 1U> &varargin_1, const ::
                      coder::array<double, 1U> &varargin_2, const ::coder::array<
                      double, 2U> &varargin_3, ::coder::array<double, 2U> &Vq);
  static void interp1_work(::coder::array<double, 1U> &y, const ::coder::array<
    double, 2U> &xi, ::coder::array<double, 1U> &x, ::coder::array<double, 2U>
    &yi);
  static void interp1_work(::coder::array<double, 2U> &y, const ::coder::array<
    double, 1U> &xi, ::coder::array<double, 1U> &x, ::coder::array<double, 2U>
    &yi);
  static double maxabs(double a, double b);
  static void repmat(const ::coder::array<double, 2U> &a, double varargin_1, ::
                     coder::array<double, 2U> &b);
  static void unwrap(::coder::array<double, 2U> &p);
  static void unwrap_vector(::coder::array<double, 1U> &p);
}

static int div_s32(int numerator, int denominator);
static void magPhase2CSI(const coder::array<double, 2U> &mag, const coder::array<
  double, 2U> &phase, coder::array<creal_T, 2U> &csi);
static double rt_atan2d_snf(double u0, double u1);
static double rt_hypotd_snf(double u0, double u1);
static double rt_remd_snf(double u0, double u1);

// Function Definitions
//
// Arguments    : const ::coder::array<creal_T, 2U> &x
//                ::coder::array<double, 2U> &y
// Return Type  : void
//
namespace coder
{
  static void angle(const ::coder::array<creal_T, 2U> &x, ::coder::array<double,
                    2U> &y)
  {
    int nx;
    nx = x.size(0) * x.size(1);
    y.set_size(x.size(0), x.size(1));
    for (int k = 0; k < nx; k++) {
      y[k] = internal::scalar::b_angle(x[k]);
    }
  }

  //
  // Arguments    : const ::coder::array<double, 1U> &x
  //                ::coder::array<double, 1U> &y
  // Return Type  : void
  //
  static void b_abs(const ::coder::array<double, 1U> &x, ::coder::array<double,
                    1U> &y)
  {
    int nx;
    nx = x.size(0);
    y.set_size(x.size(0));
    for (int k = 0; k < nx; k++) {
      y[k] = internal::scalar::c_abs(x[k]);
    }
  }

  //
  // Arguments    : double x
  // Return Type  : double
  //
  static double b_abs(double x)
  {
    return internal::scalar::c_abs(x);
  }

  //
  // Arguments    : const ::coder::array<creal_T, 2U> &x
  //                ::coder::array<double, 2U> &y
  // Return Type  : void
  //
  static void b_abs(const ::coder::array<creal_T, 2U> &x, ::coder::array<double,
                    2U> &y)
  {
    int nx;
    nx = x.size(0) * x.size(1);
    y.set_size(x.size(0), x.size(1));
    for (int k = 0; k < nx; k++) {
      y[k] = internal::scalar::c_abs(x[k]);
    }
  }

  //
  // Arguments    : ::coder::array<creal_T, 2U> &x
  // Return Type  : void
  //
  static void b_exp(::coder::array<creal_T, 2U> &x)
  {
    int nx;
    nx = x.size(0) * x.size(1);
    for (int k = 0; k < nx; k++) {
      internal::scalar::c_exp(&x[k]);
    }
  }

  //
  // Arguments    : double *x
  // Return Type  : void
  //
  static void b_fix(double *x)
  {
    internal::scalar::c_fix(x);
  }

  //
  // Arguments    : double *x
  // Return Type  : void
  //
  static void b_floor(double *x)
  {
    internal::scalar::c_floor(x);
  }

  //
  // Arguments    : double x
  // Return Type  : boolean_T
  //
  static boolean_T b_isfinite(double x)
  {
    return (!b_isinf(x)) && (!b_isnan(x));
  }

  //
  // Arguments    : double x
  // Return Type  : boolean_T
  //
  static boolean_T b_isinf(double x)
  {
    return std::isinf(x);
  }

  //
  // Arguments    : double x
  // Return Type  : boolean_T
  //
  static boolean_T b_isnan(double x)
  {
    return std::isnan(x);
  }

  //
  // Arguments    : double x
  // Return Type  : double
  //
  static double b_rem(double x)
  {
    return internal::scalar::c_rem(x);
  }

  //
  // Arguments    : double *x
  // Return Type  : void
  //
  static void b_round(double *x)
  {
    internal::scalar::c_round(x);
  }

  //
  // Arguments    : const ::coder::array<boolean_T, 1U> &x
  //                int i_data[]
  //                int i_size[1]
  // Return Type  : void
  //
  static void eml_find(const ::coder::array<boolean_T, 1U> &x, int i_data[], int
                       i_size[1])
  {
    int idx;
    int ii;
    int k;
    boolean_T exitg1;
    k = (1 <= x.size(0));
    idx = 0;
    i_size[0] = k;
    ii = 0;
    exitg1 = false;
    while ((!exitg1) && (ii <= x.size(0) - 1)) {
      if (x[ii]) {
        idx = 1;
        i_data[0] = ii + 1;
        exitg1 = true;
      } else {
        ii++;
      }
    }

    if (k == 1) {
      if (idx == 0) {
        i_size[0] = 0;
      }
    } else {
      i_size[0] = (1 <= idx);
    }
  }

  //
  // Arguments    : double a
  //                double b
  //                ::coder::array<double, 2U> &y
  // Return Type  : void
  //
  static void eml_float_colon(double a, double b, ::coder::array<double, 2U> &y)
  {
    double a1;
    double b1;
    int n;
    boolean_T n_too_large;
    float_colon_length(a, b, &n, &a1, &b1, &n_too_large);
    y.set_size(1, n);
    if (n > 0) {
      y[0] = a1;
      if (n > 1) {
        int nm1d2;
        y[n - 1] = b1;
        nm1d2 = (n - 1) / 2;
        for (int k = 0; k <= nm1d2 - 2; k++) {
          y[k + 1] = a1 + (static_cast<double>(k) + 1.0);
          y[(n - k) - 2] = b1 - (static_cast<double>(k) + 1.0);
        }

        if (nm1d2 << 1 == n - 1) {
          y[nm1d2] = (a1 + b1) / 2.0;
        } else {
          y[nm1d2] = a1 + static_cast<double>(nm1d2);
          y[nm1d2 + 1] = b1 - static_cast<double>(nm1d2);
        }
      }
    }
  }

  //
  // Arguments    : ::coder::array<double, 2U> &x
  // Return Type  : void
  //
  static void flip(::coder::array<double, 2U> &x)
  {
    if ((x.size(0) != 0) && (x.size(1) != 0) && (x.size(0) > 1)) {
      int i;
      int n;
      int nd2;
      int vlen;
      vlen = x.size(0);
      n = x.size(0) - 1;
      nd2 = x.size(0) >> 1;
      i = x.size(1) - 1;
      for (int j = 0; j <= i; j++) {
        int offset;
        offset = j * vlen;
        for (int k = 0; k < nd2; k++) {
          double tmp;
          int i1;
          int tmp_tmp;
          tmp_tmp = offset + k;
          tmp = x[tmp_tmp];
          i1 = (offset + n) - k;
          x[tmp_tmp] = x[i1];
          x[i1] = tmp;
        }
      }
    }
  }

  //
  // Arguments    : ::coder::array<double, 1U> &x
  // Return Type  : void
  //
  static void flip(::coder::array<double, 1U> &x)
  {
    if ((x.size(0) != 0) && (x.size(0) > 1)) {
      int n;
      int nd2;
      n = x.size(0) - 1;
      nd2 = x.size(0) >> 1;
      for (int k = 0; k < nd2; k++) {
        double tmp;
        tmp = x[k];
        x[k] = x[n - k];
        x[n - k] = tmp;
      }
    }
  }

  //
  // Arguments    : double a
  //                double b
  //                int *n
  //                double *anew
  //                double *bnew
  //                boolean_T *n_too_large
  // Return Type  : void
  //
  static void float_colon_length(double a, double b, int *n, double *anew,
    double *bnew, boolean_T *n_too_large)
  {
    double cdiff;
    double ndbl;
    *anew = a;
    ndbl = (b - a) + 0.5;
    b_floor(&ndbl);
    *bnew = a + ndbl;
    cdiff = *bnew - b;
    if (b_abs(cdiff) < 4.4408920985006262E-16 * maxabs(a, b)) {
      ndbl++;
      *bnew = b;
    } else if (cdiff > 0.0) {
      *bnew = a + (ndbl - 1.0);
    } else {
      ndbl++;
    }

    *n_too_large = false;
    if (ndbl >= 0.0) {
      *n = static_cast<int>(std::floor(ndbl));
    } else {
      *n = 0;
    }
  }

  //
  // Arguments    : const ::coder::array<double, 1U> &x
  //                double xi
  // Return Type  : int
  //
  namespace internal
  {
    static int b_bsearch(const ::coder::array<double, 1U> &x, double xi)
    {
      int high_i;
      int low_ip1;
      int n;
      high_i = x.size(0);
      n = 1;
      low_ip1 = 2;
      while (high_i > low_ip1) {
        int mid_i;
        mid_i = (n >> 1) + (high_i >> 1);
        if (((n & 1) == 1) && ((high_i & 1) == 1)) {
          mid_i++;
        }

        if (xi >= x[mid_i - 1]) {
          n = mid_i;
          low_ip1 = mid_i + 1;
        } else {
          high_i = mid_i;
        }
      }

      return n;
    }

    //
    // Arguments    : int nx
    //                double varargin_1
    // Return Type  : int
    //
    static int computeDimsData(int nx, double varargin_1)
    {
      int calclen;
      if (static_cast<int>(varargin_1) > 0) {
        calclen = div_s32(nx, static_cast<int>(varargin_1));
      } else {
        calclen = 0;
      }

      return calclen;
    }

    //
    // Arguments    : ::coder::array<int, 1U> &idx
    //                ::coder::array<double, 1U> &x
    //                int offset
    //                int np
    //                int nq
    //                ::coder::array<int, 1U> &iwork
    //                ::coder::array<double, 1U> &xwork
    // Return Type  : void
    //
    static void merge(::coder::array<int, 1U> &idx, ::coder::array<double, 1U>
                      &x, int offset, int np, int nq, ::coder::array<int, 1U>
                      &iwork, ::coder::array<double, 1U> &xwork)
    {
      if (nq != 0) {
        int iout;
        int j;
        int n_tmp;
        int p;
        int q;
        n_tmp = np + nq;
        for (j = 0; j < n_tmp; j++) {
          iout = offset + j;
          iwork[j] = idx[iout];
          xwork[j] = x[iout];
        }

        p = 0;
        q = np;
        iout = offset - 1;
        int exitg1;
        do {
          exitg1 = 0;
          iout++;
          if (xwork[p] <= xwork[q]) {
            idx[iout] = iwork[p];
            x[iout] = xwork[p];
            if (p + 1 < np) {
              p++;
            } else {
              exitg1 = 1;
            }
          } else {
            idx[iout] = iwork[q];
            x[iout] = xwork[q];
            if (q + 1 < n_tmp) {
              q++;
            } else {
              q = iout - p;
              for (j = p + 1; j <= np; j++) {
                iout = q + j;
                idx[iout] = iwork[j - 1];
                x[iout] = xwork[j - 1];
              }

              exitg1 = 1;
            }
          }
        } while (exitg1 == 0);
      }
    }

    //
    // Arguments    : ::coder::array<int, 1U> &idx
    //                ::coder::array<double, 1U> &x
    //                int offset
    //                int n
    //                int preSortLevel
    //                ::coder::array<int, 1U> &iwork
    //                ::coder::array<double, 1U> &xwork
    // Return Type  : void
    //
    static void merge_block(::coder::array<int, 1U> &idx, ::coder::array<double,
      1U> &x, int offset, int n, int preSortLevel, ::coder::array<int, 1U>
      &iwork, ::coder::array<double, 1U> &xwork)
    {
      int bLen;
      int nPairs;
      nPairs = n >> preSortLevel;
      bLen = 1 << preSortLevel;
      while (nPairs > 1) {
        int nTail;
        int tailOffset;
        if ((nPairs & 1) != 0) {
          nPairs--;
          tailOffset = bLen * nPairs;
          nTail = n - tailOffset;
          if (nTail > bLen) {
            merge(idx, x, offset + tailOffset, bLen, nTail - bLen, iwork, xwork);
          }
        }

        tailOffset = bLen << 1;
        nPairs >>= 1;
        for (nTail = 0; nTail < nPairs; nTail++) {
          merge(idx, x, offset + nTail * tailOffset, bLen, bLen, iwork, xwork);
        }

        bLen = tailOffset;
      }

      if (n > bLen) {
        merge(idx, x, offset, bLen, n - bLen, iwork, xwork);
      }
    }

    //
    // Arguments    : ::coder::array<int, 1U> &idx
    //                ::coder::array<double, 1U> &x
    //                int offset
    // Return Type  : void
    //
    static void merge_pow2_block(::coder::array<int, 1U> &idx, ::coder::array<
      double, 1U> &x, int offset)
    {
      double xwork[256];
      int iwork[256];
      int iout;
      for (int b = 0; b < 6; b++) {
        int bLen;
        int bLen2;
        int nPairs;
        bLen = 1 << (b + 2);
        bLen2 = bLen << 1;
        nPairs = 256 >> (b + 3);
        for (int k = 0; k < nPairs; k++) {
          int blockOffset;
          int j;
          int p;
          int q;
          blockOffset = offset + k * bLen2;
          for (j = 0; j < bLen2; j++) {
            iout = blockOffset + j;
            iwork[j] = idx[iout];
            xwork[j] = x[iout];
          }

          p = 0;
          q = bLen;
          iout = blockOffset - 1;
          int exitg1;
          do {
            exitg1 = 0;
            iout++;
            if (xwork[p] <= xwork[q]) {
              idx[iout] = iwork[p];
              x[iout] = xwork[p];
              if (p + 1 < bLen) {
                p++;
              } else {
                exitg1 = 1;
              }
            } else {
              idx[iout] = iwork[q];
              x[iout] = xwork[q];
              if (q + 1 < bLen2) {
                q++;
              } else {
                iout -= p;
                for (j = p + 1; j <= bLen; j++) {
                  q = iout + j;
                  idx[q] = iwork[j - 1];
                  x[q] = xwork[j - 1];
                }

                exitg1 = 1;
              }
            }
          } while (exitg1 == 0);
        }
      }
    }

    //
    // Arguments    : const ::coder::array<double, 1U> &x
    // Return Type  : double
    //
    static double minimum(const ::coder::array<double, 1U> &x)
    {
      double ex;
      int n;
      n = x.size(0);
      if (x.size(0) <= 2) {
        if (x.size(0) == 1) {
          ex = x[0];
        } else if ((x[0] > x[1]) || (b_isnan(x[0]) && (!b_isnan(x[1])))) {
          ex = x[1];
        } else {
          ex = x[0];
        }
      } else {
        int idx;
        int k;
        if (!b_isnan(x[0])) {
          idx = 1;
        } else {
          boolean_T exitg1;
          idx = 0;
          k = 2;
          exitg1 = false;
          while ((!exitg1) && (k <= x.size(0))) {
            if (!b_isnan(x[k - 1])) {
              idx = k;
              exitg1 = true;
            } else {
              k++;
            }
          }
        }

        if (idx == 0) {
          ex = x[0];
        } else {
          ex = x[idx - 1];
          idx++;
          for (k = idx; k <= n; k++) {
            double d;
            d = x[k - 1];
            if (ex > d) {
              ex = d;
            }
          }
        }
      }

      return ex;
    }

    //
    // Arguments    : const ::coder::array<double, 1U> &x
    // Return Type  : int
    //
    static int nonSingletonDim(const ::coder::array<double, 1U> &x)
    {
      int dim;
      dim = 2;
      if (x.size(0) != 1) {
        dim = 1;
      }

      return dim;
    }

    //
    // Arguments    : const ::coder::array<double, 2U> &x
    // Return Type  : int
    //
    static int nonSingletonDim(const ::coder::array<double, 2U> &x)
    {
      int dim;
      dim = 2;
      if (x.size(0) != 1) {
        dim = 1;
      }

      return dim;
    }

    //
    // Arguments    : const int num[2]
    //                int cell_vector[2]
    // Return Type  : void
    //
    static void num2cell_vector(const int num[2], int cell_vector[2])
    {
      cell_vector[0] = num[0];
      cell_vector[1] = num[1];
    }

    //
    // Arguments    : const creal_T x
    // Return Type  : double
    //
    namespace scalar
    {
      static double b_angle(const creal_T x)
      {
        return b_atan2(x.im, x.re);
      }

      //
      // Arguments    : double y
      //                double x
      // Return Type  : double
      //
      static double b_atan2(double y, double x)
      {
        return rt_atan2d_snf(y, x);
      }

      //
      // Arguments    : const creal_T x
      // Return Type  : double
      //
      static double c_abs(const creal_T x)
      {
        return xdlapy2(x.re, x.im);
      }

      //
      // Arguments    : double x
      // Return Type  : double
      //
      static double c_abs(double x)
      {
        return std::abs(x);
      }

      //
      // Arguments    : creal_T *x
      // Return Type  : void
      //
      static void c_exp(creal_T *x)
      {
        if (x->im == 0.0) {
          x->re = std::exp(x->re);
          x->im = 0.0;
        } else if (b_isinf(x->im) && b_isinf(x->re) && (x->re < 0.0)) {
          x->re = 0.0;
          x->im = 0.0;
        } else {
          double d;
          double r;
          r = std::exp(x->re / 2.0);
          d = x->im;
          x->re = r * (r * std::cos(x->im));
          x->im = r * (r * std::sin(d));
        }
      }

      //
      // Arguments    : double *x
      // Return Type  : void
      //
      static void c_fix(double *x)
      {
        *x = std::trunc(*x);
      }

      //
      // Arguments    : double *x
      // Return Type  : void
      //
      static void c_floor(double *x)
      {
        *x = std::floor(*x);
      }

      //
      // Arguments    : double x
      // Return Type  : double
      //
      static double c_rem(double x)
      {
        return rt_remd_snf(x, 1.0);
      }

      //
      // Arguments    : double *x
      // Return Type  : void
      //
      static void c_round(double *x)
      {
        *x = std::round(*x);
      }

      //
      // Arguments    : ::coder::array<double, 1U> &x
      // Return Type  : void
      //
    }

    static void sort(::coder::array<double, 1U> &x)
    {
      array<double, 1U> vwork;
      array<int, 1U> b_vwork;
      int dim;
      int k;
      int vlen;
      int vstride;
      dim = nonSingletonDim(x);
      if (dim <= 1) {
        vstride = x.size(0);
      } else {
        vstride = 1;
      }

      vlen = vstride - 1;
      vwork.set_size(vstride);
      vstride = 1;
      for (k = 0; k <= dim - 2; k++) {
        vstride *= x.size(0);
      }

      for (dim = 0; dim < vstride; dim++) {
        for (k = 0; k <= vlen; k++) {
          vwork[k] = x[dim + k * vstride];
        }

        sortIdx(vwork, b_vwork);
        for (k = 0; k <= vlen; k++) {
          x[dim + k * vstride] = vwork[k];
        }
      }
    }

    //
    // Arguments    : ::coder::array<double, 1U> &x
    //                ::coder::array<int, 1U> &idx
    // Return Type  : void
    //
    static void sortIdx(::coder::array<double, 1U> &x, ::coder::array<int, 1U>
                        &idx)
    {
      array<double, 1U> xwork;
      array<int, 1U> iwork;
      double x4[4];
      int idx4[4];
      int i1;
      int ib;
      signed char perm[4];
      ib = x.size(0);
      idx.set_size(ib);
      for (i1 = 0; i1 < ib; i1++) {
        idx[i1] = 0;
      }

      if (x.size(0) != 0) {
        int b_n;
        int i3;
        int k;
        int n;
        n = x.size(0);
        b_n = x.size(0);
        x4[0] = 0.0;
        idx4[0] = 0;
        x4[1] = 0.0;
        idx4[1] = 0;
        x4[2] = 0.0;
        idx4[2] = 0;
        x4[3] = 0.0;
        idx4[3] = 0;
        iwork.set_size(ib);
        for (i1 = 0; i1 < ib; i1++) {
          iwork[i1] = 0;
        }

        ib = x.size(0);
        xwork.set_size(ib);
        for (i1 = 0; i1 < ib; i1++) {
          xwork[i1] = 0.0;
        }

        ib = 0;
        for (k = 0; k < b_n; k++) {
          ib++;
          idx4[ib - 1] = k + 1;
          x4[ib - 1] = x[k];
          if (ib == 4) {
            double d;
            double d1;
            int i4;
            if (x4[0] <= x4[1]) {
              i1 = 1;
              ib = 2;
            } else {
              i1 = 2;
              ib = 1;
            }

            if (x4[2] <= x4[3]) {
              i3 = 3;
              i4 = 4;
            } else {
              i3 = 4;
              i4 = 3;
            }

            d = x4[i1 - 1];
            d1 = x4[i3 - 1];
            if (d <= d1) {
              d = x4[ib - 1];
              if (d <= d1) {
                perm[0] = static_cast<signed char>(i1);
                perm[1] = static_cast<signed char>(ib);
                perm[2] = static_cast<signed char>(i3);
                perm[3] = static_cast<signed char>(i4);
              } else if (d <= x4[i4 - 1]) {
                perm[0] = static_cast<signed char>(i1);
                perm[1] = static_cast<signed char>(i3);
                perm[2] = static_cast<signed char>(ib);
                perm[3] = static_cast<signed char>(i4);
              } else {
                perm[0] = static_cast<signed char>(i1);
                perm[1] = static_cast<signed char>(i3);
                perm[2] = static_cast<signed char>(i4);
                perm[3] = static_cast<signed char>(ib);
              }
            } else {
              d1 = x4[i4 - 1];
              if (d <= d1) {
                if (x4[ib - 1] <= d1) {
                  perm[0] = static_cast<signed char>(i3);
                  perm[1] = static_cast<signed char>(i1);
                  perm[2] = static_cast<signed char>(ib);
                  perm[3] = static_cast<signed char>(i4);
                } else {
                  perm[0] = static_cast<signed char>(i3);
                  perm[1] = static_cast<signed char>(i1);
                  perm[2] = static_cast<signed char>(i4);
                  perm[3] = static_cast<signed char>(ib);
                }
              } else {
                perm[0] = static_cast<signed char>(i3);
                perm[1] = static_cast<signed char>(i4);
                perm[2] = static_cast<signed char>(i1);
                perm[3] = static_cast<signed char>(ib);
              }
            }

            idx[k - 3] = idx4[perm[0] - 1];
            idx[k - 2] = idx4[perm[1] - 1];
            idx[k - 1] = idx4[perm[2] - 1];
            idx[k] = idx4[perm[3] - 1];
            x[k - 3] = x4[perm[0] - 1];
            x[k - 2] = x4[perm[1] - 1];
            x[k - 1] = x4[perm[2] - 1];
            x[k] = x4[perm[3] - 1];
            ib = 0;
          }
        }

        if (ib > 0) {
          perm[1] = 0;
          perm[2] = 0;
          perm[3] = 0;
          if (ib == 1) {
            perm[0] = 1;
          } else if (ib == 2) {
            if (x4[0] <= x4[1]) {
              perm[0] = 1;
              perm[1] = 2;
            } else {
              perm[0] = 2;
              perm[1] = 1;
            }
          } else if (x4[0] <= x4[1]) {
            if (x4[1] <= x4[2]) {
              perm[0] = 1;
              perm[1] = 2;
              perm[2] = 3;
            } else if (x4[0] <= x4[2]) {
              perm[0] = 1;
              perm[1] = 3;
              perm[2] = 2;
            } else {
              perm[0] = 3;
              perm[1] = 1;
              perm[2] = 2;
            }
          } else if (x4[0] <= x4[2]) {
            perm[0] = 2;
            perm[1] = 1;
            perm[2] = 3;
          } else if (x4[1] <= x4[2]) {
            perm[0] = 2;
            perm[1] = 3;
            perm[2] = 1;
          } else {
            perm[0] = 3;
            perm[1] = 2;
            perm[2] = 1;
          }

          for (k = 0; k < ib; k++) {
            i1 = perm[k] - 1;
            i3 = (b_n - ib) + k;
            idx[i3] = idx4[i1];
            x[i3] = x4[i1];
          }
        }

        ib = 2;
        if (n > 1) {
          if (n >= 256) {
            ib = n >> 8;
            for (i1 = 0; i1 < ib; i1++) {
              merge_pow2_block(idx, x, i1 << 8);
            }

            ib <<= 8;
            i1 = n - ib;
            if (i1 > 0) {
              merge_block(idx, x, ib, i1, 2, iwork, xwork);
            }

            ib = 8;
          }

          merge_block(idx, x, 0, n, ib, iwork, xwork);
        }
      }
    }

    //
    // Arguments    : double x1
    //                double x2
    // Return Type  : double
    //
    static double xdlapy2(double x1, double x2)
    {
      return rt_hypotd_snf(x1, x2);
    }

    //
    // Arguments    : const ::coder::array<double, 1U> &varargin_1
    //                const ::coder::array<double, 1U> &varargin_2
    //                const ::coder::array<double, 2U> &varargin_3
    //                ::coder::array<double, 2U> &Vq
    // Return Type  : void
    //
  }

  static void interp1(const ::coder::array<double, 1U> &varargin_1, const ::
                      coder::array<double, 1U> &varargin_2, const ::coder::array<
                      double, 2U> &varargin_3, ::coder::array<double, 2U> &Vq)
  {
    array<double, 1U> b_varargin_1;
    array<double, 1U> b_varargin_2;
    int i;
    int loop_ub;
    b_varargin_2.set_size(varargin_2.size(0));
    loop_ub = varargin_2.size(0) - 1;
    for (i = 0; i <= loop_ub; i++) {
      b_varargin_2[i] = varargin_2[i];
    }

    b_varargin_1.set_size(varargin_1.size(0));
    loop_ub = varargin_1.size(0) - 1;
    for (i = 0; i <= loop_ub; i++) {
      b_varargin_1[i] = varargin_1[i];
    }

    interp1_work(b_varargin_2, varargin_3, b_varargin_1, Vq);
  }

  //
  // Arguments    : const ::coder::array<double, 1U> &varargin_1
  //                const ::coder::array<double, 2U> &varargin_2
  //                const ::coder::array<double, 1U> &varargin_3
  //                ::coder::array<double, 2U> &Vq
  // Return Type  : void
  //
  static void interp1(const ::coder::array<double, 1U> &varargin_1, const ::
                      coder::array<double, 2U> &varargin_2, const ::coder::array<
                      double, 1U> &varargin_3, ::coder::array<double, 2U> &Vq)
  {
    array<double, 2U> b_varargin_2;
    array<double, 1U> b_varargin_1;
    int i;
    int loop_ub;
    b_varargin_2.set_size(varargin_2.size(0), varargin_2.size(1));
    loop_ub = varargin_2.size(0) * varargin_2.size(1) - 1;
    for (i = 0; i <= loop_ub; i++) {
      b_varargin_2[i] = varargin_2[i];
    }

    b_varargin_1.set_size(varargin_1.size(0));
    loop_ub = varargin_1.size(0) - 1;
    for (i = 0; i <= loop_ub; i++) {
      b_varargin_1[i] = varargin_1[i];
    }

    interp1_work(b_varargin_2, varargin_3, b_varargin_1, Vq);
  }

  //
  // Arguments    : ::coder::array<double, 1U> &y
  //                const ::coder::array<double, 2U> &xi
  //                ::coder::array<double, 1U> &x
  //                ::coder::array<double, 2U> &yi
  // Return Type  : void
  //
  static void interp1_work(::coder::array<double, 1U> &y, const ::coder::array<
    double, 2U> &xi, ::coder::array<double, 1U> &x, ::coder::array<double, 2U>
    &yi)
  {
    int k;
    int nx;
    int outsize_idx_1;
    nx = x.size(0) - 1;
    outsize_idx_1 = xi.size(1);
    yi.set_size(1, xi.size(1));
    for (k = 0; k < outsize_idx_1; k++) {
      yi[k] = rtNaN;
    }

    if (xi.size(1) != 0) {
      k = 0;
      int exitg1;
      do {
        exitg1 = 0;
        if (k <= nx) {
          if (b_isnan(x[k])) {
            exitg1 = 1;
          } else {
            k++;
          }
        } else {
          double xtmp;
          if (x[1] < x[0]) {
            k = (nx + 1) >> 1;
            for (outsize_idx_1 = 0; outsize_idx_1 < k; outsize_idx_1++) {
              xtmp = x[outsize_idx_1];
              x[outsize_idx_1] = x[nx - outsize_idx_1];
              x[nx - outsize_idx_1] = xtmp;
            }

            flip(y);
          }

          outsize_idx_1 = xi.size(1);
          for (k = 0; k < outsize_idx_1; k++) {
            xtmp = xi[k];
            if (b_isnan(xtmp)) {
              yi[k] = rtNaN;
            } else {
              if ((!(xtmp > x[x.size(0) - 1])) && (!(xtmp < x[0]))) {
                double r;
                nx = internal::b_bsearch(x, xtmp) - 1;
                r = (xtmp - x[nx]) / (x[nx + 1] - x[nx]);
                if (r == 0.0) {
                  yi[k] = y[nx];
                } else if (r == 1.0) {
                  yi[k] = y[nx + 1];
                } else {
                  xtmp = y[nx + 1];
                  if (y[nx] == xtmp) {
                    yi[k] = y[nx];
                  } else {
                    yi[k] = (1.0 - r) * y[nx] + r * xtmp;
                  }
                }
              }
            }
          }

          exitg1 = 1;
        }
      } while (exitg1 == 0);
    }
  }

  //
  // Arguments    : ::coder::array<double, 2U> &y
  //                const ::coder::array<double, 1U> &xi
  //                ::coder::array<double, 1U> &x
  //                ::coder::array<double, 2U> &yi
  // Return Type  : void
  //
  static void interp1_work(::coder::array<double, 2U> &y, const ::coder::array<
    double, 1U> &xi, ::coder::array<double, 1U> &x, ::coder::array<double, 2U>
    &yi)
  {
    int k;
    int nx;
    int nxi;
    int nycols;
    int nyrows;
    nyrows = y.size(0);
    nycols = y.size(1) - 1;
    nx = x.size(0) - 1;
    yi.set_size(xi.size(0), y.size(1));
    nxi = xi.size(0) * y.size(1);
    for (k = 0; k < nxi; k++) {
      yi[k] = rtNaN;
    }

    if (xi.size(0) != 0) {
      k = 0;
      int exitg1;
      do {
        exitg1 = 0;
        if (k <= nx) {
          if (b_isnan(x[k])) {
            exitg1 = 1;
          } else {
            k++;
          }
        } else {
          double xtmp;
          int b_j1;
          if (x[1] < x[0]) {
            k = (nx + 1) >> 1;
            for (b_j1 = 0; b_j1 < k; b_j1++) {
              xtmp = x[b_j1];
              nxi = nx - b_j1;
              x[b_j1] = x[nxi];
              x[nxi] = xtmp;
            }

            flip(y);
          }

          nxi = xi.size(0);
          for (k = 0; k < nxi; k++) {
            if (b_isnan(xi[k])) {
              for (b_j1 = 0; b_j1 <= nycols; b_j1++) {
                yi[k + b_j1 * nxi] = rtNaN;
              }
            } else {
              if ((!(xi[k] > x[x.size(0) - 1])) && (!(xi[k] < x[0]))) {
                nx = internal::b_bsearch(x, xi[k]);
                xtmp = x[nx - 1];
                xtmp = (xi[k] - xtmp) / (x[nx] - xtmp);
                if (xtmp == 0.0) {
                  for (b_j1 = 0; b_j1 <= nycols; b_j1++) {
                    yi[k + b_j1 * nxi] = y[(nx + b_j1 * nyrows) - 1];
                  }
                } else if (xtmp == 1.0) {
                  for (b_j1 = 0; b_j1 <= nycols; b_j1++) {
                    yi[k + b_j1 * nxi] = y[nx + b_j1 * nyrows];
                  }
                } else {
                  for (b_j1 = 0; b_j1 <= nycols; b_j1++) {
                    double b_y1;
                    double y2;
                    b_y1 = y[(nx + b_j1 * nyrows) - 1];
                    y2 = y[nx + b_j1 * nyrows];
                    if (b_y1 == y2) {
                      yi[k + b_j1 * nxi] = b_y1;
                    } else {
                      yi[k + b_j1 * nxi] = (1.0 - xtmp) * b_y1 + xtmp * y2;
                    }
                  }
                }
              }
            }
          }

          exitg1 = 1;
        }
      } while (exitg1 == 0);
    }
  }

  //
  // Arguments    : double a
  //                double b
  // Return Type  : double
  //
  static double maxabs(double a, double b)
  {
    return std::fmax(b_abs(a), b_abs(b));
  }

  //
  // Arguments    : const ::coder::array<double, 2U> &a
  //                double varargin_1
  //                ::coder::array<double, 2U> &b
  // Return Type  : void
  //
  static void repmat(const ::coder::array<double, 2U> &a, double varargin_1, ::
                     coder::array<double, 2U> &b)
  {
    int ncols;
    int ntilerows;
    b.set_size((static_cast<int>(varargin_1)), a.size(1));
    ncols = a.size(1);
    ntilerows = static_cast<int>(varargin_1);
    for (int jcol = 0; jcol < ncols; jcol++) {
      int ibmat;
      ibmat = jcol * static_cast<int>(varargin_1);
      for (int itilerow = 0; itilerow < ntilerows; itilerow++) {
        b[ibmat + itilerow] = a[jcol];
      }
    }
  }

  //
  // Arguments    : ::coder::array<double, 2U> &p
  // Return Type  : void
  //
  static void unwrap(::coder::array<double, 2U> &p)
  {
    array<double, 1U> vwork;
    int dim;
    int ip;
    int k;
    int npages;
    int vlen;
    int vspread;
    int vstride;
    dim = internal::nonSingletonDim(p) - 1;
    vlen = p.size(dim) - 1;
    vwork.set_size(p.size(dim));
    vstride = 1;
    for (k = 0; k < dim; k++) {
      vstride *= p.size(0);
    }

    vspread = (p.size(dim) - 1) * vstride;
    npages = 1;
    dim += 2;
    for (k = dim; k < 3; k++) {
      npages *= p.size(1);
    }

    dim = 0;
    for (int i = 0; i < npages; i++) {
      int i1;
      i1 = dim - 1;
      dim += vspread;
      for (int j = 0; j < vstride; j++) {
        i1++;
        dim++;
        ip = i1;
        for (k = 0; k <= vlen; k++) {
          vwork[k] = p[ip];
          ip += vstride;
        }

        unwrap_vector(vwork);
        ip = i1;
        for (k = 0; k <= vlen; k++) {
          p[ip] = vwork[k];
          ip += vstride;
        }
      }
    }
  }

  //
  // Arguments    : ::coder::array<double, 1U> &p
  // Return Type  : void
  //
  static void unwrap_vector(::coder::array<double, 1U> &p)
  {
    double cumsum_dp_corr;
    double dp_corr;
    unsigned int k;
    int m;
    m = p.size(0);
    cumsum_dp_corr = 0.0;
    k = 1U;
    while ((static_cast<int>(k) < m) && (!b_isfinite(p[static_cast<int>(k) - 1])))
    {
      k = static_cast<unsigned int>(static_cast<int>(k) + 1);
    }

    if (static_cast<int>(k) < p.size(0)) {
      double pkm1;
      pkm1 = p[static_cast<int>(k) - 1];
      int exitg1;
      do {
        exitg1 = 0;
        k++;
        while ((static_cast<double>(k) <= m) && (!b_isfinite(p[static_cast<int>
                 (k) - 1]))) {
          k++;
        }

        if (static_cast<double>(k) > m) {
          exitg1 = 1;
        } else {
          double dp_tmp;
          dp_tmp = p[static_cast<int>(k) - 1];
          pkm1 = dp_tmp - pkm1;
          dp_corr = pkm1 / 6.2831853071795862;
          if (b_abs(b_rem(dp_corr)) <= 0.5) {
            b_fix(&dp_corr);
          } else {
            b_round(&dp_corr);
          }

          if (b_abs(pkm1) >= 3.1415926535897931) {
            cumsum_dp_corr += dp_corr;
          }

          pkm1 = dp_tmp;
          p[static_cast<int>(k) - 1] = dp_tmp - 6.2831853071795862 *
            cumsum_dp_corr;
        }
      } while (exitg1 == 0);
    }
  }

  //
  // Arguments    : int numerator
  //                int denominator
  // Return Type  : int
  //
}

static int div_s32(int numerator, int denominator)
{
  unsigned int b_numerator;
  int quotient;
  if (denominator == 0) {
    if (numerator >= 0) {
      quotient = MAX_int32_T;
    } else {
      quotient = MIN_int32_T;
    }
  } else {
    unsigned int b_denominator;
    if (numerator < 0) {
      b_numerator = ~static_cast<unsigned int>(numerator) + 1U;
    } else {
      b_numerator = static_cast<unsigned int>(numerator);
    }

    if (denominator < 0) {
      b_denominator = ~static_cast<unsigned int>(denominator) + 1U;
    } else {
      b_denominator = static_cast<unsigned int>(denominator);
    }

    b_numerator /= b_denominator;
    if ((numerator < 0) != (denominator < 0)) {
      quotient = -static_cast<int>(b_numerator);
    } else {
      quotient = static_cast<int>(b_numerator);
    }
  }

  return quotient;
}

//
// function csi = magPhase2CSI(mag, phase)
// Arguments    : const coder::array<double, 2U> &mag
//                const coder::array<double, 2U> &phase
//                coder::array<creal_T, 2U> &csi
// Return Type  : void
//
static void magPhase2CSI(const coder::array<double, 2U> &mag, const coder::array<
  double, 2U> &phase, coder::array<creal_T, 2U> &csi)
{
  int i;
  int loop_ub;

  // 'magPhase2CSI:3' csi = mag .* exp(1i * phase);
  csi.set_size(phase.size(0), phase.size(1));
  loop_ub = phase.size(0) * phase.size(1);
  for (i = 0; i < loop_ub; i++) {
    csi[i].re = phase[i] * 0.0;
    csi[i].im = phase[i];
  }

  coder::b_exp(csi);
  loop_ub = mag.size(0) * mag.size(1);
  csi.set_size(mag.size(0), mag.size(1));
  for (i = 0; i < loop_ub; i++) {
    csi[i].re = mag[i] * csi[i].re;
    csi[i].im = mag[i] * csi[i].im;
  }
}

//
// Arguments    : double u0
//                double u1
// Return Type  : double
//
static double rt_atan2d_snf(double u0, double u1)
{
  double y;
  if (std::isnan(u0) || std::isnan(u1)) {
    y = rtNaN;
  } else if (std::isinf(u0) && std::isinf(u1)) {
    int b_u0;
    int b_u1;
    if (u0 > 0.0) {
      b_u0 = 1;
    } else {
      b_u0 = -1;
    }

    if (u1 > 0.0) {
      b_u1 = 1;
    } else {
      b_u1 = -1;
    }

    y = std::atan2(static_cast<double>(b_u0), static_cast<double>(b_u1));
  } else if (u1 == 0.0) {
    if (u0 > 0.0) {
      y = RT_PI / 2.0;
    } else if (u0 < 0.0) {
      y = -(RT_PI / 2.0);
    } else {
      y = 0.0;
    }
  } else {
    y = std::atan2(u0, u1);
  }

  return y;
}

//
// Arguments    : double u0
//                double u1
// Return Type  : double
//
static double rt_hypotd_snf(double u0, double u1)
{
  double a;
  double y;
  a = std::abs(u0);
  y = std::abs(u1);
  if (a < y) {
    a /= y;
    y *= std::sqrt(a * a + 1.0);
  } else if (a > y) {
    y /= a;
    y = a * std::sqrt(y * y + 1.0);
  } else {
    if (!std::isnan(y)) {
      y = a * 1.4142135623730951;
    }
  }

  return y;
}

//
// Arguments    : double u0
//                double u1
// Return Type  : double
//
static double rt_remd_snf(double u0, double u1)
{
  double y;
  if (std::isnan(u0) || std::isnan(u1) || std::isinf(u0)) {
    y = rtNaN;
  } else if (std::isinf(u1)) {
    y = u0;
  } else if ((u1 != 0.0) && (u1 != std::trunc(u1))) {
    double q;
    q = std::abs(u0 / u1);
    if (!(std::abs(q - std::floor(q + 0.5)) > DBL_EPSILON * q)) {
      y = 0.0 * u0;
    } else {
      y = std::fmod(u0, u1);
    }
  } else {
    y = std::fmod(u0, u1);
  }

  return y;
}

//
// function [resultCSI, resultMag, resultPhase, interpedIndex_int16] = CSIPreprocessor(CSI, subcarrierIndex_int16)
// Arguments    : const coder::array<creal_T, 2U> &CSI
//                const coder::array<short, 1U> &subcarrierIndex_int16
//                coder::array<creal_T, 2U> &resultCSI
//                coder::array<double, 2U> &resultMag
//                coder::array<double, 2U> &resultPhase
//                coder::array<short, 1U> &interpedIndex_int16
// Return Type  : void
//
void CSIPreprocessor(const coder::array<creal_T, 2U> &CSI, const coder::array<
                     short, 1U> &subcarrierIndex_int16, coder::array<creal_T, 2U>
                     &resultCSI, coder::array<double, 2U> &resultMag, coder::
                     array<double, 2U> &resultPhase, coder::array<short, 1U>
                     &interpedIndex_int16)
{
  coder::array<creal_T, 2U> b_CSI;
  coder::array<creal_T, 2U> newCSI;
  coder::array<double, 2U> all_unwrap_interp;
  coder::array<double, 2U> newMag;
  coder::array<double, 2U> r;
  coder::array<double, 2U> rawPhase;
  coder::array<double, 2U> y;
  coder::array<double, 1U> interpedIndex;
  coder::array<double, 1U> subcarrierIndex;
  coder::array<double, 1U> varargin_1_tmp;
  coder::array<boolean_T, 1U> b_varargin_1_tmp;
  double minval;
  int dataSize[2];
  int sz_tmp[2];
  int pivotIndex_data[1];
  int tmp_data[1];
  int tmp_size[1];
  int dataSize_idx_0;
  int dataSize_idx_1;
  int i;
  int subcarrierIndex_idx_1;

  // 'CSIPreprocessor:3' subcarrierIndex = sort(double(subcarrierIndex_int16));
  subcarrierIndex.set_size(subcarrierIndex_int16.size(0));
  dataSize_idx_0 = subcarrierIndex_int16.size(0);
  for (i = 0; i < dataSize_idx_0; i++) {
    subcarrierIndex[i] = subcarrierIndex_int16[i];
  }

  coder::internal::sort(subcarrierIndex);

  // 'CSIPreprocessor:4' interpedIndex = interp1(subcarrierIndex, subcarrierIndex, subcarrierIndex(1) : subcarrierIndex(end))'; 
  if (subcarrierIndex[subcarrierIndex.size(0) - 1] < subcarrierIndex[0]) {
    y.set_size(1, 0);
  } else {
    minval = subcarrierIndex[0];
    coder::b_floor(&minval);
    if (minval == subcarrierIndex[0]) {
      y.set_size(1, (static_cast<int>(std::floor
        (subcarrierIndex[subcarrierIndex.size(0) - 1] - subcarrierIndex[0])) + 1));
      dataSize_idx_0 = static_cast<int>(std::floor
        (subcarrierIndex[subcarrierIndex.size(0) - 1] - subcarrierIndex[0]));
      for (i = 0; i <= dataSize_idx_0; i++) {
        y[i] = subcarrierIndex[0] + static_cast<double>(i);
      }
    } else {
      coder::eml_float_colon(subcarrierIndex[0],
        subcarrierIndex[subcarrierIndex.size(0) - 1], y);
    }
  }

  coder::interp1(subcarrierIndex, subcarrierIndex, y, r);
  interpedIndex.set_size(r.size(1));
  dataSize_idx_0 = r.size(1);
  for (i = 0; i < dataSize_idx_0; i++) {
    interpedIndex[i] = r[i];
  }

  // 'CSIPreprocessor:5' reshapedCSI = reshape(CSI, numel(subcarrierIndex), []); 
  subcarrierIndex_idx_1 = coder::internal::computeDimsData(CSI.size(0) *
    CSI.size(1), static_cast<double>(subcarrierIndex.size(0)));

  // 'CSIPreprocessor:7' rawPhase = angle(reshapedCSI);
  dataSize_idx_0 = subcarrierIndex.size(0);
  b_CSI = CSI.reshape(dataSize_idx_0, subcarrierIndex_idx_1);
  coder::angle(b_CSI, rawPhase);

  //  find the closest index to DC
  // 'CSIPreprocessor:10' pivotIndex = find(abs(subcarrierIndex) == min(abs(subcarrierIndex - 0)), 1, 'first'); 
  coder::b_abs(subcarrierIndex, varargin_1_tmp);
  minval = coder::internal::minimum(varargin_1_tmp);
  b_varargin_1_tmp.set_size(varargin_1_tmp.size(0));
  dataSize_idx_0 = varargin_1_tmp.size(0);
  for (i = 0; i < dataSize_idx_0; i++) {
    b_varargin_1_tmp[i] = (varargin_1_tmp[i] == minval);
  }

  coder::eml_find(b_varargin_1_tmp, tmp_data, tmp_size);
  dataSize_idx_0 = tmp_size[0];
  if (0 <= dataSize_idx_0 - 1) {
    std::memcpy(&pivotIndex_data[0], &tmp_data[0], dataSize_idx_0 * sizeof(int));
  }

  // 'CSIPreprocessor:11' pivotSubcarrierId = subcarrierIndex(pivotIndex);
  //  the index of pivotIndex in interpedIndex
  // 'CSIPreprocessor:13' pivotInterpedIndex = find(interpedIndex == pivotSubcarrierId(1), 1, 'first'); 
  // 'CSIPreprocessor:14' pivotPhase = rawPhase(pivotIndex(1), :);
  // 'CSIPreprocessor:16' all_unwrap_interp = interp1(subcarrierIndex, unwrap(rawPhase), interpedIndex); 
  r.set_size(rawPhase.size(0), rawPhase.size(1));
  dataSize_idx_0 = rawPhase.size(0) * rawPhase.size(1);
  for (i = 0; i < dataSize_idx_0; i++) {
    r[i] = rawPhase[i];
  }

  coder::unwrap(r);
  coder::interp1(subcarrierIndex, r, interpedIndex, all_unwrap_interp);

  // 'CSIPreprocessor:17' phaseGap = (all_unwrap_interp(pivotInterpedIndex,:) - pivotPhase); 
  // 'CSIPreprocessor:18' newPhase = all_unwrap_interp - repmat(phaseGap, size(all_unwrap_interp, 1), 1); 
  b_varargin_1_tmp.set_size(interpedIndex.size(0));
  dataSize_idx_0 = interpedIndex.size(0);
  for (i = 0; i < dataSize_idx_0; i++) {
    b_varargin_1_tmp[i] = (interpedIndex[i] == subcarrierIndex[pivotIndex_data[0]
      - 1]);
  }

  coder::eml_find(b_varargin_1_tmp, tmp_data, tmp_size);
  dataSize_idx_0 = all_unwrap_interp.size(1);
  y.set_size(tmp_size[0], all_unwrap_interp.size(1));
  for (i = 0; i < dataSize_idx_0; i++) {
    dataSize_idx_1 = tmp_size[0];
    for (int i1 = 0; i1 < dataSize_idx_1; i1++) {
      y[i1 + i] = all_unwrap_interp[(tmp_data[i1] + all_unwrap_interp.size(0) *
        i) - 1] - rawPhase[(pivotIndex_data[0] + rawPhase.size(0) * i) - 1];
    }
  }

  coder::repmat(y, static_cast<double>(all_unwrap_interp.size(0)), newMag);
  dataSize_idx_0 = all_unwrap_interp.size(0) * all_unwrap_interp.size(1);
  for (i = 0; i < dataSize_idx_0; i++) {
    all_unwrap_interp[i] = all_unwrap_interp[i] - newMag[i];
  }

  // 'CSIPreprocessor:19' newMag = interp1(subcarrierIndex, abs(reshapedCSI), interpedIndex); 
  dataSize_idx_0 = subcarrierIndex.size(0);
  b_CSI = CSI.reshape(dataSize_idx_0, subcarrierIndex_idx_1);
  coder::b_abs(b_CSI, r);
  coder::interp1(subcarrierIndex, r, interpedIndex, newMag);

  // 'CSIPreprocessor:20' newCSI = magPhase2CSI(newMag, newPhase);
  magPhase2CSI(newMag, all_unwrap_interp, newCSI);

  // 'CSIPreprocessor:22' dataSize = size(CSI);
  dataSize_idx_0 = CSI.size(0);
  dataSize_idx_1 = CSI.size(1);

  // 'CSIPreprocessor:23' if numel(dataSize) > 1 && dataSize(1) ~= numel(CSI) && dataSize(2) ~= numel(CSI) 
  if ((CSI.size(0) != CSI.size(0) * CSI.size(1)) && (CSI.size(1) != CSI.size(0) *
       CSI.size(1))) {
    // 'CSIPreprocessor:24' dataSize(1) = size(newCSI, 1);
    dataSize_idx_0 = newCSI.size(0);
  } else {
    // 'CSIPreprocessor:25' else
    // 'CSIPreprocessor:26' if dataSize(1) == numel(CSI)
    if (CSI.size(0) == CSI.size(0) * CSI.size(1)) {
      // 'CSIPreprocessor:27' dataSize(1) = numel(newCSI);
      dataSize_idx_0 = newCSI.size(0) * newCSI.size(1);
    } else {
      if (CSI.size(1) == CSI.size(0) * CSI.size(1)) {
        // 'CSIPreprocessor:28' elseif dataSize(2) == numel(CSI)
        // 'CSIPreprocessor:29' dataSize(2) = numel(newCSI);
        dataSize_idx_1 = newCSI.size(0) * newCSI.size(1);
      }
    }
  }

  // 'CSIPreprocessor:33' resultCSI = reshape(newCSI, dataSize);
  dataSize[0] = dataSize_idx_0;
  dataSize[1] = dataSize_idx_1;
  coder::internal::num2cell_vector(dataSize, sz_tmp);
  resultCSI.set_size(sz_tmp[0], sz_tmp[1]);
  dataSize_idx_0 = sz_tmp[0] * sz_tmp[1];

  // 'CSIPreprocessor:34' resultMag = reshape(newMag, dataSize);
  resultMag.set_size(sz_tmp[0], sz_tmp[1]);

  // 'CSIPreprocessor:35' resultPhase = reshape(newPhase, dataSize);
  resultPhase.set_size(sz_tmp[0], sz_tmp[1]);
  for (i = 0; i < dataSize_idx_0; i++) {
    resultCSI[i] = newCSI[i];
    resultMag[i] = newMag[i];
    resultPhase[i] = all_unwrap_interp[i];
  }

  // 'CSIPreprocessor:36' interpedIndex_int16 = int16(interpedIndex);
  interpedIndex_int16.set_size(interpedIndex.size(0));
  dataSize_idx_0 = interpedIndex.size(0);
  for (i = 0; i < dataSize_idx_0; i++) {
    short i2;
    minval = std::round(interpedIndex[i]);
    if (minval < 32768.0) {
      if (minval >= -32768.0) {
        i2 = static_cast<short>(minval);
      } else {
        i2 = MIN_int16_T;
      }
    } else if (minval >= 32768.0) {
      i2 = MAX_int16_T;
    } else {
      i2 = 0;
    }

    interpedIndex_int16[i] = i2;
  }
}

//
// Arguments    : void
// Return Type  : void
//
void CSIPreprocessor_initialize()
{
}

//
// Arguments    : void
// Return Type  : void
//
void CSIPreprocessor_terminate()
{
  // (no terminate code required)
}

//
// File trailer for CSIPreprocessor.cpp
//
// [EOF]
//
