// Private candidate, explicitly pinned to FFmpeg8.0.1 internal decoder ABI.
// Do not add to shipped targets until runtime/rights/compatibility gates pass.
#include "GalaxyPadTHPDecoder.h"
#include <stdlib.h>
#include <string.h>
#include <libavcodec/avcodec.h>
#include <libavcodec/mjpegdec.h>
#include <libavcodec/mathops.h>
#if LIBAVCODEC_VERSION_INT != AV_VERSION_INT(62,11,100)
#error This candidate requires the audited FFmpeg8.0.1 ABI
#endif
void thp_sparse_idct_put(uint8_t *,ptrdiff_t,int16_t *);
struct GalaxyPadTHPDecoder { AVCodecContext *codec; AVPacket *packet; AVFrame *frame; };
void GalaxyPadTHPDecoderDestroy(GalaxyPadTHPDecoder *d) {
    if(!d)return;
    av_frame_free(&d->frame);av_packet_free(&d->packet);avcodec_free_context(&d->codec);free(d);
}
GalaxyPadTHPDecoder *GalaxyPadTHPDecoderCreate(void) {
    GalaxyPadTHPDecoder *d=calloc(1,sizeof *d);if(!d)return NULL;
    const AVCodec *codec=avcodec_find_decoder(AV_CODEC_ID_THP);
    if(!codec)goto fail;
    d->codec=avcodec_alloc_context3(codec);d->packet=av_packet_alloc();d->frame=av_frame_alloc();
    if(!d->codec || !d->packet || !d->frame)goto fail;
    d->codec->thread_count=1;d->codec->idct_algo=FF_IDCT_FAAN;d->codec->bits_per_raw_sample=8;
    d->codec->max_pixels=640*480;
    d->codec->err_recognition=AV_EF_EXPLODE;
    if(avcodec_open2(d->codec,codec,NULL)<0)goto fail;
    ((MJpegDecodeContext *)d->codec->priv_data)->idsp.idct_put=thp_sparse_idct_put;
    return d;
fail: GalaxyPadTHPDecoderDestroy(d);return NULL;
}
int GalaxyPadTHPDecode(GalaxyPadTHPDecoder *d,const uint8_t *data,size_t bytes,
                      unsigned w,unsigned h,uint8_t *planes[3],const size_t capacities[3]) {
    if(!d || !data || bytes<4 || bytes>4*1024*1024 || !planes || !capacities ||
       !w || !h || w>640 || h>480 || w%16 || h%16)return 0;
    size_t sizes[3]={(size_t)w*h,(size_t)w*h/4,(size_t)w*h/4};
    for(unsigned p=0;p<3;p++) {
        uintptr_t a=(uintptr_t)planes[p];
        if(!a || capacities[p]<sizes[p] || a>UINTPTR_MAX-sizes[p])return 0;
        for(unsigned q=0;q<p;q++) {
            uintptr_t b=(uintptr_t)planes[q];
            if(a<b+sizes[q] && b<a+sizes[p])return 0;
        }
    }
    av_packet_unref(d->packet);av_frame_unref(d->frame);avcodec_flush_buffers(d->codec);
    MJpegDecodeContext *mj=d->codec->priv_data;
    if(d->codec->bits_per_raw_sample!=8) {
        d->codec->bits_per_raw_sample=8;
        ff_idctdsp_init(&mj->idsp,d->codec);
        ff_permute_scantable(mj->permutated_scantable,ff_zigzag_direct,mj->idsp.idct_permutation);
    }
    mj->idsp.idct_put=thp_sparse_idct_put;
    if(av_new_packet(d->packet,(int)bytes)<0)return 0;
    memcpy(d->packet->data,data,bytes); // FFmpeg-owned zero padding, bounded copy.
    if(avcodec_send_packet(d->codec,d->packet)<0 || avcodec_receive_frame(d->codec,d->frame)<0)return 0;
    AVFrame *f=d->frame;
    if(f->width!=(int)w || f->height!=(int)h || f->format!=AV_PIX_FMT_YUVJ420P ||
       f->color_range!=AVCOL_RANGE_JPEG || f->decode_error_flags ||
       d->codec->bits_per_raw_sample!=8 || mj->idsp.idct_put!=thp_sparse_idct_put)return 0;
    for(unsigned p=0;p<3;p++) if(!f->data[p] || f->linesize[p]<(int)(p?w/2:w))return 0;
    // All validation precedes writes, so rejection can use the original decoder.
    for(unsigned p=0;p<3;p++) {
        unsigned pw=p?w/2:w,ph=p?h/2:h;
        for(unsigned y=0;y<ph;y++)for(unsigned x=0;x<pw;x++) {
            size_t tile=((y/4)*(pw/8)+x/8)*32+(y%4)*8+x%8;
            planes[p][tile]=f->data[p][(size_t)y*f->linesize[p]+x];
        }
    }
    return 1;
}
