/* crt0.S - startup for your exact link.ld */

.section .text.init
.option norvc

.global _start
.type _start, @function

.extern main
.extern exit
.extern __libc_init_array

/* Linker symbols from your link.ld */
.extern _global_pointer
.extern _bss_start
.extern _bss_end
.extern _stack_end

_start:
    /* Set global pointer exactly as your linker provides it */
    .option push
    .option norelax
    la      gp, _global_pointer
    .option pop

    /* No paging */
    csrw    satp, zero

    /* Only hart 0 runs */
    csrr    t0, mhartid
    bnez    t0, .Lhang

    /* Disable machine interrupts */
    csrw    mie, zero

    /* Set stack and keep ABI alignment */
    la      sp, _stack_end
    andi    sp, sp, -16

    /* Clear .bss safely byte-by-byte
       Your linker does not guarantee bss size is a multiple of 8. */
    la      t0, _bss_start
    la      t1, _bss_end
.Lbss_clear:
    bgeu    t0, t1, .Lbss_done
    sb      zero, 0(t0)
    addi    t0, t0, 1
    j       .Lbss_clear
.Lbss_done:

    /* Enable floating point state (for rv64gc / C++ / libc safety) */
    li      t0, (3 << 13)          /* mstatus.FS = 11 (Dirty) */
    csrs    mstatus, t0
    csrw    fcsr, zero

    /* Optional but robust: run C/C++ global constructors */
    call    __libc_init_array

    /* main(argc=0, argv=NULL) */
    li      a0, 0
    li      a1, 0
    call    main

    /* If main returns, go through libc exit path */
    call    exit

.Lhang:
    wfi
    j       .Lhang

.size _start, . - _start