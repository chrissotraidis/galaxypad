// Included in MTLTexture.mm and the standalone native Metal parity harness.
// Rendering-thread only, scoped to one refresh. Resource IDs never escape or log.
namespace galaxypad::efb_direct_batch {
namespace {
id<MTLBlitCommandEncoder> batch_encoder=nil;
id<MTLCommandBuffer> batch_command=nil;
id<MTLTexture> batch_source=nil;
id<MTLBuffer> batch_destination=nil;
}
bool HasMetalBatch() {return batch_encoder!=nil;}
void EndMetalBatch() {
  if(!batch_encoder) return;
  [batch_encoder endEncoding];
  [batch_encoder release];
  batch_encoder=nil;batch_command=nil;batch_source=nil;batch_destination=nil;
}
id<MTLBlitCommandEncoder> AcquireMetalBatch(id<MTLCommandBuffer> command,
    id<MTLTexture> source,id<MTLBuffer> destination,bool* created) {
  *created=false;
  if(batch_encoder && batch_command==command && batch_source==source &&
      batch_destination==destination) return batch_encoder;
  EndMetalBatch();
  batch_encoder=[[command blitCommandEncoder] retain];
  batch_command=command;batch_source=source;batch_destination=destination;
  *created=true;
  return batch_encoder;
}
} // namespace galaxypad::efb_direct_batch
