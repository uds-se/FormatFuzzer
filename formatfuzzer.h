#define MAX_RAND_SIZE 131072
#define MAX_FILE_SIZE 65536
#define SIMPLE_MUTATIONS 0

#include <vector>


struct InsertionPoint {
	unsigned pos;
	const char* type;
	const char* name;
#ifdef SIMPLE_MUTATIONS
	unsigned pos_file;
#endif
	InsertionPoint(unsigned pos, const char* type, const char* name, unsigned pos_file) : pos(pos), type(type), name(name)
#ifdef SIMPLE_MUTATIONS
	, pos_file(pos_file)
#endif
	{}
};

struct Chunk {
	int file_index;
	unsigned start;
	unsigned end;
	const char* type;
	const char* name;
#ifdef SIMPLE_MUTATIONS
	unsigned start_file;
	unsigned end_file;
#endif
	Chunk(int file_index, unsigned start, unsigned end, const char* type, const char* name, unsigned start_file, unsigned end_file) : file_index(file_index), start(start), end(end), type(type), name(name)
#ifdef SIMPLE_MUTATIONS
	, start_file(start_file), end_file(end_file)
#endif
	{}
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
extern std::vector<std::string> file_names;

void set_parser();

void set_generator();

bool setup_input(const char* filename);

void generate_file();

unsigned get_file_size();

double get_validity();

void delete_globals();

char* get_bin_name(char* arg);

void save_output(const char* filename);

