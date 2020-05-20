#include <random>
#include <cassert>
#include <zlib.h>

bool is_big_endian = false;

class file_accessor {
	int file_fd;
	const unsigned char* buffer;
	unsigned pos = 0;
	unsigned len;

	bool evil() {
		return rand_int(128) == 119;
	}

	void assert_cond(bool cond) {
		if (!cond)
			throw 0;
	}

public:
	long long rand_int(unsigned long long x) {
		unsigned long long max = x-1;
		if (!(max>>8)) {
			assert_cond(pos + 1 <= len);
			unsigned char* p = (unsigned char*) &buffer[pos];
			++pos;
			return (*p) % x;
		}
		if (!(max>>16)) {
			assert_cond(pos + 2 <= len);
			unsigned short* p = (unsigned short*) &buffer[pos];
			pos += 2;
			return (*p) % x;
		}
		if (!(max>>32)) {
			assert_cond(pos + 4 <= len);
			unsigned* p = (unsigned*) &buffer[pos];
			pos += 4;
			return (*p) % x;
		}
		assert_cond(pos + 8 <= len);
		unsigned long long* p = (unsigned long long*) &buffer[pos];
		pos += 8;
		if (!x)
			return *p;
		return (*p) % x;
	}

	std::string rand_bytes(int size) {
		std::string result;
		for (int i = 0; i < size; ++i) {
			unsigned char byte = rand_int(256);
			result += byte;
		}
		return result;
	}

	void set_fd(int file_fd) {
		this->file_fd = file_fd;
	}

	void seed(const unsigned char* b, unsigned l) {
		buffer = b;
		len = l;
		pos = 0;
		lseek(file_fd, 0, SEEK_SET);
		if (ftruncate(file_fd, 0)) {
			perror("Failed to truncate file");
			exit(1);
		}
	}

	int feof() {
		return rand_int(10) == 7;
	}

	template<typename T>
	long long file_integer(int size, std::vector<T>& known) {
		/*if (known.size() == 1 && known[0] == 0 && rand_int(4) == 0) {
			return file_integer(size);
		}*/
		if (evil()) {
			return file_integer(size);
		}
		assert_cond(0 < size && size <= 8);
		T value = known[rand_int(known.size())];
		char* buf = (char*) &value;
		char newbuf[8];
		if (is_big_endian) {
			for (int i = 0; i < size; ++i)
				newbuf[i] = buf[size-1-i];
			buf = newbuf;
		}
		ssize_t res = write(file_fd, buf, size);
		assert_cond(res == size);

		return value;
	}

	long long file_integer(int size, bool small = true) {
		assert_cond(0 < size && size <= 8);
		assert_cond(pos + size <= len);
		long long value;
		if (!small)
			value = rand_int(1<<(8*size));
		else {
			int s = rand_int(256);
			if (s < 2)
				value = rand_int(1<<(8*size));
			else if (s < 8)
				value = rand_int(1<<16);
			else if (s < 32)
				value = rand_int(1<<8);
			else
				value = 1+rand_int(1<<4);
		}
		char* buf = (char*) &value;
		char newbuf[8];
		if (is_big_endian) {
			for (int i = 0; i < size; ++i)
				newbuf[i] = buf[size-1-i];
			buf = newbuf;
		}
		ssize_t res = write(file_fd, buf, size);
		assert_cond(res == size);
		return value;
	}
	
	std::string file_string(std::vector<std::string> known) {
		if (evil()) {
			return file_string(known[0].length());
		}
		std::string value = known[rand_int(known.size())];
		ssize_t len = value.length();
		ssize_t res = write(file_fd, value.c_str(), len);
		assert_cond(res == len);
		return value;
	}
	
	std::string file_string(int size = 0) {
		if (rand_int(8) != 0) {
			return file_latin1_string(size);
		}
		char buf[4096];
		ssize_t len = size;
		if (!len)
			len = rand_int(80);
		assert_cond(len < 4096);
		for (int i = 0; i < len; ++i) {
			buf[i] = rand_int(255) + 1;
		}
		buf[len] = '\0';
		std::string value(buf, len);
		if (size == 0)
			++len;
		ssize_t res = write(file_fd, value.c_str(), len);
		assert_cond(res == len);
		return value;
	}

	std::string file_latin1_string(int size = 0) {
		char buf[4096];
		ssize_t len = size;
		if (!len)
			len = rand_int(80);
		assert_cond(len < 4096);
		for (int i = 0; i < len; ++i) {
			buf[i] = rand_int(190) + 32;
			if (buf[i] >= 127)
				buf[i] += 34;
		}
		buf[len] = '\0';
		std::string value(buf, len);
		if (size == 0)
			++len;
		ssize_t res = write(file_fd, value.c_str(), len);
		assert_cond(res == len);
		return value;
	}
};
