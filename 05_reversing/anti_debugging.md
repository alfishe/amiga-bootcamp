[← Home](../README.md) · [Reverse Engineering](README.md)

# Amiga Anti-Debugging & The Arms Race

The late 1980s and early 1990s saw an intense "arms race" between Amiga software developers (implementing DRM) and crackers (removing DRM). Because the Amiga allowed user software to take complete, bare-metal control of the hardware, developers created highly sophisticated anti-debugging techniques to crash or hang the system if a cracker tried to analyze the game in a debugger.

This article codifies the most prominent anti-debugging tricks used on the Motorola 68000 and Amiga custom chips.

---

## 1. Trace Vector Abuse (Trace Vector Decoding - TVD)

The most famous anti-debugging trick is the **Rob Northen Copylock**. It abuses the 68000's Trace Exception to prevent single-stepping.

### The Mechanism
The 68000 CPU has a **Trace bit** (bit 15) in the Status Register (SR). When set, the CPU executes exactly one instruction and then automatically triggers a Trace Exception (Vector `$24` at memory address `$00000024`). Debuggers use this to implement "single-step" functionality.

Developers used **Trace Vector Decoding (TVD)** to maliciously overwrite the debugger's trace vector with their own decryption routine.

```assembly
; Copylock TVD Pattern
move.l  $24.w, old_trace     ; Save the debugger's vector (or just trash it)
move.l  #my_decryption, $24.w; Install our own trace handler
ori.w   #$8000, sr           ; Set the CPU Trace bit!
nop                          ; The interrupt fires immediately after this instruction

; ... CPU jumps to my_decryption ...

my_decryption:
    ; Decrypt the next instruction of the game
    ; Execute it
    ; Re-encrypt it (optional)
    rte                      ; Return from exception (which immediately fires AGAIN)
```

### The Cracker's Solution
If a cracker is single-stepping through this code, the moment `ori.w #$8000, sr` executes, the game steals the trace vector. The debugger loses control, and the game decrypts itself synchronously in the background. Crackers defeated this by using **Trace Emulators** or custom scripts that ran the decryption loop virtually, extracting the final decrypted payload from memory without relying on the hardware Trace bit.

---

## 2. Action Replay NMI Defeat

The **Action Replay** was a hardware cartridge that plugged into the Amiga's expansion port. Pressing its physical button generated a **Level 7 Non-Maskable Interrupt (NMI)**. This instantly froze the Amiga, dumping the user into a powerful machine-code monitor regardless of what the OS or game was doing.

Because it was non-maskable, developers could not simply disable it via the `INTENA` register.

### The Mechanism
While Level 7 interrupts cannot be masked, the CPU still uses an exception vector (`$0000007C`) to handle them. Developers simply pointed the NMI vector to a dummy `RTE` (Return from Exception) instruction.

```assembly
; Defeating the Action Replay
move.l  #ignore_nmi, $7c.w   ; Overwrite Level 7 Auto-Vector

; ... game code ...

ignore_nmi:
    rte                      ; Silently return if the freeze button is pressed
```

### The Cracker's Solution
Action Replay Mk II and III introduced features to intercept writes to `$7C.w` or used the MMU (on 68030 processors) to write-protect the vector table, ensuring the freezer always retained control.

---

## 3. CIA Timer Checks

If a developer suspects their code is being single-stepped, they can measure the exact time it takes to execute a block of instructions. 

### The Mechanism
The Amiga's 8520 CIA (Complex Interface Adapter) chips contain highly accurate hardware timers (Timer A and Timer B). 

```assembly
; CIA Timer Anti-Debugging
move.b  #$08, $bfd400      ; Start CIA-B Timer A
; ... decryption loop ...
move.b  $bfd400, d0        ; Read timer value
cmp.b   #$A0, d0           ; Did this take longer than X microseconds?
bgt.s   .debugger_detected ; Yes? We are being single-stepped!

.debugger_detected:
    ; Intentionally corrupt the decryption key
    eori.l  #$FFFFFFFF, d7
```

If a human is pressing "Step" in a debugger, the time elapsed will be millions of times slower than native execution. The game detects this and silently corrupts the decryption key. The game will crash later, confusing the cracker.

---

## 4. Software Breakpoint Checksumming

A common way to set a breakpoint in a 68k debugger is to overwrite an instruction with `$4AFC` (`ILLEGAL`). When the CPU hits it, it triggers an Illegal Instruction exception (Vector `$10`), handing control back to the debugger.

### The Mechanism
To detect `$4AFC` breakpoints, games constantly checksum their own code in memory.

```assembly
; Checksumming a block of code
    lea     code_start(pc), a0
    move.w  #100, d7
    moveq   #0, d0
.csum:
    add.w   (a0)+, d0
    dbf     d7, .csum

    cmp.w   #$1234, d0         ; Does the checksum match?
    bne.s   .debugger_found    ; If not, someone modified the code!
```

### Self-Modifying Code (SMC)
To make this even harder, developers used SMC. The code would dynamically alter its own instructions just before executing them. If a debugger placed a `$4AFC` breakpoint in the path of the SMC, the SMC would corrupt the breakpoint, or the breakpoint would corrupt the SMC calculation, leading to a crash.

---

## 5. VBR (Vector Base Register) Relocation

On the 68000, exception vectors are hardcoded at memory address `$00000000`. Standard software debuggers place their hooks here.

### The Mechanism
Starting with the 68010 (and present on the 68020/030/040/060), Motorola introduced the **Vector Base Register (VBR)**. This register allows the OS to move the entire exception vector table to any location in memory.

```assembly
; Moving the vector table (Requires Supervisor State)
    lea     new_vector_table, a0
    movec   a0, vbr
```

Games running on AGA Amigas (A1200/A4000) would allocate a new block of memory, copy the vector table there, alter the `vbr`, and then install their trace/NMI traps in the *new* table. Older debuggers hardcoded to read `$00000000` would be completely blind to these changes.

---

## 6. Hardware Register Traps

Debuggers often alter hardware state slightly (e.g., stopping DMA, changing screen colors, reading registers to update the UI).

### The Mechanism
*   **Write-Only Registers**: Many custom chip registers (like `BLTCON0` or `COLOR00`) are write-only. If a debugger tries to read them to save the system state, it actually reads open bus (garbage). If the debugger blindly writes that garbage back when resuming execution, the game crashes.
*   **Undocumented CIA Bits**: Some games would write specific patterns to undocumented bits in the CIA registers. Hardware freezers that didn't perfectly emulate or save/restore these undocumented bits would cause the game to fail its own integrity checks upon resuming.

---

## Summary

The Amiga anti-debugging scene was characterized by its proximity to the bare metal. Because there was no memory protection on the standard 68000, developers had free rein to abuse CPU exceptions, hijack hardware interrupts, and weaponize the system's own debugging features against reverse engineers. 

To defeat these protections today, modern reverse engineers rely on instruction-level emulators (like WinUAE's built-in debugger), which allow for invisible tracing, hardware watchpoints, and memory dumps that the running game cannot detect.
