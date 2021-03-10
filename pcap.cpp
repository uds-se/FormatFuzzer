#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"


class uint32_class {
	int small;
	std::vector<uint32> known_values;
	uint32 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint32);
	uint32 operator () () { return value; }
	uint32_class(int small, std::vector<uint32> known_values = {}) : small(small), known_values(known_values) {}

	uint32 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint32), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint32), 0, known_values);
		}
		return value;
	}

	uint32 generate(std::vector<uint32> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uint32), 0, possible_values);
		return value;
	}
};



class uint16_class {
	int small;
	std::vector<uint16> known_values;
	uint16 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint16);
	uint16 operator () () { return value; }
	uint16_class(int small, std::vector<uint16> known_values = {}) : small(small), known_values(known_values) {}

	uint16 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint16), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint16), 0, known_values);
		}
		return value;
	}

	uint16 generate(std::vector<uint16> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uint16), 0, possible_values);
		return value;
	}
};



class int32_class {
	int small;
	std::vector<int32> known_values;
	int32 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(int32);
	int32 operator () () { return value; }
	int32_class(int small, std::vector<int32> known_values = {}) : small(small), known_values(known_values) {}

	int32 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(int32), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(int32), 0, known_values);
		}
		return value;
	}

	int32 generate(std::vector<int32> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(int32), 0, possible_values);
		return value;
	}
};



class PCAPHEADER {
	std::vector<PCAPHEADER*>& instances;

	uint32 magic_number_var;
	uint16 version_major_var;
	uint16 version_minor_var;
	int32 thiszone_var;
	uint32 sigfigs_var;
	uint32 snaplen_var;
	uint32 network_var;

public:
	bool magic_number_exists = false;
	bool version_major_exists = false;
	bool version_minor_exists = false;
	bool thiszone_exists = false;
	bool sigfigs_exists = false;
	bool snaplen_exists = false;
	bool network_exists = false;

	uint32 magic_number() {
		assert_cond(magic_number_exists, "struct field magic_number does not exist");
		return magic_number_var;
	}
	uint16 version_major() {
		assert_cond(version_major_exists, "struct field version_major does not exist");
		return version_major_var;
	}
	uint16 version_minor() {
		assert_cond(version_minor_exists, "struct field version_minor does not exist");
		return version_minor_var;
	}
	int32 thiszone() {
		assert_cond(thiszone_exists, "struct field thiszone does not exist");
		return thiszone_var;
	}
	uint32 sigfigs() {
		assert_cond(sigfigs_exists, "struct field sigfigs does not exist");
		return sigfigs_var;
	}
	uint32 snaplen() {
		assert_cond(snaplen_exists, "struct field snaplen does not exist");
		return snaplen_var;
	}
	uint32 network() {
		assert_cond(network_exists, "struct field network does not exist");
		return network_var;
	}

	/* locals */
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PCAPHEADER& operator () () { return *instances.back(); }
	PCAPHEADER* operator [] (int index) { return instances[index]; }
	PCAPHEADER(std::vector<PCAPHEADER*>& instances) : instances(instances) { instances.push_back(this); }
	~PCAPHEADER() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PCAPHEADER* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PCAPHEADER* generate();
};



class time_t_class {
	int small;
	std::vector<uint32> known_values;
	uint32 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint32);
	uint32 operator () () { return value; }
	time_t_class(int small, std::vector<uint32> known_values = {}) : small(small), known_values(known_values) {}

	uint32 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint32), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint32), 0, known_values);
		}
		return value;
	}

	uint32 generate(std::vector<uint32> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uint32), 0, possible_values);
		return value;
	}
};



class uchar_bitfield {
	int small;
	std::vector<uchar> known_values;
	uchar value;
public:
	uchar operator () () { return value; }
	uchar_bitfield(int small, std::vector<uchar> known_values = {}) : small(small), known_values(known_values) {}

	uchar generate(unsigned bits) {
		if (!bits)
			return 0;
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uchar), bits, small);
		} else {
			value = file_acc.file_integer(sizeof(uchar), bits, known_values);
		}
		return value;
	}

	uchar generate(unsigned bits, std::vector<uchar> possible_values) {
		if (!bits)
			return 0;
		value = file_acc.file_integer(sizeof(uchar), bits, possible_values);
		return value;
	}
};



class BYTE_class {
	int small;
	std::vector<BYTE> known_values;
	BYTE value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(BYTE);
	BYTE operator () () { return value; }
	BYTE_class(int small, std::vector<BYTE> known_values = {}) : small(small), known_values(known_values) {}

	BYTE generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(BYTE), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(BYTE), 0, known_values);
		}
		return value;
	}

	BYTE generate(std::vector<BYTE> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(BYTE), 0, possible_values);
		return value;
	}
};



class uchar_class {
	int small;
	std::vector<uchar> known_values;
	uchar value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uchar);
	uchar operator () () { return value; }
	uchar_class(int small, std::vector<uchar> known_values = {}) : small(small), known_values(known_values) {}

	uchar generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uchar), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uchar), 0, known_values);
		}
		return value;
	}

	uchar generate(std::vector<uchar> possible_values) {
		_startof = FTell();
		value = file_acc.file_integer(sizeof(uchar), 0, possible_values);
		return value;
	}
};



class uchar_array_class {
	uchar_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<uchar>> element_known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	uchar operator [] (int index) { return value[index]; }
	uchar_array_class(uchar_class& element, std::unordered_map<int, std::vector<uchar>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	uchar_array_class(uchar_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> possible_values = {}) {
		check_array_length(size);
		_startof = FTell();
		value = "";
		if (possible_values.size()) {
			value = file_acc.file_string(possible_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (known_values.size()) {
			value = file_acc.file_string(known_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (!element_known_values.size()) {
			if (size == 0)
				 return "";
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
				value.push_back(file_acc.file_integer(sizeof(uchar), 0, known->second));
				_sizeof += sizeof(uchar);
			}
		}
		return value;
	}
};



class IPv4addr {
	std::vector<IPv4addr*>& instances;

	std::string Byte_var;

public:
	bool Byte_exists = false;

	std::string Byte() {
		assert_cond(Byte_exists, "struct field Byte does not exist");
		return Byte_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	IPv4addr& operator () () { return *instances.back(); }
	IPv4addr* operator [] (int index) { return instances[index]; }
	IPv4addr(std::vector<IPv4addr*>& instances) : instances(instances) { instances.push_back(this); }
	~IPv4addr() {
		if (generated == 2)
			return;
		while (instances.size()) {
			IPv4addr* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	IPv4addr* generate();
};



class BYTE_array_class {
	BYTE_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<BYTE>> element_known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	BYTE operator [] (int index) { return value[index]; }
	BYTE_array_class(BYTE_class& element, std::unordered_map<int, std::vector<BYTE>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	BYTE_array_class(BYTE_class& element, std::vector<std::string> known_values)
		: element(element), known_values(known_values) {}

	std::string generate(unsigned size, std::vector<std::string> possible_values = {}) {
		check_array_length(size);
		_startof = FTell();
		value = "";
		if (possible_values.size()) {
			value = file_acc.file_string(possible_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		if (known_values.size()) {
			value = file_acc.file_string(known_values);
			assert(value.length() == size);
			_sizeof = size;
			return value;
		}
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(BYTE), 0, known->second));
				_sizeof += sizeof(BYTE);
			}
		}
		return value;
	}
};



class Layer_3 {
	std::vector<Layer_3*>& instances;

	uchar version_var : 4;
	uchar ip_hdr_len_var : 4;
	BYTE DiffServField_var;
	uint16 total_length_var;
	uint16 Identification_var;
	uint16 Flags_var;
	BYTE TTL_var;
	BYTE L4proto_var;
	uint16 HdrChecksum_var;
	IPv4addr* SRC_IP_var;
	IPv4addr* DST_IP_var;
	std::string Unknown_var;

public:
	bool version_exists = false;
	bool ip_hdr_len_exists = false;
	bool DiffServField_exists = false;
	bool total_length_exists = false;
	bool Identification_exists = false;
	bool Flags_exists = false;
	bool TTL_exists = false;
	bool L4proto_exists = false;
	bool HdrChecksum_exists = false;
	bool SRC_IP_exists = false;
	bool DST_IP_exists = false;
	bool Unknown_exists = false;

	uchar version() {
		assert_cond(version_exists, "struct field version does not exist");
		return version_var;
	}
	uchar ip_hdr_len() {
		assert_cond(ip_hdr_len_exists, "struct field ip_hdr_len does not exist");
		return ip_hdr_len_var;
	}
	BYTE DiffServField() {
		assert_cond(DiffServField_exists, "struct field DiffServField does not exist");
		return DiffServField_var;
	}
	uint16 total_length() {
		assert_cond(total_length_exists, "struct field total_length does not exist");
		return total_length_var;
	}
	uint16 Identification() {
		assert_cond(Identification_exists, "struct field Identification does not exist");
		return Identification_var;
	}
	uint16 Flags() {
		assert_cond(Flags_exists, "struct field Flags does not exist");
		return Flags_var;
	}
	BYTE TTL() {
		assert_cond(TTL_exists, "struct field TTL does not exist");
		return TTL_var;
	}
	BYTE L4proto() {
		assert_cond(L4proto_exists, "struct field L4proto does not exist");
		return L4proto_var;
	}
	uint16 HdrChecksum() {
		assert_cond(HdrChecksum_exists, "struct field HdrChecksum does not exist");
		return HdrChecksum_var;
	}
	IPv4addr& SRC_IP() {
		assert_cond(SRC_IP_exists, "struct field SRC_IP does not exist");
		return *SRC_IP_var;
	}
	IPv4addr& DST_IP() {
		assert_cond(DST_IP_exists, "struct field DST_IP does not exist");
		return *DST_IP_var;
	}
	std::string Unknown() {
		assert_cond(Unknown_exists, "struct field Unknown does not exist");
		return Unknown_var;
	}

	/* locals */
	std::vector<ubyte> valid_versions;
	std::vector<ubyte> valid_hdr_lengths;
	int hdr_length;
	uint UnknownLength;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	Layer_3& operator () () { return *instances.back(); }
	Layer_3* operator [] (int index) { return instances[index]; }
	Layer_3(std::vector<Layer_3*>& instances) : instances(instances) { instances.push_back(this); }
	~Layer_3() {
		if (generated == 2)
			return;
		while (instances.size()) {
			Layer_3* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	Layer_3* generate(uint16 proto_type);
};



class MACaddr {
	std::vector<MACaddr*>& instances;

	std::string Byte_var;

public:
	bool Byte_exists = false;

	std::string Byte() {
		assert_cond(Byte_exists, "struct field Byte does not exist");
		return Byte_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	MACaddr& operator () () { return *instances.back(); }
	MACaddr* operator [] (int index) { return instances[index]; }
	MACaddr(std::vector<MACaddr*>& instances) : instances(instances) { instances.push_back(this); }
	~MACaddr() {
		if (generated == 2)
			return;
		while (instances.size()) {
			MACaddr* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	MACaddr* generate();
};



class Layer_2 {
	std::vector<Layer_2*>& instances;

	MACaddr* DstMac_var;
	MACaddr* SrcMac_var;
	uint16 L3type_var;

public:
	bool DstMac_exists = false;
	bool SrcMac_exists = false;
	bool L3type_exists = false;

	MACaddr& DstMac() {
		assert_cond(DstMac_exists, "struct field DstMac does not exist");
		return *DstMac_var;
	}
	MACaddr& SrcMac() {
		assert_cond(SrcMac_exists, "struct field SrcMac does not exist");
		return *SrcMac_var;
	}
	uint16 L3type() {
		assert_cond(L3type_exists, "struct field L3type does not exist");
		return L3type_var;
	}

	/* locals */
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	Layer_2& operator () () { return *instances.back(); }
	Layer_2* operator [] (int index) { return instances[index]; }
	Layer_2(std::vector<Layer_2*>& instances) : instances(instances) { instances.push_back(this); }
	~Layer_2() {
		if (generated == 2)
			return;
		while (instances.size()) {
			Layer_2* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	Layer_2* generate();
};



class uint16_bitfield {
	int small;
	std::vector<uint16> known_values;
	uint16 value;
public:
	uint16 operator () () { return value; }
	uint16_bitfield(int small, std::vector<uint16> known_values = {}) : small(small), known_values(known_values) {}

	uint16 generate(unsigned bits) {
		if (!bits)
			return 0;
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint16), bits, small);
		} else {
			value = file_acc.file_integer(sizeof(uint16), bits, known_values);
		}
		return value;
	}

	uint16 generate(unsigned bits, std::vector<uint16> possible_values) {
		if (!bits)
			return 0;
		value = file_acc.file_integer(sizeof(uint16), bits, possible_values);
		return value;
	}
};



class Dot1q {
	std::vector<Dot1q*>& instances;

	uint16 priority_var : 3;
	uint16 dei_var : 1;
	uint16 id_var : 12;
	uint16 L3type_var;

public:
	bool priority_exists = false;
	bool dei_exists = false;
	bool id_exists = false;
	bool L3type_exists = false;

	uint16 priority() {
		assert_cond(priority_exists, "struct field priority does not exist");
		return priority_var;
	}
	uint16 dei() {
		assert_cond(dei_exists, "struct field dei does not exist");
		return dei_var;
	}
	uint16 id() {
		assert_cond(id_exists, "struct field id does not exist");
		return id_var;
	}
	uint16 L3type() {
		assert_cond(L3type_exists, "struct field L3type does not exist");
		return L3type_var;
	}

	/* locals */
	uint evil_state;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	Dot1q& operator () () { return *instances.back(); }
	Dot1q* operator [] (int index) { return instances[index]; }
	Dot1q(std::vector<Dot1q*>& instances) : instances(instances) { instances.push_back(this); }
	~Dot1q() {
		if (generated == 2)
			return;
		while (instances.size()) {
			Dot1q* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	Dot1q* generate();
};



class TCP_BITFIELDS_struct {
	std::vector<TCP_BITFIELDS_struct*>& instances;

	uchar tcp_hdr_len_var : 4;
	uchar Reserved_var : 4;

public:
	bool tcp_hdr_len_exists = false;
	bool Reserved_exists = false;

	uchar tcp_hdr_len() {
		assert_cond(tcp_hdr_len_exists, "struct field tcp_hdr_len does not exist");
		return tcp_hdr_len_var;
	}
	uchar Reserved() {
		assert_cond(Reserved_exists, "struct field Reserved does not exist");
		return Reserved_var;
	}

	/* locals */
	std::vector<ubyte> possible_lengths;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	TCP_BITFIELDS_struct& operator () () { return *instances.back(); }
	TCP_BITFIELDS_struct* operator [] (int index) { return instances[index]; }
	TCP_BITFIELDS_struct(std::vector<TCP_BITFIELDS_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~TCP_BITFIELDS_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			TCP_BITFIELDS_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	TCP_BITFIELDS_struct* generate();
};



class Layer_4 {
	std::vector<Layer_4*>& instances;

	uint16 SrcPort_var;
	uint16 DstPort_var;
	uint16 udp_hdr_len_var;
	uint16 ChkSum_var;
	uint32 SEQ_var;
	uint32 ACK_var;
	TCP_BITFIELDS_struct* TCP_BITFIELDS_var;
	std::string Crap_var;
	std::string packet_var;

public:
	bool SrcPort_exists = false;
	bool DstPort_exists = false;
	bool udp_hdr_len_exists = false;
	bool ChkSum_exists = false;
	bool SEQ_exists = false;
	bool ACK_exists = false;
	bool TCP_BITFIELDS_exists = false;
	bool Crap_exists = false;
	bool packet_exists = false;

	uint16 SrcPort() {
		assert_cond(SrcPort_exists, "struct field SrcPort does not exist");
		return SrcPort_var;
	}
	uint16 DstPort() {
		assert_cond(DstPort_exists, "struct field DstPort does not exist");
		return DstPort_var;
	}
	uint16 udp_hdr_len() {
		assert_cond(udp_hdr_len_exists, "struct field udp_hdr_len does not exist");
		return udp_hdr_len_var;
	}
	uint16 ChkSum() {
		assert_cond(ChkSum_exists, "struct field ChkSum does not exist");
		return ChkSum_var;
	}
	uint32 SEQ() {
		assert_cond(SEQ_exists, "struct field SEQ does not exist");
		return SEQ_var;
	}
	uint32 ACK() {
		assert_cond(ACK_exists, "struct field ACK does not exist");
		return ACK_var;
	}
	TCP_BITFIELDS_struct& TCP_BITFIELDS() {
		assert_cond(TCP_BITFIELDS_exists, "struct field TCP_BITFIELDS does not exist");
		return *TCP_BITFIELDS_var;
	}
	std::string Crap() {
		assert_cond(Crap_exists, "struct field Crap does not exist");
		return Crap_var;
	}
	std::string packet() {
		assert_cond(packet_exists, "struct field packet does not exist");
		return packet_var;
	}

	/* locals */
	uint16 ip_hdr_length;
	uint16 dgram_len;
	uint CrapSize;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	Layer_4& operator () () { return *instances.back(); }
	Layer_4* operator [] (int index) { return instances[index]; }
	Layer_4(std::vector<Layer_4*>& instances) : instances(instances) { instances.push_back(this); }
	~Layer_4() {
		if (generated == 2)
			return;
		while (instances.size()) {
			Layer_4* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	Layer_4* generate(ushort VER_HDR, uint16 total_length, uint L4proto);
};



class PCAPRECORD {
	std::vector<PCAPRECORD*>& instances;

	uint32 ts_sec_var;
	uint32 ts_usec_var;
	uint32 incl_len_var;
	uint32 orig_len_var;
	Layer_3* L3_var;
	Layer_2* L2_var;
	Dot1q* d1q_var;
	Layer_4* L4_var;
	std::string AppData_var;
	std::string padding_var;

public:
	bool ts_sec_exists = false;
	bool ts_usec_exists = false;
	bool incl_len_exists = false;
	bool orig_len_exists = false;
	bool L3_exists = false;
	bool L2_exists = false;
	bool d1q_exists = false;
	bool L4_exists = false;
	bool AppData_exists = false;
	bool padding_exists = false;

	uint32 ts_sec() {
		assert_cond(ts_sec_exists, "struct field ts_sec does not exist");
		return ts_sec_var;
	}
	uint32 ts_usec() {
		assert_cond(ts_usec_exists, "struct field ts_usec does not exist");
		return ts_usec_var;
	}
	uint32 incl_len() {
		assert_cond(incl_len_exists, "struct field incl_len does not exist");
		return incl_len_var;
	}
	uint32 orig_len() {
		assert_cond(orig_len_exists, "struct field orig_len does not exist");
		return orig_len_var;
	}
	Layer_3& L3() {
		assert_cond(L3_exists, "struct field L3 does not exist");
		return *L3_var;
	}
	Layer_2& L2() {
		assert_cond(L2_exists, "struct field L2 does not exist");
		return *L2_var;
	}
	Dot1q& d1q() {
		assert_cond(d1q_exists, "struct field d1q does not exist");
		return *d1q_var;
	}
	Layer_4& L4() {
		assert_cond(L4_exists, "struct field L4 does not exist");
		return *L4_var;
	}
	std::string AppData() {
		assert_cond(AppData_exists, "struct field AppData does not exist");
		return AppData_var;
	}
	std::string padding() {
		assert_cond(padding_exists, "struct field padding does not exist");
		return padding_var;
	}

	/* locals */
	uint32 len_before_l3;
	uint start_pos;
	uint16 AppDataLen;
	uint end_pos;
	uint frame_length;
	uint PaddingLength;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	PCAPRECORD& operator () () { return *instances.back(); }
	PCAPRECORD* operator [] (int index) { return instances[index]; }
	PCAPRECORD(std::vector<PCAPRECORD*>& instances) : instances(instances) { instances.push_back(this); }
	~PCAPRECORD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			PCAPRECORD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	PCAPRECORD* generate(uint32 network);
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


std::vector<PCAPHEADER*> PCAPHEADER_header_instances;
std::vector<IPv4addr*> IPv4addr_SRC_IP_instances;
std::vector<IPv4addr*> IPv4addr_DST_IP_instances;
std::vector<Layer_3*> Layer_3_L3_instances;
std::vector<MACaddr*> MACaddr_DstMac_instances;
std::vector<MACaddr*> MACaddr_SrcMac_instances;
std::vector<Layer_2*> Layer_2_L2_instances;
std::vector<Dot1q*> Dot1q_d1q_instances;
std::vector<TCP_BITFIELDS_struct*> TCP_BITFIELDS_struct_TCP_BITFIELDS_instances;
std::vector<Layer_4*> Layer_4_L4_instances;
std::vector<PCAPRECORD*> PCAPRECORD_record_instances;


std::unordered_map<std::string, std::string> variable_types = { { "magic_number", "uint32_class" }, { "version_major", "uint16_class" }, { "version_minor", "uint16_class" }, { "thiszone", "int32_class" }, { "sigfigs", "uint32_class" }, { "snaplen", "uint32_class" }, { "network", "uint32_class" }, { "header", "PCAPHEADER" }, { "ts_sec", "time_t_class" }, { "ts_usec", "uint32_class" }, { "incl_len", "uint32_class" }, { "orig_len", "uint32_class" }, { "version", "uchar_bitfield4" }, { "ip_hdr_len", "uchar_bitfield4" }, { "DiffServField", "BYTE_class" }, { "total_length", "uint16_class" }, { "Identification", "uint16_class" }, { "Flags", "uint16_class" }, { "TTL", "BYTE_class" }, { "L4proto", "BYTE_class" }, { "HdrChecksum", "uint16_class" }, { "Byte", "uchar_array_class" }, { "SRC_IP", "IPv4addr" }, { "DST_IP", "IPv4addr" }, { "Unknown", "BYTE_array_class" }, { "L3", "Layer_3" }, { "DstMac", "MACaddr" }, { "SrcMac", "MACaddr" }, { "L3type", "uint16_class" }, { "L2", "Layer_2" }, { "priority", "uint16_bitfield3" }, { "dei", "uint16_bitfield1" }, { "id", "uint16_bitfield12" }, { "d1q", "Dot1q" }, { "SrcPort", "uint16_class" }, { "DstPort", "uint16_class" }, { "udp_hdr_len", "uint16_class" }, { "ChkSum", "uint16_class" }, { "SEQ", "uint32_class" }, { "ACK", "uint32_class" }, { "tcp_hdr_len", "uchar_bitfield4" }, { "Reserved", "uchar_bitfield4" }, { "TCP_BITFIELDS", "TCP_BITFIELDS_struct" }, { "Crap", "BYTE_array_class" }, { "packet", "BYTE_array_class" }, { "L4", "Layer_4" }, { "AppData", "BYTE_array_class" }, { "padding", "uchar_array_class" }, { "record", "PCAPRECORD" } };

std::vector<std::vector<int>> integer_ranges = { { 1, 16 }, { 256, 1024 }, { 20 + 20, 20 + 20 + 64 } };

class globals_class {
public:
	uint32_class magic_number;
	uint16_class version_major;
	uint16_class version_minor;
	int32_class thiszone;
	uint32_class sigfigs;
	uint32_class snaplen;
	uint32_class network;
	PCAPHEADER header;
	time_t_class ts_sec;
	uint32_class ts_usec;
	uint32_class incl_len;
	uint32_class orig_len;
	uchar_bitfield version;
	uchar_bitfield ip_hdr_len;
	BYTE_class DiffServField;
	uint16_class total_length;
	uint16_class Identification;
	uint16_class Flags;
	BYTE_class TTL;
	BYTE_class L4proto;
	uint16_class HdrChecksum;
	uchar_class Byte_element;
	uchar_array_class Byte;
	IPv4addr SRC_IP;
	IPv4addr DST_IP;
	BYTE_class Unknown_element;
	BYTE_array_class Unknown;
	Layer_3 L3;
	MACaddr DstMac;
	MACaddr SrcMac;
	uint16_class L3type;
	Layer_2 L2;
	uint16_bitfield priority;
	uint16_bitfield dei;
	uint16_bitfield id;
	Dot1q d1q;
	uint16_class SrcPort;
	uint16_class DstPort;
	uint16_class udp_hdr_len;
	uint16_class ChkSum;
	uint32_class SEQ;
	uint32_class ACK;
	uchar_bitfield tcp_hdr_len;
	uchar_bitfield Reserved;
	TCP_BITFIELDS_struct TCP_BITFIELDS;
	BYTE_class Crap_element;
	BYTE_array_class Crap;
	BYTE_class packet_element;
	BYTE_array_class packet;
	Layer_4 L4;
	BYTE_class AppData_element;
	BYTE_array_class AppData;
	uchar_class padding_element;
	uchar_array_class padding;
	PCAPRECORD record;


	globals_class() :
		magic_number(1, { 0xA1B2C3D4 }),
		version_major(1),
		version_minor(1),
		thiszone(1),
		sigfigs(1),
		snaplen(3),
		network(1, { 101 }),
		header(PCAPHEADER_header_instances),
		ts_sec(1),
		ts_usec(1),
		incl_len(1),
		orig_len(1),
		version(1),
		ip_hdr_len(1),
		DiffServField(1),
		total_length(4),
		Identification(1),
		Flags(1),
		TTL(1),
		L4proto(1, { 0x11, 0x6, 0x6, 0x11 }),
		HdrChecksum(1),
		Byte_element(false),
		Byte(Byte_element),
		SRC_IP(IPv4addr_SRC_IP_instances),
		DST_IP(IPv4addr_DST_IP_instances),
		Unknown_element(false),
		Unknown(Unknown_element),
		L3(Layer_3_L3_instances),
		DstMac(MACaddr_DstMac_instances),
		SrcMac(MACaddr_SrcMac_instances),
		L3type(1, { 0x0800, 0x8100, 0x86dd }),
		L2(Layer_2_L2_instances),
		priority(1),
		dei(1),
		id(1),
		d1q(Dot1q_d1q_instances),
		SrcPort(1),
		DstPort(1),
		udp_hdr_len(1),
		ChkSum(1),
		SEQ(1),
		ACK(1),
		tcp_hdr_len(1),
		Reserved(1),
		TCP_BITFIELDS(TCP_BITFIELDS_struct_TCP_BITFIELDS_instances),
		Crap_element(false),
		Crap(Crap_element),
		packet_element(false),
		packet(packet_element),
		L4(Layer_4_L4_instances),
		AppData_element(false),
		AppData(AppData_element),
		padding_element(false),
		padding(padding_element),
		record(PCAPRECORD_record_instances)
	{}
};

globals_class* g;


PCAPHEADER* PCAPHEADER::generate() {
	if (generated == 1) {
		PCAPHEADER* new_instance = new PCAPHEADER(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	evil_state = SetEvilBit(false);
	GENERATE_VAR(magic_number, ::g->magic_number.generate({ 0xA1B2C3D4 }));
	SetEvilBit(evil_state);
	if ((magic_number() != 0xA1B2C3D4)) {
		Warning("Not a valid PCAP file");
		exit_template(1);
	};
	GENERATE_VAR(version_major, ::g->version_major.generate({ 2 }));
	GENERATE_VAR(version_minor, ::g->version_minor.generate({ 2, 4 }));
	GENERATE_VAR(thiszone, ::g->thiszone.generate());
	GENERATE_VAR(sigfigs, ::g->sigfigs.generate());
	GENERATE_VAR(snaplen, ::g->snaplen.generate());
	GENERATE_VAR(network, ::g->network.generate({ 1 }));

	_sizeof = FTell() - _startof;
	return this;
}


IPv4addr* IPv4addr::generate() {
	if (generated == 1) {
		IPv4addr* new_instance = new IPv4addr(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(Byte, ::g->Byte.generate(4));

	_sizeof = FTell() - _startof;
	return this;
}


Layer_3* Layer_3::generate(uint16 proto_type) {
	if (generated == 1) {
		Layer_3* new_instance = new Layer_3(instances);
		new_instance->generated = 2;
		return new_instance->generate(proto_type);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	valid_versions = { 4 };
	valid_hdr_lengths = { 5 };
	GENERATE_VAR(version, ::g->version.generate(4, valid_versions));
	GENERATE_VAR(ip_hdr_len, ::g->ip_hdr_len.generate(4, valid_hdr_lengths));
	hdr_length = (ip_hdr_len() * 4);
	GENERATE_VAR(DiffServField, ::g->DiffServField.generate());
	GENERATE_VAR(total_length, ::g->total_length.generate());
	if ((proto_type == 0x0800)) {
		GENERATE_VAR(Identification, ::g->Identification.generate());
		GENERATE_VAR(Flags, ::g->Flags.generate());
		GENERATE_VAR(TTL, ::g->TTL.generate());
		GENERATE_VAR(L4proto, ::g->L4proto.generate());
		GENERATE_VAR(HdrChecksum, ::g->HdrChecksum.generate());
		GENERATE_VAR(SRC_IP, ::g->SRC_IP.generate());
		GENERATE_VAR(DST_IP, ::g->DST_IP.generate());
	} else {
		UnknownLength = (hdr_length - 4);
		GENERATE_VAR(Unknown, ::g->Unknown.generate(UnknownLength));
	};

	_sizeof = FTell() - _startof;
	return this;
}


MACaddr* MACaddr::generate() {
	if (generated == 1) {
		MACaddr* new_instance = new MACaddr(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(Byte, ::g->Byte.generate(6));

	_sizeof = FTell() - _startof;
	return this;
}


Layer_2* Layer_2::generate() {
	if (generated == 1) {
		Layer_2* new_instance = new Layer_2(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(DstMac, ::g->DstMac.generate());
	GENERATE_VAR(SrcMac, ::g->SrcMac.generate());
	evil_state = SetEvilBit(false);
	GENERATE_VAR(L3type, ::g->L3type.generate({ 0x0800, 0x8100 }));
	SetEvilBit(evil_state);

	_sizeof = FTell() - _startof;
	return this;
}


Dot1q* Dot1q::generate() {
	if (generated == 1) {
		Dot1q* new_instance = new Dot1q(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(priority, ::g->priority.generate(3));
	GENERATE_VAR(dei, ::g->dei.generate(1));
	GENERATE_VAR(id, ::g->id.generate(12));
	evil_state = SetEvilBit(false);
	GENERATE_VAR(L3type, ::g->L3type.generate({ 0x0800 }));
	SetEvilBit(evil_state);

	_sizeof = FTell() - _startof;
	return this;
}


TCP_BITFIELDS_struct* TCP_BITFIELDS_struct::generate() {
	if (generated == 1) {
		TCP_BITFIELDS_struct* new_instance = new TCP_BITFIELDS_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	possible_lengths = { 5 };
	GENERATE_VAR(tcp_hdr_len, ::g->tcp_hdr_len.generate(4, possible_lengths));
	GENERATE_VAR(Reserved, ::g->Reserved.generate(4));

	_sizeof = FTell() - _startof;
	return this;
}


Layer_4* Layer_4::generate(ushort VER_HDR, uint16 total_length, uint L4proto) {
	if (generated == 1) {
		Layer_4* new_instance = new Layer_4(instances);
		new_instance->generated = 2;
		return new_instance->generate(VER_HDR, total_length, L4proto);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	ip_hdr_length = (VER_HDR * 4);
	if ((L4proto == 0x11)) {
		GENERATE_VAR(SrcPort, ::g->SrcPort.generate());
		GENERATE_VAR(DstPort, ::g->DstPort.generate());
		dgram_len = (total_length - ip_hdr_length);
		GENERATE_VAR(udp_hdr_len, ::g->udp_hdr_len.generate({ dgram_len }));
		GENERATE_VAR(ChkSum, ::g->ChkSum.generate());
	} else {
	if ((L4proto == 0x6)) {
		GENERATE_VAR(SrcPort, ::g->SrcPort.generate());
		GENERATE_VAR(DstPort, ::g->DstPort.generate());
		GENERATE_VAR(SEQ, ::g->SEQ.generate());
		GENERATE_VAR(ACK, ::g->ACK.generate());
		GENERATE_VAR(TCP_BITFIELDS, ::g->TCP_BITFIELDS.generate());
		CrapSize = ((TCP_BITFIELDS().tcp_hdr_len() * 4) - 13);
		GENERATE_VAR(Crap, ::g->Crap.generate(CrapSize));
	} else {
		GENERATE_VAR(packet, ::g->packet.generate((total_length - ip_hdr_length)));
	};
	};

	_sizeof = FTell() - _startof;
	return this;
}


PCAPRECORD* PCAPRECORD::generate(uint32 network) {
	if (generated == 1) {
		PCAPRECORD* new_instance = new PCAPRECORD(instances);
		new_instance->generated = 2;
		return new_instance->generate(network);
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(ts_sec, ::g->ts_sec.generate());
	GENERATE_VAR(ts_usec, ::g->ts_usec.generate());
	GENERATE_VAR(incl_len, ::g->incl_len.generate());
	GENERATE_VAR(orig_len, ::g->orig_len.generate());
	BigEndian();
	len_before_l3 = 0;
	start_pos = FTell();
	if ((network == 101)) {
		GENERATE_VAR(L3, ::g->L3.generate(0x0800));
	} else {
		GENERATE_VAR(L2, ::g->L2.generate());
		len_before_l3 += 14;
		if ((L2().L3type() == 0x0800)) {
			GENERATE_VAR(L3, ::g->L3.generate(L2().L3type()));
		} else {
		if ((L2().L3type() == 0x8100)) {
			GENERATE_VAR(d1q, ::g->d1q.generate());
			len_before_l3 += 4;
			GENERATE_VAR(L3, ::g->L3.generate(d1q().L3type()));
		} else {
		if ((L2().L3type() == 0x86dd)) {
			Printf("IPv6 is not yet supported!");
			exit_template(-1);
		} else {
			Printf("Unsupported L3 Type: 0x%x", L2().L3type());
			exit_template(-1);
		};
		};
		};
	};
	GENERATE_VAR(L4, ::g->L4.generate(L3().ip_hdr_len(), L3().total_length(), L3().L4proto()));
	if ((L3().L4proto() == 0x6)) {
		AppDataLen = ((L3().total_length() - (L3().ip_hdr_len() * 4)) - (L4().TCP_BITFIELDS().tcp_hdr_len() * 4));
		if ((AppDataLen > 0)) {
			GENERATE_VAR(AppData, ::g->AppData.generate(AppDataLen));
		};
	} else {
	if ((L3().L4proto() == 0x11)) {
		AppDataLen = (L4().udp_hdr_len() - 8);
		if ((AppDataLen > 0)) {
			GENERATE_VAR(AppData, ::g->AppData.generate(AppDataLen));
		};
	};
	};
	end_pos = FTell();
	frame_length = (end_pos - start_pos);
	FSeek((start_pos - 8));
	LittleEndian();
	GENERATE_VAR(incl_len, ::g->incl_len.generate({ frame_length }));
	GENERATE_VAR(orig_len, ::g->orig_len.generate({ frame_length }));
	BigEndian();
	FSeek(end_pos);
	if (((len_before_l3 + L3().total_length()) < incl_len())) {
		PaddingLength = ((incl_len() - len_before_l3) - L3().total_length());
		GENERATE_VAR(padding, ::g->padding.generate(PaddingLength));
	};
	LittleEndian();

	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	LittleEndian();
	GENERATE(header, ::g->header.generate());
	while (!FEof()) {
		GENERATE(record, ::g->record.generate(::g->header().network()));
	};

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

