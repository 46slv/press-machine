#include <math.h>
typedef struct { float x, y, z; } float3;
static inline float3 make_float3(float x, float y, float z) { float3 v = {x,y,z}; return v; }
#define DEFINE_UI_PARAMS(name, ...) float name;
#define DEFINE_UI_TOOLTIP(...)
#define __DEVICE__ static inline
#define _copysignf copysignf
#define _powf powf
#define _fabs fabsf
#define _exp2f exp2f
#define _log2f log2f
#define _fmaxf fmaxf
#define _sqrtf sqrtf
