#!/usr/bin/env python
# encoding: utf-8

"""
This module of native functions is implemented for
compatability with 010 editor functions. Some of these functions
are nops, some are fully implemented.
"""

import sys

from pfp.native import native
import pfp.fields

# http://www.sweetscape.com/010editor/manual/FuncTools.htm

#int64 Checksum( 
#    int algorithm, 
#    int64 start=0, 
#    int64 size=0, 
#    int64 crcPolynomial=-1, 
#    int64 crcInitValue=-1 )
@native(name="Checksum", ret=pfp.fields.Int64)
def Checksum(params, ctxt, scope, stream):
	"""
	Runs a simple checksum on a file and returns the result as a int64. The
	algorithm can be one of the following constants:

	CHECKSUM_BYTE - Treats the file as a set of unsigned bytes
	CHECKSUM_SHORT_LE - Treats the file as a set of unsigned little-endian shorts
	CHECKSUM_SHORT_BE - Treats the file as a set of unsigned big-endian shorts
	CHECKSUM_INT_LE - Treats the file as a set of unsigned little-endian ints
	CHECKSUM_INT_BE - Treats the file as a set of unsigned big-endian ints
	CHECKSUM_INT64_LE - Treats the file as a set of unsigned little-endian int64s
	CHECKSUM_INT64_BE - Treats the file as a set of unsigned big-endian int64s
	CHECKSUM_SUM8 - Same as CHECKSUM_BYTE except result output as 8-bits
	CHECKSUM_SUM16 - Same as CHECKSUM_BYTE except result output as 16-bits
	CHECKSUM_SUM32 - Same as CHECKSUM_BYTE except result output as 32-bits
	CHECKSUM_SUM64 - Same as CHECKSUM_BYTE
	CHECKSUM_CRC16
	CHECKSUM_CRCCCITT
	CHECKSUM_CRC32
	CHECKSUM_ADLER32

	If start and size are zero, the algorithm is run on the whole file. If
	they are not zero then the algorithm is run on size bytes starting at
	address start. See the ChecksumAlgBytes and ChecksumAlgStr functions
	to run more complex algorithms. crcPolynomial and crcInitValue
	can be used to set a custom polynomial and initial value for the
	CRC functions. A value of -1 for these parameters uses the default
	values as described in the Check Sum/Hash Algorithms topic. A negative
	number is returned on error.
	"""
	pass

#int ChecksumAlgArrayStr( 
#    int algorithm, 
#    char result[], 
#    uchar *buffer, 
#    int64 size, 
#    char ignore[]="", 
#    int64 crcPolynomial=-1, 
#    int64 crcInitValue=-1 )
@native(name="ChecksumAlgArrayStr", ret=pfp.fields.Int)
def ChecksumAlgArrayStr(params, ctxt, scope, stream):
	"""
	Similar to the ChecksumAlgStr function except that the checksum is
	run on data stored in an array instead of in a file. The data for the
	checksum should be passed in the buffer array and the size parameter
	lists the number of bytes in the array. The result from the checksum
	will be stored in the result string and the number of characters
	in the string will be returned, or -1 if an error occurred. See the
	ChecksumAlgStr function for a list of available algorithms.
	"""
	pass

#int ChecksumAlgArrayBytes( 
#    int algorithm, 
#    uchar result[], 
#    uchar *buffer, 
#    int64 size, 
#    char ignore[]="", 
#    int64 crcPolynomial=-1, 
#    int64 crcInitValue=-1 )
@native(name="ChecksumAlgArrayBytes", ret=pfp.fields.Int)
def ChecksumAlgArrayBytes(params, ctxt, scope, stream):
	"""
	Similar to the ChecksumAlgStr function except that the checksum is run
	on data in an array instead of in a file and the results are stored
	in an array of bytes instead of a string. The data for the checksum
	should be passed in the buffer array and the size parameter lists the
	number of bytes in the array. The result of the checksum operation
	will be stored as a set of hex bytes in the parameter result. The
	function will return the number of bytes placed in the result array
	or -1 if an error occurred. See the ChecksumAlgStr function for a
	list of available algorithms.
	"""
	pass

#int ChecksumAlgStr(
#    int algorithm, 
#    char result[], 
#    int64 start=0, 
#    int64 size=0, 
#    char ignore[]="", 
#    int64 crcPolynomial=-1, 
#    int64 crcInitValue=-1 )
@native(name="ChecksumAlgStr", ret=pfp.fields.Int)
def ChecksumAlgStr(params, ctxt, scope, stream):
	"""
	Similar to the Checksum algorithm except the following algorithm
	constants are supported:

	CHECKSUM_BYTE
	CHECKSUM_SHORT_LE
	CHECKSUM_SHORT_BE
	CHECKSUM_INT_LE
	CHECKSUM_INT_BE
	CHECKSUM_INT64_LE
	CHECKSUM_INT64_BE
	CHECKSUM_SUM8
	CHECKSUM_SUM16
	CHECKSUM_SUM32
	CHECKSUM_SUM64
	CHECKSUM_CRC16
	CHECKSUM_CRCCCITT
	CHECKSUM_CRC32
	CHECKSUM_ADLER32
	CHECKSUM_MD2
	CHECKSUM_MD4
	CHECKSUM_MD5
	CHECKSUM_RIPEMD160
	CHECKSUM_SHA1
	CHECKSUM_SHA256
	CHECKSUM_SHA512
	CHECKSUM_TIGER

	The result argument specifies a string which will hold the result of
	the checksum. The return value indicates the number of characters
	in the string, or is negative if an error occurred. Any ranges to
	ignore can be specified in string format with the ignore argument
	(see Check Sum/Hash Algorithms). The crcPolynomial and crcInitValue
	parameters are used to set a custom polynomial and initial value
	for the CRC algorithms. Specifying -1 for these parameters uses the
	default values as indicated in the Check Sum/Hash Algorithms help
	topic. See the Checksum function above for an explanation of the
	different checksum constants.
	"""
	pass

#int ChecksumAlgBytes( 
#    int algorithm, 
#    uchar result[], 
#    int64 start=0, 
#    int64 size=0, 
#    char ignore[]="", 
#    int64 crcPolynomial=-1, 
#    int64 crcInitValue=-1 )
@native(name="ChecksumAlgBytes", ret=pfp.fields.Int)
def ChecksumAlgBytes(params, ctxt, scope, stream):
	"""
	This function is identical to the ChecksumAlgStr function except that
	the checksum is returned as a byte array in the result argument. The
	return value is the number of bytes returned in the array.
	"""
	pass

#TCompareResults Compare( 
#    int type, 
#    int fileNumA, 
#    int fileNumB, 
#    int64 startA=0, 
#    int64 sizeA=0, 
#    int64 startB=0, 
#    int64 sizeB=0, 
#    int matchcase=true, 
#    int64 maxlookahead=10000, 
#    int64 minmatchlength=8, 
#    int64 quickmatch=512 )
@native(name="Compare", ret=pfp.fields.Void)
def Compare(params, ctxt, scope, stream):
	"""
	Runs a comparison between two files or between two blocks of data. The
	type argument indicates the type of comparison that should be run
	and can be either:

	COMPARE_SYNCHRONIZE (a binary comparison)
	COMPARE_SIMPLE (a byte-by-byte comparison)

	fileNumA and fileNumB indicate the numbers of the file to compare (see
	GetFileNum). The file numbers may be the same to compare two blocks
	in the same file. The startA, sizeA, startB, and sizeB arguments
	indicate the size of the blocks to compare in the two files. If the
	start and size are both zero, the whole file is used. If matchcase is
	false, then letters of mixed upper and lower cases will match. See
	Comparing Files for details on the maxlookahead, minmatchlength and
	quickmatch arguments. The return value is TCompareResults structure
	with contains a count variable indicating the number of resulting
	ranges, and an array of record. Each record contains the variables
	type, startA, sizeA, startB, and sizeB to indicate the range. The
	type variable will be one of:

	COMPARE_MATCH=0
	COMPARE_DIFFERENCE=1
	COMPARE_ONLY_IN_A=2
	COMPARE_ONLY_IN_B=3
	"""
	pass

#char ConvertASCIIToEBCDIC( char ascii )
@native(name="ConvertASCIIToEBCDIC", ret=pfp.fields.Char)
def ConvertASCIIToEBCDIC(params, ctxt, scope, stream):
	"""
	Converts the given ASCII character into an EBCDIC character and returns the result.
	"""
	pass

#void ConvertASCIIToUNICODE( 
#    int len, 
#    const char ascii[], 
#    ubyte unicode[], 
#    int bigendian=false )
@native(name="ConvertASCIIToUNICODE", ret=pfp.fields.Void)
def ConvertASCIIToUNICODE(params, ctxt, scope, stream):
	"""
	Converts an ASCII string into an array of bytes and stores them in the
	unicode argument. len indicates the number of characters to convert
	and the unicode array must be of size at least 2*len. If bigendian
	is true, the bytes are stored in big-endian mode, otherwise the
	bytes are stored in little-endian mode.
	"""
	pass

#void ConvertASCIIToUNICODEW( 
#    int len, 
#    const char ascii[], 
#    ushort unicode[] )
@native(name="ConvertASCIIToUNICODEW", ret=pfp.fields.Void)
def ConvertASCIIToUNICODEW(params, ctxt, scope, stream):
	"""
	Converts an ASCII string into an array of words and stores the array in
	the unicode argument. The number of characters to convert is given by
	the len argument and the unicode argument must have size at least len.
	"""
	pass

#char ConvertEBCDICToASCII( char ebcdic )
@native(name="ConvertEBCDICToASCII", ret=pfp.fields.Char)
def ConvertEBCDICToASCII(params, ctxt, scope, stream):
	"""
	Converts the given EBCDIC character into an ASCII character and returns the result.
	"""
	pass

#void ConvertUNICODEToASCII( 
#    int len, 
#    const ubyte unicode[], 
#    char ascii[], 
#    int bigendian=false )
@native(name="ConvertUNICODEToASCII", ret=pfp.fields.Void)
def ConvertUNICODEToASCII(params, ctxt, scope, stream):
	"""
	Converts an array of UNICODE characters in the unicode argument into
	ASCII bytes and stores them in the ascii array. len indicates the
	number of characters to convert. unicode must be of size at least
	size 2*len and ascii must be of size at least len. If bigendian is
	true, the bytes are stored in big-endian mode, otherwise the bytes
	are stored in little-endian mode.
	"""
	pass

#void ConvertUNICODEToASCIIW( 
#    int len, 
#    const ushort unicode[], 
#    char ascii[] )
@native(name="ConvertUNICODEToASCIIW", ret=pfp.fields.Void)
def ConvertUNICODEToASCIIW(params, ctxt, scope, stream):
	"""
	Converts the array of words in the unicode argument to ASCII bytes and
	saves them to the ascii argument. The number of characters to convert
	is given by len. unicode and ascii must be of size at least size len.
	"""
	pass

#int ExportFile( 
#    int type, 
#    char filename[], 
#    int64 start=0, 
#    int64 size=0, 
#    int64 startaddress=0, 
#    int bytesperrow=16, 
#    int wordaddresses=0 )
@native(name="ExportFile", ret=pfp.fields.Int)
def ExportFile(params, ctxt, scope, stream):
	"""
	Exports the currently open file to a file on disk given by filename
	using one of the following type formats:

	EXPORT_HEXTEXT
	EXPORT_DECTEXT
	EXPORT_BINARYTEXT
	EXPORT_CCODE
	EXPORT_JAVACODE
	EXPORT_INTEL8
	EXPORT_INTEL16
	EXPORT_INTEL32
	EXPORT_S19
	EXPORT_S28
	EXPORT_S37
	EXPORT_TEXT_AREA
	EXPORT_HTML
	EXPORT_RTF
	EXPORT_BASE64
	EXPORT_UUENCODE

	The start and size arguments indicate what portion of the
	file to export. If they are both zero then the whole file is
	exported. startaddress indicates the starting address that is written
	to the file for Intel Hex or Motorola formats. bytesperrow indicates
	the number of bytes written on each line of the output file. If
	wordaddresses is true and the export format is Intel Hex, the file
	will be written using word-based addresses. See Importing/Exporting
	Files for more information on exporting.
	"""
	pass

#TFindResults FindAll( 
#    <datatype> data, 
#    int matchcase=true, 
#    int wholeword=false, 
#    int method=0, 
#    double tolerance=0.0, 
#    int dir=1, 
#    int64 start=0, 
#    int64 size=0, 
#    int wildcardMatchLength=24 )
@native(name="FindAll", ret=pfp.fields.Void)
def FindAll(params, ctxt, scope, stream):
	"""
	This function converts the argument data into a set of hex bytes
	and then searches the current file for all occurrences of those
	bytes. data may be any of the basic types or an array of one of
	the types. If data is an array of signed bytes, it is assumed to
	be a null-terminated string. To search for an array of hex bytes,
	create an unsigned char array and fill it with the target value. If
	the type being search for is a string, the matchcase and wholeworld
	arguments can be used to control the search (see Using Find for more
	information). method controls which search method is used from the
	following options:

	FINDMETHOD_NORMAL=0 - a normal search
	FINDMETHOD_WILDCARDS=1 - when searching for strings use wildcards '*' or '?'
	FINDMETHOD_REGEX=2 - when searching for strings use Regular Expressions

	wildcardMatchLength indicates the maximum number of characters a '*' can match when searching using wildcards. If the target is a float or double, the tolerance argument indicates that values that are only off by the tolerance value still match. If dir is 1 the find direction is down and if dir is 0 the find direction is up. start and size can be used to limit the area of the file that is searched. start is the starting byte address in the file where the search will begin and size is the number of bytes after start that will be searched. If size is zero, the file will be searched from start to the end of the file.

	The return value is a TFindResults structure. This structure contains a count variable indicating the number of matches, and a start array holding an array of starting positions, plus a size array which holds an array of target lengths. For example, use the following code to find all occurrences of the ASCII string "Test" in a file:
	"""
	pass

#int64 FindFirst( 
#    <datatype> data, 
#    int matchcase=true, 
#    int wholeword=false, 
#    int method=0, 
#    double tolerance=0.0, 
#    int dir=1, 
#    int64 start=0, 
#    int64 size=0, 
#    int wildcardMatchLength=24 )
@native(name="FindFirst", ret=pfp.fields.Int64)
def FindFirst(params, ctxt, scope, stream):
	"""
	This function is identical to the FindAll function except that the
	return value is the position of the first occurrence of the target
	found. A negative number is returned if the value could not be found.
	"""
	pass

#TFindInFilesResults FindInFiles( 
#    <datatype> data, 
#    char dir[], 
#    char mask[], 
#    int subdirs=true, 
#    int openfiles=false, 
#    int matchcase=true, 
#    int wholeword=false, 
#    int method=0, 
#    double tolerance=0.0, 
#    int wildcardMatchLength=24 )
@native(name="FindInFiles", ret=pfp.fields.Void)
def FindInFiles(params, ctxt, scope, stream):
	"""
	Searches for a given set of data across multiple files. See the FindAll
	function for information on the data, matchcase, wholeword, method,
	wildcardMatchLength and tolerance arguments. The dir argument indicates
	the starting directory where the search will take place. mask indicates
	which file types to search and may contain the characters '*' and
	'?'. If subdirs is true, all subdirectories are recursively searched
	for the value as well. If openfiles is true, only the currently
	open files are searched. The return value is the TFindInFilesResults
	structure which contains a count variable indicate the number of files
	found plus an array of file variables. Each file variable contains
	a count variable indicating the number of matches, plus an array of
	start and size variables indicating the match position. For example:
	"""
	pass

#int64 FindNext( int dir=1 )
@native(name="FindNext", ret=pfp.fields.Int64)
def FindNext(params, ctxt, scope, stream):
	"""
	This function returns the position of the next occurrence of the
	target value specified with the FindFirst function. If dir is 1, the
	find direction is down. If dir is 0, the find direction is up. The
	return value is the address of the found data, or -1 if the target
	is not found.
	"""
	pass

#TFindStringsResults FindStrings( 
#    int minStringLength, 
#    int type, 
#    int matchingCharTypes, 
#    wstring customChars="", 
#    int64 start=0, 
#    int64 size=0, 
#    int requireNull=false )
@native(name="FindStrings", ret=pfp.fields.Void)
def FindStrings(params, ctxt, scope, stream):
	"""
	Attempts to locate any strings within a binary file similar to the Find
	Strings dialog which is accessed by clicking 'Search > Find Strings'
	on the main menu. Specify the minimum length of each string in number
	of characters with the minStringLength parameter. The type option
	tells the algorithm to look for ASCII strings, UNICODE strings or
	both by using one of the following constants:

	FINDSTRING_ASCII
	FINDSTRING_UNICODE
	FINDSTRING_BOTH

	To specify which characters are considered as part of a string,
	use an OR bitmask ('|') of one or more of the following constants:

	FINDSTRING_LETTERS - the letters A..Z and a..z
	FINDSTRING_LETTERS_ALL - all international numbers including FINDSTRING_LETTERS
	FINDSTRING_NUMBERS - the numbers 0..9
	FINDSTRING_NUMBERS_ALL - all international numbers including FINDSTRING_NUMBERS
	FINDSTRING_SYMBOLS - symbols such as '#', '@', '!', etc. except for '_'
	FINDSTRING_UNDERSCORE - the character '_'
	FINDSTRING_SPACES - spaces or whitespace
	FINDSTRING_LINEFEEDS - line feed characters 0x0a, 0x0d
	FINDSTRING_CUSTOM - include any custom characters in the customChars string

	Note if the FINDSTRING_CUSTOM constant is included, any characters
	from customChars are considered as part of the string otherwise the
	customChars string is ignored. The start and size parameters indicate
	the range of the file to search and if size is zero, the file is
	searched starting from start to the end of the file. If requireNull
	is true, the strings must have a null (0) character after each string.

	The return value is a TFindStringsResults structure which contains a
	count variable with the number of strings found, a start array holding
	the starting position of each string, a size array holding the size in
	bytes of each string, and a type array which indicates FINDSTRING_ASCII
	if the string is an ASCII string or FINDSTRING_UNICODE if the string
	is a Unicode string. For example, the following code finds all ASCII
	strings of length at least 5 containing the characters "A..Za..z$&":
	"""
	pass

#int GetSectorSize()
@native(name="GetSectorSize", ret=pfp.fields.Int)
def GetSectorSize(params, ctxt, scope, stream):
	"""
	Returns the size in bytes of the sectors for this drive. If this
	file is not a drive, the current sector size is defined using the
	'View > Division Lines > Set Sector Size' menu option.
	"""
	pass

#int HexOperation( 
#    int operation, 
#    int64 start, 
#    int64 size, 
#    operand, 
#    step=0, 
#    int64 skip=0 )
@native(name="HexOperation", ret=pfp.fields.Int)
def HexOperation(params, ctxt, scope, stream):
	"""
	Perform any of the operations on hex data as available in the Hex
	Operations dialog. The operation parameter chooses which operation to
	perform and these operations are described in the Hex Operations dialog
	documentation. start and size indicate which range of bytes to operate
	on and if size is 0, the whole file is used. The operand indicates what
	value to use during the operation and the result is different depending
	upon which operation is used (see the Hex Operations dialog). operand
	can be any of the basic numeric or floating point types and the type
	of this parameter tells the function how to interpret the data. For
	example, if a 'ushort' is passed as an operand, the block of data is
	considered as an array of 'ushort' using the current endian. If step
	is non-zero, the operand is incremented by step after each operation
	and if skip is non-zero, skip number of bytes are skipped after each
	operation. This function returns the number of bytes modified if
	successful, or a negative number on error. The following constants
	can be used for the operation parameter:

	HEXOP_ASSIGN
	HEXOP_ADD
	HEXOP_SUBTRACT
	HEXOP_MULTIPLY
	HEXOP_DIVIDE
	HEXOP_NEGATE
	HEXOP_MODULUS
	HEXOP_SET_MINIMUM
	HEXOP_SET_MAXIMUM
	HEXOP_SWAP_BYTES
	HEXOP_BINARY_AND
	HEXOP_BINARY_OR
	HEXOP_BINARY_XOR
	HEXOP_BINARY_INVERT
	HEXOP_SHIFT_LEFT
	HEXOP_SHIFT_RIGHT
	HEXOP_SHIFT_BLOCK_LEFT
	HEXOP_SHIFT_BLOCK_RIGHT
	HEXOP_ROTATE_LEFT
	HEXOP_ROTATE_RIGHT

	For example, the following code would treat the bytes from address
	16 to 48 as an array of floats and add the value 3.0 to each float
	in the array:
	"""
	pass

#int64 Histogram( int64 start, int64 size, int64 result[256] )
@native(name="Histogram", ret=pfp.fields.Int64)
def Histogram(params, ctxt, scope, stream):
	"""
	Counts the number of bytes of each value in the file from 0 up to
	255. The bytes are counting starting from address start and continuing
	for size bytes. The resulting counts are stored in the int64 array
	results. For example, result[0] would indicate the number of 0 bytes
	values found in the given range of data. The return value is the
	total number of bytes read.
	"""
	pass

#int ImportFile( int type, char filename[], int wordaddresses=false, int defaultByteValue=-1 )
@native(name="ImportFile", ret=pfp.fields.Int)
def ImportFile(params, ctxt, scope, stream):
	"""
	Attempts to import the file specified by filename in one of the
	supported import formats. The format is given by the type argument
	and may be:

	IMPORT_HEXTEXT
	IMPORT_DECTEXT
	IMPORT_BINARYTEXT
	IMPORT_SOURCECODE
	IMPORT_INTEL
	IMPORT_MOTOROLA
	IMPORT_BASE64
	IMPORT_UUENCODE

	If successful, the file is opened as a new file in the editor. If
	the function fails, a negative number is returned. If wordaddresses
	is true and the file is an Intel Hex file, the file is imported
	using word-based addressing. When importing some data formats (such
	as Intel Hex or S-Records) these formats may skip over certain
	bytes. The value to assign these bytes can be controlled with the
	defaultByteValue parameter and if the parameter is -1, the value
	from the Importing Options dialog is used. See Importing/Exporting
	Files for more information on importing.
	"""
	pass

#int IsDrive()
@native(name="IsDrive", ret=pfp.fields.Int)
def IsDrive(params, ctxt, scope, stream):
	"""
	Returns true if the current file is a physical or logical drive,
	or false otherwise (see Editing Drives).
	"""
	pass

#int IsLogicalDrive()
@native(name="IsLogicalDrive", ret=pfp.fields.Int)
def IsLogicalDrive(params, ctxt, scope, stream):
	"""
	Returns true if the current file is a logical drive, or false otherwise
	(see Editing Drives).
	"""
	pass

#int IsPhysicalDrive()
@native(name="IsPhysicalDrive", ret=pfp.fields.Int)
def IsPhysicalDrive(params, ctxt, scope, stream):
	"""
	Returns true if the current file is a physical drive, or false
	otherwise (see Editing Drives).
	"""
	pass

#int IsProcess()
@native(name="IsProcess", ret=pfp.fields.Int)
def IsProcess(params, ctxt, scope, stream):
	"""
	Returns true if the current file is a process, or false otherwise
	(see Editing Processes).
	"""
	pass

#int OpenLogicalDrive( char driveletter )
@native(name="OpenLogicalDrive", ret=pfp.fields.Int)
def OpenLogicalDrive(params, ctxt, scope, stream):
	"""
	Opens the drive with the given driveLetter as a new file in the
	editor. For example, 'OpenLogicalDrive('c');'. This function returns
	a negative number on failure. See Editing Drives for more information
	on drive editing.
	"""
	pass

#int OpenPhysicalDrive( int physicalID )
@native(name="OpenPhysicalDrive", ret=pfp.fields.Int)
def OpenPhysicalDrive(params, ctxt, scope, stream):
	"""
	Opens the physical drive physicalID as a new file in the editor
	(see Editing Drives). For example, 'OpenPhysicalDrive(0);'. This
	function returns a negative number on failure.
	"""
	pass

#int OpenProcessById( int processID, int openwriteable=true )
@native(name="OpenProcessById", ret=pfp.fields.Int)
def OpenProcessById(params, ctxt, scope, stream):
	"""
	Opens a process identified by the processID number (see Editing
	Processes). If openwriteable is true, only bytes that can be modified
	are opened, otherwise all readable bytes are opened. A negative
	number if returned if this function fails.
	"""
	pass

#int OpenProcessByName( char processname[], int openwriteable=true )
@native(name="OpenProcessByName", ret=pfp.fields.Int)
def OpenProcessByName(params, ctxt, scope, stream):
	"""
	Attempts to open a process given by the name processname as a new
	file in the editor. For example: 'OpenProcessByName( "cmd.exe" );'
	If openwriteable is true, only bytes that can be modified are opened,
	otherwise all readable bytes are opened. A negative number if returned
	if this function fails. See Editing Processes for more information.
	"""
	pass

#int ReplaceAll( 
#    <datatype> finddata, 
#    <datatype> replacedata, 
#    int matchcase=true, 
#    int wholeword=false, 
#    int method=0, 
#    double tolerance=0.0, 
#    int dir=1, 
#    int64 start=0, 
#    int64 size=0, 
#    int padwithzeros=false, 
#    int wildcardMatchLength=24 )
@native(name="ReplaceAll", ret=pfp.fields.Int)
def ReplaceAll(params, ctxt, scope, stream):
	"""
	This function converts the arguments finddata and replacedata into
	a set of bytes, and then finds all occurrences of the find bytes
	in the file and replaces them with the replace bytes. The arguments
	matchcase, wholeword, method, wildcardMatchLength, tolerance, dir,
	start, and size are all used when finding a value and are discussed
	in the FindAll function above. If padwithzeros is true, a set of
	zero bytes are added to the end of the replace data until it is
	the same length as the find data. The return value is the number of
	replacements made.
	"""
	pass
