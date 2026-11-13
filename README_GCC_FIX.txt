LocalCode Windows GCC runtime fix

This version prepends the standard MSYS2 UCRT64 runtime folders to PATH for compiler and program subprocesses. This addresses cases where GCC works inside the MSYS2 terminal but cc1plus.exe cannot find libgcc_s_seh-1.dll when LocalCode is launched from Windows Explorer.

Replace your existing app.py with this app.py. Keep your problems folder and all existing problem files. Then close every LocalCode window and launch run.bat again.

Assumes the default MSYS2 installation path: C:\msys64
