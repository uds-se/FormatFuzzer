#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include "bt.h"
typedef char VERSIONTYPE;

enum SignatureTYPE_enum : uint {
	S_ZIPFILERECORD = (uint) 0x04034b50,
	S_ZIPDATADESCR = (uint) 0x08074b50,
	S_ZIPDIRENTRY = (uint) 0x02014b50,
	S_ZIPDIGITALSIG = (uint) 0x05054b50,
	S_ZIP64ENDLOCATORRECORD = (uint) 0x06064b50,
	S_ZIP64ENDLOCATOR = (uint) 0x07064b50,
	S_ZIPENDLOCATOR = (uint) 0x06054b50,
};
std::vector<uint> SignatureTYPE_enum_values = { S_ZIPFILERECORD, S_ZIPDATADESCR, S_ZIPDIRENTRY, S_ZIPDIGITALSIG, S_ZIP64ENDLOCATORRECORD, S_ZIP64ENDLOCATOR, S_ZIPENDLOCATOR };

typedef enum SignatureTYPE_enum SignatureTYPE;
std::vector<uint> SignatureTYPE_values = { S_ZIPFILERECORD, S_ZIPDATADESCR, S_ZIPDIRENTRY, S_ZIPDIGITALSIG, S_ZIP64ENDLOCATORRECORD, S_ZIP64ENDLOCATOR, S_ZIPENDLOCATOR };

enum HOSTOSTYPE_enum : byte {
	OS_FAT = (byte) 0,
	OS_AMIGA = (byte) 1,
	OS_VMS = (byte) 2,
	OS_Unix = (byte) 3,
	OS_VM_CMS = (byte) 4,
	OS_Atari = (byte) 5,
	OS_HPFS = (byte) 6,
	OS_Mac = (byte) 7,
	OS_Z_System = (byte) 8,
	OS_CPM = (byte) 9,
	OS_TOPS20 = (byte) 10,
	OS_NTFS = (byte) 11,
	OS_QDOS = (byte) 12,
	OS_Acorn = (byte) 13,
	OS_VFAT = (byte) 14,
	OS_MVS = (byte) 15,
	OS_BeOS = (byte) 16,
	OS_Tandem = (byte) 17,
	OS_OS400 = (byte) 18,
	OS_OSX = (byte) 19,
};
std::vector<byte> HOSTOSTYPE_enum_values = { OS_FAT, OS_AMIGA, OS_VMS, OS_Unix, OS_VM_CMS, OS_Atari, OS_HPFS, OS_Mac, OS_Z_System, OS_CPM, OS_TOPS20, OS_NTFS, OS_QDOS, OS_Acorn, OS_VFAT, OS_MVS, OS_BeOS, OS_Tandem, OS_OS400, OS_OSX };

typedef enum HOSTOSTYPE_enum HOSTOSTYPE;
std::vector<byte> HOSTOSTYPE_values = { OS_FAT, OS_AMIGA, OS_VMS, OS_Unix, OS_VM_CMS, OS_Atari, OS_HPFS, OS_Mac, OS_Z_System, OS_CPM, OS_TOPS20, OS_NTFS, OS_QDOS, OS_Acorn, OS_VFAT, OS_MVS, OS_BeOS, OS_Tandem, OS_OS400, OS_OSX };

enum COMPTYPE_enum : short {
	COMP_STORED = (short) 0,
	COMP_SHRUNK = (short) 1,
	COMP_REDUCED1 = (short) 2,
	COMP_REDUCED2 = (short) 3,
	COMP_REDUCED3 = (short) 4,
	COMP_REDUCED4 = (short) 5,
	COMP_IMPLODED = (short) 6,
	COMP_TOKEN = (short) 7,
	COMP_DEFLATE = (short) 8,
	COMP_DEFLATE64 = (short) 9,
	COMP_PKImploding = (short) 10,
	COMP_BZip2 = (short) 12,
	COMP_LZMA = (short) 14,
	COMP_Terse = (short) 18,
	COMP_Lz77 = (short) 19,
	COMP_Jpeg = (short) 0x60,
	COMP_WavPack = (short) 0x61,
	COMP_PPMd = (short) 0x62,
	COMP_WzAES = (short) 0x63,
};
std::vector<short> COMPTYPE_enum_values = { COMP_STORED, COMP_SHRUNK, COMP_REDUCED1, COMP_REDUCED2, COMP_REDUCED3, COMP_REDUCED4, COMP_IMPLODED, COMP_TOKEN, COMP_DEFLATE, COMP_DEFLATE64, COMP_PKImploding, COMP_BZip2, COMP_LZMA, COMP_Terse, COMP_Lz77, COMP_Jpeg, COMP_WavPack, COMP_PPMd, COMP_WzAES };

typedef enum COMPTYPE_enum COMPTYPE;
std::vector<short> COMPTYPE_values = { COMP_STORED, COMP_SHRUNK, COMP_REDUCED1, COMP_REDUCED2, COMP_REDUCED3, COMP_REDUCED4, COMP_IMPLODED, COMP_TOKEN, COMP_DEFLATE, COMP_DEFLATE64, COMP_PKImploding, COMP_BZip2, COMP_LZMA, COMP_Terse, COMP_Lz77, COMP_Jpeg, COMP_WavPack, COMP_PPMd, COMP_WzAES };

enum FLAGTYPE_enum : ushort {
	FLAG_Encrypted = (ushort) 0x0001,
	FLAG_CompressionFlagBit1 = (ushort) 0x0002,
	FLAG_CompressionFlagBit2 = (ushort) 0x0004,
	FLAG_DescriptorUsedMask = (ushort) 0x0008,
	FLAG_Reserved1 = (ushort) 0x0010,
	FLAG_Reserved2 = (ushort) 0x0020,
	FLAG_StrongEncrypted = (ushort) 0x0040,
	FLAG_CurrentlyUnused1 = (ushort) 0x0080,
	FLAG_CurrentlyUnused2 = (ushort) 0x0100,
	FLAG_CurrentlyUnused3 = (ushort) 0x0200,
	FLAG_CurrentlyUnused4 = (ushort) 0x0400,
	FLAG_Utf8 = (ushort) 0x0800,
	FLAG_ReservedPKWARE1 = (ushort) 0x1000,
	FLAG_CDEncrypted = (ushort) 0x2000,
	FLAG_ReservedPKWARE2 = (ushort) 0x4000,
	FLAG_ReservedPKWARE3 = (ushort) 0x8000,
};
std::vector<ushort> FLAGTYPE_enum_values = { FLAG_Encrypted, FLAG_CompressionFlagBit1, FLAG_CompressionFlagBit2, FLAG_DescriptorUsedMask, FLAG_Reserved1, FLAG_Reserved2, FLAG_StrongEncrypted, FLAG_CurrentlyUnused1, FLAG_CurrentlyUnused2, FLAG_CurrentlyUnused3, FLAG_CurrentlyUnused4, FLAG_Utf8, FLAG_ReservedPKWARE1, FLAG_CDEncrypted, FLAG_ReservedPKWARE2, FLAG_ReservedPKWARE3 };

typedef enum FLAGTYPE_enum FLAGTYPE;
std::vector<ushort> FLAGTYPE_values = { FLAG_Encrypted, FLAG_CompressionFlagBit1, FLAG_CompressionFlagBit2, FLAG_DescriptorUsedMask, FLAG_Reserved1, FLAG_Reserved2, FLAG_StrongEncrypted, FLAG_CurrentlyUnused1, FLAG_CurrentlyUnused2, FLAG_CurrentlyUnused3, FLAG_CurrentlyUnused4, FLAG_Utf8, FLAG_ReservedPKWARE1, FLAG_CDEncrypted, FLAG_ReservedPKWARE2, FLAG_ReservedPKWARE3 };

enum HEADERFLAG_enum : ushort {
	EH_Zip64 = (ushort) 0x0001,
	EH_AVInfo = (ushort) 0x0007,
	EH_ExtLanguage = (ushort) 0x0008,
	EH_OS2 = (ushort) 0x0009,
	EH_NTFS = (ushort) 0x000a,
	EH_OpenVMS = (ushort) 0x000c,
	EH_UNIX = (ushort) 0x000d,
	EH_fileStream = (ushort) 0x000e,
	EH_PatchDescriptor = (ushort) 0x000f,
	EH_PKCS7X509 = (ushort) 0x0014,
	EH_X509IDSignature = (ushort) 0x0015,
	EH_X509IDCD = (ushort) 0x0016,
	EH_StrongEncryption = (ushort) 0x0017,
	EH_RecordManagement = (ushort) 0x0018,
	EH_PKCS7List = (ushort) 0x0019,
	EH_Attributes = (ushort) 0x0065,
	EH_ReservedAttributes = (ushort) 0x0066,
	EH_POSZIP4690 = (ushort) 0x4690,
	EH_Mac = (ushort) 0x07c8,
	EH_ZipItMac1 = (ushort) 0x2605,
	EH_ZipItMac2 = (ushort) 0x2705,
	EH_ZipItMac3 = (ushort) 0x2805,
	EH_InfoZIPMac = (ushort) 0x334d,
	EH_Acorn = (ushort) 0x4341,
	EH_WinNTSecurity = (ushort) 0x4453,
	EH_VM_CMS = (ushort) 0x4704,
	EH_MVS = (ushort) 0x470f,
	EH_FWKCS = (ushort) 0x4b46,
	EH_OS2AccessList = (ushort) 0x4c41,
	EH_InfoZIPOpenVMS = (ushort) 0x4d49,
	EH_Xceed = (ushort) 0x4f4c,
	EH_AOSVS = (ushort) 0x5356,
	EH_extTimestamp = (ushort) 0x5455,
	EH_XceedUnicode = (ushort) 0x554e,
	EH_InfoZIPUNIX = (ushort) 0x5855,
	EH_InfoZIPUnicodeComment = (ushort) 0x6375,
	EH_BeOS = (ushort) 0x6542,
	EH_InfoZIPUnicodePath = (ushort) 0x7075,
	EH_ASiUNIX = (ushort) 0x756e,
	EH_InfoZIPUNIXNew = (ushort) 0x7855,
	EH_InfoZIPUNIXNew3rd = (ushort) 0x7875,
	EH_WinGrowth = (ushort) 0xa220,
	EH_SMSQDOS = (ushort) 0xfd4a,
	EH_WzAES = (ushort) 0x9901,
};
std::vector<ushort> HEADERFLAG_enum_values = { EH_Zip64, EH_AVInfo, EH_ExtLanguage, EH_OS2, EH_NTFS, EH_OpenVMS, EH_UNIX, EH_fileStream, EH_PatchDescriptor, EH_PKCS7X509, EH_X509IDSignature, EH_X509IDCD, EH_StrongEncryption, EH_RecordManagement, EH_PKCS7List, EH_Attributes, EH_ReservedAttributes, EH_POSZIP4690, EH_Mac, EH_ZipItMac1, EH_ZipItMac2, EH_ZipItMac3, EH_InfoZIPMac, EH_Acorn, EH_WinNTSecurity, EH_VM_CMS, EH_MVS, EH_FWKCS, EH_OS2AccessList, EH_InfoZIPOpenVMS, EH_Xceed, EH_AOSVS, EH_extTimestamp, EH_XceedUnicode, EH_InfoZIPUNIX, EH_InfoZIPUnicodeComment, EH_BeOS, EH_InfoZIPUnicodePath, EH_ASiUNIX, EH_InfoZIPUNIXNew, EH_InfoZIPUNIXNew3rd, EH_WinGrowth, EH_SMSQDOS, EH_WzAES };

typedef enum HEADERFLAG_enum HEADERFLAG;
std::vector<ushort> HEADERFLAG_values = { EH_Zip64, EH_AVInfo, EH_ExtLanguage, EH_OS2, EH_NTFS, EH_OpenVMS, EH_UNIX, EH_fileStream, EH_PatchDescriptor, EH_PKCS7X509, EH_X509IDSignature, EH_X509IDCD, EH_StrongEncryption, EH_RecordManagement, EH_PKCS7List, EH_Attributes, EH_ReservedAttributes, EH_POSZIP4690, EH_Mac, EH_ZipItMac1, EH_ZipItMac2, EH_ZipItMac3, EH_InfoZIPMac, EH_Acorn, EH_WinNTSecurity, EH_VM_CMS, EH_MVS, EH_FWKCS, EH_OS2AccessList, EH_InfoZIPOpenVMS, EH_Xceed, EH_AOSVS, EH_extTimestamp, EH_XceedUnicode, EH_InfoZIPUNIX, EH_InfoZIPUnicodeComment, EH_BeOS, EH_InfoZIPUnicodePath, EH_ASiUNIX, EH_InfoZIPUNIXNew, EH_InfoZIPUNIXNew3rd, EH_WinGrowth, EH_SMSQDOS, EH_WzAES };

enum ALGFLAG_enum : ushort {
	AlgID_DES = (ushort) 0x6601,
	AlgID_RC2OLD = (ushort) 0x6602,
	AlgID_3DES168 = (ushort) 0x6603,
	AlgID_3DES112 = (ushort) 0x6609,
	AlgID_AES128 = (ushort) 0x660E,
	AlgID_AES192 = (ushort) 0x660F,
	AlgID_AES256 = (ushort) 0x6610,
	AlgID_RC2 = (ushort) 0x6702,
	AlgID_Blowfish = (ushort) 0x6720,
	AlgID_Twofish = (ushort) 0x6721,
	AlgID_RC4 = (ushort) 0x6801,
	AlgID_Unknown = (ushort) 0xFFFF,
};
std::vector<ushort> ALGFLAG_enum_values = { AlgID_DES, AlgID_RC2OLD, AlgID_3DES168, AlgID_3DES112, AlgID_AES128, AlgID_AES192, AlgID_AES256, AlgID_RC2, AlgID_Blowfish, AlgID_Twofish, AlgID_RC4, AlgID_Unknown };

typedef enum ALGFLAG_enum ALGFLAG;
std::vector<ushort> ALGFLAG_values = { AlgID_DES, AlgID_RC2OLD, AlgID_3DES168, AlgID_3DES112, AlgID_AES128, AlgID_AES192, AlgID_AES256, AlgID_RC2, AlgID_Blowfish, AlgID_Twofish, AlgID_RC4, AlgID_Unknown };

enum AESMODE_enum : byte {
	AES128 = (byte) 0x01,
	AES192 = (byte) 0x02,
	AES256 = (byte) 0x03,
};
std::vector<byte> AESMODE_enum_values = { AES128, AES192, AES256 };

typedef enum AESMODE_enum AESMODE;
std::vector<byte> AESMODE_values = { AES128, AES192, AES256 };

enum PRCFLAG_enum : ushort {
	pfPassword = (ushort) 0x0001,
	pfCertificates = (ushort) 0x0002,
	pfPasswordCertificates = (ushort) 0x0003,
};
std::vector<ushort> PRCFLAG_enum_values = { pfPassword, pfCertificates, pfPasswordCertificates };

typedef enum PRCFLAG_enum PRCFLAG;
std::vector<ushort> PRCFLAG_values = { pfPassword, pfCertificates, pfPasswordCertificates };

enum FILEATTRIBUTE_enum : uint {
	FA_READONLY = (uint) 0x00000001,
	FA_HIDDEN = (uint) 0x00000002,
	FA_SYSTEM = (uint) 0x00000004,
	FA_DIRECTORY = (uint) 0x00000010,
	FA_ARCHIVE = (uint) 0x00000020,
	FA_DEVICE = (uint) 0x00000040,
	FA_NORMAL = (uint) 0x00000080,
	FA_TEMPORARY = (uint) 0x00000100,
	FA_SPARSE_FILE = (uint) 0x00000200,
	FA_REPARSE_POINT = (uint) 0x00000400,
	FA_COMPRESSED = (uint) 0x00000800,
	FA_OFFLINE = (uint) 0x00001000,
	FA_NOT_CONTENT_INDEXED = (uint) 0x00002000,
	FA_ENCRYPTED = (uint) 0x00004000,
	FA_VIRTUAL = (uint) 0x00010000,
	kIFMT = (uint) (0170000 << 16),
	kIFDIR = (uint) (0040000 << 16),
	kIFREG = (uint) (0100000 << 16),
	kIFSOCK = (uint) (0140000 << 16),
	kIFLNK = (uint) (0120000 << 16),
	kIFBLK = (uint) (0060000 << 16),
	kIFCHR = (uint) (0020000 << 16),
	kIFIFO = (uint) (0010000 << 16),
	kISUID = (uint) (04000 << 16),
	kISGID = (uint) (02000 << 16),
	kISVTX = (uint) (01000 << 16),
	kIRWXU = (uint) (00700 << 16),
	kIRUSR = (uint) (00400 << 16),
	kIWUSR = (uint) (00200 << 16),
	kIXUSR = (uint) (00100 << 16),
	kIRWXG = (uint) (00070 << 16),
	kIRGRP = (uint) (00040 << 16),
	kIWGRP = (uint) (00020 << 16),
	kIXGRP = (uint) (00010 << 16),
	kIRWXO = (uint) (00007 << 16),
	kIROTH = (uint) (00004 << 16),
	kIWOTH = (uint) (00002 << 16),
	kIXOTH = (uint) (00001 << 16),
};
std::vector<uint> FILEATTRIBUTE_enum_values = { FA_READONLY, FA_HIDDEN, FA_SYSTEM, FA_DIRECTORY, FA_ARCHIVE, FA_DEVICE, FA_NORMAL, FA_TEMPORARY, FA_SPARSE_FILE, FA_REPARSE_POINT, FA_COMPRESSED, FA_OFFLINE, FA_NOT_CONTENT_INDEXED, FA_ENCRYPTED, FA_VIRTUAL, kIFMT, kIFDIR, kIFREG, kIFSOCK, kIFLNK, kIFBLK, kIFCHR, kIFIFO, kISUID, kISGID, kISVTX, kIRWXU, kIRUSR, kIWUSR, kIXUSR, kIRWXG, kIRGRP, kIWGRP, kIXGRP, kIRWXO, kIROTH, kIWOTH, kIXOTH };

typedef enum FILEATTRIBUTE_enum FILEATTRIBUTE;
std::vector<uint> FILEATTRIBUTE_values = { FA_READONLY, FA_HIDDEN, FA_SYSTEM, FA_DIRECTORY, FA_ARCHIVE, FA_DEVICE, FA_NORMAL, FA_TEMPORARY, FA_SPARSE_FILE, FA_REPARSE_POINT, FA_COMPRESSED, FA_OFFLINE, FA_NOT_CONTENT_INDEXED, FA_ENCRYPTED, FA_VIRTUAL, kIFMT, kIFDIR, kIFREG, kIFSOCK, kIFLNK, kIFBLK, kIFCHR, kIFIFO, kISUID, kISGID, kISVTX, kIRWXU, kIRUSR, kIWUSR, kIXUSR, kIRWXG, kIRGRP, kIWGRP, kIXGRP, kIRWXO, kIROTH, kIWOTH, kIXOTH };

SignatureTYPE SignatureTYPE_generate() {
	return (SignatureTYPE) file_acc.file_integer(sizeof(uint), 0, SignatureTYPE_values);
}

SignatureTYPE SignatureTYPE_generate(std::vector<uint> known_values) {
	return (SignatureTYPE) file_acc.file_integer(sizeof(uint), 0, known_values);
}


class VERSIONTYPE_class {
	int small;
	std::vector<VERSIONTYPE> known_values;
	VERSIONTYPE value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(VERSIONTYPE);
	VERSIONTYPE operator () () { return value; }
	VERSIONTYPE_class(int small, std::vector<VERSIONTYPE> known_values = {}) : small(small), known_values(known_values) {}

	VERSIONTYPE generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(VERSIONTYPE), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(VERSIONTYPE), 0, known_values);
		}
		return value;
	}

	VERSIONTYPE generate(std::vector<VERSIONTYPE> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(VERSIONTYPE), 0, new_known_values);
		return value;
	}
};


HOSTOSTYPE HOSTOSTYPE_generate() {
	return (HOSTOSTYPE) file_acc.file_integer(sizeof(byte), 0, HOSTOSTYPE_values);
}

HOSTOSTYPE HOSTOSTYPE_generate(std::vector<byte> known_values) {
	return (HOSTOSTYPE) file_acc.file_integer(sizeof(byte), 0, known_values);
}


class VERECORD {
	std::vector<VERECORD*>& instances;

	VERSIONTYPE Version_var;
	byte HostOS_var;

public:
	bool Version_exists = false;
	bool HostOS_exists = false;

	VERSIONTYPE Version() {
		assert_cond(Version_exists, "struct field Version does not exist");
		return Version_var;
	}
	byte HostOS() {
		assert_cond(HostOS_exists, "struct field HostOS does not exist");
		return HostOS_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	VERECORD& operator () () { return *instances.back(); }
	VERECORD* operator [] (int index) { return instances[index]; }
	VERECORD(std::vector<VERECORD*>& instances) : instances(instances) { instances.push_back(this); }
	~VERECORD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			VERECORD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	VERECORD* generate();
};


FLAGTYPE FLAGTYPE_generate() {
	return (FLAGTYPE) file_acc.file_integer(sizeof(ushort), 0, FLAGTYPE_values);
}

FLAGTYPE FLAGTYPE_generate(std::vector<ushort> known_values) {
	return (FLAGTYPE) file_acc.file_integer(sizeof(ushort), 0, known_values);
}

COMPTYPE COMPTYPE_generate() {
	return (COMPTYPE) file_acc.file_integer(sizeof(short), 0, COMPTYPE_values);
}

COMPTYPE COMPTYPE_generate(std::vector<short> known_values) {
	return (COMPTYPE) file_acc.file_integer(sizeof(short), 0, known_values);
}


class ushort_class {
	int small;
	std::vector<ushort> known_values;
	ushort value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(ushort);
	ushort operator () () { return value; }
	ushort_class(int small, std::vector<ushort> known_values = {}) : small(small), known_values(known_values) {}

	ushort generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(ushort), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(ushort), 0, known_values);
		}
		return value;
	}

	ushort generate(std::vector<ushort> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(ushort), 0, new_known_values);
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


HEADERFLAG HEADERFLAG_generate() {
	return (HEADERFLAG) file_acc.file_integer(sizeof(ushort), 0, HEADERFLAG_values);
}

HEADERFLAG HEADERFLAG_generate(std::vector<ushort> known_values) {
	return (HEADERFLAG) file_acc.file_integer(sizeof(ushort), 0, known_values);
}


class uint64_class {
	int small;
	std::vector<uint64> known_values;
	uint64 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(uint64);
	uint64 operator () () { return value; }
	uint64_class(int small, std::vector<uint64> known_values = {}) : small(small), known_values(known_values) {}

	uint64 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(uint64), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(uint64), 0, known_values);
		}
		return value;
	}

	uint64 generate(std::vector<uint64> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uint64), 0, new_known_values);
		return value;
	}
};



class byte_class {
	int small;
	std::vector<byte> known_values;
	byte value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(byte);
	byte operator () () { return value; }
	byte_class(int small, std::vector<byte> known_values = {}) : small(small), known_values(known_values) {}

	byte generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(byte), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(byte), 0, known_values);
		}
		return value;
	}

	byte generate(std::vector<byte> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(byte), 0, new_known_values);
		return value;
	}
};



class int_class {
	int small;
	std::vector<int> known_values;
	int value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(int);
	int operator () () { return value; }
	int_class(int small, std::vector<int> known_values = {}) : small(small), known_values(known_values) {}

	int generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(int), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(int), 0, known_values);
		}
		return value;
	}

	int generate(std::vector<int> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(int), 0, new_known_values);
		return value;
	}
};



class DWORD_class {
	int small;
	std::vector<DWORD> known_values;
	DWORD value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(DWORD);
	DWORD operator () () { return value; }
	DWORD_class(int small, std::vector<DWORD> known_values = {}) : small(small), known_values(known_values) {}

	DWORD generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(DWORD), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(DWORD), 0, known_values);
		}
		return value;
	}

	DWORD generate(std::vector<DWORD> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(DWORD), 0, new_known_values);
		return value;
	}
};



class FILETIME {
	std::vector<FILETIME*>& instances;

	DWORD dwLowDateTime_var;
	DWORD dwHighDateTime_var;

public:
	bool dwLowDateTime_exists = false;
	bool dwHighDateTime_exists = false;

	DWORD dwLowDateTime() {
		assert_cond(dwLowDateTime_exists, "struct field dwLowDateTime does not exist");
		return dwLowDateTime_var;
	}
	DWORD dwHighDateTime() {
		assert_cond(dwHighDateTime_exists, "struct field dwHighDateTime does not exist");
		return dwHighDateTime_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	FILETIME& operator () () { return *instances.back(); }
	FILETIME* operator [] (int index) { return instances[index]; }
	FILETIME(std::vector<FILETIME*>& instances) : instances(instances) { instances.push_back(this); }
	~FILETIME() {
		if (generated == 2)
			return;
		while (instances.size()) {
			FILETIME* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	FILETIME* generate();
};



class byte_array_class {
	byte_class& element;
	std::vector<std::string> known_values;
	std::unordered_map<int, std::vector<byte>> element_known_values;
	std::string value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	std::string operator () () { return value; }
	byte operator [] (int index) { return value[index]; }
	byte_array_class(byte_class& element, std::unordered_map<int, std::vector<byte>> element_known_values = {})
		: element(element), element_known_values(element_known_values) {}
	byte_array_class(byte_class& element, std::vector<std::string> known_values)
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
		for (unsigned i = 0; i < size; ++i) {
			auto known = element_known_values.find(i);
			if (known == element_known_values.end()) {
				value.push_back(element.generate());
				_sizeof += element._sizeof;
			} else {
				value.push_back(file_acc.file_integer(sizeof(byte), 0, known->second));
				_sizeof += sizeof(byte);
			}
		}
		return value;
	}
};


ALGFLAG ALGFLAG_generate() {
	return (ALGFLAG) file_acc.file_integer(sizeof(ushort), 0, ALGFLAG_values);
}

ALGFLAG ALGFLAG_generate(std::vector<ushort> known_values) {
	return (ALGFLAG) file_acc.file_integer(sizeof(ushort), 0, known_values);
}

PRCFLAG PRCFLAG_generate() {
	return (PRCFLAG) file_acc.file_integer(sizeof(ushort), 0, PRCFLAG_values);
}

PRCFLAG PRCFLAG_generate(std::vector<ushort> known_values) {
	return (PRCFLAG) file_acc.file_integer(sizeof(ushort), 0, known_values);
}

AESMODE AESMODE_generate() {
	return (AESMODE) file_acc.file_integer(sizeof(byte), 0, AESMODE_values);
}

AESMODE AESMODE_generate(std::vector<byte> known_values) {
	return (AESMODE) file_acc.file_integer(sizeof(byte), 0, known_values);
}


class EXTRAFIELD {
	std::vector<EXTRAFIELD*>& instances;

	ushort efHeaderID_var;
	ushort efDataSize_var;
	uint64 efOriginalSize_var;
	uint64 efCompressedSize_var;
	byte efVersion_var;
	uint efNameCRC32_var;
	std::string efUnicodeName_var;
	int Reserved_var;
	ushort Tag_var;
	ushort Size_var;
	FILETIME* Mtime_var;
	FILETIME* Atime_var;
	FILETIME* Ctime_var;
	std::string Data_var;
	ushort Format_var;
	ushort AlgID_var;
	ushort Bitlen_var;
	ushort Flags_var;
	std::string CertData_var;
	ushort version_var;
	std::string VendorID_var;
	byte Strength_var;
	short deCompression_var;
	std::string efData_var;

public:
	bool efHeaderID_exists = false;
	bool efDataSize_exists = false;
	bool efOriginalSize_exists = false;
	bool efCompressedSize_exists = false;
	bool efVersion_exists = false;
	bool efNameCRC32_exists = false;
	bool efUnicodeName_exists = false;
	bool Reserved_exists = false;
	bool Tag_exists = false;
	bool Size_exists = false;
	bool Mtime_exists = false;
	bool Atime_exists = false;
	bool Ctime_exists = false;
	bool Data_exists = false;
	bool Format_exists = false;
	bool AlgID_exists = false;
	bool Bitlen_exists = false;
	bool Flags_exists = false;
	bool CertData_exists = false;
	bool version_exists = false;
	bool VendorID_exists = false;
	bool Strength_exists = false;
	bool deCompression_exists = false;
	bool efData_exists = false;

	ushort efHeaderID() {
		assert_cond(efHeaderID_exists, "struct field efHeaderID does not exist");
		return efHeaderID_var;
	}
	ushort efDataSize() {
		assert_cond(efDataSize_exists, "struct field efDataSize does not exist");
		return efDataSize_var;
	}
	uint64 efOriginalSize() {
		assert_cond(efOriginalSize_exists, "struct field efOriginalSize does not exist");
		return efOriginalSize_var;
	}
	uint64 efCompressedSize() {
		assert_cond(efCompressedSize_exists, "struct field efCompressedSize does not exist");
		return efCompressedSize_var;
	}
	byte efVersion() {
		assert_cond(efVersion_exists, "struct field efVersion does not exist");
		return efVersion_var;
	}
	uint efNameCRC32() {
		assert_cond(efNameCRC32_exists, "struct field efNameCRC32 does not exist");
		return efNameCRC32_var;
	}
	std::string efUnicodeName() {
		assert_cond(efUnicodeName_exists, "struct field efUnicodeName does not exist");
		return efUnicodeName_var;
	}
	int Reserved() {
		assert_cond(Reserved_exists, "struct field Reserved does not exist");
		return Reserved_var;
	}
	ushort Tag() {
		assert_cond(Tag_exists, "struct field Tag does not exist");
		return Tag_var;
	}
	ushort Size() {
		assert_cond(Size_exists, "struct field Size does not exist");
		return Size_var;
	}
	FILETIME& Mtime() {
		assert_cond(Mtime_exists, "struct field Mtime does not exist");
		return *Mtime_var;
	}
	FILETIME& Atime() {
		assert_cond(Atime_exists, "struct field Atime does not exist");
		return *Atime_var;
	}
	FILETIME& Ctime() {
		assert_cond(Ctime_exists, "struct field Ctime does not exist");
		return *Ctime_var;
	}
	std::string Data() {
		assert_cond(Data_exists, "struct field Data does not exist");
		return Data_var;
	}
	ushort Format() {
		assert_cond(Format_exists, "struct field Format does not exist");
		return Format_var;
	}
	ushort AlgID() {
		assert_cond(AlgID_exists, "struct field AlgID does not exist");
		return AlgID_var;
	}
	ushort Bitlen() {
		assert_cond(Bitlen_exists, "struct field Bitlen does not exist");
		return Bitlen_var;
	}
	ushort Flags() {
		assert_cond(Flags_exists, "struct field Flags does not exist");
		return Flags_var;
	}
	std::string CertData() {
		assert_cond(CertData_exists, "struct field CertData does not exist");
		return CertData_var;
	}
	ushort version() {
		assert_cond(version_exists, "struct field version does not exist");
		return version_var;
	}
	std::string VendorID() {
		assert_cond(VendorID_exists, "struct field VendorID does not exist");
		return VendorID_var;
	}
	byte Strength() {
		assert_cond(Strength_exists, "struct field Strength does not exist");
		return Strength_var;
	}
	short deCompression() {
		assert_cond(deCompression_exists, "struct field deCompression does not exist");
		return deCompression_var;
	}
	std::string efData() {
		assert_cond(efData_exists, "struct field efData does not exist");
		return efData_var;
	}

	/* locals */
	int len;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	EXTRAFIELD& operator () () { return *instances.back(); }
	EXTRAFIELD* operator [] (int index) { return instances[index]; }
	EXTRAFIELD(std::vector<EXTRAFIELD*>& instances) : instances(instances) { instances.push_back(this); }
	~EXTRAFIELD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			EXTRAFIELD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	EXTRAFIELD* generate();
};



class StrongEncryptedHeader_struct {
	std::vector<StrongEncryptedHeader_struct*>& instances;

	ushort IVSize_var;
	std::string IVData_var;
	uint Size_var;
	ushort Format_var;
	ushort AlgID_var;
	ushort BitLen_var;
	ushort Flags_var;
	ushort ErdSize_var;
	std::string ErdData_var;
	uint Reserved_var;
	ushort VSize_var;
	std::string VData_var;
	uint VCRC32_var;

public:
	bool IVSize_exists = false;
	bool IVData_exists = false;
	bool Size_exists = false;
	bool Format_exists = false;
	bool AlgID_exists = false;
	bool BitLen_exists = false;
	bool Flags_exists = false;
	bool ErdSize_exists = false;
	bool ErdData_exists = false;
	bool Reserved_exists = false;
	bool VSize_exists = false;
	bool VData_exists = false;
	bool VCRC32_exists = false;

	ushort IVSize() {
		assert_cond(IVSize_exists, "struct field IVSize does not exist");
		return IVSize_var;
	}
	std::string IVData() {
		assert_cond(IVData_exists, "struct field IVData does not exist");
		return IVData_var;
	}
	uint Size() {
		assert_cond(Size_exists, "struct field Size does not exist");
		return Size_var;
	}
	ushort Format() {
		assert_cond(Format_exists, "struct field Format does not exist");
		return Format_var;
	}
	ushort AlgID() {
		assert_cond(AlgID_exists, "struct field AlgID does not exist");
		return AlgID_var;
	}
	ushort BitLen() {
		assert_cond(BitLen_exists, "struct field BitLen does not exist");
		return BitLen_var;
	}
	ushort Flags() {
		assert_cond(Flags_exists, "struct field Flags does not exist");
		return Flags_var;
	}
	ushort ErdSize() {
		assert_cond(ErdSize_exists, "struct field ErdSize does not exist");
		return ErdSize_var;
	}
	std::string ErdData() {
		assert_cond(ErdData_exists, "struct field ErdData does not exist");
		return ErdData_var;
	}
	uint Reserved() {
		assert_cond(Reserved_exists, "struct field Reserved does not exist");
		return Reserved_var;
	}
	ushort VSize() {
		assert_cond(VSize_exists, "struct field VSize does not exist");
		return VSize_var;
	}
	std::string VData() {
		assert_cond(VData_exists, "struct field VData does not exist");
		return VData_var;
	}
	uint VCRC32() {
		assert_cond(VCRC32_exists, "struct field VCRC32 does not exist");
		return VCRC32_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	StrongEncryptedHeader_struct& operator () () { return *instances.back(); }
	StrongEncryptedHeader_struct* operator [] (int index) { return instances[index]; }
	StrongEncryptedHeader_struct(std::vector<StrongEncryptedHeader_struct*>& instances) : instances(instances) { instances.push_back(this); }
	~StrongEncryptedHeader_struct() {
		if (generated == 2)
			return;
		while (instances.size()) {
			StrongEncryptedHeader_struct* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	StrongEncryptedHeader_struct* generate();
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

	uchar generate(std::vector<uchar> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(uchar), 0, new_known_values);
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
				value.push_back(file_acc.file_integer(sizeof(uchar), 0, known->second));
				_sizeof += sizeof(uchar);
			}
		}
		return value;
	}
};



class ZIPDATADESCR {
	std::vector<ZIPDATADESCR*>& instances;

	uint ddSignature_var;
	uint ddCRC_var;
	uint ddCompressedSize_var;
	uint ddUncompressedSize_var;

public:
	bool ddSignature_exists = false;
	bool ddCRC_exists = false;
	bool ddCompressedSize_exists = false;
	bool ddUncompressedSize_exists = false;

	uint ddSignature() {
		assert_cond(ddSignature_exists, "struct field ddSignature does not exist");
		return ddSignature_var;
	}
	uint ddCRC() {
		assert_cond(ddCRC_exists, "struct field ddCRC does not exist");
		return ddCRC_var;
	}
	uint ddCompressedSize() {
		assert_cond(ddCompressedSize_exists, "struct field ddCompressedSize does not exist");
		return ddCompressedSize_var;
	}
	uint ddUncompressedSize() {
		assert_cond(ddUncompressedSize_exists, "struct field ddUncompressedSize does not exist");
		return ddUncompressedSize_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIPDATADESCR& operator () () { return *instances.back(); }
	ZIPDATADESCR* operator [] (int index) { return instances[index]; }
	ZIPDATADESCR(std::vector<ZIPDATADESCR*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIPDATADESCR() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIPDATADESCR* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIPDATADESCR* generate();
};



class ZIPFILERECORD {
	std::vector<ZIPFILERECORD*>& instances;

	uint frSignature_var;
	VERECORD* frVersion_var;
	ushort frFlags_var;
	short frCompression_var;
	ushort frFileTime_var;
	ushort frFileDate_var;
	uint frCrc_var;
	uint frCompressedSize_var;
	uint frUncompressedSize_var;
	ushort frFileNameLength_var;
	ushort frExtraFieldLength_var;
	std::string frFileName_var;
	EXTRAFIELD* frExtraField_var;
	StrongEncryptedHeader_struct* StrongEncryptedHeader_var;
	std::string frData_var;
	std::string SaltValue_var;
	ushort PassVerification_var;
	std::string AuthenticationCode_var;
	ZIPDATADESCR* dataDescr_var;

public:
	bool frSignature_exists = false;
	bool frVersion_exists = false;
	bool frFlags_exists = false;
	bool frCompression_exists = false;
	bool frFileTime_exists = false;
	bool frFileDate_exists = false;
	bool frCrc_exists = false;
	bool frCompressedSize_exists = false;
	bool frUncompressedSize_exists = false;
	bool frFileNameLength_exists = false;
	bool frExtraFieldLength_exists = false;
	bool frFileName_exists = false;
	bool frExtraField_exists = false;
	bool StrongEncryptedHeader_exists = false;
	bool frData_exists = false;
	bool SaltValue_exists = false;
	bool PassVerification_exists = false;
	bool AuthenticationCode_exists = false;
	bool dataDescr_exists = false;

	uint frSignature() {
		assert_cond(frSignature_exists, "struct field frSignature does not exist");
		return frSignature_var;
	}
	VERECORD& frVersion() {
		assert_cond(frVersion_exists, "struct field frVersion does not exist");
		return *frVersion_var;
	}
	ushort frFlags() {
		assert_cond(frFlags_exists, "struct field frFlags does not exist");
		return frFlags_var;
	}
	short frCompression() {
		assert_cond(frCompression_exists, "struct field frCompression does not exist");
		return frCompression_var;
	}
	ushort frFileTime() {
		assert_cond(frFileTime_exists, "struct field frFileTime does not exist");
		return frFileTime_var;
	}
	ushort frFileDate() {
		assert_cond(frFileDate_exists, "struct field frFileDate does not exist");
		return frFileDate_var;
	}
	uint frCrc() {
		assert_cond(frCrc_exists, "struct field frCrc does not exist");
		return frCrc_var;
	}
	uint frCompressedSize() {
		assert_cond(frCompressedSize_exists, "struct field frCompressedSize does not exist");
		return frCompressedSize_var;
	}
	uint frUncompressedSize() {
		assert_cond(frUncompressedSize_exists, "struct field frUncompressedSize does not exist");
		return frUncompressedSize_var;
	}
	ushort frFileNameLength() {
		assert_cond(frFileNameLength_exists, "struct field frFileNameLength does not exist");
		return frFileNameLength_var;
	}
	ushort frExtraFieldLength() {
		assert_cond(frExtraFieldLength_exists, "struct field frExtraFieldLength does not exist");
		return frExtraFieldLength_var;
	}
	std::string frFileName() {
		assert_cond(frFileName_exists, "struct field frFileName does not exist");
		return frFileName_var;
	}
	EXTRAFIELD& frExtraField() {
		assert_cond(frExtraField_exists, "struct field frExtraField does not exist");
		return *frExtraField_var;
	}
	StrongEncryptedHeader_struct& StrongEncryptedHeader() {
		assert_cond(StrongEncryptedHeader_exists, "struct field StrongEncryptedHeader does not exist");
		return *StrongEncryptedHeader_var;
	}
	std::string frData() {
		assert_cond(frData_exists, "struct field frData does not exist");
		return frData_var;
	}
	std::string SaltValue() {
		assert_cond(SaltValue_exists, "struct field SaltValue does not exist");
		return SaltValue_var;
	}
	ushort PassVerification() {
		assert_cond(PassVerification_exists, "struct field PassVerification does not exist");
		return PassVerification_var;
	}
	std::string AuthenticationCode() {
		assert_cond(AuthenticationCode_exists, "struct field AuthenticationCode does not exist");
		return AuthenticationCode_var;
	}
	ZIPDATADESCR& dataDescr() {
		assert_cond(dataDescr_exists, "struct field dataDescr does not exist");
		return *dataDescr_var;
	}

	/* locals */
	uint offset;
	uint frCrcStart;
	int frExtraFieldLengthStart;
	int len;
	int frExtraFieldStart;
	int frExtraFieldEnd;
	ushort frExtraFieldRealLength;
	int evil_state;
	int lenSalt;
	uint frDataStart;
	int64 posCurrent;
	int64 posNext;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIPFILERECORD& operator () () { return *instances.back(); }
	ZIPFILERECORD* operator [] (int index) { return instances[index]; }
	ZIPFILERECORD(std::vector<ZIPFILERECORD*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIPFILERECORD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIPFILERECORD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIPFILERECORD* generate();
};


FILEATTRIBUTE FILEATTRIBUTE_generate() {
	return (FILEATTRIBUTE) file_acc.file_integer(sizeof(uint), 0, FILEATTRIBUTE_values);
}

FILEATTRIBUTE FILEATTRIBUTE_generate(std::vector<uint> known_values) {
	return (FILEATTRIBUTE) file_acc.file_integer(sizeof(uint), 0, known_values);
}


class ZIPDIRENTRY {
	std::vector<ZIPDIRENTRY*>& instances;

	uint deSignature_var;
	VERECORD* deVersionMadeBy_var;
	VERECORD* deVersionToExtract_var;
	ushort deFlags_var;
	short deCompression_var;
	ushort deFileTime_var;
	ushort deFileDate_var;
	uint deCrc_var;
	uint deCompressedSize_var;
	uint deUncompressedSize_var;
	ushort deFileNameLength_var;
	ushort deExtraFieldLength_var;
	ushort deFileCommentLength_var;
	ushort deDiskNumberStart_var;
	ushort deInternalAttributes_var;
	uint deExternalAttributes_var;
	uint deHeaderOffset_var;
	std::string deFileName_var;
	EXTRAFIELD* deExtraField_var;
	std::string deFileComment_var;

public:
	bool deSignature_exists = false;
	bool deVersionMadeBy_exists = false;
	bool deVersionToExtract_exists = false;
	bool deFlags_exists = false;
	bool deCompression_exists = false;
	bool deFileTime_exists = false;
	bool deFileDate_exists = false;
	bool deCrc_exists = false;
	bool deCompressedSize_exists = false;
	bool deUncompressedSize_exists = false;
	bool deFileNameLength_exists = false;
	bool deExtraFieldLength_exists = false;
	bool deFileCommentLength_exists = false;
	bool deDiskNumberStart_exists = false;
	bool deInternalAttributes_exists = false;
	bool deExternalAttributes_exists = false;
	bool deHeaderOffset_exists = false;
	bool deFileName_exists = false;
	bool deExtraField_exists = false;
	bool deFileComment_exists = false;

	uint deSignature() {
		assert_cond(deSignature_exists, "struct field deSignature does not exist");
		return deSignature_var;
	}
	VERECORD& deVersionMadeBy() {
		assert_cond(deVersionMadeBy_exists, "struct field deVersionMadeBy does not exist");
		return *deVersionMadeBy_var;
	}
	VERECORD& deVersionToExtract() {
		assert_cond(deVersionToExtract_exists, "struct field deVersionToExtract does not exist");
		return *deVersionToExtract_var;
	}
	ushort deFlags() {
		assert_cond(deFlags_exists, "struct field deFlags does not exist");
		return deFlags_var;
	}
	short deCompression() {
		assert_cond(deCompression_exists, "struct field deCompression does not exist");
		return deCompression_var;
	}
	ushort deFileTime() {
		assert_cond(deFileTime_exists, "struct field deFileTime does not exist");
		return deFileTime_var;
	}
	ushort deFileDate() {
		assert_cond(deFileDate_exists, "struct field deFileDate does not exist");
		return deFileDate_var;
	}
	uint deCrc() {
		assert_cond(deCrc_exists, "struct field deCrc does not exist");
		return deCrc_var;
	}
	uint deCompressedSize() {
		assert_cond(deCompressedSize_exists, "struct field deCompressedSize does not exist");
		return deCompressedSize_var;
	}
	uint deUncompressedSize() {
		assert_cond(deUncompressedSize_exists, "struct field deUncompressedSize does not exist");
		return deUncompressedSize_var;
	}
	ushort deFileNameLength() {
		assert_cond(deFileNameLength_exists, "struct field deFileNameLength does not exist");
		return deFileNameLength_var;
	}
	ushort deExtraFieldLength() {
		assert_cond(deExtraFieldLength_exists, "struct field deExtraFieldLength does not exist");
		return deExtraFieldLength_var;
	}
	ushort deFileCommentLength() {
		assert_cond(deFileCommentLength_exists, "struct field deFileCommentLength does not exist");
		return deFileCommentLength_var;
	}
	ushort deDiskNumberStart() {
		assert_cond(deDiskNumberStart_exists, "struct field deDiskNumberStart does not exist");
		return deDiskNumberStart_var;
	}
	ushort deInternalAttributes() {
		assert_cond(deInternalAttributes_exists, "struct field deInternalAttributes does not exist");
		return deInternalAttributes_var;
	}
	uint deExternalAttributes() {
		assert_cond(deExternalAttributes_exists, "struct field deExternalAttributes does not exist");
		return deExternalAttributes_var;
	}
	uint deHeaderOffset() {
		assert_cond(deHeaderOffset_exists, "struct field deHeaderOffset does not exist");
		return deHeaderOffset_var;
	}
	std::string deFileName() {
		assert_cond(deFileName_exists, "struct field deFileName does not exist");
		return deFileName_var;
	}
	EXTRAFIELD& deExtraField() {
		assert_cond(deExtraField_exists, "struct field deExtraField does not exist");
		return *deExtraField_var;
	}
	std::string deFileComment() {
		assert_cond(deFileComment_exists, "struct field deFileComment does not exist");
		return deFileComment_var;
	}

	/* locals */
	int evil_state;
	int deExtraFieldLengthStart;
	int len;
	int deExtraFieldStart;
	int deExtraFieldEnd;
	ushort deExtraFieldRealLength;

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIPDIRENTRY& operator () () { return *instances.back(); }
	ZIPDIRENTRY* operator [] (int index) { return instances[index]; }
	ZIPDIRENTRY(std::vector<ZIPDIRENTRY*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIPDIRENTRY() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIPDIRENTRY* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIPDIRENTRY* generate();
};



class ZIPDIGITALSIG {
	std::vector<ZIPDIGITALSIG*>& instances;

	uint dsSignature_var;
	ushort dsDataLength_var;
	std::string dsData_var;

public:
	bool dsSignature_exists = false;
	bool dsDataLength_exists = false;
	bool dsData_exists = false;

	uint dsSignature() {
		assert_cond(dsSignature_exists, "struct field dsSignature does not exist");
		return dsSignature_var;
	}
	ushort dsDataLength() {
		assert_cond(dsDataLength_exists, "struct field dsDataLength does not exist");
		return dsDataLength_var;
	}
	std::string dsData() {
		assert_cond(dsData_exists, "struct field dsData does not exist");
		return dsData_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIPDIGITALSIG& operator () () { return *instances.back(); }
	ZIPDIGITALSIG* operator [] (int index) { return instances[index]; }
	ZIPDIGITALSIG(std::vector<ZIPDIGITALSIG*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIPDIGITALSIG() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIPDIGITALSIG* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIPDIGITALSIG* generate();
};



class int64_class {
	int small;
	std::vector<int64> known_values;
	int64 value;
public:
	int64 _startof = 0;
	std::size_t _sizeof = sizeof(int64);
	int64 operator () () { return value; }
	int64_class(int small, std::vector<int64> known_values = {}) : small(small), known_values(known_values) {}

	int64 generate() {
		_startof = FTell();
		if (known_values.empty()) {
			value = file_acc.file_integer(sizeof(int64), 0, small);
		} else {
			value = file_acc.file_integer(sizeof(int64), 0, known_values);
		}
		return value;
	}

	int64 generate(std::vector<int64> new_known_values) {
		_startof = FTell();
		for (auto& known : known_values) {
			new_known_values.push_back(known);
		}
		value = file_acc.file_integer(sizeof(int64), 0, new_known_values);
		return value;
	}
};



class ZIP64ENDLOCATORRECORD {
	std::vector<ZIP64ENDLOCATORRECORD*>& instances;

	uint elr64Signature_var;
	int64 elr64DirectoryRecordSize_var;
	VERECORD* elr64VersionMadeBy_var;
	VERECORD* elr64VersionToExtract_var;
	uint el64DiskNumber_var;
	uint el64StartDiskNumber_var;
	int64 el64EntriesOnDisk_var;
	int64 el64EntriesInDirectory_var;
	int64 el64DirectorySize_var;
	int64 el64DirectoryOffset_var;
	std::string DataSect_var;

public:
	bool elr64Signature_exists = false;
	bool elr64DirectoryRecordSize_exists = false;
	bool elr64VersionMadeBy_exists = false;
	bool elr64VersionToExtract_exists = false;
	bool el64DiskNumber_exists = false;
	bool el64StartDiskNumber_exists = false;
	bool el64EntriesOnDisk_exists = false;
	bool el64EntriesInDirectory_exists = false;
	bool el64DirectorySize_exists = false;
	bool el64DirectoryOffset_exists = false;
	bool DataSect_exists = false;

	uint elr64Signature() {
		assert_cond(elr64Signature_exists, "struct field elr64Signature does not exist");
		return elr64Signature_var;
	}
	int64 elr64DirectoryRecordSize() {
		assert_cond(elr64DirectoryRecordSize_exists, "struct field elr64DirectoryRecordSize does not exist");
		return elr64DirectoryRecordSize_var;
	}
	VERECORD& elr64VersionMadeBy() {
		assert_cond(elr64VersionMadeBy_exists, "struct field elr64VersionMadeBy does not exist");
		return *elr64VersionMadeBy_var;
	}
	VERECORD& elr64VersionToExtract() {
		assert_cond(elr64VersionToExtract_exists, "struct field elr64VersionToExtract does not exist");
		return *elr64VersionToExtract_var;
	}
	uint el64DiskNumber() {
		assert_cond(el64DiskNumber_exists, "struct field el64DiskNumber does not exist");
		return el64DiskNumber_var;
	}
	uint el64StartDiskNumber() {
		assert_cond(el64StartDiskNumber_exists, "struct field el64StartDiskNumber does not exist");
		return el64StartDiskNumber_var;
	}
	int64 el64EntriesOnDisk() {
		assert_cond(el64EntriesOnDisk_exists, "struct field el64EntriesOnDisk does not exist");
		return el64EntriesOnDisk_var;
	}
	int64 el64EntriesInDirectory() {
		assert_cond(el64EntriesInDirectory_exists, "struct field el64EntriesInDirectory does not exist");
		return el64EntriesInDirectory_var;
	}
	int64 el64DirectorySize() {
		assert_cond(el64DirectorySize_exists, "struct field el64DirectorySize does not exist");
		return el64DirectorySize_var;
	}
	int64 el64DirectoryOffset() {
		assert_cond(el64DirectoryOffset_exists, "struct field el64DirectoryOffset does not exist");
		return el64DirectoryOffset_var;
	}
	std::string DataSect() {
		assert_cond(DataSect_exists, "struct field DataSect does not exist");
		return DataSect_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIP64ENDLOCATORRECORD& operator () () { return *instances.back(); }
	ZIP64ENDLOCATORRECORD* operator [] (int index) { return instances[index]; }
	ZIP64ENDLOCATORRECORD(std::vector<ZIP64ENDLOCATORRECORD*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIP64ENDLOCATORRECORD() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIP64ENDLOCATORRECORD* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIP64ENDLOCATORRECORD* generate();
};



class ZIP64ENDLOCATOR {
	std::vector<ZIP64ENDLOCATOR*>& instances;

	uint elSignature_var;
	uint elStartDiskNumber_var;
	int64 elDirectoryOffset_var;
	uint elEntriesInDirectory_var;

public:
	bool elSignature_exists = false;
	bool elStartDiskNumber_exists = false;
	bool elDirectoryOffset_exists = false;
	bool elEntriesInDirectory_exists = false;

	uint elSignature() {
		assert_cond(elSignature_exists, "struct field elSignature does not exist");
		return elSignature_var;
	}
	uint elStartDiskNumber() {
		assert_cond(elStartDiskNumber_exists, "struct field elStartDiskNumber does not exist");
		return elStartDiskNumber_var;
	}
	int64 elDirectoryOffset() {
		assert_cond(elDirectoryOffset_exists, "struct field elDirectoryOffset does not exist");
		return elDirectoryOffset_var;
	}
	uint elEntriesInDirectory() {
		assert_cond(elEntriesInDirectory_exists, "struct field elEntriesInDirectory does not exist");
		return elEntriesInDirectory_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIP64ENDLOCATOR& operator () () { return *instances.back(); }
	ZIP64ENDLOCATOR* operator [] (int index) { return instances[index]; }
	ZIP64ENDLOCATOR(std::vector<ZIP64ENDLOCATOR*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIP64ENDLOCATOR() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIP64ENDLOCATOR* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIP64ENDLOCATOR* generate();
};



class ZIPENDLOCATOR {
	std::vector<ZIPENDLOCATOR*>& instances;

	uint elSignature_var;
	ushort elDiskNumber_var;
	ushort elStartDiskNumber_var;
	ushort elEntriesOnDisk_var;
	ushort elEntriesInDirectory_var;
	uint elDirectorySize_var;
	uint elDirectoryOffset_var;
	ushort elCommentLength_var;
	std::string elComment_var;

public:
	bool elSignature_exists = false;
	bool elDiskNumber_exists = false;
	bool elStartDiskNumber_exists = false;
	bool elEntriesOnDisk_exists = false;
	bool elEntriesInDirectory_exists = false;
	bool elDirectorySize_exists = false;
	bool elDirectoryOffset_exists = false;
	bool elCommentLength_exists = false;
	bool elComment_exists = false;

	uint elSignature() {
		assert_cond(elSignature_exists, "struct field elSignature does not exist");
		return elSignature_var;
	}
	ushort elDiskNumber() {
		assert_cond(elDiskNumber_exists, "struct field elDiskNumber does not exist");
		return elDiskNumber_var;
	}
	ushort elStartDiskNumber() {
		assert_cond(elStartDiskNumber_exists, "struct field elStartDiskNumber does not exist");
		return elStartDiskNumber_var;
	}
	ushort elEntriesOnDisk() {
		assert_cond(elEntriesOnDisk_exists, "struct field elEntriesOnDisk does not exist");
		return elEntriesOnDisk_var;
	}
	ushort elEntriesInDirectory() {
		assert_cond(elEntriesInDirectory_exists, "struct field elEntriesInDirectory does not exist");
		return elEntriesInDirectory_var;
	}
	uint elDirectorySize() {
		assert_cond(elDirectorySize_exists, "struct field elDirectorySize does not exist");
		return elDirectorySize_var;
	}
	uint elDirectoryOffset() {
		assert_cond(elDirectoryOffset_exists, "struct field elDirectoryOffset does not exist");
		return elDirectoryOffset_var;
	}
	ushort elCommentLength() {
		assert_cond(elCommentLength_exists, "struct field elCommentLength does not exist");
		return elCommentLength_var;
	}
	std::string elComment() {
		assert_cond(elComment_exists, "struct field elComment does not exist");
		return elComment_var;
	}

	unsigned char generated = 0;
	int64 _startof = 0;
	std::size_t _sizeof = 0;
	ZIPENDLOCATOR& operator () () { return *instances.back(); }
	ZIPENDLOCATOR* operator [] (int index) { return instances[index]; }
	ZIPENDLOCATOR(std::vector<ZIPENDLOCATOR*>& instances) : instances(instances) { instances.push_back(this); }
	~ZIPENDLOCATOR() {
		if (generated == 2)
			return;
		while (instances.size()) {
			ZIPENDLOCATOR* instance = instances.back();
			instances.pop_back();
			if (instance->generated == 2)
				delete instance;
		}
	}
	ZIPENDLOCATOR* generate();
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


std::vector<VERECORD*> VERECORD_frVersion_instances;
std::vector<FILETIME*> FILETIME_Mtime_instances;
std::vector<FILETIME*> FILETIME_Atime_instances;
std::vector<FILETIME*> FILETIME_Ctime_instances;
std::vector<EXTRAFIELD*> EXTRAFIELD_frExtraField_instances;
std::vector<StrongEncryptedHeader_struct*> StrongEncryptedHeader_struct_StrongEncryptedHeader_instances;
std::vector<ZIPDATADESCR*> ZIPDATADESCR_dataDescr_instances;
std::vector<ZIPFILERECORD*> ZIPFILERECORD_record_instances;
std::vector<VERECORD*> VERECORD_deVersionMadeBy_instances;
std::vector<VERECORD*> VERECORD_deVersionToExtract_instances;
std::vector<EXTRAFIELD*> EXTRAFIELD_deExtraField_instances;
std::vector<ZIPDIRENTRY*> ZIPDIRENTRY_dirEntry_instances;
std::vector<ZIPDIGITALSIG*> ZIPDIGITALSIG_digitalSig_instances;
std::vector<VERECORD*> VERECORD_elr64VersionMadeBy_instances;
std::vector<VERECORD*> VERECORD_elr64VersionToExtract_instances;
std::vector<ZIP64ENDLOCATORRECORD*> ZIP64ENDLOCATORRECORD_end64Locator_instances;
std::vector<ZIP64ENDLOCATOR*> ZIP64ENDLOCATOR_end64Locator__instances;
std::vector<ZIPENDLOCATOR*> ZIPENDLOCATOR_endLocator_instances;


class globals_class {
public:
	/*local*/ std::string current_tag;
	/*local*/ uint frIndex;
	/*local*/ uint deIndex;
	/*local*/ uint dirOffset;
	/*local*/ uint dirSize;
	/*local*/ std::vector<std::string> preferred_tags;
	/*local*/ std::vector<std::string> possible_tags;
	/*local*/ int evil_state;
	VERSIONTYPE_class Version;
	VERECORD frVersion;
	ushort_class frFileTime;
	ushort_class frFileDate;
	uint_class frCrc;
	uint_class frCompressedSize;
	uint_class frUncompressedSize;
	ushort_class frFileNameLength;
	ushort_class frExtraFieldLength;
	char_class frFileName_element;
	char_array_class frFileName;
	ushort_class efDataSize;
	uint64_class efOriginalSize;
	uint64_class efCompressedSize;
	byte_class efVersion;
	uint_class efNameCRC32;
	char_class efUnicodeName_element;
	char_array_class efUnicodeName;
	int_class Reserved;
	ushort_class Tag;
	ushort_class Size;
	DWORD_class dwLowDateTime;
	DWORD_class dwHighDateTime;
	FILETIME Mtime;
	FILETIME Atime;
	FILETIME Ctime;
	byte_class Data_element;
	byte_array_class Data;
	ushort_class Format;
	ushort_class Bitlen;
	byte_class CertData_element;
	byte_array_class CertData;
	ushort_class version;
	char_class VendorID_element;
	char_array_class VendorID;
	char_class efData_element;
	char_array_class efData;
	EXTRAFIELD frExtraField;
	ushort_class IVSize;
	byte_class IVData_element;
	byte_array_class IVData;
	uint_class Size_;
	ushort_class BitLen;
	ushort_class Flags;
	ushort_class ErdSize;
	byte_class ErdData_element;
	byte_array_class ErdData;
	uint_class Reserved_;
	ushort_class VSize;
	byte_class VData_element;
	byte_array_class VData;
	uint_class VCRC32;
	StrongEncryptedHeader_struct StrongEncryptedHeader;
	char_class frData_element;
	char_array_class frData;
	uchar_class SaltValue_element;
	uchar_array_class SaltValue;
	ushort_class PassVerification;
	uchar_class frData__element;
	uchar_array_class frData_;
	uchar_class AuthenticationCode_element;
	uchar_array_class AuthenticationCode;
	uint_class ddCRC;
	uint_class ddCompressedSize;
	uint_class ddUncompressedSize;
	ZIPDATADESCR dataDescr;
	ZIPFILERECORD record;
	VERECORD deVersionMadeBy;
	VERECORD deVersionToExtract;
	ushort_class deFileTime;
	ushort_class deFileDate;
	uint_class deCrc;
	uint_class deCompressedSize;
	uint_class deUncompressedSize;
	ushort_class deFileNameLength;
	ushort_class deExtraFieldLength;
	ushort_class deFileCommentLength;
	ushort_class deDiskNumberStart;
	ushort_class deInternalAttributes;
	uint_class deHeaderOffset;
	char_class deFileName_element;
	char_array_class deFileName;
	EXTRAFIELD deExtraField;
	uchar_class deFileComment_element;
	uchar_array_class deFileComment;
	ZIPDIRENTRY dirEntry;
	ushort_class dsDataLength;
	uchar_class dsData_element;
	uchar_array_class dsData;
	ZIPDIGITALSIG digitalSig;
	int64_class elr64DirectoryRecordSize;
	VERECORD elr64VersionMadeBy;
	VERECORD elr64VersionToExtract;
	uint_class el64DiskNumber;
	uint_class el64StartDiskNumber;
	int64_class el64EntriesOnDisk;
	int64_class el64EntriesInDirectory;
	int64_class el64DirectorySize;
	int64_class el64DirectoryOffset;
	char_class DataSect_element;
	char_array_class DataSect;
	ZIP64ENDLOCATORRECORD end64Locator;
	uint_class elStartDiskNumber;
	int64_class elDirectoryOffset;
	uint_class elEntriesInDirectory;
	ZIP64ENDLOCATOR end64Locator_;
	ushort_class elDiskNumber;
	ushort_class elStartDiskNumber_;
	ushort_class elEntriesOnDisk;
	ushort_class elEntriesInDirectory_;
	uint_class elDirectorySize;
	uint_class elDirectoryOffset_;
	ushort_class elCommentLength;
	char_class elComment_element;
	char_array_class elComment;
	ZIPENDLOCATOR endLocator;


	globals_class() :
		current_tag(4, 0),
		Version(1),
		frVersion(VERECORD_frVersion_instances),
		frFileTime(1),
		frFileDate(1),
		frCrc(1),
		frCompressedSize(2),
		frUncompressedSize(1),
		frFileNameLength(2),
		frExtraFieldLength(2),
		frFileName_element(false),
		frFileName(frFileName_element),
		efDataSize(2),
		efOriginalSize(1),
		efCompressedSize(1),
		efVersion(1),
		efNameCRC32(1),
		efUnicodeName_element(false),
		efUnicodeName(efUnicodeName_element),
		Reserved(1),
		Tag(1, { 0x001 }),
		Size(2),
		dwLowDateTime(1),
		dwHighDateTime(1),
		Mtime(FILETIME_Mtime_instances),
		Atime(FILETIME_Atime_instances),
		Ctime(FILETIME_Ctime_instances),
		Data_element(false),
		Data(Data_element),
		Format(1),
		Bitlen(1),
		CertData_element(false),
		CertData(CertData_element),
		version(1),
		VendorID_element(false),
		VendorID(VendorID_element),
		efData_element(false),
		efData(efData_element),
		frExtraField(EXTRAFIELD_frExtraField_instances),
		IVSize(2),
		IVData_element(false),
		IVData(IVData_element),
		Size_(2),
		BitLen(1),
		Flags(1),
		ErdSize(2),
		ErdData_element(false),
		ErdData(ErdData_element),
		Reserved_(1),
		VSize(2),
		VData_element(false),
		VData(VData_element),
		VCRC32(1),
		StrongEncryptedHeader(StrongEncryptedHeader_struct_StrongEncryptedHeader_instances),
		frData_element(false),
		frData(frData_element),
		SaltValue_element(false),
		SaltValue(SaltValue_element),
		PassVerification(1),
		frData__element(false),
		frData_(frData__element),
		AuthenticationCode_element(false),
		AuthenticationCode(AuthenticationCode_element),
		ddCRC(1),
		ddCompressedSize(1),
		ddUncompressedSize(1),
		dataDescr(ZIPDATADESCR_dataDescr_instances),
		record(ZIPFILERECORD_record_instances),
		deVersionMadeBy(VERECORD_deVersionMadeBy_instances),
		deVersionToExtract(VERECORD_deVersionToExtract_instances),
		deFileTime(1),
		deFileDate(1),
		deCrc(1),
		deCompressedSize(1),
		deUncompressedSize(1),
		deFileNameLength(1),
		deExtraFieldLength(2),
		deFileCommentLength(2),
		deDiskNumberStart(1),
		deInternalAttributes(1),
		deHeaderOffset(1),
		deFileName_element(false),
		deFileName(deFileName_element),
		deExtraField(EXTRAFIELD_deExtraField_instances),
		deFileComment_element(false),
		deFileComment(deFileComment_element),
		dirEntry(ZIPDIRENTRY_dirEntry_instances),
		dsDataLength(2),
		dsData_element(false),
		dsData(dsData_element),
		digitalSig(ZIPDIGITALSIG_digitalSig_instances),
		elr64DirectoryRecordSize(2),
		elr64VersionMadeBy(VERECORD_elr64VersionMadeBy_instances),
		elr64VersionToExtract(VERECORD_elr64VersionToExtract_instances),
		el64DiskNumber(1),
		el64StartDiskNumber(1),
		el64EntriesOnDisk(1),
		el64EntriesInDirectory(1),
		el64DirectorySize(1),
		el64DirectoryOffset(1),
		DataSect_element(false),
		DataSect(DataSect_element),
		end64Locator(ZIP64ENDLOCATORRECORD_end64Locator_instances),
		elStartDiskNumber(1),
		elDirectoryOffset(1),
		elEntriesInDirectory(1),
		end64Locator_(ZIP64ENDLOCATOR_end64Locator__instances),
		elDiskNumber(1),
		elStartDiskNumber_(1),
		elEntriesOnDisk(1),
		elEntriesInDirectory_(1),
		elDirectorySize(1),
		elDirectoryOffset_(1),
		elCommentLength(2),
		elComment_element(false),
		elComment(elComment_element),
		endLocator(ZIPENDLOCATOR_endLocator_instances)
	{}
};

globals_class* g;


VERECORD* VERECORD::generate() {
	if (generated == 1) {
		VERECORD* new_instance = new VERECORD(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(Version, ::g->Version.generate());
	GENERATE_VAR(HostOS, HOSTOSTYPE_generate());

	_sizeof = FTell() - _startof;
	return this;
}


FILETIME* FILETIME::generate() {
	if (generated == 1) {
		FILETIME* new_instance = new FILETIME(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(dwLowDateTime, ::g->dwLowDateTime.generate());
	GENERATE_VAR(dwHighDateTime, ::g->dwHighDateTime.generate());

	_sizeof = FTell() - _startof;
	return this;
}


EXTRAFIELD* EXTRAFIELD::generate() {
	if (generated == 1) {
		EXTRAFIELD* new_instance = new EXTRAFIELD(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(efHeaderID, HEADERFLAG_generate());
	GENERATE_VAR(efDataSize, ::g->efDataSize.generate());
	switch (efHeaderID()) {
	case EH_Zip64:
		GENERATE_VAR(efOriginalSize, ::g->efOriginalSize.generate());
		GENERATE_VAR(efCompressedSize, ::g->efCompressedSize.generate());
		break;
	case EH_InfoZIPUnicodePath:
		GENERATE_VAR(efVersion, ::g->efVersion.generate());
		GENERATE_VAR(efNameCRC32, ::g->efNameCRC32.generate());
		if ((efDataSize() > 0)) {
			GENERATE_VAR(efUnicodeName, ::g->efUnicodeName.generate((efDataSize() - 5)));
		};
		break;
	case EH_NTFS:
		GENERATE_VAR(Reserved, ::g->Reserved.generate());
		len = (efDataSize() - 4);
		while ((len > 0)) {
			GENERATE_VAR(Tag, ::g->Tag.generate());
			GENERATE_VAR(Size, ::g->Size.generate());
			if ((Tag() == 0x001)) {
				GENERATE_VAR(Mtime, ::g->Mtime.generate());
				GENERATE_VAR(Atime, ::g->Atime.generate());
				GENERATE_VAR(Ctime, ::g->Ctime.generate());
			} else {
				GENERATE_VAR(Data, ::g->Data.generate(Size()));
			};
			len -= (Size() + 4);
		};
		break;
	case EH_StrongEncryption:
		GENERATE_VAR(Format, ::g->Format.generate());
		GENERATE_VAR(AlgID, ALGFLAG_generate());
		GENERATE_VAR(Bitlen, ::g->Bitlen.generate());
		GENERATE_VAR(Flags, PRCFLAG_generate());
		if ((efDataSize() > 8)) {
			GENERATE_VAR(CertData, ::g->CertData.generate((efDataSize() - 8)));
		};
		break;
	case EH_WzAES:
		GENERATE_VAR(version, ::g->version.generate());
		GENERATE_VAR(VendorID, ::g->VendorID.generate(2));
		GENERATE_VAR(Strength, AESMODE_generate());
		GENERATE_VAR(deCompression, COMPTYPE_generate());
		break;
	default:
		if ((efDataSize() > 0)) {
			GENERATE_VAR(efData, ::g->efData.generate(efDataSize()));
		};
		break;
	};

	_sizeof = FTell() - _startof;
	return this;
}


StrongEncryptedHeader_struct* StrongEncryptedHeader_struct::generate() {
	if (generated == 1) {
		StrongEncryptedHeader_struct* new_instance = new StrongEncryptedHeader_struct(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(IVSize, ::g->IVSize.generate());
	GENERATE_VAR(IVData, ::g->IVData.generate(IVSize()));
	GENERATE_VAR(Size, ::g->Size_.generate());
	GENERATE_VAR(Format, ::g->Format.generate());
	GENERATE_VAR(AlgID, ALGFLAG_generate());
	GENERATE_VAR(BitLen, ::g->BitLen.generate());
	GENERATE_VAR(Flags, ::g->Flags.generate());
	GENERATE_VAR(ErdSize, ::g->ErdSize.generate());
	GENERATE_VAR(ErdData, ::g->ErdData.generate(ErdSize()));
	GENERATE_VAR(Reserved, ::g->Reserved_.generate());
	GENERATE_VAR(VSize, ::g->VSize.generate());
	GENERATE_VAR(VData, ::g->VData.generate((VSize() - 4)));
	GENERATE_VAR(VCRC32, ::g->VCRC32.generate());

	_sizeof = FTell() - _startof;
	return this;
}


ZIPDATADESCR* ZIPDATADESCR::generate() {
	if (generated == 1) {
		ZIPDATADESCR* new_instance = new ZIPDATADESCR(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(ddSignature, SignatureTYPE_generate());
	GENERATE_VAR(ddCRC, ::g->ddCRC.generate());
	GENERATE_VAR(ddCompressedSize, ::g->ddCompressedSize.generate());
	GENERATE_VAR(ddUncompressedSize, ::g->ddUncompressedSize.generate());

	_sizeof = FTell() - _startof;
	return this;
}


ZIPFILERECORD* ZIPFILERECORD::generate() {
	if (generated == 1) {
		ZIPFILERECORD* new_instance = new ZIPFILERECORD(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	offset = FTell();
	GENERATE_VAR(frSignature, SignatureTYPE_generate());
	GENERATE_VAR(frVersion, ::g->frVersion.generate());
	GENERATE_VAR(frFlags, FLAGTYPE_generate({ 0 }));
	GENERATE_VAR(frCompression, COMPTYPE_generate({ COMP_STORED }));
	GENERATE_VAR(frFileTime, ::g->frFileTime.generate());
	GENERATE_VAR(frFileDate, ::g->frFileDate.generate());
	frCrcStart = FTell();
	GENERATE_VAR(frCrc, ::g->frCrc.generate());
	GENERATE_VAR(frCompressedSize, ::g->frCompressedSize.generate());
	GENERATE_VAR(frUncompressedSize, ::g->frUncompressedSize.generate({ frCompressedSize() }));
	GENERATE_VAR(frFileNameLength, ::g->frFileNameLength.generate());
	frExtraFieldLengthStart = FTell();
	GENERATE_VAR(frExtraFieldLength, ::g->frExtraFieldLength.generate());
	if ((frFileNameLength() > 0)) {
		GENERATE_VAR(frFileName, ::g->frFileName.generate(frFileNameLength()));
	};
	len = frExtraFieldLength();
	frExtraFieldStart = FTell();
	while ((len > 0)) {
		GENERATE_VAR(frExtraField, ::g->frExtraField.generate());
		len -= (frExtraField().efDataSize() + 4);
	};
	frExtraFieldEnd = FTell();
	frExtraFieldRealLength = (frExtraFieldEnd - frExtraFieldStart);
	FSeek(frExtraFieldLengthStart);
	evil_state = SetEvilBit(false);
	GENERATE_VAR(frExtraFieldLength, ::g->frExtraFieldLength.generate({ frExtraFieldRealLength }));
	SetEvilBit(evil_state);
	FSeek(frExtraFieldEnd);
	SetBackColor(cNone);
	if (((frFlags() & FLAG_Encrypted) && (frFlags() & FLAG_StrongEncrypted))) {
		GENERATE_VAR(StrongEncryptedHeader, ::g->StrongEncryptedHeader.generate());
		GENERATE_VAR(frData, ::g->frData.generate((((frCompressedSize() - StrongEncryptedHeader().IVSize()) - StrongEncryptedHeader().Size()) - 6)));
	} else {
	if (((frFlags() & FLAG_Encrypted) && (frCompression() == COMP_WzAES))) {
		lenSalt = 0;
		if ((frExtraField().efHeaderID() == EH_WzAES)) {
			switch (frExtraField().Strength()) {
			case AES128:
				lenSalt = 8;
				break;
			case AES192:
				lenSalt = 12;
				break;
			case AES256:
				lenSalt = 16;
				break;
			};
		};
		GENERATE_VAR(SaltValue, ::g->SaltValue.generate(lenSalt));
		GENERATE_VAR(PassVerification, ::g->PassVerification.generate());
		GENERATE_VAR(frData, ::g->frData_.generate(((frCompressedSize() - 12) - lenSalt)));
		GENERATE_VAR(AuthenticationCode, ::g->AuthenticationCode.generate(10));
	} else {
	if (((frCompressedSize() > 0) && (frCompressedSize() < 0xFFFFFFFF))) {
		frDataStart = FTell();
		GENERATE_VAR(frData, ::g->frData_.generate(frCompressedSize()));
		FSeek(frCrcStart);
		GENERATE_VAR(frCrc, ::g->frCrc.generate({ Checksum(CHECKSUM_CRC32, frDataStart, frCompressedSize()) }));
		FSeek((frDataStart + frCompressedSize()));
	} else {
	if (((frCompressedSize() == 0) && (frFlags() & FLAG_DescriptorUsedMask))) {
		posCurrent = FTell();
		posNext = FindFirst(S_ZIPDATADESCR, true, false, false, 0.0, 1, posCurrent);
		if ((posNext >= posCurrent)) {
			GENERATE_VAR(frData, ::g->frData_.generate((posNext - posCurrent)));
			SetBackColor(cLtGreen);
			GENERATE_VAR(dataDescr, ::g->dataDescr.generate());
		};
	};
	};
	};
	};

	_sizeof = FTell() - _startof;
	return this;
}


ZIPDIRENTRY* ZIPDIRENTRY::generate() {
	if (generated == 1) {
		ZIPDIRENTRY* new_instance = new ZIPDIRENTRY(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	Printf("Dir entry referencing record %d\n", ::g->deIndex);
	Printf("Record %d comp type %d\n", ::g->deIndex, ::g->record()[::g->deIndex]->frCompression());
	GENERATE_VAR(deSignature, SignatureTYPE_generate());
	GENERATE_VAR(deVersionMadeBy, ::g->deVersionMadeBy.generate());
	GENERATE_VAR(deVersionToExtract, ::g->deVersionToExtract.generate());
	GENERATE_VAR(deFlags, FLAGTYPE_generate());
	GENERATE_VAR(deCompression, COMPTYPE_generate({ ::g->record()[::g->deIndex]->frCompression() }));
	GENERATE_VAR(deFileTime, ::g->deFileTime.generate());
	GENERATE_VAR(deFileDate, ::g->deFileDate.generate());
	GENERATE_VAR(deCrc, ::g->deCrc.generate({ ::g->record()[::g->deIndex]->frCrc() }));
	if ((::g->record()[::g->deIndex]->frCompressedSize() > 0)) {
		GENERATE_VAR(deCompressedSize, ::g->deCompressedSize.generate({ ::g->record()[::g->deIndex]->frCompressedSize() }));
	} else {
		GENERATE_VAR(deCompressedSize, ::g->deCompressedSize.generate());
	};
	GENERATE_VAR(deUncompressedSize, ::g->deUncompressedSize.generate({ ::g->record()[::g->deIndex]->frUncompressedSize() }));
	evil_state = SetEvilBit(false);
	GENERATE_VAR(deFileNameLength, ::g->deFileNameLength.generate({ ::g->record()[::g->deIndex]->frFileNameLength() }));
	SetEvilBit(evil_state);
	deExtraFieldLengthStart = FTell();
	GENERATE_VAR(deExtraFieldLength, ::g->deExtraFieldLength.generate());
	GENERATE_VAR(deFileCommentLength, ::g->deFileCommentLength.generate());
	GENERATE_VAR(deDiskNumberStart, ::g->deDiskNumberStart.generate({ 0 }));
	GENERATE_VAR(deInternalAttributes, ::g->deInternalAttributes.generate());
	GENERATE_VAR(deExternalAttributes, FILEATTRIBUTE_generate());
	GENERATE_VAR(deHeaderOffset, ::g->deHeaderOffset.generate({ ::g->record()[::g->deIndex]->offset }));
	if ((deFileNameLength() > 0)) {
		GENERATE_VAR(deFileName, ::g->deFileName.generate(deFileNameLength(), { ::g->record()[::g->deIndex]->frFileName() }));
	};
	len = deExtraFieldLength();
	deExtraFieldStart = FTell();
	while ((len > 0)) {
		GENERATE_VAR(deExtraField, ::g->deExtraField.generate());
		len -= (deExtraField().efDataSize() + 4);
	};
	deExtraFieldEnd = FTell();
	deExtraFieldRealLength = (deExtraFieldEnd - deExtraFieldStart);
	FSeek(deExtraFieldLengthStart);
	evil_state = SetEvilBit(false);
	GENERATE_VAR(deExtraFieldLength, ::g->deExtraFieldLength.generate({ deExtraFieldRealLength }));
	SetEvilBit(evil_state);
	FSeek(deExtraFieldEnd);
	if ((deFileCommentLength() > 0)) {
		GENERATE_VAR(deFileComment, ::g->deFileComment.generate(deFileCommentLength()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


ZIPDIGITALSIG* ZIPDIGITALSIG::generate() {
	if (generated == 1) {
		ZIPDIGITALSIG* new_instance = new ZIPDIGITALSIG(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(dsSignature, SignatureTYPE_generate());
	GENERATE_VAR(dsDataLength, ::g->dsDataLength.generate());
	if ((dsDataLength() > 0)) {
		GENERATE_VAR(dsData, ::g->dsData.generate(dsDataLength()));
	};

	_sizeof = FTell() - _startof;
	return this;
}


ZIP64ENDLOCATORRECORD* ZIP64ENDLOCATORRECORD::generate() {
	if (generated == 1) {
		ZIP64ENDLOCATORRECORD* new_instance = new ZIP64ENDLOCATORRECORD(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(elr64Signature, SignatureTYPE_generate());
	GENERATE_VAR(elr64DirectoryRecordSize, ::g->elr64DirectoryRecordSize.generate());
	if ((elr64DirectoryRecordSize() > 1)) {
		GENERATE_VAR(elr64VersionMadeBy, ::g->elr64VersionMadeBy.generate());
	};
	if ((elr64DirectoryRecordSize() > 2)) {
		GENERATE_VAR(elr64VersionToExtract, ::g->elr64VersionToExtract.generate());
	};
	if ((elr64DirectoryRecordSize() > 4)) {
		GENERATE_VAR(el64DiskNumber, ::g->el64DiskNumber.generate());
	};
	if ((elr64DirectoryRecordSize() > 8)) {
		GENERATE_VAR(el64StartDiskNumber, ::g->el64StartDiskNumber.generate());
	};
	if ((elr64DirectoryRecordSize() > 12)) {
		GENERATE_VAR(el64EntriesOnDisk, ::g->el64EntriesOnDisk.generate());
	};
	if ((elr64DirectoryRecordSize() > 20)) {
		GENERATE_VAR(el64EntriesInDirectory, ::g->el64EntriesInDirectory.generate());
	};
	if ((elr64DirectoryRecordSize() > 28)) {
		GENERATE_VAR(el64DirectorySize, ::g->el64DirectorySize.generate());
	};
	if ((elr64DirectoryRecordSize() > 36)) {
		GENERATE_VAR(el64DirectoryOffset, ::g->el64DirectoryOffset.generate());
	};
	if ((elr64DirectoryRecordSize() > 44)) {
		GENERATE_VAR(DataSect, ::g->DataSect.generate((elr64DirectoryRecordSize() - 44)));
	};

	_sizeof = FTell() - _startof;
	return this;
}


ZIP64ENDLOCATOR* ZIP64ENDLOCATOR::generate() {
	if (generated == 1) {
		ZIP64ENDLOCATOR* new_instance = new ZIP64ENDLOCATOR(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(elSignature, SignatureTYPE_generate());
	GENERATE_VAR(elStartDiskNumber, ::g->elStartDiskNumber.generate());
	GENERATE_VAR(elDirectoryOffset, ::g->elDirectoryOffset.generate());
	GENERATE_VAR(elEntriesInDirectory, ::g->elEntriesInDirectory.generate());

	_sizeof = FTell() - _startof;
	return this;
}


ZIPENDLOCATOR* ZIPENDLOCATOR::generate() {
	if (generated == 1) {
		ZIPENDLOCATOR* new_instance = new ZIPENDLOCATOR(instances);
		new_instance->generated = 2;
		return new_instance->generate();
	}
	if (!generated)
		generated = 1;
	_startof = FTell();

	GENERATE_VAR(elSignature, SignatureTYPE_generate());
	GENERATE_VAR(elDiskNumber, ::g->elDiskNumber.generate({ 0 }));
	GENERATE_VAR(elStartDiskNumber, ::g->elStartDiskNumber_.generate({ 0 }));
	GENERATE_VAR(elEntriesOnDisk, ::g->elEntriesOnDisk.generate({ (ushort)::g->frIndex }));
	GENERATE_VAR(elEntriesInDirectory, ::g->elEntriesInDirectory_.generate({ (ushort)::g->frIndex }));
	GENERATE_VAR(elDirectorySize, ::g->elDirectorySize.generate({ ::g->dirSize }));
	GENERATE_VAR(elDirectoryOffset, ::g->elDirectoryOffset_.generate({ ::g->dirOffset }));
	GENERATE_VAR(elCommentLength, ::g->elCommentLength.generate());
	if ((elCommentLength() > 0)) {
		GENERATE_VAR(elComment, ::g->elComment.generate(elCommentLength()));
	};

	_sizeof = FTell() - _startof;
	return this;
}



void generate_file() {
	::g = new globals_class();

	LittleEndian();
	::g->frIndex = 0;
	::g->deIndex = 0;
	::g->dirOffset = 0;
	::g->dirSize = 0;
	::g->preferred_tags = { "PK\x03\x04" };
	::g->possible_tags = { "PK\x03\x04", "PK\x05\x06" };
	::g->evil_state = SetEvilBit(false);
	while (ReadBytes(::g->current_tag, FTell(), 4, ::g->preferred_tags, ::g->possible_tags)) {
		SetEvilBit(::g->evil_state);
		switch (STR2INT(::g->current_tag)) {
		case STR2INT("PK\x03\x04"):
			SetBackColor(cLtGray);
			GENERATE(record, ::g->record.generate());
			Printf("Generated record %d\n", ::g->frIndex);
			::g->frIndex++;
			if (((::g->record().frExtraFieldLength() > 0) && (::g->record().frExtraField().efHeaderID() == EH_Zip64))) {
				FSkip(::g->record().frExtraField().efCompressedSize());
			};
			if ((::g->frIndex > 1)) {
				::g->preferred_tags = { "PK\x01\x02" };
				::g->possible_tags = { "PK\x01\x02", "PK\x03\x04" };
			} else {
				::g->preferred_tags = { "PK\x03\x04" };
				::g->possible_tags = { "PK\x03\x04", "PK\x03\x04" };
			};
			break;
		case STR2INT("PK\x01\x02"):
			if ((::g->deIndex == 0)) {
				::g->dirOffset = FTell();
			};
			SetBackColor(cLtPurple);
			GENERATE(dirEntry, ::g->dirEntry.generate());
			::g->deIndex++;
			if ((::g->deIndex == ::g->frIndex)) {
				::g->dirSize = (FTell() - ::g->dirOffset);
				::g->preferred_tags = { "PK\x05\x06" };
				::g->possible_tags = { "PK\x05\x06" };
			} else {
				::g->preferred_tags = { "PK\x01\x02" };
				::g->possible_tags = { "PK\x01\x02" };
			};
			break;
		case STR2INT("PK\x07\x08"):
			SetBackColor(cLtGreen);
			GENERATE(dataDescr, ::g->dataDescr.generate());
			break;
		case STR2INT("PK\x05\x05"):
			SetBackColor(cLtBlue);
			GENERATE(digitalSig, ::g->digitalSig.generate());
			break;
		case STR2INT("PK\x06\x06"):
			SetBackColor(cYellow);
			GENERATE(end64Locator, ::g->end64Locator.generate());
			::g->preferred_tags = { "PK\x06\x07" };
			::g->possible_tags = { "PK\x06\x07" };
			break;
		case STR2INT("PK\x06\x07"):
			SetBackColor(cDkYellow);
			GENERATE(end64Locator, ::g->end64Locator_.generate());
			::g->preferred_tags = { "PK\x05\x06" };
			::g->possible_tags = { "PK\x05\x06" };
			break;
		case STR2INT("PK\x05\x06"):
			SetBackColor(cLtYellow);
			GENERATE(endLocator, ::g->endLocator.generate());
			::g->preferred_tags = {  };
			::g->possible_tags = {  };
			break;
		default:
			Printf("Invalid ZIP tag occurred!\n");
			exit_template(-1);
		};
		::g->evil_state = SetEvilBit(false);
	};

	file_acc.finish();
	delete_globals();
}

void delete_globals() { delete ::g; }

