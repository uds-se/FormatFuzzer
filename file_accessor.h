#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <random>
#include <cassert>
#include <algorithm>
#include <functional>
#include <zlib.h>
#include "formatfuzzer.h"

extern std::vector<std::vector<int>> integer_ranges;

bool is_big_endian = false;
bool is_bitfield_left_to_right[2] = {false, true};
bool is_padded_bitfield = true;

bool is_following = false;
bool following_is_optional = false;

const char* chunk_name;

bool get_chunk = false;
bool smart_mutation = false;
unsigned chunk_start;
unsigned chunk_end;
unsigned rand_start;
unsigned rand_end;
bool is_optional = false;
bool is_delete = false;

void swap_bytes(void* b, unsigned size) {
	if (is_big_endian) {
		char* start = (char*) b;
		char* end = start + size;
		std::reverse(start, end);
	}
}


bool debug_print = false;
bool print_errors = false;
bool get_parse_tree = false;
struct stack_cell {
	const char* name;
	std::unordered_map<std::string, int> counts;
	unsigned rand_start = 0;
	unsigned rand_start2 = 0;
	unsigned min = UINT_MAX;
	unsigned max = 0;
	stack_cell(const char* name, unsigned rand_start, unsigned rand_start2) : name(name), rand_start(rand_start), rand_start2(rand_start2) {}
	void clear() {
		counts.clear();
		min = UINT_MAX;
		max = 0;
	}
};
stack_cell root_cell("file", 0, 0);
std::vector<stack_cell> generator_stack = {root_cell};


void assert_cond(bool cond, const char* error_msg) {
	if (!cond) {
		if (debug_print || print_errors)
			fprintf(stderr, "Error: %s\n", error_msg);
		throw -1;
	}
}

unsigned char *rand_buffer;

class file_accessor {
	bool allow_evil_values = true;
	unsigned bitfield_size = 0;
	unsigned bitfield_bits = 0;
	bool has_bitmap = false;
	std::vector<bool> bitmap;

	unsigned long long parse_integer(unsigned char* file_buf, unsigned size, unsigned bits = 0) {
		unsigned long long value = 0;
		if (bits) {
			unsigned new_pos = 0;
			unsigned new_bitfield_bits = bitfield_bits;
			if (is_padded_bitfield && (bitfield_bits + bits > 8 * bitfield_size || size != bitfield_size)) {
				new_pos += bitfield_size;
				new_bitfield_bits = 0;
			}

			unsigned initial_bitfield_bits = new_bitfield_bits;
			unsigned new_bits = bits;
			while (new_bits) {
				unsigned byte_pos = new_bitfield_bits / 8;
				unsigned bits_pos = new_bitfield_bits % 8;
				unsigned write_bits = 8 - bits_pos;
				if (new_bits < write_bits)
					write_bits = new_bits;
				unsigned b1;
				unsigned b2;
				if (is_big_endian) {
					b2 = bits - write_bits - (new_bitfield_bits - initial_bitfield_bits);
				} else {
					b2 = new_bitfield_bits - initial_bitfield_bits;
				}
				if (is_bitfield_left_to_right[is_big_endian]) {
					b1 = (8 - bits_pos - write_bits);
				} else {
					b1 = bits_pos;
				}
				unsigned long long c = file_buf[new_pos + byte_pos] >> b1;
				c &= (1 << write_bits) - 1;
				c <<= b2;
				value |= c;

				new_bits -= write_bits;
				new_bitfield_bits += write_bits;
			}

			return value;
		}
		unsigned start_pos = bitfield_bits ? bitfield_size : 0;
		if (is_big_endian) {
			unsigned char* dest = (unsigned char*) &value;
			for (unsigned i = 0; i < size; ++i)
				dest[i] = file_buf[start_pos + size-1-i];
		} else {
			memcpy(&value, file_buf + start_pos, size);
		}
		return value;
	}

	void write_file_bits(unsigned long long value, size_t size, unsigned bits) {
		if (is_padded_bitfield && bitfield_size && (bitfield_bits + bits > 8 * bitfield_size || size != bitfield_size)) {
			is_padding = true;
			file_integer(bitfield_size, 8 * bitfield_size - bitfield_bits, 0);
			is_padding = false;
		}
		unsigned start_pos = file_pos;
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		assert_cond(!has_size || file_pos + size <= file_size, "file size exceeded known size");
		value &= (1LLU << bits) - 1LLU;
		unsigned new_bits = bits;
		while (new_bits) {
			unsigned byte_pos = bitfield_bits / 8;
			unsigned bits_pos = bitfield_bits % 8;
			unsigned write_bits = 8 - bits_pos;
			if (new_bits < write_bits)
				write_bits = new_bits;
			unsigned char c;
			unsigned char mask = (1 << write_bits) - 1;
			if (is_big_endian) {
				c = value >> (bits - write_bits);
				value <<= write_bits;
				value &= (1LLU << bits) - 1LLU;
			} else {
				c = value & ((1 << write_bits) - 1);
				value >>= write_bits;
			}
			if (is_bitfield_left_to_right[is_big_endian]) {
				c <<= (8 - bits_pos - write_bits);
				mask <<= 8 - bits_pos - write_bits;
			} else {
				c <<= bits_pos;
				mask <<= bits_pos;
			}
			unsigned index = file_pos + byte_pos;
			if (!generate)
				assert_cond(index < final_file_size, "reading past the end of file");
			unsigned char old = file_buffer[index];
			file_buffer[index] &= ~mask;
			file_buffer[index] |= c;
			if (!generate)
				assert_cond(file_buffer[index] == old, "parsed wrong file contents");
			new_bits -= write_bits;
			bitfield_bits += write_bits;
		}
		bitfield_size = size;
		while (bitfield_bits >= bitfield_size * 8) {
			file_pos += bitfield_size;
			bitfield_bits -= bitfield_size * 8;
		}
		if (bitfield_bits == 0)
			bitfield_size = 0;

		if (file_size < file_pos)
			file_size = file_pos;
		if (is_padding)
			return;
		if (!generate && parsed_file_size < file_pos)
			parsed_file_size = file_pos;
		if (!get_parse_tree)
			return;
		if (is_following) {
			is_following = false;
		}
		if (start_pos < generator_stack.back().min)
			generator_stack.back().min = start_pos;
		unsigned end = bitfield_size ? file_pos + ((bitfield_bits - 1) / 8) : file_pos - 1;
		if (end > generator_stack.back().max)
			generator_stack.back().max = end;
	}

	void write_file(const void *buf, size_t size) {
		if (bitfield_bits) {
			is_padding = true;
			file_integer(bitfield_size, 8 * bitfield_size - bitfield_bits, 0);
			is_padding = false;
		}
		unsigned start_pos = file_pos;
		file_pos += size;
		assert_cond(file_pos <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		assert_cond(!has_size || file_pos <= file_size, "file size exceeded known size");
		if (generate) {
			memcpy(file_buffer + start_pos, buf, size);
		} else {
			assert_cond(file_pos <= final_file_size, "reading past the end of file");
			assert_cond(memcmp(file_buffer + start_pos, buf, size) == 0, "parsed wrong file contents");
		}

		if (file_size < file_pos)
			file_size = file_pos;

		if (lookahead) {
			has_bitmap = true;
			unsigned original_pos = file_pos - size;
			for (unsigned i = 0; i < size; ++i)
				bitmap[original_pos + i] = true;
		}

		if (is_following && !is_padding) {
			following_is_optional = lookahead;
			is_following = false;
		}
		if (is_padding || lookahead)
			return;
		if (!generate && parsed_file_size < file_pos)
			parsed_file_size = file_pos;
		if (!get_parse_tree)
			return;
		if (start_pos < generator_stack.back().min)
			generator_stack.back().min = start_pos;
		if (file_pos - 1 > generator_stack.back().max)
			generator_stack.back().max = file_pos - 1;
	}

public:
	unsigned char* rand_buffer;
	unsigned rand_pos = 0;
	unsigned rand_size = 0;
	unsigned char *file_buffer;
	unsigned file_pos = 0;
	unsigned file_size = 0;
	unsigned final_file_size = 0;
	unsigned parsed_file_size = 0;
	unsigned rand_prev = 0;
	unsigned rand_last = UINT_MAX;
	bool has_size = false;
	bool generate = true;
	bool lookahead = false;
	bool is_padding = false;

	file_accessor() : bitmap(MAX_FILE_SIZE) {
		file_buffer = new unsigned char[MAX_FILE_SIZE];
		::rand_buffer = new unsigned char[MAX_RAND_SIZE];
	}
	
	~file_accessor() {
		delete[] file_buffer;
		delete[] ::rand_buffer;
	}

	bool set_evil_bit(bool allow) {
		bool old = allow_evil_values;
		allow_evil_values = allow;
		return old;
	}

	std::function<bool (unsigned char*)> evil_parse;

	bool evil(std::function<bool (unsigned char*)>& evil_parse) {
		if (!generate)
			parse = [&evil_parse](unsigned char* file_buf) -> long long { return evil_parse(file_buf) ? 127 : 0; };
		bool is_evil = rand_int(127 + allow_evil_values, parse) == 127;
		assert_cond(!(!generate && !allow_evil_values && rand_buffer[rand_pos-1] == 127), "Evil bit is disabled, but an evil decision is required to parse this file");
		return is_evil;
	}

	std::function<long long (unsigned char*)> parse;

	long long rand_int(unsigned long long x, std::function<long long (unsigned char*)>& parse) {
		unsigned long long max = x-1;
		if (!max)
			return 0;
		if (get_parse_tree) {
			if (lookahead || is_padding) {
				if (rand_last == UINT_MAX)
					rand_last = rand_pos;
			} else {
				rand_last = UINT_MAX;
			}
		}
		if (!(max>>8)) {
			assert_cond(rand_pos + 1 <= rand_size, "random size exceeded rand_size");
			unsigned char* p = (unsigned char*) &rand_buffer[rand_pos];
			if (!generate) {
				*p = parse(&file_buffer[file_pos]);
			}
			++rand_pos;
			return (*p) % x;
		}
		if (!(max>>16)) {
			assert_cond(rand_pos + 2 <= rand_size, "random size exceeded rand_size");
			unsigned short* p = (unsigned short*) &rand_buffer[rand_pos];
			if (!generate) {
				*p = parse(&file_buffer[file_pos]);
			}
			rand_pos += 2;
			return (*p) % x;
		}
		if (!(max>>32)) {
			assert_cond(rand_pos + 4 <= rand_size, "random size exceeded rand_size");
			unsigned* p = (unsigned*) &rand_buffer[rand_pos];
			if (!generate) {
				*p = parse(&file_buffer[file_pos]);
			}
			rand_pos += 4;
			return (*p) % x;
		}
		assert_cond(rand_pos + 8 <= rand_size, "random size exceeded rand_size");
		unsigned long long* p = (unsigned long long*) &rand_buffer[rand_pos];
		if (!generate) {
			*p = parse(&file_buffer[file_pos]);
		}
		rand_pos += 8;
		if (!x)
			return *p;
		return (*p) % x;
	}

	void finish() {
		if (bitfield_bits) {
			is_padding = true;
			file_integer(bitfield_size, 8 * bitfield_size - bitfield_bits, 0);
			is_padding = false;
		}
		if (!generate) {
			assert_cond(file_size == final_file_size, "unparsed bytes left at the end of file");
			assert_cond(parsed_file_size == final_file_size, "unparsed (lookahead) bytes left at the end of file");

			if (get_parse_tree && get_chunk && chunk_end == UINT_MAX && file_pos == chunk_start && rand_last != UINT_MAX) {
				printf("FILE IS APPENDABLE\n");
				rand_start = rand_last;
				chunk_name = "file";
			}
		}
	}

	std::string rand_bytes(int size) {
		std::string result;
		for (int i = 0; i < size; ++i) {
			unsigned char byte = rand_int(256, parse);
			result += byte;
		}
		return result;
	}

	void seed(unsigned char* b, unsigned rsize, unsigned fsize) {
		rand_buffer = b;
		rand_size = rsize;
		rand_pos = 0;
		file_pos = 0;
		file_size = 0;
		final_file_size = fsize;
		parsed_file_size = 0;
		rand_prev = 0;
		rand_last = UINT_MAX;
		following_is_optional = false;

		has_size = false;
		allow_evil_values = true;
		bitfield_size = 0;
		bitfield_bits = 0;
		lookahead = false;
		is_padding = false;
		if (has_bitmap)
			std::fill(bitmap.begin(), bitmap.end(), false);
		has_bitmap = false;
		is_big_endian = false;
		is_bitfield_left_to_right[0] = false;
		is_bitfield_left_to_right[1] = true;
		is_padded_bitfield = true;
		if (get_parse_tree) {
			generator_stack.erase(generator_stack.begin() + 1, generator_stack.end());
			generator_stack[0].clear();
		}
	}

	int feof() {
		if (file_pos < file_size)
			return 0;
		if (has_size)
			return 1;
		if (is_following) {
			following_is_optional = true;
			is_following = false;
		}
		lookahead = true;
		if (!generate)
			parse = [this](unsigned char* file_buf) -> long long { return file_pos == final_file_size ? 7 : 0; };
		int is_feof = rand_int(8, parse) == 7;
		lookahead = false;
		if (is_feof)
			has_size = true;
		return is_feof;
	}

	template<typename T>
	bool is_compatible_integer(unsigned size, T& v) {
		unsigned char* p = (unsigned char*) &v;
		for (unsigned i = 0; i < size; ++i) {
			if (bitmap[file_pos + i]) {
				unsigned index = is_big_endian ? size - 1 - i : i;
				if (p[index] != file_buffer[file_pos + i])
					return false;
			}
		}
		return true;
	}

	template<typename T>
	long long file_integer(unsigned size, unsigned bits, std::vector<T>& known) {
		assert_cond(0 < size && size <= 8, "sizeof integer invalid");
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		std::vector<T> compatible;
		bool match = false;
		if (has_bitmap) {
			for (unsigned i = 0; i < size; ++i) {
				if (bitmap[file_pos + i]) {
					match = true;
					break;
				}
			}
			if (match) {
				assert_cond(bits == 0, "bitfield lookahead not implemented");
				for (T& v : known) {
					if (is_compatible_integer(size, v))
						compatible.push_back(v);
				}
			}
		}
		std::vector<T>& good = match ? compatible : known;

		if (!generate)
			evil_parse = [&size, &bits, &good, this](unsigned char* file_buf) -> bool {
				T value = (T)parse_integer(file_buf, size, bits);
				return std::find(good.begin(), good.end(), value) == good.end();
			};

		if ((match && compatible.empty()) || evil(evil_parse)) {
			return file_integer(size, bits);
		}

		if (!generate)
			parse = [&size, &bits, &good, this](unsigned char* file_buf) -> long long {
				T value = (T)parse_integer(file_buf, size, bits);
				return std::find(good.begin(), good.end(), value) - good.begin();
			};

		T value = good[rand_int(good.size(), parse)];
		T newvalue = value;
		if (bits) {
			value = (T)((unsigned long long)value & ((1LLU << bits) - 1LLU));
			write_file_bits(value, size, bits);
		} else {
			swap_bytes(&newvalue, size);
			write_file(&newvalue, size);
		}

		return value;
	}

	long long file_integer(unsigned size, unsigned bits, int small = 1) {
		assert_cond(0 < size && size <= 8, "sizeof integer invalid");
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");

		unsigned long long range = bits ? bits : 8*size;
		range = range == 64 ? 0 : 1LLU << range;
		long long value;
		if (!generate)
			parse = [&size, &bits, this](unsigned char* file_buf) -> long long {
				return parse_integer(file_buf, size, bits);
			};
		if (small == 0)
			value = rand_int(range, parse);
		else if (small == 1 || (small >= 2 && integer_ranges[small-2][1] == INT_MAX)) {
			int min = 0;
			if (small >= 2)
				min = integer_ranges[small-2][0];
			std::function<long long (unsigned char*)> choice_parse;
			if (!generate)
				choice_parse = [&size, &bits, &min, this](unsigned char* file_buf) -> long long {
					unsigned long long value = parse_integer(file_buf, size, bits) - min;
					if (value > 0 && value <= 1<<4)
						return 0;
					if (value < 1<<8)
						return 256 - 32;
					if (value < 1<<16)
						return 256 - 8;
					return 256 - 2;
				};
			int s = rand_int(256, choice_parse);
			if (s >= 256 - 2)
				value = rand_int(range, parse);
			else if (s >= 256 - 8)
				value = rand_int(1<<16, parse);
			else if (s >= 256 - 32)
				value = rand_int(1<<8, parse);
			else {
				if (!generate)
					parse = [&size, &bits, this](unsigned char* file_buf) -> long long {
						long long value = parse_integer(file_buf, size, bits);
						--value;
						return value;
					};
				value = 1+rand_int(1<<4, parse);
			}
			value += min;
		} else {
			int min = integer_ranges[small-2][0];
			int max = integer_ranges[small-2][1];
			std::function<long long (unsigned char*)> choice_parse;
			if (!generate)
				choice_parse = [&size, &bits, &min, &max, this](unsigned char* file_buf) -> long long {
					long long value = parse_integer(file_buf, size, bits);
					if (value >= min && value <= max)
						return 0;
					return 255;
				};
			int s = rand_int(256, choice_parse);
			if (s == 255)
				value = rand_int(range, parse);
			else {
				if (!generate)
					parse = [&size, &bits, &min, this](unsigned char* file_buf) -> long long {
						long long value = parse_integer(file_buf, size, bits);
						value -= min;
						return value;
					};
				value = min + rand_int(max + 1 - min, parse);
			}
		}
		if (has_bitmap) {
			for (unsigned i = 0; i < size; ++i) {
				if (bitmap[file_pos + i]) {
					assert_cond(bits == 0, "bitfield lookahead not implemented");
					unsigned char* p = (unsigned char*) &value;
					unsigned index = is_big_endian ? size - 1 - i : i;
					p[index] = file_buffer[file_pos + i];
				}
			}
		}
		long long newvalue = value;
		if (bits) {
			value &= (1LLU << bits) - 1LLU;
			write_file_bits(value, size, bits);
		} else {
			swap_bytes(&newvalue, size);
			write_file(&newvalue, size);
		}

		return value;
	}

	bool is_compatible_string(std::string& v) {
		unsigned char* p = (unsigned char*) v.c_str();
		for (unsigned i = 0; i < v.length(); ++i) {
			if (bitmap[file_pos + i] && p[i] != file_buffer[file_pos + i])
				return false;
		}
		return true;
	}
	
	std::string file_string(std::vector<std::string>& known) {
		int size = known[0].length();
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		std::vector<std::string> compatible;
		bool match = false;
		if (has_bitmap) {
			for (int i = 0; i < size; ++i) {
				if (bitmap[file_pos + i]) {
					match = true;
					break;
				}
			}
			if (match) {
				for (std::string& v : known) {
					if (is_compatible_string(v))
						compatible.push_back(v);
				}
			}
		}
		std::vector<std::string>& good = match ? compatible : known;

		if (!generate)
			evil_parse = [&good](unsigned char* file_buf) -> bool {
				std::string value((char*) file_buf, good[0].length());
				return std::find(good.begin(), good.end(), value) == good.end();
			};
		if ((match && compatible.empty()) || evil(evil_parse)) {
			return file_string(size);
		}
		if (!generate)
			parse = [&good](unsigned char* file_buf) -> long long {
				std::string value((char*) file_buf, good[0].length());
				return std::find(good.begin(), good.end(), value) - good.begin();
			};
		std::string value = good[rand_int(good.size(), parse)];
		ssize_t len = value.length();
		write_file(value.c_str(), len);
		return value;
	}
	
	std::string file_string(int size = 0) {
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		if (!generate)
			parse = [&size](unsigned char* file_buf) -> long long {
				int len = size ? size : INT_MAX;
				for (int i = 0; i < len && (size || file_buf[i]); ++i)
					if (file_buf[i] < 32 || file_buf[i] >= 127)
						return 15;
				return 0;
			};
		int choice = rand_int(16, parse);
		if (choice < 14) {
			return file_ascii_string(size);
		} else if (choice == 14) {
			return file_latin1_string(size);
		}
		unsigned char buf[4096];
		ssize_t len = size;
		if (!len) {
			if (!generate)
				parse = [](unsigned char* file_buf) -> long long { return strlen((char*)file_buf); };
			len = rand_int(80, parse);
		}
		assert_cond(len < 4096, "string too large");
		for (int i = 0; i < len; ++i) {
			if (size == 0) {
				if (!generate)
					parse = [&i](unsigned char* file_buf) -> long long { return file_buf[i] - 1; };
				buf[i] = rand_int(255, parse) + 1;
			} else {
				if (!generate)
					parse = [&i](unsigned char* file_buf) -> long long { return file_buf[i]; };
				buf[i] = rand_int(256, parse);
			}
		}
		buf[len] = '\0';
		if (has_bitmap) {
			for (int i = 0; i < len; ++i) {
				if (bitmap[file_pos + i]) {
					buf[i] = file_buffer[file_pos + i];
				}
			}
		}
		std::string value((char*)buf, len);
		if (size == 0)
			++len;
		write_file(value.c_str(), len);
		return value;
	}

	std::string file_ascii_string(int size = 0) {
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		unsigned char buf[4096];
		ssize_t len = size;
		if (!len) {
			if (!generate)
				parse = [](unsigned char* file_buf) -> long long { return strlen((char*)file_buf); };
			len = rand_int(80, parse);
		}
		assert_cond(len < 4096, "string too large");
		for (int i = 0; i < len; ++i) {
			if (!generate)
				parse = [&i](unsigned char* file_buf) -> long long { return file_buf[i] - 32; };
			buf[i] = rand_int(95, parse) + 32;
		}
		buf[len] = '\0';
		if (has_bitmap) {
			for (int i = 0; i < len; ++i) {
				if (bitmap[file_pos + i]) {
					buf[i] = file_buffer[file_pos + i];
				}
			}
		}
		std::string value((char*)buf, len);
		if (size == 0)
			++len;
		write_file(value.c_str(), len);
		return value;
	}

	std::string file_latin1_string(int size = 0) {
		assert_cond(file_pos + size <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		unsigned char buf[4096];
		ssize_t len = size;
		if (!len) {
			if (!generate)
				parse = [](unsigned char* file_buf) -> long long { return strlen((char*)file_buf); };
			len = rand_int(80, parse);
		}
		assert_cond(len < 4096, "string too large");
		for (int i = 0; i < len; ++i) {
			if (!generate)
				parse = [&i](unsigned char* file_buf) -> long long { return file_buf[i] >= 161 ? file_buf[i] - 66 : file_buf[i] - 32; };
			buf[i] = rand_int(190, parse) + 32;
			if (buf[i] >= 127)
				buf[i] += 34;
		}
		buf[len] = '\0';
		if (has_bitmap) {
			for (int i = 0; i < len; ++i) {
				if (bitmap[file_pos + i]) {
					buf[i] = file_buffer[file_pos + i];
				}
			}
		}
		std::string value((char*)buf, len);
		if (size == 0)
			++len;
		write_file(value.c_str(), len);
		return value;
	}
};
