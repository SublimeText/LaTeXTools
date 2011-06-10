import sublime, sublime_plugin
from ctypes import *

# Send DDE Execute command to running program

class send_ddeCommand(sublime_plugin.TextCommand):
	def run(self, edit, service = "", topic = "", command = ""):
		
		print "Got request for DDE!"

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
		idInst = c_uint(0)
		# Conversation handle
		hConv = 0
		# server and topic names, as LPTSTR = wchar *
		service = c_wchar_p(service)
		topic = c_wchar_p(topic)
		pData = c_char_p(command)
		cbData = len(command)+1 # Important! Zero-terminated!
		
		# initialize
		ret = DdeInitialize(byref(idInst), pointer(mycallback), 0, 0)
		# for the next two calls, the last param is the codepage:
		# 1004 = CP_Winansi, 1200 = CP_WINUNICODE
		hszService = DdeCreateStringHandle(idInst, service, 1200) 
		hszTopic = DdeCreateStringHandle(idInst, topic, 1200)
		hConv = DdeConnect(idInst, hszService, hszTopic, 0)
		
		if hConv:  # zero means we could not connect for some reason
			#print "start!"
			XTYP_EXECUTE = int("4050",16) # transaction type; note -1 for timeout_async
			hDdeData = DdeClientTransaction(pData, cbData, hConv, 0, 0, XTYP_EXECUTE, 10000, 0)
			print "DDE Execute returned: ", hex(windll.user32.DdeGetLastError(idInst))
			DdeFreeDataHandle(hDdeData)
		else:
			print "Could not connect!"
		
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
		