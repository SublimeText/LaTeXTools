# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True


# Send DDE Execute command to running program

import sublime_plugin
from ctypes import *
import ctypes.wintypes


class send_ddeCommand(sublime_plugin.TextCommand):
	def run(self, edit, service = "", topic = "", command = ""):
		
		print ("Got request for DDE!")

		print(command)

		# define win32 api functions
		DdeInitialize = windll.user32.DdeInitializeW
		DdeUninitialize = windll.user32.DdeUninitialize
		DdeConnect = windll.user32.DdeConnect
		DdeDisconnect = windll.user32.DdeDisconnect
		DdeClientTransaction = windll.user32.DdeClientTransaction
		DdeCreateStringHandle = windll.user32.DdeCreateStringHandleW
		DdeFreeStringHandle = windll.user32.DdeFreeStringHandle
		DdeFreeDataHandle = windll.user32.DdeFreeDataHandle
		
		# Dde callback definition
		DDECALLBACK = WINFUNCTYPE(c_void_p, c_uint, c_uint, c_void_p, c_void_p, c_void_p, c_void_p, 
								 c_ulong, c_ulong)
		
		def py_mycallback(uType, uFmt, hconv, hsz1, hsz2, hdata, dwData1, dwData2):
			return 0
			
		mycallback = DDECALLBACK(py_mycallback)
		
		# Instance ID (filled out by DdeInitialize)
		idInst = c_ulong(0) # was c_uint
		# Conversation handle
		hConv = 0
		# server and topic names, as LPTSTR = wchar *
		service = c_wchar_p(service)
		topic = c_wchar_p(topic)
		# Potential ST2/ST3 difference:
		if _ST3:
			pData = create_unicode_buffer(command) # when all else fails, RTFM!
			cbData = len(bytes(pData))
			print (cbData, len(command))
		else:
			pData = c_char_p(command)
			cbData = len(command)+1 # Important! Zero-terminated!
		
		# initialize
		ret = DdeInitialize(byref(idInst), pointer(mycallback), 0, 0)
		print("DdeInitialize ", ret, idInst)
		# for the next two calls, the last param is the codepage:
		# 1004 = CP_Winansi, 1200 = CP_WINUNICODE
		hszService = DdeCreateStringHandle(idInst, service, 1200) 
		hszTopic = DdeCreateStringHandle(idInst, topic, 1200)
		hConv = DdeConnect(idInst, hszService, hszTopic, 0)
		print("DdeConnect ", hConv)
		
		if hConv:  # zero means we could not connect for some reason
			#print "start!"
			# c_uint for ST3
			XTYP_EXECUTE = c_uint(int("4050",16)) # transaction type; note -1 for timeout_async
			hDdeData = DdeClientTransaction(pData, cbData, hConv, 0, 0, XTYP_EXECUTE, 1000, 0) # 1000 was 10000
			print ("DDE Execute returned: " + hex(windll.user32.DdeGetLastError(idInst)), hDdeData)
			DdeFreeDataHandle(hDdeData)
		else:
			print ("Could not connect!")
		
		#print ret, idInst, hszService, hszTopic, hConv
		
		# test of string handles
		#buf = create_string_buffer(200)
		#print windll.user32.DdeQueryStringW(idInst, hszService, buf, 100, 1200)
		#print repr(buf.raw)
		# OK, this works!
				
		DdeFreeStringHandle(idInst, hszTopic)
		DdeFreeStringHandle(idInst, hszService)
		DdeDisconnect(hConv)
		DdeUninitialize(idInst)
		