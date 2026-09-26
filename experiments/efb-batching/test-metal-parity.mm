#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include "MetalEfbBatch.h"
#include "MetalEfbBatchImpl.inc"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <array>
namespace b=galaxypad::efb_direct_batch;
struct TileRect {unsigned x,y,w,h;};
int main() { @autoreleasepool {
  id<MTLDevice> device=MTLCreateSystemDefaultDevice();assert(device);
  id<MTLCommandQueue> queue=[device newCommandQueue];assert(queue);
  NSError* error=nil;
  NSString* source=@"#include <metal_stdlib>\nusing namespace metal;\n"
    "vertex float4 vs(uint i [[vertex_id]]) { const float2 p[3]={float2(-1,-1),float2(3,-1),float2(-1,3)}; return float4(p[i],0,1); }\n"
    "struct Out {float z [[depth(any)]];};\n"
    "fragment Out fs(float4 p [[position]],constant float& base [[buffer(0)]]) {return {base+p.x/2048.0f+p.y/4096.0f};}";
  id<MTLLibrary> library=[device newLibraryWithSource:source options:nil error:&error];
  if(!library) {fprintf(stderr,"shader: %s\n",error.localizedDescription.UTF8String);return 1;}
  MTLRenderPipelineDescriptor* pd=[MTLRenderPipelineDescriptor new];
  pd.vertexFunction=[library newFunctionWithName:@"vs"];
  pd.fragmentFunction=[library newFunctionWithName:@"fs"];
  pd.depthAttachmentPixelFormat=MTLPixelFormatDepth32Float;
  id<MTLRenderPipelineState> pipeline=[device newRenderPipelineStateWithDescriptor:pd error:&error];assert(pipeline);
  MTLDepthStencilDescriptor* dd=[MTLDepthStencilDescriptor new];dd.depthWriteEnabled=YES;dd.depthCompareFunction=MTLCompareFunctionAlways;
  id<MTLDepthStencilState> depthState=[device newDepthStencilStateWithDescriptor:dd];assert(depthState);
  MTLTextureDescriptor* td=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatDepth32Float width:640 height:528 mipmapped:NO];
  td.storageMode=MTLStorageModePrivate;td.usage=MTLTextureUsageRenderTarget|MTLTextureUsageShaderRead;
  id<MTLTexture> textures[2]={[device newTextureWithDescriptor:td],[device newTextureWithDescriptor:td]};
  constexpr unsigned stride=640*4,bytes=stride*528;
  id<MTLBuffer> control[2]={[device newBufferWithLength:bytes options:MTLResourceStorageModeShared],
                          [device newBufferWithLength:bytes options:MTLResourceStorageModeShared]};
  id<MTLBuffer> candidate[2]={[device newBufferWithLength:bytes options:MTLResourceStorageModeShared],
                            [device newBufferWithLength:bytes options:MTLResourceStorageModeShared]};
  const std::array<TileRect,3> rects={TileRect{0,0,64,64},TileRect{256,256,64,64},TileRect{576,512,64,16}};
  auto copy=[&](id<MTLBlitCommandEncoder> enc,id<MTLTexture> src,id<MTLBuffer> dst,TileRect r) {
    [enc copyFromTexture:src sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(r.x,r.y,0)
      sourceSize:MTLSizeMake(r.w,r.h,1) toBuffer:dst destinationOffset:r.y*stride+r.x*4
      destinationBytesPerRow:stride destinationBytesPerImage:stride*r.h];
  };
  unsigned trials=0,controlEncoders=0,candidateEncoders=0;
  for(unsigned kind=0;kind<7;++kind) for(unsigned iteration=0;iteration<16;++iteration) { @autoreleasepool {
    for(unsigned i=0;i<2;++i) {memset(control[i].contents,0xA5,bytes);memset(candidate[i].contents,0xA5,bytes);}
    id<MTLCommandBuffer> command=[queue commandBuffer];
    const float base=.03125f*(1+iteration%8);
    for(unsigned t=0;t<2;++t) {
      MTLRenderPassDescriptor* rp=[MTLRenderPassDescriptor renderPassDescriptor];
      rp.depthAttachment.texture=textures[t];rp.depthAttachment.loadAction=MTLLoadActionClear;
      rp.depthAttachment.storeAction=MTLStoreActionStore;rp.depthAttachment.clearDepth=1;
      id<MTLRenderCommandEncoder> enc=[command renderCommandEncoderWithDescriptor:rp];
      [enc setRenderPipelineState:pipeline];[enc setDepthStencilState:depthState];
      const float value=base+t*.0625f;[enc setFragmentBytes:&value length:sizeof(value) atIndex:0];
      [enc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];[enc endEncoding];
    }
    for(unsigned i=0;i<3;++i) {
      const unsigned dst=(kind==2 && i==1)?1:0,src=(kind==3 && i==2)?1:0;
      id<MTLBlitCommandEncoder> enc=[command blitCommandEncoder];++controlEncoders;
      copy(enc,textures[src],control[dst],rects[i]);[enc endEncoding];
    }
    unsigned createdThisTrial=0;
    for(unsigned i=0;i<3;++i) {
      const unsigned dst=(kind==2 && i==1)?1:0,src=(kind==3 && i==2)?1:0;
      if(i==1 && (kind==1 || kind>=4)) {
        b::EndMetalBatch();assert(!b::HasMetalBatch());
        if(kind==1) {
          // An intervening real render pass must not overlap the blit encoder.
          MTLRenderPassDescriptor* rp=[MTLRenderPassDescriptor renderPassDescriptor];
          rp.depthAttachment.texture=textures[0];rp.depthAttachment.loadAction=MTLLoadActionLoad;
          rp.depthAttachment.storeAction=MTLStoreActionStore;
          id<MTLRenderCommandEncoder> enc=[command renderCommandEncoderWithDescriptor:rp];[enc endEncoding];
        } else if(kind==4) {
          [command commit];[command waitUntilCompleted];assert(command.status==MTLCommandBufferStatusCompleted);
          command=[queue commandBuffer];
        } else if(kind==5) {
          id<MTLComputeCommandEncoder> enc=[command computeCommandEncoder];[enc endEncoding];
        } else {
          id<MTLBlitCommandEncoder> enc=[command blitCommandEncoder];[enc endEncoding];
        }
      }
      bool created=false;id<MTLBlitCommandEncoder> enc=b::AcquireMetalBatch(command,textures[src],candidate[dst],&created);
      createdThisTrial+=created;copy(enc,textures[src],candidate[dst],rects[i]);
    }
    b::EndMetalBatch();assert(!b::HasMetalBatch());
    [command commit];[command waitUntilCompleted];assert(command.status==MTLCommandBufferStatusCompleted);
    const unsigned expectedEncoders=kind==0?1:(kind==2?3:2);
    assert(createdThisTrial==expectedEncoders);candidateEncoders+=createdThisTrial;
    for(unsigned buffer=0;buffer<2;++buffer) {
      assert(memcmp(control[buffer].contents,candidate[buffer].contents,bytes)==0);
      for(unsigned y=0;y<528;++y) for(unsigned x=0;x<640;++x) {
        bool written=false;float expected=0;
        for(unsigned i=0;i<3;++i) {
          const unsigned dst=(kind==2 && i==1)?1:0,src=(kind==3 && i==2)?1:0;
          const auto r=rects[i];
          if(dst==buffer && x>=r.x && x<r.x+r.w && y>=r.y && y<r.y+r.h) {
            written=true;expected=base+src*.0625f+(x+.5f)/2048.f+(y+.5f)/4096.f;
          }
        }
        const auto* actual=static_cast<const unsigned char*>(candidate[buffer].contents)+y*stride+x*4;
        if(written) assert(memcmp(actual,&expected,4)==0);
        else for(unsigned byte=0;byte<4;++byte) assert(actual[byte]==0xA5);
      }
    }
    ++trials;
  }}
  printf("Metal D32F parity: %u trials; full staging buffers, spatial depth values and untouched bytes match; baseline encoders=%u candidate=%u; render/compute/blit/resource/command boundaries pass\n",trials,controlEncoders,candidateEncoders);
  return 0;
}}
