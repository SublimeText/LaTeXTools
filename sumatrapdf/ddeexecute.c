#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <shellapi.h>
#include <ddeml.h>



// just hoping this is big enough
#define STRSAFE_MAX_CCH 1000


HDDEDATA CALLBACK dummy_callback(
  UINT uType,
  UINT uFmt,
  HCONV hconv,
  HSZ hsz1,
  HSZ hsz2,
  HDDEDATA hdata,
  ULONG_PTR dwData1,
  ULONG_PTR dwData2
) { return 0; }


int dde_execute(LPWSTR service, LPWSTR topic, LPWSTR command, UINT *lasterr)
{

   DWORD idInst = 0;
   DWORD cbCmdLength;
   
   UINT ret = DdeInitializeW(&idInst, &dummy_callback, APPCLASS_STANDARD, 0);
   if (ret)
   {
      return 1;
   }

   HSZ hszService = DdeCreateStringHandleW(idInst, service, CP_WINUNICODE);
   HSZ hszTopic = DdeCreateStringHandleW(idInst, topic, CP_WINUNICODE);

   HCONV hConv = DdeConnect(idInst, hszService, hszTopic, 0);

   if (hConv)
   {   
      cbCmdLength = (wcslen(command)+1) * sizeof(wchar_t);
      HDDEDATA hDdeData = DdeClientTransaction((LPBYTE)command, cbCmdLength, hConv, 0,0, XTYP_EXECUTE, 1000, 0);
      *lasterr = DdeGetLastError(idInst);
      DdeFreeDataHandle(hDdeData);
   }
   else
      return 3;


   DdeFreeStringHandle(idInst, hszTopic);
   DdeFreeStringHandle(idInst, hszService);
   DdeDisconnect(hConv);
   DdeUninitialize(idInst);
   return 0;
}



int main()
{
   LPWSTR *szArglist;
   int nArgs;
   int i;

   UINT lasterr;
   int dderes;

   // Read Unicode command-line arguments 
   szArglist = CommandLineToArgvW(GetCommandLineW(), &nArgs);
   if( NULL == szArglist )
   {
      wprintf(L"CommandLineToArgvW failed\n");
      return 1;
   }

   // Diagnostics:
   for( i=0; i<nArgs; i++) 
      wprintf(L"%d: %ws\n", i, szArglist[i]);
   
   if( nArgs != 4 ) {
      wprintf(L"usage: ddeexecute <service> <topic> <command>");
      return 1;
   }

   // We're good to go

   dderes = dde_execute(szArglist[1], szArglist[2], szArglist[3], &lasterr);

   // Diagnostics:
   if(dderes == 0)
      wprintf(L"DdeClientTransaction returned %d\n", lasterr);
   else
      wprintf(L"dderes = %d\n", dderes);

   // Free memory allocated for CommandLineToArgvW arguments.
   LocalFree(szArglist);

   return dderes;
}