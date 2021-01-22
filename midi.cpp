#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"


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

	char generate(std::vector<char> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(char), 0, new_known_values);
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

	std::string generate(unsigned size, std::vector<std::string> new_known_values = {}) {
		check_array_length(size);
		_startof = FTell();
		value = "";
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		if (new_known_values.size()) {
			value = file_acc.file_string(new_known_values);
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



class uint_class {
	int small;
	std::vector<uint> known_values;
	uint value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint);
	uint operator () () { return value; }
	uint_class(int small, std::vector<uint> known_values = {}) : small(small), known_values(known_values) {}

	uint generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint), 0, known_values);
		}
		return value;
	}

	uint generate(std::vector<uint> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uint), 0, new_known_values);
		return value;
	}
};


enum m_format_enum : short {
	MIDI_SINGLE = (short) 0,
	MIDI_MULTIPLE = (short) 1,
	MIDI_PATTERN = (short) 2,
};
std::vector<short> m_format_enum_values = { MIDI_SINGLE, MIDI_MULTIPLE, MIDI_PATTERN };

m_format_enum m_format_enum_generate() {
	return (m_format_enum) file_acc.file_integer(sizeof(short), 0, m_format_enum_values);
}

m_format_enum m_format_enum_generate(std::vector<short> known_values) {
	return (m_format_enum) file_acc.file_integer(sizeof(short), 0, known_values);
}


class short_class {
	int small;
	std::vector<short> known_values;
	short value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(short);
	short operator () () { return value; }
	short_class(int small, std::vector<short> known_values = {}) : small(small), known_values(known_values) {}

	short generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(short), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(short), 0, known_values);
		}
		return value;
	}

	short generate(std::vector<short> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(short), 0, new_known_values);
		return value;
	}
};



class MidiHeader {
	std::vector<MidiHeader*>& instances;

	std::string m_magic_var;
	uint m_seclen_var;
	short m_format_var;
	short m_ntracks_var;
	short m_tickdiv_var;

public:
	bool m_magic_exists = false;
	bool m_seclen_exists = false;
	bool m_format_exists = false;
	bool m_ntracks_exists = false;
	bool m_tickdiv_exists = false;

	std::string m_magic() {
		assert_cond(m_magic_exists, "struct field m_magic does not exist");
		return m_magic_var;
	}
	uint m_seclen() {
		assert_cond(m_seclen_exists, "struct field m_seclen does not exist");
		return m_seclen_var;
	}
	short m_format() {
		assert_cond(m_format_exists, "struct field m_format does not exist");
		return m_format_var;
	}
	short m_ntracks() {
		assert_cond(m_ntracks_exists, "struct field m_ntracks does not exist");
		return m_ntracks_var;
	}
	short m_tickdiv() {
		assert_cond(m_tickdiv_exists, "struct field m_tickdiv does not exist");
		return m_tickdiv_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiHeader& operator () () { return *instances.back(); }
	MidiHeader* operator [] (int index) { return instances[index]; }
	MidiHeader(std::vector<MidiHeader*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiHeader() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiHeader* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiHeader* generate();
};



class DeltaTime {
	std::vector<DeltaTime*>& instances;

	char t0_var;
	char t1_var;
	char t2_var;
	char t3_var;

public:
	bool t0_exists = false;
	bool t1_exists = false;
	bool t2_exists = false;
	bool t3_exists = false;

	char t0() {
		assert_cond(t0_exists, "struct field t0 does not exist");
		return t0_var;
	}
	char t1() {
		assert_cond(t1_exists, "struct field t1 does not exist");
		return t1_var;
	}
	char t2() {
		assert_cond(t2_exists, "struct field t2 does not exist");
		return t2_var;
	}
	char t3() {
		assert_cond(t3_exists, "struct field t3 does not exist");
		return t3_var;
	}

	/* locals */
	uint total;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	DeltaTime& operator () () { return *instances.back(); }
	DeltaTime* operator [] (int index) { return instances[index]; }
	DeltaTime(std::vector<DeltaTime*>& instances) : instances(instances) { instances.push_back(this); }
	~DeltaTime() {
		if (generated == 2)
			return;
		while (instances.size()) {
			DeltaTime* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	DeltaTime* generate();
};



class MidiMessage_note_off_event_struct {
	std::vector<MidiMessage_note_off_event_struct*>& instances;

	char m_note_var;
	char m_velocity_var;

public:
	bool m_note_exists = false;
	bool m_velocity_exists = false;

	char m_note() {
		assert_cond(m_note_exists, "struct field m_note does not exist");
		return m_note_var;
	}
	char m_velocity() {
		assert_cond(m_velocity_exists, "struct field m_velocity does not exist");
		return m_velocity_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_note_off_event_struct& operator () () { return *instances.back(); }
	MidiMessage_note_off_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_note_off_event_struct(std::vector<MidiMessage_note_off_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_note_off_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_note_off_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_note_off_event_struct* generate();
};



class MidiMessage_note_on_event_struct {
	std::vector<MidiMessage_note_on_event_struct*>& instances;

	char m_note_var;
	char m_velocity_var;

public:
	bool m_note_exists = false;
	bool m_velocity_exists = false;

	char m_note() {
		assert_cond(m_note_exists, "struct field m_note does not exist");
		return m_note_var;
	}
	char m_velocity() {
		assert_cond(m_velocity_exists, "struct field m_velocity does not exist");
		return m_velocity_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_note_on_event_struct& operator () () { return *instances.back(); }
	MidiMessage_note_on_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_note_on_event_struct(std::vector<MidiMessage_note_on_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_note_on_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_note_on_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_note_on_event_struct* generate();
};



class MidiMessage_note_pressure_event_struct {
	std::vector<MidiMessage_note_pressure_event_struct*>& instances;

	char m_note_var;
	char m_pressure_var;

public:
	bool m_note_exists = false;
	bool m_pressure_exists = false;

	char m_note() {
		assert_cond(m_note_exists, "struct field m_note does not exist");
		return m_note_var;
	}
	char m_pressure() {
		assert_cond(m_pressure_exists, "struct field m_pressure does not exist");
		return m_pressure_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_note_pressure_event_struct& operator () () { return *instances.back(); }
	MidiMessage_note_pressure_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_note_pressure_event_struct(std::vector<MidiMessage_note_pressure_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_note_pressure_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_note_pressure_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_note_pressure_event_struct* generate();
};



class MidiMessage_controller_event_struct {
	std::vector<MidiMessage_controller_event_struct*>& instances;

	char m_controller_var;
	char m_value_var;

public:
	bool m_controller_exists = false;
	bool m_value_exists = false;

	char m_controller() {
		assert_cond(m_controller_exists, "struct field m_controller does not exist");
		return m_controller_var;
	}
	char m_value() {
		assert_cond(m_value_exists, "struct field m_value does not exist");
		return m_value_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_controller_event_struct& operator () () { return *instances.back(); }
	MidiMessage_controller_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_controller_event_struct(std::vector<MidiMessage_controller_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_controller_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_controller_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_controller_event_struct* generate();
};



class MidiMessage_program_event_struct {
	std::vector<MidiMessage_program_event_struct*>& instances;

	char m_program_var;

public:
	bool m_program_exists = false;

	char m_program() {
		assert_cond(m_program_exists, "struct field m_program does not exist");
		return m_program_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_program_event_struct& operator () () { return *instances.back(); }
	MidiMessage_program_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_program_event_struct(std::vector<MidiMessage_program_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_program_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_program_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_program_event_struct* generate();
};



class MidiMessage_channel_pressure_event_struct {
	std::vector<MidiMessage_channel_pressure_event_struct*>& instances;

	char m_pressure_var;

public:
	bool m_pressure_exists = false;

	char m_pressure() {
		assert_cond(m_pressure_exists, "struct field m_pressure does not exist");
		return m_pressure_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_channel_pressure_event_struct& operator () () { return *instances.back(); }
	MidiMessage_channel_pressure_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_channel_pressure_event_struct(std::vector<MidiMessage_channel_pressure_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_channel_pressure_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_channel_pressure_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_channel_pressure_event_struct* generate();
};



class MidiMessage_pitch_bend_event_struct {
	std::vector<MidiMessage_pitch_bend_event_struct*>& instances;

	char m_lsb_var;
	char m_msb_var;

public:
	bool m_lsb_exists = false;
	bool m_msb_exists = false;

	char m_lsb() {
		assert_cond(m_lsb_exists, "struct field m_lsb does not exist");
		return m_lsb_var;
	}
	char m_msb() {
		assert_cond(m_msb_exists, "struct field m_msb does not exist");
		return m_msb_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_pitch_bend_event_struct& operator () () { return *instances.back(); }
	MidiMessage_pitch_bend_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_pitch_bend_event_struct(std::vector<MidiMessage_pitch_bend_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_pitch_bend_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_pitch_bend_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_pitch_bend_event_struct* generate();
};


enum m_type_enum : char {
	META_SEQUENCE_NUM = (char) 0,
	META_TEXT = (char) 1,
	META_COPYRIGHT = (char) 2,
	META_SEQUENCE_NAME = (char) 3,
	META_INSTRUMENT_NAME = (char) 4,
	META_LYRIC = (char) 5,
	META_MARKER = (char) 6,
	META_CUE_POINT = (char) 7,
	META_PROGRAM_NAME = (char) 8,
	META_DEVICE_NAME = (char) 9,
	META_MIDI_CHANNEL_PREFIX = (char) 0x20,
	META_MIDI_PORT = (char) 0x21,
	META_END_OF_TRACK = (char) 0x2f,
	META_TEMPO = (char) 0x51,
	META_SMPTE_OFFSET = (char) 0x54,
	META_TIME_SIGNATURE = (char) 0x58,
	META_KEY_SIGNATURE = (char) 0x59,
	META_SEQUENCER_EVENT = (char) 0x7f,
};
std::vector<char> m_type_enum_values = { META_SEQUENCE_NUM, META_TEXT, META_COPYRIGHT, META_SEQUENCE_NAME, META_INSTRUMENT_NAME, META_LYRIC, META_MARKER, META_CUE_POINT, META_PROGRAM_NAME, META_DEVICE_NAME, META_MIDI_CHANNEL_PREFIX, META_MIDI_PORT, META_END_OF_TRACK, META_TEMPO, META_SMPTE_OFFSET, META_TIME_SIGNATURE, META_KEY_SIGNATURE, META_SEQUENCER_EVENT };

m_type_enum m_type_enum_generate() {
	return (m_type_enum) file_acc.file_integer(sizeof(char), 0, m_type_enum_values);
}

m_type_enum m_type_enum_generate(std::vector<char> known_values) {
	return (m_type_enum) file_acc.file_integer(sizeof(char), 0, known_values);
}


class uint_bitfield {
	int small;
	std::vector<uint> known_values;
	uint value;
public:
	uint operator () () { return value; }
	uint_bitfield(int small, std::vector<uint> known_values = {}) : small(small), known_values(known_values) {}

	uint generate(unsigned bits) {
		if (!bits)
			return 0;
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint), bits, small);
		} else {
			value = file_acc.file_integer(sizeof(uint), bits, known_values);
		}
		return value;
	}

	uint generate(unsigned bits, std::vector<uint> new_known_values) {
		if (!bits)
			return 0;
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uint), bits, new_known_values);
		return value;
	}
};



class MidiMessage_meta_event_struct {
	std::vector<MidiMessage_meta_event_struct*>& instances;

	char m_type_var;
	DeltaTime* m_length_var;
	short m_seqNum_var;
	std::string m_text_var;
	std::string m_copyright_var;
	std::string m_name_var;
	std::string m_lyric_var;
	std::string m_marker_var;
	std::string m_cuePoint_var;
	std::string m_programName_var;
	std::string m_deviceName_var;
	char m_channelPrefix_var;
	char m_port_var;
	uint m_usecPerQuarterNote_var : 24;
	char m_hours_var;
	char m_mins_var;
	char m_secs_var;
	char m_fps_var;
	char m_fracFrames_var;
	char m_numerator_var;
	char m_denominator_var;
	char m_clocksPerClick_var;
	char m_32ndPer4th_var;
	char m_flatsSharps_var;
	char m_majorMinor_var;
	std::string m_data_var;

public:
	bool m_type_exists = false;
	bool m_length_exists = false;
	bool m_seqNum_exists = false;
	bool m_text_exists = false;
	bool m_copyright_exists = false;
	bool m_name_exists = false;
	bool m_lyric_exists = false;
	bool m_marker_exists = false;
	bool m_cuePoint_exists = false;
	bool m_programName_exists = false;
	bool m_deviceName_exists = false;
	bool m_channelPrefix_exists = false;
	bool m_port_exists = false;
	bool m_usecPerQuarterNote_exists = false;
	bool m_hours_exists = false;
	bool m_mins_exists = false;
	bool m_secs_exists = false;
	bool m_fps_exists = false;
	bool m_fracFrames_exists = false;
	bool m_numerator_exists = false;
	bool m_denominator_exists = false;
	bool m_clocksPerClick_exists = false;
	bool m_32ndPer4th_exists = false;
	bool m_flatsSharps_exists = false;
	bool m_majorMinor_exists = false;
	bool m_data_exists = false;

	char m_type() {
		assert_cond(m_type_exists, "struct field m_type does not exist");
		return m_type_var;
	}
	DeltaTime& m_length() {
		assert_cond(m_length_exists, "struct field m_length does not exist");
		return *m_length_var;
	}
	short m_seqNum() {
		assert_cond(m_seqNum_exists, "struct field m_seqNum does not exist");
		return m_seqNum_var;
	}
	std::string m_text() {
		assert_cond(m_text_exists, "struct field m_text does not exist");
		return m_text_var;
	}
	std::string m_copyright() {
		assert_cond(m_copyright_exists, "struct field m_copyright does not exist");
		return m_copyright_var;
	}
	std::string m_name() {
		assert_cond(m_name_exists, "struct field m_name does not exist");
		return m_name_var;
	}
	std::string m_lyric() {
		assert_cond(m_lyric_exists, "struct field m_lyric does not exist");
		return m_lyric_var;
	}
	std::string m_marker() {
		assert_cond(m_marker_exists, "struct field m_marker does not exist");
		return m_marker_var;
	}
	std::string m_cuePoint() {
		assert_cond(m_cuePoint_exists, "struct field m_cuePoint does not exist");
		return m_cuePoint_var;
	}
	std::string m_programName() {
		assert_cond(m_programName_exists, "struct field m_programName does not exist");
		return m_programName_var;
	}
	std::string m_deviceName() {
		assert_cond(m_deviceName_exists, "struct field m_deviceName does not exist");
		return m_deviceName_var;
	}
	char m_channelPrefix() {
		assert_cond(m_channelPrefix_exists, "struct field m_channelPrefix does not exist");
		return m_channelPrefix_var;
	}
	char m_port() {
		assert_cond(m_port_exists, "struct field m_port does not exist");
		return m_port_var;
	}
	uint m_usecPerQuarterNote() {
		assert_cond(m_usecPerQuarterNote_exists, "struct field m_usecPerQuarterNote does not exist");
		return m_usecPerQuarterNote_var;
	}
	char m_hours() {
		assert_cond(m_hours_exists, "struct field m_hours does not exist");
		return m_hours_var;
	}
	char m_mins() {
		assert_cond(m_mins_exists, "struct field m_mins does not exist");
		return m_mins_var;
	}
	char m_secs() {
		assert_cond(m_secs_exists, "struct field m_secs does not exist");
		return m_secs_var;
	}
	char m_fps() {
		assert_cond(m_fps_exists, "struct field m_fps does not exist");
		return m_fps_var;
	}
	char m_fracFrames() {
		assert_cond(m_fracFrames_exists, "struct field m_fracFrames does not exist");
		return m_fracFrames_var;
	}
	char m_numerator() {
		assert_cond(m_numerator_exists, "struct field m_numerator does not exist");
		return m_numerator_var;
	}
	char m_denominator() {
		assert_cond(m_denominator_exists, "struct field m_denominator does not exist");
		return m_denominator_var;
	}
	char m_clocksPerClick() {
		assert_cond(m_clocksPerClick_exists, "struct field m_clocksPerClick does not exist");
		return m_clocksPerClick_var;
	}
	char m_32ndPer4th() {
		assert_cond(m_32ndPer4th_exists, "struct field m_32ndPer4th does not exist");
		return m_32ndPer4th_var;
	}
	char m_flatsSharps() {
		assert_cond(m_flatsSharps_exists, "struct field m_flatsSharps does not exist");
		return m_flatsSharps_var;
	}
	char m_majorMinor() {
		assert_cond(m_majorMinor_exists, "struct field m_majorMinor does not exist");
		return m_majorMinor_var;
	}
	std::string m_data() {
		assert_cond(m_data_exists, "struct field m_data does not exist");
		return m_data_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_meta_event_struct& operator () () { return *instances.back(); }
	MidiMessage_meta_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_meta_event_struct(std::vector<MidiMessage_meta_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_meta_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_meta_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_meta_event_struct* generate();
};



class MidiMessage_sysex_event_struct {
	std::vector<MidiMessage_sysex_event_struct*>& instances;

	DeltaTime* m_length_var;
	std::string m_message_var;

public:
	bool m_length_exists = false;
	bool m_message_exists = false;

	DeltaTime& m_length() {
		assert_cond(m_length_exists, "struct field m_length does not exist");
		return *m_length_var;
	}
	std::string m_message() {
		assert_cond(m_message_exists, "struct field m_message does not exist");
		return m_message_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage_sysex_event_struct& operator () () { return *instances.back(); }
	MidiMessage_sysex_event_struct* operator [] (int index) { return instances[index]; }
	MidiMessage_sysex_event_struct(std::vector<MidiMessage_sysex_event_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage_sysex_event_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage_sysex_event_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage_sysex_event_struct* generate();
};



class MidiMessage {
	std::vector<MidiMessage*>& instances;

	DeltaTime* m_dtime_var;
	char m_status_var;
	MidiMessage_note_off_event_struct* note_off_event_var;
	MidiMessage_note_on_event_struct* note_on_event_var;
	MidiMessage_note_pressure_event_struct* note_pressure_event_var;
	MidiMessage_controller_event_struct* controller_event_var;
	MidiMessage_program_event_struct* program_event_var;
	MidiMessage_channel_pressure_event_struct* channel_pressure_event_var;
	MidiMessage_pitch_bend_event_struct* pitch_bend_event_var;
	MidiMessage_meta_event_struct* meta_event_var;
	MidiMessage_sysex_event_struct* sysex_event_var;

public:
	bool m_dtime_exists = false;
	bool m_status_exists = false;
	bool note_off_event_exists = false;
	bool note_on_event_exists = false;
	bool note_pressure_event_exists = false;
	bool controller_event_exists = false;
	bool program_event_exists = false;
	bool channel_pressure_event_exists = false;
	bool pitch_bend_event_exists = false;
	bool meta_event_exists = false;
	bool sysex_event_exists = false;

	DeltaTime& m_dtime() {
		assert_cond(m_dtime_exists, "struct field m_dtime does not exist");
		return *m_dtime_var;
	}
	char m_status() {
		assert_cond(m_status_exists, "struct field m_status does not exist");
		return m_status_var;
	}
	MidiMessage_note_off_event_struct& note_off_event() {
		assert_cond(note_off_event_exists, "struct field note_off_event does not exist");
		return *note_off_event_var;
	}
	MidiMessage_note_on_event_struct& note_on_event() {
		assert_cond(note_on_event_exists, "struct field note_on_event does not exist");
		return *note_on_event_var;
	}
	MidiMessage_note_pressure_event_struct& note_pressure_event() {
		assert_cond(note_pressure_event_exists, "struct field note_pressure_event does not exist");
		return *note_pressure_event_var;
	}
	MidiMessage_controller_event_struct& controller_event() {
		assert_cond(controller_event_exists, "struct field controller_event does not exist");
		return *controller_event_var;
	}
	MidiMessage_program_event_struct& program_event() {
		assert_cond(program_event_exists, "struct field program_event does not exist");
		return *program_event_var;
	}
	MidiMessage_channel_pressure_event_struct& channel_pressure_event() {
		assert_cond(channel_pressure_event_exists, "struct field channel_pressure_event does not exist");
		return *channel_pressure_event_var;
	}
	MidiMessage_pitch_bend_event_struct& pitch_bend_event() {
		assert_cond(pitch_bend_event_exists, "struct field pitch_bend_event does not exist");
		return *pitch_bend_event_var;
	}
	MidiMessage_meta_event_struct& meta_event() {
		assert_cond(meta_event_exists, "struct field meta_event does not exist");
		return *meta_event_var;
	}
	MidiMessage_sysex_event_struct& sysex_event() {
		assert_cond(sysex_event_exists, "struct field sysex_event does not exist");
		return *sysex_event_var;
	}

	/* locals */
	char m_channel;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiMessage& operator () () { return *instances.back(); }
	MidiMessage* operator [] (int index) { return instances[index]; }
	MidiMessage(std::vector<MidiMessage*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiMessage() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiMessage* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiMessage* generate(uint& message_index);
};



class MidiTrack {
	std::vector<MidiTrack*>& instances;

	std::string m_magic_var;
	uint m_seclen_var;
	MidiMessage* message_var;

public:
	bool m_magic_exists = false;
	bool m_seclen_exists = false;
	bool message_exists = false;

	std::string m_magic() {
		assert_cond(m_magic_exists, "struct field m_magic does not exist");
		return m_magic_var;
	}
	uint m_seclen() {
		assert_cond(m_seclen_exists, "struct field m_seclen does not exist");
		return m_seclen_var;
	}
	MidiMessage& message() {
		assert_cond(message_exists, "struct field message does not exist");
		return *message_var;
	}

	/* locals */
	uint m_seclen_pos;
	uint remaining;
	uint message_index;
	uint sec_start;
	uint message_len;
	uint sec_end;
	int evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MidiTrack& operator () () { return *instances.back(); }
	MidiTrack* operator [] (int index) { return instances[index]; }
	MidiTrack(std::vector<MidiTrack*>& instances) : instances(instances) { instances.push_back(this); }
	~MidiTrack() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MidiTrack* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MidiTrack* generate();
};



class MidiTrack_array_class {
	MidiTrack& element;
	std::vector<MidiTrack*> value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::vector<MidiTrack*> operator () () { return value; }
	MidiTrack operator [] (int index) { return *value[index]; }
	MidiTrack_array_class(MidiTrack& element) : element(element) {}

	std::vector<MidiTrack*> generate(unsigned size) {
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



class file_struct {
	std::vector<file_struct*>& instances;

	MidiHeader* header_var;
	std::vector<MidiTrack*> tracks_var;

public:
	bool header_exists = false;
	bool tracks_exists = false;

	MidiHeader& header() {
		assert_cond(header_exists, "struct field header does not exist");
		return *header_var;
	}
	std::vector<MidiTrack*> tracks() {
		assert_cond(tracks_exists, "struct field tracks does not exist");
		return tracks_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	file_struct& operator () () { return *instances.back(); }
	file_struct* operator [] (int index) { return instances[index]; }
	file_struct(std::vector<file_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~file_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			file_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	file_struct* generate();
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


std::vector<MidiHeader*> MidiHeader_header_instances;
std::vector<DeltaTime*> DeltaTime_m_dtime_instances;
std::vector<MidiMessage_note_off_event_struct*> MidiMessage_note_off_event_struct_note_off_event_instances;
std::vector<MidiMessage_note_on_event_struct*> MidiMessage_note_on_event_struct_note_on_event_instances;
std::vector<MidiMessage_note_pressure_event_struct*> MidiMessage_note_pressure_event_struct_note_pressure_event_instances;
std::vector<MidiMessage_controller_event_struct*> MidiMessage_controller_event_struct_controller_event_instances;
std::vector<MidiMessage_program_event_struct*> MidiMessage_program_event_struct_program_event_instances;
std::vector<MidiMessage_channel_pressure_event_struct*> MidiMessage_channel_pressure_event_struct_channel_pressure_event_instances;
std::vector<MidiMessage_pitch_bend_event_struct*> MidiMessage_pitch_bend_event_struct_pitch_bend_event_instances;
std::vector<DeltaTime*> DeltaTime_m_length_instances;
std::vector<MidiMessage_meta_event_struct*> MidiMessage_meta_event_struct_meta_event_instances;
std::vector<MidiMessage_sysex_event_struct*> MidiMessage_sysex_event_struct_sysex_event_instances;
std::vector<MidiMessage*> MidiMessage_message_instances;
std::vector<MidiTrack*> MidiTrack_tracks_element_instances;
std::vector<file_struct*> file_struct_file_instances;


std::unordered_map<std::string, std::string> variable_types = { { "m_magic", "char_array_class" }, { "m_seclen", "uint_class" }, { "m_format", "m_format_enum" }, { "m_ntracks", "short_class" }, { "m_tickdiv", "short_class" }, { "header", "MidiHeader" }, { "t0", "char_class" }, { "t1", "char_class" }, { "t2", "char_class" }, { "t3", "char_class" }, { "m_dtime", "DeltaTime" }, { "m_status", "char_class" }, { "m_note", "char_class" }, { "m_velocity", "char_class" }, { "note_off_event", "MidiMessage_note_off_event_struct" }, { "note_on_event", "MidiMessage_note_on_event_struct" }, { "m_pressure", "char_class" }, { "note_pressure_event", "MidiMessage_note_pressure_event_struct" }, { "m_controller", "char_class" }, { "m_value", "char_class" }, { "controller_event", "MidiMessage_controller_event_struct" }, { "m_program", "char_class" }, { "program_event", "MidiMessage_program_event_struct" }, { "channel_pressure_event", "MidiMessage_channel_pressure_event_struct" }, { "m_lsb", "char_class" }, { "m_msb", "char_class" }, { "pitch_bend_event", "MidiMessage_pitch_bend_event_struct" }, { "m_type", "m_type_enum" }, { "m_length", "DeltaTime" }, { "m_seqNum", "short_class" }, { "m_text", "char_array_class" }, { "m_copyright", "char_array_class" }, { "m_name", "char_array_class" }, { "m_lyric", "char_array_class" }, { "m_marker", "char_array_class" }, { "m_cuePoint", "char_array_class" }, { "m_programName", "char_array_class" }, { "m_deviceName", "char_array_class" }, { "m_channelPrefix", "char_class" }, { "m_port", "char_class" }, { "m_usecPerQuarterNote", "uint_bitfield24" }, { "m_hours", "char_class" }, { "m_mins", "char_class" }, { "m_secs", "char_class" }, { "m_fps", "char_class" }, { "m_fracFrames", "char_class" }, { "m_numerator", "char_class" }, { "m_denominator", "char_class" }, { "m_clocksPerClick", "char_class" }, { "m_32ndPer4th", "char_class" }, { "m_flatsSharps", "char_class" }, { "m_majorMinor", "char_class" }, { "m_data", "char_array_class" }, { "meta_event", "MidiMessage_meta_event_struct" }, { "m_message", "char_array_class" }, { "sysex_event", "MidiMessage_sysex_event_struct" }, { "message", "MidiMessage" }, { "tracks", "MidiTrack_array_class" }, { "file", "file_struct" } };

std::vector<std::vector<int>> integer_ranges = { { 1, 16 } };

class globals_class {
public:
	/*local*/ uint track_index;
	/*local*/ uint message_index;
	/*local*/ char lastStatus;
	char_class m_magic_element;
	char_array_class m_magic;
	uint_class m_seclen;
	short_class m_ntracks;
	short_class m_tickdiv;
	MidiHeader header;
	char_class t0;
	char_class t1;
	char_class t2;
	char_class t3;
	DeltaTime m_dtime;
	char_class m_status;
	char_class m_note;
	char_class m_velocity;
	MidiMessage_note_off_event_struct note_off_event;
	MidiMessage_note_on_event_struct note_on_event;
	char_class m_pressure;
	MidiMessage_note_pressure_event_struct note_pressure_event;
	char_class m_controller;
	char_class m_value;
	MidiMessage_controller_event_struct controller_event;
	char_class m_program;
	MidiMessage_program_event_struct program_event;
	MidiMessage_channel_pressure_event_struct channel_pressure_event;
	char_class m_lsb;
	char_class m_msb;
	MidiMessage_pitch_bend_event_struct pitch_bend_event;
	DeltaTime m_length;
	short_class m_seqNum;
	char_class m_text_element;
	char_array_class m_text;
	char_class m_copyright_element;
	char_array_class m_copyright;
	char_class m_name_element;
	char_array_class m_name;
	char_class m_lyric_element;
	char_array_class m_lyric;
	char_class m_marker_element;
	char_array_class m_marker;
	char_class m_cuePoint_element;
	char_array_class m_cuePoint;
	char_class m_programName_element;
	char_array_class m_programName;
	char_class m_deviceName_element;
	char_array_class m_deviceName;
	char_class m_channelPrefix;
	char_class m_port;
	uint_bitfield m_usecPerQuarterNote;
	char_class m_hours;
	char_class m_mins;
	char_class m_secs;
	char_class m_fps;
	char_class m_fracFrames;
	char_class m_numerator;
	char_class m_denominator;
	char_class m_clocksPerClick;
	char_class m_32ndPer4th;
	char_class m_flatsSharps;
	char_class m_majorMinor;
	char_class m_data_element;
	char_array_class m_data;
	MidiMessage_meta_event_struct meta_event;
	char_class m_message_element;
	char_array_class m_message;
	MidiMessage_sysex_event_struct sysex_event;
	MidiMessage message;
	MidiTrack tracks_element;
	MidiTrack_array_class tracks;
	file_struct file;


	globals_class() :
		m_magic_element(false),
		m_magic(m_magic_element),
		m_seclen(1),
		m_ntracks(2),
		m_tickdiv(1),
		header(MidiHeader_header_instances),
		t0(1),
		t1(1),
		t2(1),
		t3(1),
		m_dtime(DeltaTime_m_dtime_instances),
		m_status(1),
		m_note(1),
		m_velocity(1),
		note_off_event(MidiMessage_note_off_event_struct_note_off_event_instances),
		note_on_event(MidiMessage_note_on_event_struct_note_on_event_instances),
		m_pressure(1),
		note_pressure_event(MidiMessage_note_pressure_event_struct_note_pressure_event_instances),
		m_controller(1),
		m_value(1),
		controller_event(MidiMessage_controller_event_struct_controller_event_instances),
		m_program(1),
		program_event(MidiMessage_program_event_struct_program_event_instances),
		channel_pressure_event(MidiMessage_channel_pressure_event_struct_channel_pressure_event_instances),
		m_lsb(1),
		m_msb(1),
		pitch_bend_event(MidiMessage_pitch_bend_event_struct_pitch_bend_event_instances),
		m_length(DeltaTime_m_length_instances),
		m_seqNum(1),
		m_text_element(false),
		m_text(m_text_element),
		m_copyright_element(false),
		m_copyright(m_copyright_element),
		m_name_element(false),
		m_name(m_name_element),
		m_lyric_element(false),
		m_lyric(m_lyric_element),
		m_marker_element(false),
		m_marker(m_marker_element),
		m_cuePoint_element(false),
		m_cuePoint(m_cuePoint_element),
		m_programName_element(false),
		m_programName(m_programName_element),
		m_deviceName_element(false),
		m_deviceName(m_deviceName_element),
		m_channelPrefix(1),
		m_port(1),
		m_usecPerQuarterNote(1),
		m_hours(1),
		m_mins(1),
		m_secs(1),
		m_fps(1),
		m_fracFrames(1),
		m_numerator(1),
		m_denominator(1),
		m_clocksPerClick(1),
		m_32ndPer4th(1),
		m_flatsSharps(1),
		m_majorMinor(1),
		m_data_element(false),
		m_data(m_data_element),
		meta_event(MidiMessage_meta_event_struct_meta_event_instances),
		m_message_element(false),
		m_message(m_message_element),
		sysex_event(MidiMessage_sysex_event_struct_sysex_event_instances),
		message(MidiMessage_message_instances),
		tracks_element(MidiTrack_tracks_element_instances),
		tracks(tracks_element),
		file(file_struct_file_instances)
	{}
};

globals_class* g;


MidiHeader* MidiHeader::generate() {
	if (generated == 1) {
		MidiHeader* new_instance = new MidiHeader(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_magic, ::g->m_magic.generate(4, { "MThd" }));
	GENERATE_VAR(m_seclen, ::g->m_seclen.generate());
	GENERATE_VAR(m_format, m_format_enum_generate());
	GENERATE_VAR(m_ntracks, ::g->m_ntracks.generate());
	GENERATE_VAR(m_tickdiv, ::g->m_tickdiv.generate());
	Printf("---MIDI header---\n\tMagic: %s\n\tSection length: %d\n\tTracks: %d\n\tTick div: %d\n", std::string(m_magic()).c_str(), m_seclen(), m_ntracks(), m_tickdiv());

	_sizeof = FTell() - _startof;
	return this;
}


DeltaTime* DeltaTime::generate() {
do {
	if (generated == 1) {
		DeltaTime* new_instance = new DeltaTime(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	total = 0;
	GENERATE_VAR(t0, ::g->t0.generate({ 0 }));
	total += (t0() & 0x7f);
	if (!(t0() & 0x80)) {
	break;
	};
	total <<= 7;
	GENERATE_VAR(t1, ::g->t1.generate());
	total += (t1() & 0x7f);
	if (!(t1() & 0x80)) {
	break;
	};
	total <<= 7;
	GENERATE_VAR(t2, ::g->t2.generate());
	total += (t2() & 0x7f);
	if (!(t2() & 0x80)) {
	break;
	};
	total <<= 7;
	GENERATE_VAR(t3, ::g->t3.generate());
	total += (t3() & 0x7f);
	if (!(t3() & 0x80)) {
	break;
	};
} while (false);

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_note_off_event_struct* MidiMessage_note_off_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_note_off_event_struct* new_instance = new MidiMessage_note_off_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_note, ::g->m_note.generate());
	GENERATE_VAR(m_velocity, ::g->m_velocity.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_note_on_event_struct* MidiMessage_note_on_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_note_on_event_struct* new_instance = new MidiMessage_note_on_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_note, ::g->m_note.generate());
	GENERATE_VAR(m_velocity, ::g->m_velocity.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_note_pressure_event_struct* MidiMessage_note_pressure_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_note_pressure_event_struct* new_instance = new MidiMessage_note_pressure_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_note, ::g->m_note.generate());
	GENERATE_VAR(m_pressure, ::g->m_pressure.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_controller_event_struct* MidiMessage_controller_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_controller_event_struct* new_instance = new MidiMessage_controller_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_controller, ::g->m_controller.generate());
	GENERATE_VAR(m_value, ::g->m_value.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_program_event_struct* MidiMessage_program_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_program_event_struct* new_instance = new MidiMessage_program_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_program, ::g->m_program.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_channel_pressure_event_struct* MidiMessage_channel_pressure_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_channel_pressure_event_struct* new_instance = new MidiMessage_channel_pressure_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_pressure, ::g->m_pressure.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_pitch_bend_event_struct* MidiMessage_pitch_bend_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_pitch_bend_event_struct* new_instance = new MidiMessage_pitch_bend_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_lsb, ::g->m_lsb.generate());
	GENERATE_VAR(m_msb, ::g->m_msb.generate());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_meta_event_struct* MidiMessage_meta_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_meta_event_struct* new_instance = new MidiMessage_meta_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_type, m_type_enum_generate());
	GENERATE_VAR(m_length, ::g->m_length.generate());
	if ((m_type() == META_SEQUENCE_NUM)) {
		GENERATE_VAR(m_seqNum, ::g->m_seqNum.generate());
	} else {
	if ((m_type() == META_TEXT)) {
		GENERATE_VAR(m_text, ::g->m_text.generate(m_length().total));
	} else {
	if ((m_type() == META_COPYRIGHT)) {
		GENERATE_VAR(m_copyright, ::g->m_copyright.generate(m_length().total));
	} else {
	if ((m_type() == META_SEQUENCE_NAME)) {
		GENERATE_VAR(m_name, ::g->m_name.generate(m_length().total));
	} else {
	if ((m_type() == META_INSTRUMENT_NAME)) {
		GENERATE_VAR(m_name, ::g->m_name.generate(m_length().total));
	} else {
	if ((m_type() == META_LYRIC)) {
		GENERATE_VAR(m_lyric, ::g->m_lyric.generate(m_length().total));
	} else {
	if ((m_type() == META_MARKER)) {
		GENERATE_VAR(m_marker, ::g->m_marker.generate(m_length().total));
	} else {
	if ((m_type() == META_CUE_POINT)) {
		GENERATE_VAR(m_cuePoint, ::g->m_cuePoint.generate(m_length().total));
	} else {
	if ((m_type() == META_PROGRAM_NAME)) {
		GENERATE_VAR(m_programName, ::g->m_programName.generate(m_length().total));
	} else {
	if ((m_type() == META_DEVICE_NAME)) {
		GENERATE_VAR(m_deviceName, ::g->m_deviceName.generate(m_length().total));
	} else {
	if ((m_type() == META_MIDI_CHANNEL_PREFIX)) {
		GENERATE_VAR(m_channelPrefix, ::g->m_channelPrefix.generate());
	} else {
	if ((m_type() == META_MIDI_PORT)) {
		GENERATE_VAR(m_port, ::g->m_port.generate());
	} else {
	if ((m_type() == META_END_OF_TRACK)) {
	;
	} else {
	if ((m_type() == META_TEMPO)) {
		GENERATE_VAR(m_usecPerQuarterNote, ::g->m_usecPerQuarterNote.generate(24));
		FSeek((FTell() - 1));
	} else {
	if ((m_type() == META_SMPTE_OFFSET)) {
		GENERATE_VAR(m_hours, ::g->m_hours.generate());
		GENERATE_VAR(m_mins, ::g->m_mins.generate());
		GENERATE_VAR(m_secs, ::g->m_secs.generate());
		GENERATE_VAR(m_fps, ::g->m_fps.generate());
		GENERATE_VAR(m_fracFrames, ::g->m_fracFrames.generate());
	} else {
	if ((m_type() == META_TIME_SIGNATURE)) {
		GENERATE_VAR(m_numerator, ::g->m_numerator.generate());
		GENERATE_VAR(m_denominator, ::g->m_denominator.generate());
		GENERATE_VAR(m_clocksPerClick, ::g->m_clocksPerClick.generate());
		GENERATE_VAR(m_32ndPer4th, ::g->m_32ndPer4th.generate());
	} else {
	if ((m_type() == META_KEY_SIGNATURE)) {
		GENERATE_VAR(m_flatsSharps, ::g->m_flatsSharps.generate());
		GENERATE_VAR(m_majorMinor, ::g->m_majorMinor.generate());
	} else {
		GENERATE_VAR(m_data, ::g->m_data.generate(m_length().total));
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};
	};

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage_sysex_event_struct* MidiMessage_sysex_event_struct::generate() {
	if (generated == 1) {
		MidiMessage_sysex_event_struct* new_instance = new MidiMessage_sysex_event_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_length, ::g->m_length.generate());
	Printf("\t\tsysex_event m_length: %d\n", m_length().total);
	GENERATE_VAR(m_message, ::g->m_message.generate(m_length().total));
	Printf("\t\tMessage: %s\n", std::string(m_message()).c_str());

	_sizeof = FTell() - _startof;
	return this;
}


MidiMessage* MidiMessage::generate(uint& message_index) {
	if (generated == 1) {
		MidiMessage* new_instance = new MidiMessage(instances);
		new_instance->generated = 2;
		return new_instance->generate(message_index);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_dtime, ::g->m_dtime.generate());
	GENERATE_VAR(m_status, ::g->m_status.generate());
	if ((m_status() & 0x80)) {
	::g->lastStatus = m_status();
	} else {
	FSeek((FTell() - 1));
	};
	Printf("\t---MIDI Message (%d,%d)---\n\t\tStatus: %c\n", ::g->track_index, message_index, m_status());
	m_channel = (::g->lastStatus & 0xf);
	if (((::g->lastStatus & 0xf0) == 0x80)) {
		Printf("\t\tnote_off_event\n");
		GENERATE_VAR(note_off_event, ::g->note_off_event.generate());
		Printf("\t\tNote: %c\n\t\tVelocity: %c\n", note_off_event().m_note(), note_off_event().m_velocity());
	} else {
	if (((::g->lastStatus & 0xf0) == 0x90)) {
		Printf("\t\tnote_on_event\n");
		GENERATE_VAR(note_on_event, ::g->note_on_event.generate());
		Printf("\t\tNote: %c\n\t\tVelocity: %c\n", note_on_event().m_note(), note_on_event().m_velocity());
	} else {
	if (((::g->lastStatus & 0xf0) == 0xA0)) {
		Printf("\t\tnote_pressure_event\n");
		GENERATE_VAR(note_pressure_event, ::g->note_pressure_event.generate());
		Printf("\t\tNote: %c\n\t\tPressure: %c\n", note_pressure_event().m_note(), note_pressure_event().m_pressure());
	} else {
	if (((::g->lastStatus & 0xf0) == 0xB0)) {
		Printf("\t\tcontroller_event\n");
		GENERATE_VAR(controller_event, ::g->controller_event.generate());
		Printf("\t\tController: %c\n\t\tValue: %c\n", controller_event().m_controller(), controller_event().m_value());
	} else {
	if (((::g->lastStatus & 0xf0) == 0xC0)) {
		Printf("\t\tprogram_event\n");
		GENERATE_VAR(program_event, ::g->program_event.generate());
		Printf("\t\tProgram: %c\n", program_event().m_program());
	} else {
	if (((::g->lastStatus & 0xf0) == 0xD0)) {
		Printf("\t\tchannel_pressure_event\n");
		GENERATE_VAR(channel_pressure_event, ::g->channel_pressure_event.generate());
		Printf("\t\tPressure: %c\n", channel_pressure_event().m_pressure());
	} else {
	if (((::g->lastStatus & 0xf0) == 0xE0)) {
		Printf("\t\tpitch_bend_event\n");
		GENERATE_VAR(pitch_bend_event, ::g->pitch_bend_event.generate());
		Printf("\t\tLSB: %c\n\t\tMSB: %c\n", pitch_bend_event().m_lsb(), pitch_bend_event().m_msb());
	} else {
	if ((::g->lastStatus == -1)) {
		Printf("\t\tmeta_event\n");
		GENERATE_VAR(meta_event, ::g->meta_event.generate());
		Printf("\t\tType: %c\n", meta_event().m_type());
	} else {
	if (((::g->lastStatus & 0xf0) == 0xF0)) {
		GENERATE_VAR(sysex_event, ::g->sysex_event.generate());
	};
	};
	};
	};
	};
	};
	};
	};
	};

	_sizeof = FTell() - _startof;
	return this;
}


MidiTrack* MidiTrack::generate() {
	if (generated == 1) {
		MidiTrack* new_instance = new MidiTrack(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(m_magic, ::g->m_magic.generate(4, { "MTrk" }));
	m_seclen_pos = FTell();
	GENERATE_VAR(m_seclen, ::g->m_seclen.generate());
	remaining = m_seclen();
	message_index = 0;
	Printf("---MIDI Track (%d)---\n\tMagic: %s\n\tSection length: %d\n", ::g->track_index, std::string(m_magic()).c_str(), m_seclen());
	sec_start = FTell();
	while (remaining) {
		GENERATE_VAR(message, ::g->message.generate(message_index));
		message_len = message()._sizeof;
		if ((message_len > remaining)) {
			remaining = 0;
			sec_end = FTell();
			FSeek(m_seclen_pos);
			evil_state = SetEvilBit(false);
			GENERATE_VAR(m_seclen, ::g->m_seclen.generate({ (sec_end - sec_start) }));
			SetEvilBit(evil_state);
			FSeek(sec_end);
			break;
		};
		remaining -= message_len;
		message_index++;
	};
	::g->track_index++;

	_sizeof = FTell() - _startof;
	return this;
}


file_struct* file_struct::generate() {
	if (generated == 1) {
		file_struct* new_instance = new file_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(header, ::g->header.generate());
	GENERATE_VAR(tracks, ::g->tracks.generate(header().m_ntracks()));

	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	BigEndian();
	::g->track_index = 0;
	::g->message_index = 0;
	::g->lastStatus = 0;
	GENERATE(file, ::g->file.generate());

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

