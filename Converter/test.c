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
  none = 0,  // No disposal is done on this frame before rendering the next;
     //the contents of the output buffer are left as is.
     //
  background = 1,  // The frame's region of the output buffer is to be cleared to
     //fully transparent black before rendering the next frame.
     //
  previous = 2  // The frame's region of the output buffer is to be reverted
     //to the previous contents before rendering the next frame.
     //
} dispose_op_values;


enum <byte> {
  source = 0,  // All color components of the frame, including alpha,
     //overwrite the current contents of the frame's output buffer region.
     //
  over = 1  // The frame is composited onto the output buffer based on its alpha
     //
} blend_op_values;


struct chunk{
    uint32 len;
    str type;
    4 crc;
};


struct ihdr_chunk{
  // https://www.w3.org/TR/PNG/#11IHDR
    uint32 width;
    uint32 height;
    ubyte bit_depth;
    ubyte color_type;
    ubyte compression_method;
    ubyte filter_method;
    ubyte interlace_method;
};


struct plte_chunk{
  // https://www.w3.org/TR/PNG/#11PLTE
    rgb entries;
};


struct rgb{
    ubyte r;
    ubyte g;
    ubyte b;
};


struct chrm_chunk{
  // https://www.w3.org/TR/PNG/#11cHRM
    point white_point;
    point red;
    point green;
    point blue;
};


struct point{
    uint32 x_int;
    uint32 y_int;
};


struct gama_chunk{
  // https://www.w3.org/TR/PNG/#11gAMA
    uint32 gamma_int;
};


struct srgb_chunk{
  // https://www.w3.org/TR/PNG/#11sRGB
    ubyte render_intent;
};


struct bkgd_chunk{
  // Background chunk stores default background color to display this
     //image against. Contents depend on `color_type` of the image.
     //
  // https://www.w3.org/TR/PNG/#11bKGD
};


struct bkgd_greyscale{
  // Background chunk for greyscale images.
    uint16 value;
};


struct bkgd_truecolor{
  // Background chunk for truecolor images.
    uint16 red;
    uint16 green;
    uint16 blue;
};


struct bkgd_indexed{
  // Background chunk for images with indexed palette.
    ubyte palette_index;
};


struct phys_chunk{
  // "Physical size" chunk stores data that allows to translate
     //logical pixels into physical units (meters, etc) and vice-versa.
     //
  // https://www.w3.org/TR/PNG/#11pHYs
    uint32 pixels_per_unit_x;     //Number of pixels per physical unit (typically, 1 meter) by X
     //axis.
     //
    uint32 pixels_per_unit_y;     //Number of pixels per physical unit (typically, 1 meter) by Y
     //axis.
     //
    ubyte unit;
};


struct time_chunk{
  // Time chunk stores time stamp of last modification of this image,
     //up to 1 second precision in UTC timezone.
     //
  // https://www.w3.org/TR/PNG/#11tIME
    uint16 year;
    ubyte month;
    ubyte day;
    ubyte hour;
    ubyte minute;
    ubyte second;
};


struct international_text_chunk{
  // International text chunk effectively allows to store key-value string pairs in
     //PNG container. Both "key" (keyword) and "value" (text) parts are
     //given in pre-defined subset of iso8859-1 without control
     //characters.
     //
  // https://www.w3.org/TR/PNG/#11iTXt
    strz keyword;     //Indicates purpose of the following text data.
    ubyte compression_flag;     //0 = text is uncompressed, 1 = text is compressed with a
     //method specified in `compression_method`.
     //
    ubyte compression_method;
    strz language_tag;     //Human language used in `translated_keyword` and `text`
     //attributes - should be a language code conforming to ISO
     //646.IRV:1991.
     //
    strz translated_keyword;     //Keyword translated into language specified in
     //`language_tag`. Line breaks are not allowed.
     //
    str text;     //Text contents ("value" of this key-value pair), written in
     //language specified in `language_tag`. Linke breaks are
     //allowed.
     //
};


struct text_chunk{
  // Text chunk effectively allows to store key-value string pairs in
     //PNG container. Both "key" (keyword) and "value" (text) parts are
     //given in pre-defined subset of iso8859-1 without control
     //characters.
     //
  // https://www.w3.org/TR/PNG/#11tEXt
    strz keyword;     //Indicates purpose of the following text data.
    str text;
};


struct compressed_text_chunk{
  // Compressed text chunk effectively allows to store key-value
     //string pairs in PNG container, compressing "value" part (which
     //can be quite lengthy) with zlib compression.
     //
  // https://www.w3.org/TR/PNG/#11zTXt
    strz keyword;     //Indicates purpose of the following text data.
    ubyte compression_method;
};


struct animation_control_chunk{
  // https://wiki.mozilla.org/APNG_Specification#.60acTL.60:_The_Animation_Control_Chunk
    uint32 num_frames;     //Number of frames, must be equal to the number of `frame_control_chunk`s
    uint32 num_plays;     //Number of times to loop, 0 indicates infinite looping.
};


struct frame_control_chunk{
  // https://wiki.mozilla.org/APNG_Specification#.60fcTL.60:_The_Frame_Control_Chunk
    uint32 sequence_number;     //Sequence number of the animation chunk
    uint32 width;     //Width of the following frame
    uint32 height;     //Height of the following frame
    uint32 x_offset;     //X position at which to render the following frame
    uint32 y_offset;     //Y position at which to render the following frame
    uint16 delay_num;     //Frame delay fraction numerator
    uint16 delay_den;     //Frame delay fraction denominator
    ubyte dispose_op;     //Type of frame area disposal to be done after rendering this frame
    ubyte blend_op;     //Type of frame area rendering for this frame
};


struct frame_data_chunk{
  // https://wiki.mozilla.org/APNG_Specification#.60fdAT.60:_The_Frame_Data_Chunk
    uint32 sequence_number;     //Sequence number of the animation chunk. The fcTL and fdAT chunks
     //have a 4 byte sequence number. Both chunk types share the sequence.
     //The first fcTL chunk must contain sequence number 0, and the sequence
     //numbers in the remaining fcTL and fdAT chunks must be in order, with
     //no gaps or duplicates.
     //
};

