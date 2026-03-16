//
// Created by yoav on 3/8/26.
//

//not my code taken from git.musl-libc.org/cgit/musl/tree/src/malloc/posix_memalign.c


#include <stdlib.h>
#include <errno.h>

int posix_memalign(void **res, size_t align, size_t len)
{
    if (align < sizeof(void *)) return EINVAL;
    void *mem = aligned_alloc(align, len);
    if (!mem) return errno;
    *res = mem;
    return 0;
}

