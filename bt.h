#ifndef BT_H
#define BT_H

#include <cstdio>
#include <cstdlib>
#include <string>
#include <cstring>
#include <vector>
#include <unordered_set>
#include <stdarg.h>

#include <boost/crc.hpp>

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
typedef int LONG;
typedef unsigned int uint;
typedef unsigned int uint32;
//typedef unsigned int ulong;
typedef unsigned int UINT;
typedef unsigned int UINT32;
typedef unsigned int ULONG;
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
#ifndef __clang__
	assert(strlen(s) <= 8);
#endif
	unsigned long long result = 0;
	while (*s) {
		result = (result << 8) | *s;
		++s;
	}
	return result;
}

extern unsigned char *rand_buffer;
file_accessor file_acc;

extern bool is_big_endian;
extern bool is_padded_bitfield;
void generate_file();

bool aflsmart_output = false;

double get_validity() {
	return (double)file_acc.parsed_file_size / (double)file_acc.final_file_size;
}


void start_generation(const char* name) {
	if (!get_parse_tree)
		return;
	generator_stack.emplace_back(name, file_acc.rand_prev, file_acc.rand_pos);
	file_acc.rand_prev = file_acc.rand_pos;
	file_acc.rand_last = UINT_MAX;
}

void end_generation() {
	if (!get_parse_tree)
		return;
	stack_cell& back = generator_stack.back();
	stack_cell& prev = generator_stack[generator_stack.size() - 2];
	file_acc.rand_prev = file_acc.rand_pos;
	
	if (smart_mutation && back.rand_start == rand_start && (is_optional || strcmp(back.name, chunk_name) == 0)) {
		unsigned size = MAX_RAND_SIZE - file_acc.rand_pos;
		if (size > MAX_RAND_SIZE - (rand_end + 1))
			size = MAX_RAND_SIZE - (rand_end + 1);
		memmove(file_acc.rand_buffer + file_acc.rand_pos, file_acc.rand_buffer + (rand_end + 1), size);
		if (smart_swapping) {
			if (rand_start2 > rand_end)
				rand_start2 += file_acc.rand_pos - (rand_end + 1);
			rand_end2 += file_acc.rand_pos - (rand_end + 1);
		}
		rand_end = file_acc.rand_pos - 1;
	}
	if (smart_swapping && back.rand_start == rand_start2 && (is_optional || strcmp(back.name, chunk_name2) == 0)) {
		unsigned size = MAX_RAND_SIZE - file_acc.rand_pos;
		if (size > MAX_RAND_SIZE - (rand_end2 + 1))
			size = MAX_RAND_SIZE - (rand_end2 + 1);
		memmove(file_acc.rand_buffer + file_acc.rand_pos, file_acc.rand_buffer + (rand_end2 + 1), size);
		rand_end2 = file_acc.rand_pos - 1;
	}
	if (smart_abstraction && back.rand_start == rand_start && (is_optional || strcmp(back.name, chunk_name) == 0)) {
		if (following_rand_size > MAX_RAND_SIZE - file_acc.rand_pos)
			following_rand_size = MAX_RAND_SIZE - file_acc.rand_pos;
		memcpy(file_acc.rand_buffer + file_acc.rand_pos, following_rand_buffer, following_rand_size);
		smart_abstraction = false;
	}

	if (back.min < prev.min)
		prev.min = back.min;
	if (back.max > prev.max)
		prev.max = back.max;

	if (back.min > back.max) {
		back.min = file_acc.file_pos;
		back.max = file_acc.file_pos - 1;
	}
	if (debug_print && back.min <= back.max) {
		// printf("%u,%u, ", back.rand_start, file_acc.rand_pos - 1);
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
		if (aflsmart_output) {
			printf(",Enabled\n");
		} else {
			if (file_acc.rand_last != UINT_MAX)
				printf(",Appendable");
			if (back.rand_start != back.rand_start_real)
				printf(",Optional\n");
			else
				printf("\n");
		}
	}

	if (get_chunk && back.min == chunk_start && back.max == chunk_end) {
		printf("TARGET CHUNK FOUND\n");
		rand_start = back.rand_start;
		rand_end = file_acc.rand_pos - 1;
		is_optional = back.rand_start != back.rand_start_real;
		chunk_name = back.name;
		if (is_delete) {
			is_following = true;
		}
	}

	if (get_chunk && chunk_end == UINT_MAX && back.max == chunk_start - 1 && file_acc.rand_last != UINT_MAX) {
		printf("APPENDABLE CHUNK FOUND\n");
		rand_start = file_acc.rand_last;
		chunk_name = back.name;
	}
	
	if (get_chunk && chunk_end == UINT_MAX && back.min == chunk_start && back.rand_start != back.rand_start_real) {
		printf("OPTIONAL CHUNK FOUND\n");
		rand_start = back.rand_start;
		chunk_name = back.name;
	}
	
	if (get_all_chunks) {
		if (back.rand_start != back.rand_start_real) {
			optional_chunks.emplace_back(file_index, back.rand_start, file_acc.rand_pos - 1, variable_types[back.name].c_str(), back.name);
			insertion_points[file_index].emplace_back(back.rand_start, variable_types[back.name].c_str(), back.name);
			is_following = true;
			chunk_name = back.name;
			rand_start = back.rand_start;
			rand_end = file_acc.rand_pos - 1;
		} else if (file_acc.rand_pos > back.rand_start) {
			int size = non_optional_index[file_index].size();
			int i;
			for (i = 0; i < size; ++i) {
				if (strcmp(non_optional_index[file_index][i].type, variable_types[back.name].c_str()) == 0) {
					++non_optional_index[file_index][i].size;
					break;
				}
			}
			if (i == size) {
				non_optional_index[file_index].emplace_back(variable_types[back.name].c_str(), non_optional_chunks[variable_types[back.name]].size(), 1);
			}
			non_optional_chunks[variable_types[back.name]].emplace_back(file_index, back.rand_start, file_acc.rand_pos - 1, variable_types[back.name].c_str(), back.name);
		}
		if (file_acc.rand_last != UINT_MAX) {
			insertion_points[file_index].emplace_back(file_acc.rand_last, variable_types[back.name].c_str(), back.name);
		}
	}

	file_acc.rand_last = UINT_MAX;

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

void set_generator() {
	file_acc.generate = true;
}


bool setup_input(const char* filename) {
	bool success = true;
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
		ssize_t file_size = st.st_size;
		if (file_size > MAX_FILE_SIZE) {
			fprintf(stderr, "File size exceeds MAX_FILE_SIZE\n");
			file_size = MAX_FILE_SIZE;
			success = false;
		}
		ssize_t size = read(file_fd, file_acc.file_buffer, file_size);
		if (size != file_size) {
			perror("Failed to read input file");
			exit(1);
		}
		file_acc.seed(rand_buffer, MAX_RAND_SIZE, file_size);
	}
    
	if (file_fd != STDIN_FILENO)
		close(file_fd);
	return success;
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

unsigned copy_rand(unsigned char *dest) {
	memcpy(dest, file_acc.rand_buffer, file_acc.rand_pos);
	return file_acc.rand_pos;
}

void delete_globals();

extern "C" size_t ff_generate(unsigned char* data, size_t size, unsigned char** new_data) {
	file_acc.seed(data, size, 0);
	try {
		generate_file();
	} catch (int status) {
		delete_globals();
		if (status) {
			*new_data = NULL;
			return 0;
		}
	} catch (...) {
		delete_globals();
		*new_data = NULL;
		return 0;
	}
	*new_data = file_acc.file_buffer;
	return file_acc.file_size;
}

extern "C" int ff_parse(unsigned char* data, size_t size, unsigned char** new_data, size_t* new_size) {
	file_acc.generate = false;

	if (size > MAX_FILE_SIZE) {
		fprintf(stderr, "File size larger than MAX_FILE_SIZE\n");
		size = MAX_FILE_SIZE;
	}
	if (data != file_acc.file_buffer) {
		memcpy(file_acc.file_buffer, data, size);
	}
	memset(file_acc.file_buffer + size, 0, MAX_FILE_SIZE - size);
	file_acc.seed(rand_buffer, MAX_RAND_SIZE, size);
	bool success = true;
	try {
		generate_file();
	} catch (int status) {
		delete_globals();
		if (status)
			success = false;
	} catch (...) {
		delete_globals();
		success = false;
	}
	*new_data = rand_buffer;
	*new_size = file_acc.rand_pos;
	file_acc.generate = true;
	return success;
}

void exit_template(int status) {
	if (debug_print || print_errors)
		fprintf(stderr, "Template exited with code %d\n", status);
	throw status;
}

void exit_template(std::string message) {
	if (debug_print || print_errors)
		fprintf(stderr, "Template exited with message: %s\n", message.c_str());
	throw -1;
}

void Assert(int value, const char* msg = "") {
	if (!value)
		exit_template(msg);
}

bool change_array_length = false;

void check_array_length(unsigned& size) {
	if (change_array_length && size > MAX_FILE_SIZE/16 && file_acc.generate) {
		unsigned new_size = file_acc.rand_int(16, file_acc.parse);
		if (debug_print)
			fprintf(stderr, "Array length too large: %d, replaced with %u\n", (signed)size, new_size);
		size = new_size;
	}
	assert_cond(size <= MAX_FILE_SIZE - file_acc.file_pos, "Array length too large");
}

void ChangeArrayLength() {
	change_array_length = true;
}

void EndChangeArrayLength() {
	change_array_length = false;
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

void DisplayFormatBinary() { }
void DisplayFormatDecimal() { }
void DisplayFormatHex() { }
void DisplayFormatOctal() { }

int SetEvilBit(int allow) {
	return file_acc.set_evil_bit(allow);
}

uint32 Checksum(int checksum_type, int64 start, int64 size) {
	assert_cond(start + size <= file_acc.file_size, "checksum range invalid");
	switch(checksum_type) {
	case CHECKSUM_CRC16: {
		boost::crc_16_type res;
		res.process_bytes(file_acc.file_buffer + start, size);
		return res.checksum();
	}
	case CHECKSUM_CRC32: {
		boost::crc_32_type res;
		res.process_bytes(file_acc.file_buffer + start, size);
		return res.checksum();
	}
	default:
		abort();
	}
}

void Warning(const std::string fmt, ...) {
	if (!debug_print && !print_errors)
		return;
	fprintf(stderr, "Warning: ");
	va_list args;
	va_start(args,fmt);
	vfprintf(stderr, fmt.c_str(), args);
	va_end(args);
	fprintf(stderr, "\n");
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

int Atoi(std::string s) {
	return atoi(s.c_str());
}

int Strlen(std::string s) { return s.size(); }

int Strcmp(std::string s1, std::string s2) {
	return strcmp(s1.c_str(), s2.c_str());
}

int Strncmp(std::string s1, std::string s2, int n) {
	assert ((unsigned) n <= s1.length() && (unsigned) n <= s2.length());
	return strncmp(s1.c_str(), s2.c_str(), n);
}

int Strstr(std::string s1, std::string s2) {
	return s1.find(s2);
}

std::string SubStr(std::string s, int start, int count = -1) {
	size_t len = s.length();
	assert_cond((unsigned)start < len, "SubStr: invalid position");
	if (count == -1)
		return std::string(s.c_str() + start, len - start);
	assert_cond((unsigned)count <= len - start, "SubStr: invalid count");
	return std::string(s.c_str() + start, count);
}

int Memcmp(std::string s1, std::string s2, int n) {
	assert ((unsigned) n <= s1.length() && (unsigned) n <= s2.length());
	return memcmp(s1.c_str(), s2.c_str(), n);
}

void Memcpy(std::string& dest, std::string src, int n, int destOffset = 0, int srcOffset = 0) {
	// Other configurations not yet handled
	assert(destOffset == 0 && srcOffset == 0);
	assert ((unsigned) n <= src.length());
	dest = std::string(src.c_str(), n);
}

int IsParsing() {
	return !file_acc.generate;
}

int FEof(double p = 0.125) { return file_acc.feof(p); }

int64 FTell() { return file_acc.file_pos; }

int FSeek(int64 pos, bool print = true) {
	assert_cond(0 <= pos && pos <= MAX_FILE_SIZE, "FSeek/FSkip: invalid position");
	if (print && debug_print && file_acc.file_pos != pos)
		fprintf(stderr, "FSeek from %u to %lld\n", file_acc.file_pos, pos);
	if (pos > file_acc.file_size) {
		if (debug_print)
			fprintf(stderr, "Padding file from %u to %lld\n", file_acc.file_size, pos);
		file_acc.file_pos = file_acc.file_size;
		file_acc.is_padding = true;
		while (file_acc.file_pos < pos) {
			file_acc.file_integer(1, 0, 0);
		}
		file_acc.is_padding = false;
	} else {
		file_acc.file_pos = pos;
	}
	return 0;
}

int FSkip(int64 offset) {
	if (debug_print && offset != 0)
		fprintf(stderr, "FSkip from %u to %lld\n", file_acc.file_pos, file_acc.file_pos + offset);
	return FSeek(file_acc.file_pos + offset, false);
}

int64 FileSize() {
	if (!file_acc.has_size) {
		file_acc.lookahead = true;
		if (!file_acc.generate)
			file_acc.parse = [](unsigned char* file_buf) -> long long { return file_acc.final_file_size - file_acc.file_size; };
		unsigned new_file_size = file_acc.file_size + file_acc.rand_int(MAX_FILE_SIZE + 1 - file_acc.file_size, file_acc.parse);
		file_acc.lookahead = false;
		if (debug_print)
			fprintf(stderr, "FileSize %u\n", new_file_size);
		int64 original_pos = FTell();
		FSeek(new_file_size, false);
		FSeek(original_pos, false);
		file_acc.has_size = true;
	}
	return file_acc.file_size;
}

unsigned get_file_size() {
	return file_acc.file_size;
}


class TFindResults {
public:
	int count_var = 0;
	std::vector<long> start_var;
	std::vector<long> size_var;

	int& count() { return count_var; }
	std::vector<long>& start() { return start_var; }
	std::vector<long>& size() { return size_var; }
};


template<typename T>
TFindResults FindAll(T data, int matchcase=true, int wholeword=false, int method=0, double tolerance=0.0, int dir=1, int64 start=0, int64 size=0, int wildcardMatchLength=24) {
	// Arbitrary types T not yet handled
	abort();
}


template<>
TFindResults FindAll(const char* data, int matchcase, int wholeword, int method, double tolerance, int dir, int64 start, int64 size, int wildcardMatchLength) {
	// Other configurations not yet handled
	assert(matchcase == true && wholeword == false && method == 0 && tolerance == 0.0 && dir == 1 && size == 0 && wildcardMatchLength == 24);

	// This function is currently only implemented in parsing mode
	assert(!file_acc.generate);

	unsigned data_size = strlen(data);
	TFindResults res;
	while (true) {
		unsigned char* p = (unsigned char*) memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, data, data_size);
		if (!p)
			break;
		++res.count_var;
		res.start_var.push_back(p - file_acc.file_buffer);
		res.size_var.push_back(data_size);
		start = (p - file_acc.file_buffer) + 1;
	}
	return res;
}

template<typename T>
int64 FindFirst(T data, int matchcase=true, int wholeword=false, int method=0, double tolerance=0.0, int dir=1, int64 start=0, int64 size=0, int wildcardMatchLength=24) {
	// Other configurations not yet handled
	assert(matchcase == true && wholeword == false && method == 0 && tolerance == 0.0 && dir == 1 && size == 0 && wildcardMatchLength == 24);

	T newdata = data;
	swap_bytes(&newdata, sizeof(T));

	file_acc.lookahead = true;
	if (!file_acc.generate)
		file_acc.evil_parse = [&start, &newdata](unsigned char* file_buf) -> bool {
			return memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, &newdata, sizeof(T)) == NULL;
		};
	if (file_acc.evil(file_acc.evil_parse)) {
		file_acc.lookahead = false;
		return -1;
	}
	if (!file_acc.generate)
		file_acc.parse = [&start, &newdata](unsigned char* file_buf) -> long long {
			return (unsigned char *)memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, &newdata, sizeof(T)) - (file_acc.file_buffer + start);
		};
	int64 pos = start + file_acc.rand_int(MAX_FILE_SIZE + 1 - sizeof(T) - start, file_acc.parse);
	int64 original_pos = FTell();
	FSeek(pos);
	std::vector<T> values = { data };
	bool evil = file_acc.set_evil_bit(false);
	file_acc.file_integer(sizeof(T), 0, values);
	file_acc.set_evil_bit(evil);
        file_acc.lookahead = false;
        FSeek(original_pos);
        return pos;

}


template<>
int64 FindFirst(std::string data, int matchcase, int wholeword, int method, double tolerance, int dir, int64 start, int64 size, int wildcardMatchLength) {
	// Other configurations not yet handled
	assert(matchcase == true && wholeword == false && method == 0 && tolerance == 0.0 && dir == 1 && size == 0 && wildcardMatchLength == 24);

	file_acc.lookahead = true;
	if (!file_acc.generate)
		file_acc.evil_parse = [&start, &data](unsigned char* file_buf) -> bool {
			return memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, data.c_str(), data.size()) == NULL;
		};
	if (file_acc.evil(file_acc.evil_parse)) {
		file_acc.lookahead = false;
		return -1;
	}
	if (!file_acc.generate)
		file_acc.parse = [&start, &data](unsigned char* file_buf) -> long long {
			return (unsigned char *)memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, data.c_str(), data.size()) - (file_acc.file_buffer + start);
		};
	int64 pos = start + file_acc.rand_int(MAX_FILE_SIZE + 1 - data.size() - start, file_acc.parse);
	int64 original_pos = FTell();
	FSeek(pos);
	std::vector<std::string> values = { data };
	bool evil = file_acc.set_evil_bit(false);
	file_acc.file_string(values);
	file_acc.set_evil_bit(evil);
        file_acc.lookahead = false;
        FSeek(original_pos);
        return pos;

}


template<>
int64 FindFirst(const char* data, int matchcase, int wholeword, int method, double tolerance, int dir, int64 start, int64 size, int wildcardMatchLength) {
	// Other configurations not yet handled
	assert(matchcase == true && wholeword == false && method == 0 && tolerance == 0.0 && dir == 1 && size == 0 && wildcardMatchLength == 24);

	file_acc.lookahead = true;
	if (!file_acc.generate)
		file_acc.evil_parse = [&start, &data](unsigned char* file_buf) -> bool {
			return memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, data, strlen(data)) == NULL;
		};
	if (file_acc.evil(file_acc.evil_parse)) {
		file_acc.lookahead = false;
		return -1;
	}
	if (!file_acc.generate)
		file_acc.parse = [&start, &data](unsigned char* file_buf) -> long long {
			return (unsigned char *)memmem(file_acc.file_buffer + start, file_acc.final_file_size - start, data, strlen(data)) - (file_acc.file_buffer + start);
		};
	int64 pos = start + file_acc.rand_int(MAX_FILE_SIZE + 1 - strlen(data) - start, file_acc.parse);
	int64 original_pos = FTell();
	FSeek(pos);
	std::vector<std::string> values = { data };
	bool evil = file_acc.set_evil_bit(false);
	file_acc.file_string(values);
	file_acc.set_evil_bit(evil);
        file_acc.lookahead = false;
        FSeek(original_pos);
        return pos;

}


template<typename T>
void VectorRemove(std::vector<T>& vec, std::unordered_set<T> set) {
	vec.erase(std::remove_if(vec.begin(), vec.end(), [&set](T s) { return set.find(s) != set.end(); }), vec.end());
}

std::string ReadLine(int64 pos, int maxLen = -1, int includeLinefeeds = true) {
	// This function is currently only implemented in parsing mode
	assert(!file_acc.generate);

	unsigned end = file_acc.final_file_size;
	if (maxLen >= 0 && pos + maxLen < file_acc.final_file_size)
		end = pos + maxLen;

	unsigned i;
	for (i = pos; i < end; ++i) {
		unsigned char c = file_acc.file_buffer[i];
		if (c == '\0' || c == '\n') {
			if (includeLinefeeds && c == '\n')
				++i;
			break;
		}
	}
	return std::string((const char *) file_acc.file_buffer + pos, i - pos);
}


extern std::vector<std::string> ReadBytesInitValues;

bool ReadBytes(std::string& s, int64 pos, int n) {
	assert_cond(n > 0, "ReadBytes: invalid number of bytes");
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;

	if (ReadBytesInitValues.size())
		s = file_acc.file_string(ReadBytesInitValues);
	else
		s = file_acc.file_string(n);

	file_acc.lookahead = false;
	FSeek(original_pos);
	return true;
}

bool ReadBytes(std::string& s, int64 pos, int n, std::vector<std::string> preferred_values, std::vector<std::string> possible_values = {}, double p = 0.25) {
	assert_cond(n > 0, "ReadBytes: invalid number of bytes");
	int64 original_pos = FTell();
	file_acc.file_pos = pos;
	file_acc.lookahead = true;

	int evil = SetEvilBit(false);
	if (possible_values.size() && ReadBytesInitValues.size()) {
		if (!file_acc.generate && preferred_values.size()) {
			file_acc.parse = [&preferred_values, &possible_values, &n](unsigned char* file_buf) -> long long {
					if (file_acc.file_pos + n > file_acc.final_file_size)
						return 0;
			        	if (std::find(preferred_values.begin(), preferred_values.end(), std::string((char*)file_buf, n)) != preferred_values.end())
			        		return 0;
			        	if (std::find(possible_values.begin(), possible_values.end(), std::string((char*)file_buf, n)) != possible_values.end())
			        		return 253;
			        	return 255;
			        };
		} else if (!file_acc.generate) {
			file_acc.parse = [&possible_values, &n](unsigned char* file_buf) -> long long {
					if (file_acc.file_pos + n > file_acc.final_file_size)
						return 0;
			        	if (std::find(possible_values.begin(), possible_values.end(), std::string((char*)file_buf, n)) != possible_values.end())
			        		return 253;
			        	if (std::find(ReadBytesInitValues.begin(), ReadBytesInitValues.end(), std::string((char*)file_buf, n)) != ReadBytesInitValues.end())
			        		return 255;
			        	return 0;
			        };
		}
		int choice = file_acc.rand_int(256, file_acc.parse);
		if (choice < 255 * p) {
			if (preferred_values.size())
				s = file_acc.file_string(preferred_values);
			else {
				s = "";
			}
		} else if (choice < 254) {
			if (preferred_values.size())
				SetEvilBit(evil);
			s = file_acc.file_string(possible_values);
		} else {
			if (preferred_values.size())
				SetEvilBit(evil);
			s = file_acc.file_string(ReadBytesInitValues);
		}
	} else if (!possible_values.size() && !ReadBytesInitValues.size()) {
		if (preferred_values.size()) {
			SetEvilBit(evil);
			s = file_acc.file_string(preferred_values);
		} else {
			s = "";
		}
	} else {
		std::vector<std::string>& known_values = possible_values.size() ? possible_values : ReadBytesInitValues;
		if (!possible_values.size())
			p = 0.995;
		if (!file_acc.generate && preferred_values.size()) {
			file_acc.parse = [&preferred_values, &n](unsigned char* file_buf) -> long long {
					if (file_acc.file_pos + n > file_acc.final_file_size)
						return 0;
			        	return 255 * (std::find(preferred_values.begin(), preferred_values.end(), std::string((char*)file_buf, n)) == preferred_values.end());
			        };
		} else if (!file_acc.generate) {
			file_acc.parse = [&known_values, &n](unsigned char* file_buf) -> long long {
					if (file_acc.file_pos + n > file_acc.final_file_size)
						return 0;
			        	return 255 * (std::find(known_values.begin(), known_values.end(), std::string((char*)file_buf, n)) != known_values.end());
			        };
		}
		int choice = file_acc.rand_int(256, file_acc.parse);
		if (choice < 255 * p) {
			if (preferred_values.size())
				s = file_acc.file_string(preferred_values);
			else {
				s = "";
			}
		} else {
			if (preferred_values.size())
				SetEvilBit(evil);
			s = file_acc.file_string(known_values);
		}
	}
	SetEvilBit(evil);

	file_acc.lookahead = false;
	file_acc.file_pos = original_pos;
	return s.length() != 0;
}

extern std::vector<byte> ReadByteInitValues;

byte ReadByte(int64 pos = FTell(), std::vector<byte> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	byte value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(byte), 0, possible_values);
	else if (ReadByteInitValues.size())
		value = file_acc.file_integer(sizeof(byte), 0, ReadByteInitValues);
	else
		value = file_acc.file_integer(sizeof(byte), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<ubyte> ReadUByteInitValues;

ubyte ReadUByte(int64 pos = FTell(), std::vector<ubyte> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	ubyte value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(ubyte), 0, possible_values);
	else if (ReadUByteInitValues.size())
		value = file_acc.file_integer(sizeof(ubyte), 0, ReadUByteInitValues);
	else
		value = file_acc.file_integer(sizeof(ubyte), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<short> ReadShortInitValues;

short ReadShort(int64 pos = FTell(), std::vector<short> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	short value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(short), 0, possible_values);
	else if (ReadShortInitValues.size())
		value = file_acc.file_integer(sizeof(double), 0, ReadShortInitValues);
	else
		value = file_acc.file_integer(sizeof(short), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<ushort> ReadUShortInitValues;

ushort ReadUShort(int64 pos = FTell(), std::vector<ushort> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	ushort value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(ushort), 0, possible_values);
	else if (ReadUShortInitValues.size())
		value = file_acc.file_integer(sizeof(ushort), 0, ReadUShortInitValues);
	else
		value = file_acc.file_integer(sizeof(ushort), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<int> ReadIntInitValues;

int ReadInt(int64 pos = FTell(), std::vector<int> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	int value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(int), 0, possible_values);
	else if (ReadIntInitValues.size())
		value = file_acc.file_integer(sizeof(int), 0, ReadIntInitValues);
	else
		value = file_acc.file_integer(sizeof(int), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<uint> ReadUIntInitValues;

uint ReadUInt(int64 pos = FTell(), std::vector<uint> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	uint value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(uint), 0, possible_values);
	else if (ReadUIntInitValues.size())
		value = file_acc.file_integer(sizeof(uint), 0, ReadUIntInitValues);
	else
		value = file_acc.file_integer(sizeof(uint), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<int64> ReadQuadInitValues;

int64 ReadQuad(int64 pos = FTell(), std::vector<int64> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	int64 value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(int64), 0, possible_values);
	else if (ReadQuadInitValues.size())
		value = file_acc.file_integer(sizeof(int64), 0, ReadQuadInitValues);
	else
		value = file_acc.file_integer(sizeof(int64), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<uint64> ReadUQuadInitValues;

uint64 ReadUQuad(int64 pos = FTell(), std::vector<uint64> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	uint64 value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(uint64), 0, possible_values);
	else if (ReadUQuadInitValues.size())
		value = file_acc.file_integer(sizeof(uint64), 0, ReadUQuadInitValues);
	else
		value = file_acc.file_integer(sizeof(uint64), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<int64> ReadInt64InitValues;

int64 ReadInt64(int64 pos = FTell(), std::vector<int64> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	int64 value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(int64), 0, possible_values);
	else if (ReadInt64InitValues.size())
		value = file_acc.file_integer(sizeof(int64), 0, ReadInt64InitValues);
	else
		value = file_acc.file_integer(sizeof(int64), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<uint64> ReadUInt64InitValues;

uint64 ReadUInt64(int64 pos = FTell(), std::vector<uint64> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	uint64 value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(uint64), 0, possible_values);
	else if (ReadUInt64InitValues.size())
		value = file_acc.file_integer(sizeof(uint64), 0, ReadUInt64InitValues);
	else
		value = file_acc.file_integer(sizeof(uint64), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<hfloat> ReadHFloatInitValues;

hfloat ReadHFloat(int64 pos = FTell(), std::vector<hfloat> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	hfloat value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(hfloat), 0, possible_values);
	else if (ReadHFloatInitValues.size())
		value = file_acc.file_integer(sizeof(hfloat), 0, ReadHFloatInitValues);
	else
		value = file_acc.file_integer(sizeof(hfloat), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<float> ReadFloatInitValues;

float ReadFloat(int64 pos = FTell(), std::vector<float> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	float value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(float), 0, possible_values);
	else if (ReadFloatInitValues.size())
		value = file_acc.file_integer(sizeof(float), 0, ReadFloatInitValues);
	else
		value = file_acc.file_integer(sizeof(float), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}

extern std::vector<double> ReadDoubleInitValues;

double ReadDouble(int64 pos = FTell(), std::vector<double> possible_values = {}) {
	int64 original_pos = FTell();
	FSeek(pos);
	file_acc.lookahead = true;
	double value;
	if (possible_values.size())
		value = file_acc.file_integer(sizeof(double), 0, possible_values);
	else if (ReadDoubleInitValues.size())
		value = file_acc.file_integer(sizeof(double), 0, ReadDoubleInitValues);
	else
		value = file_acc.file_integer(sizeof(double), 0);
	file_acc.lookahead = false;
	FSeek(original_pos);
	return value;
}


#endif
