#include "NativeV3.cpp"
EXPORT void pm_rec709_matrix(const double* x,int inverse,double* out){
 auto r=pair(x[0]),g=pair(x[1]),b=pair(x[2]);
 for(int axis=0;axis<3;++axis)out[axis]=value(inverse?pm::pma_from_dwg_channel(r,g,b,4,axis):pm::pma_to_dwg_channel(r,g,b,4,axis));
}

EXPORT void pm_display_matrix(const double* x,int gamut,int inverse,double* out){
 auto r=pair(x[0]),g=pair(x[1]),b=pair(x[2]);
 for(int axis=0;axis<3;++axis)out[axis]=value(inverse?pm::pma_from_dwg_channel(r,g,b,gamut,axis):pm::pma_to_dwg_channel(r,g,b,gamut,axis));
}
EXPORT double pm_display_transfer(float v,int curve,int encode){
 // Scalar transfer oracle; pair collapse has a separate existing rounding boundary.
 return encode?(double)pm::pma_display_encode(v,curve):(double)pm::pma_display_decode(v,curve);
}
