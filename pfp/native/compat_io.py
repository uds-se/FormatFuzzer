#!/usr/bin/env python
# encoding: utf-8

"""
This module of native functions is implemented for
compatability with 010 editor functions. Some of these functions
are nops, some are fully implemented.
"""

import six
import sys

from pfp.native import native
import pfp.fields
import pfp.errors as errors
import pfp.bitwrap as bitwrap

# http://www.sweetscape.com/010editor/manual/FuncIO.htm

#void BigEndian()
@native(name="BigEndian", ret=pfp.fields.Void)
def BigEndian(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    pfp.fields.NumberBase.endian = pfp.fields.BIG_ENDIAN

#void BitfieldDisablePadding()
@native(name="BitfieldDisablePadding", ret=pfp.fields.Void, send_interp=True)
def BitfieldDisablePadding(params, ctxt, scope, stream, coord, interp):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    interp.set_bitfield_padded(False)

#void BitfieldEnablePadding()
@native(name="BitfieldEnablePadding", ret=pfp.fields.Void, send_interp=True)
def BitfieldEnablePadding(params, ctxt, scope, stream, coord, interp):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    interp.set_bitfield_padded(True)

#void BitfieldLeftToRight()
@native(name="BitfieldLeftToRight", ret=pfp.fields.Void, send_interp=True)
def BitfieldLeftToRight(params, ctxt, scope, stream, coord, interp):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    interp.set_bitfield_direction(interp.BITFIELD_DIR_LEFT_RIGHT)

#void BitfieldRightToLeft()
@native(name="BitfieldRightToLeft", ret=pfp.fields.Void, send_interp=True)
def BitfieldRightToLeft(params, ctxt, scope, stream, coord, interp):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    interp.set_bitfield_direction(interp.BITFIELD_DIR_RIGHT_LEFT)

#double ConvertBytesToDouble( uchar byteArray[] )
@native(name="ConvertBytesToDouble", ret=pfp.fields.Double)
def ConvertBytesToDouble(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#float ConvertBytesToFloat( uchar byteArray[] )
@native(name="ConvertBytesToFloat", ret=pfp.fields.Float)
def ConvertBytesToFloat(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#hfloat ConvertBytesToHFloat( uchar byteArray[] )
@native(name="ConvertBytesToHFloat", ret=pfp.fields.Float)
def ConvertBytesToHFloat(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int ConvertDataToBytes( data_type value, uchar byteArray[] )
@native(name="ConvertDataToBytes", ret=pfp.fields.Int)
def ConvertDataToBytes(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void DeleteBytes( int64 start, int64 size )
@native(name="DeleteBytes", ret=pfp.fields.Void)
def DeleteBytes(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int DirectoryExists( string dir )
@native(name="DirectoryExists", ret=pfp.fields.Int)
def DirectoryExists(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FEof()
@native(name="FEof", ret=pfp.fields.Int)
def FEof(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    
    # now that streams are _ALL_ BitwrappedStreams, we can use BitwrappedStream-specific
    # functions
    if stream.is_eof():
        return 1
    else:
        return 0

#int64 FileSize()
@native(name="FileSize", ret=pfp.fields.Int64)
def FileSize(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    return stream.size()

#TFileList FindFiles( string dir, string filter )
@native(name="FindFiles", ret=pfp.fields.Void)
def FindFiles(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FPrintf( int fileNum, char format[], ... )
@native(name="FPrintf", ret=pfp.fields.Int)
def FPrintf(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FSeek( int64 pos )
@native(name="FSeek", ret=pfp.fields.Int)
def FSeek(params, ctxt, scope, stream, coord):
    """Returns 0 if successful or -1 if the address is out of range
    """
    if len(params) != 1:
        raise errors.InvalidArguments(coord, "{} args".format(len(params)), "FSeek accepts only one argument")
    
    pos = PYVAL(params[0])
    curr_pos = stream.tell()

    fsize = stream.size()

    if pos > fsize:
        stream.seek(fsize)
        return -1
    elif pos < 0:
        stream.seek(0)
        return -1

    diff = pos - curr_pos
    if diff < 0:
        stream.seek(pos)
        return 0

    data = stream.read(diff)

    # let the ctxt automatically append numbers, as needed, unless the previous
    # child was also a skipped field
    skipped_name = "_skipped"

    if len(ctxt._pfp__children) > 0 and ctxt._pfp__children[-1]._pfp__name.startswith("_skipped"):
        old_name = ctxt._pfp__children[-1]._pfp__name
        data = ctxt._pfp__children[-1].raw_data + data
        skipped_name = old_name
        ctxt._pfp__children = ctxt._pfp__children[:-1]
        del ctxt._pfp__children_map[old_name]

    tmp_stream = bitwrap.BitwrappedStream(six.BytesIO(data))
    new_field = pfp.fields.Array(len(data), pfp.fields.Char, tmp_stream)
    ctxt._pfp__add_child(skipped_name, new_field, stream)
    scope.add_var(skipped_name, new_field)

    return 0

#int FSkip( int64 offset )
@native(name="FSkip", ret=pfp.fields.Int)
def FSkip(params, ctxt, scope, stream, coord):
    """Returns 0 if successful or -1 if the address is out of range
    """
    if len(params) != 1:
        raise errors.InvalidArguments(coord, "{} args".format(len(params)), "FSkip accepts only one argument")

    skip_amt = PYVAL(params[0])
    pos = skip_amt + stream.tell()
    return FSeek([pos], ctxt, scope, stream, coord)

#int64 FTell()
@native(name="FTell", ret=pfp.fields.Int64)
def FTell(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    return stream.tell()

#void InsertBytes( int64 start, int64 size, uchar value=0 )
@native(name="InsertBytes", ret=pfp.fields.Void)
def InsertBytes(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int IsBigEndian()
@native(name="IsBigEndian", ret=pfp.fields.Int)
def IsBigEndian(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    if pfp.fields.NumberBase.endian == pfp.fields.BIG_ENDIAN:
        return 1
    else:
        return 0

#int IsLittleEndian()
@native(name="IsLittleEndian", ret=pfp.fields.Int)
def IsLittleEndian(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    if pfp.fields.NumberBase.endian == pfp.fields.LITTLE_ENDIAN:
        return 0
    else:
        return 1

#void LittleEndian()
@native(name="LittleEndian", ret=pfp.fields.Void)
def LittleEndian(params, ctxt, scope, stream, coord):
    if len(params) > 0:
        raise errors.InvalidArguments(coord, "0 arguments", "{} args".format(len(params)))
    pfp.fields.NumberBase.endian = pfp.fields.LITTLE_ENDIAN

#int MakeDir( string dir )
@native(name="MakeDir", ret=pfp.fields.Int)
def MakeDir(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void OverwriteBytes( int64 start, int64 size, uchar value=0 )
@native(name="OverwriteBytes", ret=pfp.fields.Void)
def OverwriteBytes(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

def _read_data(params, stream, cls, coord):
    bits = stream._bits
    curr_pos = stream.tell()

    if len(params) == 1:
        pos = PYVAL(params[0])
        stream.seek(pos, 0)
    elif len(params) > 1:
        raise errors.InvalidArguments(coord, "at most 1 arguments", "{} args".format(len(params)))

    res = cls(stream=stream)

    # reset the stream
    stream.seek(curr_pos, 0)
    stream._bits = bits

    return res

#char ReadByte( int64 pos=FTell() )
@native(name="ReadByte", ret=pfp.fields.Char)
def ReadByte(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Char, coord)

#double ReadDouble( int64 pos=FTell() )
@native(name="ReadDouble", ret=pfp.fields.Double)
def ReadDouble(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Double, coord)

#float ReadFloat( int64 pos=FTell() )
@native(name="ReadFloat", ret=pfp.fields.Float)
def ReadFloat(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Float, coord)

#hfloat ReadHFloat( int64 pos=FTell() )
@native(name="ReadHFloat", ret=pfp.fields.Float)
def ReadHFloat(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Float, coord)

#int ReadInt( int64 pos=FTell() )
@native(name="ReadInt", ret=pfp.fields.Int)
def ReadInt(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Int, coord)

#int64 ReadInt64( int64 pos=FTell() )
@native(name="ReadInt64", ret=pfp.fields.Int64)
def ReadInt64(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Int64, coord)

#int64 ReadQuad( int64 pos=FTell() )
@native(name="ReadQuad", ret=pfp.fields.Int64)
def ReadQuad(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Int64, coord)

#short ReadShort( int64 pos=FTell() )
@native(name="ReadShort", ret=pfp.fields.Short)
def ReadShort(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.Short, coord)

#uchar ReadUByte( int64 pos=FTell() )
@native(name="ReadUByte", ret=pfp.fields.UChar)
def ReadUByte(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.UChar, coord)

#uint ReadUInt( int64 pos=FTell() )
@native(name="ReadUInt", ret=pfp.fields.UInt)
def ReadUInt(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.UInt, coord)

#uint64 ReadUInt64( int64 pos=FTell() )
@native(name="ReadUInt64", ret=pfp.fields.UInt64)
def ReadUInt64(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.UInt64, coord)

#uint64 ReadUQuad( int64 pos=FTell() )
@native(name="ReadUQuad", ret=pfp.fields.UInt64)
def ReadUQuad(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.UInt64, coord)

#ushort ReadUShort( int64 pos=FTell() )
@native(name="ReadUShort", ret=pfp.fields.UShort)
def ReadUShort(params, ctxt, scope, stream, coord):
    return _read_data(params, stream, pfp.fields.UShort, coord)

#char[] ReadLine( int64 pos, int maxLen=-1, int includeLinefeeds=true )
@native(name="ReadLine", ret=pfp.fields.String)
def ReadLine(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void ReadBytes( uchar buffer[], int64 pos, int n )
@native(name="ReadBytes", ret=pfp.fields.Void)
def ReadBytes(params, ctxt, scope, stream, coord):
    if len(params) != 3:
        raise errors.InvalidArguments(coord, "3 arguments (buffer, pos, n)", "{} args".format(len(params)))
    if not isinstance(params[0], pfp.fields.Array):
        raise errors.InvalidArguments(coord, "buffer must be an array", params[0].__class__.__name__)
    if params[0].field_cls not in [pfp.fields.UChar, pfp.fields.Char]:
        raise errors.InvalidArguments(coord, "buffer must be an array of uchar or char", params[0].field_cls.__name__)
    
    if not isinstance(params[1], pfp.fields.IntBase):
        raise errors.InvalidArguments(coord, "pos must be an integer", params[1].__class__.__name__)

    if not isinstance(params[2], pfp.fields.IntBase):
        raise errors.InvalidArguments(coord, "n must be an integer", params[2].__class__.__name__)
    
    bits = stream._bits
    curr_pos = stream.tell()

    vals = [params[0].field_cls(stream) for x in six.moves.range(PYVAL(params[2]))]

    stream.seek(curr_pos, 0)
    stream._bits = bits

    params[0]._pfp__set_value(vals)

#char[] ReadString( int64 pos, int maxLen=-1 )
@native(name="ReadString", ret=pfp.fields.String)
def ReadString(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int ReadStringLength( int64 pos, int maxLen=-1 )
@native(name="ReadStringLength", ret=pfp.fields.Int)
def ReadStringLength(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wstring ReadWLine( int64 pos, int maxLen=-1 )
@native(name="ReadWLine", ret=pfp.fields.WString)
def ReadWLine(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wstring ReadWString( int64 pos, int maxLen=-1 )
@native(name="ReadWString", ret=pfp.fields.WString)
def ReadWString(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int ReadWStringLength( int64 pos, int maxLen=-1 )
@native(name="ReadWStringLength", ret=pfp.fields.Int)
def ReadWStringLength(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 TextAddressToLine( int64 address )
@native(name="TextAddressToLine", ret=pfp.fields.Int64)
def TextAddressToLine(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int TextAddressToColumn( int64 address )
@native(name="TextAddressToColumn", ret=pfp.fields.Int)
def TextAddressToColumn(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 TextColumnToAddress( int64 line, int column )
@native(name="TextColumnToAddress", ret=pfp.fields.Int64)
def TextColumnToAddress(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 TextGetNumLines()
@native(name="TextGetNumLines", ret=pfp.fields.Int64)
def TextGetNumLines(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int TextGetLineSize( int64 line, int includeLinefeeds=true )
@native(name="TextGetLineSize", ret=pfp.fields.Int)
def TextGetLineSize(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 TextLineToAddress( int64 line )
@native(name="TextLineToAddress", ret=pfp.fields.Int64)
def TextLineToAddress(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int TextReadLine( char buffer[], int64 line, int maxsize, int includeLinefeeds=true )
@native(name="TextReadLine", ret=pfp.fields.Int)
def TextReadLine(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int TextReadLineW( wchar_t buffer[], int64 line, int maxsize, int includeLinefeeds=true )
@native(name="TextReadLineW", ret=pfp.fields.Int)
def TextReadLineW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void TextWriteLine( const char buffer[], int64 line, int includeLinefeeds=true )
@native(name="TextWriteLine", ret=pfp.fields.Void)
def TextWriteLine(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void TextWriteLineW( const wchar_t buffer[], int64 line, int includeLinefeeds=true )
@native(name="TextWriteLineW", ret=pfp.fields.Void)
def TextWriteLineW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteByte( int64 pos, char value )
@native(name="WriteByte", ret=pfp.fields.Void)
def WriteByte(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteDouble( int64 pos, double value )
@native(name="WriteDouble", ret=pfp.fields.Void)
def WriteDouble(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteFloat( int64 pos, float value )
@native(name="WriteFloat", ret=pfp.fields.Void)
def WriteFloat(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteHFloat( int64 pos, float value )
@native(name="WriteHFloat", ret=pfp.fields.Void)
def WriteHFloat(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteInt( int64 pos, int value )
@native(name="WriteInt", ret=pfp.fields.Void)
def WriteInt(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteInt64( int64 pos, int64 value )
@native(name="WriteInt64", ret=pfp.fields.Void)
def WriteInt64(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteQuad( int64 pos, int64 value )
@native(name="WriteQuad", ret=pfp.fields.Void)
def WriteQuad(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteShort( int64 pos, short value )
@native(name="WriteShort", ret=pfp.fields.Void)
def WriteShort(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteUByte( int64 pos, uchar value )
@native(name="WriteUByte", ret=pfp.fields.Void)
def WriteUByte(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteUInt( int64 pos, uint value )
@native(name="WriteUInt", ret=pfp.fields.Void)
def WriteUInt(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteUInt64( int64 pos, uint64 value )
@native(name="WriteUInt64", ret=pfp.fields.Void)
def WriteUInt64(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteUQuad( int64 pos, uint64 value )
@native(name="WriteUQuad", ret=pfp.fields.Void)
def WriteUQuad(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteUShort( int64 pos, ushort value )
@native(name="WriteUShort", ret=pfp.fields.Void)
def WriteUShort(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteBytes( const uchar buffer[], int64 pos, int n )
@native(name="WriteBytes", ret=pfp.fields.Void)
def WriteBytes(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteString( int64 pos, const char value[] )
@native(name="WriteString", ret=pfp.fields.Void)
def WriteString(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void WriteWString( int64 pos, const wstring value )
@native(name="WriteWString", ret=pfp.fields.Void)
def WriteWString(params, ctxt, scope, stream, coord):
    raise NotImplementedError()
