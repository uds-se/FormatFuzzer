#ifndef BT_H
#define BT_H

#include <cstdio>
#include <cstdlib>
#include <string>
#include <cstring>
#include <vector>
#include <stdarg.h>

#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>

#include "file_accessor.h"


typedef unsigned int UINT;
typedef char byte;
typedef char CHAR;
typedef char BYTE;
typedef unsigned char uchar;
typedef unsigned char ubyte;
typedef unsigned char UCHAR;
typedef unsigned char UBYTE;
typedef short int16;
typedef short SHORT;
typedef short INT16;
typedef unsigned short uint16;
typedef unsigned short ushort;
typedef unsigned short USHORT;
typedef unsigned short UINT16;
typedef unsigned short WORD;
typedef int int32;
typedef int INT;
typedef int INT32;
typedef long LONG;
typedef unsigned int uint;
typedef unsigned int uint32;
typedef unsigned long ulong;
typedef unsigned int UINT;
typedef unsigned int UINT32;
typedef unsigned long ULONG;
typedef unsigned int DWORD;
typedef long long int64;
typedef long long quad;
typedef long long QUAD;
typedef long long INT64;
typedef long long __int64;
typedef unsigned long long uint64;
typedef unsigned long long uquad;
typedef unsigned long long UQUAD;
typedef unsigned long long UINT64;
typedef unsigned long long QWORD;
typedef unsigned long long __uint64;
typedef float FLOAT;
typedef double DOUBLE;
typedef float hfloat;
typedef float HFLOAT;
typedef unsigned long long OLETIME;
typedef long time_t;

const int CHECKSUM_BYTE = 0;
const int CHECKSUM_SHORT_LE = 1;
const int CHECKSUM_SHORT_BE = 2;
const int CHECKSUM_INT_LE = 3;
const int CHECKSUM_INT_BE = 4;
const int CHECKSUM_INT64_LE = 5;
const int CHECKSUM_INT64_BE = 6;
const int CHECKSUM_SUM8 = 7;
const int CHECKSUM_SUM16 = 8;
const int CHECKSUM_SUM32 = 9;
const int CHECKSUM_SUM64 = 10;
const int CHECKSUM_CRC16 = 11;
const int CHECKSUM_CRCCCITT = 12;
const int CHECKSUM_CRC32 = 13;
const int CHECKSUM_ADLER32 = 14;
const int FINDMETHOD_NORMAL = 0;
const int FINDMETHOD_WILDCARDS = 1;
const int FINDMETHOD_REGEX = 2;
const int cBlack = 0x000000;
const int cRed = 0x0000ff;
const int cDkRed = 0x000080;
const int cLtRed = 0x8080ff;
const int cGreen = 0x00ff00;
const int cDkGreen = 0x008000;
const int cLtGreen = 0x80ff80;
const int cBlue = 0xff0000;
const int cDkBlue = 0x800000;
const int cLtBlue = 0xff8080;
const int cPurple = 0xff00ff;
const int cDkPurple = 0x800080;
const int cLtPurple = 0xffe0ff;
const int cAqua = 0xffff00;
const int cDkAqua = 0x808000;
const int cLtAqua = 0xffffe0;
const int cYellow = 0x00ffff;
const int cDkYellow = 0x008080;
const int cLtYellow = 0x80ffff;
const int cDkGray = 0x404040;
const int cGray = 0x808080;
const int cSilver = 0xc0c0c0;
const int cLtGray = 0xe0e0e0;
const int cWhite = 0xffffff;
const int cNone = 0xffffffff;
const int True = 1;
const int TRUE = 1;
const int False = 0;
const int FALSE = 0;

#define GENERATE_VAR(name, value) do { \
	start_generation(#name);       \
	name ## _var = (value);        \
	name ## _exists = true;        \
	end_generation();              \
	} while (0)

#define GENERATE(name, value) do {     \
	start_generation(#name);       \
	(value);                       \
	end_generation();              \
	} while (0)

#define GENERATE_EXISTS(name, value)   \
	name ## _exists = true


unsigned long long STR2INT(std::string s) {
	assert(s.size() <= 8);
	unsigned long long result = 0;
	for (char& c : s) {
		result = (result << 8) | c;
	}
	return result;
}

constexpr unsigned long long STR2INT(const char * s) {
	assert(strlen(s) <= 8);
	unsigned long long result = 0;
	while (*s) {
		result = (result << 8) | *s;
		++s;
	}
	return result;
}

unsigned char rand_buffer[MAX_RAND_SIZE];
file_accessor file_acc;

extern bool is_big_endian;
extern bool is_padded_bitfield;
void generate_file();


void start_generation(const char* name) {
	if (!get_parse_tree)
		return;
	generator_stack.emplace_back(name);
}

void end_generation() {
	if (!get_parse_tree)
		return;
	stack_cell& back = generator_stack.back();
	stack_cell& prev = generator_stack[generator_stack.size() - 2];
	printf("%u,%u,", back.min, back.max);
	bool first = true;
	stack_cell* parent = NULL;
	for (auto& cell : generator_stack) {
		if (first) {
			printf("%s", cell.name);
			first = false;
		} else {
			printf("~%s", cell.name);
			if (parent->counts[cell.name])
				printf("_%u", parent->counts[cell.name]);
		}
		parent = &cell;
	}
	printf(",Enabled\n");
	if (back.min < prev.min)
		prev.min = back.min;
	if (back.max > prev.max)
		prev.max = back.max;
	++prev.counts[back.name];
	generator_stack.pop_back();
}


char* get_bin_name(char* arg) {
	char* bin = strrchr(arg, '/');
	if (bin)
		return bin+1;
	return arg;
}


void set_parser() {
	file_acc.generate = false;
}


void setup_input(const char* filename) {
	debug_print = true;
	int file_fd;
	if (strcmp(filename, "-") == 0)
		file_fd = STDIN_FILENO;
	else
		file_fd = open(filename, O_RDONLY);
    
	if (file_fd == -1) {
		perror(filename);
		exit(1);
	}
    
    if (file_fd == STDIN_FILENO) {
        // Read from stdin, up to MAX_RAND_SIZE
        unsigned char *p = rand_buffer;
		ssize_t size;
		ssize_t chars_left = MAX_RAND_SIZE;
        
        while (chars_left > 0 && 
               (size = read(file_fd, p, chars_left)) > 0)
        {
            p += size;
            chars_left -= size;
        }
        if (chars_left == 0)
        {
			perror("Standard input size exceeds MAX_RAND_SIZE");
			exit(1);
        }
        ssize_t total = p - rand_buffer;
		file_acc.seed(rand_buffer, MAX_RAND_SIZE, total);
    }
	if (file_acc.generate) {
		ssize_t size = read(file_fd, rand_buffer, MAX_RAND_SIZE);
		if (size < 0) {
			perror("Failed to read seed file");
			exit(1);
		}
		file_acc.seed(rand_buffer, size, 0);
	} else {
		get_parse_tree = true;
		struct stat st;
		if (fstat(file_fd, &st)) {
			perror("Failed to stat input file");
			exit(1);
		}
		if (st.st_size > MAX_FILE_SIZE) {
			fprintf(stderr, "File size exceeds MAX_FILE_SIZE\n");
			exit(1);
		}
		ssize_t size = read(file_fd, file_acc.file_buffer, st.st_size);
		if (size != st.st_size) {
			perror("Failed to read input file");
			exit(1);
		}
		file_acc.seed(rand_buffer, MAX_RAND_SIZE, st.st_size);
	}
    
	if (file_fd != STDIN_FILENO)
		close(file_fd);
}

void save_output(const char* filename) {
	int file_fd;
	if (strcmp(filename, "-") == 0)
		file_fd = STDOUT_FILENO;
	else
		file_fd = open(filename, O_CREAT | O_WRONLY | O_TRUNC, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
    
	if (file_fd == -1) {
		perror(filename);
		exit(1);
	}
	if (file_acc.generate) {
		ssize_t res = write(file_fd, file_acc.file_buffer, file_acc.file_size);
		if (res != file_acc.file_size)
			fprintf(stderr, "Failed to write file\n");
	} else {
		ssize_t res = write(file_fd, rand_buffer, file_acc.rand_pos);
		if (res != file_acc.rand_pos)
			fprintf(stderr, "Failed to write file\n");
	}
    
	if (file_fd != STDOUT_FILENO)
        close(file_fd);
}

void delete_globals();

extern "C" size_t afl_pre_save_handler(unsigned char* data, size_t size, unsigned char** new_data) {
	file_acc.seed(data, size, 0);
	try {
		generate_file();
	} catch (...) {
		delete_globals();
		*new_data = NULL;
		return 0;
	}
	*new_data = file_acc.file_buffer;
	return file_acc.file_size;
}

void exit_template(int status) {
	if (debug_print)
		fprintf(stderr, "Template exited with code %d\n", status);
	throw status;
}

bool change_array_length = false;

void check_array_length(unsigned& size) {
	if (change_array_length && size > MAX_FILE_SIZE/16 && file_acc.generate) {
		unsigned new_size = file_acc.rand_int(16, NULL);
		if (debug_print)
			fprintf(stderr, "Array length too large: %d, replaced with %u\n", (signed)size, new_size);
		// throw 0;
		size = new_size;
	}
}

void BigEndian() { is_big_endian = true; }
void LittleEndian() { is_big_endian = false; }
int IsBigEndian() { return is_big_endian; }

void BitfieldLeftToRight() {
	is_bitfield_left_to_right[is_big_endian] = true;
}

void BitfieldEnablePadding() {
	is_padded_bitfield = true;
}

void BitfieldDisablePadding() {
	is_padded_bitfield = false;
}

void SetBackColor(int color) { }

uint32 Checksum(int checksum_type, int64 start, int64 size) {
	assert_cond(start + size <= file_acc.file_size, "checksum range invalid");
	switch(checksum_type) {
	case CHECKSUM_CRC32: {
		return crc32(0, file_acc.file_buffer + start, size);
	}
	default:
		abort();
	}
}

void Warning(std::string s) {
	if (debug_print)
		fprintf(stderr, "Warning: %s\n", s.c_str());
}

void Printf(const std::string fmt, ...) {
	if (!debug_print)
		return;
	va_list args;
	va_start(args,fmt);
	vprintf(fmt.c_str(),args);
	va_end(args);
}

void SPrintf(std::string& s, const char* fmt, ...) {
	char res[4096];
	va_list args;
	va_start(args,fmt);
	vsnprintf(res, 4096, fmt, args);
	va_end(args);
	s = res;
}

std::string::size_type Strlen(std::string s) { return s.size(); }

int Strncmp(std::string s1, std::string s2, int n) {
	return strncmp(s1.c_str(), s2.c_str(), n);
}

std::string SubStr(std::string s, int start, int count = -1) {
	size_t len = s.length();
	assert_cond((unsigned)start < len, "SubStr: invalid position");
	if (count == -1)
		return std::string(s.c_str() + start, len - start);
	assert_cond((unsigned)count <= len - start, "SubStr: invalid count");
	return std::string(s.c_str() + start, count);
}

void Memcpy(std::string& dest, std::string src, int n, int destOffset = 0, int srcOffset = 0) {
	// Other configurations not yet handled
	assert(destOffset == 0 && srcOffset == 0);
	assert ((unsigned) n <= src.length());
	dest = std::string(src.c_str(), n);
}

int FEof() { return file_acc.feof(); }

int64 FTell() { return file_acc.file_pos; }

int FSeek(int64 pos) {
	assert_cond(0 <= pos && pos < MAX_FILE_SIZE, "FSeek: invalid position");
	file_acc.file_pos = pos;
	return 0;
}
int FSkip(int64 offset) {
	file_acc.file_pos += offset;
	assert_cond(0 <= file_acc.file_pos && file_acc.file_pos < MAX_FILE_SIZE, "FSkip: invalid position");
	return 0;
}

int64 FileSize() {
	static bool has_size = false;
	if (!has_size) {
		file_acc.file_size = file_acc.file_pos + file_acc.rand_int(MAX_FILE_SIZE + 1 - file_acc.file_pos, [](unsigned char* file_buf) -> long long { return file_acc.file_size - file_acc.file_pos; } );
		has_size = true;
	}
	return file_acc.file_size;
}

template<typename T>
int64 FindFirst(T data, int matchcase=true, int wholeword=false, int method=0, double tolerance=0.0, int dir=1, int64 start=0, int64 size=0, int wildcardMatchLength=24) {
	// Other configurations not yet handled
	assert(matchcase == true && wholeword == false && method == 0 && tolerance == 0.0 && dir == 1 && size == 0 && wildcardMatchLength == 24);
	T newdata = data;
	swap_bytes(&newdata, sizeof(T));
	if (file_acc.evil( [&start, &newdata](unsigned char* file_buf) -> bool {
			return memmem(file_acc.file_buffer + start, file_acc.file_size - start, &newdata, sizeof(T)) == NULL;
		} )) {
		return -1;
	}
	int64 pos = start + file_acc.rand_int(MAX_FILE_SIZE + 1 - sizeof(T) - start, [&start, &newdata](unsigned char* file_buf) -> long long {
			return (unsigned char *)memmem(file_acc.file_buffer + start, file_acc.file_size - start, &newdata, sizeof(T)) - (file_acc.file_buffer + start);
		} );
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	std::vector<T> values = { data };
	bool evil = file_acc.set_evil_bit(false);
	file_acc.file_integer(sizeof(T), 0, values);
	file_acc.set_evil_bit(evil);
        FSeek(original_pos);
        file_acc.lookahead = false;
        return pos;

}

extern std::vector<std::string> ReadBytesInitValues;

void ReadBytes(std::string& s, int64 pos, int n, std::vector<std::string> new_known_values = {}) {
	assert_cond(n > 0, "ReadBytes: invalid number of bytes");
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	for (auto& known : ReadBytesInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		s = file_acc.file_string(new_known_values);
	else
		s = file_acc.file_string(n);
	FSeek(original_pos);
	file_acc.lookahead = false;
}

extern std::vector<char> ReadByteInitValues;

char ReadByte(int64 pos = FTell(), std::vector<char> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	char value;
	for (auto& known : ReadByteInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(char), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(char), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<uchar> ReadUByteInitValues;

uchar ReadUByte(int64 pos = FTell(), std::vector<uchar> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	uchar value;
	for (auto& known : ReadUByteInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(uchar), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(uchar), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<short> ReadShortInitValues;

short ReadShort(int64 pos = FTell(), std::vector<short> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	short value;
	for (auto& known : ReadShortInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(short), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(short), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<ushort> ReadUShortInitValues;

ushort ReadUShort(int64 pos = FTell(), std::vector<ushort> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	ushort value;
	for (auto& known : ReadUShortInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(ushort), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(ushort), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<int> ReadIntInitValues;

int ReadInt(int64 pos = FTell(), std::vector<int> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	int value;
	for (auto& known : ReadIntInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(int), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(int), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<uint> ReadUIntInitValues;

uint ReadUInt(int64 pos = FTell(), std::vector<uint> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	uint value;
	for (auto& known : ReadUIntInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(uint), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(uint), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<int64> ReadQuadInitValues;

int64 ReadQuad(int64 pos = FTell(), std::vector<int64> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	int64 value;
	for (auto& known : ReadQuadInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(int64), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(int64), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<uint64> ReadUQuadInitValues;

uint64 ReadUQuad(int64 pos = FTell(), std::vector<uint64> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	uint64 value;
	for (auto& known : ReadUQuadInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(uint64), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(uint64), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<int64> ReadInt64InitValues;

int64 ReadInt64(int64 pos = FTell(), std::vector<int64> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	int64 value;
	for (auto& known : ReadInt64InitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(int64), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(int64), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<uint64> ReadUInt64InitValues;

uint64 ReadUInt64(int64 pos = FTell(), std::vector<uint64> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	uint64 value;
	for (auto& known : ReadUInt64InitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(uint64), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(uint64), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<hfloat> ReadHFloatInitValues;

hfloat ReadHFloat(int64 pos = FTell(), std::vector<hfloat> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	hfloat value;
	for (auto& known : ReadHFloatInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(hfloat), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(hfloat), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<float> ReadFloatInitValues;

float ReadFloat(int64 pos = FTell(), std::vector<float> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	float value;
	for (auto& known : ReadFloatInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(float), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(float), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}

extern std::vector<double> ReadDoubleInitValues;

double ReadDouble(int64 pos = FTell(), std::vector<double> new_known_values = {}) {
	file_acc.lookahead = true;
	int64 original_pos = FTell();
	FSeek(pos);
	double value;
	for (auto& known : ReadDoubleInitValues) {
		new_known_values.push_back(known);
	}
	if (new_known_values.size())
		value = file_acc.file_integer(sizeof(double), 0, new_known_values);
	else
		value = file_acc.file_integer(sizeof(double), 0);
	FSeek(original_pos);
	file_acc.lookahead = false;
	return value;
}


#endif
