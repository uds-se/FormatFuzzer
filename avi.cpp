#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"

enum VIDEO_FORMAT_enum : DWORD {
	FORMAT_UNKNOWN,
	FORMAT_PAL_SQUARE,
	FORMAT_PAL_CCTR_601,
	FORMAT_NTSC_SQUARE,
	FORMAT_NTSC_CCTR_601,
};
std::vector<DWORD> VIDEO_FORMAT_enum_values = { FORMAT_UNKNOWN, FORMAT_PAL_SQUARE, FORMAT_PAL_CCTR_601, FORMAT_NTSC_SQUARE, FORMAT_NTSC_CCTR_601 };

typedef enum VIDEO_FORMAT_enum VIDEO_FORMAT;
std::vector<DWORD> VIDEO_FORMAT_values = { FORMAT_UNKNOWN, FORMAT_PAL_SQUARE, FORMAT_PAL_CCTR_601, FORMAT_NTSC_SQUARE, FORMAT_NTSC_CCTR_601 };

enum VIDEO_STANDARD_enum : DWORD {
	STANDARD_UNKNOWN,
	STANDARD_PAL,
	STANDARD_NTSC,
	STANDARD_SECAM,
};
std::vector<DWORD> VIDEO_STANDARD_enum_values = { STANDARD_UNKNOWN, STANDARD_PAL, STANDARD_NTSC, STANDARD_SECAM };

typedef enum VIDEO_STANDARD_enum VIDEO_STANDARD;
std::vector<DWORD> VIDEO_STANDARD_values = { STANDARD_UNKNOWN, STANDARD_PAL, STANDARD_NTSC, STANDARD_SECAM };


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
	char operator [] (int index) { return value[index]; }
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



class ROOT {
	std::vector<ROOT*>& instances;

	std::string id_var;
	uint32 root_datalen_var;
	std::string form_var;

public:
	bool id_exists = false;
	bool root_datalen_exists = false;
	bool form_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 root_datalen() {
		assert_cond(root_datalen_exists, "struct field root_datalen does not exist");
		return root_datalen_var;
	}
	std::string form() {
		assert_cond(form_exists, "struct field form does not exist");
		return form_var;
	}

	/* locals */
	uint root_datalen_pos;
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ROOT& operator () () { return *instances.back(); }
	ROOT* operator [] (int index) { return instances[index]; }
	ROOT(std::vector<ROOT*>& instances) : instances(instances) { instances.push_back(this); }
	~ROOT() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ROOT* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ROOT* generate();
};



class DWORD_class {
	int small;
	std::vector<DWORD> known_values;
	DWORD value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(DWORD);
	DWORD operator () () { return value; }
	DWORD_class(int small, std::vector<DWORD> known_values = {}) : small(small), known_values(known_values) {}

	DWORD generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(DWORD), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(DWORD), 0, known_values);
		}
		return value;
	}

	DWORD generate(std::vector<DWORD> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(DWORD), 0, possible_values);
		return value;
	}
};



class MainAVIHeader {
	std::vector<MainAVIHeader*>& instances;

	DWORD dwMicroSecPerFrame_var;
	DWORD dwMaxBytesPerSec_var;
	DWORD dwReserved1_var;
	DWORD dwFlags_var;
	DWORD dwTotalFrames_var;
	DWORD dwInitialFrames_var;
	DWORD dwStreams_var;
	DWORD dwSuggestedBufferSize_var;
	DWORD dwWidth_var;
	DWORD dwHeight_var;
	DWORD dwScale_var;
	DWORD dwRate_var;
	DWORD dwStart_var;
	DWORD dwLength_var;

public:
	bool dwMicroSecPerFrame_exists = false;
	bool dwMaxBytesPerSec_exists = false;
	bool dwReserved1_exists = false;
	bool dwFlags_exists = false;
	bool dwTotalFrames_exists = false;
	bool dwInitialFrames_exists = false;
	bool dwStreams_exists = false;
	bool dwSuggestedBufferSize_exists = false;
	bool dwWidth_exists = false;
	bool dwHeight_exists = false;
	bool dwScale_exists = false;
	bool dwRate_exists = false;
	bool dwStart_exists = false;
	bool dwLength_exists = false;

	DWORD dwMicroSecPerFrame() {
		assert_cond(dwMicroSecPerFrame_exists, "struct field dwMicroSecPerFrame does not exist");
		return dwMicroSecPerFrame_var;
	}
	DWORD dwMaxBytesPerSec() {
		assert_cond(dwMaxBytesPerSec_exists, "struct field dwMaxBytesPerSec does not exist");
		return dwMaxBytesPerSec_var;
	}
	DWORD dwReserved1() {
		assert_cond(dwReserved1_exists, "struct field dwReserved1 does not exist");
		return dwReserved1_var;
	}
	DWORD dwFlags() {
		assert_cond(dwFlags_exists, "struct field dwFlags does not exist");
		return dwFlags_var;
	}
	DWORD dwTotalFrames() {
		assert_cond(dwTotalFrames_exists, "struct field dwTotalFrames does not exist");
		return dwTotalFrames_var;
	}
	DWORD dwInitialFrames() {
		assert_cond(dwInitialFrames_exists, "struct field dwInitialFrames does not exist");
		return dwInitialFrames_var;
	}
	DWORD dwStreams() {
		assert_cond(dwStreams_exists, "struct field dwStreams does not exist");
		return dwStreams_var;
	}
	DWORD dwSuggestedBufferSize() {
		assert_cond(dwSuggestedBufferSize_exists, "struct field dwSuggestedBufferSize does not exist");
		return dwSuggestedBufferSize_var;
	}
	DWORD dwWidth() {
		assert_cond(dwWidth_exists, "struct field dwWidth does not exist");
		return dwWidth_var;
	}
	DWORD dwHeight() {
		assert_cond(dwHeight_exists, "struct field dwHeight does not exist");
		return dwHeight_var;
	}
	DWORD dwScale() {
		assert_cond(dwScale_exists, "struct field dwScale does not exist");
		return dwScale_var;
	}
	DWORD dwRate() {
		assert_cond(dwRate_exists, "struct field dwRate does not exist");
		return dwRate_var;
	}
	DWORD dwStart() {
		assert_cond(dwStart_exists, "struct field dwStart does not exist");
		return dwStart_var;
	}
	DWORD dwLength() {
		assert_cond(dwLength_exists, "struct field dwLength does not exist");
		return dwLength_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MainAVIHeader& operator () () { return *instances.back(); }
	MainAVIHeader* operator [] (int index) { return instances[index]; }
	MainAVIHeader(std::vector<MainAVIHeader*>& instances) : instances(instances) { instances.push_back(this); }
	~MainAVIHeader() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MainAVIHeader* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MainAVIHeader* generate();
};



class avihHEADER {
	std::vector<avihHEADER*>& instances;

	std::string id_var;
	uint32 avi_hdr_datalen_var;
	MainAVIHeader* data_var;

public:
	bool id_exists = false;
	bool avi_hdr_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 avi_hdr_datalen() {
		assert_cond(avi_hdr_datalen_exists, "struct field avi_hdr_datalen does not exist");
		return avi_hdr_datalen_var;
	}
	MainAVIHeader& data() {
		assert_cond(data_exists, "struct field data does not exist");
		return *data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	avihHEADER& operator () () { return *instances.back(); }
	avihHEADER* operator [] (int index) { return instances[index]; }
	avihHEADER(std::vector<avihHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~avihHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			avihHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	avihHEADER* generate();
};



class AVIStreamHeader {
	std::vector<AVIStreamHeader*>& instances;

	std::string fccType_var;
	std::string fccHandler_var;
	DWORD dwFlags_var;
	DWORD dwReserved1_var;
	DWORD dwInitialFrames_var;
	DWORD dwScale_var;
	DWORD dwRate_var;
	DWORD dwStart_var;
	DWORD dwLength_var;
	DWORD dwSuggestedBufferSize_var;
	DWORD dwQuality_var;
	DWORD dwSampleSize_var;
	DWORD xdwQuality_var;
	DWORD xdwSampleSize_var;

public:
	bool fccType_exists = false;
	bool fccHandler_exists = false;
	bool dwFlags_exists = false;
	bool dwReserved1_exists = false;
	bool dwInitialFrames_exists = false;
	bool dwScale_exists = false;
	bool dwRate_exists = false;
	bool dwStart_exists = false;
	bool dwLength_exists = false;
	bool dwSuggestedBufferSize_exists = false;
	bool dwQuality_exists = false;
	bool dwSampleSize_exists = false;
	bool xdwQuality_exists = false;
	bool xdwSampleSize_exists = false;

	std::string fccType() {
		assert_cond(fccType_exists, "struct field fccType does not exist");
		return fccType_var;
	}
	std::string fccHandler() {
		assert_cond(fccHandler_exists, "struct field fccHandler does not exist");
		return fccHandler_var;
	}
	DWORD dwFlags() {
		assert_cond(dwFlags_exists, "struct field dwFlags does not exist");
		return dwFlags_var;
	}
	DWORD dwReserved1() {
		assert_cond(dwReserved1_exists, "struct field dwReserved1 does not exist");
		return dwReserved1_var;
	}
	DWORD dwInitialFrames() {
		assert_cond(dwInitialFrames_exists, "struct field dwInitialFrames does not exist");
		return dwInitialFrames_var;
	}
	DWORD dwScale() {
		assert_cond(dwScale_exists, "struct field dwScale does not exist");
		return dwScale_var;
	}
	DWORD dwRate() {
		assert_cond(dwRate_exists, "struct field dwRate does not exist");
		return dwRate_var;
	}
	DWORD dwStart() {
		assert_cond(dwStart_exists, "struct field dwStart does not exist");
		return dwStart_var;
	}
	DWORD dwLength() {
		assert_cond(dwLength_exists, "struct field dwLength does not exist");
		return dwLength_var;
	}
	DWORD dwSuggestedBufferSize() {
		assert_cond(dwSuggestedBufferSize_exists, "struct field dwSuggestedBufferSize does not exist");
		return dwSuggestedBufferSize_var;
	}
	DWORD dwQuality() {
		assert_cond(dwQuality_exists, "struct field dwQuality does not exist");
		return dwQuality_var;
	}
	DWORD dwSampleSize() {
		assert_cond(dwSampleSize_exists, "struct field dwSampleSize does not exist");
		return dwSampleSize_var;
	}
	DWORD xdwQuality() {
		assert_cond(xdwQuality_exists, "struct field xdwQuality does not exist");
		return xdwQuality_var;
	}
	DWORD xdwSampleSize() {
		assert_cond(xdwSampleSize_exists, "struct field xdwSampleSize does not exist");
		return xdwSampleSize_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	AVIStreamHeader& operator () () { return *instances.back(); }
	AVIStreamHeader* operator [] (int index) { return instances[index]; }
	AVIStreamHeader(std::vector<AVIStreamHeader*>& instances) : instances(instances) { instances.push_back(this); }
	~AVIStreamHeader() {
		if (generated == 2)
			return;
		while (instances.size()) {
			AVIStreamHeader* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	AVIStreamHeader* generate();
};



class strhHEADER {
	std::vector<strhHEADER*>& instances;

	std::string id_var;
	uint32 strh_hdr_datalen_var;
	AVIStreamHeader* data_var;

public:
	bool id_exists = false;
	bool strh_hdr_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 strh_hdr_datalen() {
		assert_cond(strh_hdr_datalen_exists, "struct field strh_hdr_datalen does not exist");
		return strh_hdr_datalen_var;
	}
	AVIStreamHeader& data() {
		assert_cond(data_exists, "struct field data does not exist");
		return *data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	strhHEADER& operator () () { return *instances.back(); }
	strhHEADER* operator [] (int index) { return instances[index]; }
	strhHEADER(std::vector<strhHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~strhHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			strhHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	strhHEADER* generate();
};



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



class BITMAPINFOHEADER {
	std::vector<BITMAPINFOHEADER*>& instances;

	uint32 biSize_var;
	uint32 biWidth_var;
	uint32 biHeight_var;
	uint16 biPlanes_var;
	uint16 biBitCount_var;
	uint32 biCompression_var;
	uint32 biSizeImage_var;
	uint32 biXPelsPerMeter_var;
	uint32 biYPelsPerMeter_var;
	uint32 biClrUsed_var;
	uint32 biClrImportant_var;

public:
	bool biSize_exists = false;
	bool biWidth_exists = false;
	bool biHeight_exists = false;
	bool biPlanes_exists = false;
	bool biBitCount_exists = false;
	bool biCompression_exists = false;
	bool biSizeImage_exists = false;
	bool biXPelsPerMeter_exists = false;
	bool biYPelsPerMeter_exists = false;
	bool biClrUsed_exists = false;
	bool biClrImportant_exists = false;

	uint32 biSize() {
		assert_cond(biSize_exists, "struct field biSize does not exist");
		return biSize_var;
	}
	uint32 biWidth() {
		assert_cond(biWidth_exists, "struct field biWidth does not exist");
		return biWidth_var;
	}
	uint32 biHeight() {
		assert_cond(biHeight_exists, "struct field biHeight does not exist");
		return biHeight_var;
	}
	uint16 biPlanes() {
		assert_cond(biPlanes_exists, "struct field biPlanes does not exist");
		return biPlanes_var;
	}
	uint16 biBitCount() {
		assert_cond(biBitCount_exists, "struct field biBitCount does not exist");
		return biBitCount_var;
	}
	uint32 biCompression() {
		assert_cond(biCompression_exists, "struct field biCompression does not exist");
		return biCompression_var;
	}
	uint32 biSizeImage() {
		assert_cond(biSizeImage_exists, "struct field biSizeImage does not exist");
		return biSizeImage_var;
	}
	uint32 biXPelsPerMeter() {
		assert_cond(biXPelsPerMeter_exists, "struct field biXPelsPerMeter does not exist");
		return biXPelsPerMeter_var;
	}
	uint32 biYPelsPerMeter() {
		assert_cond(biYPelsPerMeter_exists, "struct field biYPelsPerMeter does not exist");
		return biYPelsPerMeter_var;
	}
	uint32 biClrUsed() {
		assert_cond(biClrUsed_exists, "struct field biClrUsed does not exist");
		return biClrUsed_var;
	}
	uint32 biClrImportant() {
		assert_cond(biClrImportant_exists, "struct field biClrImportant does not exist");
		return biClrImportant_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	BITMAPINFOHEADER& operator () () { return *instances.back(); }
	BITMAPINFOHEADER* operator [] (int index) { return instances[index]; }
	BITMAPINFOHEADER(std::vector<BITMAPINFOHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~BITMAPINFOHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			BITMAPINFOHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	BITMAPINFOHEADER* generate();
};



class unsigned_char_class {
	int small;
	std::vector<unsigned char> known_values;
	unsigned char value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(unsigned char);
	unsigned char operator () () { return value; }
	unsigned_char_class(int small, std::vector<unsigned char> known_values = {}) : small(small), known_values(known_values) {}

	unsigned char generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(unsigned char), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(unsigned char), 0, known_values);
		}
		return value;
	}

	unsigned char generate(std::vector<unsigned char> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(unsigned char), 0, possible_values);
		return value;
	}
};



class RGBQUAD {
	std::vector<RGBQUAD*>& instances;

	unsigned char rgbBlue_var;
	unsigned char rgbGreen_var;
	unsigned char rgbRed_var;
	unsigned char rgbReserved_var;

public:
	bool rgbBlue_exists = false;
	bool rgbGreen_exists = false;
	bool rgbRed_exists = false;
	bool rgbReserved_exists = false;

	unsigned char rgbBlue() {
		assert_cond(rgbBlue_exists, "struct field rgbBlue does not exist");
		return rgbBlue_var;
	}
	unsigned char rgbGreen() {
		assert_cond(rgbGreen_exists, "struct field rgbGreen does not exist");
		return rgbGreen_var;
	}
	unsigned char rgbRed() {
		assert_cond(rgbRed_exists, "struct field rgbRed does not exist");
		return rgbRed_var;
	}
	unsigned char rgbReserved() {
		assert_cond(rgbReserved_exists, "struct field rgbReserved does not exist");
		return rgbReserved_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	RGBQUAD& operator () () { return *instances.back(); }
	RGBQUAD* operator [] (int index) { return instances[index]; }
	RGBQUAD(std::vector<RGBQUAD*>& instances) : instances(instances) { instances.push_back(this); }
	~RGBQUAD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			RGBQUAD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	RGBQUAD* generate();
};



class strfHEADER_BIH {
	std::vector<strfHEADER_BIH*>& instances;

	std::string id_var;
	uint32 strf_hdr_bih_datalen_var;
	BITMAPINFOHEADER* bmiHeader_var;
	RGBQUAD* bmiColors_var;
	std::string exData_var;

public:
	bool id_exists = false;
	bool strf_hdr_bih_datalen_exists = false;
	bool bmiHeader_exists = false;
	bool bmiColors_exists = false;
	bool exData_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 strf_hdr_bih_datalen() {
		assert_cond(strf_hdr_bih_datalen_exists, "struct field strf_hdr_bih_datalen does not exist");
		return strf_hdr_bih_datalen_var;
	}
	BITMAPINFOHEADER& bmiHeader() {
		assert_cond(bmiHeader_exists, "struct field bmiHeader does not exist");
		return *bmiHeader_var;
	}
	RGBQUAD& bmiColors() {
		assert_cond(bmiColors_exists, "struct field bmiColors does not exist");
		return *bmiColors_var;
	}
	std::string exData() {
		assert_cond(exData_exists, "struct field exData does not exist");
		return exData_var;
	}

	/* locals */
	int sz;
	uint exDataLen;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	strfHEADER_BIH& operator () () { return *instances.back(); }
	strfHEADER_BIH* operator [] (int index) { return instances[index]; }
	strfHEADER_BIH(std::vector<strfHEADER_BIH*>& instances) : instances(instances) { instances.push_back(this); }
	~strfHEADER_BIH() {
		if (generated == 2)
			return;
		while (instances.size()) {
			strfHEADER_BIH* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	strfHEADER_BIH* generate();
};



class WORD_class {
	int small;
	std::vector<WORD> known_values;
	WORD value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(WORD);
	WORD operator () () { return value; }
	WORD_class(int small, std::vector<WORD> known_values = {}) : small(small), known_values(known_values) {}

	WORD generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(WORD), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(WORD), 0, known_values);
		}
		return value;
	}

	WORD generate(std::vector<WORD> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(WORD), 0, possible_values);
		return value;
	}
};



class WAVEFORMATEX {
	std::vector<WAVEFORMATEX*>& instances;

	WORD wFormatTag_var;
	WORD nChannels_var;
	DWORD nSamplesPerSec_var;
	DWORD nAvgBytesPerSec_var;
	WORD nBlockAlign_var;
	WORD wBitsPerSample_var;
	WORD cbSize_var;

public:
	bool wFormatTag_exists = false;
	bool nChannels_exists = false;
	bool nSamplesPerSec_exists = false;
	bool nAvgBytesPerSec_exists = false;
	bool nBlockAlign_exists = false;
	bool wBitsPerSample_exists = false;
	bool cbSize_exists = false;

	WORD wFormatTag() {
		assert_cond(wFormatTag_exists, "struct field wFormatTag does not exist");
		return wFormatTag_var;
	}
	WORD nChannels() {
		assert_cond(nChannels_exists, "struct field nChannels does not exist");
		return nChannels_var;
	}
	DWORD nSamplesPerSec() {
		assert_cond(nSamplesPerSec_exists, "struct field nSamplesPerSec does not exist");
		return nSamplesPerSec_var;
	}
	DWORD nAvgBytesPerSec() {
		assert_cond(nAvgBytesPerSec_exists, "struct field nAvgBytesPerSec does not exist");
		return nAvgBytesPerSec_var;
	}
	WORD nBlockAlign() {
		assert_cond(nBlockAlign_exists, "struct field nBlockAlign does not exist");
		return nBlockAlign_var;
	}
	WORD wBitsPerSample() {
		assert_cond(wBitsPerSample_exists, "struct field wBitsPerSample does not exist");
		return wBitsPerSample_var;
	}
	WORD cbSize() {
		assert_cond(cbSize_exists, "struct field cbSize does not exist");
		return cbSize_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	WAVEFORMATEX& operator () () { return *instances.back(); }
	WAVEFORMATEX* operator [] (int index) { return instances[index]; }
	WAVEFORMATEX(std::vector<WAVEFORMATEX*>& instances) : instances(instances) { instances.push_back(this); }
	~WAVEFORMATEX() {
		if (generated == 2)
			return;
		while (instances.size()) {
			WAVEFORMATEX* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	WAVEFORMATEX* generate();
};



class strfHEADER_WAVE {
	std::vector<strfHEADER_WAVE*>& instances;

	std::string id_var;
	uint32 strf_hdr_wave_datalen_var;
	WAVEFORMATEX* wave_var;
	std::string exData_var;

public:
	bool id_exists = false;
	bool strf_hdr_wave_datalen_exists = false;
	bool wave_exists = false;
	bool exData_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 strf_hdr_wave_datalen() {
		assert_cond(strf_hdr_wave_datalen_exists, "struct field strf_hdr_wave_datalen does not exist");
		return strf_hdr_wave_datalen_var;
	}
	WAVEFORMATEX& wave() {
		assert_cond(wave_exists, "struct field wave does not exist");
		return *wave_var;
	}
	std::string exData() {
		assert_cond(exData_exists, "struct field exData does not exist");
		return exData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	strfHEADER_WAVE& operator () () { return *instances.back(); }
	strfHEADER_WAVE* operator [] (int index) { return instances[index]; }
	strfHEADER_WAVE(std::vector<strfHEADER_WAVE*>& instances) : instances(instances) { instances.push_back(this); }
	~strfHEADER_WAVE() {
		if (generated == 2)
			return;
		while (instances.size()) {
			strfHEADER_WAVE* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	strfHEADER_WAVE* generate();
};



class strfHEADER {
	std::vector<strfHEADER*>& instances;

	std::string id_var;
	uint32 strf_hdr_datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool strf_hdr_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 strf_hdr_datalen() {
		assert_cond(strf_hdr_datalen_exists, "struct field strf_hdr_datalen does not exist");
		return strf_hdr_datalen_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	strfHEADER& operator () () { return *instances.back(); }
	strfHEADER* operator [] (int index) { return instances[index]; }
	strfHEADER(std::vector<strfHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~strfHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			strfHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	strfHEADER* generate();
};



class strnHEADER {
	std::vector<strnHEADER*>& instances;

	std::string id_var;
	uint32 strn_hdr_datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool strn_hdr_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 strn_hdr_datalen() {
		assert_cond(strn_hdr_datalen_exists, "struct field strn_hdr_datalen does not exist");
		return strn_hdr_datalen_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	strnHEADER& operator () () { return *instances.back(); }
	strnHEADER* operator [] (int index) { return instances[index]; }
	strnHEADER(std::vector<strnHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~strnHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			strnHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	strnHEADER* generate();
};


class LISTHEADER;



class MOVICHUNK {
	std::vector<MOVICHUNK*>& instances;

	std::string id_var;
	uint32 movi_datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool movi_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 movi_datalen() {
		assert_cond(movi_datalen_exists, "struct field movi_datalen does not exist");
		return movi_datalen_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MOVICHUNK& operator () () { return *instances.back(); }
	MOVICHUNK* operator [] (int index) { return instances[index]; }
	MOVICHUNK(std::vector<MOVICHUNK*>& instances) : instances(instances) { instances.push_back(this); }
	~MOVICHUNK() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MOVICHUNK* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MOVICHUNK* generate();
};



class LISTHEADER {
	std::vector<LISTHEADER*>& instances;

	std::string id_var;
	uint32 list_hdr_datalen_var;
	std::string type_var;
	avihHEADER* avhi_var;
	strhHEADER* strh_var;
	strnHEADER* strn_var;
	LISTHEADER* movi_list_var;
	MOVICHUNK* movi_chunk_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool list_hdr_datalen_exists = false;
	bool type_exists = false;
	bool avhi_exists = false;
	bool strh_exists = false;
	bool strn_exists = false;
	bool movi_list_exists = false;
	bool movi_chunk_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 list_hdr_datalen() {
		assert_cond(list_hdr_datalen_exists, "struct field list_hdr_datalen does not exist");
		return list_hdr_datalen_var;
	}
	std::string type() {
		assert_cond(type_exists, "struct field type does not exist");
		return type_var;
	}
	avihHEADER& avhi() {
		assert_cond(avhi_exists, "struct field avhi does not exist");
		return *avhi_var;
	}
	strhHEADER& strh() {
		assert_cond(strh_exists, "struct field strh does not exist");
		return *strh_var;
	}
	strnHEADER& strn() {
		assert_cond(strn_exists, "struct field strn does not exist");
		return *strn_var;
	}
	LISTHEADER& movi_list() {
		assert_cond(movi_list_exists, "struct field movi_list does not exist");
		return *movi_list_var;
	}
	MOVICHUNK& movi_chunk() {
		assert_cond(movi_chunk_exists, "struct field movi_chunk does not exist");
		return *movi_chunk_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	/* locals */
	uint datalen_pos;
	std::string next_hdr;
	int32 pointer;
	int32 stop;
	uint block_count;
	uint movi_blk_start;
	std::string movi_blk_hdr;
	std::vector<std::string> movi_blk_hdr_preferred;
	std::vector<std::string> movi_blk_hdr_possible;
	uint after_pos;
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	LISTHEADER& operator () () { return *instances.back(); }
	LISTHEADER* operator [] (int index) { return instances[index]; }
	LISTHEADER(std::vector<LISTHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~LISTHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			LISTHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	LISTHEADER* generate();
};



class JUNKHEADER {
	std::vector<JUNKHEADER*>& instances;

	std::string id_var;
	uint32 junk_hdr_datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool junk_hdr_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 junk_hdr_datalen() {
		assert_cond(junk_hdr_datalen_exists, "struct field junk_hdr_datalen does not exist");
		return junk_hdr_datalen_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	JUNKHEADER& operator () () { return *instances.back(); }
	JUNKHEADER* operator [] (int index) { return instances[index]; }
	JUNKHEADER(std::vector<JUNKHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~JUNKHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			JUNKHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	JUNKHEADER* generate();
};



class AVIINDEXENTRY {
	std::vector<AVIINDEXENTRY*>& instances;

	DWORD ckid_var;
	DWORD dwFlags_var;
	DWORD dwChunkOffset_var;
	DWORD dwChunkLength_var;

public:
	bool ckid_exists = false;
	bool dwFlags_exists = false;
	bool dwChunkOffset_exists = false;
	bool dwChunkLength_exists = false;

	DWORD ckid() {
		assert_cond(ckid_exists, "struct field ckid does not exist");
		return ckid_var;
	}
	DWORD dwFlags() {
		assert_cond(dwFlags_exists, "struct field dwFlags does not exist");
		return dwFlags_var;
	}
	DWORD dwChunkOffset() {
		assert_cond(dwChunkOffset_exists, "struct field dwChunkOffset does not exist");
		return dwChunkOffset_var;
	}
	DWORD dwChunkLength() {
		assert_cond(dwChunkLength_exists, "struct field dwChunkLength does not exist");
		return dwChunkLength_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	AVIINDEXENTRY& operator () () { return *instances.back(); }
	AVIINDEXENTRY* operator [] (int index) { return instances[index]; }
	AVIINDEXENTRY(std::vector<AVIINDEXENTRY*>& instances) : instances(instances) { instances.push_back(this); }
	~AVIINDEXENTRY() {
		if (generated == 2)
			return;
		while (instances.size()) {
			AVIINDEXENTRY* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	AVIINDEXENTRY* generate(DWORD type, DWORD flags, DWORD offset, DWORD len);
};



class idx1HEADER {
	std::vector<idx1HEADER*>& instances;

	std::string id_var;
	uint32 idx1_datalen_var;
	AVIINDEXENTRY* entry_var;
	uint32 idx1_hdr_datalen_var;

public:
	bool id_exists = false;
	bool idx1_datalen_exists = false;
	bool entry_exists = false;
	bool idx1_hdr_datalen_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 idx1_datalen() {
		assert_cond(idx1_datalen_exists, "struct field idx1_datalen does not exist");
		return idx1_datalen_var;
	}
	AVIINDEXENTRY& entry() {
		assert_cond(entry_exists, "struct field entry does not exist");
		return *entry_var;
	}
	uint32 idx1_hdr_datalen() {
		assert_cond(idx1_hdr_datalen_exists, "struct field idx1_hdr_datalen does not exist");
		return idx1_hdr_datalen_var;
	}

	/* locals */
	uint index_start;
	uint i;
	uint j;
	uint offset_count;
	uint current_len;
	DWORD current_type;
	uint index_end;
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	idx1HEADER& operator () () { return *instances.back(); }
	idx1HEADER* operator [] (int index) { return instances[index]; }
	idx1HEADER(std::vector<idx1HEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~idx1HEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			idx1HEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	idx1HEADER* generate();
};


VIDEO_FORMAT VIDEO_FORMAT_generate() {
	return (VIDEO_FORMAT) file_acc.file_integer(sizeof(DWORD), 0, VIDEO_FORMAT_values);
}

VIDEO_FORMAT VIDEO_FORMAT_generate(std::vector<DWORD> known_values) {
	return (VIDEO_FORMAT) file_acc.file_integer(sizeof(DWORD), 0, known_values);
}

VIDEO_STANDARD VIDEO_STANDARD_generate() {
	return (VIDEO_STANDARD) file_acc.file_integer(sizeof(DWORD), 0, VIDEO_STANDARD_values);
}

VIDEO_STANDARD VIDEO_STANDARD_generate(std::vector<DWORD> known_values) {
	return (VIDEO_STANDARD) file_acc.file_integer(sizeof(DWORD), 0, known_values);
}


class VIDEO_FIELD_DESC {
	std::vector<VIDEO_FIELD_DESC*>& instances;

	DWORD CompressedBMHeight_var;
	DWORD CompressedBMWidth_var;
	DWORD ValidBMHeight_var;
	DWORD ValidBMWidth_var;
	DWORD ValidBMXOffset_var;
	DWORD ValidBMYOffset_var;
	DWORD VideoXOffsetInT_var;
	DWORD VideoYValidStartLine_var;

public:
	bool CompressedBMHeight_exists = false;
	bool CompressedBMWidth_exists = false;
	bool ValidBMHeight_exists = false;
	bool ValidBMWidth_exists = false;
	bool ValidBMXOffset_exists = false;
	bool ValidBMYOffset_exists = false;
	bool VideoXOffsetInT_exists = false;
	bool VideoYValidStartLine_exists = false;

	DWORD CompressedBMHeight() {
		assert_cond(CompressedBMHeight_exists, "struct field CompressedBMHeight does not exist");
		return CompressedBMHeight_var;
	}
	DWORD CompressedBMWidth() {
		assert_cond(CompressedBMWidth_exists, "struct field CompressedBMWidth does not exist");
		return CompressedBMWidth_var;
	}
	DWORD ValidBMHeight() {
		assert_cond(ValidBMHeight_exists, "struct field ValidBMHeight does not exist");
		return ValidBMHeight_var;
	}
	DWORD ValidBMWidth() {
		assert_cond(ValidBMWidth_exists, "struct field ValidBMWidth does not exist");
		return ValidBMWidth_var;
	}
	DWORD ValidBMXOffset() {
		assert_cond(ValidBMXOffset_exists, "struct field ValidBMXOffset does not exist");
		return ValidBMXOffset_var;
	}
	DWORD ValidBMYOffset() {
		assert_cond(ValidBMYOffset_exists, "struct field ValidBMYOffset does not exist");
		return ValidBMYOffset_var;
	}
	DWORD VideoXOffsetInT() {
		assert_cond(VideoXOffsetInT_exists, "struct field VideoXOffsetInT does not exist");
		return VideoXOffsetInT_var;
	}
	DWORD VideoYValidStartLine() {
		assert_cond(VideoYValidStartLine_exists, "struct field VideoYValidStartLine does not exist");
		return VideoYValidStartLine_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	VIDEO_FIELD_DESC& operator () () { return *instances.back(); }
	VIDEO_FIELD_DESC* operator [] (int index) { return instances[index]; }
	VIDEO_FIELD_DESC(std::vector<VIDEO_FIELD_DESC*>& instances) : instances(instances) { instances.push_back(this); }
	~VIDEO_FIELD_DESC() {
		if (generated == 2)
			return;
		while (instances.size()) {
			VIDEO_FIELD_DESC* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	VIDEO_FIELD_DESC* generate();
};



class VIDEO_FIELD_DESC_array_class {
	VIDEO_FIELD_DESC& element;
	std::vector<VIDEO_FIELD_DESC*> value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::vector<VIDEO_FIELD_DESC*> operator () () { return value; }
	VIDEO_FIELD_DESC operator [] (int index) { return *value[index]; }
	VIDEO_FIELD_DESC_array_class(VIDEO_FIELD_DESC& element) : element(element) {}

	std::vector<VIDEO_FIELD_DESC*> generate(unsigned size) {
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



class VideoPropHeader {
	std::vector<VideoPropHeader*>& instances;

	std::string id_var;
	uint32 vprp_datalen_var;
	DWORD VideoFormatToken_var;
	DWORD VideoStandard_var;
	DWORD dwVerticalRefreshRate_var;
	DWORD dwHTotalInT_var;
	DWORD dwVTotalInLines_var;
	DWORD dwFrameAspectRatio_var;
	DWORD dwFrameWidthInPixels_var;
	DWORD dwFrameHeightInLines_var;
	DWORD nbFieldPerFrame_var;
	std::vector<VIDEO_FIELD_DESC*> FieldInfo_var;

public:
	bool id_exists = false;
	bool vprp_datalen_exists = false;
	bool VideoFormatToken_exists = false;
	bool VideoStandard_exists = false;
	bool dwVerticalRefreshRate_exists = false;
	bool dwHTotalInT_exists = false;
	bool dwVTotalInLines_exists = false;
	bool dwFrameAspectRatio_exists = false;
	bool dwFrameWidthInPixels_exists = false;
	bool dwFrameHeightInLines_exists = false;
	bool nbFieldPerFrame_exists = false;
	bool FieldInfo_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 vprp_datalen() {
		assert_cond(vprp_datalen_exists, "struct field vprp_datalen does not exist");
		return vprp_datalen_var;
	}
	DWORD VideoFormatToken() {
		assert_cond(VideoFormatToken_exists, "struct field VideoFormatToken does not exist");
		return VideoFormatToken_var;
	}
	DWORD VideoStandard() {
		assert_cond(VideoStandard_exists, "struct field VideoStandard does not exist");
		return VideoStandard_var;
	}
	DWORD dwVerticalRefreshRate() {
		assert_cond(dwVerticalRefreshRate_exists, "struct field dwVerticalRefreshRate does not exist");
		return dwVerticalRefreshRate_var;
	}
	DWORD dwHTotalInT() {
		assert_cond(dwHTotalInT_exists, "struct field dwHTotalInT does not exist");
		return dwHTotalInT_var;
	}
	DWORD dwVTotalInLines() {
		assert_cond(dwVTotalInLines_exists, "struct field dwVTotalInLines does not exist");
		return dwVTotalInLines_var;
	}
	DWORD dwFrameAspectRatio() {
		assert_cond(dwFrameAspectRatio_exists, "struct field dwFrameAspectRatio does not exist");
		return dwFrameAspectRatio_var;
	}
	DWORD dwFrameWidthInPixels() {
		assert_cond(dwFrameWidthInPixels_exists, "struct field dwFrameWidthInPixels does not exist");
		return dwFrameWidthInPixels_var;
	}
	DWORD dwFrameHeightInLines() {
		assert_cond(dwFrameHeightInLines_exists, "struct field dwFrameHeightInLines does not exist");
		return dwFrameHeightInLines_var;
	}
	DWORD nbFieldPerFrame() {
		assert_cond(nbFieldPerFrame_exists, "struct field nbFieldPerFrame does not exist");
		return nbFieldPerFrame_var;
	}
	std::vector<VIDEO_FIELD_DESC*> FieldInfo() {
		assert_cond(FieldInfo_exists, "struct field FieldInfo does not exist");
		return FieldInfo_var;
	}

	/* locals */
	uint vprp_start;
	uint vprp_end;
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	VideoPropHeader& operator () () { return *instances.back(); }
	VideoPropHeader* operator [] (int index) { return instances[index]; }
	VideoPropHeader(std::vector<VideoPropHeader*>& instances) : instances(instances) { instances.push_back(this); }
	~VideoPropHeader() {
		if (generated == 2)
			return;
		while (instances.size()) {
			VideoPropHeader* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	VideoPropHeader* generate();
};



class genericblock {
	std::vector<genericblock*>& instances;

	std::string id_var;
	uint32 genblk_datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool genblk_datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 genblk_datalen() {
		assert_cond(genblk_datalen_exists, "struct field genblk_datalen does not exist");
		return genblk_datalen_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	genericblock& operator () () { return *instances.back(); }
	genericblock* operator [] (int index) { return instances[index]; }
	genericblock(std::vector<genericblock*>& instances) : instances(instances) { instances.push_back(this); }
	~genericblock() {
		if (generated == 2)
			return;
		while (instances.size()) {
			genericblock* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	genericblock* generate();
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


std::vector<ROOT*> ROOT_root_instances;
std::vector<MainAVIHeader*> MainAVIHeader_data_instances;
std::vector<avihHEADER*> avihHEADER_avhi_instances;
std::vector<AVIStreamHeader*> AVIStreamHeader_data__instances;
std::vector<strhHEADER*> strhHEADER_strh_instances;
std::vector<BITMAPINFOHEADER*> BITMAPINFOHEADER_bmiHeader_instances;
std::vector<RGBQUAD*> RGBQUAD_bmiColors_instances;
std::vector<strfHEADER_BIH*> strfHEADER_BIH_strf_instances;
std::vector<WAVEFORMATEX*> WAVEFORMATEX_wave_instances;
std::vector<strfHEADER_WAVE*> strfHEADER_WAVE_strf__instances;
std::vector<strfHEADER*> strfHEADER_strf___instances;
std::vector<strnHEADER*> strnHEADER_strn_instances;
std::vector<MOVICHUNK*> MOVICHUNK_movi_chunk_instances;
std::vector<LISTHEADER*> LISTHEADER_movi_list_instances;
std::vector<LISTHEADER*> LISTHEADER_list_instances;
std::vector<JUNKHEADER*> JUNKHEADER_junk_instances;
std::vector<AVIINDEXENTRY*> AVIINDEXENTRY_entry_instances;
std::vector<idx1HEADER*> idx1HEADER_idx1_instances;
std::vector<VIDEO_FIELD_DESC*> VIDEO_FIELD_DESC_FieldInfo_element_instances;
std::vector<VideoPropHeader*> VideoPropHeader_vprp_instances;
std::vector<genericblock*> genericblock_unknown_block_instances;


std::unordered_map<std::string, std::string> variable_types = { { "id", "char_array_class" }, { "root_datalen", "uint32_class" }, { "form", "char_array_class" }, { "root", "ROOT" }, { "list_hdr_datalen", "uint32_class" }, { "type", "char_array_class" }, { "avi_hdr_datalen", "uint32_class" }, { "dwMicroSecPerFrame", "DWORD_class" }, { "dwMaxBytesPerSec", "DWORD_class" }, { "dwReserved1", "DWORD_class" }, { "dwFlags", "DWORD_class" }, { "dwTotalFrames", "DWORD_class" }, { "dwInitialFrames", "DWORD_class" }, { "dwStreams", "DWORD_class" }, { "dwSuggestedBufferSize", "DWORD_class" }, { "dwWidth", "DWORD_class" }, { "dwHeight", "DWORD_class" }, { "dwScale", "DWORD_class" }, { "dwRate", "DWORD_class" }, { "dwStart", "DWORD_class" }, { "dwLength", "DWORD_class" }, { "data", "MainAVIHeader" }, { "avhi", "avihHEADER" }, { "strh_hdr_datalen", "uint32_class" }, { "fccType", "char_array_class" }, { "fccHandler", "char_array_class" }, { "dwQuality", "DWORD_class" }, { "dwSampleSize", "DWORD_class" }, { "xdwQuality", "DWORD_class" }, { "xdwSampleSize", "DWORD_class" }, { "data_", "AVIStreamHeader" }, { "strh", "strhHEADER" }, { "strf_hdr_bih_datalen", "uint32_class" }, { "biSize", "uint32_class" }, { "biWidth", "uint32_class" }, { "biHeight", "uint32_class" }, { "biPlanes", "uint16_class" }, { "biBitCount", "uint16_class" }, { "biCompression", "uint32_class" }, { "biSizeImage", "uint32_class" }, { "biXPelsPerMeter", "uint32_class" }, { "biYPelsPerMeter", "uint32_class" }, { "biClrUsed", "uint32_class" }, { "biClrImportant", "uint32_class" }, { "bmiHeader", "BITMAPINFOHEADER" }, { "rgbBlue", "unsigned_char_class" }, { "rgbGreen", "unsigned_char_class" }, { "rgbRed", "unsigned_char_class" }, { "rgbReserved", "unsigned_char_class" }, { "bmiColors", "RGBQUAD" }, { "exData", "char_array_class" }, { "strf", "strfHEADER_BIH" }, { "strf_hdr_wave_datalen", "uint32_class" }, { "wFormatTag", "WORD_class" }, { "nChannels", "WORD_class" }, { "nSamplesPerSec", "DWORD_class" }, { "nAvgBytesPerSec", "DWORD_class" }, { "nBlockAlign", "WORD_class" }, { "wBitsPerSample", "WORD_class" }, { "cbSize", "WORD_class" }, { "wave", "WAVEFORMATEX" }, { "strf_", "strfHEADER_WAVE" }, { "strf_hdr_datalen", "uint32_class" }, { "data__", "char_array_class" }, { "strf__", "strfHEADER" }, { "strn_hdr_datalen", "uint32_class" }, { "strn", "strnHEADER" }, { "movi_datalen", "uint32_class" }, { "movi_chunk", "MOVICHUNK" }, { "movi_list", "LISTHEADER" }, { "list", "LISTHEADER" }, { "junk_hdr_datalen", "uint32_class" }, { "junk", "JUNKHEADER" }, { "idx1_datalen", "uint32_class" }, { "ckid", "DWORD_class" }, { "dwChunkOffset", "DWORD_class" }, { "dwChunkLength", "DWORD_class" }, { "entry", "AVIINDEXENTRY" }, { "idx1_hdr_datalen", "uint32_class" }, { "idx1", "idx1HEADER" }, { "vprp_datalen", "uint32_class" }, { "VideoFormatToken", "VIDEO_FORMAT" }, { "VideoStandard", "VIDEO_STANDARD" }, { "dwVerticalRefreshRate", "DWORD_class" }, { "dwHTotalInT", "DWORD_class" }, { "dwVTotalInLines", "DWORD_class" }, { "dwFrameAspectRatio", "DWORD_class" }, { "dwFrameWidthInPixels", "DWORD_class" }, { "dwFrameHeightInLines", "DWORD_class" }, { "nbFieldPerFrame", "DWORD_class" }, { "CompressedBMHeight", "DWORD_class" }, { "CompressedBMWidth", "DWORD_class" }, { "ValidBMHeight", "DWORD_class" }, { "ValidBMWidth", "DWORD_class" }, { "ValidBMXOffset", "DWORD_class" }, { "ValidBMYOffset", "DWORD_class" }, { "VideoXOffsetInT", "DWORD_class" }, { "VideoYValidStartLine", "DWORD_class" }, { "FieldInfo", "VIDEO_FIELD_DESC_array_class" }, { "vprp", "VideoPropHeader" }, { "genblk_datalen", "uint32_class" }, { "unknown_block", "genericblock" } };

std::vector<std::vector<int>> integer_ranges = { { 1, 16 }, { 6, 22 }, { 40, 58 }, { 20, 36 } };

class globals_class {
public:
	/*local*/ uint list_index;
	char_class id_element;
	char_array_class id;
	uint32_class root_datalen;
	char_class form_element;
	char_array_class form;
	ROOT root;
	/*local*/ uint junk_count;
	/*local*/ uint allow_vprp;
	/*local*/ std::vector<std::string> nheader_preferred;
	/*local*/ std::vector<std::string> nheader_possible;
	/*local*/ std::string nheader;
	uint32_class list_hdr_datalen;
	char_class type_element;
	char_array_class type;
	uint32_class avi_hdr_datalen;
	DWORD_class dwMicroSecPerFrame;
	DWORD_class dwMaxBytesPerSec;
	DWORD_class dwReserved1;
	DWORD_class dwFlags;
	DWORD_class dwTotalFrames;
	DWORD_class dwInitialFrames;
	DWORD_class dwStreams;
	DWORD_class dwSuggestedBufferSize;
	DWORD_class dwWidth;
	DWORD_class dwHeight;
	DWORD_class dwScale;
	DWORD_class dwRate;
	DWORD_class dwStart;
	DWORD_class dwLength;
	MainAVIHeader data;
	avihHEADER avhi;
	uint32_class strh_hdr_datalen;
	char_class fccType_element;
	char_array_class fccType;
	char_class fccHandler_element;
	char_array_class fccHandler;
	DWORD_class dwQuality;
	DWORD_class dwSampleSize;
	DWORD_class xdwQuality;
	DWORD_class xdwSampleSize;
	AVIStreamHeader data_;
	strhHEADER strh;
	uint32_class strf_hdr_bih_datalen;
	uint32_class biSize;
	uint32_class biWidth;
	uint32_class biHeight;
	uint16_class biPlanes;
	uint16_class biBitCount;
	uint32_class biCompression;
	uint32_class biSizeImage;
	uint32_class biXPelsPerMeter;
	uint32_class biYPelsPerMeter;
	uint32_class biClrUsed;
	uint32_class biClrImportant;
	BITMAPINFOHEADER bmiHeader;
	unsigned_char_class rgbBlue;
	unsigned_char_class rgbGreen;
	unsigned_char_class rgbRed;
	unsigned_char_class rgbReserved;
	RGBQUAD bmiColors;
	char_class exData_element;
	char_array_class exData;
	strfHEADER_BIH strf;
	uint32_class strf_hdr_wave_datalen;
	WORD_class wFormatTag;
	WORD_class nChannels;
	DWORD_class nSamplesPerSec;
	DWORD_class nAvgBytesPerSec;
	WORD_class nBlockAlign;
	WORD_class wBitsPerSample;
	WORD_class cbSize;
	WAVEFORMATEX wave;
	strfHEADER_WAVE strf_;
	uint32_class strf_hdr_datalen;
	char_class data___element;
	char_array_class data__;
	strfHEADER strf__;
	uint32_class strn_hdr_datalen;
	strnHEADER strn;
	uint32_class movi_datalen;
	MOVICHUNK movi_chunk;
	LISTHEADER movi_list;
	LISTHEADER list;
	uint32_class junk_hdr_datalen;
	JUNKHEADER junk;
	uint32_class idx1_datalen;
	DWORD_class ckid;
	DWORD_class dwChunkOffset;
	DWORD_class dwChunkLength;
	AVIINDEXENTRY entry;
	uint32_class idx1_hdr_datalen;
	idx1HEADER idx1;
	uint32_class vprp_datalen;
	DWORD_class dwVerticalRefreshRate;
	DWORD_class dwHTotalInT;
	DWORD_class dwVTotalInLines;
	DWORD_class dwFrameAspectRatio;
	DWORD_class dwFrameWidthInPixels;
	DWORD_class dwFrameHeightInLines;
	DWORD_class nbFieldPerFrame;
	DWORD_class CompressedBMHeight;
	DWORD_class CompressedBMWidth;
	DWORD_class ValidBMHeight;
	DWORD_class ValidBMWidth;
	DWORD_class ValidBMXOffset;
	DWORD_class ValidBMYOffset;
	DWORD_class VideoXOffsetInT;
	DWORD_class VideoYValidStartLine;
	VIDEO_FIELD_DESC FieldInfo_element;
	VIDEO_FIELD_DESC_array_class FieldInfo;
	VideoPropHeader vprp;
	uint32_class genblk_datalen;
	genericblock unknown_block;
	/*local*/ uint file_end;
	/*local*/ uint evil_state;


	globals_class() :
		id_element(false),
		id(id_element, { { 3, {{'X'}} } }),
		root_datalen(2),
		form_element(false),
		form(form_element),
		root(ROOT_root_instances),
		nheader(4, 0),
		list_hdr_datalen(3),
		type_element(false),
		type(type_element, { "movi" }),
		avi_hdr_datalen(1),
		dwMicroSecPerFrame(1),
		dwMaxBytesPerSec(1),
		dwReserved1(1),
		dwFlags(1),
		dwTotalFrames(1),
		dwInitialFrames(1),
		dwStreams(1),
		dwSuggestedBufferSize(1),
		dwWidth(1),
		dwHeight(1),
		dwScale(1),
		dwRate(1),
		dwStart(1),
		dwLength(1),
		data(MainAVIHeader_data_instances),
		avhi(avihHEADER_avhi_instances),
		strh_hdr_datalen(1),
		fccType_element(false),
		fccType(fccType_element),
		fccHandler_element(false),
		fccHandler(fccHandler_element),
		dwQuality(1),
		dwSampleSize(1),
		xdwQuality(1),
		xdwSampleSize(1),
		data_(AVIStreamHeader_data__instances),
		strh(strhHEADER_strh_instances),
		strf_hdr_bih_datalen(4),
		biSize(1),
		biWidth(1),
		biHeight(1),
		biPlanes(1),
		biBitCount(1),
		biCompression(1),
		biSizeImage(1),
		biXPelsPerMeter(1),
		biYPelsPerMeter(1),
		biClrUsed(1),
		biClrImportant(1),
		bmiHeader(BITMAPINFOHEADER_bmiHeader_instances),
		rgbBlue(1),
		rgbGreen(1),
		rgbRed(1),
		rgbReserved(1),
		bmiColors(RGBQUAD_bmiColors_instances),
		exData_element(false),
		exData(exData_element),
		strf(strfHEADER_BIH_strf_instances),
		strf_hdr_wave_datalen(5),
		wFormatTag(1),
		nChannels(1),
		nSamplesPerSec(1),
		nAvgBytesPerSec(1),
		nBlockAlign(1),
		wBitsPerSample(1),
		cbSize(1),
		wave(WAVEFORMATEX_wave_instances),
		strf_(strfHEADER_WAVE_strf__instances),
		strf_hdr_datalen(2),
		data___element(false),
		data__(data___element),
		strf__(strfHEADER_strf___instances),
		strn_hdr_datalen(2),
		strn(strnHEADER_strn_instances),
		movi_datalen(2),
		movi_chunk(MOVICHUNK_movi_chunk_instances),
		movi_list(LISTHEADER_movi_list_instances),
		list(LISTHEADER_list_instances),
		junk_hdr_datalen(2),
		junk(JUNKHEADER_junk_instances),
		idx1_datalen(1),
		ckid(1),
		dwChunkOffset(1),
		dwChunkLength(1),
		entry(AVIINDEXENTRY_entry_instances),
		idx1_hdr_datalen(1),
		idx1(idx1HEADER_idx1_instances),
		vprp_datalen(1),
		dwVerticalRefreshRate(1),
		dwHTotalInT(1),
		dwVTotalInLines(1),
		dwFrameAspectRatio(1),
		dwFrameWidthInPixels(1),
		dwFrameHeightInLines(1),
		nbFieldPerFrame(1),
		CompressedBMHeight(1),
		CompressedBMWidth(1),
		ValidBMHeight(1),
		ValidBMWidth(1),
		ValidBMXOffset(1),
		ValidBMYOffset(1),
		VideoXOffsetInT(1),
		VideoYValidStartLine(1),
		FieldInfo_element(VIDEO_FIELD_DESC_FieldInfo_element_instances),
		FieldInfo(FieldInfo_element),
		vprp(VideoPropHeader_vprp_instances),
		genblk_datalen(2),
		unknown_block(genericblock_unknown_block_instances)
	{}
};

globals_class* g;

DWORD DWORDFromString(std::string str) {
	if ((Strlen(str) != 4)) {
		Printf("DWORDFromString(): String was not 32 bits.\n");
		return (-1);
	};
	/*local*/ DWORD t0 = ((DWORD)str[3] << 24);
	/*local*/ DWORD t1 = ((DWORD)str[2] << 16);
	/*local*/ DWORD t2 = ((DWORD)str[1] << 8);
	/*local*/ DWORD t3 = (DWORD)str[0];
	return ((((t0 + t1) + t2) + t3));
}

ROOT* ROOT::generate() {
	if (generated == 1) {
		ROOT* new_instance = new ROOT(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "RIFF" }));
	if ((::g->root().id()[3] == 'X')) {
		Printf("Motorola format\n");
		BigEndian();
	} else {
		Printf("Intel format\n");
		LittleEndian();
	};
	root_datalen_pos = FTell();
	GENERATE_VAR(root_datalen, ::g->root_datalen.generate());
	evil_state = SetEvilBit(false);
	GENERATE_VAR(form, ::g->form.generate(4, { "AVI " }));
	SetEvilBit(evil_state);
	if (Strcmp(form(), "AVI ")) {
		Warning("Not a valid AVI file");
		exit_template(-1);
	};

	_sizeof = FTell() - _startof;
	return this;
}


MainAVIHeader* MainAVIHeader::generate() {
	if (generated == 1) {
		MainAVIHeader* new_instance = new MainAVIHeader(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(dwMicroSecPerFrame, ::g->dwMicroSecPerFrame.generate());
	GENERATE_VAR(dwMaxBytesPerSec, ::g->dwMaxBytesPerSec.generate());
	GENERATE_VAR(dwReserved1, ::g->dwReserved1.generate());
	GENERATE_VAR(dwFlags, ::g->dwFlags.generate());
	GENERATE_VAR(dwTotalFrames, ::g->dwTotalFrames.generate());
	GENERATE_VAR(dwInitialFrames, ::g->dwInitialFrames.generate());
	GENERATE_VAR(dwStreams, ::g->dwStreams.generate());
	GENERATE_VAR(dwSuggestedBufferSize, ::g->dwSuggestedBufferSize.generate());
	GENERATE_VAR(dwWidth, ::g->dwWidth.generate());
	GENERATE_VAR(dwHeight, ::g->dwHeight.generate());
	GENERATE_VAR(dwScale, ::g->dwScale.generate());
	GENERATE_VAR(dwRate, ::g->dwRate.generate());
	GENERATE_VAR(dwStart, ::g->dwStart.generate());
	GENERATE_VAR(dwLength, ::g->dwLength.generate());

	_sizeof = FTell() - _startof;
	return this;
}


avihHEADER* avihHEADER::generate() {
	if (generated == 1) {
		avihHEADER* new_instance = new avihHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "avih" }));
	GENERATE_VAR(avi_hdr_datalen, ::g->avi_hdr_datalen.generate({ 56 }));
	GENERATE_VAR(data, ::g->data.generate());

	_sizeof = FTell() - _startof;
	return this;
}


AVIStreamHeader* AVIStreamHeader::generate() {
	if (generated == 1) {
		AVIStreamHeader* new_instance = new AVIStreamHeader(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(fccType, ::g->fccType.generate(4, { "vids" }));
	GENERATE_VAR(fccHandler, ::g->fccHandler.generate(4));
	GENERATE_VAR(dwFlags, ::g->dwFlags.generate());
	GENERATE_VAR(dwReserved1, ::g->dwReserved1.generate());
	GENERATE_VAR(dwInitialFrames, ::g->dwInitialFrames.generate());
	GENERATE_VAR(dwScale, ::g->dwScale.generate());
	GENERATE_VAR(dwRate, ::g->dwRate.generate());
	GENERATE_VAR(dwStart, ::g->dwStart.generate());
	GENERATE_VAR(dwLength, ::g->dwLength.generate());
	GENERATE_VAR(dwSuggestedBufferSize, ::g->dwSuggestedBufferSize.generate());
	GENERATE_VAR(dwQuality, ::g->dwQuality.generate());
	GENERATE_VAR(dwSampleSize, ::g->dwSampleSize.generate());
	GENERATE_VAR(xdwQuality, ::g->xdwQuality.generate());
	GENERATE_VAR(xdwSampleSize, ::g->xdwSampleSize.generate());

	_sizeof = FTell() - _startof;
	return this;
}


strhHEADER* strhHEADER::generate() {
	if (generated == 1) {
		strhHEADER* new_instance = new strhHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "strh" }));
	GENERATE_VAR(strh_hdr_datalen, ::g->strh_hdr_datalen.generate({ 56 }));
	GENERATE_VAR(data, ::g->data_.generate());

	_sizeof = FTell() - _startof;
	return this;
}


BITMAPINFOHEADER* BITMAPINFOHEADER::generate() {
	if (generated == 1) {
		BITMAPINFOHEADER* new_instance = new BITMAPINFOHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(biSize, ::g->biSize.generate());
	GENERATE_VAR(biWidth, ::g->biWidth.generate());
	GENERATE_VAR(biHeight, ::g->biHeight.generate());
	GENERATE_VAR(biPlanes, ::g->biPlanes.generate());
	GENERATE_VAR(biBitCount, ::g->biBitCount.generate({ 8 }));
	GENERATE_VAR(biCompression, ::g->biCompression.generate({ 1 }));
	GENERATE_VAR(biSizeImage, ::g->biSizeImage.generate());
	GENERATE_VAR(biXPelsPerMeter, ::g->biXPelsPerMeter.generate());
	GENERATE_VAR(biYPelsPerMeter, ::g->biYPelsPerMeter.generate());
	GENERATE_VAR(biClrUsed, ::g->biClrUsed.generate());
	GENERATE_VAR(biClrImportant, ::g->biClrImportant.generate());

	_sizeof = FTell() - _startof;
	return this;
}


RGBQUAD* RGBQUAD::generate() {
	if (generated == 1) {
		RGBQUAD* new_instance = new RGBQUAD(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(rgbBlue, ::g->rgbBlue.generate());
	GENERATE_VAR(rgbGreen, ::g->rgbGreen.generate());
	GENERATE_VAR(rgbRed, ::g->rgbRed.generate());
	GENERATE_VAR(rgbReserved, ::g->rgbReserved.generate());

	_sizeof = FTell() - _startof;
	return this;
}


strfHEADER_BIH* strfHEADER_BIH::generate() {
	if (generated == 1) {
		strfHEADER_BIH* new_instance = new strfHEADER_BIH(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "strf" }));
	GENERATE_VAR(strf_hdr_bih_datalen, ::g->strf_hdr_bih_datalen.generate());
	Printf("STRF_HDR_BIH_DATALEN: %d\n", strf_hdr_bih_datalen());
	GENERATE_VAR(bmiHeader, ::g->bmiHeader.generate());
	sz = bmiHeader()._sizeof;
	if ((strf_hdr_bih_datalen() == 44)) {
		GENERATE_VAR(bmiColors, ::g->bmiColors.generate());
		sz += 4;
	};
	Printf("left: %d\n", sz);
	exDataLen = (strf_hdr_bih_datalen() - sz);
	Printf("exDataLen: %d\n", exDataLen);
	GENERATE_VAR(exData, ::g->exData.generate(exDataLen));

	_sizeof = FTell() - _startof;
	return this;
}


WAVEFORMATEX* WAVEFORMATEX::generate() {
	if (generated == 1) {
		WAVEFORMATEX* new_instance = new WAVEFORMATEX(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(wFormatTag, ::g->wFormatTag.generate());
	GENERATE_VAR(nChannels, ::g->nChannels.generate());
	GENERATE_VAR(nSamplesPerSec, ::g->nSamplesPerSec.generate());
	GENERATE_VAR(nAvgBytesPerSec, ::g->nAvgBytesPerSec.generate());
	GENERATE_VAR(nBlockAlign, ::g->nBlockAlign.generate());
	GENERATE_VAR(wBitsPerSample, ::g->wBitsPerSample.generate());
	GENERATE_VAR(cbSize, ::g->cbSize.generate());

	_sizeof = FTell() - _startof;
	return this;
}


strfHEADER_WAVE* strfHEADER_WAVE::generate() {
	if (generated == 1) {
		strfHEADER_WAVE* new_instance = new strfHEADER_WAVE(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "strf" }));
	GENERATE_VAR(strf_hdr_wave_datalen, ::g->strf_hdr_wave_datalen.generate());
	Printf("%d\n", strf_hdr_wave_datalen());
	GENERATE_VAR(wave, ::g->wave.generate());
	GENERATE_VAR(exData, ::g->exData.generate((strf_hdr_wave_datalen() - 18)));

	_sizeof = FTell() - _startof;
	return this;
}


strfHEADER* strfHEADER::generate() {
	if (generated == 1) {
		strfHEADER* new_instance = new strfHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "strf" }));
	GENERATE_VAR(strf_hdr_datalen, ::g->strf_hdr_datalen.generate());
	if ((strf_hdr_datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((strf_hdr_datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(strf_hdr_datalen()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


strnHEADER* strnHEADER::generate() {
	if (generated == 1) {
		strnHEADER* new_instance = new strnHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "vedt" }));
	GENERATE_VAR(strn_hdr_datalen, ::g->strn_hdr_datalen.generate());
	if ((strn_hdr_datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((strn_hdr_datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(strn_hdr_datalen()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


MOVICHUNK* MOVICHUNK::generate() {
	if (generated == 1) {
		MOVICHUNK* new_instance = new MOVICHUNK(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(movi_datalen, ::g->movi_datalen.generate());
	if ((movi_datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((movi_datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(movi_datalen()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


LISTHEADER* LISTHEADER::generate() {
	if (generated == 1) {
		LISTHEADER* new_instance = new LISTHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4, { "RIFF", "LIST" }));
	datalen_pos = FTell();
	GENERATE_VAR(list_hdr_datalen, ::g->list_hdr_datalen.generate());
	GENERATE_VAR(type, ::g->type.generate(4, { ((::g->list_index == 0) ? "hdrl" : ((::g->list_index == 1) ? "strl" : "movi")) }));
	if (!Memcmp(type(), "hdrl", 4)) {
		GENERATE_VAR(avhi, ::g->avhi.generate());
	} else {
	if (!Memcmp(type(), "strl", 4)) {
		GENERATE_VAR(strh, ::g->strh.generate());
		if ((Memcmp(strh().data().fccType(), "vids", 4) == 0)) {
			GENERATE(strf, ::g->strf.generate());
		} else {
		if ((Memcmp(strh().data().fccType(), "auds", 4) == 0)) {
			GENERATE(strf, ::g->strf_.generate());
		} else {
			GENERATE(strf, ::g->strf__.generate());
		};
		};
		ReadBytes(next_hdr, FTell(), 4);
		if (((((next_hdr != "LIST") && (next_hdr != "vprp")) && (next_hdr != "idx1")) && (next_hdr != "JUNK"))) {
			GENERATE_VAR(strn, ::g->strn.generate());
		};
	} else {
	if (((Memcmp(type(), "movi", 4) == 0) || (Memcmp(type(), "rec ", 4) == 0))) {
		pointer = 0;
		stop = (list_hdr_datalen() - 4);
		block_count = 0;
		do {
			movi_blk_start = FTell();
			movi_blk_hdr_preferred = { "00db" };
			movi_blk_hdr_possible = { "00db" };
			ReadBytes(movi_blk_hdr, FTell(), 4);
			if ((movi_blk_hdr == "LIST")) {
				GENERATE_VAR(movi_list, ::g->movi_list.generate());
			} else {
				GENERATE_VAR(movi_chunk, ::g->movi_chunk.generate());
			};
			block_count++;
			pointer += (FTell() - movi_blk_start);
		} while ((pointer < stop));
		after_pos = FTell();
		FSeek(datalen_pos);
		evil_state = SetEvilBit(false);
		GENERATE_VAR(list_hdr_datalen, ::g->list_hdr_datalen.generate({ ((uint32)pointer + 4) }));
		SetEvilBit(evil_state);
		FSeek(after_pos);
	} else {
		GENERATE_VAR(data, ::g->data__.generate((list_hdr_datalen() - 4)));
	};
	};
	};

	_sizeof = FTell() - _startof;
	return this;
}


JUNKHEADER* JUNKHEADER::generate() {
	if (generated == 1) {
		JUNKHEADER* new_instance = new JUNKHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(junk_hdr_datalen, ::g->junk_hdr_datalen.generate());
	if ((junk_hdr_datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((junk_hdr_datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(junk_hdr_datalen()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


AVIINDEXENTRY* AVIINDEXENTRY::generate(DWORD type, DWORD flags, DWORD offset, DWORD len) {
	if (generated == 1) {
		AVIINDEXENTRY* new_instance = new AVIINDEXENTRY(instances);
		new_instance->generated = 2;
		return new_instance->generate(type, flags, offset, len);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(ckid, ::g->ckid.generate({ type }));
	GENERATE_VAR(dwFlags, ::g->dwFlags.generate({ flags }));
	GENERATE_VAR(dwChunkOffset, ::g->dwChunkOffset.generate({ offset }));
	GENERATE_VAR(dwChunkLength, ::g->dwChunkLength.generate({ len }));

	_sizeof = FTell() - _startof;
	return this;
}


idx1HEADER* idx1HEADER::generate() {
	if (generated == 1) {
		idx1HEADER* new_instance = new idx1HEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(idx1_datalen, ::g->idx1_datalen.generate());
	index_start = FTell();
	j = 0;
	offset_count = 4;
	for (i = 0; (i < ::g->list_index); i++) {
			if ((::g->list()[i]->type() == "movi")) {
			for (j = 0; (j < ::g->list()[i]->block_count); j++) {
					if (!::g->list()[i]->movi_chunk_exists) {
				continue;
				};
				current_len = ::g->list()[i]->movi_chunk()[j]->movi_datalen();
				current_type = DWORDFromString(::g->list()[i]->movi_chunk()[j]->id());
				GENERATE_VAR(entry, ::g->entry.generate(current_type, 0x00, offset_count, current_len));
				offset_count += (current_len + ((current_len % 2) ? 9 : 8));
			;
			};
		};
	;
	};
	index_end = FTell();
	FSeek((index_start - 4));
	evil_state = SetEvilBit(false);
	GENERATE_VAR(idx1_hdr_datalen, ::g->idx1_hdr_datalen.generate({ (index_end - index_start) }));
	SetEvilBit(evil_state);
	FSeek(index_end);

	_sizeof = FTell() - _startof;
	return this;
}


VIDEO_FIELD_DESC* VIDEO_FIELD_DESC::generate() {
	if (generated == 1) {
		VIDEO_FIELD_DESC* new_instance = new VIDEO_FIELD_DESC(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(CompressedBMHeight, ::g->CompressedBMHeight.generate());
	GENERATE_VAR(CompressedBMWidth, ::g->CompressedBMWidth.generate());
	GENERATE_VAR(ValidBMHeight, ::g->ValidBMHeight.generate());
	GENERATE_VAR(ValidBMWidth, ::g->ValidBMWidth.generate());
	GENERATE_VAR(ValidBMXOffset, ::g->ValidBMXOffset.generate());
	GENERATE_VAR(ValidBMYOffset, ::g->ValidBMYOffset.generate());
	GENERATE_VAR(VideoXOffsetInT, ::g->VideoXOffsetInT.generate());
	GENERATE_VAR(VideoYValidStartLine, ::g->VideoYValidStartLine.generate());

	_sizeof = FTell() - _startof;
	return this;
}


VideoPropHeader* VideoPropHeader::generate() {
	if (generated == 1) {
		VideoPropHeader* new_instance = new VideoPropHeader(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(vprp_datalen, ::g->vprp_datalen.generate());
	vprp_start = FTell();
	GENERATE_VAR(VideoFormatToken, VIDEO_FORMAT_generate());
	GENERATE_VAR(VideoStandard, VIDEO_STANDARD_generate());
	GENERATE_VAR(dwVerticalRefreshRate, ::g->dwVerticalRefreshRate.generate());
	GENERATE_VAR(dwHTotalInT, ::g->dwHTotalInT.generate());
	GENERATE_VAR(dwVTotalInLines, ::g->dwVTotalInLines.generate());
	GENERATE_VAR(dwFrameAspectRatio, ::g->dwFrameAspectRatio.generate());
	GENERATE_VAR(dwFrameWidthInPixels, ::g->dwFrameWidthInPixels.generate());
	GENERATE_VAR(dwFrameHeightInLines, ::g->dwFrameHeightInLines.generate());
	GENERATE_VAR(nbFieldPerFrame, ::g->nbFieldPerFrame.generate({ 0x01, 0x02 }));
	GENERATE_VAR(FieldInfo, ::g->FieldInfo.generate(nbFieldPerFrame()));
	vprp_end = FTell();
	FSeek((vprp_start - 4));
	evil_state = SetEvilBit(false);
	GENERATE_VAR(vprp_datalen, ::g->vprp_datalen.generate({ (vprp_end - vprp_start) }));
	SetEvilBit(evil_state);
	FSeek(vprp_end);

	_sizeof = FTell() - _startof;
	return this;
}


genericblock* genericblock::generate() {
	if (generated == 1) {
		genericblock* new_instance = new genericblock(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(genblk_datalen, ::g->genblk_datalen.generate());
	if ((genblk_datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((genblk_datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(genblk_datalen()));
	};

	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	::g->list_index = 0;
	GENERATE(root, ::g->root.generate());
	::g->junk_count = 0;
	::g->allow_vprp = 1;
	::g->nheader_preferred = { "LIST", "JUNK" };
	::g->nheader_possible = { "LIST", "JUNK" };
	while (ReadBytes(::g->nheader, FTell(), 4, ::g->nheader_preferred, ::g->nheader_possible)) {
		switch (STR2INT(::g->nheader)) {
		case STR2INT("LIST"):
			GENERATE(list, ::g->list.generate());
			::g->list_index++;
			if (((::g->list_index == 1) && ::g->allow_vprp)) {
				::g->nheader_preferred.insert(::g->nheader_preferred.end(), { "vprp" });
				::g->nheader_possible.insert(::g->nheader_possible.end(), { "vprp" });
			} else {
			if ((::g->list_index >= 3)) {
				::g->nheader_preferred = { "idx1" };
				::g->nheader_possible = { "idx1" };
			};
			};
			break;
		case STR2INT("JUNK"):
			GENERATE(junk, ::g->junk.generate());
			::g->junk_count++;
			if ((::g->junk_count >= 2)) {
				VectorRemove(::g->nheader_preferred, { "JUNK" });
			};
			break;
		case STR2INT("idx1"):
			GENERATE(idx1, ::g->idx1.generate());
			::g->nheader_preferred = {  };
			::g->nheader_possible = {  };
			break;
		case STR2INT("vprp"):
			GENERATE(vprp, ::g->vprp.generate());
			VectorRemove(::g->nheader_preferred, { "vprp" });
			VectorRemove(::g->nheader_possible, { "vprp" });
			break;
		default:
			GENERATE(unknown_block, ::g->unknown_block.generate());
		};
	};
	::g->file_end = FTell();
	FSeek(::g->root().root_datalen_pos);
	::g->evil_state = SetEvilBit(false);
	GENERATE(root_datalen, ::g->root_datalen.generate({ (::g->file_end - 8) }));
	SetEvilBit(::g->evil_state);
	FSeek(::g->file_end);

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

