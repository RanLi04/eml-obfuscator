#include <string.h>

int is_blacklisted(const char* proc_name) {
    return strcmp(proc_name, "CheatEngine.exe") == 0 ||
           strcmp(proc_name, "ollydbg.exe") == 0;
}