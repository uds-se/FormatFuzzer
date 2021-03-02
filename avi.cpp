#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"
const DWORD AVIINDEXENTRYLEN = 16;


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
	uint32 datalen_var;
	std::string form_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool form_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
	}
	std::string form() {
		assert_cond(form_exists, "struct field form does not exist");
		return form_var;
	}

	/* locals */
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
	uint32 datalen_var;
	MainAVIHeader* data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	uint32 datalen_var;
	AVIStreamHeader* data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	uint32 datalen_var;
	BITMAPINFOHEADER* bmiHeader_var;
	RGBQUAD* bmiColors_var;
	std::string exData_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool bmiHeader_exists = false;
	bool bmiColors_exists = false;
	bool exData_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	uint32 datalen_var;
	WAVEFORMATEX* wave_var;
	std::string exData_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool wave_exists = false;
	bool exData_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	uint32 datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	uint32 datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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



class genericblock {
	std::vector<genericblock*>& instances;

	std::string id_var;
	uint32 datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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



class LISTHEADER {
	std::vector<LISTHEADER*>& instances;

	std::string id_var;
	uint32 datalen_var;
	std::string type_var;
	avihHEADER* avhi_var;
	strhHEADER* strh_var;
	strnHEADER* strn_var;
	genericblock* gb_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool type_exists = false;
	bool avhi_exists = false;
	bool strh_exists = false;
	bool strn_exists = false;
	bool gb_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	genericblock& gb() {
		assert_cond(gb_exists, "struct field gb does not exist");
		return *gb_var;
	}
	std::string data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

	/* locals */
	int32 pointer;
	int32 stop;

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
	uint32 datalen_var;
	std::string data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
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
	AVIINDEXENTRY* generate();
};



class AVIINDEXENTRY_array_class {
	AVIINDEXENTRY& element;
	std::vector<AVIINDEXENTRY*> value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::vector<AVIINDEXENTRY*> operator () () { return value; }
	AVIINDEXENTRY operator [] (int index) { return *value[index]; }
	AVIINDEXENTRY_array_class(AVIINDEXENTRY& element) : element(element) {}

	std::vector<AVIINDEXENTRY*> generate(unsigned size) {
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



class idx1HEADER {
	std::vector<idx1HEADER*>& instances;

	std::string id_var;
	uint32 datalen_var;
	std::vector<AVIINDEXENTRY*> data_var;

public:
	bool id_exists = false;
	bool datalen_exists = false;
	bool data_exists = false;

	std::string id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint32 datalen() {
		assert_cond(datalen_exists, "struct field datalen does not exist");
		return datalen_var;
	}
	std::vector<AVIINDEXENTRY*> data() {
		assert_cond(data_exists, "struct field data does not exist");
		return data_var;
	}

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
std::vector<genericblock*> genericblock_gb_instances;
std::vector<LISTHEADER*> LISTHEADER_list_instances;
std::vector<JUNKHEADER*> JUNKHEADER_junk_instances;
std::vector<AVIINDEXENTRY*> AVIINDEXENTRY_data____element_instances;
std::vector<idx1HEADER*> idx1HEADER_idx1_instances;


std::unordered_map<std::string, std::string> variable_types = { { "id", "char_array_class" }, { "datalen", "uint32_class" }, { "form", "char_array_class" }, { "root", "ROOT" }, { "type", "char_array_class" }, { "dwMicroSecPerFrame", "DWORD_class" }, { "dwMaxBytesPerSec", "DWORD_class" }, { "dwReserved1", "DWORD_class" }, { "dwFlags", "DWORD_class" }, { "dwTotalFrames", "DWORD_class" }, { "dwInitialFrames", "DWORD_class" }, { "dwStreams", "DWORD_class" }, { "dwSuggestedBufferSize", "DWORD_class" }, { "dwWidth", "DWORD_class" }, { "dwHeight", "DWORD_class" }, { "dwScale", "DWORD_class" }, { "dwRate", "DWORD_class" }, { "dwStart", "DWORD_class" }, { "dwLength", "DWORD_class" }, { "data", "MainAVIHeader" }, { "avhi", "avihHEADER" }, { "fccType", "char_array_class" }, { "fccHandler", "char_array_class" }, { "dwQuality", "DWORD_class" }, { "dwSampleSize", "DWORD_class" }, { "xdwQuality", "DWORD_class" }, { "xdwSampleSize", "DWORD_class" }, { "data_", "AVIStreamHeader" }, { "strh", "strhHEADER" }, { "biSize", "uint32_class" }, { "biWidth", "uint32_class" }, { "biHeight", "uint32_class" }, { "biPlanes", "uint16_class" }, { "biBitCount", "uint16_class" }, { "biCompression", "uint32_class" }, { "biSizeImage", "uint32_class" }, { "biXPelsPerMeter", "uint32_class" }, { "biYPelsPerMeter", "uint32_class" }, { "biClrUsed", "uint32_class" }, { "biClrImportant", "uint32_class" }, { "bmiHeader", "BITMAPINFOHEADER" }, { "rgbBlue", "unsigned_char_class" }, { "rgbGreen", "unsigned_char_class" }, { "rgbRed", "unsigned_char_class" }, { "rgbReserved", "unsigned_char_class" }, { "bmiColors", "RGBQUAD" }, { "exData", "char_array_class" }, { "strf", "strfHEADER_BIH" }, { "wFormatTag", "WORD_class" }, { "nChannels", "WORD_class" }, { "nSamplesPerSec", "DWORD_class" }, { "nAvgBytesPerSec", "DWORD_class" }, { "nBlockAlign", "WORD_class" }, { "wBitsPerSample", "WORD_class" }, { "cbSize", "WORD_class" }, { "wave", "WAVEFORMATEX" }, { "strf_", "strfHEADER_WAVE" }, { "data__", "char_array_class" }, { "strf__", "strfHEADER" }, { "strn", "strnHEADER" }, { "gb", "genericblock" }, { "list", "LISTHEADER" }, { "junk", "JUNKHEADER" }, { "ckid", "DWORD_class" }, { "dwChunkOffset", "DWORD_class" }, { "dwChunkLength", "DWORD_class" }, { "data___", "AVIINDEXENTRY_array_class" }, { "idx1", "idx1HEADER" } };

std::vector<std::vector<int>> integer_ranges = { { 1, 16 } };

class globals_class {
public:
	/*local*/ std::string nheader;
	char_class id_element;
	char_array_class id;
	uint32_class datalen;
	char_class form_element;
	char_array_class form;
	ROOT root;
	/*local*/ std::vector<std::string> nheader_values;
	char_class type_element;
	char_array_class type;
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
	WORD_class wFormatTag;
	WORD_class nChannels;
	DWORD_class nSamplesPerSec;
	DWORD_class nAvgBytesPerSec;
	WORD_class nBlockAlign;
	WORD_class wBitsPerSample;
	WORD_class cbSize;
	WAVEFORMATEX wave;
	strfHEADER_WAVE strf_;
	char_class data___element;
	char_array_class data__;
	strfHEADER strf__;
	strnHEADER strn;
	genericblock gb;
	LISTHEADER list;
	JUNKHEADER junk;
	DWORD_class ckid;
	DWORD_class dwChunkOffset;
	DWORD_class dwChunkLength;
	AVIINDEXENTRY data____element;
	AVIINDEXENTRY_array_class data___;
	idx1HEADER idx1;
	/*local*/ uint evil_state;


	globals_class() :
		nheader(4, 0),
		id_element(false),
		id(id_element, { { 3, {{'X'}} } }),
		datalen(2),
		form_element(false),
		form(form_element),
		root(ROOT_root_instances),
		type_element(false),
		type(type_element),
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
		wFormatTag(1),
		nChannels(1),
		nSamplesPerSec(1),
		nAvgBytesPerSec(1),
		nBlockAlign(1),
		wBitsPerSample(1),
		cbSize(1),
		wave(WAVEFORMATEX_wave_instances),
		strf_(strfHEADER_WAVE_strf__instances),
		data___element(false),
		data__(data___element),
		strf__(strfHEADER_strf___instances),
		strn(strnHEADER_strn_instances),
		gb(genericblock_gb_instances),
		list(LISTHEADER_list_instances),
		junk(JUNKHEADER_junk_instances),
		ckid(1),
		dwChunkOffset(1),
		dwChunkLength(1),
		data____element(AVIINDEXENTRY_data____element_instances),
		data___(data____element),
		idx1(idx1HEADER_idx1_instances)
	{}
};

globals_class* g;


ROOT* ROOT::generate() {
	if (generated == 1) {
		ROOT* new_instance = new ROOT(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(id, ::g->id.generate(4));
	if ((::g->root().id()[3] == 'X')) {
		Printf("Motorola format\n");
		BigEndian();
	} else {
		Printf("Intel format\n");
		LittleEndian();
	};
	GENERATE_VAR(datalen, ::g->datalen.generate());
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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
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

	GENERATE_VAR(fccType, ::g->fccType.generate(4, { "vids", "auds" }));
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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
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
	GENERATE_VAR(biBitCount, ::g->biBitCount.generate());
	GENERATE_VAR(biCompression, ::g->biCompression.generate());
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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
	GENERATE_VAR(bmiHeader, ::g->bmiHeader.generate());
	sz = bmiHeader()._sizeof;
	if ((datalen() == 44)) {
		GENERATE_VAR(bmiColors, ::g->bmiColors.generate());
		sz += 4;
	};
	Printf("left: %d\n", sz);
	GENERATE_VAR(exData, ::g->exData.generate((datalen() - sz)));

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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
	GENERATE_VAR(wave, ::g->wave.generate());
	GENERATE_VAR(exData, ::g->exData.generate((datalen() - 18)));

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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
	if ((datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(datalen()));
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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
	if ((datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(datalen()));
	};

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
	GENERATE_VAR(datalen, ::g->datalen.generate());
	if ((datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(datalen()));
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

	GENERATE_VAR(id, ::g->id.generate(4));
	GENERATE_VAR(datalen, ::g->datalen.generate());
	GENERATE_VAR(type, ::g->type.generate(4, { "hdrl", "strl", "movi" }));
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
		GENERATE_VAR(strn, ::g->strn.generate());
	} else {
	if ((Memcmp(type(), "movi", 4) == 0)) {
		pointer = 0;
		stop = (datalen() - 4);
		do {
			GENERATE_VAR(gb, ::g->gb.generate());
			pointer += gb()._sizeof;
		} while ((pointer != stop));
	} else {
		GENERATE_VAR(data, ::g->data__.generate((datalen() - 4)));
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
	GENERATE_VAR(datalen, ::g->datalen.generate());
	if ((datalen() % 2)) {
		GENERATE_VAR(data, ::g->data__.generate((datalen() + 1)));
	} else {
		GENERATE_VAR(data, ::g->data__.generate(datalen()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


AVIINDEXENTRY* AVIINDEXENTRY::generate() {
	if (generated == 1) {
		AVIINDEXENTRY* new_instance = new AVIINDEXENTRY(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(ckid, ::g->ckid.generate());
	GENERATE_VAR(dwFlags, ::g->dwFlags.generate());
	GENERATE_VAR(dwChunkOffset, ::g->dwChunkOffset.generate());
	GENERATE_VAR(dwChunkLength, ::g->dwChunkLength.generate());

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
	GENERATE_VAR(datalen, ::g->datalen.generate());
	GENERATE_VAR(data, ::g->data___.generate(datalen()));

	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	GENERATE(root, ::g->root.generate());
	::g->nheader_values = { "LIST", "JUNK", "idx1" };
	while (!FEof()) {
		::g->evil_state = SetEvilBit(false);
		ReadBytes(::g->nheader, FTell(), 4, ::g->nheader_values);
		SetEvilBit(::g->evil_state);
		if ((Memcmp(::g->nheader, "LIST", 4) == 0)) {
			GENERATE(list, ::g->list.generate());
		} else {
		if ((Memcmp(::g->nheader, "JUNK", 4) == 0)) {
			GENERATE(junk, ::g->junk.generate());
		} else {
		if ((Memcmp(::g->nheader, "idx1", 4) == 0)) {
			GENERATE(idx1, ::g->idx1.generate());
		} else {
			if (!FEof()) {
				Printf("unknown chunk: %c%c%c%c", ::g->nheader[0], ::g->nheader[1], ::g->nheader[2], ::g->nheader[3]);
			};
			exit_template(-1);
		};
		};
		};
	};

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

