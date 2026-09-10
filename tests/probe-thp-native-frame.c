/* Private first-frame linear-plane reference from standalone FFmpeg. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavcodec/mjpegdec.h>
#include <libavcodec/mathops.h>
static MJpegDecodeContext *decoder;
static void (*original_put)(uint8_t *,ptrdiff_t,int16_t *);
static unsigned blocks;
#ifdef THP_FLOOR_IDCT
void thp_floor_idct_put(uint8_t *,ptrdiff_t,int16_t *);
void thp_sparse_idct_put(uint8_t *,ptrdiff_t,int16_t *);
#endif
static void trace_put(uint8_t *dst,ptrdiff_t stride,int16_t *block) {
#ifndef THP_BENCH
    if(blocks<5520) {
        unsigned position=blocks%6, component=position<4?0:position-3;
        int raw[64]={0};
        int quant[64]={0};
        for(unsigned i=0;i<64;i++) {
            int value=block[decoder->permutated_scantable[i]]-(i==0?1024:0);
            int q=decoder->quant_matrixes[decoder->quant_sindex[component]][i];
            assert(q && value%q==0);
            quant[ff_zigzag_direct[i]]=q;
            raw[ff_zigzag_direct[i]]=value/q;
        }
        fprintf(stderr,"block %u coefficients=",blocks);
        for(unsigned i=0;i<64;i++)fprintf(stderr,"%s%d",i?",":"",raw[i]);
        fputc('\n',stderr);
        if(blocks<6) {
            fprintf(stderr,"quant %u values=",blocks);
            for(unsigned i=0;i<64;i++)fprintf(stderr,"%s%d",i?",":"",quant[i]);
            fputc('\n',stderr);
        }
    }
#endif
    blocks++;original_put(dst,stride,block);
}
int main(int argc,char **argv) {
    assert(argc>=3 && argc<=5);
    AVFormatContext *input=NULL;
    assert(avformat_open_input(&input,argv[1],NULL,NULL)>=0);
    assert(avformat_find_stream_info(input,NULL)>=0);
    const AVCodec *codec=NULL;
    int stream=av_find_best_stream(input,AVMEDIA_TYPE_VIDEO,-1,-1,&codec,0);
    assert(stream>=0 && codec);
    AVCodecContext *ctx=avcodec_alloc_context3(codec); assert(ctx);
    assert(avcodec_parameters_to_context(ctx,input->streams[stream]->codecpar)>=0);
    ctx->thread_count=1;
    if(argc>=4) {
        ctx->idct_algo=atoi(argv[3]);
        assert(ctx->idct_algo==FF_IDCT_AUTO || ctx->idct_algo==FF_IDCT_INT ||
               ctx->idct_algo==FF_IDCT_SIMPLE || ctx->idct_algo==FF_IDCT_FAAN);
    }
    assert(avcodec_open2(ctx,codec,NULL)>=0);
    /* Private FFmpeg8.0.1 diagnostic ABI; never part of product integration. */
    decoder=ctx->priv_data; original_put=decoder->idsp.idct_put;
#ifdef THP_FLOOR_IDCT
    assert(ctx->idct_algo==FF_IDCT_FAAN);
    original_put=thp_floor_idct_put;
#ifdef THP_SPARSE_IDCT
    original_put=thp_sparse_idct_put;
#endif
#endif
    decoder->idsp.idct_put=trace_put;
    AVPacket *packet=av_packet_alloc(); AVFrame *frame=av_frame_alloc();
    assert(packet && frame);
#ifdef THP_BENCH
    assert(argc==4); /* argv[2] unused: no decoded files are written. */
    struct timespec start,end;clock_gettime(CLOCK_MONOTONIC,&start);
    unsigned decoded=0;int result;
    while((result=av_read_frame(input,packet))>=0) {
        if(packet->stream_index==stream) {
            assert(avcodec_send_packet(ctx,packet)>=0);
            assert(avcodec_receive_frame(ctx,frame)>=0);
            assert(frame->width==640 && frame->height==368);
            decoded++;av_frame_unref(frame);
        }
        av_packet_unref(packet);
    }
    assert(result==AVERROR_EOF && decoded==5591);
    clock_gettime(CLOCK_MONOTONIC,&end);
    double seconds=end.tv_sec-start.tv_sec+(end.tv_nsec-start.tv_nsec)*1e-9;
    printf("decoded=%u seconds=%.6f fps=%.3f ms_per_frame=%.6f blocks=%u\n",
           decoded,seconds,decoded/seconds,seconds*1000/decoded,blocks);
    av_frame_free(&frame);av_packet_free(&packet);avcodec_free_context(&ctx);
    avformat_close_input(&input);return 0;
#endif
    unsigned target=argc==5 ? (unsigned)strtoul(argv[4],NULL,10) : 0, index=0;
    assert(target<5591);
    for(;;) {
        assert(av_read_frame(input,packet)>=0);
        if(packet->stream_index!=stream) {av_packet_unref(packet);continue;}
        if(index++!=target) {av_packet_unref(packet);continue;}
        assert(avcodec_send_packet(ctx,packet)>=0);
        assert(avcodec_receive_frame(ctx,frame)>=0);break;
    }
    assert(frame->width==640 && frame->height==368 && frame->format==AV_PIX_FMT_YUVJ420P);
    FILE *out=fopen(argv[2],"wbx");assert(out);
    for(int p=0;p<3;p++) {
        int w=p?320:640,h=p?184:368;
        for(int y=0;y<h;y++) assert(fwrite(frame->data[p]+y*frame->linesize[p],1,w,out)==w);
    }
    assert(!fclose(out));
    av_frame_free(&frame);av_packet_free(&packet);avcodec_free_context(&ctx);
    avformat_close_input(&input);return 0;
}
