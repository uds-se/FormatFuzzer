#!/usr/bin/env python
# encoding: utf-8

"""
This module of native functions is implemented for
compatability with 010 editor functions. Some of these functions
are nops, some are fully implemented.
"""

import sys

from pfp.native import native, predefine
import pfp.fields
import pfp.errors as errors

# http://www.sweetscape.com/010editor/manual/FuncInterface.htm

#void AddBookmark( 
#    int64 pos, 
#    string name, 
#    string typename, 
#    int arraySize=-1, 
#    int forecolor=cNone, 
#    int backcolor=0xffffc4, 
#    int moveWithCursor=false )
@native(name="AddBookmark", ret=pfp.fields.Void)
def AddBookmark(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void ClearClipboard()
@native(name="ClearClipboard", ret=pfp.fields.Void)
def ClearClipboard(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void CopyBytesToClipboard( uchar buffer[], int size, int charset=CHARSET_ANSI, int bigendian=false )
@native(name="CopyBytesToClipboard", ret=pfp.fields.Void)
def CopyBytesToClipboard(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void CopyStringToClipboard( const char str[], int charset=CHARSET_ANSI )
@native(name="CopyStringToClipboard", ret=pfp.fields.Void)
def CopyStringToClipboard(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void CopyToClipboard()
@native(name="CopyToClipboard", ret=pfp.fields.Void)
def CopyToClipboard(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void CutToClipboard()
@native(name="CutToClipboard", ret=pfp.fields.Void)
def CutToClipboard(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int DeleteFile( char filename[] )
@native(name="DeleteFile", ret=pfp.fields.Int)
def DeleteFile(params, ctxt, scope, stream, coord):
    return 0

#void DisableUndo()
@native(name="DisableUndo", ret=pfp.fields.Void)
def DisableUndo(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void DisplayFormatBinary()
@native(name="DisplayFormatBinary", ret=pfp.fields.Void)
def DisplayFormatBinary(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void DisplayFormatDecimal()
@native(name="DisplayFormatDecimal", ret=pfp.fields.Void)
def DisplayFormatDecimal(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void DisplayFormatHex()
@native(name="DisplayFormatHex", ret=pfp.fields.Void)
def DisplayFormatHex(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void DisplayFormatOctal()
@native(name="DisplayFormatOctal", ret=pfp.fields.Void)
def DisplayFormatOctal(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void EnableUndo()
@native(name="EnableUndo", ret=pfp.fields.Void)
def EnableUndo(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int Exec( const char program[], const char arguments[], int wait, int &errorCode )
@native(name="Exec", ret=pfp.fields.Int)
def Exec(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void Exit( int errorcode )
@native(name="Exit", ret=pfp.fields.Void)
def Exit(params, ctxt, scope, stream, coord):
    if len(params) != 1:
        raise errors.InvalidArguments(coord, "1 arguments", "{} args".format(len(params)))
    error_code = PYVAL(params[0])
    raise errors.InterpExit(error_code)

#void ExpandAll()
@native(name="ExpandAll", ret=pfp.fields.Void)
def ExpandAll(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void ExportCSV( const char filename[] )
@native(name="ExportCSV", ret=pfp.fields.Void)
def ExportCSV(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void ExportXML( const char filename[] )
@native(name="ExportXML", ret=pfp.fields.Void)
def ExportXML(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void FileClose()
@native(name="FileClose", ret=pfp.fields.Void)
def FileClose(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FileCount()
@native(name="FileCount", ret=pfp.fields.Int)
def FileCount(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FileExists( const char filename[] )
@native(name="FileExists", ret=pfp.fields.Int)
def FileExists(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FileNew( char interface[]="", int makeActive=true )
@native(name="FileNew", ret=pfp.fields.Int)
def FileNew(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FileOpen( const char filename[], int runTemplate=false, char interface[]="", int openDuplicate=false )
@native(name="FileOpen", ret=pfp.fields.Int)
def FileOpen(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FileSave()
#int FileSave( const char filename[] )
#int FileSave( const wchar_t filename[] )
@native(name="FileSave", ret=pfp.fields.Int)
def FileSave(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FileSaveRange( const char filename[], int64 start, int64 size )
#int FileSaveRange( const wchar_t filename[], int64 start, int64 size )
@native(name="FileSaveRange", ret=pfp.fields.Int)
def FileSaveRange(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void FileSelect( int index )
@native(name="FileSelect", ret=pfp.fields.Void)
def FileSelect(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FindOpenFile( const char path[] )
@native(name="FindOpenFile", ret=pfp.fields.Int)
def FindOpenFile(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int FindOpenFileW( const wchar_t path[] )
@native(name="FindOpenFileW", ret=pfp.fields.Int)
def FindOpenFileW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetArg( int index )
@native(name="GetArg", ret=pfp.fields.String)
def GetArg(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] GetArgW( int index )
@native(name="GetArgW", ret=pfp.fields.WString)
def GetArgW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetBackColor()
@native(name="GetBackColor", ret=pfp.fields.Int)
def GetBackColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetBookmarkArraySize( int index )
@native(name="GetBookmarkArraySize", ret=pfp.fields.Int)
def GetBookmarkArraySize(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetBookmarkBackColor( int index )
@native(name="GetBookmarkBackColor", ret=pfp.fields.Int)
def GetBookmarkBackColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetBookmarkForeColor( int index )
@native(name="GetBookmarkForeColor", ret=pfp.fields.Int)
def GetBookmarkForeColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetBookmarkMoveWithCursor( int index )
@native(name="GetBookmarkMoveWithCursor", ret=pfp.fields.Int)
def GetBookmarkMoveWithCursor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#string GetBookmarkName( int index )
@native(name="GetBookmarkName", ret=pfp.fields.String)
def GetBookmarkName(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int64 GetBookmarkPos( int index )
@native(name="GetBookmarkPos", ret=pfp.fields.Int64)
def GetBookmarkPos(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#string GetBookmarkType( int index )
@native(name="GetBookmarkType", ret=pfp.fields.String)
def GetBookmarkType(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetBytesPerLine()
@native(name="GetBytesPerLine", ret=pfp.fields.Int)
def GetBytesPerLine(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetClipboardBytes( uchar buffer[], int maxBytes )
@native(name="GetClipboardBytes", ret=pfp.fields.Int)
def GetClipboardBytes(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetClipboardIndex()
@native(name="GetClipboardIndex", ret=pfp.fields.Int)
def GetClipboardIndex(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#string GetClipboardString()
@native(name="GetClipboardString", ret=pfp.fields.String)
def GetClipboardString(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#string GetCurrentTime( char format[] = "hh:mm:ss" )
@native(name="GetCurrentTime", ret=pfp.fields.String)
def GetCurrentTime(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#string GetCurrentDate( char format[] = "MM/dd/yyyy" )
@native(name="GetCurrentDate", ret=pfp.fields.String)
def GetCurrentDate(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#string GetCurrentDateTime( char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="GetCurrentDateTime", ret=pfp.fields.String)
def GetCurrentDateTime(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 GetCursorPos()
@native(name="GetCursorPos", ret=pfp.fields.Int64)
def GetCursorPos(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetEnv( const char str[] )
@native(name="GetEnv", ret=pfp.fields.String)
def GetEnv(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetFileAttributesUnix()
@native(name="GetFileAttributesUnix", ret=pfp.fields.Int)
def GetFileAttributesUnix(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetFileAttributesWin()
@native(name="GetFileAttributesWin", ret=pfp.fields.Int)
def GetFileAttributesWin(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetFileCharSet()
@native(name="GetFileCharSet", ret=pfp.fields.Int)
def GetFileCharSet(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetFileInterface()
@native(name="GetFileInterface", ret=pfp.fields.String)
def GetFileInterface(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetFileName()
@native(name="GetFileName", ret=pfp.fields.String, send_interp=True)
def GetFileName(params, ctxt, scope, stream, coord, interp):
    return interp.get_filename()

#wchar_t[] GetFileNameW()
@native(name="GetFileNameW", ret=pfp.fields.WString)
def GetFileNameW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetFileNum()
@native(name="GetFileNum", ret=pfp.fields.Int)
def GetFileNum(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetForeColor()
@native(name="GetForeColor", ret=pfp.fields.Int)
def GetForeColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetMouseWheelScrollSpeed()
@native(name="GetMouseWheelScrollSpeed", ret=pfp.fields.Int)
def GetMouseWheelScrollSpeed(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetNumArgs()
@native(name="GetNumArgs", ret=pfp.fields.Int)
def GetNumArgs(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int GetNumBookmarks()
@native(name="GetNumBookmarks", ret=pfp.fields.Int)
def GetNumBookmarks(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int GetReadOnly()
@native(name="GetReadOnly", ret=pfp.fields.Int)
def GetReadOnly(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetScriptName()
@native(name="GetScriptName", ret=pfp.fields.String)
def GetScriptName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] GetScriptNameW()
@native(name="GetScriptNameW", ret=pfp.fields.WString)
def GetScriptNameW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetScriptFileName()
@native(name="GetScriptFileName", ret=pfp.fields.String)
def GetScriptFileName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] GetScriptFileNameW()
@native(name="GetScriptFileNameW", ret=pfp.fields.WString)
def GetScriptFileNameW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 GetSelSize()
@native(name="GetSelSize", ret=pfp.fields.Int64)
def GetSelSize(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 GetSelStart()
@native(name="GetSelStart", ret=pfp.fields.Int64)
def GetSelStart(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#string GetTempDirectory()
@native(name="GetTempDirectory", ret=pfp.fields.String)
def GetTempDirectory(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetTempFileName()
@native(name="GetTempFileName", ret=pfp.fields.String)
def GetTempFileName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetTemplateName()
@native(name="GetTemplateName", ret=pfp.fields.String)
def GetTemplateName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] GetTemplateNameW()
@native(name="GetTemplateNameW", ret=pfp.fields.WString)
def GetTemplateNameW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetTemplateFileName()
@native(name="GetTemplateFileName", ret=pfp.fields.String)
def GetTemplateFileName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] GetTemplateFileNameW()
@native(name="GetTemplateFileNameW", ret=pfp.fields.WString)
def GetTemplateFileNameW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] GetWorkingDirectory()
@native(name="GetWorkingDirectory", ret=pfp.fields.String)
def GetWorkingDirectory(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] GetWorkingDirectoryW()
@native(name="GetWorkingDirectoryW", ret=pfp.fields.WString)
def GetWorkingDirectoryW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] InputDirectory( const char title[], const char defaultDir[]="" , coord)
@native(name="InputDirectory", ret=pfp.fields.String)
def InputDirectory(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#double InputFloat(const char title[], const char caption[], const char defaultValue[] , coord)
@native(name="InputFloat", ret=pfp.fields.Double)
def InputFloat(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int InputNumber(const char title[], const char caption[], const char defaultValue[] , coord)
@native(name="InputNumber", ret=pfp.fields.Int)
def InputNumber(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] InputOpenFileName(
#    char title[], 
#    char filter[]="All files (*.*)",
#    char filename[]="" )
@native(name="InputOpenFileName", ret=pfp.fields.String)
def InputOpenFileName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#TOpenFileNames InputOpenFileNames(
#    char title[], 
#    char filter[]="All files (*.*)",
#    char filename[]="" )
@native(name="InputOpenFileNames", ret=pfp.fields.Void)
def InputOpenFileNames(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int InputRadioButtonBox(
#    const char title[], 
#    const char caption[], 
#    int defaultIndex, 
#    const char str1[], const char str2[], const char str3[]="", 
#    const char str4[]="", const char str5[]="", const char str6[]="", 
#    const char str7[]="", const char str8[]="", const char str9[]="",
#    const char str10[]="", const char str11[]="", const char str12[]="",
#    const char str13[]="", const char str14[]="", const char str15[]="" )
@native(name="InputRadioButtonBox", ret=pfp.fields.Int)
def InputRadioButtonBox(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] InputSaveFileName(
#    char title[],
#    char filter[]="All files (*.*)",
#    char filename[]="",
#    char extension[]="" )
@native(name="InputSaveFileName", ret=pfp.fields.String)
def InputSaveFileName(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#char[] InputString(
#    const char title[],
#    const char caption[],
#    const char defaultValue[] , coord)
@native(name="InputString", ret=pfp.fields.String)
def InputString(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wstring InputWString(
#    const char title[],
#    const char caption[],
#    const wstring defaultValue , coord)
@native(name="InputWString", ret=pfp.fields.WString)
def InputWString(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int InsertFile( const char filename[], int64 position )
@native(name="InsertFile", ret=pfp.fields.Int)
def InsertFile(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int IsEditorFocused()
@native(name="IsEditorFocused", ret=pfp.fields.Int)
def IsEditorFocused(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int IsModified()
@native(name="IsModified", ret=pfp.fields.Int)
def IsModified(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int IsNoUIMode()
@native(name="IsNoUIMode", ret=pfp.fields.Int)
def IsNoUIMode(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int MessageBox( int mask, const char title[], const char format[] [, argument, ... ] )
@native(name="MessageBox", ret=pfp.fields.Int)
def MessageBox(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void OutputPaneClear()
@native(name="OutputPaneClear", ret=pfp.fields.Void)
def OutputPaneClear(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int OutputPaneSave( const char filename[] )
@native(name="OutputPaneSave", ret=pfp.fields.Int)
def OutputPaneSave(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void OutputPaneCopy()
@native(name="OutputPaneCopy", ret=pfp.fields.Void)
def OutputPaneCopy(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void PasteFromClipboard()
@native(name="PasteFromClipboard", ret=pfp.fields.Void)
def PasteFromClipboard(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int Printf( const char format[] [, argument, ... ] ) 
@native(name="Printf", ret=pfp.fields.Int)
def Printf(params, ctxt, scope, stream, coord):
    """Prints format string to stdout

    :params: TODO
    :returns: TODO

    """
    if len(params) == 1:
        sys.stdout.write(PYSTR(params[0]))
        return len(PYSTR(params[0]))

    parts = []
    for part in params[1:]:
        if isinstance(part, pfp.fields.Array) or isinstance(part, pfp.fields.String):
            parts.append(PYSTR(part))
        else:
            parts.append(PYVAL(part))

    to_print = PYSTR(params[0]) % tuple(parts)
    res = len(to_print)
    sys.stdout.write(to_print)
    sys.stdout.flush()
    return res

#int64 ProcessGetHeapLocalAddress( int index )
@native(name="ProcessGetHeapLocalAddress", ret=pfp.fields.Int64)
def ProcessGetHeapLocalAddress(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#wchar_t[] ProcessGetHeapModule( int index )
@native(name="ProcessGetHeapModule", ret=pfp.fields.WString)
def ProcessGetHeapModule(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int ProcessGetHeapSize( int index )
@native(name="ProcessGetHeapSize", ret=pfp.fields.Int)
def ProcessGetHeapSize(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 ProcessGetHeapStartAddress( int index )
@native(name="ProcessGetHeapStartAddress", ret=pfp.fields.Int64)
def ProcessGetHeapStartAddress(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int ProcessGetNumHeaps()
@native(name="ProcessGetNumHeaps", ret=pfp.fields.Int)
def ProcessGetNumHeaps(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 ProcessHeapToLocalAddress( int64 memoryAddress )
@native(name="ProcessHeapToLocalAddress", ret=pfp.fields.Int64)
def ProcessHeapToLocalAddress(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int64 ProcessLocalToHeapAddress( int64 localAddress )
@native(name="ProcessLocalToHeapAddress", ret=pfp.fields.Int64)
def ProcessLocalToHeapAddress(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void RemoveBookmark( int index )
@native(name="RemoveBookmark", ret=pfp.fields.Void)
def RemoveBookmark(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int RenameFile( const char originalname[], const char newname[] )
@native(name="RenameFile", ret=pfp.fields.Int)
def RenameFile(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void RequiresFile()
@native(name="RequiresFile", ret=pfp.fields.Void)
def RequiresFile(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void RequiresVersion( int majorVer, int minorVer=0, int revision=0 )
@native(name="RequiresVersion", ret=pfp.fields.Void)
def RequiresVersion(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void RunTemplate( const char filename[]="", int clearOutput=false )
@native(name="RunTemplate", ret=pfp.fields.Void)
def RunTemplate(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

predefine("""
const int cBlack = 0x000000;
const int cRed = 0x0000ff;
const int cDkRed = 0x000080;
const int cLtRed = 0x8080ff;
const int cGreen = 0x00ff00;
const int cDkGreen = 0x008000;
const int cLtGreen = 0x80ff80;
const int cBlue = 0xff0000;
const int cDkBlue = 0x800000;
const int cLtBlue = 0xff8080;
const int cPurple = 0xff00ff;
const int cDkPurple = 0x800080;
const int cLtPurple = 0xffe0ff;
const int cAqua = 0xffff00;
const int cDkAqua = 0x808000;
const int cLtAqua = 0xffffe0;
const int cYellow = 0x00ffff;
const int cDkYellow = 0x008080;
const int cLtYellow = 0x80ffff;
const int cDkGray = 0x404040;
const int cGray = 0x808080;
const int cSilver = 0xc0c0c0;
const int cLtGray = 0xe0e0e0;
const int cWhite = 0xffffff;
const int cNone = 0xffffffff;
""")
#void SetBackColor( int color )
@native(name="SetBackColor", ret=pfp.fields.Void)
def SetBackColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void SetColor( int forecolor, int backcolor )
@native(name="SetColor", ret=pfp.fields.Void)
def SetColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void SetForeColor( int color )
@native(name="SetForeColor", ret=pfp.fields.Void)
def SetForeColor(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#int SetClipboardIndex( int index )
@native(name="SetClipboardIndex", ret=pfp.fields.Int)
def SetClipboardIndex(params, ctxt, scope, stream, coord):
    # resolved: won't implement
    pass

#void SetCursorPos( int64 pos )
@native(name="SetCursorPos", ret=pfp.fields.Void)
def SetCursorPos(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetEnv( const char str[], const char value[] )
@native(name="SetEnv", ret=pfp.fields.Int)
def SetEnv(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetFileAttributesUnix( int attributes )
@native(name="SetFileAttributesUnix", ret=pfp.fields.Int)
def SetFileAttributesUnix(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetFileAttributesWin( int attributes )
@native(name="SetFileAttributesWin", ret=pfp.fields.Int)
def SetFileAttributesWin(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetFileInterface( const char name[] )
@native(name="SetFileInterface", ret=pfp.fields.Int)
def SetFileInterface(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void SetMouseWheelScrollSpeed( int speed )
@native(name="SetMouseWheelScrollSpeed", ret=pfp.fields.Void)
def SetMouseWheelScrollSpeed(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetReadOnly( int readonly )
@native(name="SetReadOnly", ret=pfp.fields.Int)
def SetReadOnly(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void SetSelection( int64 start, int64 size )
@native(name="SetSelection", ret=pfp.fields.Void)
def SetSelection(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetWorkingDirectory( const char dir[] )
@native(name="SetWorkingDirectory", ret=pfp.fields.Int)
def SetWorkingDirectory(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#int SetWorkingDirectoryW( const wchar_t dir[] )
@native(name="SetWorkingDirectoryW", ret=pfp.fields.Int)
def SetWorkingDirectoryW(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void Sleep( int milliseconds )
@native(name="Sleep", ret=pfp.fields.Void)
def Sleep(params, ctxt, scope, stream, coord):
    raise NotImplementedError()

#void StatusMessage( const char format[] [, argument, ... ] )
@native(name="StatusMessage", ret=pfp.fields.Void)
def StatusMessage(params, ctxt, scope, stream, coord):
    pass

#void Terminate( int force=true )
@native(name="Terminate", ret=pfp.fields.Void)
def Terminate(params, ctxt, scope, stream, coord):
    raise errors.InterpExit()

#void Warning( const char format[] [, argument, ... ] )
@native(name="Warning", ret=pfp.fields.Void)
def Warning(params, ctxt, scope, stream, coord):
    pass

#void Assert( int value, const char msg[] = "" )
@native(name="Assert", ret=pfp.fields.Void)
def Assert(params, ctxt, scope, stream, coord):
    pass
