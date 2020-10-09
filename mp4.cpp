#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"

enum qtlang {
	qtlEnglish = 0,
	qtlFrench = 1,
	qtlGerman = 2,
	qtlItalian = 3,
	qtlDutch = 4,
	qtlSwedish = 5,
	qtlSpanish = 6,
	qtlDanish = 7,
	qtlPortuguese = 8,
	qtlNorwegian = 9,
	qtlHebrew = 10,
	qtlJapanese = 11,
	qtlArabic = 12,
	qtlFinnish = 13,
	qtlGreek = 14,
	qtlIcelandic = 15,
	qtlMaltese = 16,
	qtlTurkish = 17,
	qtlCroatian = 18,
	qtlChineseTraditional = 19,
	qtlUrdu = 20,
	qtlHindi = 21,
	qtlThai = 22,
	qtlKorean = 23,
	qtlLithuanian = 24,
	qtlPolish = 25,
	qtlHungarian = 26,
	qtlEstonian = 27,
	qtlLettish = 28,
	qtlLatvian = 28,
	qtlSaami = 29,
	qtlSami = 29,
	qtlFaroese = 30,
	qtlFarsi = 31,
	qtlRussian = 32,
	qtlChineseSimplified = 33,
	qtlFlemish = 34,
	qtlIrish = 35,
	qtlAlbanian = 36,
	qtlRomanian = 37,
	qtlCzech = 38,
	qtlSlovak = 39,
	qtlSlovenian = 40,
	qtlYiddish = 41,
	qtlSerbian = 42,
	qtlMacedonian = 43,
	qtlBulgarian = 44,
	qtlUkrainian = 45,
	qtlBelarusian = 46,
	qtlUzbek = 47,
	qtlKazakh = 48,
	qtlAzerbaijani = 49,
	qtlAzerbaijanAr = 50,
	qtlArmenian = 51,
	qtlGeorgian = 52,
	qtlMoldavian = 53,
	qtlKirghiz = 54,
	qtlTajiki = 55,
	qtlTurkmen = 56,
	qtlMongolian = 57,
	qtlMongolianCyr = 58,
	qtlPashto = 59,
	qtlKurdish = 60,
	qtlKashmiri = 61,
	qtlSindhi = 62,
	qtlTibetan = 63,
	qtlNepali = 64,
	qtlSanskrit = 65,
	qtlMarathi = 66,
	qtlBengali = 67,
	qtlAssamese = 68,
	qtlGujarati = 69,
	qtlPunjabi = 70,
	qtlOriya = 71,
	qtlMalayalam = 72,
	qtlKannada = 73,
	qtlTamil = 74,
	qtlTelugu = 75,
	qtlSinhala = 76,
	qtlBurmese = 77,
	qtlKhmer = 78,
	qtlLao = 79,
	qtlVietnamese = 80,
	qtlIndonesian = 81,
	qtlTagalog = 82,
	qtlMalayRoman = 83,
	qtlMalayArabic = 84,
	qtlAmharic = 85,
	qtlGalla = 87,
	qtlOromo = 87,
	qtlSomali = 88,
	qtlSwahili = 89,
	qtlKinyarwanda = 90,
	qtlRundi = 91,
	qtlNyanja = 92,
	qtlMalagasy = 93,
	qtlEsperanto = 94,
	qtlWelsh = 128,
	qtlBasque = 129,
	qtlCatalan = 130,
	qtlLatin = 131,
	qtlQuechua = 132,
	qtlGuarani = 133,
	qtlAymara = 134,
	qtlTatar = 135,
	qtlUighur = 136,
	qtlDzongkha = 137,
	qtlJavaneseRom = 138,
	qtlUnspecified = 32767,
};

enum qtgfxmode : uint16 {
	qtgCopy = (uint16) 0x000,
	qtgDitherCopy = (uint16) 0x040,
	qtgBlend = (uint16) 0x020,
	qtgTransparent = (uint16) 0x024,
	qtgStraightAlpha = (uint16) 0x100,
	qtgPremulWhiteAlpha = (uint16) 0x101,
	qtgPremulBlackAlpha = (uint16) 0x102,
	qtgStraightAlphaBlend = (uint16) 0x104,
	qtgComposition = (uint16) 0x103,
};
std::vector<uint16> qtgfxmode_values = { qtgCopy, qtgDitherCopy, qtgBlend, qtgTransparent, qtgStraightAlpha, qtgPremulWhiteAlpha, qtgPremulBlackAlpha, qtgStraightAlphaBlend, qtgComposition };


class uint32_class {
	bool small;
	std::vector<uint32> known_values;
	uint32 value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(uint32);
	uint32 operator () () { return value; }
	uint32_class(bool small, std::vector<uint32> known_values = {}) : small(small), known_values(known_values) {}

	uint32 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint32), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint32), 0, known_values);
		}
		return value;
	}

	uint32 generate(std::vector<uint32> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uint32), 0, new_known_values);
		return value;
	}
};



class byte_class {
	bool small;
	std::vector<byte> known_values;
	byte value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(byte);
	byte operator () () { return value; }
	byte_class(bool small, std::vector<byte> known_values = {}) : small(small), known_values(known_values) {}

	byte generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(byte), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(byte), 0, known_values);
		}
		return value;
	}

	byte generate(std::vector<byte> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(byte), 0, new_known_values);
		return value;
	}
};



class byte_array_class {
	byte_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<byte>> element_known_values;
	std::string value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::string operator () () { return value; }
	byte operator [] (int index) { return value[index]; }
	byte_array_class(byte_class& element, std::unordered_map<int, std::vector<byte>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	byte_array_class(byte_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> new_known_values = {}) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = "";
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		if (new_known_values.size()) {
			std::string res = file_acc.file_string(new_known_values);
			assert(res.length() == size);
			for (unsigned i = 0; i < size; ++i) {
				value.push_back(res[i]);
			}
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



class fourcc {
	std::vector<fourcc*>& instances;

	std::string value_var;

public:
	bool value_exists = false;

	std::string value() {
		assert_cond(value_exists, "struct field value does not exist");
		return value_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	fourcc& operator () () { return *instances.back(); }
	fourcc* operator [] (int index) { return instances[index]; }
	fourcc(std::vector<fourcc*>& instances) : instances(instances) { instances.push_back(this); }
	~fourcc() {
		if (generated == 2)
			return;
		while (instances.size()) {
			fourcc* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	fourcc* generate();
};


class mp4box;



class char_class {
	bool small;
	std::vector<char> known_values;
	char value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(char);
	char operator () () { return value; }
	char_class(bool small, std::vector<char> known_values = {}) : small(small), known_values(known_values) {}

	char generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(char), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(char), 0, known_values);
		}
		return value;
	}

	char generate(std::vector<char> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(char), 0, new_known_values);
		return value;
	}
};



class char_array_class {
	char_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<char>> element_known_values;
	std::string value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::string operator () () { return value; }
	char operator [] (int index) { return value[index]; }
	char_array_class(char_class& element, std::unordered_map<int, std::vector<char>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	char_array_class(char_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> new_known_values = {}) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = "";
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		if (new_known_values.size()) {
			std::string res = file_acc.file_string(new_known_values);
			assert(res.length() == size);
			for (unsigned i = 0; i < size; ++i) {
				value.push_back(res[i]);
			}
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



class uint64_class {
	bool small;
	std::vector<uint64> known_values;
	uint64 value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(uint64);
	uint64 operator () () { return value; }
	uint64_class(bool small, std::vector<uint64> known_values = {}) : small(small), known_values(known_values) {}

	uint64 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint64), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint64), 0, known_values);
		}
		return value;
	}

	uint64 generate(std::vector<uint64> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uint64), 0, new_known_values);
		return value;
	}
};



class int32_class {
	bool small;
	std::vector<int32> known_values;
	int32 value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(int32);
	int32 operator () () { return value; }
	int32_class(bool small, std::vector<int32> known_values = {}) : small(small), known_values(known_values) {}

	int32 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(int32), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(int32), 0, known_values);
		}
		return value;
	}

	int32 generate(std::vector<int32> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(int32), 0, new_known_values);
		return value;
	}
};



class fp32 {
	std::vector<fp32*>& instances;

	int32 value_var;

public:
	bool value_exists = false;

	int32 value() {
		assert_cond(value_exists, "struct field value does not exist");
		return value_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	fp32& operator () () { return *instances.back(); }
	fp32* operator [] (int index) { return instances[index]; }
	fp32(std::vector<fp32*>& instances) : instances(instances) { instances.push_back(this); }
	~fp32() {
		if (generated == 2)
			return;
		while (instances.size()) {
			fp32* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	fp32* generate();
};



class int16_class {
	bool small;
	std::vector<int16> known_values;
	int16 value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(int16);
	int16 operator () () { return value; }
	int16_class(bool small, std::vector<int16> known_values = {}) : small(small), known_values(known_values) {}

	int16 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(int16), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(int16), 0, known_values);
		}
		return value;
	}

	int16 generate(std::vector<int16> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(int16), 0, new_known_values);
		return value;
	}
};



class fp16 {
	std::vector<fp16*>& instances;

	int16 value_var;

public:
	bool value_exists = false;

	int16 value() {
		assert_cond(value_exists, "struct field value does not exist");
		return value_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	fp16& operator () () { return *instances.back(); }
	fp16* operator [] (int index) { return instances[index]; }
	fp16(std::vector<fp16*>& instances) : instances(instances) { instances.push_back(this); }
	~fp16() {
		if (generated == 2)
			return;
		while (instances.size()) {
			fp16* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	fp16* generate();
};



class fp32uvw {
	std::vector<fp32uvw*>& instances;

	int32 value_var;

public:
	bool value_exists = false;

	int32 value() {
		assert_cond(value_exists, "struct field value does not exist");
		return value_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	fp32uvw& operator () () { return *instances.back(); }
	fp32uvw* operator [] (int index) { return instances[index]; }
	fp32uvw(std::vector<fp32uvw*>& instances) : instances(instances) { instances.push_back(this); }
	~fp32uvw() {
		if (generated == 2)
			return;
		while (instances.size()) {
			fp32uvw* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	fp32uvw* generate();
};



class matrix {
	std::vector<matrix*>& instances;

	fp32* a_var;
	fp32* b_var;
	fp32uvw* u_var;
	fp32* c_var;
	fp32* d_var;
	fp32uvw* v_var;
	fp32* x_var;
	fp32* y_var;
	fp32uvw* w_var;

public:
	bool a_exists = false;
	bool b_exists = false;
	bool u_exists = false;
	bool c_exists = false;
	bool d_exists = false;
	bool v_exists = false;
	bool x_exists = false;
	bool y_exists = false;
	bool w_exists = false;

	fp32& a() {
		assert_cond(a_exists, "struct field a does not exist");
		return *a_var;
	}
	fp32& b() {
		assert_cond(b_exists, "struct field b does not exist");
		return *b_var;
	}
	fp32uvw& u() {
		assert_cond(u_exists, "struct field u does not exist");
		return *u_var;
	}
	fp32& c() {
		assert_cond(c_exists, "struct field c does not exist");
		return *c_var;
	}
	fp32& d() {
		assert_cond(d_exists, "struct field d does not exist");
		return *d_var;
	}
	fp32uvw& v() {
		assert_cond(v_exists, "struct field v does not exist");
		return *v_var;
	}
	fp32& x() {
		assert_cond(x_exists, "struct field x does not exist");
		return *x_var;
	}
	fp32& y() {
		assert_cond(y_exists, "struct field y does not exist");
		return *y_var;
	}
	fp32uvw& w() {
		assert_cond(w_exists, "struct field w does not exist");
		return *w_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	matrix& operator () () { return *instances.back(); }
	matrix* operator [] (int index) { return instances[index]; }
	matrix(std::vector<matrix*>& instances) : instances(instances) { instances.push_back(this); }
	~matrix() {
		if (generated == 2)
			return;
		while (instances.size()) {
			matrix* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	matrix* generate();
};



class uint32_array_class {
	uint32_class& element;
	std::unordered_map<int, std::vector<uint32>> element_known_values;
	std::vector<uint32> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<uint32> operator () () { return value; }
	uint32 operator [] (int index) { return value[index]; }
	uint32_array_class(uint32_class& element, std::unordered_map<int, std::vector<uint32>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}

	std::vector<uint32> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(uint32), 0, known->second));
				_sizeof += sizeof(uint32);
			}
		}
		return value;
	}
};



class byte_bitfield {
	bool small;
	std::vector<byte> known_values;
	byte value;
public:
	byte operator () () { return value; }
	byte_bitfield(bool small, std::vector<byte> known_values = {}) : small(small), known_values(known_values) {}

	byte generate(unsigned bits) {
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(byte), bits, small);
		} else {
			value = file_acc.file_integer(sizeof(byte), bits, known_values);
		}
		return value;
	}

	byte generate(unsigned bits, std::vector<byte> new_known_values) {
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(byte), bits, new_known_values);
		return value;
	}
};



class tkhd_flags {
	std::vector<tkhd_flags*>& instances;

	std::string dummy_var;
	byte dummy2_var : 4;
	byte track_in_poster_var : 1;
	byte track_in_preview_var : 1;
	byte track_in_movie_var : 1;
	byte track_enabled_var : 1;

public:
	bool dummy_exists = false;
	bool dummy2_exists = false;
	bool track_in_poster_exists = false;
	bool track_in_preview_exists = false;
	bool track_in_movie_exists = false;
	bool track_enabled_exists = false;

	std::string dummy() {
		assert_cond(dummy_exists, "struct field dummy does not exist");
		return dummy_var;
	}
	byte dummy2() {
		assert_cond(dummy2_exists, "struct field dummy2 does not exist");
		return dummy2_var;
	}
	byte track_in_poster() {
		assert_cond(track_in_poster_exists, "struct field track_in_poster does not exist");
		return track_in_poster_var;
	}
	byte track_in_preview() {
		assert_cond(track_in_preview_exists, "struct field track_in_preview does not exist");
		return track_in_preview_var;
	}
	byte track_in_movie() {
		assert_cond(track_in_movie_exists, "struct field track_in_movie does not exist");
		return track_in_movie_var;
	}
	byte track_enabled() {
		assert_cond(track_enabled_exists, "struct field track_enabled does not exist");
		return track_enabled_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	tkhd_flags& operator () () { return *instances.back(); }
	tkhd_flags* operator [] (int index) { return instances[index]; }
	tkhd_flags(std::vector<tkhd_flags*>& instances) : instances(instances) { instances.push_back(this); }
	~tkhd_flags() {
		if (generated == 2)
			return;
		while (instances.size()) {
			tkhd_flags* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	tkhd_flags* generate();
};



class uint16_class {
	bool small;
	std::vector<uint16> known_values;
	uint16 value;
public:
	int64 _startof;
	std::size_t _sizeof = sizeof(uint16);
	uint16 operator () () { return value; }
	uint16_class(bool small, std::vector<uint16> known_values = {}) : small(small), known_values(known_values) {}

	uint16 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint16), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint16), 0, known_values);
		}
		return value;
	}

	uint16 generate(std::vector<uint16> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uint16), 0, new_known_values);
		return value;
	}
};



class mp4lang {
	std::vector<mp4lang*>& instances;

	uint16 value_var;

public:
	bool value_exists = false;

	uint16 value() {
		assert_cond(value_exists, "struct field value does not exist");
		return value_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	mp4lang& operator () () { return *instances.back(); }
	mp4lang* operator [] (int index) { return instances[index]; }
	mp4lang(std::vector<mp4lang*>& instances) : instances(instances) { instances.push_back(this); }
	~mp4lang() {
		if (generated == 2)
			return;
		while (instances.size()) {
			mp4lang* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	mp4lang* generate();
};



class str_stts {
	std::vector<str_stts*>& instances;

	uint32 sample_count_var;
	uint32 sample_delta_var;

public:
	bool sample_count_exists = false;
	bool sample_delta_exists = false;

	uint32 sample_count() {
		assert_cond(sample_count_exists, "struct field sample_count does not exist");
		return sample_count_var;
	}
	uint32 sample_delta() {
		assert_cond(sample_delta_exists, "struct field sample_delta does not exist");
		return sample_delta_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	str_stts& operator () () { return *instances.back(); }
	str_stts* operator [] (int index) { return instances[index]; }
	str_stts(std::vector<str_stts*>& instances) : instances(instances) { instances.push_back(this); }
	~str_stts() {
		if (generated == 2)
			return;
		while (instances.size()) {
			str_stts* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	str_stts* generate();
};



class str_stts_array_class {
	str_stts& element;
	std::vector<str_stts*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<str_stts*> operator () () { return value; }
	str_stts operator [] (int index) { return *value[index]; }
	str_stts_array_class(str_stts& element) : element(element) {}

	std::vector<str_stts*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class elst_entry {
	std::vector<elst_entry*>& instances;

	uint32 duration_var;
	uint32 media_time_var;
	fp32* media_rate_var;

public:
	bool duration_exists = false;
	bool media_time_exists = false;
	bool media_rate_exists = false;

	uint32 duration() {
		assert_cond(duration_exists, "struct field duration does not exist");
		return duration_var;
	}
	uint32 media_time() {
		assert_cond(media_time_exists, "struct field media_time does not exist");
		return media_time_var;
	}
	fp32& media_rate() {
		assert_cond(media_rate_exists, "struct field media_rate does not exist");
		return *media_rate_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	elst_entry& operator () () { return *instances.back(); }
	elst_entry* operator [] (int index) { return instances[index]; }
	elst_entry(std::vector<elst_entry*>& instances) : instances(instances) { instances.push_back(this); }
	~elst_entry() {
		if (generated == 2)
			return;
		while (instances.size()) {
			elst_entry* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	elst_entry* generate();
};



class elst_entry_array_class {
	elst_entry& element;
	std::vector<elst_entry*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<elst_entry*> operator () () { return value; }
	elst_entry operator [] (int index) { return *value[index]; }
	elst_entry_array_class(elst_entry& element) : element(element) {}

	std::vector<elst_entry*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class uint16_array_class {
	uint16_class& element;
	std::unordered_map<int, std::vector<uint16>> element_known_values;
	std::vector<uint16> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<uint16> operator () () { return value; }
	uint16 operator [] (int index) { return value[index]; }
	uint16_array_class(uint16_class& element, std::unordered_map<int, std::vector<uint16>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}

	std::vector<uint16> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
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



class string_class {
	std::vector<std::string> known_values;
	std::string value;
public:
	int64 _startof;
	std::size_t _sizeof;
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



class vmhd_flags {
	std::vector<vmhd_flags*>& instances;

	std::string dummy_var;
	byte dummy2_var;

public:
	bool dummy_exists = false;
	bool dummy2_exists = false;

	std::string dummy() {
		assert_cond(dummy_exists, "struct field dummy does not exist");
		return dummy_var;
	}
	byte dummy2() {
		assert_cond(dummy2_exists, "struct field dummy2 does not exist");
		return dummy2_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	vmhd_flags& operator () () { return *instances.back(); }
	vmhd_flags* operator [] (int index) { return instances[index]; }
	vmhd_flags(std::vector<vmhd_flags*>& instances) : instances(instances) { instances.push_back(this); }
	~vmhd_flags() {
		if (generated == 2)
			return;
		while (instances.size()) {
			vmhd_flags* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	vmhd_flags* generate();
};


qtgfxmode qtgfxmode_generate() {
	return (qtgfxmode) file_acc.file_integer(sizeof(uint16), 0, qtgfxmode_values);
}


class qtopcolor {
	std::vector<qtopcolor*>& instances;

	uint16 red_var;
	uint16 green_var;
	uint16 blue_var;

public:
	bool red_exists = false;
	bool green_exists = false;
	bool blue_exists = false;

	uint16 red() {
		assert_cond(red_exists, "struct field red does not exist");
		return red_var;
	}
	uint16 green() {
		assert_cond(green_exists, "struct field green does not exist");
		return green_var;
	}
	uint16 blue() {
		assert_cond(blue_exists, "struct field blue does not exist");
		return blue_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	qtopcolor& operator () () { return *instances.back(); }
	qtopcolor* operator [] (int index) { return instances[index]; }
	qtopcolor(std::vector<qtopcolor*>& instances) : instances(instances) { instances.push_back(this); }
	~qtopcolor() {
		if (generated == 2)
			return;
		while (instances.size()) {
			qtopcolor* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	qtopcolor* generate();
};



class str_stsc {
	std::vector<str_stsc*>& instances;

	uint32 first_chunk_var;
	uint32 samples_per_chunk_var;
	uint32 sample_description_index_var;

public:
	bool first_chunk_exists = false;
	bool samples_per_chunk_exists = false;
	bool sample_description_index_exists = false;

	uint32 first_chunk() {
		assert_cond(first_chunk_exists, "struct field first_chunk does not exist");
		return first_chunk_var;
	}
	uint32 samples_per_chunk() {
		assert_cond(samples_per_chunk_exists, "struct field samples_per_chunk does not exist");
		return samples_per_chunk_var;
	}
	uint32 sample_description_index() {
		assert_cond(sample_description_index_exists, "struct field sample_description_index does not exist");
		return sample_description_index_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	str_stsc& operator () () { return *instances.back(); }
	str_stsc* operator [] (int index) { return instances[index]; }
	str_stsc(std::vector<str_stsc*>& instances) : instances(instances) { instances.push_back(this); }
	~str_stsc() {
		if (generated == 2)
			return;
		while (instances.size()) {
			str_stsc* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	str_stsc* generate();
};



class str_stsc_array_class {
	str_stsc& element;
	std::vector<str_stsc*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<str_stsc*> operator () () { return value; }
	str_stsc operator [] (int index) { return *value[index]; }
	str_stsc_array_class(str_stsc& element) : element(element) {}

	std::vector<str_stsc*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class uint64_array_class {
	uint64_class& element;
	std::unordered_map<int, std::vector<uint64>> element_known_values;
	std::vector<uint64> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<uint64> operator () () { return value; }
	uint64 operator [] (int index) { return value[index]; }
	uint64_array_class(uint64_class& element, std::unordered_map<int, std::vector<uint64>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}

	std::vector<uint64> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(uint64), 0, known->second));
				_sizeof += sizeof(uint64);
			}
		}
		return value;
	}
};



class KID_struct {
	std::vector<KID_struct*>& instances;

	std::string entry_var;

public:
	bool entry_exists = false;

	std::string entry() {
		assert_cond(entry_exists, "struct field entry does not exist");
		return entry_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	KID_struct& operator () () { return *instances.back(); }
	KID_struct* operator [] (int index) { return instances[index]; }
	KID_struct(std::vector<KID_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~KID_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			KID_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	KID_struct* generate();
};



class KID_struct_array_class {
	KID_struct& element;
	std::vector<KID_struct*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<KID_struct*> operator () () { return value; }
	KID_struct operator [] (int index) { return *value[index]; }
	KID_struct_array_class(KID_struct& element) : element(element) {}

	std::vector<KID_struct*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class entry_struct_subsample_data_struct {
	std::vector<entry_struct_subsample_data_struct*>& instances;

	uint16 bytes_of_clear_data_var;
	uint32 bytes_of_protected_data_var;

public:
	bool bytes_of_clear_data_exists = false;
	bool bytes_of_protected_data_exists = false;

	uint16 bytes_of_clear_data() {
		assert_cond(bytes_of_clear_data_exists, "struct field bytes_of_clear_data does not exist");
		return bytes_of_clear_data_var;
	}
	uint32 bytes_of_protected_data() {
		assert_cond(bytes_of_protected_data_exists, "struct field bytes_of_protected_data does not exist");
		return bytes_of_protected_data_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	entry_struct_subsample_data_struct& operator () () { return *instances.back(); }
	entry_struct_subsample_data_struct* operator [] (int index) { return instances[index]; }
	entry_struct_subsample_data_struct(std::vector<entry_struct_subsample_data_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~entry_struct_subsample_data_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			entry_struct_subsample_data_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	entry_struct_subsample_data_struct* generate();
};



class entry_struct_subsample_data_struct_array_class {
	entry_struct_subsample_data_struct& element;
	std::vector<entry_struct_subsample_data_struct*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<entry_struct_subsample_data_struct*> operator () () { return value; }
	entry_struct_subsample_data_struct operator [] (int index) { return *value[index]; }
	entry_struct_subsample_data_struct_array_class(entry_struct_subsample_data_struct& element) : element(element) {}

	std::vector<entry_struct_subsample_data_struct*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class entry_struct {
	std::vector<entry_struct*>& instances;

	std::string per_sample_IV_var;
	uint16 subsample_count_var;
	std::vector<entry_struct_subsample_data_struct*> subsample_data_var;

public:
	bool per_sample_IV_exists = false;
	bool subsample_count_exists = false;
	bool subsample_data_exists = false;

	std::string per_sample_IV() {
		assert_cond(per_sample_IV_exists, "struct field per_sample_IV does not exist");
		return per_sample_IV_var;
	}
	uint16 subsample_count() {
		assert_cond(subsample_count_exists, "struct field subsample_count does not exist");
		return subsample_count_var;
	}
	std::vector<entry_struct_subsample_data_struct*> subsample_data() {
		assert_cond(subsample_data_exists, "struct field subsample_data does not exist");
		return subsample_data_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	entry_struct& operator () () { return *instances.back(); }
	entry_struct* operator [] (int index) { return instances[index]; }
	entry_struct(std::vector<entry_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~entry_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			entry_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	entry_struct* generate();
};



class entry_struct_array_class {
	entry_struct& element;
	std::vector<entry_struct*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<entry_struct*> operator () () { return value; }
	entry_struct operator [] (int index) { return *value[index]; }
	entry_struct_array_class(entry_struct& element) : element(element) {}

	std::vector<entry_struct*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class str_sidx {
	std::vector<str_sidx*>& instances;

	uint32 reference_size31_type1_var;
	uint32 subsegment_duration_var;
	uint32 SAP_delta_time28_type3_starts_with1_var;

public:
	bool reference_size31_type1_exists = false;
	bool subsegment_duration_exists = false;
	bool SAP_delta_time28_type3_starts_with1_exists = false;

	uint32 reference_size31_type1() {
		assert_cond(reference_size31_type1_exists, "struct field reference_size31_type1 does not exist");
		return reference_size31_type1_var;
	}
	uint32 subsegment_duration() {
		assert_cond(subsegment_duration_exists, "struct field subsegment_duration does not exist");
		return subsegment_duration_var;
	}
	uint32 SAP_delta_time28_type3_starts_with1() {
		assert_cond(SAP_delta_time28_type3_starts_with1_exists, "struct field SAP_delta_time28_type3_starts_with1 does not exist");
		return SAP_delta_time28_type3_starts_with1_var;
	}

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	str_sidx& operator () () { return *instances.back(); }
	str_sidx* operator [] (int index) { return instances[index]; }
	str_sidx(std::vector<str_sidx*>& instances) : instances(instances) { instances.push_back(this); }
	~str_sidx() {
		if (generated == 2)
			return;
		while (instances.size()) {
			str_sidx* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	str_sidx* generate();
};



class str_sidx_array_class {
	str_sidx& element;
	std::vector<str_sidx*> value;
public:
	int64 _startof;
	std::size_t _sizeof;
	std::vector<str_sidx*> operator () () { return value; }
	str_sidx operator [] (int index) { return *value[index]; }
	str_sidx_array_class(str_sidx& element) : element(element) {}

	std::vector<str_sidx*> generate(unsigned size) {
		check_array_length(size);
		_startof = FTell();
		_sizeof = 0;
		value = {};
		for (unsigned i = 0; i < size; ++i) {
			value.push_back(element.generate());
			_sizeof += element._sizeof;
		}
		return value;
	}
};



class mp4box {
	std::vector<mp4box*>& instances;

	uint32 size_var;
	fourcc* type_var;
	mp4box* box_var;
	std::string major_brand_var;
	uint32 coin_var;
	std::string compatiple_brand_var;
	uint32 minor_version_var;
	byte version_var;
	uint32 time_scale_var;
	fp32* preferred_rate_var;
	fp16* preferred_volume_var;
	matrix* matrix_structure_var;
	uint32 preview_time_var;
	uint32 preview_duration_var;
	uint32 poster_time_var;
	uint32 selection_time_var;
	uint32 selection_duration_var;
	uint32 current_time_var;
	uint32 next_track_id_var;
	uint32 length_var;
	std::string data_var;
	uint32 num_entries_var;
	std::vector<uint32> track_IDs_var;
	uint32 track_id_var;
	uint16 layer_var;
	uint16 alt_group_var;
	fp16* volume_var;
	uint16 reserved3_var;
	fp32* width_var;
	fp32* height_var;
	uint16 quality_var;
	fourcc* subtype_var;
	uint32 mfr_var;
	uint32 flags_mask_var;
	std::string rest_var;
	std::string flag_var;
	uint32 entry_count_1_var;
	uint32 t_var;
	uint32 entry_count_2_var;
	std::vector<elst_entry*> entries_var;
	std::string notice_var;
	uint16 entry_count_3_var;
	uint16 item_ID_var;
	uint16 item_protection_index_var;
	std::string item_name_var;
	std::string content_type_var;
	std::string content_encoding_var;
	std::string location_var;
	std::string name_var;
	fp16* balance_var;
	uint16 graphics_mode_var;
	qtopcolor* opcolor_var;
	uint32 entry_count_4_var;
	uint32 entry_count_5_var;
	uint32 entry_count_6_var;
	uint32 sample_size_var;
	uint32 sample_count_var;
	std::vector<uint32> entry_size_var;
	uint32 codingName_var;
	byte reserved1_var;
	byte default_crypt_skip_byte_block_var;
	byte default_is_protected_var;
	byte default_per_sample_IV_size_var;
	std::string default_KID_var;
	byte default_constant_IV_size_var;
	std::string default_constant_IV_var;
	uint32 scheme_type_var;
	uint32 scheme_version_var;
	std::string systemID_var;
	uint32 KID_count_var;
	std::vector<KID_struct*> KID_var;
	uint32 DataSize_var;
	std::string Data_var;
	uint32 aux_info_type_var;
	uint32 aud_info_type_parameter_var;
	uint32 entry_count_7_var;
	uint32 aux_info_type_parameter_var;
	byte default_sample_info_size_var;
	uint32 data_offset_var;
	uint32 first_sample_flags_var;
	uint32 trackID_var;
	uint64 base_data_offset_var;
	uint32 sample_description_index_var;
	uint32 default_sample_duration_var;
	uint32 default_sample_size_var;
	uint32 default_sample_flags_var;
	uint32 sequence_number_var;
	uint32 referenceID_var;
	uint32 timescale_var;
	uint16 reference_count_var;
	std::vector<str_sidx*> references_var;
	uint32 default_sample_description_index_var;
	uint32 entry_count_8_var;
	uint32 entry_count_9_var;
	std::vector<uint32> sample_number_var;

public:
	bool size_exists = false;
	bool type_exists = false;
	bool box_exists = false;
	bool major_brand_exists = false;
	bool coin_exists = false;
	bool compatiple_brand_exists = false;
	bool minor_version_exists = false;
	bool version_exists = false;
	bool time_scale_exists = false;
	bool preferred_rate_exists = false;
	bool preferred_volume_exists = false;
	bool matrix_structure_exists = false;
	bool preview_time_exists = false;
	bool preview_duration_exists = false;
	bool poster_time_exists = false;
	bool selection_time_exists = false;
	bool selection_duration_exists = false;
	bool current_time_exists = false;
	bool next_track_id_exists = false;
	bool length_exists = false;
	bool data_exists = false;
	bool num_entries_exists = false;
	bool track_IDs_exists = false;
	bool track_id_exists = false;
	bool layer_exists = false;
	bool alt_group_exists = false;
	bool volume_exists = false;
	bool reserved3_exists = false;
	bool width_exists = false;
	bool height_exists = false;
	bool quality_exists = false;
	bool subtype_exists = false;
	bool mfr_exists = false;
	bool flags_mask_exists = false;
	bool rest_exists = false;
	bool flag_exists = false;
	bool entry_count_1_exists = false;
	bool t_exists = false;
	bool entry_count_2_exists = false;
	bool entries_exists = false;
	bool notice_exists = false;
	bool entry_count_3_exists = false;
	bool item_ID_exists = false;
	bool item_protection_index_exists = false;
	bool item_name_exists = false;
	bool content_type_exists = false;
	bool content_encoding_exists = false;
	bool location_exists = false;
	bool name_exists = false;
	bool balance_exists = false;
	bool graphics_mode_exists = false;
	bool opcolor_exists = false;
	bool entry_count_4_exists = false;
	bool entry_count_5_exists = false;
	bool entry_count_6_exists = false;
	bool sample_size_exists = false;
	bool sample_count_exists = false;
	bool entry_size_exists = false;
	bool codingName_exists = false;
	bool reserved1_exists = false;
	bool default_crypt_skip_byte_block_exists = false;
	bool default_is_protected_exists = false;
	bool default_per_sample_IV_size_exists = false;
	bool default_KID_exists = false;
	bool default_constant_IV_size_exists = false;
	bool default_constant_IV_exists = false;
	bool scheme_type_exists = false;
	bool scheme_version_exists = false;
	bool systemID_exists = false;
	bool KID_count_exists = false;
	bool KID_exists = false;
	bool DataSize_exists = false;
	bool Data_exists = false;
	bool aux_info_type_exists = false;
	bool aud_info_type_parameter_exists = false;
	bool entry_count_7_exists = false;
	bool aux_info_type_parameter_exists = false;
	bool default_sample_info_size_exists = false;
	bool data_offset_exists = false;
	bool first_sample_flags_exists = false;
	bool trackID_exists = false;
	bool base_data_offset_exists = false;
	bool sample_description_index_exists = false;
	bool default_sample_duration_exists = false;
	bool default_sample_size_exists = false;
	bool default_sample_flags_exists = false;
	bool sequence_number_exists = false;
	bool referenceID_exists = false;
	bool timescale_exists = false;
	bool reference_count_exists = false;
	bool references_exists = false;
	bool default_sample_description_index_exists = false;
	bool entry_count_8_exists = false;
	bool entry_count_9_exists = false;
	bool sample_number_exists = false;

	uint32 size() {
		assert_cond(size_exists, "struct field size does not exist");
		return size_var;
	}
	fourcc& type() {
		assert_cond(type_exists, "struct field type does not exist");
		return *type_var;
	}
	mp4box& box() {
		assert_cond(box_exists, "struct field box does not exist");
		return *box_var;
	}
	std::string major_brand() {
		assert_cond(major_brand_exists, "struct field major_brand does not exist");
		return major_brand_var;
	}
	uint32 coin() {
		assert_cond(coin_exists, "struct field coin does not exist");
		return coin_var;
	}
	std::string compatiple_brand() {
		assert_cond(compatiple_brand_exists, "struct field compatiple_brand does not exist");
		return compatiple_brand_var;
	}
	uint32 minor_version() {
		assert_cond(minor_version_exists, "struct field minor_version does not exist");
		return minor_version_var;
	}
	byte version() {
		assert_cond(version_exists, "struct field version does not exist");
		return version_var;
	}
	uint32 time_scale() {
		assert_cond(time_scale_exists, "struct field time_scale does not exist");
		return time_scale_var;
	}
	fp32& preferred_rate() {
		assert_cond(preferred_rate_exists, "struct field preferred_rate does not exist");
		return *preferred_rate_var;
	}
	fp16& preferred_volume() {
		assert_cond(preferred_volume_exists, "struct field preferred_volume does not exist");
		return *preferred_volume_var;
	}
	matrix& matrix_structure() {
		assert_cond(matrix_structure_exists, "struct field matrix_structure does not exist");
		return *matrix_structure_var;
	}
	uint32 preview_time() {
		assert_cond(preview_time_exists, "struct field preview_time does not exist");
		return preview_time_var;
	}
	uint32 preview_duration() {
		assert_cond(preview_duration_exists, "struct field preview_duration does not exist");
		return preview_duration_var;
	}
	uint32 poster_time() {
		assert_cond(poster_time_exists, "struct field poster_time does not exist");
		return poster_time_var;
	}
	uint32 selection_time() {
		assert_cond(selection_time_exists, "struct field selection_time does not exist");
		return selection_time_var;
	}
	uint32 selection_duration() {
		assert_cond(selection_duration_exists, "struct field selection_duration does not exist");
		return selection_duration_var;
	}
	uint32 current_time() {
		assert_cond(current_time_exists, "struct field current_time does not exist");
		return current_time_var;
	}
	uint32 next_track_id() {
		assert_cond(next_track_id_exists, "struct field next_track_id does not exist");
		return next_track_id_var;
	}
	uint32 length() {
		assert_cond(length_exists, "struct field length does not exist");
		return length_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}
	uint32 num_entries() {
		assert_cond(num_entries_exists, "struct field num_entries does not exist");
		return num_entries_var;
	}
	std::vector<uint32> track_IDs() {
		assert_cond(track_IDs_exists, "struct field track_IDs does not exist");
		return track_IDs_var;
	}
	uint32 track_id() {
		assert_cond(track_id_exists, "struct field track_id does not exist");
		return track_id_var;
	}
	uint16 layer() {
		assert_cond(layer_exists, "struct field layer does not exist");
		return layer_var;
	}
	uint16 alt_group() {
		assert_cond(alt_group_exists, "struct field alt_group does not exist");
		return alt_group_var;
	}
	fp16& volume() {
		assert_cond(volume_exists, "struct field volume does not exist");
		return *volume_var;
	}
	uint16 reserved3() {
		assert_cond(reserved3_exists, "struct field reserved3 does not exist");
		return reserved3_var;
	}
	fp32& width() {
		assert_cond(width_exists, "struct field width does not exist");
		return *width_var;
	}
	fp32& height() {
		assert_cond(height_exists, "struct field height does not exist");
		return *height_var;
	}
	uint16 quality() {
		assert_cond(quality_exists, "struct field quality does not exist");
		return quality_var;
	}
	fourcc& subtype() {
		assert_cond(subtype_exists, "struct field subtype does not exist");
		return *subtype_var;
	}
	uint32 mfr() {
		assert_cond(mfr_exists, "struct field mfr does not exist");
		return mfr_var;
	}
	uint32 flags_mask() {
		assert_cond(flags_mask_exists, "struct field flags_mask does not exist");
		return flags_mask_var;
	}
	std::string rest() {
		assert_cond(rest_exists, "struct field rest does not exist");
		return rest_var;
	}
	std::string flag() {
		assert_cond(flag_exists, "struct field flag does not exist");
		return flag_var;
	}
	uint32 entry_count_1() {
		assert_cond(entry_count_1_exists, "struct field entry_count_1 does not exist");
		return entry_count_1_var;
	}
	uint32 t() {
		assert_cond(t_exists, "struct field t does not exist");
		return t_var;
	}
	uint32 entry_count_2() {
		assert_cond(entry_count_2_exists, "struct field entry_count_2 does not exist");
		return entry_count_2_var;
	}
	std::vector<elst_entry*> entries() {
		assert_cond(entries_exists, "struct field entries does not exist");
		return entries_var;
	}
	std::string notice() {
		assert_cond(notice_exists, "struct field notice does not exist");
		return notice_var;
	}
	uint16 entry_count_3() {
		assert_cond(entry_count_3_exists, "struct field entry_count_3 does not exist");
		return entry_count_3_var;
	}
	uint16 item_ID() {
		assert_cond(item_ID_exists, "struct field item_ID does not exist");
		return item_ID_var;
	}
	uint16 item_protection_index() {
		assert_cond(item_protection_index_exists, "struct field item_protection_index does not exist");
		return item_protection_index_var;
	}
	std::string item_name() {
		assert_cond(item_name_exists, "struct field item_name does not exist");
		return item_name_var;
	}
	std::string content_type() {
		assert_cond(content_type_exists, "struct field content_type does not exist");
		return content_type_var;
	}
	std::string content_encoding() {
		assert_cond(content_encoding_exists, "struct field content_encoding does not exist");
		return content_encoding_var;
	}
	std::string location() {
		assert_cond(location_exists, "struct field location does not exist");
		return location_var;
	}
	std::string name() {
		assert_cond(name_exists, "struct field name does not exist");
		return name_var;
	}
	fp16& balance() {
		assert_cond(balance_exists, "struct field balance does not exist");
		return *balance_var;
	}
	uint16 graphics_mode() {
		assert_cond(graphics_mode_exists, "struct field graphics_mode does not exist");
		return graphics_mode_var;
	}
	qtopcolor& opcolor() {
		assert_cond(opcolor_exists, "struct field opcolor does not exist");
		return *opcolor_var;
	}
	uint32 entry_count_4() {
		assert_cond(entry_count_4_exists, "struct field entry_count_4 does not exist");
		return entry_count_4_var;
	}
	uint32 entry_count_5() {
		assert_cond(entry_count_5_exists, "struct field entry_count_5 does not exist");
		return entry_count_5_var;
	}
	uint32 entry_count_6() {
		assert_cond(entry_count_6_exists, "struct field entry_count_6 does not exist");
		return entry_count_6_var;
	}
	uint32 sample_size() {
		assert_cond(sample_size_exists, "struct field sample_size does not exist");
		return sample_size_var;
	}
	uint32 sample_count() {
		assert_cond(sample_count_exists, "struct field sample_count does not exist");
		return sample_count_var;
	}
	std::vector<uint32> entry_size() {
		assert_cond(entry_size_exists, "struct field entry_size does not exist");
		return entry_size_var;
	}
	uint32 codingName() {
		assert_cond(codingName_exists, "struct field codingName does not exist");
		return codingName_var;
	}
	byte reserved1() {
		assert_cond(reserved1_exists, "struct field reserved1 does not exist");
		return reserved1_var;
	}
	byte default_crypt_skip_byte_block() {
		assert_cond(default_crypt_skip_byte_block_exists, "struct field default_crypt_skip_byte_block does not exist");
		return default_crypt_skip_byte_block_var;
	}
	byte default_is_protected() {
		assert_cond(default_is_protected_exists, "struct field default_is_protected does not exist");
		return default_is_protected_var;
	}
	byte default_per_sample_IV_size() {
		assert_cond(default_per_sample_IV_size_exists, "struct field default_per_sample_IV_size does not exist");
		return default_per_sample_IV_size_var;
	}
	std::string default_KID() {
		assert_cond(default_KID_exists, "struct field default_KID does not exist");
		return default_KID_var;
	}
	byte default_constant_IV_size() {
		assert_cond(default_constant_IV_size_exists, "struct field default_constant_IV_size does not exist");
		return default_constant_IV_size_var;
	}
	std::string default_constant_IV() {
		assert_cond(default_constant_IV_exists, "struct field default_constant_IV does not exist");
		return default_constant_IV_var;
	}
	uint32 scheme_type() {
		assert_cond(scheme_type_exists, "struct field scheme_type does not exist");
		return scheme_type_var;
	}
	uint32 scheme_version() {
		assert_cond(scheme_version_exists, "struct field scheme_version does not exist");
		return scheme_version_var;
	}
	std::string systemID() {
		assert_cond(systemID_exists, "struct field systemID does not exist");
		return systemID_var;
	}
	uint32 KID_count() {
		assert_cond(KID_count_exists, "struct field KID_count does not exist");
		return KID_count_var;
	}
	std::vector<KID_struct*> KID() {
		assert_cond(KID_exists, "struct field KID does not exist");
		return KID_var;
	}
	uint32 DataSize() {
		assert_cond(DataSize_exists, "struct field DataSize does not exist");
		return DataSize_var;
	}
	std::string Data() {
		assert_cond(Data_exists, "struct field Data does not exist");
		return Data_var;
	}
	uint32 aux_info_type() {
		assert_cond(aux_info_type_exists, "struct field aux_info_type does not exist");
		return aux_info_type_var;
	}
	uint32 aud_info_type_parameter() {
		assert_cond(aud_info_type_parameter_exists, "struct field aud_info_type_parameter does not exist");
		return aud_info_type_parameter_var;
	}
	uint32 entry_count_7() {
		assert_cond(entry_count_7_exists, "struct field entry_count_7 does not exist");
		return entry_count_7_var;
	}
	uint32 aux_info_type_parameter() {
		assert_cond(aux_info_type_parameter_exists, "struct field aux_info_type_parameter does not exist");
		return aux_info_type_parameter_var;
	}
	byte default_sample_info_size() {
		assert_cond(default_sample_info_size_exists, "struct field default_sample_info_size does not exist");
		return default_sample_info_size_var;
	}
	uint32 data_offset() {
		assert_cond(data_offset_exists, "struct field data_offset does not exist");
		return data_offset_var;
	}
	uint32 first_sample_flags() {
		assert_cond(first_sample_flags_exists, "struct field first_sample_flags does not exist");
		return first_sample_flags_var;
	}
	uint32 trackID() {
		assert_cond(trackID_exists, "struct field trackID does not exist");
		return trackID_var;
	}
	uint64 base_data_offset() {
		assert_cond(base_data_offset_exists, "struct field base_data_offset does not exist");
		return base_data_offset_var;
	}
	uint32 sample_description_index() {
		assert_cond(sample_description_index_exists, "struct field sample_description_index does not exist");
		return sample_description_index_var;
	}
	uint32 default_sample_duration() {
		assert_cond(default_sample_duration_exists, "struct field default_sample_duration does not exist");
		return default_sample_duration_var;
	}
	uint32 default_sample_size() {
		assert_cond(default_sample_size_exists, "struct field default_sample_size does not exist");
		return default_sample_size_var;
	}
	uint32 default_sample_flags() {
		assert_cond(default_sample_flags_exists, "struct field default_sample_flags does not exist");
		return default_sample_flags_var;
	}
	uint32 sequence_number() {
		assert_cond(sequence_number_exists, "struct field sequence_number does not exist");
		return sequence_number_var;
	}
	uint32 referenceID() {
		assert_cond(referenceID_exists, "struct field referenceID does not exist");
		return referenceID_var;
	}
	uint32 timescale() {
		assert_cond(timescale_exists, "struct field timescale does not exist");
		return timescale_var;
	}
	uint16 reference_count() {
		assert_cond(reference_count_exists, "struct field reference_count does not exist");
		return reference_count_var;
	}
	std::vector<str_sidx*> references() {
		assert_cond(references_exists, "struct field references does not exist");
		return references_var;
	}
	uint32 default_sample_description_index() {
		assert_cond(default_sample_description_index_exists, "struct field default_sample_description_index does not exist");
		return default_sample_description_index_var;
	}
	uint32 entry_count_8() {
		assert_cond(entry_count_8_exists, "struct field entry_count_8 does not exist");
		return entry_count_8_var;
	}
	uint32 entry_count_9() {
		assert_cond(entry_count_9_exists, "struct field entry_count_9 does not exist");
		return entry_count_9_var;
	}
	std::vector<uint32> sample_number() {
		assert_cond(sample_number_exists, "struct field sample_number does not exist");
		return sample_number_var;
	}

	/* locals */
	uint64 startOffset;
	int64 endOffset;
	uint64 contentsize;
	std::vector<std::string> tmp_s;
	std::string tmp;
	uint32 coinPosition;
	uint64 writePosition;
	uint32 i;
	uint32 newSize;

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	mp4box& operator () () { return *instances.back(); }
	mp4box* operator [] (int index) { return instances[index]; }
	mp4box(std::vector<mp4box*>& instances) : instances(instances) { instances.push_back(this); }
	~mp4box() {
		if (generated == 2)
			return;
		while (instances.size()) {
			mp4box* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	mp4box* generate();
};


class mp4file {
	std::vector<mp4file*>& instances;

	mp4box* box_var;

public:
	bool box_exists = false;

	mp4box& box() {
		assert_cond(box_exists, "struct field box does not exist");
		return *box_var;
	}

	/* locals */
	std::vector<std::string> tmp_s;
	std::string tmp;

	unsigned char generated = 0;
	int64 _startof;
	std::size_t _sizeof;
	mp4file& operator () () { return *instances.back(); }
	mp4file* operator [] (int index) { return instances[index]; }
	mp4file(std::vector<mp4file*>& instances) : instances(instances) { instances.push_back(this); }
	~mp4file() {
		if (generated == 2)
			return;
		while (instances.size()) {
			mp4file* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	mp4file* generate();
};

std::vector<char> ReadByteInitValues;
std::vector<uchar> ReadUByteInitValues;
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


std::vector<fourcc*> fourcc_type_instances;
std::vector<fp32*> fp32_preferred_rate_instances;
std::vector<fp16*> fp16_preferred_volume_instances;
std::vector<fp32*> fp32_a_instances;
std::vector<fp32*> fp32_b_instances;
std::vector<fp32uvw*> fp32uvw_u_instances;
std::vector<fp32*> fp32_c_instances;
std::vector<fp32*> fp32_d_instances;
std::vector<fp32uvw*> fp32uvw_v_instances;
std::vector<fp32*> fp32_x_instances;
std::vector<fp32*> fp32_y_instances;
std::vector<fp32uvw*> fp32uvw_w_instances;
std::vector<matrix*> matrix_matrix_structure_instances;
std::vector<tkhd_flags*> tkhd_flags_flags__instances;
std::vector<fp16*> fp16_volume_instances;
std::vector<fp32*> fp32_width_instances;
std::vector<fp32*> fp32_height_instances;
std::vector<mp4lang*> mp4lang_language_instances;
std::vector<fourcc*> fourcc_subtype_instances;
std::vector<str_stts*> str_stts_entry_element_instances;
std::vector<fp32*> fp32_media_rate_instances;
std::vector<elst_entry*> elst_entry_entries_element_instances;
std::vector<fp16*> fp16_balance_instances;
std::vector<vmhd_flags*> vmhd_flags_flags___instances;
std::vector<qtopcolor*> qtopcolor_opcolor_instances;
std::vector<str_stsc*> str_stsc_entry__element_instances;
std::vector<KID_struct*> KID_struct_KID_element_instances;
std::vector<entry_struct_subsample_data_struct*> entry_struct_subsample_data_struct_subsample_data_element_instances;
std::vector<entry_struct*> entry_struct_entry____element_instances;
std::vector<entry_struct*> entry_struct_entry_____instances;
std::vector<str_sidx*> str_sidx_references_element_instances;
std::vector<mp4box*> mp4box_box_instances;
std::vector<mp4file*> mp4file_file_instances;


class globals_class {
public:
	uint32_class size;
	byte_class value_element;
	byte_array_class value;
	fourcc type;
	char_class major_brand_element;
	char_array_class major_brand;
	uint32_class coin;
	char_class compatiple_brand_element;
	char_array_class compatiple_brand;
	uint32_class minor_version;
	byte_class version;
	byte_class flags_element;
	byte_array_class flags;
	uint32_class create_time;
	uint32_class modify_time;
	uint32_class time_scale;
	uint32_class duration;
	uint64_class create_time_;
	uint64_class modify_time_;
	int32_class value_;
	fp32 preferred_rate;
	int16_class value__;
	fp16 preferred_volume;
	byte_class reserved_element;
	byte_array_class reserved;
	fp32 a;
	fp32 b;
	fp32uvw u;
	fp32 c;
	fp32 d;
	fp32uvw v;
	fp32 x;
	fp32 y;
	fp32uvw w;
	matrix matrix_structure;
	uint32_class preview_time;
	uint32_class preview_duration;
	uint32_class poster_time;
	uint32_class selection_time;
	uint32_class selection_duration;
	uint32_class current_time;
	uint32_class next_track_id;
	uint32_class length;
	byte_class data_element;
	byte_array_class data;
	uint32_class num_entries;
	uint32_class track_IDs_element;
	uint32_array_class track_IDs;
	byte_class dummy_element;
	byte_array_class dummy;
	byte_bitfield dummy2;
	byte_bitfield track_in_poster;
	byte_bitfield track_in_preview;
	byte_bitfield track_in_movie;
	byte_bitfield track_enabled;
	tkhd_flags flags_;
	uint32_class track_id;
	uint32_class reserved_;
	uint64_class duration_;
	uint64_class reserved2;
	uint16_class layer;
	uint16_class alt_group;
	fp16 volume;
	uint16_class reserved3;
	fp32 width;
	fp32 height;
	uint16_class value___;
	mp4lang language;
	uint16_class quality;
	fourcc subtype;
	uint32_class mfr;
	uint32_class flags_mask;
	byte_class rest_element;
	byte_array_class rest;
	byte_class flag_element;
	byte_array_class flag;
	uint32_class entry_count_1;
	uint32_class t;
	uint32_class entry_count_2;
	uint32_class sample_count;
	uint32_class sample_delta;
	str_stts entry_element;
	str_stts_array_class entry;
	uint32_class media_time;
	fp32 media_rate;
	elst_entry entries_element;
	elst_entry_array_class entries;
	uint16_class language__element;
	uint16_array_class language_;
	string_class notice;
	uint16_class entry_count_3;
	uint16_class item_ID;
	uint16_class item_protection_index;
	string_class item_name;
	string_class content_type;
	string_class content_encoding;
	string_class location;
	string_class name;
	fp16 balance;
	uint16_class reserved__;
	byte_class dummy2_;
	vmhd_flags flags__;
	uint16_class red;
	uint16_class green;
	uint16_class blue;
	qtopcolor opcolor;
	uint32_class entry_count_4;
	uint32_class first_chunk;
	uint32_class samples_per_chunk;
	uint32_class sample_description_index;
	str_stsc entry__element;
	str_stsc_array_class entry_;
	uint32_class entry_count_5;
	uint64_class chunk_offset_element;
	uint64_array_class chunk_offset;
	uint32_class entry_count_6;
	uint32_class chunk_offset__element;
	uint32_array_class chunk_offset_;
	uint32_class sample_size;
	uint32_class entry_size_element;
	uint32_array_class entry_size;
	uint32_class codingName;
	byte_class reserved1;
	byte_class reserved2_;
	byte_class default_crypt_skip_byte_block;
	byte_class default_is_protected;
	byte_class default_per_sample_IV_size;
	byte_class default_KID_element;
	byte_array_class default_KID;
	byte_class default_constant_IV_size;
	byte_class default_constant_IV_element;
	byte_array_class default_constant_IV;
	uint32_class scheme_type;
	uint32_class scheme_version;
	byte_class systemID_element;
	byte_array_class systemID;
	uint32_class KID_count;
	byte_class entry___element;
	byte_array_class entry__;
	KID_struct KID_element;
	KID_struct_array_class KID;
	uint32_class DataSize;
	byte_class Data_element;
	byte_array_class Data;
	byte_class per_sample_IV_element;
	byte_array_class per_sample_IV;
	uint16_class subsample_count;
	uint16_class bytes_of_clear_data;
	uint32_class bytes_of_protected_data;
	entry_struct_subsample_data_struct subsample_data_element;
	entry_struct_subsample_data_struct_array_class subsample_data;
	entry_struct entry____element;
	entry_struct_array_class entry___;
	uint32_class aux_info_type;
	uint32_class aud_info_type_parameter;
	uint32_class entry_count_7;
	uint32_class offset_element;
	uint32_array_class offset;
	uint64_class offset__element;
	uint64_array_class offset_;
	uint32_class aux_info_type_parameter;
	byte_class default_sample_info_size;
	uint32_class data_offset;
	uint32_class first_sample_flags;
	uint32_class sample_duration;
	uint32_class sample_flags;
	uint32_class sample_composition_time_offset;
	int32_class sample_composition_time_offset_;
	entry_struct entry____;
	uint32_class trackID;
	uint64_class base_data_offset;
	uint32_class default_sample_duration;
	uint32_class default_sample_size;
	uint32_class default_sample_flags;
	uint32_class sequence_number;
	uint32_class referenceID;
	uint32_class timescale;
	uint32_class earliest_presentation_time;
	uint32_class first_offset;
	uint64_class earliest_presentation_time_;
	uint64_class first_offset_;
	uint16_class reference_count;
	uint32_class reference_size31_type1;
	uint32_class subsegment_duration;
	uint32_class SAP_delta_time28_type3_starts_with1;
	str_sidx references_element;
	str_sidx_array_class references;
	uint32_class default_sample_description_index;
	uint32_class fragment_duration;
	uint64_class fragment_duration_;
	uint32_class entry_count_8;
	uint32_class entry_count_9;
	uint32_class sample_number_element;
	uint32_array_class sample_number;
	mp4box box;
	mp4file file;


	globals_class() :
		size(true),
		value_element(false),
		value(value_element),
		type(fourcc_type_instances),
		major_brand_element(false),
		major_brand(major_brand_element),
		coin(true, { 0 }),
		compatiple_brand_element(false),
		compatiple_brand(compatiple_brand_element),
		minor_version(true),
		version(true, { 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0 }),
		flags_element(false),
		flags(flags_element),
		create_time(true),
		modify_time(true),
		time_scale(true),
		duration(true),
		create_time_(true),
		modify_time_(true),
		value_(true),
		preferred_rate(fp32_preferred_rate_instances),
		value__(true),
		preferred_volume(fp16_preferred_volume_instances),
		reserved_element(false),
		reserved(reserved_element),
		a(fp32_a_instances),
		b(fp32_b_instances),
		u(fp32uvw_u_instances),
		c(fp32_c_instances),
		d(fp32_d_instances),
		v(fp32uvw_v_instances),
		x(fp32_x_instances),
		y(fp32_y_instances),
		w(fp32uvw_w_instances),
		matrix_structure(matrix_matrix_structure_instances),
		preview_time(true),
		preview_duration(true),
		poster_time(true),
		selection_time(true),
		selection_duration(true),
		current_time(true),
		next_track_id(true),
		length(true),
		data_element(false),
		data(data_element),
		num_entries(true),
		track_IDs_element(false),
		track_IDs(track_IDs_element),
		dummy_element(false),
		dummy(dummy_element),
		dummy2(true),
		track_in_poster(true),
		track_in_preview(true),
		track_in_movie(true),
		track_enabled(true),
		flags_(tkhd_flags_flags__instances),
		track_id(true),
		reserved_(true),
		duration_(true),
		reserved2(true),
		layer(true),
		alt_group(true),
		volume(fp16_volume_instances),
		reserved3(true),
		width(fp32_width_instances),
		height(fp32_height_instances),
		value___(true),
		language(mp4lang_language_instances),
		quality(true),
		subtype(fourcc_subtype_instances),
		mfr(true),
		flags_mask(true),
		rest_element(false),
		rest(rest_element),
		flag_element(false),
		flag(flag_element),
		entry_count_1(true),
		t(true),
		entry_count_2(true),
		sample_count(true),
		sample_delta(true),
		entry_element(str_stts_entry_element_instances),
		entry(entry_element),
		media_time(true),
		media_rate(fp32_media_rate_instances),
		entries_element(elst_entry_entries_element_instances),
		entries(entries_element),
		language__element(false),
		language_(language__element),
		entry_count_3(true),
		item_ID(true),
		item_protection_index(true),
		balance(fp16_balance_instances),
		reserved__(true),
		dummy2_(true),
		flags__(vmhd_flags_flags___instances),
		red(true),
		green(true),
		blue(true),
		opcolor(qtopcolor_opcolor_instances),
		entry_count_4(true),
		first_chunk(true),
		samples_per_chunk(true),
		sample_description_index(true),
		entry__element(str_stsc_entry__element_instances),
		entry_(entry__element),
		entry_count_5(true),
		chunk_offset_element(false),
		chunk_offset(chunk_offset_element),
		entry_count_6(true),
		chunk_offset__element(false),
		chunk_offset_(chunk_offset__element),
		sample_size(true, { 0 }),
		entry_size_element(false),
		entry_size(entry_size_element),
		codingName(true),
		reserved1(true),
		reserved2_(true),
		default_crypt_skip_byte_block(true),
		default_is_protected(true),
		default_per_sample_IV_size(true, { 0 }),
		default_KID_element(false),
		default_KID(default_KID_element),
		default_constant_IV_size(true),
		default_constant_IV_element(false),
		default_constant_IV(default_constant_IV_element),
		scheme_type(true),
		scheme_version(true),
		systemID_element(false),
		systemID(systemID_element),
		KID_count(true),
		entry___element(false),
		entry__(entry___element),
		KID_element(KID_struct_KID_element_instances),
		KID(KID_element),
		DataSize(true),
		Data_element(false),
		Data(Data_element),
		per_sample_IV_element(false),
		per_sample_IV(per_sample_IV_element),
		subsample_count(true),
		bytes_of_clear_data(true),
		bytes_of_protected_data(true),
		subsample_data_element(entry_struct_subsample_data_struct_subsample_data_element_instances),
		subsample_data(subsample_data_element),
		entry____element(entry_struct_entry____element_instances),
		entry___(entry____element),
		aux_info_type(true),
		aud_info_type_parameter(true),
		entry_count_7(true),
		offset_element(false),
		offset(offset_element),
		offset__element(false),
		offset_(offset__element),
		aux_info_type_parameter(true),
		default_sample_info_size(true, { 0 }),
		data_offset(true),
		first_sample_flags(true),
		sample_duration(true),
		sample_flags(true),
		sample_composition_time_offset(true),
		sample_composition_time_offset_(true),
		entry____(entry_struct_entry_____instances),
		trackID(true),
		base_data_offset(true),
		default_sample_duration(true),
		default_sample_size(true),
		default_sample_flags(true),
		sequence_number(true),
		referenceID(true),
		timescale(true),
		earliest_presentation_time(true),
		first_offset(true),
		earliest_presentation_time_(true),
		first_offset_(true),
		reference_count(true),
		reference_size31_type1(true),
		subsegment_duration(true),
		SAP_delta_time28_type3_starts_with1(true),
		references_element(str_sidx_references_element_instances),
		references(references_element),
		default_sample_description_index(true),
		fragment_duration(true),
		fragment_duration_(true),
		entry_count_8(true),
		entry_count_9(true),
		sample_number_element(false),
		sample_number(sample_number_element),
		box(mp4box_box_instances),
		file(mp4file_file_instances)
	{}
};

globals_class* g;


fourcc* fourcc::generate() {
	if (generated == 1) {
		fourcc* new_instance = new fourcc(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(value, ::g->value.generate(4, { "dinf", "edts", "mdia", "minf", "moov", "moof", "stbl", "trak", "udta", "traf", "mvex", "sinf", "schi", "frma", "tenc", "schm", "pssh", "senc", "saio", "saiz", "trun", "tfhd", "mfhd", "sidx", "trex", "mehd", "stsd", "enca", "stts", "stsc", "stco", "co64", "stsz", "stss", "elst", "ftyp", "hdlr", "mdhd", "mvhd", "smhd", "tkhd", "vmhd" }));
	return this;
}


fp32* fp32::generate() {
	if (generated == 1) {
		fp32* new_instance = new fp32(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(value, ::g->value_.generate());
	return this;
}


fp16* fp16::generate() {
	if (generated == 1) {
		fp16* new_instance = new fp16(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(value, ::g->value__.generate());
	return this;
}


fp32uvw* fp32uvw::generate() {
	if (generated == 1) {
		fp32uvw* new_instance = new fp32uvw(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(value, ::g->value_.generate());
	return this;
}


matrix* matrix::generate() {
	if (generated == 1) {
		matrix* new_instance = new matrix(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(a, ::g->a.generate());
	GENERATE_VAR(b, ::g->b.generate());
	GENERATE_VAR(u, ::g->u.generate());
	GENERATE_VAR(c, ::g->c.generate());
	GENERATE_VAR(d, ::g->d.generate());
	GENERATE_VAR(v, ::g->v.generate());
	GENERATE_VAR(x, ::g->x.generate());
	GENERATE_VAR(y, ::g->y.generate());
	GENERATE_VAR(w, ::g->w.generate());
	return this;
}


tkhd_flags* tkhd_flags::generate() {
	if (generated == 1) {
		tkhd_flags* new_instance = new tkhd_flags(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(dummy, ::g->dummy.generate(2));
	GENERATE_VAR(dummy2, ::g->dummy2.generate(4));
	GENERATE_VAR(track_in_poster, ::g->track_in_poster.generate(1));
	GENERATE_VAR(track_in_preview, ::g->track_in_preview.generate(1));
	GENERATE_VAR(track_in_movie, ::g->track_in_movie.generate(1));
	GENERATE_VAR(track_enabled, ::g->track_enabled.generate(1));
	return this;
}


mp4lang* mp4lang::generate() {
	if (generated == 1) {
		mp4lang* new_instance = new mp4lang(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(value, ::g->value___.generate());
	return this;
}


str_stts* str_stts::generate() {
	if (generated == 1) {
		str_stts* new_instance = new str_stts(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(sample_count, ::g->sample_count.generate());
	GENERATE_VAR(sample_delta, ::g->sample_delta.generate());
	return this;
}


elst_entry* elst_entry::generate() {
	if (generated == 1) {
		elst_entry* new_instance = new elst_entry(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(duration, ::g->duration.generate());
	GENERATE_VAR(media_time, ::g->media_time.generate());
	GENERATE_VAR(media_rate, ::g->media_rate.generate());
	return this;
}


vmhd_flags* vmhd_flags::generate() {
	if (generated == 1) {
		vmhd_flags* new_instance = new vmhd_flags(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(dummy, ::g->dummy.generate(2));
	GENERATE_VAR(dummy2, ::g->dummy2_.generate({ 1 }));
	return this;
}


qtopcolor* qtopcolor::generate() {
	if (generated == 1) {
		qtopcolor* new_instance = new qtopcolor(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(red, ::g->red.generate());
	GENERATE_VAR(green, ::g->green.generate());
	GENERATE_VAR(blue, ::g->blue.generate());
	return this;
}


str_stsc* str_stsc::generate() {
	if (generated == 1) {
		str_stsc* new_instance = new str_stsc(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(first_chunk, ::g->first_chunk.generate());
	GENERATE_VAR(samples_per_chunk, ::g->samples_per_chunk.generate());
	GENERATE_VAR(sample_description_index, ::g->sample_description_index.generate());
	return this;
}


KID_struct* KID_struct::generate() {
	if (generated == 1) {
		KID_struct* new_instance = new KID_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(entry, ::g->entry__.generate(16));
	return this;
}


entry_struct_subsample_data_struct* entry_struct_subsample_data_struct::generate() {
	if (generated == 1) {
		entry_struct_subsample_data_struct* new_instance = new entry_struct_subsample_data_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(bytes_of_clear_data, ::g->bytes_of_clear_data.generate());
	GENERATE_VAR(bytes_of_protected_data, ::g->bytes_of_protected_data.generate());
	return this;
}


entry_struct* entry_struct::generate() {
	if (generated == 1) {
		entry_struct* new_instance = new entry_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(per_sample_IV, ::g->per_sample_IV.generate(8));
	if ((::g->flag()[2] == 2)) {
		GENERATE_VAR(subsample_count, ::g->subsample_count.generate());
		GENERATE_VAR(subsample_data, ::g->subsample_data.generate(subsample_count()));
	};
	return this;
}


str_sidx* str_sidx::generate() {
	if (generated == 1) {
		str_sidx* new_instance = new str_sidx(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	GENERATE_VAR(reference_size31_type1, ::g->reference_size31_type1.generate());
	GENERATE_VAR(subsegment_duration, ::g->subsegment_duration.generate());
	GENERATE_VAR(SAP_delta_time28_type3_starts_with1, ::g->SAP_delta_time28_type3_starts_with1.generate());
	return this;
}


mp4box* mp4box::generate() {
	if (generated == 1) {
		mp4box* new_instance = new mp4box(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	startOffset = FTell();
	GENERATE_VAR(size, ::g->size.generate());
	GENERATE_VAR(type, ::g->type.generate());
	endOffset = (startOffset + size());
	contentsize = (size() - 8);
	printf("start %llu type %s\n", startOffset, type().value().c_str());
	
	switch (STR2INT(type().value())) {
	case STR2INT("moof"):
	case STR2INT("traf"):
	case STR2INT("mvex"):
	case STR2INT("sinf"):
	case STR2INT("schi"):
		while ((FTell() < endOffset)) {
			GENERATE_VAR(box, ::g->box.generate());
			FSeek(box().endOffset);
		};
		break;
	case STR2INT("moov"):
		tmp_s = { "mvhd" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "iods" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "trak" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "udta" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "meta" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("ftyp"):
		GENERATE_VAR(major_brand, ::g->major_brand.generate(4, { {"avc1"}, {"iso2"}, {"isom"}, {"mmp4"}, {"mp41"}, {"mp42"}, {"mp71"}, {"msnv"}, {"ndas"}, {"ndsc"}, {"ndsh"}, {"ndsm"}, {"ndsp"}, {"ndss"}, {"ndxc"}, {"ndxh"}, {"ndxm"}, {"ndxp"}, {"ndxs"} }));
		coinPosition = FTell();
		GENERATE_VAR(coin, ::g->coin.generate({ 0, 1, 2, 3 }));
		writePosition = FTell();
		while (true) {
			GENERATE_VAR(compatiple_brand, ::g->compatiple_brand.generate(4, { {"avc1"}, {"iso2"}, {"isom"}, {"mmp4"}, {"mp41"}, {"mp42"}, {"mp71"}, {"msnv"}, {"ndas"}, {"ndsc"}, {"ndsh"}, {"ndsm"}, {"ndsp"}, {"ndss"}, {"ndxc"}, {"ndxh"}, {"ndxm"}, {"ndxp"}, {"ndxs"} }));
			writePosition = (writePosition + 4);
			if ((coin() == 0)) {
				FSeek(coinPosition);
				GENERATE_VAR(minor_version, ::g->minor_version.generate());
				FSeek(writePosition);
				break;
			};
			FSeek(coinPosition);
			GENERATE_VAR(coin, ::g->coin.generate({ 0, 1 }));
			FSeek(writePosition);
		};
		break;
	case STR2INT("mvhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags.generate(3));
		if ((version() == 0)) {
			GENERATE(create_time, ::g->create_time.generate());
			GENERATE(modify_time, ::g->modify_time.generate());
			GENERATE_VAR(time_scale, ::g->time_scale.generate());
			GENERATE(duration, ::g->duration.generate());
		};
		if ((version() == 1)) {
			GENERATE(create_time, ::g->create_time_.generate());
			GENERATE(modify_time, ::g->modify_time_.generate());
			GENERATE_VAR(time_scale, ::g->time_scale.generate());
			GENERATE(duration, ::g->duration.generate());
		};
		GENERATE_VAR(preferred_rate, ::g->preferred_rate.generate());
		GENERATE_VAR(preferred_volume, ::g->preferred_volume.generate());
		GENERATE(reserved, ::g->reserved.generate(10));
		GENERATE_VAR(matrix_structure, ::g->matrix_structure.generate());
		GENERATE_VAR(preview_time, ::g->preview_time.generate());
		GENERATE_VAR(preview_duration, ::g->preview_duration.generate());
		GENERATE_VAR(poster_time, ::g->poster_time.generate());
		GENERATE_VAR(selection_time, ::g->selection_time.generate());
		GENERATE_VAR(selection_duration, ::g->selection_duration.generate());
		GENERATE_VAR(current_time, ::g->current_time.generate());
		GENERATE_VAR(next_track_id, ::g->next_track_id.generate());
		break;
	case STR2INT("mdat"):
		GENERATE_VAR(length, ::g->length.generate());
		GENERATE_VAR(data, ::g->data.generate(length()));
		break;
	case STR2INT("iods"):
		GENERATE_VAR(num_entries, ::g->num_entries.generate());
		FSeek((FTell() - 4));
		GENERATE_VAR(track_IDs, ::g->track_IDs.generate(num_entries()));
		break;
	case STR2INT("tref"):
		GENERATE_VAR(num_entries, ::g->num_entries.generate());
		FSeek((FTell() - 4));
		GENERATE_VAR(track_IDs, ::g->track_IDs.generate(num_entries()));
		break;
	case STR2INT("trak"):
		tmp_s = { "tkhd" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "tref" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "mdia" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "edts" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "udta" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "meta" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("tkhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags_.generate());
		if ((version() == 1)) {
			GENERATE(create_time, ::g->create_time_.generate());
			GENERATE(modify_time, ::g->modify_time_.generate());
			GENERATE_VAR(track_id, ::g->track_id.generate());
			GENERATE(reserved, ::g->reserved_.generate());
			GENERATE(duration, ::g->duration_.generate());
		};
		if ((version() == 0)) {
			GENERATE(create_time, ::g->create_time.generate());
			GENERATE(modify_time, ::g->modify_time.generate());
			GENERATE_VAR(track_id, ::g->track_id.generate());
			GENERATE(reserved, ::g->reserved_.generate());
			GENERATE(duration, ::g->duration.generate());
		};
		GENERATE(reserved2, ::g->reserved2.generate());
		GENERATE_VAR(layer, ::g->layer.generate());
		GENERATE_VAR(alt_group, ::g->alt_group.generate());
		GENERATE_VAR(volume, ::g->volume.generate());
		GENERATE_VAR(reserved3, ::g->reserved3.generate());
		GENERATE_VAR(matrix_structure, ::g->matrix_structure.generate());
		GENERATE_VAR(width, ::g->width.generate());
		GENERATE_VAR(height, ::g->height.generate());
		break;
	case STR2INT("mdia"):
		tmp_s = { "mdhd" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "hdlr" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "minf" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("mdhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags.generate(3));
		if ((version() == 1)) {
			GENERATE(create_time, ::g->create_time_.generate());
			GENERATE(modify_time, ::g->modify_time_.generate());
			GENERATE_VAR(time_scale, ::g->time_scale.generate());
			GENERATE(duration, ::g->duration_.generate());
		};
		if ((version() == 0)) {
			GENERATE(create_time, ::g->create_time.generate());
			GENERATE(modify_time, ::g->modify_time.generate());
			GENERATE_VAR(time_scale, ::g->time_scale.generate());
			GENERATE(duration, ::g->duration.generate());
		};
		GENERATE(language, ::g->language.generate());
		GENERATE_VAR(quality, ::g->quality.generate());
		break;
	case STR2INT("hdlr"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags.generate(3));
		GENERATE_VAR(type, ::g->type.generate());
		GENERATE_VAR(subtype, ::g->subtype.generate());
		GENERATE_VAR(mfr, ::g->mfr.generate());
		GENERATE_VAR(flags_mask, ::g->flags_mask.generate());
		GENERATE_VAR(rest, ::g->rest.generate((contentsize - (FTell() - ::g->version._startof))));
		break;
	case STR2INT("edts"):
		tmp_s = { "elst" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("udta"):
		tmp_s = { "cprt" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("meta"):
		tmp_s = { "hdlr" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "iinf" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "dinf" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("minf"):
		tmp_s = { "vmhd", "smhd" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "dinf" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "stbl" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("stbl"):
		tmp_s = { "stts" };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "stsd" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "stsc" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "stsz" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		tmp_s = { "co64", "stco" };
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("stsd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_1, ::g->entry_count_1.generate());
		;
		for (i = 0; (i < entry_count_1()); i++) {
			GENERATE_VAR(t, ::g->t.generate({ 0, 1, 2 }));
			FSeek((FTell() - 4));
			switch (t()) {
			case 0:
				break;
			case 1:
				break;
			case 2:
				break;
			};
		};
		break;
	case STR2INT("stts"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_2, ::g->entry_count_2.generate());
		GENERATE(entry, ::g->entry.generate(entry_count_2()));
		break;
	case STR2INT("elst"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags.generate(3));
		GENERATE_VAR(num_entries, ::g->num_entries.generate());
		GENERATE_VAR(entries, ::g->entries.generate(num_entries()));
		break;
	case STR2INT("cprt"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(language, ::g->language_.generate(3));
		GENERATE_VAR(notice, ::g->notice.generate());
		break;
	case STR2INT("iinf"):
		GENERATE_VAR(entry_count_3, ::g->entry_count_3.generate());
		;
		for (i = 0; (i < entry_count_3()); i++) {
			GENERATE_VAR(item_ID, ::g->item_ID.generate({ (uint16)i }));
			GENERATE_VAR(item_protection_index, ::g->item_protection_index.generate());
			GENERATE_VAR(item_name, ::g->item_name.generate());
			GENERATE_VAR(content_type, ::g->content_type.generate());
			GENERATE_VAR(content_encoding, ::g->content_encoding.generate());
		};
		break;
	case STR2INT("dinf"):
		tmp_s = { "url ", "urn " };
		;
		ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
		GENERATE_VAR(box, ::g->box.generate());
		break;
	case STR2INT("url "):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(location, ::g->location.generate());
		break;
	case STR2INT("urn "):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(name, ::g->name.generate());
		GENERATE_VAR(location, ::g->location.generate());
		break;
	case STR2INT("smhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags.generate(3));
		GENERATE_VAR(balance, ::g->balance.generate());
		GENERATE(reserved, ::g->reserved__.generate());
		break;
	case STR2INT("vmhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE(flags, ::g->flags__.generate());
		GENERATE_VAR(graphics_mode, qtgfxmode_generate());
		GENERATE_VAR(opcolor, ::g->opcolor.generate());
		break;
	case STR2INT("stsc"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_4, ::g->entry_count_4.generate());
		GENERATE(entry, ::g->entry_.generate(entry_count_4()));
		break;
	case STR2INT("co64"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_5, ::g->entry_count_5.generate());
		GENERATE(chunk_offset, ::g->chunk_offset.generate(entry_count_5()));
		break;
	case STR2INT("stco"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_6, ::g->entry_count_6.generate());
		GENERATE(chunk_offset, ::g->chunk_offset_.generate(entry_count_6()));
		break;
	case STR2INT("stsz"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(sample_size, ::g->sample_size.generate());
		GENERATE_VAR(sample_count, ::g->sample_count.generate());
		if ((sample_size() == 0)) {
			GENERATE_VAR(entry_size, ::g->entry_size.generate(sample_count()));
		};
		break;
	case STR2INT("frma"):
		GENERATE_VAR(codingName, ::g->codingName.generate());
		break;
	case STR2INT("tenc"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(reserved1, ::g->reserved1.generate());
		if ((version() == 0)) {
			GENERATE(reserved2, ::g->reserved2_.generate());
		} else {
			GENERATE_VAR(default_crypt_skip_byte_block, ::g->default_crypt_skip_byte_block.generate());
		};
		GENERATE_VAR(default_is_protected, ::g->default_is_protected.generate());
		GENERATE_VAR(default_per_sample_IV_size, ::g->default_per_sample_IV_size.generate());
		GENERATE_VAR(default_KID, ::g->default_KID.generate(16));
		if ((0 == default_per_sample_IV_size())) {
			GENERATE_VAR(default_constant_IV_size, ::g->default_constant_IV_size.generate());
			GENERATE_VAR(default_constant_IV, ::g->default_constant_IV.generate(default_constant_IV_size()));
		};
		break;
	case STR2INT("schm"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(scheme_type, ::g->scheme_type.generate());
		GENERATE_VAR(scheme_version, ::g->scheme_version.generate());
		break;
	case STR2INT("pssh"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(systemID, ::g->systemID.generate(16));
		if ((version() > 0)) {
			GENERATE_VAR(KID_count, ::g->KID_count.generate());
			GENERATE_VAR(KID, ::g->KID.generate(KID_count()));
		};
		GENERATE_VAR(DataSize, ::g->DataSize.generate());
		GENERATE_VAR(Data, ::g->Data.generate(DataSize()));
		break;
	case STR2INT("senc"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(sample_count, ::g->sample_count.generate());
		GENERATE(entry, ::g->entry___.generate(sample_count()));
		break;
	case STR2INT("saio"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		if (((flag()[2] & 1) != 0)) {
			GENERATE_VAR(aux_info_type, ::g->aux_info_type.generate());
			GENERATE_VAR(aud_info_type_parameter, ::g->aud_info_type_parameter.generate());
		};
		GENERATE_VAR(entry_count_7, ::g->entry_count_7.generate());
		if ((version() == 0)) {
			GENERATE(offset, ::g->offset.generate(entry_count_7()));
		} else {
			GENERATE(offset, ::g->offset_.generate(entry_count_7()));
		};
		break;
	case STR2INT("saiz"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		if (((flag()[2] & 1) != 0)) {
			GENERATE_VAR(aux_info_type, ::g->aux_info_type.generate());
			GENERATE_VAR(aux_info_type_parameter, ::g->aux_info_type_parameter.generate());
		};
		GENERATE_VAR(default_sample_info_size, ::g->default_sample_info_size.generate());
		GENERATE_VAR(sample_count, ::g->sample_count.generate());
		if ((default_sample_info_size() == 0)) {
			GENERATE(entry, ::g->entry__.generate(sample_count()));
		};
		break;
	case STR2INT("trun"):
		;
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(sample_count, ::g->sample_count.generate());
		if (((flag()[2] & 1) != 0)) {
			GENERATE_VAR(data_offset, ::g->data_offset.generate());
		};
		if (((flag()[2] & 4) != 0)) {
			GENERATE_VAR(first_sample_flags, ::g->first_sample_flags.generate());
		};
		for (i = 0; (i < sample_count()); i++) {
			GENERATE(entry, ::g->entry____.generate());
		};
		break;
	case STR2INT("tfhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(trackID, ::g->trackID.generate());
		if ((0 != (flag()[2] & 1))) {
			GENERATE_VAR(base_data_offset, ::g->base_data_offset.generate());
		};
		if ((0 != (flag()[2] & 2))) {
			GENERATE_VAR(sample_description_index, ::g->sample_description_index.generate());
		};
		if ((0 != (flag()[2] & 8))) {
			GENERATE_VAR(default_sample_duration, ::g->default_sample_duration.generate());
		};
		if ((0 != (flag()[2] & 0x10))) {
			GENERATE_VAR(default_sample_size, ::g->default_sample_size.generate());
		};
		if ((0 != (flag()[2] & 0x20))) {
			GENERATE_VAR(default_sample_flags, ::g->default_sample_flags.generate());
		};
		break;
	case STR2INT("mfhd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(sequence_number, ::g->sequence_number.generate());
		break;
	case STR2INT("sidx"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(referenceID, ::g->referenceID.generate());
		GENERATE_VAR(timescale, ::g->timescale.generate());
		if ((version() == 0)) {
			GENERATE(earliest_presentation_time, ::g->earliest_presentation_time.generate());
			GENERATE(first_offset, ::g->first_offset.generate());
		} else {
			GENERATE(earliest_presentation_time, ::g->earliest_presentation_time_.generate());
			GENERATE(first_offset, ::g->first_offset_.generate());
		};
		GENERATE(reserved, ::g->reserved__.generate());
		GENERATE_VAR(reference_count, ::g->reference_count.generate());
		GENERATE_VAR(references, ::g->references.generate(reference_count()));
		break;
	case STR2INT("trex"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(trackID, ::g->trackID.generate());
		GENERATE_VAR(default_sample_description_index, ::g->default_sample_description_index.generate());
		GENERATE_VAR(default_sample_duration, ::g->default_sample_duration.generate());
		GENERATE_VAR(default_sample_size, ::g->default_sample_size.generate());
		GENERATE_VAR(default_sample_flags, ::g->default_sample_flags.generate());
		break;
	case STR2INT("mehd"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		if ((version() == 0)) {
			GENERATE(fragment_duration, ::g->fragment_duration.generate());
		} else {
			GENERATE(fragment_duration, ::g->fragment_duration_.generate());
		};
		break;
	case STR2INT("enca"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_8, ::g->entry_count_8.generate());
		GENERATE_VAR(data, ::g->data.generate(0x14));
		break;
	case STR2INT("stss"):
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(flag, ::g->flag.generate(3));
		GENERATE_VAR(entry_count_9, ::g->entry_count_9.generate());
		GENERATE_VAR(sample_number, ::g->sample_number.generate(entry_count_9()));
		break;
	default:
		FSkip(contentsize);
		break;
	};
	writePosition = FTell();
	//printf("write %llu start %llu type %s\n", writePosition, startOffset, type().value().c_str());

	FSeek(startOffset);
	newSize = (writePosition - startOffset);
	GENERATE_VAR(size, ::g->size.generate({ newSize }));
	FSeek(writePosition);
	return this;
}


mp4file* mp4file::generate() {
	if (generated == 1) {
		mp4file* new_instance = new mp4file(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;

	tmp_s = { "ftyp" };
	ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
	GENERATE_VAR(box, ::g->box.generate());
	tmp_s = { "mdat" };
	ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
	GENERATE_VAR(box, ::g->box.generate());
	tmp_s = { "moov" };
	ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
	GENERATE_VAR(box, ::g->box.generate());
	tmp_s = { "free" };
	ReadBytes(tmp, (FTell() + 4), 4, tmp_s);
	GENERATE_VAR(box, ::g->box.generate());
	return this;
}



void generate_file() {
	::g = new globals_class();
	BigEndian();
	GENERATE(file, ::g->file.generate());
	delete_globals();
}

void delete_globals() { delete ::g; }

