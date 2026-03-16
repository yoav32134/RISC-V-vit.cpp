/*
 * Copyright (C) 2020 Embecosm Limited
 * SPDX-License-Identifier: BSD-2-Clause
 */
#include <machine/syscall.h>
#include <errno.h>
#include <sys/types.h>
#include "semihost_syscall.h"
#include "semihost_fdtable.h"
#include <stdio.h>

/* Read from a file.  */
ssize_t _read (int file, void *ptr, size_t len)
{
  struct fdentry *fd =__get_fdentry (file);
  long data_block[3];
  long res;

  if (fd == NULL)
    return -1;

  data_block[0] = fd->handle;
  data_block[1] = (long) ptr;
  data_block[2] = len;
  res = syscall_errno (SEMIHOST_read, data_block);
  if (res >= 0)
    {
      ssize_t bytes_read = len - res;
      fd->pos += bytes_read;
      if (bytes_read < 0 || bytes_read > len) {
        printf("READ BUG: len=%ld res=%ld bytes_read=%ld\n",
               (long)len, (long)res, (long)bytes_read);
        while (1);
      }
      return bytes_read;
    }
  return -1;
}
