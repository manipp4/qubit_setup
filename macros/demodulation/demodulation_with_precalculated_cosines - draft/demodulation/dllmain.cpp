// dllmain.cpp : D�finit le point d'entr�e pour l'application DLL.
#include "stdafx.h"
#include <math.h>
#include <iostream>
#define PI 3.14159265359	






BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}

