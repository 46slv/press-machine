// Compile the actual DCTL as native float32 C++, not a second pixel algorithm.
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
struct float2 { float x, y; };
static float2 make_float2(float x,float y) { return {x,y}; }
struct float3 { float x, y, z; };
static float3 make_float3(float x, float y, float z) { return {x, y, z}; }
#define __DEVICE__ static
#define DEFINE_UI_PARAMS(name, label, kind, value, ...) static float name = value;
#define _fabs std::fabs
#define _powf std::pow
#define _sqrtf std::sqrt
#define _log2f std::log2
#define _fmaf std::fma
#define _floorf std::floor
#define _fmaxf std::fmax
#include "../dctl/PressMachine_R2.dctl"
static float word(uint32_t v) { float x; std::memcpy(&x, &v, 4); return x; }
static uint32_t word(float v) { uint32_t x; std::memcpy(&x, &v, 4); return x; }
int main() {
    static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559,
                  "IEEE binary32 required");
    char op;
    uint32_t r, g, b, t, a, p;
    int bypass;
    std::cout << std::setprecision(17);
    while (std::cin >> op >> r >> g >> b >> t >> a >> p >> bypass) {
        pm_threshold=word(t); pm_compression=word(a); pm_softness=word(p);
        pm_bypass=static_cast<float>(bypass);
        float3 out;
        if (op == 'P') out=transform(1,1,0,0,word(r),word(g),word(b));
        else if (op == 'S') out=make_float3(pm_transfer(word(r),word(t),word(a),word(p)),0,0);
        else if (op == 'D') {
            float3 lab={word(r),word(g),word(b)};
            float c=_sqrtf(lab.y*lab.y+lab.z*lab.z);
            out=make_float3(static_cast<float>(pm_domain(lab,c,100.0f*(c/lab.x))),0,0);
        } else if (op == 'G') {
            out=make_float3(static_cast<float>(pm_domain({word(r),word(g),word(b)},.2f,word(t))),0,0);
        } else if (op == 'M') {
            float3 linear={pm_decode(word(r)),pm_decode(word(g)),pm_decode(word(b))};
            float3 lms=pm_condition_lms({word(r),word(g),word(b)},pm_xyz_lms(pm_dwg_xyz(linear)));
            out=pm_root_lab(make_float3(pm_cbrt(lms.x),pm_cbrt(lms.y),pm_cbrt(lms.z)));
        } else if (op == 'E') out=make_float3(pm_encode(word(r)),pm_decode(word(g)),pm_cbrt(word(b)));
        else return 2;
        std::cout << word(out.x) << ' ' << word(out.y) << ' ' << word(out.z) << '\n';
    }
    return std::cin.eof() ? 0 : 3;
}
