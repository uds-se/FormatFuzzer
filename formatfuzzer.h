#define MAX_RAND_SIZE 65536
#define MAX_FILE_SIZE 4096

void set_parser();

void set_generator();

void setup_input(const char* filename);

void generate_file();

void delete_globals();

char* get_bin_name(char* arg);

void save_output(const char* filename);

