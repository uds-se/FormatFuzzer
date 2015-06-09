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

# http://www.sweetscape.com/010editor/manual/FuncString.htm

#double Atof( const char s[] )
@native(name="Atof", ret=pfp.fields.Double)
def Atof(params, ctxt, scope, stream, coord):
	pass

#int Atoi( const char s[] )
@native(name="Atoi", ret=pfp.fields.Int)
def Atoi(params, ctxt, scope, stream, coord):
	pass

#int64 BinaryStrToInt( const char s[] )
@native(name="BinaryStrToInt", ret=pfp.fields.Int64)
def BinaryStrToInt(params, ctxt, scope, stream, coord):
	pass

#char[] ConvertString( const char src[], int srcCharSet, int destCharSet )
@native(name="ConvertString", ret=pfp.fields.String)
def ConvertString(params, ctxt, scope, stream, coord):
	pass

#string DosDateToString( DOSDATE d, char format[] = "MM/dd/yyyy" )
@native(name="DosDateToString", ret=pfp.fields.String)
def DosDateToString(params, ctxt, scope, stream, coord):
	pass

#string DosTimeToString( DOSTIME t, char format[] = "hh:mm:ss" )
@native(name="DosTimeToString", ret=pfp.fields.String)
def DosTimeToString(params, ctxt, scope, stream, coord):
	pass

#string EnumToString( enum e )
@native(name="EnumToString", ret=pfp.fields.String)
def EnumToString(params, ctxt, scope, stream, coord):
	pass

#char[] FileNameGetBase( const char path[], int includeExtension=true )
@native(name="FileNameGetBase", ret=pfp.fields.String)
def FileNameGetBase(params, ctxt, scope, stream, coord):
	pass

#wchar_t[] FileNameGetBaseW( const wchar_t path[], int includeExtension=true )
@native(name="FileNameGetBaseW", ret=pfp.fields.WString)
def FileNameGetBaseW(params, ctxt, scope, stream, coord):
	pass

#char[] FileNameGetExtension( const char path[] )
@native(name="FileNameGetExtension", ret=pfp.fields.String)
def FileNameGetExtension(params, ctxt, scope, stream, coord):
	pass

#wchar_t[] FileNameGetExtensionW( const wchar_t path[] )
@native(name="FileNameGetExtensionW", ret=pfp.fields.WString)
def FileNameGetExtensionW(params, ctxt, scope, stream, coord):
	pass

#char[] FileNameGetPath( const char path[], int includeSlash=true )
@native(name="FileNameGetPath", ret=pfp.fields.String)
def FileNameGetPath(params, ctxt, scope, stream, coord):
	pass

#wchar_t[] FileNameGetPathW( const wchar_t path[], int includeSlash=true )
@native(name="FileNameGetPathW", ret=pfp.fields.WString)
def FileNameGetPathW(params, ctxt, scope, stream, coord):
	pass

#char[] FileNameSetExtension( const char path[], const char extension[] )
@native(name="FileNameSetExtension", ret=pfp.fields.String)
def FileNameSetExtension(params, ctxt, scope, stream, coord):
	pass

#wchar_t[] FileNameSetExtensionW( const wchar_t path[], const wchar_t extension[] )
@native(name="FileNameSetExtensionW", ret=pfp.fields.WString)
def FileNameSetExtensionW(params, ctxt, scope, stream, coord):
	pass

#string FileTimeToString( FILETIME ft, char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="FileTimeToString", ret=pfp.fields.String)
def FileTimeToString(params, ctxt, scope, stream, coord):
	pass

#char[] IntToBinaryStr( int64 num, int numGroups=0, int includeSpaces=true )
@native(name="IntToBinaryStr", ret=pfp.fields.String)
def IntToBinaryStr(params, ctxt, scope, stream, coord):
	pass

#int Memcmp( const uchar s1[], const uchar s2[], int n )
@native(name="Memcmp", ret=pfp.fields.Int)
def Memcmp(params, ctxt, scope, stream, coord):
	pass

#void Memcpy( uchar dest[], const uchar src[], int n, int destOffset=0, int srcOffset=0 )
@native(name="Memcpy", ret=pfp.fields.Void)
def Memcpy(params, ctxt, scope, stream, coord):
	pass

#void Memset( uchar s[], int c, int n )
@native(name="Memset", ret=pfp.fields.Void)
def Memset(params, ctxt, scope, stream, coord):
	pass

#string OleTimeToString( OLETIME ot, char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="OleTimeToString", ret=pfp.fields.String)
def OleTimeToString(params, ctxt, scope, stream, coord):
	pass

#int RegExMatch( string str, string regex );
@native(name="RegExMatch", ret=pfp.fields.Int)
def RegExMatch(params, ctxt, scope, stream, coord):
	pass

#int RegExMatchW( wstring str, wstring regex );
@native(name="RegExMatchW", ret=pfp.fields.Int)
def RegExMatchW(params, ctxt, scope, stream, coord):
	pass

#int RegExSearch( string str, string regex, int &matchSize, int startPos=0 );
@native(name="RegExSearch", ret=pfp.fields.Int)
def RegExSearch(params, ctxt, scope, stream, coord):
	pass

#int RegExSearchW( wstring str, wstring regex, int &matchSize, int startPos=0 );
@native(name="RegExSearchW", ret=pfp.fields.Int)
def RegExSearchW(params, ctxt, scope, stream, coord):
	pass

#int SPrintf( char buffer[], const char format[] [, argument, ... ] )
@native(name="SPrintf", ret=pfp.fields.Int)
def SPrintf(params, ctxt, scope, stream, coord):
	pass

#int SScanf( char str[], char format[], ... )
@native(name="SScanf", ret=pfp.fields.Int)
def SScanf(params, ctxt, scope, stream, coord):
	pass

#void Strcat( char dest[], const char src[] )
@native(name="Strcat", ret=pfp.fields.Void)
def Strcat(params, ctxt, scope, stream, coord):
	pass

#int Strchr( const char s[], char c )
@native(name="Strchr", ret=pfp.fields.Int)
def Strchr(params, ctxt, scope, stream, coord):
	pass

#int Strcmp( const char s1[], const char s2[] )
@native(name="Strcmp", ret=pfp.fields.Int)
def Strcmp(params, ctxt, scope, stream, coord):
	pass

#void Strcpy( char dest[], const char src[] )
@native(name="Strcpy", ret=pfp.fields.Void)
def Strcpy(params, ctxt, scope, stream, coord):
	pass

#char[] StrDel( const char str[], int start, int count )
@native(name="StrDel", ret=pfp.fields.String)
def StrDel(params, ctxt, scope, stream, coord):
	pass

#int Stricmp( const char s1[], const char s2[] )
@native(name="Stricmp", ret=pfp.fields.Int)
def Stricmp(params, ctxt, scope, stream, coord):
	pass

#int StringToDosDate( string s, DOSDATE &d, char format[] = "MM/dd/yyyy" )
@native(name="StringToDosDate", ret=pfp.fields.Int)
def StringToDosDate(params, ctxt, scope, stream, coord):
	pass

#int StringToDosTime( string s, DOSTIME &t, char format[] = "hh:mm:ss" )
@native(name="StringToDosTime", ret=pfp.fields.Int)
def StringToDosTime(params, ctxt, scope, stream, coord):
	pass

#int StringToFileTime( string s, FILETIME &ft, char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="StringToFileTime", ret=pfp.fields.Int)
def StringToFileTime(params, ctxt, scope, stream, coord):
	pass

#int StringToOleTime( string s, OLETIME &ot, char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="StringToOleTime", ret=pfp.fields.Int)
def StringToOleTime(params, ctxt, scope, stream, coord):
	pass

#int StringToTimeT( string s, time_t &t, char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="StringToTimeT", ret=pfp.fields.Int)
def StringToTimeT(params, ctxt, scope, stream, coord):
	pass

#char[] StringToUTF8( const char src[], int srcCharSet=CHARSET_ANSI )
@native(name="StringToUTF8", ret=pfp.fields.String)
def StringToUTF8(params, ctxt, scope, stream, coord):
	pass

#wstring StringToWString( const char str[], int srcCharSet=CHARSET_ANSI )
@native(name="StringToWString", ret=pfp.fields.WString)
def StringToWString(params, ctxt, scope, stream, coord):
	pass

#int Strlen( const char s[] )
@native(name="Strlen", ret=pfp.fields.Int)
def Strlen(params, ctxt, scope, stream, coord):
	pass

#int Strncmp( const char s1[], const char s2[], int n )
@native(name="Strncmp", ret=pfp.fields.Int)
def Strncmp(params, ctxt, scope, stream, coord):
	pass

#void Strncpy( char dest[], const char src[], int n )
@native(name="Strncpy", ret=pfp.fields.Void)
def Strncpy(params, ctxt, scope, stream, coord):
	pass

#int Strnicmp( const char s1[], const char s2[], int n )
@native(name="Strnicmp", ret=pfp.fields.Int)
def Strnicmp(params, ctxt, scope, stream, coord):
	pass

#int Strstr( const char s1[], const char s2[] )
@native(name="Strstr", ret=pfp.fields.Int)
def Strstr(params, ctxt, scope, stream, coord):
	pass

#char[] SubStr( const char str[], int start, int count=-1 )
@native(name="SubStr", ret=pfp.fields.String)
def SubStr(params, ctxt, scope, stream, coord):
	pass

#string TimeTToString( time_t t, char format[] = "MM/dd/yyyy hh:mm:ss" )
@native(name="TimeTToString", ret=pfp.fields.String)
def TimeTToString(params, ctxt, scope, stream, coord):
	pass

#char ToLower( char c )
@native(name="ToLower", ret=pfp.fields.Char)
def ToLower(params, ctxt, scope, stream, coord):
	pass

#wchar_t ToLowerW( wchar_t c )
@native(name="ToLowerW", ret=pfp.fields.WChar)
def ToLowerW(params, ctxt, scope, stream, coord):
	pass

#char ToUpper( char c )
@native(name="ToUpper", ret=pfp.fields.Char)
def ToUpper(params, ctxt, scope, stream, coord):
	pass

#void WMemcmp( const wchar_t s1[], const wchar_t s2[], int n )
@native(name="WMemcmp", ret=pfp.fields.Void)
def WMemcmp(params, ctxt, scope, stream, coord):
	pass

#void WMemcpy( wchar_t dest[], const wchar_t src[], int n, int destOffset=0, int srcOffset=0 )
@native(name="WMemcpy", ret=pfp.fields.Void)
def WMemcpy(params, ctxt, scope, stream, coord):
	pass

#void WMemset( wchar_t s[], int c, int n )
@native(name="WMemset", ret=pfp.fields.Void)
def WMemset(params, ctxt, scope, stream, coord):
	pass

#void WStrcat( wchar_t dest[], const wchar_t src[] )
@native(name="WStrcat", ret=pfp.fields.Void)
def WStrcat(params, ctxt, scope, stream, coord):
	pass

#int WStrchr( const wchar_t s[], wchar_t c )
@native(name="WStrchr", ret=pfp.fields.Int)
def WStrchr(params, ctxt, scope, stream, coord):
	pass

#int WStrcmp( const wchar_t s1[], const wchar_t s2[] )
@native(name="WStrcmp", ret=pfp.fields.Int)
def WStrcmp(params, ctxt, scope, stream, coord):
	pass

#void WStrcpy( wchar_t dest[], const wchar_t src[] )
@native(name="WStrcpy", ret=pfp.fields.Void)
def WStrcpy(params, ctxt, scope, stream, coord):
	pass

#wchar_t[] WStrDel( const whar_t str[], int start, int count )
@native(name="WStrDel", ret=pfp.fields.WString)
def WStrDel(params, ctxt, scope, stream, coord):
	pass

#int WStricmp( const wchar_t s1[], const wchar_t s2[] )
@native(name="WStricmp", ret=pfp.fields.Int)
def WStricmp(params, ctxt, scope, stream, coord):
	pass

#char[] WStringToString( const wchar_t str[], int destCharSet=CHARSET_ANSI )
@native(name="WStringToString", ret=pfp.fields.String)
def WStringToString(params, ctxt, scope, stream, coord):
	pass

#char[] WStringToUTF8( const wchar_t str[] )
@native(name="WStringToUTF8", ret=pfp.fields.String)
def WStringToUTF8(params, ctxt, scope, stream, coord):
	pass

#int WStrlen( const wchar_t s[] )
@native(name="WStrlen", ret=pfp.fields.Int)
def WStrlen(params, ctxt, scope, stream, coord):
	pass

#int WStrncmp( const wchar_t s1[], const wchar_t s2[], int n )
@native(name="WStrncmp", ret=pfp.fields.Int)
def WStrncmp(params, ctxt, scope, stream, coord):
	pass

#void WStrncpy( wchar_t dest[], const wchar_t src[], int n )
@native(name="WStrncpy", ret=pfp.fields.Void)
def WStrncpy(params, ctxt, scope, stream, coord):
	pass

#int WStrnicmp( const wchar_t s1[], const wchar_t s2[], int n )
@native(name="WStrnicmp", ret=pfp.fields.Int)
def WStrnicmp(params, ctxt, scope, stream, coord):
	pass

#int WStrstr( const wchar_t s1[], const wchar_t s2[] )
@native(name="WStrstr", ret=pfp.fields.Int)
def WStrstr(params, ctxt, scope, stream, coord):
	pass

#wchar_t[] WSubStr( const wchar_t str[], int start, int count=-1 )
@native(name="WSubStr", ret=pfp.fields.WString)
def WSubStr(params, ctxt, scope, stream, coord):
	pass
