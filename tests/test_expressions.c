// Baseline test expressions for compilation
#include <math.h>

double polynomial(double x) {
    return x*x + 2*x + 1;
}

double trig(double x) {
    return sin(x) + cos(x);
}

int compare(double x) {
    return (x > 5.0) ? 1 : 0;
}