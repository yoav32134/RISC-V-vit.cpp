//
// Created by yoav on 3/8/26.
//
//code taken from the https://github.com/gcc-mirror/gcc/blob/master/libgcc/crtstuff.c
//repository, not my code


#ifdef TARGET_LIBGCC_SDATA_SECTION
extern void *__dso_handle __attribute__ ((__section__ (TARGET_LIBGCC_SDATA_SECTION)));
#endif
#ifdef HAVE_GAS_HIDDEN
extern void *__dso_handle __attribute__ ((__visibility__ ("hidden")));
#endif
#ifdef CRTSTUFFS_O
void *__dso_handle = &__dso_handle;
#else
void *__dso_handle = 0;
#endif
