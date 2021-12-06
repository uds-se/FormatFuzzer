typedef enum <byte> color_type {
  greyscale = 0,
  truecolor = 2,
  indexed = 3,
  greyscale_alpha = 4,
  truecolor_alpha = 6
} COLOR_TYPE;


typedef enum <byte> phys_unit {
  unknown = 0,
  meter = 1
} PHYS_UNIT;


typedef enum <byte> compression_methods {
  zlib = 0
} COMPRESSION_METHODS;


typedef enum <byte> dispose_op_values {
  none = 0,  // No disposal is done on this frame before rendering the next; the contents of the output buffer are left as is. 
  background = 1,  // The frame's region of the output buffer is to be cleared to fully transparent black before rendering the next frame. 
  previous = 2  // The frame's region of the output buffer is to be reverted to the previous contents before rendering the next frame. 
} DISPOSE_OP_VALUES;


typedef enum <byte> blend_op_values {
  source = 0,  // All color components of the frame, including alpha, overwrite the current contents of the frame's output buffer region. 
  over = 1  // The frame is composited onto the output buffer based on its alpha 
} BLEND_OP_VALUES;


typedef struct {
    uint32 len;
    STR type;
    4 crc;
} CHUNK;


typedef struct {
  // https://www.w3.org/TR/PNG/#11IHDR
    uint32 width;
    uint32 height;
    ubyte bit_depth;
    ubyte color_type;
    ubyte compression_method;
    ubyte filter_method;
    ubyte interlace_method;
} IHDR_CHUNK;


typedef struct {
  // https://www.w3.org/TR/PNG/#11PLTE
    RGB entries;
} PLTE_CHUNK;


typedef struct {
    ubyte r;
    ubyte g;
    ubyte b;
} RGB;


typedef struct {
  // https://www.w3.org/TR/PNG/#11cHRM
    POINT white_point;
    POINT red;
    POINT green;
    POINT blue;
} CHRM_CHUNK;


typedef struct {
    uint32 x_int;
    uint32 y_int;
} POINT;


typedef struct {
  // https://www.w3.org/TR/PNG/#11gAMA
    uint32 gamma_int;
} GAMA_CHUNK;


typedef struct {
  // https://www.w3.org/TR/PNG/#11sRGB
    ubyte render_intent;
} SRGB_CHUNK;


typedef struct {
  // Background chunk stores default background color to display this image against. Contents depend on `color_type` of the image. 
  // https://www.w3.org/TR/PNG/#11bKGD
} BKGD_CHUNK;


typedef struct {
  // Background chunk for greyscale images.
    uint16 value;
} BKGD_GREYSCALE;


typedef struct {
  // Background chunk for truecolor images.
    uint16 red;
    uint16 green;
    uint16 blue;
} BKGD_TRUECOLOR;


typedef struct {
  // Background chunk for images with indexed palette.
    ubyte palette_index;
} BKGD_INDEXED;


typedef struct {
  // "Physical size" chunk stores data that allows to translate logical pixels into physical units (meters, etc) and vice-versa. 
  // https://www.w3.org/TR/PNG/#11pHYs
    uint32 pixels_per_unit_x;     //Number of pixels per physical unit (typically, 1 meter) by X axis. 
    uint32 pixels_per_unit_y;     //Number of pixels per physical unit (typically, 1 meter) by Y axis. 
    ubyte unit;
} PHYS_CHUNK;


typedef struct {
  // Time chunk stores time stamp of last modification of this image, up to 1 second precision in UTC timezone. 
  // https://www.w3.org/TR/PNG/#11tIME
    uint16 year;
    ubyte month;
    ubyte day;
    ubyte hour;
    ubyte minute;
    ubyte second;
} TIME_CHUNK;


typedef struct {
  // International text chunk effectively allows to store key-value string pairs in PNG container. Both "key" (keyword) and "value" (text) parts are given in pre-defined subset of iso8859-1 without control characters. 
  // https://www.w3.org/TR/PNG/#11iTXt
    STRZ keyword;     //Indicates purpose of the following text data.
    ubyte compression_flag;     //0 = text is uncompressed, 1 = text is compressed with a method specified in `compression_method`. 
    ubyte compression_method;
    STRZ language_tag;     //Human language used in `translated_keyword` and `text` attributes - should be a language code conforming to ISO 646.IRV:1991. 
    STRZ translated_keyword;     //Keyword translated into language specified in `language_tag`. Line breaks are not allowed. 
    STR text;     //Text contents ("value" of this key-value pair), written in language specified in `language_tag`. Linke breaks are allowed. 
} INTERNATIONAL_TEXT_CHUNK;


typedef struct {
  // Text chunk effectively allows to store key-value string pairs in PNG container. Both "key" (keyword) and "value" (text) parts are given in pre-defined subset of iso8859-1 without control characters. 
  // https://www.w3.org/TR/PNG/#11tEXt
    STRZ keyword;     //Indicates purpose of the following text data.
    STR text;
} TEXT_CHUNK;


typedef struct {
  // Compressed text chunk effectively allows to store key-value string pairs in PNG container, compressing "value" part (which can be quite lengthy) with zlib compression. 
  // https://www.w3.org/TR/PNG/#11zTXt
    STRZ keyword;     //Indicates purpose of the following text data.
    ubyte compression_method;
} COMPRESSED_TEXT_CHUNK;


typedef struct {
  // https://wiki.mozilla.org/APNG_Specification#.60acTL.60:_The_Animation_Control_Chunk
    uint32 num_frames;     //Number of frames, must be equal to the number of `frame_control_chunk`s
    uint32 num_plays;     //Number of times to loop, 0 indicates infinite looping.
} ANIMATION_CONTROL_CHUNK;


typedef struct {
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
} FRAME_CONTROL_CHUNK;


typedef struct {
  // https://wiki.mozilla.org/APNG_Specification#.60fdAT.60:_The_Frame_Data_Chunk
    uint32 sequence_number;     //Sequence number of the animation chunk. The fcTL and fdAT chunks have a 4 byte sequence number. Both chunk types share the sequence. The first fcTL chunk must contain sequence number 0, and the sequence numbers in the remaining fcTL and fdAT chunks must be in order, with no gaps or duplicates. 
} FRAME_DATA_CHUNK;

