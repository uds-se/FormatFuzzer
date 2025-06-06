#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"


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
	std::string& operator () () { return value; }
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



class GIFHEADER {
	std::vector<GIFHEADER*>& instances;

	std::string Signature_var;
	std::string Version_var;

public:
	bool Signature_exists = false;
	bool Version_exists = false;

	std::string& Signature() {
		assert_cond(Signature_exists, "struct field Signature does not exist");
		return Signature_var;
	}
	std::string& Version() {
		assert_cond(Version_exists, "struct field Version does not exist");
		return Version_var;
	}

	/* locals */
	int evil;

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	GIFHEADER& operator () () { return *instances.back(); }
	GIFHEADER& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	GIFHEADER(std::vector<GIFHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~GIFHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			GIFHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	GIFHEADER* generate();
};

int GIFHEADER::_parent_id = 0;
int GIFHEADER::_index_start = 0;



class ushort_class {
	int small;
	std::vector<ushort> known_values;
	ushort value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(ushort);
	ushort operator () () { return value; }
	ushort_class(int small, std::vector<ushort> known_values = {}) : small(small), known_values(known_values) {}

	ushort generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(ushort), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(ushort), 0, known_values);
		}
		return value;
	}

	ushort generate(std::vector<ushort> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(ushort), 0, possible_values);
		return value;
	}
};



class UBYTE_bitfield {
	int small;
	std::vector<UBYTE> known_values;
	UBYTE value;
public:
	UBYTE operator () () { return value; }
	UBYTE_bitfield(int small, std::vector<UBYTE> known_values = {}) : small(small), known_values(known_values) {}

	UBYTE generate(unsigned bits) {
		if (!bits)
			return 0;
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(UBYTE), bits, small);
		} else {
			value = file_acc.file_integer(sizeof(UBYTE), bits, known_values);
		}
		return value;
	}

	UBYTE generate(unsigned bits, std::vector<UBYTE> possible_values) {
		if (!bits)
			return 0;
		value = file_acc.file_integer(sizeof(UBYTE), bits, possible_values);
		return value;
	}
};



class LOGICALSCREENDESCRIPTOR_PACKEDFIELDS {
	std::vector<LOGICALSCREENDESCRIPTOR_PACKEDFIELDS*>& instances;

	UBYTE GlobalColorTableFlag_var : 1;
	UBYTE ColorResolution_var : 3;
	UBYTE SortFlag_var : 1;
	UBYTE SizeOfGlobalColorTable_var : 3;

public:
	bool GlobalColorTableFlag_exists = false;
	bool ColorResolution_exists = false;
	bool SortFlag_exists = false;
	bool SizeOfGlobalColorTable_exists = false;

	UBYTE GlobalColorTableFlag() {
		assert_cond(GlobalColorTableFlag_exists, "struct field GlobalColorTableFlag does not exist");
		return GlobalColorTableFlag_var;
	}
	UBYTE ColorResolution() {
		assert_cond(ColorResolution_exists, "struct field ColorResolution does not exist");
		return ColorResolution_var;
	}
	UBYTE SortFlag() {
		assert_cond(SortFlag_exists, "struct field SortFlag does not exist");
		return SortFlag_var;
	}
	UBYTE SizeOfGlobalColorTable() {
		assert_cond(SizeOfGlobalColorTable_exists, "struct field SizeOfGlobalColorTable does not exist");
		return SizeOfGlobalColorTable_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS& operator () () { return *instances.back(); }
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS(std::vector<LOGICALSCREENDESCRIPTOR_PACKEDFIELDS*>& instances) : instances(instances) { instances.push_back(this); }
	~LOGICALSCREENDESCRIPTOR_PACKEDFIELDS() {
		if (generated == 2)
			return;
		while (instances.size()) {
			LOGICALSCREENDESCRIPTOR_PACKEDFIELDS* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS* generate();
};

int LOGICALSCREENDESCRIPTOR_PACKEDFIELDS::_parent_id = 0;
int LOGICALSCREENDESCRIPTOR_PACKEDFIELDS::_index_start = 0;



class UBYTE_class {
	int small;
	std::vector<UBYTE> known_values;
	UBYTE value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(UBYTE);
	UBYTE operator () () { return value; }
	UBYTE_class(int small, std::vector<UBYTE> known_values = {}) : small(small), known_values(known_values) {}

	UBYTE generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(UBYTE), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(UBYTE), 0, known_values);
		}
		return value;
	}

	UBYTE generate(std::vector<UBYTE> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(UBYTE), 0, possible_values);
		return value;
	}
};



class LOGICALSCREENDESCRIPTOR {
	std::vector<LOGICALSCREENDESCRIPTOR*>& instances;

	ushort Width_var;
	ushort Height_var;
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS* PackedFields_var;
	UBYTE BackgroundColorIndex_var;
	UBYTE PixelAspectRatio_var;

public:
	bool Width_exists = false;
	bool Height_exists = false;
	bool PackedFields_exists = false;
	bool BackgroundColorIndex_exists = false;
	bool PixelAspectRatio_exists = false;

	ushort& Width() {
		assert_cond(Width_exists, "struct field Width does not exist");
		return Width_var;
	}
	ushort& Height() {
		assert_cond(Height_exists, "struct field Height does not exist");
		return Height_var;
	}
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS& PackedFields() {
		assert_cond(PackedFields_exists, "struct field PackedFields does not exist");
		return *PackedFields_var;
	}
	UBYTE& BackgroundColorIndex() {
		assert_cond(BackgroundColorIndex_exists, "struct field BackgroundColorIndex does not exist");
		return BackgroundColorIndex_var;
	}
	UBYTE& PixelAspectRatio() {
		assert_cond(PixelAspectRatio_exists, "struct field PixelAspectRatio does not exist");
		return PixelAspectRatio_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	LOGICALSCREENDESCRIPTOR& operator () () { return *instances.back(); }
	LOGICALSCREENDESCRIPTOR& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	LOGICALSCREENDESCRIPTOR(std::vector<LOGICALSCREENDESCRIPTOR*>& instances) : instances(instances) { instances.push_back(this); }
	~LOGICALSCREENDESCRIPTOR() {
		if (generated == 2)
			return;
		while (instances.size()) {
			LOGICALSCREENDESCRIPTOR* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	LOGICALSCREENDESCRIPTOR* generate();
};

int LOGICALSCREENDESCRIPTOR::_parent_id = 0;
int LOGICALSCREENDESCRIPTOR::_index_start = 0;



class RGB {
	std::vector<RGB*>& instances;

	UBYTE R_var;
	UBYTE G_var;
	UBYTE B_var;

public:
	bool R_exists = false;
	bool G_exists = false;
	bool B_exists = false;

	UBYTE& R() {
		assert_cond(R_exists, "struct field R does not exist");
		return R_var;
	}
	UBYTE& G() {
		assert_cond(G_exists, "struct field G does not exist");
		return G_var;
	}
	UBYTE& B() {
		assert_cond(B_exists, "struct field B does not exist");
		return B_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	RGB& operator () () { return *instances.back(); }
	RGB& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	RGB(std::vector<RGB*>& instances) : instances(instances) { instances.push_back(this); }
	~RGB() {
		if (generated == 2)
			return;
		while (instances.size()) {
			RGB* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	RGB* generate();
};

int RGB::_parent_id = 0;
int RGB::_index_start = 0;



class RGB_array_class {
	RGB& element;
	std::vector<RGB*> value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::vector<RGB*>& operator () () { return value; }
	RGB operator [] (int index) {
		assert_cond((unsigned)index < value.size(), "array index out of bounds");
		return *value[index];
	}
	RGB_array_class(RGB& element) : element(element) {}

	std::vector<RGB*> generate(unsigned size) {
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



class GLOBALCOLORTABLE {
	std::vector<GLOBALCOLORTABLE*>& instances;

	std::vector<RGB*> rgb_var;

public:
	bool rgb_exists = false;

	std::vector<RGB*>& rgb() {
		assert_cond(rgb_exists, "struct field rgb does not exist");
		return rgb_var;
	}

	/* locals */
	int i;
	int size;

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	GLOBALCOLORTABLE& operator () () { return *instances.back(); }
	GLOBALCOLORTABLE& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	GLOBALCOLORTABLE(std::vector<GLOBALCOLORTABLE*>& instances) : instances(instances) { instances.push_back(this); }
	~GLOBALCOLORTABLE() {
		if (generated == 2)
			return;
		while (instances.size()) {
			GLOBALCOLORTABLE* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	GLOBALCOLORTABLE* generate();
};

int GLOBALCOLORTABLE::_parent_id = 0;
int GLOBALCOLORTABLE::_index_start = 0;



class IMAGEDESCRIPTOR_PACKEDFIELDS {
	std::vector<IMAGEDESCRIPTOR_PACKEDFIELDS*>& instances;

	UBYTE LocalColorTableFlag_var : 1;
	UBYTE InterlaceFlag_var : 1;
	UBYTE SortFlag_var : 1;
	UBYTE Reserved_var : 2;
	UBYTE SizeOfLocalColorTable_var : 3;

public:
	bool LocalColorTableFlag_exists = false;
	bool InterlaceFlag_exists = false;
	bool SortFlag_exists = false;
	bool Reserved_exists = false;
	bool SizeOfLocalColorTable_exists = false;

	UBYTE LocalColorTableFlag() {
		assert_cond(LocalColorTableFlag_exists, "struct field LocalColorTableFlag does not exist");
		return LocalColorTableFlag_var;
	}
	UBYTE InterlaceFlag() {
		assert_cond(InterlaceFlag_exists, "struct field InterlaceFlag does not exist");
		return InterlaceFlag_var;
	}
	UBYTE SortFlag() {
		assert_cond(SortFlag_exists, "struct field SortFlag does not exist");
		return SortFlag_var;
	}
	UBYTE Reserved() {
		assert_cond(Reserved_exists, "struct field Reserved does not exist");
		return Reserved_var;
	}
	UBYTE SizeOfLocalColorTable() {
		assert_cond(SizeOfLocalColorTable_exists, "struct field SizeOfLocalColorTable does not exist");
		return SizeOfLocalColorTable_var;
	}

	/* locals */
	std::vector<UBYTE> possible_values;

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	IMAGEDESCRIPTOR_PACKEDFIELDS& operator () () { return *instances.back(); }
	IMAGEDESCRIPTOR_PACKEDFIELDS& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	IMAGEDESCRIPTOR_PACKEDFIELDS(std::vector<IMAGEDESCRIPTOR_PACKEDFIELDS*>& instances) : instances(instances) { instances.push_back(this); }
	~IMAGEDESCRIPTOR_PACKEDFIELDS() {
		if (generated == 2)
			return;
		while (instances.size()) {
			IMAGEDESCRIPTOR_PACKEDFIELDS* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	IMAGEDESCRIPTOR_PACKEDFIELDS* generate();
};

int IMAGEDESCRIPTOR_PACKEDFIELDS::_parent_id = 0;
int IMAGEDESCRIPTOR_PACKEDFIELDS::_index_start = 0;



class IMAGEDESCRIPTOR {
	std::vector<IMAGEDESCRIPTOR*>& instances;

	UBYTE ImageSeperator_var;
	ushort ImageLeftPosition_var;
	ushort ImageTopPosition_var;
	ushort ImageWidth_var;
	ushort ImageHeight_var;
	IMAGEDESCRIPTOR_PACKEDFIELDS* PackedFields_var;

public:
	bool ImageSeperator_exists = false;
	bool ImageLeftPosition_exists = false;
	bool ImageTopPosition_exists = false;
	bool ImageWidth_exists = false;
	bool ImageHeight_exists = false;
	bool PackedFields_exists = false;

	UBYTE& ImageSeperator() {
		assert_cond(ImageSeperator_exists, "struct field ImageSeperator does not exist");
		return ImageSeperator_var;
	}
	ushort& ImageLeftPosition() {
		assert_cond(ImageLeftPosition_exists, "struct field ImageLeftPosition does not exist");
		return ImageLeftPosition_var;
	}
	ushort& ImageTopPosition() {
		assert_cond(ImageTopPosition_exists, "struct field ImageTopPosition does not exist");
		return ImageTopPosition_var;
	}
	ushort& ImageWidth() {
		assert_cond(ImageWidth_exists, "struct field ImageWidth does not exist");
		return ImageWidth_var;
	}
	ushort& ImageHeight() {
		assert_cond(ImageHeight_exists, "struct field ImageHeight does not exist");
		return ImageHeight_var;
	}
	IMAGEDESCRIPTOR_PACKEDFIELDS& PackedFields() {
		assert_cond(PackedFields_exists, "struct field PackedFields does not exist");
		return *PackedFields_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	IMAGEDESCRIPTOR& operator () () { return *instances.back(); }
	IMAGEDESCRIPTOR& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	IMAGEDESCRIPTOR(std::vector<IMAGEDESCRIPTOR*>& instances) : instances(instances) { instances.push_back(this); }
	~IMAGEDESCRIPTOR() {
		if (generated == 2)
			return;
		while (instances.size()) {
			IMAGEDESCRIPTOR* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	IMAGEDESCRIPTOR* generate();
};

int IMAGEDESCRIPTOR::_parent_id = 0;
int IMAGEDESCRIPTOR::_index_start = 0;



class LOCALCOLORTABLE {
	std::vector<LOCALCOLORTABLE*>& instances;

	std::vector<RGB*> rgb_var;

public:
	bool rgb_exists = false;

	std::vector<RGB*>& rgb() {
		assert_cond(rgb_exists, "struct field rgb does not exist");
		return rgb_var;
	}

	/* locals */
	int i;
	int size;

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	LOCALCOLORTABLE& operator () () { return *instances.back(); }
	LOCALCOLORTABLE& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	LOCALCOLORTABLE(std::vector<LOCALCOLORTABLE*>& instances) : instances(instances) { instances.push_back(this); }
	~LOCALCOLORTABLE() {
		if (generated == 2)
			return;
		while (instances.size()) {
			LOCALCOLORTABLE* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	LOCALCOLORTABLE* generate();
};

int LOCALCOLORTABLE::_parent_id = 0;
int LOCALCOLORTABLE::_index_start = 0;



class DATASUBBLOCK {
	std::vector<DATASUBBLOCK*>& instances;

	UBYTE Size_var;
	std::string Data_var;

public:
	bool Size_exists = false;
	bool Data_exists = false;

	UBYTE& Size() {
		assert_cond(Size_exists, "struct field Size does not exist");
		return Size_var;
	}
	std::string& Data() {
		assert_cond(Data_exists, "struct field Data does not exist");
		return Data_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	DATASUBBLOCK& operator () () { return *instances.back(); }
	DATASUBBLOCK& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	DATASUBBLOCK(std::vector<DATASUBBLOCK*>& instances) : instances(instances) { instances.push_back(this); }
	~DATASUBBLOCK() {
		if (generated == 2)
			return;
		while (instances.size()) {
			DATASUBBLOCK* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	DATASUBBLOCK* generate(UBYTE& size);
};

int DATASUBBLOCK::_parent_id = 0;
int DATASUBBLOCK::_index_start = 0;



class DATASUBBLOCKS {
	std::vector<DATASUBBLOCKS*>& instances;

	DATASUBBLOCK* DataSubBlock_var;
	UBYTE BlockTerminator_var;

public:
	bool DataSubBlock_exists = false;
	bool BlockTerminator_exists = false;

	DATASUBBLOCK& DataSubBlock() {
		assert_cond(DataSubBlock_exists, "struct field DataSubBlock does not exist");
		return *DataSubBlock_var;
	}
	UBYTE& BlockTerminator() {
		assert_cond(BlockTerminator_exists, "struct field BlockTerminator does not exist");
		return BlockTerminator_var;
	}

	/* locals */
	std::vector<UBYTE> values;
	int count;
	UBYTE size;

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	DATASUBBLOCKS& operator () () { return *instances.back(); }
	DATASUBBLOCKS& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	DATASUBBLOCKS(std::vector<DATASUBBLOCKS*>& instances) : instances(instances) { instances.push_back(this); }
	~DATASUBBLOCKS() {
		if (generated == 2)
			return;
		while (instances.size()) {
			DATASUBBLOCKS* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	DATASUBBLOCKS* generate();
};

int DATASUBBLOCKS::_parent_id = 0;
int DATASUBBLOCKS::_index_start = 0;



class IMAGEDATA {
	std::vector<IMAGEDATA*>& instances;

	UBYTE LZWMinimumCodeSize_var;
	DATASUBBLOCKS* DataSubBlocks_var;

public:
	bool LZWMinimumCodeSize_exists = false;
	bool DataSubBlocks_exists = false;

	UBYTE& LZWMinimumCodeSize() {
		assert_cond(LZWMinimumCodeSize_exists, "struct field LZWMinimumCodeSize does not exist");
		return LZWMinimumCodeSize_var;
	}
	DATASUBBLOCKS& DataSubBlocks() {
		assert_cond(DataSubBlocks_exists, "struct field DataSubBlocks does not exist");
		return *DataSubBlocks_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	IMAGEDATA& operator () () { return *instances.back(); }
	IMAGEDATA& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	IMAGEDATA(std::vector<IMAGEDATA*>& instances) : instances(instances) { instances.push_back(this); }
	~IMAGEDATA() {
		if (generated == 2)
			return;
		while (instances.size()) {
			IMAGEDATA* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	IMAGEDATA* generate();
};

int IMAGEDATA::_parent_id = 0;
int IMAGEDATA::_index_start = 0;



class GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS {
	std::vector<GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS*>& instances;

	UBYTE Reserved_var : 3;
	UBYTE DisposalMethod_var : 3;
	UBYTE UserInputFlag_var : 1;
	UBYTE TransparentColorFlag_var : 1;

public:
	bool Reserved_exists = false;
	bool DisposalMethod_exists = false;
	bool UserInputFlag_exists = false;
	bool TransparentColorFlag_exists = false;

	UBYTE Reserved() {
		assert_cond(Reserved_exists, "struct field Reserved does not exist");
		return Reserved_var;
	}
	UBYTE DisposalMethod() {
		assert_cond(DisposalMethod_exists, "struct field DisposalMethod does not exist");
		return DisposalMethod_var;
	}
	UBYTE UserInputFlag() {
		assert_cond(UserInputFlag_exists, "struct field UserInputFlag does not exist");
		return UserInputFlag_var;
	}
	UBYTE TransparentColorFlag() {
		assert_cond(TransparentColorFlag_exists, "struct field TransparentColorFlag does not exist");
		return TransparentColorFlag_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS& operator () () { return *instances.back(); }
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS(std::vector<GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS*>& instances) : instances(instances) { instances.push_back(this); }
	~GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS() {
		if (generated == 2)
			return;
		while (instances.size()) {
			GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS* generate();
};

int GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS::_parent_id = 0;
int GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS::_index_start = 0;



class GRAPHICCONTROLSUBBLOCK {
	std::vector<GRAPHICCONTROLSUBBLOCK*>& instances;

	UBYTE BlockSize_var;
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS* PackedFields_var;
	ushort DelayTime_var;
	UBYTE TransparentColorIndex_var;

public:
	bool BlockSize_exists = false;
	bool PackedFields_exists = false;
	bool DelayTime_exists = false;
	bool TransparentColorIndex_exists = false;

	UBYTE& BlockSize() {
		assert_cond(BlockSize_exists, "struct field BlockSize does not exist");
		return BlockSize_var;
	}
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS& PackedFields() {
		assert_cond(PackedFields_exists, "struct field PackedFields does not exist");
		return *PackedFields_var;
	}
	ushort& DelayTime() {
		assert_cond(DelayTime_exists, "struct field DelayTime does not exist");
		return DelayTime_var;
	}
	UBYTE& TransparentColorIndex() {
		assert_cond(TransparentColorIndex_exists, "struct field TransparentColorIndex does not exist");
		return TransparentColorIndex_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	GRAPHICCONTROLSUBBLOCK& operator () () { return *instances.back(); }
	GRAPHICCONTROLSUBBLOCK& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	GRAPHICCONTROLSUBBLOCK(std::vector<GRAPHICCONTROLSUBBLOCK*>& instances) : instances(instances) { instances.push_back(this); }
	~GRAPHICCONTROLSUBBLOCK() {
		if (generated == 2)
			return;
		while (instances.size()) {
			GRAPHICCONTROLSUBBLOCK* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	GRAPHICCONTROLSUBBLOCK* generate();
};

int GRAPHICCONTROLSUBBLOCK::_parent_id = 0;
int GRAPHICCONTROLSUBBLOCK::_index_start = 0;



class GRAPHICCONTROLEXTENSION {
	std::vector<GRAPHICCONTROLEXTENSION*>& instances;

	UBYTE ExtensionIntroducer_var;
	UBYTE GraphicControlLabel_var;
	GRAPHICCONTROLSUBBLOCK* GraphicControlSubBlock_var;
	UBYTE BlockTerminator_var;

public:
	bool ExtensionIntroducer_exists = false;
	bool GraphicControlLabel_exists = false;
	bool GraphicControlSubBlock_exists = false;
	bool BlockTerminator_exists = false;

	UBYTE& ExtensionIntroducer() {
		assert_cond(ExtensionIntroducer_exists, "struct field ExtensionIntroducer does not exist");
		return ExtensionIntroducer_var;
	}
	UBYTE& GraphicControlLabel() {
		assert_cond(GraphicControlLabel_exists, "struct field GraphicControlLabel does not exist");
		return GraphicControlLabel_var;
	}
	GRAPHICCONTROLSUBBLOCK& GraphicControlSubBlock() {
		assert_cond(GraphicControlSubBlock_exists, "struct field GraphicControlSubBlock does not exist");
		return *GraphicControlSubBlock_var;
	}
	UBYTE& BlockTerminator() {
		assert_cond(BlockTerminator_exists, "struct field BlockTerminator does not exist");
		return BlockTerminator_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	GRAPHICCONTROLEXTENSION& operator () () { return *instances.back(); }
	GRAPHICCONTROLEXTENSION& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	GRAPHICCONTROLEXTENSION(std::vector<GRAPHICCONTROLEXTENSION*>& instances) : instances(instances) { instances.push_back(this); }
	~GRAPHICCONTROLEXTENSION() {
		if (generated == 2)
			return;
		while (instances.size()) {
			GRAPHICCONTROLEXTENSION* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	GRAPHICCONTROLEXTENSION* generate();
};

int GRAPHICCONTROLEXTENSION::_parent_id = 0;
int GRAPHICCONTROLEXTENSION::_index_start = 0;



class COMMENTEXTENSION {
	std::vector<COMMENTEXTENSION*>& instances;

	UBYTE ExtensionIntroducer_var;
	UBYTE CommentLabel_var;
	DATASUBBLOCKS* CommentData_var;

public:
	bool ExtensionIntroducer_exists = false;
	bool CommentLabel_exists = false;
	bool CommentData_exists = false;

	UBYTE& ExtensionIntroducer() {
		assert_cond(ExtensionIntroducer_exists, "struct field ExtensionIntroducer does not exist");
		return ExtensionIntroducer_var;
	}
	UBYTE& CommentLabel() {
		assert_cond(CommentLabel_exists, "struct field CommentLabel does not exist");
		return CommentLabel_var;
	}
	DATASUBBLOCKS& CommentData() {
		assert_cond(CommentData_exists, "struct field CommentData does not exist");
		return *CommentData_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	COMMENTEXTENSION& operator () () { return *instances.back(); }
	COMMENTEXTENSION& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	COMMENTEXTENSION(std::vector<COMMENTEXTENSION*>& instances) : instances(instances) { instances.push_back(this); }
	~COMMENTEXTENSION() {
		if (generated == 2)
			return;
		while (instances.size()) {
			COMMENTEXTENSION* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	COMMENTEXTENSION* generate();
};

int COMMENTEXTENSION::_parent_id = 0;
int COMMENTEXTENSION::_index_start = 0;



class PLAINTEXTSUBBLOCK {
	std::vector<PLAINTEXTSUBBLOCK*>& instances;

	UBYTE BlockSize_var;
	ushort TextGridLeftPosition_var;
	ushort TextGridTopPosition_var;
	ushort TextGridWidth_var;
	ushort TextGridHeight_var;
	UBYTE CharacterCellWidth_var;
	UBYTE CharacterCellHeight_var;
	UBYTE TextForegroundColorIndex_var;
	UBYTE TextBackgroundColorIndex_var;

public:
	bool BlockSize_exists = false;
	bool TextGridLeftPosition_exists = false;
	bool TextGridTopPosition_exists = false;
	bool TextGridWidth_exists = false;
	bool TextGridHeight_exists = false;
	bool CharacterCellWidth_exists = false;
	bool CharacterCellHeight_exists = false;
	bool TextForegroundColorIndex_exists = false;
	bool TextBackgroundColorIndex_exists = false;

	UBYTE& BlockSize() {
		assert_cond(BlockSize_exists, "struct field BlockSize does not exist");
		return BlockSize_var;
	}
	ushort& TextGridLeftPosition() {
		assert_cond(TextGridLeftPosition_exists, "struct field TextGridLeftPosition does not exist");
		return TextGridLeftPosition_var;
	}
	ushort& TextGridTopPosition() {
		assert_cond(TextGridTopPosition_exists, "struct field TextGridTopPosition does not exist");
		return TextGridTopPosition_var;
	}
	ushort& TextGridWidth() {
		assert_cond(TextGridWidth_exists, "struct field TextGridWidth does not exist");
		return TextGridWidth_var;
	}
	ushort& TextGridHeight() {
		assert_cond(TextGridHeight_exists, "struct field TextGridHeight does not exist");
		return TextGridHeight_var;
	}
	UBYTE& CharacterCellWidth() {
		assert_cond(CharacterCellWidth_exists, "struct field CharacterCellWidth does not exist");
		return CharacterCellWidth_var;
	}
	UBYTE& CharacterCellHeight() {
		assert_cond(CharacterCellHeight_exists, "struct field CharacterCellHeight does not exist");
		return CharacterCellHeight_var;
	}
	UBYTE& TextForegroundColorIndex() {
		assert_cond(TextForegroundColorIndex_exists, "struct field TextForegroundColorIndex does not exist");
		return TextForegroundColorIndex_var;
	}
	UBYTE& TextBackgroundColorIndex() {
		assert_cond(TextBackgroundColorIndex_exists, "struct field TextBackgroundColorIndex does not exist");
		return TextBackgroundColorIndex_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PLAINTEXTSUBBLOCK& operator () () { return *instances.back(); }
	PLAINTEXTSUBBLOCK& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	PLAINTEXTSUBBLOCK(std::vector<PLAINTEXTSUBBLOCK*>& instances) : instances(instances) { instances.push_back(this); }
	~PLAINTEXTSUBBLOCK() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PLAINTEXTSUBBLOCK* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PLAINTEXTSUBBLOCK* generate();
};

int PLAINTEXTSUBBLOCK::_parent_id = 0;
int PLAINTEXTSUBBLOCK::_index_start = 0;



class PLAINTEXTEXTENTION {
	std::vector<PLAINTEXTEXTENTION*>& instances;

	UBYTE ExtensionIntroducer_var;
	UBYTE PlainTextLabel_var;
	PLAINTEXTSUBBLOCK* PlainTextSubBlock_var;
	DATASUBBLOCKS* PlainTextData_var;

public:
	bool ExtensionIntroducer_exists = false;
	bool PlainTextLabel_exists = false;
	bool PlainTextSubBlock_exists = false;
	bool PlainTextData_exists = false;

	UBYTE& ExtensionIntroducer() {
		assert_cond(ExtensionIntroducer_exists, "struct field ExtensionIntroducer does not exist");
		return ExtensionIntroducer_var;
	}
	UBYTE& PlainTextLabel() {
		assert_cond(PlainTextLabel_exists, "struct field PlainTextLabel does not exist");
		return PlainTextLabel_var;
	}
	PLAINTEXTSUBBLOCK& PlainTextSubBlock() {
		assert_cond(PlainTextSubBlock_exists, "struct field PlainTextSubBlock does not exist");
		return *PlainTextSubBlock_var;
	}
	DATASUBBLOCKS& PlainTextData() {
		assert_cond(PlainTextData_exists, "struct field PlainTextData does not exist");
		return *PlainTextData_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PLAINTEXTEXTENTION& operator () () { return *instances.back(); }
	PLAINTEXTEXTENTION& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	PLAINTEXTEXTENTION(std::vector<PLAINTEXTEXTENTION*>& instances) : instances(instances) { instances.push_back(this); }
	~PLAINTEXTEXTENTION() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PLAINTEXTEXTENTION* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PLAINTEXTEXTENTION* generate();
};

int PLAINTEXTEXTENTION::_parent_id = 0;
int PLAINTEXTEXTENTION::_index_start = 0;



class APPLICATIONSUBBLOCK {
	std::vector<APPLICATIONSUBBLOCK*>& instances;

	UBYTE BlockSize_var;
	std::string ApplicationIdentifier_var;
	std::string ApplicationAuthenticationCode_var;

public:
	bool BlockSize_exists = false;
	bool ApplicationIdentifier_exists = false;
	bool ApplicationAuthenticationCode_exists = false;

	UBYTE& BlockSize() {
		assert_cond(BlockSize_exists, "struct field BlockSize does not exist");
		return BlockSize_var;
	}
	std::string& ApplicationIdentifier() {
		assert_cond(ApplicationIdentifier_exists, "struct field ApplicationIdentifier does not exist");
		return ApplicationIdentifier_var;
	}
	std::string& ApplicationAuthenticationCode() {
		assert_cond(ApplicationAuthenticationCode_exists, "struct field ApplicationAuthenticationCode does not exist");
		return ApplicationAuthenticationCode_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	APPLICATIONSUBBLOCK& operator () () { return *instances.back(); }
	APPLICATIONSUBBLOCK& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	APPLICATIONSUBBLOCK(std::vector<APPLICATIONSUBBLOCK*>& instances) : instances(instances) { instances.push_back(this); }
	~APPLICATIONSUBBLOCK() {
		if (generated == 2)
			return;
		while (instances.size()) {
			APPLICATIONSUBBLOCK* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	APPLICATIONSUBBLOCK* generate();
};

int APPLICATIONSUBBLOCK::_parent_id = 0;
int APPLICATIONSUBBLOCK::_index_start = 0;



class APPLICATIONEXTENTION {
	std::vector<APPLICATIONEXTENTION*>& instances;

	UBYTE ExtensionIntroducer_var;
	UBYTE ApplicationLabel_var;
	APPLICATIONSUBBLOCK* ApplicationSubBlock_var;
	DATASUBBLOCKS* ApplicationData_var;

public:
	bool ExtensionIntroducer_exists = false;
	bool ApplicationLabel_exists = false;
	bool ApplicationSubBlock_exists = false;
	bool ApplicationData_exists = false;

	UBYTE& ExtensionIntroducer() {
		assert_cond(ExtensionIntroducer_exists, "struct field ExtensionIntroducer does not exist");
		return ExtensionIntroducer_var;
	}
	UBYTE& ApplicationLabel() {
		assert_cond(ApplicationLabel_exists, "struct field ApplicationLabel does not exist");
		return ApplicationLabel_var;
	}
	APPLICATIONSUBBLOCK& ApplicationSubBlock() {
		assert_cond(ApplicationSubBlock_exists, "struct field ApplicationSubBlock does not exist");
		return *ApplicationSubBlock_var;
	}
	DATASUBBLOCKS& ApplicationData() {
		assert_cond(ApplicationData_exists, "struct field ApplicationData does not exist");
		return *ApplicationData_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	APPLICATIONEXTENTION& operator () () { return *instances.back(); }
	APPLICATIONEXTENTION& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	APPLICATIONEXTENTION(std::vector<APPLICATIONEXTENTION*>& instances) : instances(instances) { instances.push_back(this); }
	~APPLICATIONEXTENTION() {
		if (generated == 2)
			return;
		while (instances.size()) {
			APPLICATIONEXTENTION* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	APPLICATIONEXTENTION* generate();
};

int APPLICATIONEXTENTION::_parent_id = 0;
int APPLICATIONEXTENTION::_index_start = 0;



class UNDEFINEDDATA {
	std::vector<UNDEFINEDDATA*>& instances;

	UBYTE ExtensionIntroducer_var;
	UBYTE Label_var;
	DATASUBBLOCKS* DataSubBlocks_var;

public:
	bool ExtensionIntroducer_exists = false;
	bool Label_exists = false;
	bool DataSubBlocks_exists = false;

	UBYTE& ExtensionIntroducer() {
		assert_cond(ExtensionIntroducer_exists, "struct field ExtensionIntroducer does not exist");
		return ExtensionIntroducer_var;
	}
	UBYTE& Label() {
		assert_cond(Label_exists, "struct field Label does not exist");
		return Label_var;
	}
	DATASUBBLOCKS& DataSubBlocks() {
		assert_cond(DataSubBlocks_exists, "struct field DataSubBlocks does not exist");
		return *DataSubBlocks_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	UNDEFINEDDATA& operator () () { return *instances.back(); }
	UNDEFINEDDATA& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	UNDEFINEDDATA(std::vector<UNDEFINEDDATA*>& instances) : instances(instances) { instances.push_back(this); }
	~UNDEFINEDDATA() {
		if (generated == 2)
			return;
		while (instances.size()) {
			UNDEFINEDDATA* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	UNDEFINEDDATA* generate();
};

int UNDEFINEDDATA::_parent_id = 0;
int UNDEFINEDDATA::_index_start = 0;



class DATA {
	std::vector<DATA*>& instances;

	IMAGEDESCRIPTOR* ImageDescriptor_var;
	LOCALCOLORTABLE* LocalColorTable_var;
	IMAGEDATA* ImageData_var;
	GRAPHICCONTROLEXTENSION* GraphicControlExtension_var;
	COMMENTEXTENSION* CommentExtension_var;
	PLAINTEXTEXTENTION* PlainTextExtension_var;
	APPLICATIONEXTENTION* ApplicationExtension_var;
	UNDEFINEDDATA* UndefinedData_var;

public:
	bool ImageDescriptor_exists = false;
	bool LocalColorTable_exists = false;
	bool ImageData_exists = false;
	bool GraphicControlExtension_exists = false;
	bool CommentExtension_exists = false;
	bool PlainTextExtension_exists = false;
	bool ApplicationExtension_exists = false;
	bool UndefinedData_exists = false;

	IMAGEDESCRIPTOR& ImageDescriptor() {
		assert_cond(ImageDescriptor_exists, "struct field ImageDescriptor does not exist");
		return *ImageDescriptor_var;
	}
	LOCALCOLORTABLE& LocalColorTable() {
		assert_cond(LocalColorTable_exists, "struct field LocalColorTable does not exist");
		return *LocalColorTable_var;
	}
	IMAGEDATA& ImageData() {
		assert_cond(ImageData_exists, "struct field ImageData does not exist");
		return *ImageData_var;
	}
	GRAPHICCONTROLEXTENSION& GraphicControlExtension() {
		assert_cond(GraphicControlExtension_exists, "struct field GraphicControlExtension does not exist");
		return *GraphicControlExtension_var;
	}
	COMMENTEXTENSION& CommentExtension() {
		assert_cond(CommentExtension_exists, "struct field CommentExtension does not exist");
		return *CommentExtension_var;
	}
	PLAINTEXTEXTENTION& PlainTextExtension() {
		assert_cond(PlainTextExtension_exists, "struct field PlainTextExtension does not exist");
		return *PlainTextExtension_var;
	}
	APPLICATIONEXTENTION& ApplicationExtension() {
		assert_cond(ApplicationExtension_exists, "struct field ApplicationExtension does not exist");
		return *ApplicationExtension_var;
	}
	UNDEFINEDDATA& UndefinedData() {
		assert_cond(UndefinedData_exists, "struct field UndefinedData does not exist");
		return *UndefinedData_var;
	}

	/* locals */
	std::vector<UBYTE> possible;
	int has_data;

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	DATA& operator () () { return *instances.back(); }
	DATA& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	DATA(std::vector<DATA*>& instances) : instances(instances) { instances.push_back(this); }
	~DATA() {
		if (generated == 2)
			return;
		while (instances.size()) {
			DATA* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	DATA* generate();
};

int DATA::_parent_id = 0;
int DATA::_index_start = 0;



class TRAILER {
	std::vector<TRAILER*>& instances;

	UBYTE GIFTrailer_var;

public:
	bool GIFTrailer_exists = false;

	UBYTE& GIFTrailer() {
		assert_cond(GIFTrailer_exists, "struct field GIFTrailer does not exist");
		return GIFTrailer_var;
	}

	unsigned char generated = 0;
	static int _parent_id;
	static int _index_start;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	TRAILER& operator () () { return *instances.back(); }
	TRAILER& operator [] (int index) {
		assert_cond((unsigned)(_index_start + index) < instances.size(), "instance index out of bounds");
		return *instances[_index_start + index];
	}
	std::size_t array_size() {
		return instances.size() - _index_start;
	}
	TRAILER(std::vector<TRAILER*>& instances) : instances(instances) { instances.push_back(this); }
	~TRAILER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			TRAILER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	TRAILER* generate();
};

int TRAILER::_parent_id = 0;
int TRAILER::_index_start = 0;

std::vector<byte> ReadByteInitValues;
std::vector<ubyte> ReadUByteInitValues = {  };
std::vector<short> ReadShortInitValues;
std::vector<ushort> ReadUShortInitValues = { 0xF921, 0xFE21, 0x0121, 0xFF21 };
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


std::vector<GIFHEADER*> GIFHEADER_GifHeader_instances;
std::vector<LOGICALSCREENDESCRIPTOR_PACKEDFIELDS*> LOGICALSCREENDESCRIPTOR_PACKEDFIELDS_PackedFields_instances;
std::vector<LOGICALSCREENDESCRIPTOR*> LOGICALSCREENDESCRIPTOR_LogicalScreenDescriptor_instances;
std::vector<RGB*> RGB_rgb_element_instances;
std::vector<GLOBALCOLORTABLE*> GLOBALCOLORTABLE_GlobalColorTable_instances;
std::vector<IMAGEDESCRIPTOR_PACKEDFIELDS*> IMAGEDESCRIPTOR_PACKEDFIELDS_PackedFields__instances;
std::vector<IMAGEDESCRIPTOR*> IMAGEDESCRIPTOR_ImageDescriptor_instances;
std::vector<LOCALCOLORTABLE*> LOCALCOLORTABLE_LocalColorTable_instances;
std::vector<DATASUBBLOCK*> DATASUBBLOCK_DataSubBlock_instances;
std::vector<DATASUBBLOCKS*> DATASUBBLOCKS_DataSubBlocks_instances;
std::vector<IMAGEDATA*> IMAGEDATA_ImageData_instances;
std::vector<GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS*> GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS_PackedFields___instances;
std::vector<GRAPHICCONTROLSUBBLOCK*> GRAPHICCONTROLSUBBLOCK_GraphicControlSubBlock_instances;
std::vector<GRAPHICCONTROLEXTENSION*> GRAPHICCONTROLEXTENSION_GraphicControlExtension_instances;
std::vector<DATASUBBLOCKS*> DATASUBBLOCKS_CommentData_instances;
std::vector<COMMENTEXTENSION*> COMMENTEXTENSION_CommentExtension_instances;
std::vector<PLAINTEXTSUBBLOCK*> PLAINTEXTSUBBLOCK_PlainTextSubBlock_instances;
std::vector<DATASUBBLOCKS*> DATASUBBLOCKS_PlainTextData_instances;
std::vector<PLAINTEXTEXTENTION*> PLAINTEXTEXTENTION_PlainTextExtension_instances;
std::vector<APPLICATIONSUBBLOCK*> APPLICATIONSUBBLOCK_ApplicationSubBlock_instances;
std::vector<DATASUBBLOCKS*> DATASUBBLOCKS_ApplicationData_instances;
std::vector<APPLICATIONEXTENTION*> APPLICATIONEXTENTION_ApplicationExtension_instances;
std::vector<UNDEFINEDDATA*> UNDEFINEDDATA_UndefinedData_instances;
std::vector<DATA*> DATA_Data__instances;
std::vector<TRAILER*> TRAILER_Trailer_instances;


std::unordered_map<std::string, std::string> variable_types = { { "Signature", "char_array_class" }, { "Version", "char_array_class" }, { "GifHeader", "GIFHEADER" }, { "Width", "ushort_class" }, { "Height", "ushort_class" }, { "GlobalColorTableFlag", "UBYTE_bitfield" }, { "ColorResolution", "UBYTE_bitfield" }, { "SortFlag", "UBYTE_bitfield" }, { "SizeOfGlobalColorTable", "UBYTE_bitfield" }, { "PackedFields", "LOGICALSCREENDESCRIPTOR_PACKEDFIELDS" }, { "BackgroundColorIndex", "UBYTE_class" }, { "PixelAspectRatio", "UBYTE_class" }, { "LogicalScreenDescriptor", "LOGICALSCREENDESCRIPTOR" }, { "R", "UBYTE_class" }, { "G", "UBYTE_class" }, { "B", "UBYTE_class" }, { "rgb", "RGB_array_class" }, { "GlobalColorTable", "GLOBALCOLORTABLE" }, { "ImageSeperator", "UBYTE_class" }, { "ImageLeftPosition", "ushort_class" }, { "ImageTopPosition", "ushort_class" }, { "ImageWidth", "ushort_class" }, { "ImageHeight", "ushort_class" }, { "LocalColorTableFlag", "UBYTE_bitfield" }, { "InterlaceFlag", "UBYTE_bitfield" }, { "Reserved", "UBYTE_bitfield" }, { "SizeOfLocalColorTable", "UBYTE_bitfield" }, { "PackedFields_", "IMAGEDESCRIPTOR_PACKEDFIELDS" }, { "ImageDescriptor", "IMAGEDESCRIPTOR" }, { "LocalColorTable", "LOCALCOLORTABLE" }, { "LZWMinimumCodeSize", "UBYTE_class" }, { "Size", "UBYTE_class" }, { "Data", "char_array_class" }, { "DataSubBlock", "DATASUBBLOCK" }, { "BlockTerminator", "UBYTE_class" }, { "DataSubBlocks", "DATASUBBLOCKS" }, { "ImageData", "IMAGEDATA" }, { "ExtensionIntroducer", "UBYTE_class" }, { "GraphicControlLabel", "UBYTE_class" }, { "BlockSize", "UBYTE_class" }, { "DisposalMethod", "UBYTE_bitfield" }, { "UserInputFlag", "UBYTE_bitfield" }, { "TransparentColorFlag", "UBYTE_bitfield" }, { "PackedFields__", "GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS" }, { "DelayTime", "ushort_class" }, { "TransparentColorIndex", "UBYTE_class" }, { "GraphicControlSubBlock", "GRAPHICCONTROLSUBBLOCK" }, { "GraphicControlExtension", "GRAPHICCONTROLEXTENSION" }, { "CommentLabel", "UBYTE_class" }, { "CommentData", "DATASUBBLOCKS" }, { "CommentExtension", "COMMENTEXTENSION" }, { "PlainTextLabel", "UBYTE_class" }, { "TextGridLeftPosition", "ushort_class" }, { "TextGridTopPosition", "ushort_class" }, { "TextGridWidth", "ushort_class" }, { "TextGridHeight", "ushort_class" }, { "CharacterCellWidth", "UBYTE_class" }, { "CharacterCellHeight", "UBYTE_class" }, { "TextForegroundColorIndex", "UBYTE_class" }, { "TextBackgroundColorIndex", "UBYTE_class" }, { "PlainTextSubBlock", "PLAINTEXTSUBBLOCK" }, { "PlainTextData", "DATASUBBLOCKS" }, { "PlainTextExtension", "PLAINTEXTEXTENTION" }, { "ApplicationLabel", "UBYTE_class" }, { "ApplicationIdentifier", "char_array_class" }, { "ApplicationAuthenticationCode", "char_array_class" }, { "ApplicationSubBlock", "APPLICATIONSUBBLOCK" }, { "ApplicationData", "DATASUBBLOCKS" }, { "ApplicationExtension", "APPLICATIONEXTENTION" }, { "Label", "UBYTE_class" }, { "UndefinedData", "UNDEFINEDDATA" }, { "Data_", "DATA" }, { "GIFTrailer", "UBYTE_class" }, { "Trailer", "TRAILER" } };

std::vector<std::vector<int>> integer_ranges = { { 1, 16 } };

class globals_class {
public:
	int _struct_id = 0;
	int _struct_id_counter = 0;
	char_class Signature_element;
	char_array_class Signature;
	char_class Version_element;
	char_array_class Version;
	GIFHEADER GifHeader;
	ushort_class Width;
	ushort_class Height;
	UBYTE_bitfield GlobalColorTableFlag;
	UBYTE_bitfield ColorResolution;
	UBYTE_bitfield SortFlag;
	UBYTE_bitfield SizeOfGlobalColorTable;
	LOGICALSCREENDESCRIPTOR_PACKEDFIELDS PackedFields;
	UBYTE_class BackgroundColorIndex;
	UBYTE_class PixelAspectRatio;
	LOGICALSCREENDESCRIPTOR LogicalScreenDescriptor;
	UBYTE_class R;
	UBYTE_class G;
	UBYTE_class B;
	RGB rgb_element;
	RGB_array_class rgb;
	GLOBALCOLORTABLE GlobalColorTable;
	UBYTE_class ImageSeperator;
	ushort_class ImageLeftPosition;
	ushort_class ImageTopPosition;
	ushort_class ImageWidth;
	ushort_class ImageHeight;
	UBYTE_bitfield LocalColorTableFlag;
	UBYTE_bitfield InterlaceFlag;
	UBYTE_bitfield Reserved;
	UBYTE_bitfield SizeOfLocalColorTable;
	IMAGEDESCRIPTOR_PACKEDFIELDS PackedFields_;
	IMAGEDESCRIPTOR ImageDescriptor;
	LOCALCOLORTABLE LocalColorTable;
	UBYTE_class LZWMinimumCodeSize;
	UBYTE_class Size;
	char_class Data_element;
	char_array_class Data;
	DATASUBBLOCK DataSubBlock;
	UBYTE_class BlockTerminator;
	DATASUBBLOCKS DataSubBlocks;
	IMAGEDATA ImageData;
	UBYTE_class ExtensionIntroducer;
	UBYTE_class GraphicControlLabel;
	UBYTE_class BlockSize;
	UBYTE_bitfield DisposalMethod;
	UBYTE_bitfield UserInputFlag;
	UBYTE_bitfield TransparentColorFlag;
	GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS PackedFields__;
	ushort_class DelayTime;
	UBYTE_class TransparentColorIndex;
	GRAPHICCONTROLSUBBLOCK GraphicControlSubBlock;
	GRAPHICCONTROLEXTENSION GraphicControlExtension;
	UBYTE_class CommentLabel;
	DATASUBBLOCKS CommentData;
	COMMENTEXTENSION CommentExtension;
	UBYTE_class PlainTextLabel;
	ushort_class TextGridLeftPosition;
	ushort_class TextGridTopPosition;
	ushort_class TextGridWidth;
	ushort_class TextGridHeight;
	UBYTE_class CharacterCellWidth;
	UBYTE_class CharacterCellHeight;
	UBYTE_class TextForegroundColorIndex;
	UBYTE_class TextBackgroundColorIndex;
	PLAINTEXTSUBBLOCK PlainTextSubBlock;
	DATASUBBLOCKS PlainTextData;
	PLAINTEXTEXTENTION PlainTextExtension;
	UBYTE_class ApplicationLabel;
	char_class ApplicationIdentifier_element;
	char_array_class ApplicationIdentifier;
	char_class ApplicationAuthenticationCode_element;
	char_array_class ApplicationAuthenticationCode;
	APPLICATIONSUBBLOCK ApplicationSubBlock;
	DATASUBBLOCKS ApplicationData;
	APPLICATIONEXTENTION ApplicationExtension;
	UBYTE_class Label;
	UNDEFINEDDATA UndefinedData;
	DATA Data_;
	UBYTE_class GIFTrailer;
	TRAILER Trailer;


	globals_class() :
		Signature_element(false),
		Signature(Signature_element, { "GIF" }),
		Version_element(false),
		Version(Version_element, { "89a" }),
		GifHeader(GIFHEADER_GifHeader_instances),
		Width(1),
		Height(1),
		GlobalColorTableFlag(1, { 1 }),
		ColorResolution(1),
		SortFlag(1),
		SizeOfGlobalColorTable(1),
		PackedFields(LOGICALSCREENDESCRIPTOR_PACKEDFIELDS_PackedFields_instances),
		BackgroundColorIndex(1),
		PixelAspectRatio(1),
		LogicalScreenDescriptor(LOGICALSCREENDESCRIPTOR_LogicalScreenDescriptor_instances),
		R(1),
		G(1),
		B(1),
		rgb_element(RGB_rgb_element_instances),
		rgb(rgb_element),
		GlobalColorTable(GLOBALCOLORTABLE_GlobalColorTable_instances),
		ImageSeperator(1),
		ImageLeftPosition(1),
		ImageTopPosition(1),
		ImageWidth(1),
		ImageHeight(1),
		LocalColorTableFlag(1, { 1 }),
		InterlaceFlag(1),
		Reserved(1),
		SizeOfLocalColorTable(1),
		PackedFields_(IMAGEDESCRIPTOR_PACKEDFIELDS_PackedFields__instances),
		ImageDescriptor(IMAGEDESCRIPTOR_ImageDescriptor_instances),
		LocalColorTable(LOCALCOLORTABLE_LocalColorTable_instances),
		LZWMinimumCodeSize(1),
		Size(1),
		Data_element(false),
		Data(Data_element),
		DataSubBlock(DATASUBBLOCK_DataSubBlock_instances),
		BlockTerminator(1),
		DataSubBlocks(DATASUBBLOCKS_DataSubBlocks_instances),
		ImageData(IMAGEDATA_ImageData_instances),
		ExtensionIntroducer(1),
		GraphicControlLabel(1),
		BlockSize(1),
		DisposalMethod(1),
		UserInputFlag(1),
		TransparentColorFlag(1),
		PackedFields__(GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS_PackedFields___instances),
		DelayTime(1),
		TransparentColorIndex(1),
		GraphicControlSubBlock(GRAPHICCONTROLSUBBLOCK_GraphicControlSubBlock_instances),
		GraphicControlExtension(GRAPHICCONTROLEXTENSION_GraphicControlExtension_instances),
		CommentLabel(1),
		CommentData(DATASUBBLOCKS_CommentData_instances),
		CommentExtension(COMMENTEXTENSION_CommentExtension_instances),
		PlainTextLabel(1),
		TextGridLeftPosition(1),
		TextGridTopPosition(1),
		TextGridWidth(1),
		TextGridHeight(1),
		CharacterCellWidth(1),
		CharacterCellHeight(1),
		TextForegroundColorIndex(1),
		TextBackgroundColorIndex(1),
		PlainTextSubBlock(PLAINTEXTSUBBLOCK_PlainTextSubBlock_instances),
		PlainTextData(DATASUBBLOCKS_PlainTextData_instances),
		PlainTextExtension(PLAINTEXTEXTENTION_PlainTextExtension_instances),
		ApplicationLabel(1),
		ApplicationIdentifier_element(false),
		ApplicationIdentifier(ApplicationIdentifier_element),
		ApplicationAuthenticationCode_element(false),
		ApplicationAuthenticationCode(ApplicationAuthenticationCode_element),
		ApplicationSubBlock(APPLICATIONSUBBLOCK_ApplicationSubBlock_instances),
		ApplicationData(DATASUBBLOCKS_ApplicationData_instances),
		ApplicationExtension(APPLICATIONEXTENTION_ApplicationExtension_instances),
		Label(1),
		UndefinedData(UNDEFINEDDATA_UndefinedData_instances),
		Data_(DATA_Data__instances),
		GIFTrailer(1),
		Trailer(TRAILER_Trailer_instances)
	{}
};

globals_class* g;


GIFHEADER* GIFHEADER::generate() {
	if (generated == 1) {
		GIFHEADER* new_instance = new GIFHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	evil = SetEvilBit(false);
	GENERATE_VAR(Signature, ::g->Signature.generate(3));
	SetEvilBit(evil);
	GENERATE_VAR(Version, ::g->Version.generate(3, { {"87a"}, {"89a"} }));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


LOGICALSCREENDESCRIPTOR_PACKEDFIELDS* LOGICALSCREENDESCRIPTOR_PACKEDFIELDS::generate() {
	if (generated == 1) {
		LOGICALSCREENDESCRIPTOR_PACKEDFIELDS* new_instance = new LOGICALSCREENDESCRIPTOR_PACKEDFIELDS(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(GlobalColorTableFlag, ::g->GlobalColorTableFlag.generate(1));
	GENERATE_VAR(ColorResolution, ::g->ColorResolution.generate(3));
	GENERATE_VAR(SortFlag, ::g->SortFlag.generate(1));
	GENERATE_VAR(SizeOfGlobalColorTable, ::g->SizeOfGlobalColorTable.generate(3));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


LOGICALSCREENDESCRIPTOR* LOGICALSCREENDESCRIPTOR::generate() {
	if (generated == 1) {
		LOGICALSCREENDESCRIPTOR* new_instance = new LOGICALSCREENDESCRIPTOR(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(Width, ::g->Width.generate());
	GENERATE_VAR(Height, ::g->Height.generate());
	BitfieldLeftToRight();
	GENERATE_VAR(PackedFields, ::g->PackedFields.generate());
	GENERATE_VAR(BackgroundColorIndex, ::g->BackgroundColorIndex.generate());
	if ((::g->GifHeader().Version() == "89a")) {
		GENERATE_VAR(PixelAspectRatio, ::g->PixelAspectRatio.generate());
	} else {
		GENERATE_VAR(PixelAspectRatio, ::g->PixelAspectRatio.generate({ 0 }));
	};

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


RGB* RGB::generate() {
	if (generated == 1) {
		RGB* new_instance = new RGB(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(R, ::g->R.generate());
	GENERATE_VAR(G, ::g->G.generate());
	GENERATE_VAR(B, ::g->B.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


GLOBALCOLORTABLE* GLOBALCOLORTABLE::generate() {
	if (generated == 1) {
		GLOBALCOLORTABLE* new_instance = new GLOBALCOLORTABLE(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	size = 1;
	for (i = 0; (i <= ::g->LogicalScreenDescriptor().PackedFields().SizeOfGlobalColorTable()); i++) {
			size *= 2;
	;
	};
	GENERATE_VAR(rgb, ::g->rgb.generate(size));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


IMAGEDESCRIPTOR_PACKEDFIELDS* IMAGEDESCRIPTOR_PACKEDFIELDS::generate() {
	if (generated == 1) {
		IMAGEDESCRIPTOR_PACKEDFIELDS* new_instance = new IMAGEDESCRIPTOR_PACKEDFIELDS(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	if ((::g->LogicalScreenDescriptor().PackedFields().GlobalColorTableFlag() == 1)) {
		possible_values = { 0, 1 };
	} else {
		possible_values = { 1 };
	};
	GENERATE_VAR(LocalColorTableFlag, ::g->LocalColorTableFlag.generate(1, possible_values));
	GENERATE_VAR(InterlaceFlag, ::g->InterlaceFlag.generate(1));
	GENERATE_VAR(SortFlag, ::g->SortFlag.generate(1));
	GENERATE_VAR(Reserved, ::g->Reserved.generate(2));
	GENERATE_VAR(SizeOfLocalColorTable, ::g->SizeOfLocalColorTable.generate(3));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


IMAGEDESCRIPTOR* IMAGEDESCRIPTOR::generate() {
	if (generated == 1) {
		IMAGEDESCRIPTOR* new_instance = new IMAGEDESCRIPTOR(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(ImageSeperator, ::g->ImageSeperator.generate());
	GENERATE_VAR(ImageLeftPosition, ::g->ImageLeftPosition.generate());
	GENERATE_VAR(ImageTopPosition, ::g->ImageTopPosition.generate());
	GENERATE_VAR(ImageWidth, ::g->ImageWidth.generate());
	GENERATE_VAR(ImageHeight, ::g->ImageHeight.generate());
	GENERATE_VAR(PackedFields, ::g->PackedFields_.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


LOCALCOLORTABLE* LOCALCOLORTABLE::generate() {
	if (generated == 1) {
		LOCALCOLORTABLE* new_instance = new LOCALCOLORTABLE(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	size = 1;
	for (i = 0; (i <= ::g->ImageDescriptor().PackedFields().SizeOfLocalColorTable()); i++) {
			size *= 2;
	;
	};
	GENERATE_VAR(rgb, ::g->rgb.generate(size));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


DATASUBBLOCK* DATASUBBLOCK::generate(UBYTE& size) {
	if (generated == 1) {
		DATASUBBLOCK* new_instance = new DATASUBBLOCK(instances);
		new_instance->generated = 2;
		return new_instance->generate(size);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(Size, ::g->Size.generate());
	GENERATE_VAR(Data, ::g->Data.generate(size));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


DATASUBBLOCKS* DATASUBBLOCKS::generate() {
	if (generated == 1) {
		DATASUBBLOCKS* new_instance = new DATASUBBLOCKS(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	values = {  };
	for (count = 1; (count < 256); ++count) {
		values.insert(values.end(), { (UBYTE)count });
	};
	count = 0;
	size = ReadUByte(FTell(), values);
	while ((size != 0)) {
		GENERATE_VAR(DataSubBlock, ::g->DataSubBlock.generate(size));
		count += size;
		size = ReadUByte(FTell(), values);
		if ((count > 1500)) {
			values = { 0, 255 };
		};
	};
	GENERATE_VAR(BlockTerminator, ::g->BlockTerminator.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


IMAGEDATA* IMAGEDATA::generate() {
	if (generated == 1) {
		IMAGEDATA* new_instance = new IMAGEDATA(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(LZWMinimumCodeSize, ::g->LZWMinimumCodeSize.generate({ 8 }));
	GENERATE_VAR(DataSubBlocks, ::g->DataSubBlocks.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS* GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS::generate() {
	if (generated == 1) {
		GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS* new_instance = new GRAPHICCONTROLEXTENSION_DATASUBBLOCK_PACKEDFIELDS(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(Reserved, ::g->Reserved.generate(3));
	GENERATE_VAR(DisposalMethod, ::g->DisposalMethod.generate(3));
	GENERATE_VAR(UserInputFlag, ::g->UserInputFlag.generate(1));
	GENERATE_VAR(TransparentColorFlag, ::g->TransparentColorFlag.generate(1));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


GRAPHICCONTROLSUBBLOCK* GRAPHICCONTROLSUBBLOCK::generate() {
	if (generated == 1) {
		GRAPHICCONTROLSUBBLOCK* new_instance = new GRAPHICCONTROLSUBBLOCK(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(BlockSize, ::g->BlockSize.generate({ 4 }));
	GENERATE_VAR(PackedFields, ::g->PackedFields__.generate());
	GENERATE_VAR(DelayTime, ::g->DelayTime.generate());
	GENERATE_VAR(TransparentColorIndex, ::g->TransparentColorIndex.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


GRAPHICCONTROLEXTENSION* GRAPHICCONTROLEXTENSION::generate() {
	if (generated == 1) {
		GRAPHICCONTROLEXTENSION* new_instance = new GRAPHICCONTROLEXTENSION(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(ExtensionIntroducer, ::g->ExtensionIntroducer.generate());
	GENERATE_VAR(GraphicControlLabel, ::g->GraphicControlLabel.generate());
	GENERATE_VAR(GraphicControlSubBlock, ::g->GraphicControlSubBlock.generate());
	GENERATE_VAR(BlockTerminator, ::g->BlockTerminator.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


COMMENTEXTENSION* COMMENTEXTENSION::generate() {
	if (generated == 1) {
		COMMENTEXTENSION* new_instance = new COMMENTEXTENSION(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(ExtensionIntroducer, ::g->ExtensionIntroducer.generate());
	GENERATE_VAR(CommentLabel, ::g->CommentLabel.generate());
	GENERATE_VAR(CommentData, ::g->CommentData.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


PLAINTEXTSUBBLOCK* PLAINTEXTSUBBLOCK::generate() {
	if (generated == 1) {
		PLAINTEXTSUBBLOCK* new_instance = new PLAINTEXTSUBBLOCK(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(BlockSize, ::g->BlockSize.generate());
	GENERATE_VAR(TextGridLeftPosition, ::g->TextGridLeftPosition.generate());
	GENERATE_VAR(TextGridTopPosition, ::g->TextGridTopPosition.generate());
	GENERATE_VAR(TextGridWidth, ::g->TextGridWidth.generate());
	GENERATE_VAR(TextGridHeight, ::g->TextGridHeight.generate());
	GENERATE_VAR(CharacterCellWidth, ::g->CharacterCellWidth.generate());
	GENERATE_VAR(CharacterCellHeight, ::g->CharacterCellHeight.generate());
	GENERATE_VAR(TextForegroundColorIndex, ::g->TextForegroundColorIndex.generate());
	GENERATE_VAR(TextBackgroundColorIndex, ::g->TextBackgroundColorIndex.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


PLAINTEXTEXTENTION* PLAINTEXTEXTENTION::generate() {
	if (generated == 1) {
		PLAINTEXTEXTENTION* new_instance = new PLAINTEXTEXTENTION(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(ExtensionIntroducer, ::g->ExtensionIntroducer.generate());
	GENERATE_VAR(PlainTextLabel, ::g->PlainTextLabel.generate());
	GENERATE_VAR(PlainTextSubBlock, ::g->PlainTextSubBlock.generate());
	GENERATE_VAR(PlainTextData, ::g->PlainTextData.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


APPLICATIONSUBBLOCK* APPLICATIONSUBBLOCK::generate() {
	if (generated == 1) {
		APPLICATIONSUBBLOCK* new_instance = new APPLICATIONSUBBLOCK(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(BlockSize, ::g->BlockSize.generate());
	GENERATE_VAR(ApplicationIdentifier, ::g->ApplicationIdentifier.generate(8));
	GENERATE_VAR(ApplicationAuthenticationCode, ::g->ApplicationAuthenticationCode.generate(3));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


APPLICATIONEXTENTION* APPLICATIONEXTENTION::generate() {
	if (generated == 1) {
		APPLICATIONEXTENTION* new_instance = new APPLICATIONEXTENTION(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(ExtensionIntroducer, ::g->ExtensionIntroducer.generate());
	GENERATE_VAR(ApplicationLabel, ::g->ApplicationLabel.generate());
	GENERATE_VAR(ApplicationSubBlock, ::g->ApplicationSubBlock.generate());
	GENERATE_VAR(ApplicationData, ::g->ApplicationData.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


UNDEFINEDDATA* UNDEFINEDDATA::generate() {
	if (generated == 1) {
		UNDEFINEDDATA* new_instance = new UNDEFINEDDATA(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(ExtensionIntroducer, ::g->ExtensionIntroducer.generate());
	GENERATE_VAR(Label, ::g->Label.generate());
	GENERATE_VAR(DataSubBlocks, ::g->DataSubBlocks.generate());

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


DATA* DATA::generate() {
	if (generated == 1) {
		DATA* new_instance = new DATA(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	if ((::g->GifHeader().Version() == "89a")) {
		possible = { 0x2C, 0x21 };
	} else {
		possible = { 0x2C };
	};
	has_data = false;
	while ((ReadUByte(FTell(), possible) != 0x3B)) {
		if ((ReadUByte(FTell()) == 0x2C)) {
			if (!has_data) {
				has_data = true;
				possible.insert(possible.end(), { 0x3B });
			};
			SetBackColor(0xE0FFE0);
			GENERATE_VAR(ImageDescriptor, ::g->ImageDescriptor.generate());
			if ((ImageDescriptor().PackedFields().LocalColorTableFlag() == 1)) {
				SetBackColor(0xC0FFC0);
				GENERATE_VAR(LocalColorTable, ::g->LocalColorTable.generate());
			};
			SetBackColor(0xA0FFA0);
			GENERATE_VAR(ImageData, ::g->ImageData.generate());
		} else {
		if ((ReadUShort(FTell()) == 0xF921)) {
			SetBackColor(0xC0FFFF);
			GENERATE_VAR(GraphicControlExtension, ::g->GraphicControlExtension.generate());
		} else {
		if ((ReadUShort(FTell()) == 0xFE21)) {
			SetBackColor(0xFFFFC0);
			GENERATE_VAR(CommentExtension, ::g->CommentExtension.generate());
		} else {
		if ((ReadUShort(FTell()) == 0x0121)) {
			SetBackColor(0xC0C0C0);
			GENERATE_VAR(PlainTextExtension, ::g->PlainTextExtension.generate());
		} else {
		if ((ReadUShort(FTell()) == 0xFF21)) {
			SetBackColor(0xC0C0FF);
			GENERATE_VAR(ApplicationExtension, ::g->ApplicationExtension.generate());
		} else {
			SetBackColor(0xFF8080);
			GENERATE_VAR(UndefinedData, ::g->UndefinedData.generate());
		};
		};
		};
		};
		};
	};

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}


TRAILER* TRAILER::generate() {
	if (generated == 1) {
		TRAILER* new_instance = new TRAILER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();
	if (_parent_id != ::g->_struct_id && !global_indexing_of_arrays) {
		_index_start = instances.size() - 1;
	}
	_parent_id = ::g->_struct_id;
	::g->_struct_id = ++::g->_struct_id_counter;

	GENERATE_VAR(GIFTrailer, ::g->GIFTrailer.generate({ 0x3B }));

	::g->_struct_id = _parent_id;
	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	LittleEndian();
	SetBackColor(0xFFFFFF);
	GENERATE(GifHeader, ::g->GifHeader.generate());
	if ((::g->GifHeader().Signature() != "GIF")) {
		Warning("File is not a valid GIF. Template stopped.");
		exit_template(-1);
	};
	SetBackColor(0xE0E0E0);
	GENERATE(LogicalScreenDescriptor, ::g->LogicalScreenDescriptor.generate());
	if ((::g->LogicalScreenDescriptor().PackedFields().GlobalColorTableFlag() == 1)) {
		SetBackColor(0xC0C0C0);
		GENERATE(GlobalColorTable, ::g->GlobalColorTable.generate());
	};
	SetBackColor(0xFFFFFF);
	GENERATE(Data, ::g->Data_.generate());
	SetBackColor(0xFFFFFF);
	SetEvilBit(false);
	GENERATE(Trailer, ::g->Trailer.generate());

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

