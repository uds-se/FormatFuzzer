#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"

enum pngColorSpaceType : byte {
	GrayScale = (byte) 0,
	TrueColor = (byte) 2,
	Indexed = (byte) 3,
	AlphaGrayScale = (byte) 4,
	AlphaTrueColor = (byte) 6,
};
std::vector<byte> pngColorSpaceType_values = { GrayScale, TrueColor, Indexed, AlphaGrayScale, AlphaTrueColor };

typedef enum pngColorSpaceType PNG_COLOR_SPACE_TYPE;
std::vector<byte> PNG_COLOR_SPACE_TYPE_values = { GrayScale, TrueColor, Indexed, AlphaGrayScale, AlphaTrueColor };

enum pngCompressionMethod : byte {
	Deflate = (byte) 0,
};
std::vector<byte> pngCompressionMethod_values = { Deflate };

typedef enum pngCompressionMethod PNG_COMPR_METHOD;
std::vector<byte> PNG_COMPR_METHOD_values = { Deflate };

enum pngFilterMethod : byte {
	AdaptiveFiltering = (byte) 0,
};
std::vector<byte> pngFilterMethod_values = { AdaptiveFiltering };

typedef enum pngFilterMethod PNG_FILTER_METHOD;
std::vector<byte> PNG_FILTER_METHOD_values = { AdaptiveFiltering };

enum pngInterlaceMethod : byte {
	NoInterlace = (byte) 0,
	Adam7Interlace = (byte) 1,
};
std::vector<byte> pngInterlaceMethod_values = { NoInterlace, Adam7Interlace };

typedef enum pngInterlaceMethod PNG_INTERLACE_METHOD;
std::vector<byte> PNG_INTERLACE_METHOD_values = { NoInterlace, Adam7Interlace };

enum PNG_SRGB_CHUNK_DATA_enum : byte {
	Perceptual = (byte) 0,
	RelativeColorimetric = (byte) 1,
	Saturation = (byte) 2,
	AbsoluteColorimetric = (byte) 3,
};
std::vector<byte> PNG_SRGB_CHUNK_DATA_enum_values = { Perceptual, RelativeColorimetric, Saturation, AbsoluteColorimetric };

typedef enum PNG_SRGB_CHUNK_DATA_enum PNG_SRGB_CHUNK_DATA;
std::vector<byte> PNG_SRGB_CHUNK_DATA_values = { Perceptual, RelativeColorimetric, Saturation, AbsoluteColorimetric };

enum APNG_DISPOSE_OP_enum : byte {
	APNG_DISPOSE_OP_NONE = (byte) 0,
	APNG_DISPOSE_OP_BACKGROUND = (byte) 1,
	APNG_DISPOSE_OP_PREVIOUS = (byte) 2,
};
std::vector<byte> APNG_DISPOSE_OP_enum_values = { APNG_DISPOSE_OP_NONE, APNG_DISPOSE_OP_BACKGROUND, APNG_DISPOSE_OP_PREVIOUS };

typedef enum APNG_DISPOSE_OP_enum APNG_DISPOSE_OP;
std::vector<byte> APNG_DISPOSE_OP_values = { APNG_DISPOSE_OP_NONE, APNG_DISPOSE_OP_BACKGROUND, APNG_DISPOSE_OP_PREVIOUS };

enum APNG_BLEND_OP_enum : byte {
	APNG_BLEND_OP_SOURCE = (byte) 0,
	APNG_BLEND_OP_OVER = (byte) 1,
};
std::vector<byte> APNG_BLEND_OP_enum_values = { APNG_BLEND_OP_SOURCE, APNG_BLEND_OP_OVER };

typedef enum APNG_BLEND_OP_enum APNG_BLEND_OP;
std::vector<byte> APNG_BLEND_OP_values = { APNG_BLEND_OP_SOURCE, APNG_BLEND_OP_OVER };


class uint16_class {
	int small;
	std::vector<uint16> known_values;
	uint16 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint16);
	uint16 operator () () { return value; }
	uint16_class(int small, std::vector<uint16> known_values = {}) : small(small), known_values(known_values) {}

	uint16 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint16), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint16), 0, known_values);
		}
		return value;
	}

	uint16 generate(std::vector<uint16> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uint16), 0, possible_values);
		return value;
	}
};



class uint16_array_class {
	uint16_class& element;
	std::unordered_map<int, std::vector<uint16>> element_known_values;
	std::vector<uint16> value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::vector<uint16> operator () () { return value; }
	uint16 operator [] (int index) {
		assert_cond((unsigned)index < value.size(), "array index out of bounds");
		return value[index];
	}
	uint16_array_class(uint16_class& element, std::unordered_map<int, std::vector<uint16>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}

	std::vector<uint16> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(uint16), 0, known->second));
				_sizeof += sizeof(uint16);
			}
		}
		return value;
	}
};



class PNG_SIGNATURE {
	std::vector<PNG_SIGNATURE*>& instances;

	std::vector<uint16> btPngSignature_var;

public:
	bool btPngSignature_exists = false;

	std::vector<uint16> btPngSignature() {
		assert_cond(btPngSignature_exists, "struct field btPngSignature does not exist");
		return btPngSignature_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_SIGNATURE& operator () () { return *instances.back(); }
	PNG_SIGNATURE* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_SIGNATURE(std::vector<PNG_SIGNATURE*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_SIGNATURE() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_SIGNATURE* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_SIGNATURE* generate();
};



class uint32_class {
	int small;
	std::vector<uint32> known_values;
	uint32 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint32);
	uint32 operator () () { return value; }
	uint32_class(int small, std::vector<uint32> known_values = {}) : small(small), known_values(known_values) {}

	uint32 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint32), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint32), 0, known_values);
		}
		return value;
	}

	uint32 generate(std::vector<uint32> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uint32), 0, possible_values);
		return value;
	}
};



class char_class {
	int small;
	std::vector<char> known_values;
	char value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(char);
	char operator () () { return value; }
	char_class(int small, std::vector<char> known_values = {}) : small(small), known_values(known_values) {}

	char generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(char), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(char), 0, known_values);
		}
		return value;
	}

	char generate(std::vector<char> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(char), 0, possible_values);
		return value;
	}
};



class char_array_class {
	char_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<char>> element_known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	char operator [] (int index) {
		assert_cond((unsigned)index < value.size(), "array index out of bounds");
		return value[index];
	}
	char_array_class(char_class& element, std::unordered_map<int, std::vector<char>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	char_array_class(char_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> possible_values = {}) {
		check_array_length(size);
		_startof = FTell();
		value = "";
		if (possible_values.size()) {
			value = file_acc.file_string(possible_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (known_values.size()) {
			value = file_acc.file_string(known_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (!element_known_values.size()) {
			if (size == 0)
				 return "";
			value = file_acc.file_string(size);
			_sizeof = size;
			return value;
		}
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(char), 0, known->second));
				_sizeof += sizeof(char);
			}
		}
		return value;
	}
};



class CTYPE {
	std::vector<CTYPE*>& instances;

// union {
	std::string cname_var;
	uint32 ctype_var;
// };

public:
	bool cname_exists = false;
	bool ctype_exists = false;

	std::string cname() {
		assert_cond(cname_exists, "struct field cname does not exist");
		return cname_var;
	}
	uint32 ctype() {
		assert_cond(ctype_exists, "struct field ctype does not exist");
		return ctype_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	CTYPE& operator () () { return *instances.back(); }
	CTYPE* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	CTYPE(std::vector<CTYPE*>& instances) : instances(instances) { instances.push_back(this); }
	~CTYPE() {
		if (generated == 2)
			return;
		while (instances.size()) {
			CTYPE* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	CTYPE* generate();
};

const std::vector<byte> color_types = { GrayScale, TrueColor, Indexed, AlphaGrayScale, AlphaTrueColor };

class ubyte_class {
	int small;
	std::vector<ubyte> known_values;
	ubyte value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(ubyte);
	ubyte operator () () { return value; }
	ubyte_class(int small, std::vector<ubyte> known_values = {}) : small(small), known_values(known_values) {}

	ubyte generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(ubyte), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(ubyte), 0, known_values);
		}
		return value;
	}

	ubyte generate(std::vector<ubyte> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(ubyte), 0, possible_values);
		return value;
	}
};


PNG_COLOR_SPACE_TYPE PNG_COLOR_SPACE_TYPE_generate() {
	return (PNG_COLOR_SPACE_TYPE) file_acc.file_integer(sizeof(byte), 0, PNG_COLOR_SPACE_TYPE_values);
}

PNG_COLOR_SPACE_TYPE PNG_COLOR_SPACE_TYPE_generate(std::vector<byte> known_values) {
	return (PNG_COLOR_SPACE_TYPE) file_acc.file_integer(sizeof(byte), 0, known_values);
}

PNG_COMPR_METHOD PNG_COMPR_METHOD_generate() {
	return (PNG_COMPR_METHOD) file_acc.file_integer(sizeof(byte), 0, PNG_COMPR_METHOD_values);
}

PNG_COMPR_METHOD PNG_COMPR_METHOD_generate(std::vector<byte> known_values) {
	return (PNG_COMPR_METHOD) file_acc.file_integer(sizeof(byte), 0, known_values);
}

PNG_FILTER_METHOD PNG_FILTER_METHOD_generate() {
	return (PNG_FILTER_METHOD) file_acc.file_integer(sizeof(byte), 0, PNG_FILTER_METHOD_values);
}

PNG_FILTER_METHOD PNG_FILTER_METHOD_generate(std::vector<byte> known_values) {
	return (PNG_FILTER_METHOD) file_acc.file_integer(sizeof(byte), 0, known_values);
}

PNG_INTERLACE_METHOD PNG_INTERLACE_METHOD_generate() {
	return (PNG_INTERLACE_METHOD) file_acc.file_integer(sizeof(byte), 0, PNG_INTERLACE_METHOD_values);
}

PNG_INTERLACE_METHOD PNG_INTERLACE_METHOD_generate(std::vector<byte> known_values) {
	return (PNG_INTERLACE_METHOD) file_acc.file_integer(sizeof(byte), 0, known_values);
}


class PNG_CHUNK_IHDR {
	std::vector<PNG_CHUNK_IHDR*>& instances;

	uint32 width_var;
	uint32 height_var;
	ubyte bits_var;
	byte color_type_var;
	byte compr_method_var;
	byte filter_method_var;
	byte interlace_method_var;

public:
	bool width_exists = false;
	bool height_exists = false;
	bool bits_exists = false;
	bool color_type_exists = false;
	bool compr_method_exists = false;
	bool filter_method_exists = false;
	bool interlace_method_exists = false;

	uint32 width() {
		assert_cond(width_exists, "struct field width does not exist");
		return width_var;
	}
	uint32 height() {
		assert_cond(height_exists, "struct field height does not exist");
		return height_var;
	}
	ubyte bits() {
		assert_cond(bits_exists, "struct field bits does not exist");
		return bits_var;
	}
	byte color_type() {
		assert_cond(color_type_exists, "struct field color_type does not exist");
		return color_type_var;
	}
	byte compr_method() {
		assert_cond(compr_method_exists, "struct field compr_method does not exist");
		return compr_method_var;
	}
	byte filter_method() {
		assert_cond(filter_method_exists, "struct field filter_method does not exist");
		return filter_method_var;
	}
	byte interlace_method() {
		assert_cond(interlace_method_exists, "struct field interlace_method does not exist");
		return interlace_method_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_IHDR& operator () () { return *instances.back(); }
	PNG_CHUNK_IHDR* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_IHDR(std::vector<PNG_CHUNK_IHDR*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_IHDR() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_IHDR* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_IHDR* generate();
};



class string_class {
	std::vector<std::string> known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	string_class(std::vector<std::string> known_values = {}) : known_values(known_values) {}

	std::string generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_string();
		} else {
			value = file_acc.file_string(known_values);
		}
		_sizeof = value.length() + 1;
		return value;
	}
};



class PNG_CHUNK_TEXT {
	std::vector<PNG_CHUNK_TEXT*>& instances;

	std::string label_var;
	std::string data_var;

public:
	bool label_exists = false;
	bool data_exists = false;

	std::string label() {
		assert_cond(label_exists, "struct field label does not exist");
		return label_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_TEXT& operator () () { return *instances.back(); }
	PNG_CHUNK_TEXT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_TEXT(std::vector<PNG_CHUNK_TEXT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_TEXT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_TEXT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_TEXT* generate();
};



class byte_class {
	int small;
	std::vector<byte> known_values;
	byte value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(byte);
	byte operator () () { return value; }
	byte_class(int small, std::vector<byte> known_values = {}) : small(small), known_values(known_values) {}

	byte generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(byte), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(byte), 0, known_values);
		}
		return value;
	}

	byte generate(std::vector<byte> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(byte), 0, possible_values);
		return value;
	}
};



class PNG_PALETTE_PIXEL {
	std::vector<PNG_PALETTE_PIXEL*>& instances;

	byte btRed_var;
	byte btGreen_var;
	byte btBlue_var;

public:
	bool btRed_exists = false;
	bool btGreen_exists = false;
	bool btBlue_exists = false;

	byte btRed() {
		assert_cond(btRed_exists, "struct field btRed does not exist");
		return btRed_var;
	}
	byte btGreen() {
		assert_cond(btGreen_exists, "struct field btGreen does not exist");
		return btGreen_var;
	}
	byte btBlue() {
		assert_cond(btBlue_exists, "struct field btBlue does not exist");
		return btBlue_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_PALETTE_PIXEL& operator () () { return *instances.back(); }
	PNG_PALETTE_PIXEL* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_PALETTE_PIXEL(std::vector<PNG_PALETTE_PIXEL*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_PALETTE_PIXEL() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_PALETTE_PIXEL* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_PALETTE_PIXEL* generate();
};



class PNG_PALETTE_PIXEL_array_class {
	PNG_PALETTE_PIXEL& element;
	std::vector<PNG_PALETTE_PIXEL*> value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::vector<PNG_PALETTE_PIXEL*> operator () () { return value; }
	PNG_PALETTE_PIXEL operator [] (int index) {
		assert_cond((unsigned)index < value.size(), "array index out of bounds");
		return *value[index];
	}
	PNG_PALETTE_PIXEL_array_class(PNG_PALETTE_PIXEL& element) : element(element) {}

	std::vector<PNG_PALETTE_PIXEL*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class PNG_CHUNK_PLTE {
	std::vector<PNG_CHUNK_PLTE*>& instances;

	std::vector<PNG_PALETTE_PIXEL*> plteChunkData_var;

public:
	bool plteChunkData_exists = false;

	std::vector<PNG_PALETTE_PIXEL*> plteChunkData() {
		assert_cond(plteChunkData_exists, "struct field plteChunkData does not exist");
		return plteChunkData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_PLTE& operator () () { return *instances.back(); }
	PNG_CHUNK_PLTE* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_PLTE(std::vector<PNG_CHUNK_PLTE*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_PLTE() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_PLTE* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_PLTE* generate(int32 chunkLen);
};



class PNG_POINT {
	std::vector<PNG_POINT*>& instances;

	uint32 x_var;
	uint32 y_var;

public:
	bool x_exists = false;
	bool y_exists = false;

	uint32 x() {
		assert_cond(x_exists, "struct field x does not exist");
		return x_var;
	}
	uint32 y() {
		assert_cond(y_exists, "struct field y does not exist");
		return y_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_POINT& operator () () { return *instances.back(); }
	PNG_POINT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_POINT(std::vector<PNG_POINT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_POINT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_POINT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_POINT* generate();
};



class PNG_CHUNK_CHRM {
	std::vector<PNG_CHUNK_CHRM*>& instances;

	PNG_POINT* white_var;
	PNG_POINT* red_var;
	PNG_POINT* green_var;
	PNG_POINT* blue_var;

public:
	bool white_exists = false;
	bool red_exists = false;
	bool green_exists = false;
	bool blue_exists = false;

	PNG_POINT& white() {
		assert_cond(white_exists, "struct field white does not exist");
		return *white_var;
	}
	PNG_POINT& red() {
		assert_cond(red_exists, "struct field red does not exist");
		return *red_var;
	}
	PNG_POINT& green() {
		assert_cond(green_exists, "struct field green does not exist");
		return *green_var;
	}
	PNG_POINT& blue() {
		assert_cond(blue_exists, "struct field blue does not exist");
		return *blue_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_CHRM& operator () () { return *instances.back(); }
	PNG_CHUNK_CHRM* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_CHRM(std::vector<PNG_CHUNK_CHRM*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_CHRM() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_CHRM* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_CHRM* generate();
};


PNG_SRGB_CHUNK_DATA PNG_SRGB_CHUNK_DATA_generate() {
	return (PNG_SRGB_CHUNK_DATA) file_acc.file_integer(sizeof(byte), 0, PNG_SRGB_CHUNK_DATA_values);
}

PNG_SRGB_CHUNK_DATA PNG_SRGB_CHUNK_DATA_generate(std::vector<byte> known_values) {
	return (PNG_SRGB_CHUNK_DATA) file_acc.file_integer(sizeof(byte), 0, known_values);
}


class PNG_CHUNK_SRGB {
	std::vector<PNG_CHUNK_SRGB*>& instances;

	byte srgbChunkData_var;

public:
	bool srgbChunkData_exists = false;

	byte srgbChunkData() {
		assert_cond(srgbChunkData_exists, "struct field srgbChunkData does not exist");
		return srgbChunkData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_SRGB& operator () () { return *instances.back(); }
	PNG_CHUNK_SRGB* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_SRGB(std::vector<PNG_CHUNK_SRGB*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_SRGB() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_SRGB* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_SRGB* generate();
};



class PNG_CHUNK_IEXT {
	std::vector<PNG_CHUNK_IEXT*>& instances;

	std::string iextIdChunkData_var;
	byte iextCompressionFlag_var;
	byte iextComprMethod_var;
	std::string iextLanguageTag_var;
	std::string iextTranslatedKeyword_var;
	std::string iextValChunkData_var;

public:
	bool iextIdChunkData_exists = false;
	bool iextCompressionFlag_exists = false;
	bool iextComprMethod_exists = false;
	bool iextLanguageTag_exists = false;
	bool iextTranslatedKeyword_exists = false;
	bool iextValChunkData_exists = false;

	std::string iextIdChunkData() {
		assert_cond(iextIdChunkData_exists, "struct field iextIdChunkData does not exist");
		return iextIdChunkData_var;
	}
	byte iextCompressionFlag() {
		assert_cond(iextCompressionFlag_exists, "struct field iextCompressionFlag does not exist");
		return iextCompressionFlag_var;
	}
	byte iextComprMethod() {
		assert_cond(iextComprMethod_exists, "struct field iextComprMethod does not exist");
		return iextComprMethod_var;
	}
	std::string iextLanguageTag() {
		assert_cond(iextLanguageTag_exists, "struct field iextLanguageTag does not exist");
		return iextLanguageTag_var;
	}
	std::string iextTranslatedKeyword() {
		assert_cond(iextTranslatedKeyword_exists, "struct field iextTranslatedKeyword does not exist");
		return iextTranslatedKeyword_var;
	}
	std::string iextValChunkData() {
		assert_cond(iextValChunkData_exists, "struct field iextValChunkData does not exist");
		return iextValChunkData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_IEXT& operator () () { return *instances.back(); }
	PNG_CHUNK_IEXT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_IEXT(std::vector<PNG_CHUNK_IEXT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_IEXT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_IEXT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_IEXT* generate(int32 chunkLen);
};



class PNG_CHUNK_ZEXT {
	std::vector<PNG_CHUNK_ZEXT*>& instances;

	std::string zextIdChunkData_var;
	byte comprMethod_var;
	std::string zextValChunkData_var;

public:
	bool zextIdChunkData_exists = false;
	bool comprMethod_exists = false;
	bool zextValChunkData_exists = false;

	std::string zextIdChunkData() {
		assert_cond(zextIdChunkData_exists, "struct field zextIdChunkData does not exist");
		return zextIdChunkData_var;
	}
	byte comprMethod() {
		assert_cond(comprMethod_exists, "struct field comprMethod does not exist");
		return comprMethod_var;
	}
	std::string zextValChunkData() {
		assert_cond(zextValChunkData_exists, "struct field zextValChunkData does not exist");
		return zextValChunkData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_ZEXT& operator () () { return *instances.back(); }
	PNG_CHUNK_ZEXT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_ZEXT(std::vector<PNG_CHUNK_ZEXT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_ZEXT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_ZEXT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_ZEXT* generate(int32 chunkLen);
};



class int16_class {
	int small;
	std::vector<int16> known_values;
	int16 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(int16);
	int16 operator () () { return value; }
	int16_class(int small, std::vector<int16> known_values = {}) : small(small), known_values(known_values) {}

	int16 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(int16), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(int16), 0, known_values);
		}
		return value;
	}

	int16 generate(std::vector<int16> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(int16), 0, possible_values);
		return value;
	}
};



class PNG_CHUNK_TIME {
	std::vector<PNG_CHUNK_TIME*>& instances;

	int16 timeYear_var;
	byte timeMonth_var;
	byte timeDay_var;
	byte timeHour_var;
	byte timeMin_var;
	byte timeSec_var;

public:
	bool timeYear_exists = false;
	bool timeMonth_exists = false;
	bool timeDay_exists = false;
	bool timeHour_exists = false;
	bool timeMin_exists = false;
	bool timeSec_exists = false;

	int16 timeYear() {
		assert_cond(timeYear_exists, "struct field timeYear does not exist");
		return timeYear_var;
	}
	byte timeMonth() {
		assert_cond(timeMonth_exists, "struct field timeMonth does not exist");
		return timeMonth_var;
	}
	byte timeDay() {
		assert_cond(timeDay_exists, "struct field timeDay does not exist");
		return timeDay_var;
	}
	byte timeHour() {
		assert_cond(timeHour_exists, "struct field timeHour does not exist");
		return timeHour_var;
	}
	byte timeMin() {
		assert_cond(timeMin_exists, "struct field timeMin does not exist");
		return timeMin_var;
	}
	byte timeSec() {
		assert_cond(timeSec_exists, "struct field timeSec does not exist");
		return timeSec_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_TIME& operator () () { return *instances.back(); }
	PNG_CHUNK_TIME* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_TIME(std::vector<PNG_CHUNK_TIME*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_TIME() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_TIME* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_TIME* generate();
};



class uint_class {
	int small;
	std::vector<uint> known_values;
	uint value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint);
	uint operator () () { return value; }
	uint_class(int small, std::vector<uint> known_values = {}) : small(small), known_values(known_values) {}

	uint generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint), 0, known_values);
		}
		return value;
	}

	uint generate(std::vector<uint> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uint), 0, possible_values);
		return value;
	}
};


enum physUnitSpec_enum : byte {
	UnkownUnit = (byte) 0,
	Meter = (byte) 1,
};
std::vector<byte> physUnitSpec_enum_values = { UnkownUnit, Meter };

physUnitSpec_enum physUnitSpec_enum_generate() {
	return (physUnitSpec_enum) file_acc.file_integer(sizeof(byte), 0, physUnitSpec_enum_values);
}

physUnitSpec_enum physUnitSpec_enum_generate(std::vector<byte> known_values) {
	return (physUnitSpec_enum) file_acc.file_integer(sizeof(byte), 0, known_values);
}


class PNG_CHUNK_PHYS {
	std::vector<PNG_CHUNK_PHYS*>& instances;

	uint physPixelPerUnitX_var;
	uint physPixelPerUnitY_var;
	byte physUnitSpec_var;

public:
	bool physPixelPerUnitX_exists = false;
	bool physPixelPerUnitY_exists = false;
	bool physUnitSpec_exists = false;

	uint physPixelPerUnitX() {
		assert_cond(physPixelPerUnitX_exists, "struct field physPixelPerUnitX does not exist");
		return physPixelPerUnitX_var;
	}
	uint physPixelPerUnitY() {
		assert_cond(physPixelPerUnitY_exists, "struct field physPixelPerUnitY does not exist");
		return physPixelPerUnitY_var;
	}
	byte physUnitSpec() {
		assert_cond(physUnitSpec_exists, "struct field physUnitSpec does not exist");
		return physUnitSpec_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_PHYS& operator () () { return *instances.back(); }
	PNG_CHUNK_PHYS* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_PHYS(std::vector<PNG_CHUNK_PHYS*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_PHYS() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_PHYS* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_PHYS* generate();
};



class PNG_CHUNK_BKGD {
	std::vector<PNG_CHUNK_BKGD*>& instances;

	ubyte bgColorPaletteIndex_var;
	uint16 bgGrayscalePixelValue_var;
	uint16 bgColorPixelRed_var;
	uint16 bgColorPixelGreen_var;
	uint16 bgColorPixelBlue_var;

public:
	bool bgColorPaletteIndex_exists = false;
	bool bgGrayscalePixelValue_exists = false;
	bool bgColorPixelRed_exists = false;
	bool bgColorPixelGreen_exists = false;
	bool bgColorPixelBlue_exists = false;

	ubyte bgColorPaletteIndex() {
		assert_cond(bgColorPaletteIndex_exists, "struct field bgColorPaletteIndex does not exist");
		return bgColorPaletteIndex_var;
	}
	uint16 bgGrayscalePixelValue() {
		assert_cond(bgGrayscalePixelValue_exists, "struct field bgGrayscalePixelValue does not exist");
		return bgGrayscalePixelValue_var;
	}
	uint16 bgColorPixelRed() {
		assert_cond(bgColorPixelRed_exists, "struct field bgColorPixelRed does not exist");
		return bgColorPixelRed_var;
	}
	uint16 bgColorPixelGreen() {
		assert_cond(bgColorPixelGreen_exists, "struct field bgColorPixelGreen does not exist");
		return bgColorPixelGreen_var;
	}
	uint16 bgColorPixelBlue() {
		assert_cond(bgColorPixelBlue_exists, "struct field bgColorPixelBlue does not exist");
		return bgColorPixelBlue_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_BKGD& operator () () { return *instances.back(); }
	PNG_CHUNK_BKGD* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_BKGD(std::vector<PNG_CHUNK_BKGD*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_BKGD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_BKGD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_BKGD* generate(int32 colorType);
};



class PNG_CHUNK_SBIT {
	std::vector<PNG_CHUNK_SBIT*>& instances;

	byte sbitRed_var;
	byte sbitGreen_var;
	byte sbitBlue_var;
	byte sbitGraySource_var;
	byte sbitGrayAlphaSource_var;
	byte sbitGrayAlphaSourceAlpha_var;
	byte sbitColorRed_var;
	byte sbitColorGreen_var;
	byte sbitColorBlue_var;
	byte sbitColorAlphaRed_var;
	byte sbitColorAlphaGreen_var;
	byte sbitColorAlphaBlue_var;
	byte sbitColorAlphaAlpha_var;

public:
	bool sbitRed_exists = false;
	bool sbitGreen_exists = false;
	bool sbitBlue_exists = false;
	bool sbitGraySource_exists = false;
	bool sbitGrayAlphaSource_exists = false;
	bool sbitGrayAlphaSourceAlpha_exists = false;
	bool sbitColorRed_exists = false;
	bool sbitColorGreen_exists = false;
	bool sbitColorBlue_exists = false;
	bool sbitColorAlphaRed_exists = false;
	bool sbitColorAlphaGreen_exists = false;
	bool sbitColorAlphaBlue_exists = false;
	bool sbitColorAlphaAlpha_exists = false;

	byte sbitRed() {
		assert_cond(sbitRed_exists, "struct field sbitRed does not exist");
		return sbitRed_var;
	}
	byte sbitGreen() {
		assert_cond(sbitGreen_exists, "struct field sbitGreen does not exist");
		return sbitGreen_var;
	}
	byte sbitBlue() {
		assert_cond(sbitBlue_exists, "struct field sbitBlue does not exist");
		return sbitBlue_var;
	}
	byte sbitGraySource() {
		assert_cond(sbitGraySource_exists, "struct field sbitGraySource does not exist");
		return sbitGraySource_var;
	}
	byte sbitGrayAlphaSource() {
		assert_cond(sbitGrayAlphaSource_exists, "struct field sbitGrayAlphaSource does not exist");
		return sbitGrayAlphaSource_var;
	}
	byte sbitGrayAlphaSourceAlpha() {
		assert_cond(sbitGrayAlphaSourceAlpha_exists, "struct field sbitGrayAlphaSourceAlpha does not exist");
		return sbitGrayAlphaSourceAlpha_var;
	}
	byte sbitColorRed() {
		assert_cond(sbitColorRed_exists, "struct field sbitColorRed does not exist");
		return sbitColorRed_var;
	}
	byte sbitColorGreen() {
		assert_cond(sbitColorGreen_exists, "struct field sbitColorGreen does not exist");
		return sbitColorGreen_var;
	}
	byte sbitColorBlue() {
		assert_cond(sbitColorBlue_exists, "struct field sbitColorBlue does not exist");
		return sbitColorBlue_var;
	}
	byte sbitColorAlphaRed() {
		assert_cond(sbitColorAlphaRed_exists, "struct field sbitColorAlphaRed does not exist");
		return sbitColorAlphaRed_var;
	}
	byte sbitColorAlphaGreen() {
		assert_cond(sbitColorAlphaGreen_exists, "struct field sbitColorAlphaGreen does not exist");
		return sbitColorAlphaGreen_var;
	}
	byte sbitColorAlphaBlue() {
		assert_cond(sbitColorAlphaBlue_exists, "struct field sbitColorAlphaBlue does not exist");
		return sbitColorAlphaBlue_var;
	}
	byte sbitColorAlphaAlpha() {
		assert_cond(sbitColorAlphaAlpha_exists, "struct field sbitColorAlphaAlpha does not exist");
		return sbitColorAlphaAlpha_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_SBIT& operator () () { return *instances.back(); }
	PNG_CHUNK_SBIT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_SBIT(std::vector<PNG_CHUNK_SBIT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_SBIT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_SBIT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_SBIT* generate(int32 colorType);
};



class byte_array_class {
	byte_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<byte>> element_known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	byte operator [] (int index) {
		assert_cond((unsigned)index < value.size(), "array index out of bounds");
		return value[index];
	}
	byte_array_class(byte_class& element, std::unordered_map<int, std::vector<byte>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	byte_array_class(byte_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> possible_values = {}) {
		check_array_length(size);
		_startof = FTell();
		value = "";
		if (possible_values.size()) {
			value = file_acc.file_string(possible_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (known_values.size()) {
			value = file_acc.file_string(known_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(byte), 0, known->second));
				_sizeof += sizeof(byte);
			}
		}
		return value;
	}
};



class PNG_CHUNK_SPLT {
	std::vector<PNG_CHUNK_SPLT*>& instances;

	std::string paletteName_var;
	byte sampleDepth_var;
	std::string spltData_var;

public:
	bool paletteName_exists = false;
	bool sampleDepth_exists = false;
	bool spltData_exists = false;

	std::string paletteName() {
		assert_cond(paletteName_exists, "struct field paletteName does not exist");
		return paletteName_var;
	}
	byte sampleDepth() {
		assert_cond(sampleDepth_exists, "struct field sampleDepth does not exist");
		return sampleDepth_var;
	}
	std::string spltData() {
		assert_cond(spltData_exists, "struct field spltData does not exist");
		return spltData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_SPLT& operator () () { return *instances.back(); }
	PNG_CHUNK_SPLT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_SPLT(std::vector<PNG_CHUNK_SPLT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_SPLT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_SPLT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_SPLT* generate(int32 chunkLen);
};



class PNG_CHUNK_ACTL {
	std::vector<PNG_CHUNK_ACTL*>& instances;

	uint32 num_frames_var;
	uint32 num_plays_var;

public:
	bool num_frames_exists = false;
	bool num_plays_exists = false;

	uint32 num_frames() {
		assert_cond(num_frames_exists, "struct field num_frames does not exist");
		return num_frames_var;
	}
	uint32 num_plays() {
		assert_cond(num_plays_exists, "struct field num_plays does not exist");
		return num_plays_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_ACTL& operator () () { return *instances.back(); }
	PNG_CHUNK_ACTL* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_ACTL(std::vector<PNG_CHUNK_ACTL*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_ACTL() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_ACTL* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_ACTL* generate();
};


APNG_DISPOSE_OP APNG_DISPOSE_OP_generate() {
	return (APNG_DISPOSE_OP) file_acc.file_integer(sizeof(byte), 0, APNG_DISPOSE_OP_values);
}

APNG_DISPOSE_OP APNG_DISPOSE_OP_generate(std::vector<byte> known_values) {
	return (APNG_DISPOSE_OP) file_acc.file_integer(sizeof(byte), 0, known_values);
}

APNG_BLEND_OP APNG_BLEND_OP_generate() {
	return (APNG_BLEND_OP) file_acc.file_integer(sizeof(byte), 0, APNG_BLEND_OP_values);
}

APNG_BLEND_OP APNG_BLEND_OP_generate(std::vector<byte> known_values) {
	return (APNG_BLEND_OP) file_acc.file_integer(sizeof(byte), 0, known_values);
}


class PNG_CHUNK_FCTL {
	std::vector<PNG_CHUNK_FCTL*>& instances;

	uint32 sequence_number_var;
	uint32 width_var;
	uint32 height_var;
	uint32 x_offset_var;
	uint32 y_offset_var;
	int16 delay_num_var;
	int16 delay_den_var;
	byte dispose_op_var;
	byte blend_op_var;

public:
	bool sequence_number_exists = false;
	bool width_exists = false;
	bool height_exists = false;
	bool x_offset_exists = false;
	bool y_offset_exists = false;
	bool delay_num_exists = false;
	bool delay_den_exists = false;
	bool dispose_op_exists = false;
	bool blend_op_exists = false;

	uint32 sequence_number() {
		assert_cond(sequence_number_exists, "struct field sequence_number does not exist");
		return sequence_number_var;
	}
	uint32 width() {
		assert_cond(width_exists, "struct field width does not exist");
		return width_var;
	}
	uint32 height() {
		assert_cond(height_exists, "struct field height does not exist");
		return height_var;
	}
	uint32 x_offset() {
		assert_cond(x_offset_exists, "struct field x_offset does not exist");
		return x_offset_var;
	}
	uint32 y_offset() {
		assert_cond(y_offset_exists, "struct field y_offset does not exist");
		return y_offset_var;
	}
	int16 delay_num() {
		assert_cond(delay_num_exists, "struct field delay_num does not exist");
		return delay_num_var;
	}
	int16 delay_den() {
		assert_cond(delay_den_exists, "struct field delay_den does not exist");
		return delay_den_var;
	}
	byte dispose_op() {
		assert_cond(dispose_op_exists, "struct field dispose_op does not exist");
		return dispose_op_var;
	}
	byte blend_op() {
		assert_cond(blend_op_exists, "struct field blend_op does not exist");
		return blend_op_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_FCTL& operator () () { return *instances.back(); }
	PNG_CHUNK_FCTL* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_FCTL(std::vector<PNG_CHUNK_FCTL*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_FCTL() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_FCTL* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_FCTL* generate();
};



class ubyte_array_class {
	ubyte_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<ubyte>> element_known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	ubyte operator [] (int index) {
		assert_cond((unsigned)index < value.size(), "array index out of bounds");
		return value[index];
	}
	ubyte_array_class(ubyte_class& element, std::unordered_map<int, std::vector<ubyte>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	ubyte_array_class(ubyte_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> possible_values = {}) {
		check_array_length(size);
		_startof = FTell();
		value = "";
		if (possible_values.size()) {
			value = file_acc.file_string(possible_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (known_values.size()) {
			value = file_acc.file_string(known_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(ubyte), 0, known->second));
				_sizeof += sizeof(ubyte);
			}
		}
		return value;
	}
};



class PNG_CHUNK_FDAT {
	std::vector<PNG_CHUNK_FDAT*>& instances;

	uint32 sequence_number_var;
	std::string frame_data_var;

public:
	bool sequence_number_exists = false;
	bool frame_data_exists = false;

	uint32 sequence_number() {
		assert_cond(sequence_number_exists, "struct field sequence_number does not exist");
		return sequence_number_var;
	}
	std::string frame_data() {
		assert_cond(frame_data_exists, "struct field frame_data does not exist");
		return frame_data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK_FDAT& operator () () { return *instances.back(); }
	PNG_CHUNK_FDAT* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK_FDAT(std::vector<PNG_CHUNK_FDAT*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK_FDAT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK_FDAT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK_FDAT* generate();
};



class PNG_CHUNK {
	std::vector<PNG_CHUNK*>& instances;

	uint32 length_var;
	CTYPE* type_var;
	PNG_CHUNK_IHDR* ihdr_var;
	PNG_CHUNK_TEXT* text_var;
	PNG_CHUNK_PLTE* plte_var;
	PNG_CHUNK_CHRM* chrm_var;
	PNG_CHUNK_SRGB* srgb_var;
	PNG_CHUNK_IEXT* iext_var;
	PNG_CHUNK_ZEXT* zext_var;
	PNG_CHUNK_TIME* time_var;
	PNG_CHUNK_PHYS* phys_var;
	PNG_CHUNK_BKGD* bkgd_var;
	PNG_CHUNK_SBIT* sbit_var;
	PNG_CHUNK_SPLT* splt_var;
	PNG_CHUNK_ACTL* actl_var;
	PNG_CHUNK_FCTL* fctl_var;
	PNG_CHUNK_FDAT* fdat_var;
	std::string data_var;
	uint32 crc_var;
	uint16 pad_var;

public:
	bool length_exists = false;
	bool type_exists = false;
	bool ihdr_exists = false;
	bool text_exists = false;
	bool plte_exists = false;
	bool chrm_exists = false;
	bool srgb_exists = false;
	bool iext_exists = false;
	bool zext_exists = false;
	bool time_exists = false;
	bool phys_exists = false;
	bool bkgd_exists = false;
	bool sbit_exists = false;
	bool splt_exists = false;
	bool actl_exists = false;
	bool fctl_exists = false;
	bool fdat_exists = false;
	bool data_exists = false;
	bool crc_exists = false;
	bool pad_exists = false;

	uint32 length() {
		assert_cond(length_exists, "struct field length does not exist");
		return length_var;
	}
	CTYPE& type() {
		assert_cond(type_exists, "struct field type does not exist");
		return *type_var;
	}
	PNG_CHUNK_IHDR& ihdr() {
		assert_cond(ihdr_exists, "struct field ihdr does not exist");
		return *ihdr_var;
	}
	PNG_CHUNK_TEXT& text() {
		assert_cond(text_exists, "struct field text does not exist");
		return *text_var;
	}
	PNG_CHUNK_PLTE& plte() {
		assert_cond(plte_exists, "struct field plte does not exist");
		return *plte_var;
	}
	PNG_CHUNK_CHRM& chrm() {
		assert_cond(chrm_exists, "struct field chrm does not exist");
		return *chrm_var;
	}
	PNG_CHUNK_SRGB& srgb() {
		assert_cond(srgb_exists, "struct field srgb does not exist");
		return *srgb_var;
	}
	PNG_CHUNK_IEXT& iext() {
		assert_cond(iext_exists, "struct field iext does not exist");
		return *iext_var;
	}
	PNG_CHUNK_ZEXT& zext() {
		assert_cond(zext_exists, "struct field zext does not exist");
		return *zext_var;
	}
	PNG_CHUNK_TIME& time() {
		assert_cond(time_exists, "struct field time does not exist");
		return *time_var;
	}
	PNG_CHUNK_PHYS& phys() {
		assert_cond(phys_exists, "struct field phys does not exist");
		return *phys_var;
	}
	PNG_CHUNK_BKGD& bkgd() {
		assert_cond(bkgd_exists, "struct field bkgd does not exist");
		return *bkgd_var;
	}
	PNG_CHUNK_SBIT& sbit() {
		assert_cond(sbit_exists, "struct field sbit does not exist");
		return *sbit_var;
	}
	PNG_CHUNK_SPLT& splt() {
		assert_cond(splt_exists, "struct field splt does not exist");
		return *splt_var;
	}
	PNG_CHUNK_ACTL& actl() {
		assert_cond(actl_exists, "struct field actl does not exist");
		return *actl_var;
	}
	PNG_CHUNK_FCTL& fctl() {
		assert_cond(fctl_exists, "struct field fctl does not exist");
		return *fctl_var;
	}
	PNG_CHUNK_FDAT& fdat() {
		assert_cond(fdat_exists, "struct field fdat does not exist");
		return *fdat_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}
	uint32 crc() {
		assert_cond(crc_exists, "struct field crc does not exist");
		return crc_var;
	}
	uint16 pad() {
		assert_cond(pad_exists, "struct field pad does not exist");
		return pad_var;
	}

	/* locals */
	int64 pos_start;
	int64 pos_end;
	uint32 correct_length;
	int evil;
	int64 data_size;
	uint32 crc_calc;
	std::string msg;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PNG_CHUNK& operator () () { return *instances.back(); }
	PNG_CHUNK* operator [] (int index) {
		assert_cond((unsigned)index < instances.size(), "instance index out of bounds");
		return instances[index];
	}
	PNG_CHUNK(std::vector<PNG_CHUNK*>& instances) : instances(instances) { instances.push_back(this); }
	~PNG_CHUNK() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PNG_CHUNK* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PNG_CHUNK* generate();
};

std::vector<byte> ReadByteInitValues;
std::vector<ubyte> ReadUByteInitValues;
std::vector<short> ReadShortInitValues;
std::vector<ushort> ReadUShortInitValues;
std::vector<int> ReadIntInitValues;
std::vector<uint> ReadUIntInitValues;
std::vector<int64> ReadQuadInitValues;
std::vector<uint64> ReadUQuadInitValues;
std::vector<int64> ReadInt64InitValues;
std::vector<uint64> ReadUInt64InitValues;
std::vector<hfloat> ReadHFloatInitValues;
std::vector<float> ReadFloatInitValues;
std::vector<double> ReadDoubleInitValues;
std::vector<std::string> ReadBytesInitValues;


std::vector<PNG_SIGNATURE*> PNG_SIGNATURE_sig_instances;
std::vector<CTYPE*> CTYPE_type_instances;
std::vector<PNG_CHUNK_IHDR*> PNG_CHUNK_IHDR_ihdr_instances;
std::vector<PNG_CHUNK_TEXT*> PNG_CHUNK_TEXT_text_instances;
std::vector<PNG_PALETTE_PIXEL*> PNG_PALETTE_PIXEL_plteChunkData_element_instances;
std::vector<PNG_CHUNK_PLTE*> PNG_CHUNK_PLTE_plte_instances;
std::vector<PNG_POINT*> PNG_POINT_white_instances;
std::vector<PNG_POINT*> PNG_POINT_red_instances;
std::vector<PNG_POINT*> PNG_POINT_green_instances;
std::vector<PNG_POINT*> PNG_POINT_blue_instances;
std::vector<PNG_CHUNK_CHRM*> PNG_CHUNK_CHRM_chrm_instances;
std::vector<PNG_CHUNK_SRGB*> PNG_CHUNK_SRGB_srgb_instances;
std::vector<PNG_CHUNK_IEXT*> PNG_CHUNK_IEXT_iext_instances;
std::vector<PNG_CHUNK_ZEXT*> PNG_CHUNK_ZEXT_zext_instances;
std::vector<PNG_CHUNK_TIME*> PNG_CHUNK_TIME_time__instances;
std::vector<PNG_CHUNK_PHYS*> PNG_CHUNK_PHYS_phys_instances;
std::vector<PNG_CHUNK_BKGD*> PNG_CHUNK_BKGD_bkgd_instances;
std::vector<PNG_CHUNK_SBIT*> PNG_CHUNK_SBIT_sbit_instances;
std::vector<PNG_CHUNK_SPLT*> PNG_CHUNK_SPLT_splt_instances;
std::vector<PNG_CHUNK_ACTL*> PNG_CHUNK_ACTL_actl_instances;
std::vector<PNG_CHUNK_FCTL*> PNG_CHUNK_FCTL_fctl_instances;
std::vector<PNG_CHUNK_FDAT*> PNG_CHUNK_FDAT_fdat_instances;
std::vector<PNG_CHUNK*> PNG_CHUNK_chunk_instances;


std::unordered_map<std::string, std::string> variable_types = { { "btPngSignature", "uint16_array_class" }, { "sig", "PNG_SIGNATURE" }, { "length", "uint32_class" }, { "cname", "char_array_class" }, { "ctype", "uint32_class" }, { "type", "CTYPE" }, { "width", "uint32_class" }, { "height", "uint32_class" }, { "bits", "ubyte_class" }, { "color_type", "PNG_COLOR_SPACE_TYPE" }, { "compr_method", "PNG_COMPR_METHOD" }, { "filter_method", "PNG_FILTER_METHOD" }, { "interlace_method", "PNG_INTERLACE_METHOD" }, { "ihdr", "PNG_CHUNK_IHDR" }, { "label", "string_class" }, { "data", "char_array_class" }, { "text", "PNG_CHUNK_TEXT" }, { "btRed", "byte_class" }, { "btGreen", "byte_class" }, { "btBlue", "byte_class" }, { "plteChunkData", "PNG_PALETTE_PIXEL_array_class" }, { "plte", "PNG_CHUNK_PLTE" }, { "x", "uint32_class" }, { "y", "uint32_class" }, { "white", "PNG_POINT" }, { "red", "PNG_POINT" }, { "green", "PNG_POINT" }, { "blue", "PNG_POINT" }, { "chrm", "PNG_CHUNK_CHRM" }, { "srgbChunkData", "PNG_SRGB_CHUNK_DATA" }, { "srgb", "PNG_CHUNK_SRGB" }, { "iextIdChunkData", "string_class" }, { "iextCompressionFlag", "byte_class" }, { "iextComprMethod", "PNG_COMPR_METHOD" }, { "iextLanguageTag", "string_class" }, { "iextTranslatedKeyword", "string_class" }, { "iextValChunkData", "char_array_class" }, { "iext", "PNG_CHUNK_IEXT" }, { "zextIdChunkData", "string_class" }, { "comprMethod", "PNG_COMPR_METHOD" }, { "zextValChunkData", "char_array_class" }, { "zext", "PNG_CHUNK_ZEXT" }, { "timeYear", "int16_class" }, { "timeMonth", "byte_class" }, { "timeDay", "byte_class" }, { "timeHour", "byte_class" }, { "timeMin", "byte_class" }, { "timeSec", "byte_class" }, { "time_", "PNG_CHUNK_TIME" }, { "physPixelPerUnitX", "uint_class" }, { "physPixelPerUnitY", "uint_class" }, { "physUnitSpec", "physUnitSpec_enum" }, { "phys", "PNG_CHUNK_PHYS" }, { "bgColorPaletteIndex", "ubyte_class" }, { "bgGrayscalePixelValue", "uint16_class" }, { "bgColorPixelRed", "uint16_class" }, { "bgColorPixelGreen", "uint16_class" }, { "bgColorPixelBlue", "uint16_class" }, { "bkgd", "PNG_CHUNK_BKGD" }, { "sbitRed", "byte_class" }, { "sbitGreen", "byte_class" }, { "sbitBlue", "byte_class" }, { "sbitGraySource", "byte_class" }, { "sbitGrayAlphaSource", "byte_class" }, { "sbitGrayAlphaSourceAlpha", "byte_class" }, { "sbitColorRed", "byte_class" }, { "sbitColorGreen", "byte_class" }, { "sbitColorBlue", "byte_class" }, { "sbitColorAlphaRed", "byte_class" }, { "sbitColorAlphaGreen", "byte_class" }, { "sbitColorAlphaBlue", "byte_class" }, { "sbitColorAlphaAlpha", "byte_class" }, { "sbit", "PNG_CHUNK_SBIT" }, { "paletteName", "string_class" }, { "sampleDepth", "byte_class" }, { "spltData", "byte_array_class" }, { "splt", "PNG_CHUNK_SPLT" }, { "num_frames", "uint32_class" }, { "num_plays", "uint32_class" }, { "actl", "PNG_CHUNK_ACTL" }, { "sequence_number", "uint32_class" }, { "x_offset", "uint32_class" }, { "y_offset", "uint32_class" }, { "delay_num", "int16_class" }, { "delay_den", "int16_class" }, { "dispose_op", "APNG_DISPOSE_OP" }, { "blend_op", "APNG_BLEND_OP" }, { "fctl", "PNG_CHUNK_FCTL" }, { "frame_data", "ubyte_array_class" }, { "fdat", "PNG_CHUNK_FDAT" }, { "data_", "ubyte_array_class" }, { "crc", "uint32_class" }, { "pad", "uint16_class" }, { "chunk", "PNG_CHUNK" } };

std::vector<std::vector<int>> integer_ranges = { { 1, 16 }, { 1, 24 }, { 1, 24 } };

class globals_class {
public:
	/*local*/ uint32 sec_num;
	/*local*/ uint32 CHUNK_CNT;
	/*local*/ int evil;
	uint16_class btPngSignature_element;
	uint16_array_class btPngSignature;
	PNG_SIGNATURE sig;
	/*local*/ int32 chunk_count;
	/*local*/ std::string chunk_type;
	/*local*/ std::vector<std::string> preferred_chunks;
	/*local*/ std::vector<std::string> possible_chunks;
	uint32_class length;
	char_class cname_element;
	char_array_class cname;
	uint32_class ctype;
	CTYPE type;
	uint32_class width;
	uint32_class height;
	ubyte_class bits;
	PNG_CHUNK_IHDR ihdr;
	string_class label;
	char_class data_element;
	char_array_class data;
	PNG_CHUNK_TEXT text;
	byte_class btRed;
	byte_class btGreen;
	byte_class btBlue;
	PNG_PALETTE_PIXEL plteChunkData_element;
	PNG_PALETTE_PIXEL_array_class plteChunkData;
	PNG_CHUNK_PLTE plte;
	uint32_class x;
	uint32_class y;
	PNG_POINT white;
	PNG_POINT red;
	PNG_POINT green;
	PNG_POINT blue;
	PNG_CHUNK_CHRM chrm;
	PNG_CHUNK_SRGB srgb;
	string_class iextIdChunkData;
	byte_class iextCompressionFlag;
	string_class iextLanguageTag;
	string_class iextTranslatedKeyword;
	char_class iextValChunkData_element;
	char_array_class iextValChunkData;
	PNG_CHUNK_IEXT iext;
	string_class zextIdChunkData;
	char_class zextValChunkData_element;
	char_array_class zextValChunkData;
	PNG_CHUNK_ZEXT zext;
	int16_class timeYear;
	byte_class timeMonth;
	byte_class timeDay;
	byte_class timeHour;
	byte_class timeMin;
	byte_class timeSec;
	PNG_CHUNK_TIME time_;
	uint_class physPixelPerUnitX;
	uint_class physPixelPerUnitY;
	PNG_CHUNK_PHYS phys;
	ubyte_class bgColorPaletteIndex;
	uint16_class bgGrayscalePixelValue;
	uint16_class bgColorPixelRed;
	uint16_class bgColorPixelGreen;
	uint16_class bgColorPixelBlue;
	PNG_CHUNK_BKGD bkgd;
	byte_class sbitRed;
	byte_class sbitGreen;
	byte_class sbitBlue;
	byte_class sbitGraySource;
	byte_class sbitGrayAlphaSource;
	byte_class sbitGrayAlphaSourceAlpha;
	byte_class sbitColorRed;
	byte_class sbitColorGreen;
	byte_class sbitColorBlue;
	byte_class sbitColorAlphaRed;
	byte_class sbitColorAlphaGreen;
	byte_class sbitColorAlphaBlue;
	byte_class sbitColorAlphaAlpha;
	PNG_CHUNK_SBIT sbit;
	string_class paletteName;
	byte_class sampleDepth;
	byte_class spltData_element;
	byte_array_class spltData;
	PNG_CHUNK_SPLT splt;
	uint32_class num_frames;
	uint32_class num_plays;
	PNG_CHUNK_ACTL actl;
	uint32_class sequence_number;
	uint32_class x_offset;
	uint32_class y_offset;
	int16_class delay_num;
	int16_class delay_den;
	PNG_CHUNK_FCTL fctl;
	ubyte_class frame_data_element;
	ubyte_array_class frame_data;
	PNG_CHUNK_FDAT fdat;
	ubyte_class data__element;
	ubyte_array_class data_;
	uint32_class crc;
	uint16_class pad;
	PNG_CHUNK chunk;


	globals_class() :
		btPngSignature_element(false),
		btPngSignature(btPngSignature_element, { { 0, {{0x8950}} }, { 1, {{0x4E47}} }, { 2, {{0x0D0A}} }, { 3, {{0x1A0A}} } }),
		sig(PNG_SIGNATURE_sig_instances),
		chunk_type(4, 0),
		length(2),
		cname_element(false),
		cname(cname_element, { "IHDR", "tEXt", "PLTE", "cHRM", "sRGB", "iEXt", "zEXt", "tIME", "pHYs", "bKGD", "sBIT", "sPLT", "acTL", "fcTL", "fdAT", "IEND", "eXIf", "IHDR", "IEND" }),
		ctype(1),
		type(CTYPE_type_instances),
		width(3),
		height(4),
		bits(1),
		ihdr(PNG_CHUNK_IHDR_ihdr_instances),
		data_element(false),
		data(data_element),
		text(PNG_CHUNK_TEXT_text_instances),
		btRed(1),
		btGreen(1),
		btBlue(1),
		plteChunkData_element(PNG_PALETTE_PIXEL_plteChunkData_element_instances),
		plteChunkData(plteChunkData_element),
		plte(PNG_CHUNK_PLTE_plte_instances),
		x(1),
		y(1),
		white(PNG_POINT_white_instances),
		red(PNG_POINT_red_instances),
		green(PNG_POINT_green_instances),
		blue(PNG_POINT_blue_instances),
		chrm(PNG_CHUNK_CHRM_chrm_instances),
		srgb(PNG_CHUNK_SRGB_srgb_instances),
		iextCompressionFlag(1),
		iextValChunkData_element(false),
		iextValChunkData(iextValChunkData_element),
		iext(PNG_CHUNK_IEXT_iext_instances),
		zextValChunkData_element(false),
		zextValChunkData(zextValChunkData_element),
		zext(PNG_CHUNK_ZEXT_zext_instances),
		timeYear(1),
		timeMonth(1),
		timeDay(1),
		timeHour(1),
		timeMin(1),
		timeSec(1),
		time_(PNG_CHUNK_TIME_time__instances),
		physPixelPerUnitX(1),
		physPixelPerUnitY(1),
		phys(PNG_CHUNK_PHYS_phys_instances),
		bgColorPaletteIndex(1),
		bgGrayscalePixelValue(1),
		bgColorPixelRed(1),
		bgColorPixelGreen(1),
		bgColorPixelBlue(1),
		bkgd(PNG_CHUNK_BKGD_bkgd_instances),
		sbitRed(1),
		sbitGreen(1),
		sbitBlue(1),
		sbitGraySource(1),
		sbitGrayAlphaSource(1),
		sbitGrayAlphaSourceAlpha(1),
		sbitColorRed(1),
		sbitColorGreen(1),
		sbitColorBlue(1),
		sbitColorAlphaRed(1),
		sbitColorAlphaGreen(1),
		sbitColorAlphaBlue(1),
		sbitColorAlphaAlpha(1),
		sbit(PNG_CHUNK_SBIT_sbit_instances),
		sampleDepth(1),
		spltData_element(false),
		spltData(spltData_element),
		splt(PNG_CHUNK_SPLT_splt_instances),
		num_frames(1),
		num_plays(1),
		actl(PNG_CHUNK_ACTL_actl_instances),
		sequence_number(1),
		x_offset(1),
		y_offset(1),
		delay_num(1),
		delay_den(1),
		fctl(PNG_CHUNK_FCTL_fctl_instances),
		frame_data_element(false),
		frame_data(frame_data_element),
		fdat(PNG_CHUNK_FDAT_fdat_instances),
		data__element(false),
		data_(data__element),
		crc(1),
		pad(1),
		chunk(PNG_CHUNK_chunk_instances)
	{}
};

globals_class* g;

void error_message(std::string msg) {
	Warning(msg);
	Printf((msg + "\n"));
}

PNG_SIGNATURE* PNG_SIGNATURE::generate() {
	if (generated == 1) {
		PNG_SIGNATURE* new_instance = new PNG_SIGNATURE(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(btPngSignature, ::g->btPngSignature.generate(4));

	_sizeof = FTell() - _startof;
	return this;
}


CTYPE* CTYPE::generate() {
	if (generated == 1) {
		CTYPE* new_instance = new CTYPE(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(cname, ::g->cname.generate(4));
	GENERATE_EXISTS(ctype, ::g->ctype.generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_IHDR* PNG_CHUNK_IHDR::generate() {
	if (generated == 1) {
		PNG_CHUNK_IHDR* new_instance = new PNG_CHUNK_IHDR(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(width, ::g->width.generate());
	GENERATE_VAR(height, ::g->height.generate());
	switch (ReadByte((FTell() + 1), color_types)) {
	case GrayScale:
		GENERATE_VAR(bits, ::g->bits.generate({ 1, 2, 4, 8, 16 }));
		break;
	case TrueColor:
		GENERATE_VAR(bits, ::g->bits.generate({ 8, 16 }));
		break;
	case Indexed:
		GENERATE_VAR(bits, ::g->bits.generate({ 1, 2, 4, 8 }));
		break;
	case AlphaGrayScale:
		GENERATE_VAR(bits, ::g->bits.generate({ 8, 16 }));
		break;
	case AlphaTrueColor:
		GENERATE_VAR(bits, ::g->bits.generate({ 8, 16 }));
		break;
	default:
		GENERATE_VAR(bits, ::g->bits.generate());
		break;
	};
	GENERATE_VAR(color_type, PNG_COLOR_SPACE_TYPE_generate());
	GENERATE_VAR(compr_method, PNG_COMPR_METHOD_generate());
	GENERATE_VAR(filter_method, PNG_FILTER_METHOD_generate());
	GENERATE_VAR(interlace_method, PNG_INTERLACE_METHOD_generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_TEXT* PNG_CHUNK_TEXT::generate() {
	if (generated == 1) {
		PNG_CHUNK_TEXT* new_instance = new PNG_CHUNK_TEXT(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(label, ::g->label.generate());
	GENERATE_VAR(data, ::g->data.generate(((::g->length() - Strlen(label())) - 1)));

	_sizeof = FTell() - _startof;
	return this;
}


PNG_PALETTE_PIXEL* PNG_PALETTE_PIXEL::generate() {
	if (generated == 1) {
		PNG_PALETTE_PIXEL* new_instance = new PNG_PALETTE_PIXEL(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(btRed, ::g->btRed.generate());
	GENERATE_VAR(btGreen, ::g->btGreen.generate());
	GENERATE_VAR(btBlue, ::g->btBlue.generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_PLTE* PNG_CHUNK_PLTE::generate(int32 chunkLen) {
	if (generated == 1) {
		PNG_CHUNK_PLTE* new_instance = new PNG_CHUNK_PLTE(instances);
		new_instance->generated = 2;
		return new_instance->generate(chunkLen);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(plteChunkData, ::g->plteChunkData.generate((chunkLen / 3)));

	_sizeof = FTell() - _startof;
	return this;
}


PNG_POINT* PNG_POINT::generate() {
	if (generated == 1) {
		PNG_POINT* new_instance = new PNG_POINT(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(x, ::g->x.generate());
	GENERATE_VAR(y, ::g->y.generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_CHRM* PNG_CHUNK_CHRM::generate() {
	if (generated == 1) {
		PNG_CHUNK_CHRM* new_instance = new PNG_CHUNK_CHRM(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(white, ::g->white.generate());
	GENERATE_VAR(red, ::g->red.generate());
	GENERATE_VAR(green, ::g->green.generate());
	GENERATE_VAR(blue, ::g->blue.generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_SRGB* PNG_CHUNK_SRGB::generate() {
	if (generated == 1) {
		PNG_CHUNK_SRGB* new_instance = new PNG_CHUNK_SRGB(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(srgbChunkData, PNG_SRGB_CHUNK_DATA_generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_IEXT* PNG_CHUNK_IEXT::generate(int32 chunkLen) {
	if (generated == 1) {
		PNG_CHUNK_IEXT* new_instance = new PNG_CHUNK_IEXT(instances);
		new_instance->generated = 2;
		return new_instance->generate(chunkLen);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(iextIdChunkData, ::g->iextIdChunkData.generate());
	GENERATE_VAR(iextCompressionFlag, ::g->iextCompressionFlag.generate());
	GENERATE_VAR(iextComprMethod, PNG_COMPR_METHOD_generate());
	GENERATE_VAR(iextLanguageTag, ::g->iextLanguageTag.generate());
	GENERATE_VAR(iextTranslatedKeyword, ::g->iextTranslatedKeyword.generate());
	GENERATE_VAR(iextValChunkData, ::g->iextValChunkData.generate((((((((chunkLen - Strlen(iextIdChunkData())) - 1) - Strlen(iextLanguageTag())) - 1) - Strlen(iextTranslatedKeyword())) - 1) - 2)));

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_ZEXT* PNG_CHUNK_ZEXT::generate(int32 chunkLen) {
	if (generated == 1) {
		PNG_CHUNK_ZEXT* new_instance = new PNG_CHUNK_ZEXT(instances);
		new_instance->generated = 2;
		return new_instance->generate(chunkLen);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(zextIdChunkData, ::g->zextIdChunkData.generate());
	GENERATE_VAR(comprMethod, PNG_COMPR_METHOD_generate());
	GENERATE_VAR(zextValChunkData, ::g->zextValChunkData.generate(((chunkLen - Strlen(zextIdChunkData())) - 2)));

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_TIME* PNG_CHUNK_TIME::generate() {
	if (generated == 1) {
		PNG_CHUNK_TIME* new_instance = new PNG_CHUNK_TIME(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(timeYear, ::g->timeYear.generate());
	GENERATE_VAR(timeMonth, ::g->timeMonth.generate());
	GENERATE_VAR(timeDay, ::g->timeDay.generate());
	GENERATE_VAR(timeHour, ::g->timeHour.generate());
	GENERATE_VAR(timeMin, ::g->timeMin.generate());
	GENERATE_VAR(timeSec, ::g->timeSec.generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_PHYS* PNG_CHUNK_PHYS::generate() {
	if (generated == 1) {
		PNG_CHUNK_PHYS* new_instance = new PNG_CHUNK_PHYS(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(physPixelPerUnitX, ::g->physPixelPerUnitX.generate());
	GENERATE_VAR(physPixelPerUnitY, ::g->physPixelPerUnitY.generate());
	GENERATE_VAR(physUnitSpec, physUnitSpec_enum_generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_BKGD* PNG_CHUNK_BKGD::generate(int32 colorType) {
	if (generated == 1) {
		PNG_CHUNK_BKGD* new_instance = new PNG_CHUNK_BKGD(instances);
		new_instance->generated = 2;
		return new_instance->generate(colorType);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	switch (colorType) {
	case 3:
		GENERATE_VAR(bgColorPaletteIndex, ::g->bgColorPaletteIndex.generate());
		break;
	case 0:
	case 4:
		GENERATE_VAR(bgGrayscalePixelValue, ::g->bgGrayscalePixelValue.generate());
		break;
	case 2:
	case 6:
		GENERATE_VAR(bgColorPixelRed, ::g->bgColorPixelRed.generate());
		GENERATE_VAR(bgColorPixelGreen, ::g->bgColorPixelGreen.generate());
		GENERATE_VAR(bgColorPixelBlue, ::g->bgColorPixelBlue.generate());
		break;
	default:
		error_message("*WARNING: Unknown Color Model Type for background color chunk.");
		exit_template(-4);
	};

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_SBIT* PNG_CHUNK_SBIT::generate(int32 colorType) {
	if (generated == 1) {
		PNG_CHUNK_SBIT* new_instance = new PNG_CHUNK_SBIT(instances);
		new_instance->generated = 2;
		return new_instance->generate(colorType);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	switch (colorType) {
	case 3:
		GENERATE_VAR(sbitRed, ::g->sbitRed.generate());
		GENERATE_VAR(sbitGreen, ::g->sbitGreen.generate());
		GENERATE_VAR(sbitBlue, ::g->sbitBlue.generate());
		break;
	case 0:
		GENERATE_VAR(sbitGraySource, ::g->sbitGraySource.generate());
		break;
	case 4:
		GENERATE_VAR(sbitGrayAlphaSource, ::g->sbitGrayAlphaSource.generate());
		GENERATE_VAR(sbitGrayAlphaSourceAlpha, ::g->sbitGrayAlphaSourceAlpha.generate());
		break;
	case 2:
		GENERATE_VAR(sbitColorRed, ::g->sbitColorRed.generate());
		GENERATE_VAR(sbitColorGreen, ::g->sbitColorGreen.generate());
		GENERATE_VAR(sbitColorBlue, ::g->sbitColorBlue.generate());
		break;
	case 6:
		GENERATE_VAR(sbitColorAlphaRed, ::g->sbitColorAlphaRed.generate());
		GENERATE_VAR(sbitColorAlphaGreen, ::g->sbitColorAlphaGreen.generate());
		GENERATE_VAR(sbitColorAlphaBlue, ::g->sbitColorAlphaBlue.generate());
		GENERATE_VAR(sbitColorAlphaAlpha, ::g->sbitColorAlphaAlpha.generate());
		break;
	default:
		error_message("*WARNING: Unknown Color Model Type for background color chunk.");
		exit_template(-4);
	};

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_SPLT* PNG_CHUNK_SPLT::generate(int32 chunkLen) {
	if (generated == 1) {
		PNG_CHUNK_SPLT* new_instance = new PNG_CHUNK_SPLT(instances);
		new_instance->generated = 2;
		return new_instance->generate(chunkLen);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(paletteName, ::g->paletteName.generate());
	GENERATE_VAR(sampleDepth, ::g->sampleDepth.generate());
	GENERATE_VAR(spltData, ::g->spltData.generate(((chunkLen - Strlen(paletteName())) - 2)));

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_ACTL* PNG_CHUNK_ACTL::generate() {
	if (generated == 1) {
		PNG_CHUNK_ACTL* new_instance = new PNG_CHUNK_ACTL(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(num_frames, ::g->num_frames.generate());
	GENERATE_VAR(num_plays, ::g->num_plays.generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_FCTL* PNG_CHUNK_FCTL::generate() {
	if (generated == 1) {
		PNG_CHUNK_FCTL* new_instance = new PNG_CHUNK_FCTL(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(sequence_number, ::g->sequence_number.generate({ ::g->sec_num++ }));
	GENERATE_VAR(width, ::g->width.generate());
	GENERATE_VAR(height, ::g->height.generate());
	GENERATE_VAR(x_offset, ::g->x_offset.generate());
	GENERATE_VAR(y_offset, ::g->y_offset.generate());
	GENERATE_VAR(delay_num, ::g->delay_num.generate());
	GENERATE_VAR(delay_den, ::g->delay_den.generate());
	GENERATE_VAR(dispose_op, APNG_DISPOSE_OP_generate());
	GENERATE_VAR(blend_op, APNG_BLEND_OP_generate());

	_sizeof = FTell() - _startof;
	return this;
}


PNG_CHUNK_FDAT* PNG_CHUNK_FDAT::generate() {
	if (generated == 1) {
		PNG_CHUNK_FDAT* new_instance = new PNG_CHUNK_FDAT(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(sequence_number, ::g->sequence_number.generate({ ::g->sec_num++ }));
	GENERATE_VAR(frame_data, ::g->frame_data.generate((::g->length() - 4)));

	_sizeof = FTell() - _startof;
	return this;
}



std::string compress_data(std::string data, int level) {
	unsigned long data_len = data.size();
	unsigned long comp_len = compressBound(data_len);
	unsigned char* compressed = (unsigned char*) malloc(comp_len);
	compress2(compressed, &comp_len, (const Bytef*) data.c_str(), data_len, level);
	std::string compressed_str((char*) compressed, comp_len);
	free(compressed);
	return compressed_str;
}

std::string generate_data(uint32 width, uint32 height, PNG_COLOR_SPACE_TYPE color, ubyte bit_depth, PNG_INTERLACE_METHOD interlace) {
	int channels_per_pixel[] = {1, 0, 3, 1, 2, 0, 4};
	int bits_per_pixel = 0;
	if (0 <= color && color <= 6)
		bits_per_pixel = channels_per_pixel[color] * bit_depth;
	assert_cond(bits_per_pixel, "Invalid color");
	const unsigned max_size = 16384;
	assert_cond(width <= max_size && height <= max_size && bits_per_pixel * width * height <= 4 * max_size, "image dimensions too large");
	std::string data;
	data.reserve(max_size);
	unsigned char uncompressed[max_size];
	unsigned long data_len = max_size;
	if (!file_acc.generate) {
		int res = uncompress(uncompressed, &data_len, &file_acc.file_buffer[file_acc.file_pos], ::g->length());
		assert_cond (res == Z_OK, "failed to uncompress IDAT data");
	}

	int interlacing[7][4] = {{0, 8, 0, 8},
		                 {4, 8, 0, 8},
		                 {0, 4, 4, 8},
		                 {2, 4, 0, 4},
		                 {0, 2, 2, 4},
		                 {1, 2, 0, 2},
		                 {0, 1, 1, 2}};

	if (!interlace) {
		for (unsigned y = 0; y < height; ++y) {
			assert_cond(data.length() < max_size, "image dimensions too large");
			unsigned char current_byte = uncompressed[data.length()];
			if (!file_acc.generate)
				file_acc.parse = [&current_byte](unsigned char* file_buf) -> long long { return current_byte; };
			unsigned char filter_type = file_acc.rand_int(5, file_acc.parse);
			data += filter_type;
			int bytes_per_scanline = (bits_per_pixel * width + 7)/8;
			if (file_acc.generate) {
				data += file_acc.rand_bytes(bytes_per_scanline);
			} else {
				memcpy(&file_acc.rand_buffer[file_acc.rand_pos], &uncompressed[data.length()], bytes_per_scanline);
				file_acc.rand_pos += bytes_per_scanline;
				std::string s((char*)&uncompressed[data.length()], bytes_per_scanline);
				data += s;
			}
		}
	} else {
		for (unsigned pass = 0; pass < 7; ++pass) {
			int pixels_per_scanline = (width - interlacing[pass][0] + interlacing[pass][1] - 1)/interlacing[pass][1];
			if (!pixels_per_scanline)
				continue;
			int scanlines_per_pass = (height - interlacing[pass][2] + interlacing[pass][3] - 1)/interlacing[pass][3];
			int bytes_per_scanline = (bits_per_pixel * pixels_per_scanline + 7)/8;
			for (int y = 0; y < scanlines_per_pass; ++y) {
				assert_cond(data.length() < max_size, "image dimensions too large");
				unsigned char current_byte = uncompressed[data.length()];
				if (!file_acc.generate)
					file_acc.parse = [&current_byte](unsigned char* file_buf) -> long long { return current_byte; };
				unsigned char filter_type = file_acc.rand_int(5, file_acc.parse);
				data += filter_type;
				if (file_acc.generate) {
					data += file_acc.rand_bytes(bytes_per_scanline);
				} else {
					memcpy(&file_acc.rand_buffer[file_acc.rand_pos], &uncompressed[data.length()], bytes_per_scanline);
					file_acc.rand_pos += bytes_per_scanline;
					std::string s((char*)&uncompressed[data.length()], bytes_per_scanline);
					data += s;
				}
			}
		}
	}

	if (!file_acc.generate) {
		assert_cond(data_len == data.length(), "wrong length for uncompressed IDAT data");
		file_acc.parse = NULL;
		std::string compressed((char*)&file_acc.file_buffer[file_acc.file_pos], ::g->length());
		for (int l = 0; l < 10; ++l)
			if (compress_data(data, l) == compressed) {
				file_acc.parse = [l](unsigned char* file_buf) -> long long { return l + 1; };
				break;
			}
		assert_cond(!!file_acc.parse, "failed to find working compression level");
	}
	int level = file_acc.rand_int(11, file_acc.parse) - 1;
	return compress_data(data, level);
}



PNG_CHUNK* PNG_CHUNK::generate() {
	if (generated == 1) {
		PNG_CHUNK* new_instance = new PNG_CHUNK(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(length, ::g->length.generate());
	pos_start = FTell();
	GENERATE_VAR(type, ::g->type.generate());
	if ((type().cname() == "IHDR")) {
		GENERATE_VAR(ihdr, ::g->ihdr.generate());
	} else {
	if ((type().cname() == "tEXt")) {
		GENERATE_VAR(text, ::g->text.generate());
	} else {
	if ((type().cname() == "PLTE")) {
		GENERATE_VAR(plte, ::g->plte.generate(length()));
	} else {
	if ((type().cname() == "cHRM")) {
		GENERATE_VAR(chrm, ::g->chrm.generate());
	} else {
	if ((type().cname() == "sRGB")) {
		GENERATE_VAR(srgb, ::g->srgb.generate());
	} else {
	if ((type().cname() == "iEXt")) {
		GENERATE_VAR(iext, ::g->iext.generate(length()));
	} else {
	if ((type().cname() == "zEXt")) {
		GENERATE_VAR(zext, ::g->zext.generate(length()));
	} else {
	if ((type().cname() == "tIME")) {
		GENERATE_VAR(time, ::g->time_.generate());
	} else {
	if ((type().cname() == "pHYs")) {
		GENERATE_VAR(phys, ::g->phys.generate());
	} else {
	if ((type().cname() == "bKGD")) {
		GENERATE_VAR(bkgd, ::g->bkgd.generate(::g->chunk()[0]->ihdr().color_type()));
	} else {
	if ((type().cname() == "sBIT")) {
		GENERATE_VAR(sbit, ::g->sbit.generate(::g->chunk()[0]->ihdr().color_type()));
	} else {
	if ((type().cname() == "sPLT")) {
		GENERATE_VAR(splt, ::g->splt.generate(length()));
	} else {
	if ((type().cname() == "acTL")) {
		GENERATE_VAR(actl, ::g->actl.generate());
	} else {
	if ((type().cname() == "fcTL")) {
		GENERATE_VAR(fctl, ::g->fctl.generate());
	} else {
	if ((type().cname() == "fdAT")) {
		GENERATE_VAR(fdat, ::g->fdat.generate());
	} else {
	if ((type().cname() == "IDAT")) {
		std::string compressed_data = generate_data(::g->chunk()[0]->ihdr().width(), ::g->chunk()[0]->ihdr().height(), (PNG_COLOR_SPACE_TYPE) ::g->chunk()[0]->ihdr().color_type(), ::g->chunk()[0]->ihdr().bits(), (PNG_INTERLACE_METHOD) ::g->chunk()[0]->ihdr().interlace_method());
		std::vector<std::string> good_data = { compressed_data };
		bool evil = file_acc.set_evil_bit(false);
		start_generation("data");
		file_acc.file_string(good_data);
		end_generation();
		file_acc.set_evil_bit(evil);
	} else {
	if (((length() > 0) && (type().cname() != "IEND"))) {
		GENERATE_VAR(data, ::g->data_.generate(length()));
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	pos_end = FTell();
	correct_length = ((pos_end - pos_start) - 4);
	if ((length() != correct_length)) {
		FSeek((pos_start - 4));
		evil = SetEvilBit(false);
		GENERATE_VAR(length, ::g->length.generate({ correct_length }));
		SetEvilBit(evil);
		FSeek(pos_end);
	};
	data_size = (pos_end - pos_start);
	crc_calc = Checksum(CHECKSUM_CRC32, pos_start, data_size);
	GENERATE_VAR(crc, ::g->crc.generate({ crc_calc }));
	if ((crc() != crc_calc)) {
		SPrintf(msg, "*ERROR: CRC Mismatch @ chunk[%d]; in data: %08x; expected: %08x", ::g->CHUNK_CNT, crc(), crc_calc);
		error_message(msg);
	};
	::g->CHUNK_CNT++;
	if ((type().cname() == "eXIf")) {
		GENERATE_VAR(pad, ::g->pad.generate());
	};

	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	BigEndian();
	::g->sec_num = 0;
	::g->CHUNK_CNT = 0;
	::g->evil = SetEvilBit(false);
	GENERATE(sig, ::g->sig.generate());
	SetEvilBit(::g->evil);
	if (((((::g->sig().btPngSignature()[0] != 0x8950) || (::g->sig().btPngSignature()[1] != 0x4E47)) || (::g->sig().btPngSignature()[2] != 0x0D0A)) || (::g->sig().btPngSignature()[3] != 0x1A0A))) {
		error_message("*ERROR: File is not a PNG image. Template stopped.");
		exit_template(-1);
	};
	ChangeArrayLength();
	::g->chunk_count = 0;
	::g->preferred_chunks = { "IHDR" };
	::g->possible_chunks = { "IHDR" };
	while (ReadBytes(::g->chunk_type, (FTell() + 4), 4, ::g->preferred_chunks, ::g->possible_chunks)) {
		SetBackColor(((::g->chunk_count++ % 2) ? cNone : cLtGray));
		GENERATE(chunk, ::g->chunk.generate());
		switch (STR2INT(::g->chunk_type)) {
		case STR2INT("IHDR"):
			switch (::g->chunk().ihdr().color_type()) {
			case Indexed:
				::g->preferred_chunks = { "PLTE" };
				::g->possible_chunks = { "tIME", "zTXt", "tEXt", "iTXt", "pHYs", "sPLT", "iCCP", "sRGB", "sBIT", "gAMA", "cHRM", "iEXt", "zEXt", "acTL", "fcTL", "fdAT", "eXIf", "PLTE" };
				break;
			case GrayScale:
			case AlphaGrayScale:
				::g->preferred_chunks = { "IDAT" };
				::g->possible_chunks = { "tIME", "zTXt", "tEXt", "iTXt", "pHYs", "sPLT", "iCCP", "sRGB", "sBIT", "gAMA", "cHRM", "tRNS", "bKGD", "iEXt", "zEXt", "acTL", "fcTL", "fdAT", "eXIf", "IDAT" };
				break;
			default:
				::g->preferred_chunks = { "PLTE", "IDAT" };
				::g->possible_chunks = { "tIME", "zTXt", "tEXt", "iTXt", "pHYs", "sPLT", "iCCP", "sRGB", "sBIT", "gAMA", "cHRM", "PLTE", "tRNS", "bKGD", "iEXt", "zEXt", "acTL", "fcTL", "fdAT", "eXIf", "IDAT" };
			};
			break;
		case STR2INT("tIME"):
			VectorRemove(::g->possible_chunks, { "tIME" });
			break;
		case STR2INT("pHYs"):
			VectorRemove(::g->possible_chunks, { "pHYs" });
			break;
		case STR2INT("iCCP"):
			VectorRemove(::g->possible_chunks, { "iCCP", "sRGB" });
			break;
		case STR2INT("sRGB"):
			VectorRemove(::g->possible_chunks, { "iCCP", "sRGB" });
			break;
		case STR2INT("sBIT"):
			VectorRemove(::g->possible_chunks, { "sBIT" });
			break;
		case STR2INT("gAMA"):
			VectorRemove(::g->possible_chunks, { "gAMA" });
			break;
		case STR2INT("cHRM"):
			VectorRemove(::g->possible_chunks, { "cHRM" });
			break;
		case STR2INT("PLTE"):
			::g->preferred_chunks = { "IDAT" };
			VectorRemove(::g->possible_chunks, { "PLTE", "iCCP", "sRGB", "sBIT", "gAMA", "cHRM" });
			::g->possible_chunks.insert(::g->possible_chunks.end(), { "tRNS", "hIST", "bKGD", "IDAT" });
			break;
		case STR2INT("tRNS"):
			VectorRemove(::g->possible_chunks, { "tRNS" });
			break;
		case STR2INT("hIST"):
			VectorRemove(::g->possible_chunks, { "hIST" });
			break;
		case STR2INT("bKGD"):
			VectorRemove(::g->possible_chunks, { "bKGD" });
			break;
		case STR2INT("IDAT"):
			::g->preferred_chunks = { "IEND" };
			VectorRemove(::g->possible_chunks, { "IDAT", "pHYs", "sPLT", "iCCP", "sRGB", "sBIT", "gAMA", "cHRM", "PLTE", "tRNS", "hIST", "bKGD" });
			::g->possible_chunks.insert(::g->possible_chunks.end(), { "IEND" });
			break;
		case STR2INT("IEND"):
			::g->preferred_chunks = {  };
			::g->possible_chunks = {  };
			break;
		};
	};
	if ((::g->CHUNK_CNT > 1)) {
		if ((::g->chunk()[0]->type().cname() != "IHDR")) {
			error_message("*ERROR: Chunk IHDR must be first chunk.");
		};
		if ((::g->chunk()[(::g->CHUNK_CNT - 1)]->type().cname() != "IEND")) {
			error_message("*ERROR: Chunk IEND must be last chunk.");
		};
	};

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

