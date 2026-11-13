#include "NativeV3.cpp"
EXPORT void pm_rec709_matrix(const double* x,int inverse,double* out){
 auto r=pair(x[0]),g=pair(x[1]),b=pair(x[2]);
 for(int axis=0;axis<3;++axis)out[axis]=value(inverse?pm::pma_from_dwg_channel(r,g,b,4,axis):pm::pma_to_dwg_channel(r,g,b,4,axis));
}
