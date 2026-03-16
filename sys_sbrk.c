//taken from https://gist.github.com/winsrewu/910a0c4f83b17c9b5be8ad8cab437ad3
//not my code in any way
#include <errno.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>


extern char _heap_start;
extern char _heap_size;

static char *heap_end = &_heap_start;

// EXTERN_C_BEGIN

caddr_t _sbrk(int incr)
{
    char *prev;
    if (heap_end + incr > (&_heap_start + (uintptr_t)&_heap_size))
    {
        errno = ENOMEM;
        return (caddr_t)-1;
    }
    prev = heap_end;
    heap_end += incr;
    return prev;
}

int _gettimeofday(struct timeval *tv, void *tz) {
    (void)tz;

    if (tv) {
        tv->tv_sec = 0;
        tv->tv_usec = 0;
    }

    return 0;
}


//taken from https://github.com/payne92/bare-metal-arm/blob/master/syscalls.c
//not my code
int _fstat(int file, struct stat *st)
{
    st->st_mode = S_IFCHR;
    return 0;
}

int _isatty(int fd)
{
    (void)fd;
    return 1;
}


