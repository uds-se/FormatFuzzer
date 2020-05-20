#ifndef BT_H
#define BT_H

#include <cstdio>
#include <cstdlib>
#include <string>
#include <cstring>
#include <vector>
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

#define EXISTS(a, b) 1

#define MAX_FILE_SIZE 4096

char* file_data;
int file_fd;
bool debug_print = true;

unsigned char rand_init[65536];
file_accessor file_acc;

extern bool is_big_endian;
void generate_file();


void setup_generation(const char* filename, bool random = true) {
	file_fd = open(filename, O_CREAT|O_RDWR|O_TRUNC, S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH);
	if (file_fd == -1) {
		perror("Failed to open file");
		exit(1);
	}
	file_data = (char*) mmap(NULL, MAX_FILE_SIZE, PROT_READ|PROT_WRITE, MAP_SHARED_VALIDATE, file_fd, 0);
	if (file_data == MAP_FAILED) {
		perror("Failed to open file");
		exit(1);
	}
	file_acc.set_fd(file_fd);

	if (!random)
		return;
	struct timespec tp;
	clock_gettime(CLOCK_REALTIME, &tp);
	std::random_device r;
	unsigned seed = tp.tv_sec ^ tp.tv_nsec ^ getpid() ^ r();
	if (debug_print)
		fprintf(stderr, "Seed %u\n", seed);
	srand(seed);

	for (int i = 0; i < 65536; ++i)
		rand_init[i] = rand();
	
	file_acc.seed(rand_init, 65536);
}

void delete_globals();

extern "C" const unsigned char* afl_postprocess(const unsigned char* in_buf, unsigned int* len) {
	static bool setup_done = false;
	if (!setup_done) {
		std::string filename = "/dev/shm/afltmp" + std::to_string(getpid());
		setup_generation(filename.c_str(), false);
		debug_print = false;
		setup_done = true;
	}
	file_acc.seed(in_buf, *len);
	try {
		generate_file();
	} catch (...) {
		delete_globals();
		return NULL;
	}
	unsigned file_len = lseek(file_fd, 0, SEEK_END);
	if (file_len > MAX_FILE_SIZE)
		return NULL;
	*len = file_len;
	return (const unsigned char*) file_data;
}

void exit_template(int status) {
	if (debug_print)
		fprintf(stderr, "Template exited with code %d\n", status);
	throw status;
}

void check_exists(bool exists) {
	if (exists)
		return;
	if (debug_print)
		fprintf(stderr, "Struct field does not exist\n");
	throw 0;
}

void check_array_length(unsigned& size) {
	if (size > MAX_FILE_SIZE) {
		unsigned new_size = file_acc.rand_int(16);
		if (debug_print)
			fprintf(stderr, "Array length too large: %d, replaced with %u\n", (signed)size, new_size);
		// throw 0;
		size = new_size;
	}
}

void BigEndian() { is_big_endian = true; }
void LittleEndian() { is_big_endian = false; }
void SetBackColor(int color) { }
uint32 Checksum(int checksum_type, int64 start, int64 size) {
	if (start + size > MAX_FILE_SIZE)
		throw 0;
	switch(checksum_type) {
	case CHECKSUM_CRC32: {
		boost::crc_32_type res;
		res.process_bytes(file_data + start, size);
		return res.checksum();
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
int FEof() { return file_acc.feof(); }
int64 FTell() { return lseek(file_fd, 0, SEEK_CUR); }
void ReadBytes(std::string& s, int64 pos, int n) {abort();}
void ReadBytes(char* s, int64 pos, int n) {abort();}
void ReadBytes(std::vector<uchar> s, int64 pos, int n) {abort();}
int ReadInt(int64 pos) {abort();}
int FSeek(int64 pos) {
	if (lseek(file_fd, pos, SEEK_SET) >= 0)
		return 0;
	return -1;
}
int Strncmp(std::string s1, std::string s2, int n) {abort();}
std::string SubStr(std::string s, int start, int count=-1) {abort();}
void Memcpy(char* dest, std::string src, int n) {abort();}
void Memcpy(std::string dest, std::string src, int n) {abort();}
int IsBigEndian() {abort();}
ushort ReadUShort(int64 pos) {abort();}
int FSkip(int64 offset) {abort();}
int64 FindFirst(WORD data, int matchcase=true, int wholeword=false, int method=0, double tolerance=0.0, int dir=1, int64 start=0) {abort();}
uchar ReadUByte(int64 pos) {abort();}
void BitfieldLeftToRight() {abort();}
int64 FileSize() {abort();}

#endif
