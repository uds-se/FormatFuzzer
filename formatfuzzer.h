#define MAX_RAND_SIZE 131072
#define MAX_FILE_SIZE 65536

#include <vector>


struct InsertionPoint {
	unsigned pos;
	const char* type;
	const char* name;
	InsertionPoint(unsigned pos, const char* type, const char* name) : pos(pos), type(type), name(name) {}
};

struct Chunk {
	int file_index;
	unsigned start;
	unsigned end;
	const char* type;
	const char* name;
	Chunk(int file_index, unsigned start, unsigned end, const char* type, const char* name) : file_index(file_index), start(start), end(end), type(type), name(name) {}
};

struct NonOptional {
	const char* type;
	int start;
	int size;
	NonOptional(const char* type, int start, int size) : type(type), start(start), size(size) {}
};

extern std::unordered_map<std::string, std::string> variable_types;
extern std::vector<std::vector<InsertionPoint>> insertion_points;
extern std::vector<std::vector<Chunk>> deletable_chunks;
extern std::vector<Chunk> optional_chunks;
extern std::vector<int> optional_index;
extern std::unordered_map<std::string, std::vector<Chunk>> non_optional_chunks;
extern std::vector<std::vector<NonOptional>> non_optional_index;
extern std::vector<std::string> rand_names;

void set_parser();

void set_generator();

bool setup_input(const char* filename);

void generate_file();

unsigned get_file_size();

double get_validity();

void delete_globals();

char* get_bin_name(char* arg);

void save_output(const char* filename);

