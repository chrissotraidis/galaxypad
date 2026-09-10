/* Opt-in candidate: FFmpeg8.0.1 FAAN with final rounding changed to floor.
 * Compile against the pinned ignored FFmpeg source; not product code.
 * For clipped unsigned output, floor and truncation agree on nonnegative values.
 * Keep all transform arithmetic otherwise unchanged to test this one hypothesis. */
#include <math.h>
#define ff_faanidct thp_floor_idct
#define ff_faanidct_add thp_floor_idct_add
#define ff_faanidct_put thp_floor_idct_put
#define lrintf(x) ((long)floorf(x))
#include "libavcodec/faanidct.c"

/* Preserve the SDK's quarter-row middle-output ordering before the column pass.
 * This is a transform-domain case, not a global output-pixel swap. */
void thp_sparse_idct_put(uint8_t *dest, ptrdiff_t stride, int16_t block[64]) {
    FLOAT temp[64];
    int sparse[8];
    for(int row=0;row<8;row++) {
        sparse[row]=block[row*8+1]!=0;
        for(int col=2;col<8;col++) sparse[row]&=block[row*8+col]==0;
    }
    for(int i=0;i<64;i++) temp[i]=block[i]*prescale[i];
    p8idct(block,temp,NULL,0,1,8,0);
    for(int row=0;row<8;row++) if(sparse[row]) {
        FLOAT value=temp[row*8+3];
        temp[row*8+3]=temp[row*8+4]; temp[row*8+4]=value;
    }
    p8idct(NULL,temp,dest,stride,8,1,3);
}
