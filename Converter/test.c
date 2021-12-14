enum <byte> {
  greyscale = 0,
  truecolor = 2,
  indexed = 3,
  greyscale_alpha = 4,
  truecolor_alpha = 6
} color_type;


enum <byte> {
  unknown = 0,
  meter = 1
} phys_unit;


enum <byte> {
  zlib = 0
} compression_methods;


enum <byte> {
  none = 0,     // No disposal is done on this frame before rendering the next;
     //the contents of the output buffer are left as is.
  background = 1,     // The frame's region of the output buffer is to be cleared to
     //fully transparent black before rendering the next frame.
  previous = 2      // The frame's region of the output buffer is to be reverted
     //to the previous contents before rendering the next frame.
} dispose_op_values;


enum <byte> {
  source = 0,     // All color components of the frame, including alpha,
     //overwrite the current contents of the frame's output buffer region.
  over = 1      // The frame is composited onto the output buffer based on its alpha
} blend_op_values;


struct chunk;
struct ihdr_chunk;
struct plte_chunk;
struct rgb;
struct chrm_chunk;
struct point;
struct gama_chunk;
struct srgb_chunk;
struct bkgd_chunk;
struct bkgd_greyscale;
struct bkgd_truecolor;
struct bkgd_indexed;
struct phys_chunk;
struct time_chunk;
struct international_text_chunk;
struct text_chunk;
struct compressed_text_chunk;
struct animation_control_chunk;
struct frame_control_chunk;
struct frame_data_chunk;
struct chunk {
    uint32 len;
    char type[4];
     switch(type) {
         case "PLTE":
             plte_chunk body(len);
             break;
         case "cHRM":
             chrm_chunk body;
             break;
         case "gAMA":
             gama_chunk body;
             break;
         case "sRGB":
             srgb_chunk body;
             break;
         case "bKGD":
             bkgd_chunk body;
             break;
         case "pHYs":
             phys_chunk body;
             break;
         case "tIME":
             time_chunk body;
             break;
         case "iTXt":
             international_text_chunk body;
             break;
         case "tEXt":
             text_chunk body;
             break;
         case "zTXt":
             compressed_text_chunk body;
             break;
         case "acTL":
             animation_control_chunk body;
             break;
         case "fcTL":
             frame_control_chunk body;
             break;
         case "fdAT":
             frame_data_chunk body(len);
             break;
};
    byte crc[4];
};
struct ihdr_chunk {
    //     https://www.w3.org/TR/PNG/#11IHDR
    uint32 width;
    uint32 height;
    ubyte bit_depth;
    ubyte color_type;
    ubyte compression_method;
    ubyte filter_method;
    ubyte interlace_method;
};
struct plte_chunk {
    //     https://www.w3.org/TR/PNG/#11PLTE
    rgb entries;
};
struct rgb {
    ubyte r;
    ubyte g;
    ubyte b;
};
struct chrm_chunk {
    //     https://www.w3.org/TR/PNG/#11cHRM
    point white_point;
    point red;
    point green;
    point blue;
};
struct point {
    uint32 x_int;
    uint32 y_int;
};
struct gama_chunk {
    //     https://www.w3.org/TR/PNG/#11gAMA
    uint32 gamma_int;
};
struct srgb_chunk {
    //     https://www.w3.org/TR/PNG/#11sRGB
    ubyte render_intent;
enum <byte> {
  perceptual = 0,
  relative_colorimetric = 1,
  saturation = 2,
  absolute_colorimetric = 3
} intent;


};
struct bkgd_chunk {
    //     Background chunk stores default background color to display this
    //    image against. Contents depend on `color_type` of the image.
    //    
    //     https://www.w3.org/TR/PNG/#11bKGD
     switch(ihdr.color_type) {
         case 0:
             bkgd_greyscale bkgd;
             break;
         case 4:
             bkgd_greyscale bkgd;
             break;
         case 2:
             bkgd_truecolor bkgd;
             break;
         case 6:
             bkgd_truecolor bkgd;
             break;
         case 3:
             bkgd_indexed bkgd;
             break;
};
};
struct bkgd_greyscale {
    //     Background chunk for greyscale images.
    uint16 value;
};
struct bkgd_truecolor {
    //     Background chunk for truecolor images.
    uint16 red;
    uint16 green;
    uint16 blue;
};
struct bkgd_indexed {
    //     Background chunk for images with indexed palette.
    ubyte palette_index;
};
struct phys_chunk {
    //     "Physical size" chunk stores data that allows to translate
    //    logical pixels into physical units (meters, etc) and vice-versa.
    //    
    //     https://www.w3.org/TR/PNG/#11pHYs
    uint32 pixels_per_unit_x;
    uint32 pixels_per_unit_y;
    ubyte unit;
};
struct time_chunk {
    //     Time chunk stores time stamp of last modification of this image,
    //    up to 1 second precision in UTC timezone.
    //    
    //     https://www.w3.org/TR/PNG/#11tIME
    uint16 year;
    ubyte month;
    ubyte day;
    ubyte hour;
    ubyte minute;
    ubyte second;
};
struct international_text_chunk {
    //     International text chunk effectively allows to store key-value string pairs in
    //    PNG container. Both "key" (keyword) and "value" (text) parts are
    //    given in pre-defined subset of iso8859-1 without control
    //    characters.
    //    
    //     https://www.w3.org/TR/PNG/#11iTXt
    string keyword;
    ubyte compression_flag;
    ubyte compression_method;
    string language_tag;
    string translated_keyword;
    string text;
};
struct text_chunk {
    //     Text chunk effectively allows to store key-value string pairs in
    //    PNG container. Both "key" (keyword) and "value" (text) parts are
    //    given in pre-defined subset of iso8859-1 without control
    //    characters.
    //    
    //     https://www.w3.org/TR/PNG/#11tEXt
    string keyword;
    string text;
};
struct compressed_text_chunk {
    //     Compressed text chunk effectively allows to store key-value
    //    string pairs in PNG container, compressing "value" part (which
    //    can be quite lengthy) with zlib compression.
    //    
    //     https://www.w3.org/TR/PNG/#11zTXt
    string keyword;
    ubyte compression_method;
//STUFF MISSING HERE @ NO MAGIC text_datastream {'id': 'text_datastream', 'process': 'zlib', 'size-eos': True}
};
struct animation_control_chunk {
    //     https://wiki.mozilla.org/APNG_Specification#.60acTL.60:_The_Animation_Control_Chunk
    uint32 num_frames;
    uint32 num_plays;
};
struct frame_control_chunk {
    //     https://wiki.mozilla.org/APNG_Specification#.60fcTL.60:_The_Frame_Control_Chunk
    uint32 sequence_number;
    uint32 width;
    uint32 height;
    uint32 x_offset;
    uint32 y_offset;
    uint16 delay_num;
    uint16 delay_den;
    ubyte dispose_op;
    ubyte blend_op;
};
struct frame_data_chunk(int32 lenght) {
    //     https://wiki.mozilla.org/APNG_Specification#.60fdAT.60:_The_Frame_Data_Chunk
    uint32 sequence_number;
//STUFF MISSING HERE @ NO MAGIC frame_data {'id': 'frame_data', 'size-eos': True, 'doc': 'Frame data for the frame. At least one fdAT chunk is required for\neach frame. The compressed datastream is the concatenation of the\ncontents of the data fields of all the fdAT chunks within a frame.\n'}
};
    uint32 ihdr_len;
    ihdr_chunk ihdr;
    byte ihdr_crc[4];
    chunk chunks;