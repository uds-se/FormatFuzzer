#include <string>
#include <vector>
#include <random>
#include <cassert>
#include <functional>
#include <zlib.h>

#define MAX_RAND_SIZE 65536
#define MAX_FILE_SIZE 4096

bool is_big_endian = false;


void swap_bytes(void* b, int size) {
	char* buf = (char*) b;
	char newbuf[8];
	if (is_big_endian) {
		for (int i = 0; i < size; ++i)
			newbuf[i] = buf[size-1-i];
		memcpy(buf, newbuf, size);
	}
}


bool debug_print = false;
bool get_parse_tree = false;
struct stack_cell {
	const char* name;
	std::unordered_map<std::string, int> counts;
	unsigned min = UINT_MAX;
	unsigned max = 0;
	stack_cell(const char* name) : name(name) {}
};
stack_cell root_cell("file");
std::vector<stack_cell> generator_stack = {root_cell};


void assert_cond(bool cond, const char* error_msg) {
	if (!cond) {
		if (debug_print)
			fprintf(stderr, "Error: %s\n", error_msg);
		throw 0;
	}
}


class file_accessor {
	bool allow_evil_values = true;

	bool evil(std::function<bool (unsigned char*)> parse) {
		return rand_int(127 + allow_evil_values, [&parse](unsigned char* file_buf) -> long long { return parse(file_buf) ? 127 : 0; } ) == 127;
	}

	void write_file(const void *buf, size_t count) {
		unsigned pos = file_pos;
		file_pos += count;
		assert_cond(file_pos <= MAX_FILE_SIZE, "file size exceeded MAX_FILE_SIZE");
		if (generate) {
			memcpy(file_buffer + pos, buf, count);
		} else {
			assert_cond(file_pos <= file_size, "reading past the end of file");
			assert_cond(memcmp(file_buffer + pos, buf, count) == 0, "parsed wrong file contents");
		}
		if (file_size < file_pos)
			file_size = file_pos;
		if (!get_parse_tree)
			return;
		if (pos < generator_stack.back().min)
			generator_stack.back().min = pos;
		if (file_pos - 1 > generator_stack.back().max)
			generator_stack.back().max = file_pos - 1;
	}

public:
	unsigned char* rand_buffer;
	unsigned rand_pos = 0;
	unsigned rand_size = 0;
	unsigned char file_buffer[MAX_FILE_SIZE];
	unsigned file_pos = 0;
	unsigned file_size = 0;
	bool generate = true;

	bool set_evil_bit(bool allow) {
		bool old = allow_evil_values;
		allow_evil_values = allow;
		return old;
	}

	long long rand_int(unsigned long long x, std::function<long long (unsigned char*)> parse) {
		unsigned long long max = x-1;
		if (!max)
			return 0;
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

	std::string rand_bytes(int size) {
		std::string result;
		for (int i = 0; i < size; ++i) {
			unsigned char byte = rand_int(256, NULL);
			result += byte;
		}
		return result;
	}

	void seed(unsigned char* b, unsigned rsize, unsigned fsize) {
		rand_buffer = b;
		rand_size = rsize;
		rand_pos = 0;
		file_pos = 0;
		file_size = fsize;
	}

	int feof() {
		return rand_int(8, [this](unsigned char* file_buf) -> long long { return file_pos == file_size ? 7 : 0; } ) == 7;
	}

	template<typename T>
	long long file_integer(int size, std::vector<T>& known) {
		if (evil( [&size, &known](unsigned char* file_buf) -> bool {
				T value;
				memcpy(&value, file_buf, size);
				swap_bytes(&value, size);
				return std::find(known.begin(), known.end(), value) == known.end();
			} )) {
			return file_integer(size);
		}
		assert_cond(0 < size && size <= 8, "sizeof integer invalid");
		T value = known[rand_int(known.size(), [&size, &known](unsigned char* file_buf) -> long long {
			T value;
			memcpy(&value, file_buf, size);
			swap_bytes(&value, size);
			return std::find(known.begin(), known.end(), value) - known.begin();
		} )];
		T newvalue = value;
		swap_bytes(&newvalue, size);
		write_file(&newvalue, size);

		return value;
	}

	long long file_integer(int size, bool small = true) {
		assert_cond(0 < size && size <= 8, "sizeof integer invalid");
		long long value;
		std::function<long long (unsigned char*)> parse = [&size](unsigned char* file_buf) -> long long {
			long long value = 0;
			memcpy(&value, file_buf, size);
			swap_bytes(&value, size);
			return value;
		};
		if (!small)
			value = rand_int(1<<(8*size), parse);
		else {
			int s = rand_int(256, [&size](unsigned char* file_buf) -> long long {
				unsigned long long value = 0;
				memcpy(&value, file_buf, size);
				swap_bytes(&value, size);
				if (value > 0 && value <= 1<<4)
					return 32;
				if (value < 1<<8)
					return 8;
				if (value < 1<<16)
					return 2;
				return 0;
			});
			if (s < 2)
				value = rand_int(1<<(8*size), parse);
			else if (s < 8)
				value = rand_int(1<<16, parse);
			else if (s < 32)
				value = rand_int(1<<8, parse);
			else
				value = 1+rand_int(1<<4, [&size](unsigned char* file_buf) -> long long {
					long long value = 0;
					memcpy(&value, file_buf, size);
					swap_bytes(&value, size);
					--value;
					return value;
				});
		}
		long long newvalue = value;
		swap_bytes(&newvalue, size);
		write_file(&newvalue, size);
		return value;
	}
	
	std::string file_string(std::vector<std::string>& known) {
		if (evil( [&known](unsigned char* file_buf) -> bool {
				std::string value((char*) file_buf, known[0].length());
				return std::find(known.begin(), known.end(), value) == known.end();
			} )) {
			return file_string(known[0].length());
		}
		std::string value = known[rand_int(known.size(), [&known](unsigned char* file_buf) -> long long {
				std::string value((char*) file_buf, known[0].length());
				return std::find(known.begin(), known.end(), value) - known.begin();
			} )];
		ssize_t len = value.length();
		write_file(value.c_str(), len);
		return value;
	}
	
	std::string file_string(int size = 0) {
		if (rand_int(8, [&size](unsigned char* file_buf) -> long long {
			int len = size ? size : INT_MAX;
			for (int i = 0; i < len && file_buf[i]; ++i)
				if (file_buf[i] < 32 || (127 <= file_buf[i] && file_buf[i] < 161))
					return 7;
			return 0;
		} ) != 7) {
			return file_latin1_string(size);
		}
		unsigned char buf[4096];
		ssize_t len = size;
		if (!len)
			len = rand_int(80, [](unsigned char* file_buf) -> long long { return strlen((char*)file_buf); } );
		assert_cond(len < 4096, "string too large");
		for (int i = 0; i < len; ++i) {
			if (size == 0)
				buf[i] = rand_int(255, [&i](unsigned char* file_buf) -> long long { return file_buf[i] - 1; } ) + 1;
			else
				buf[i] = rand_int(256, [&i](unsigned char* file_buf) -> long long { return file_buf[i]; } );
		}
		buf[len] = '\0';
		std::string value((char*)buf, len);
		if (size == 0)
			++len;
		write_file(value.c_str(), len);
		return value;
	}

	std::string file_latin1_string(int size = 0) {
		unsigned char buf[4096];
		ssize_t len = size;
		if (!len)
			len = rand_int(80, [](unsigned char* file_buf) -> long long { return strlen((char*)file_buf); } );
		assert_cond(len < 4096, "string too large");
		for (int i = 0; i < len; ++i) {
			buf[i] = rand_int(190, [&i](unsigned char* file_buf) -> long long { return file_buf[i] >= 161 ? file_buf[i] - 66 : file_buf[i] - 32; } ) + 32;
			if (buf[i] >= 127)
				buf[i] += 34;
		}
		buf[len] = '\0';
		std::string value((char*)buf, len);
		if (size == 0)
			++len;
		write_file(value.c_str(), len);
		return value;
	}
};
