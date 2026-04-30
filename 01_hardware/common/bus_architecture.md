[← Home](../../README.md) · [Hardware](../README.md)

# Bus Architecture & Register Access

## Overview

Every instruction the CPU executes, every pixel the display fetches, and every audio sample Paula plays involves a **bus transaction** — a precisely timed handshake between a bus master and a target device over shared address and data lines. Understanding how these transactions physically propagate through the Amiga's bus hierarchy is the key to understanding *why* Chip RAM is slow, *why* Fast RAM is fast, *how* custom chip registers must be accessed, and *what* happens when an accelerated CPU tries to talk to hardware designed for a 7 MHz 68000.

This article covers the **mechanics** of bus operation. For *where* things are mapped, see [address_space.md](address_space.md). For *what kinds of memory* exist, see [memory_types.md](memory_types.md). For DMA slot scheduling and bandwidth, see [dma_architecture.md](dma_architecture.md). For the clock tree that drives all bus timing, see [video_timing.md](video_timing.md).

---

## §1 — The Bus Hierarchy

### The Dual-Domain Architecture

The Amiga is not a single-bus machine. Even a stock A500 has a hierarchy of interconnected buses, and adding an accelerator card creates a **dual-domain** system with two fundamentally different clock domains:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ACCELERATOR LOCAL BUS                            │
│            (32-bit, CPU speed: 25–50+ MHz)                          │
│  ┌──────────┐    ┌──────────────┐                                   │
│  │ 68030/40 │◄──►│  Fast RAM    │  ← Zero wait states, no DMA       │
│  │  /060    │    │  (private)   │     contention, full CPU speed    │
│  └────┬─────┘    └──────────────┘                                   │
│       │                                                             │
│  ┌────▼─────────────────────┐                                       │
│  │   BUS ADAPTER / BRIDGE   │  ← Clock domain crossing              │
│  │  (CPLD/FPGA/gate array)  │     Synchronizes to 7 MHz             │
│  └────┬─────────────────────┘                                       │
└───────┼─────────────────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────────┐
│                  MOTHERBOARD BUS (16-bit, 7.09 MHz)                 │
│                                                                     │
│  ┌──────────┐                                                       │
│  │  Gary /  │  ← Address decoder: reads A17–A23,                    │
│  │ Fat Gary │    generates chip-select signals                      │
│  └────┬─────┘                                                       │
│       │                                                             │
│  ┌────▼──────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐           │
│  │   Agnus   │  │  CIAs    │  │ Kickstart │  │  Zorro   │           │
│  │  (DMA     │  │ ($BFx000)│  │   ROM     │  │  Slots   │           │
│  │  master)  │  │          │  │($F80000)  │  │($200000+)│           │
│  └────┬──────┘  └──────────┘  └───────────┘  └──────────┘           │
│       │                                                             │
│  ┌────▼───────────────────────────────────────────────────┐         │
│  │              CHIP RAM BUS                              │         │
│  │     (16-bit, DMA-interleaved, video-synchronous)       │         │
│  │                                                        │         │
│  │  Shared between: Agnus DMA, Denise, Paula, CPU         │         │
│  │  Access rule: time-slot interleaving (see dma_arch.)   │         │
│  └────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Everything below Gary runs at the video-derived clock** — 7.09 MHz (PAL) or 7.16 MHz (NTSC). This frequency is not arbitrary; it is the master crystal ÷ 4, the same clock that drives CPU cycles, DMA slots, and the Copper. See [video_timing.md §2](video_timing.md#2--the-clock-tree) for the full derivation.

2. **Agnus is the bus master** — on the Chip RAM bus, Agnus (or Alice on AGA) decides who gets access each cycle. The CPU gets whatever slots the custom chips don't need. On a heavy display (6 bitplanes, all sprites active, Blitter running), the CPU may get **zero** Chip RAM slots during the active display area.

3. **Gary is the address decoder** — it doesn't touch the data bus. It reads the upper address lines and asserts chip-select signals: `/CAS` for Chip RAM, `/ROMEN` for Kickstart, `/CIAA`/`/CIAB` for the CIAs, etc. See [gary_system_controller.md](../ocs_a500/gary_system_controller.md) for the full decode matrix.

4. **The bus adapter is a clock-domain bridge** — when an accelerated CPU accesses anything on the motherboard (Chip RAM, custom registers, CIAs, ROM), the bus adapter must synchronize the request to the 7 MHz motherboard clock and wait for an available slot. This is the **"Chip RAM penalty"** — typically 5–15× slower than local Fast RAM access.

5. **Fast RAM is private** — it lives on the accelerator's local bus, runs at the CPU's native clock, and has no contention with DMA. This is why adding Fast RAM to an Amiga produces a dramatic speedup even without changing the CPU.

---

## §2 — Anatomy of a Bus Cycle

### The 68000 Bus Cycle

Every CPU access to memory or I/O follows a strict protocol defined by the 68000 bus specification. The minimum bus cycle is **4 clock periods** (S0–S7, where each S-state is a half-clock):

```
Clock:  ─┐  ┌──┐  ┌──┐  ┌──┐  ┌──
         │  │  │  │  │  │  │  │
         └──┘  └──┘  └──┘  └──┘

State:  S0  S1  S2  S3  S4  S5  S6  S7
        ├───┤   ├───┤   ├───┤   ├───┤
         ↑       ↑       ↑       ↑
         │       │       │       └── Data latched (read) or removed (write)
         │       │       └────────── DTACK sampled — if not asserted, insert
         │       │                   wait states (repeat S4–S5)
         │       └────────────────── Address stable, AS asserted, R/W set
         └────────────────────────── Address output begins
```

At 7.09 MHz (PAL), one clock period = **141 ns**, so the minimum 4-clock bus cycle = **~564 ns**. This is the fastest possible memory access on a stock Amiga.

### Read vs. Write

| Phase | Read Cycle | Write Cycle |
|---|---|---|
| S0–S1 | CPU drives address, sets R/W = Read | CPU drives address, sets R/W = Write |
| S2 | `/AS` asserted, address valid | `/AS` asserted, address valid |
| S3 | — | CPU drives data onto bus |
| S4 | Target samples address, asserts `/DTACK` | Target samples address + data, asserts `/DTACK` |
| S5 | — (wait for DTACK if not yet asserted) | — |
| S6 | CPU samples data from bus | — |
| S7 | `/AS` released, bus cycle ends | `/AS` released, bus cycle ends |

> [!NOTE]
> The `CLR.W` instruction on the 68000 performs a **read-modify-write** cycle: it reads the target, then writes zero. On a read-only register or a strobe register (like `COPJMP1`), the read has side effects. Later CPUs (68020+) changed `CLR` to write-only, creating a behavioral difference that matters for hardware register access. See §4.

### Wait States

When the target is not ready, it delays asserting `/DTACK`. The CPU inserts **wait states** — extra S4–S5 pairs — until DTACK arrives. Each wait state adds one full clock (141 ns):

| Target | Typical Wait States | Total Cycle Time (PAL) |
|---|---|---|
| **Chip RAM** (CPU's turn) | 0 | ~564 ns (4 clocks) |
| **Chip RAM** (DMA busy) | 2–8+ | ~846 ns – 1.7 µs |
| **Kickstart ROM** | 0–2 | ~564–846 ns |
| **CIA registers** | 6–10 | ~1.4–2.0 µs (E-clock sync) |
| **Zorro II I/O** | 0–4 (card-dependent) | ~564 ns – 1.1 µs |
| **Non-existent address** | Timeout → Bus Error | ~10 µs (Gary bus timeout) |

### Word and Long-Word on a 16-bit Bus

The 68000 has a 16-bit data bus. Accessing different data sizes costs different numbers of bus cycles:

| Access Size | Bus Cycles | Minimum Time (PAL) | Notes |
|---|---|---|---|
| Byte (`.B`) | 1 | ~564 ns | Upper or lower byte via `/UDS`/`/LDS` |
| Word (`.W`) | 1 | ~564 ns | Full 16-bit transfer |
| Long (`.L`) | 2 | ~1.13 µs | Two consecutive word transfers |

On 68020/030 with 32-bit bus (A3000, A4000 motherboard bus, or accelerator local bus), a long-word access completes in a single bus cycle. But when these CPUs access the 16-bit motherboard bus, the bus adapter performs **dynamic bus sizing** — splitting the 32-bit access into two 16-bit cycles automatically.

---

## §3 — Address Decoding — The Bus Glue Chips

Every bus cycle begins with the CPU placing an address on the bus. Something must decide which device should respond. On the Amiga, this job falls to a hierarchy of **bus glue** chips — custom gate arrays that decode the upper address bits and assert the appropriate chip-select signal.

### The Decode Chain

```
CPU Address Lines (A17–A23 / A17–A31)
          │
          ▼
    ┌───────────┐
    │   Gary /  │──── /CAS (Chip RAM)
    │ Fat Gary  │──── /ROMEN (Kickstart ROM)
    │           │──── /CIAA, /CIAB (CIA pair)
    │           │──── /OVL (overlay control)
    │           │──── /DTACK (cycle acknowledge)
    │           │──── /EXTRN (expansion bus)
    └───────────┘
          │ (for A3000/A4000)
          ▼
    ┌───────────┐
    │  Buster   │──── Zorro III arbitration
    │           │──── DMA handshake (DMAEN, DSACK)
    └───────────┘
          │
          ▼
    ┌───────────┐
    │  Ramsey   │──── DRAM /RAS, /CAS
    │           │──── Refresh control
    │           │──── Fast RAM page-hit optimization
    └───────────┘
```

### Per-Model Glue Chips

| Chip | Models | Role | Key Functions |
|---|---|---|---|
| **Gary** (CSG 5719) | A500, A2000 | Address decoder | A17–A23 decode, chip selects, bus timeout, ROM overlay |
| **Fat Gary** (CSG 5391/5393) | A3000 | 32-bit address decoder | Gary + SCSI/FPU chip select, Zorro III decode, 32-bit DTACK |
| **Gayle** (CSG 391424) | A600, A1200, A4000 | System controller | IDE, PCMCIA, address decode (replaces Gary on these models) |
| **Buster** (CSG 5394/5396) | A3000, A4000 | Zorro III controller | DMA arbitration, burst mode, slot negotiation |
| **Ramsey** (CSG 3901/3902) | A3000, A4000 | DRAM controller | /RAS//CAS generation, refresh, page-mode, burst |
| **Budgie** | CDTV | System controller | Gary equivalent + DMAC glue for CD-ROM |

> [!TIP]
> **FPGA developers:** Gary's decode logic is purely combinational — no internal state. Fat Gary adds a small state machine for SCSI and FPU acknowledgment. Both are well-documented in the dedicated articles: [Gary (OCS)](../ocs_a500/gary_system_controller.md), [Fat Gary (ECS)](../ecs_a600_a3000/gary_system_controller.md).

### The ROM Overlay Mechanism

At power-on, the CPU fetches its initial stack pointer and program counter from address `$000000`. But Chip RAM lives there — and Chip RAM is empty at boot. Gary solves this with the **overlay** bit:

1. At reset, Gary maps Kickstart ROM (`$F80000`) over Chip RAM at `$000000`
2. CPU reads exception vectors from ROM
3. Kickstart writes to CIA-A port bit 0, clearing the overlay
4. Gary unmaps ROM from $000000, making Chip RAM visible
5. Kickstart copies exception vectors into Chip RAM

This mechanism is identical across all Amiga models — only the chip implementing it changes (Gary → Fat Gary → Gayle).

### Bus Timeout

If no device asserts `/DTACK` within a configurable window, Gary generates a `/BERR` (Bus Error) exception. This protects the system from hanging when accessing non-existent hardware:

- **Gary (A500/A2000):** ~10 µs timeout
- **Fat Gary (A3000):** ~8 µs timeout, configurable
- **Gayle (A1200/A4000):** similar timeout with IDE-specific extensions

### Bus Arbitration Algorithms

Multiple devices compete for the bus: the CPU, Agnus DMA, expansion cards (Zorro DMA masters), and accelerator bridges. The Amiga uses a **layered priority** scheme:

**Layer 1 — Agnus Chip RAM Arbitration (fixed priority)**

Agnus controls Chip RAM access using a deterministic slot-based schedule. Priority is hardwired — not negotiable:

```
Priority (highest to lowest):
  1. Disk DMA         — guaranteed slots, cannot be preempted
  2. Audio DMA        — 4 channels, guaranteed slots
  3. Sprite DMA       — 8 sprites, guaranteed slots per scanline
  4. Bitplane DMA     — 1–8 bitplanes, consumes proportional slots
  5. Copper DMA       — interleaved with display
  6. Blitter DMA      — fills remaining DMA slots (nasty mode overrides CPU)
  7. CPU              — gets whatever is left
```

When `BLTPRI` (Blitter nasty mode) is set in `DMACON`, the Blitter takes priority over the CPU for *all* remaining slots, effectively freezing the CPU during Blitter operations. Without nasty mode, CPU and Blitter alternate on available slots.

See [dma_architecture.md](dma_architecture.md) for the complete slot allocation table and per-scanline bandwidth analysis.

**Layer 2 — 68000 Bus Arbitration (3-wire handshake)**

External DMA masters (Zorro cards, accelerator bridges) request the bus using the standard 68000 protocol:

1. Device asserts `/BR` (Bus Request)
2. CPU finishes current bus cycle, asserts `/BG` (Bus Grant)
3. Device asserts `/BGACK` (Bus Grant Acknowledge) — CPU tri-states its bus lines
4. Device performs DMA transfers
5. Device releases `/BR` and `/BGACK` — CPU reclaims bus

This is a **daisy-chain priority** — multiple requestors are wired in series. The device closest to the CPU in the chain has highest priority. On the A2000, the Zorro II slots are daisy-chained in slot order.

> [!NOTE]
> This is the **motherboard** bus arbitration — separate from Agnus's Chip RAM slot scheduling. A Zorro DMA master can own the motherboard bus, but Agnus still controls Chip RAM access independently. The Zorro master can access Chip RAM only through Agnus's slot allocation.

**Layer 3 — Buster Zorro III Arbitration (A3000/A4000)**

On Zorro III systems, Buster provides a more sophisticated fair arbitration:

- **Round-robin** among Zorro III slots — no permanent starvation
- **Burst mode** — a master can hold the bus for multiple transfers (up to 256 bytes on rev 11)
- **Bus tenure** — each master gets a maximum time window before forced release
- **Buster revision matters:** rev 9 (A3000) has known arbitration bugs that cause DMA corruption with certain card combinations. Rev 11 (A4000, fixed A3000 boards) resolves these.


---

## §4 — Custom Chip Register Access (`$DFF000`)

The custom chip registers occupy a 512-byte block at `$DFF000`–`$DFF1FE`. These are not memory — they are hardware ports with strict access rules. Violating them causes silent corruption, not exceptions.

### Register Categories

| Category | Access | Count | Examples | Notes |
|---|---|---|---|---|
| **Write-only** | Write | ~130 | `COLOR00`, `BPLCON0`, `BPL1PTH` | Reading returns bus noise or last DMA value |
| **Read-only** | Read | ~15 | `VPOSR`, `VHPOSR`, `DMACONR`, `JOY0DAT` | Writing is silently ignored |
| **Strobe** | Write | ~10 | `COPJMP1`, `COPJMP2`, `INTREQ` | Write triggers action; data value may be irrelevant |
| **Read-clear** | Read | ~5 | `INTREQR`, `ADKCONR` | Reading returns current value |
| **Set/Clear** | Write | ~10 | `DMACON`, `INTENA`, `INTREQ` | Bit 15 = SET (1) or CLEAR (0) for remaining bits |

### The Word-Only Rule

Custom chip registers are **16-bit wide** and must be accessed with word-sized operations:

```asm
; ✓ CORRECT — word write to COLOR00
    MOVE.W  #$0F00,$DFF180      ; Set background to red

; ✗ WRONG — byte write
    MOVE.B  #$0F,$DFF180        ; Unpredictable! Byte lane mismatch

; ✓ CORRECT — long-word write to paired register (high/low pointer)
    MOVE.L  #copperlist,$DFF080 ; Writes COP1LCH and COP1LCL atomically
```

Long-word writes to **consecutive register pairs** (e.g., `BPL1PTH`/`BPL1PTL` at `$DFF0E0`/`$DFF0E2`) work correctly because the 68000 performs two sequential word writes. This is a common and intentional optimization for pointer registers.

### The `CLR.W` Hazard

The 68000's `CLR` instruction performs a **read-modify-write** bus cycle:

```asm
; ✗ DANGEROUS on 68000 — reads the register first!
    CLR.W   $DFF09C             ; INTREQ — the READ has side effects!

; ✓ SAFE — pure write, no read cycle
    MOVE.W  #0,$DFF09C          ; INTREQ — write-only, no read side effects
```

On the 68000, `CLR.W $DFF09C` first **reads** INTREQ (which on some registers clears flags), then writes zero. The read is an unintended side effect. On 68020+ processors, Motorola changed `CLR` to a write-only cycle, so the same instruction behaves differently.

> [!WARNING]
> **Portable rule:** Never use `CLR` on hardware registers. Always use `MOVE.W #0,addr`. This works identically on all 680x0 processors and avoids the read side effect entirely.

### C Language Access Pattern

When accessing hardware registers from C, two things are mandatory:

1. **`volatile`** — prevents the compiler from optimizing away or reordering register accesses
2. **Word pointer type** — ensures the compiler generates `MOVE.W`, not `MOVE.B` or `MOVE.L`

```c
/* Standard pattern — NDK-style custom base */
struct Custom *custom = (struct Custom *)0xDFF000;

/* Direct register access (volatile is built into the NDK struct definition) */
custom->color[0] = 0x000;          /* MOVE.W #0,$DFF180 */
custom->intreq = INTF_SETCLR | INTF_VERTB;  /* Set VBL interrupt */

/* Raw pointer pattern (for register not in struct) */
#define VHPOSR (*(volatile UWORD *)0xDFF006)
UWORD pos = VHPOSR;               /* Read beam position */
```

> [!NOTE]
> The Amiga NDK `hardware/custom.h` defines `struct Custom` with all fields already `volatile`. If you use a custom base pointer, your code is automatically safe from optimization bugs.

### Timing Semantics

Register writes take effect at the **start of the next color clock (CCK) cycle** — not instantaneously. A write to `COLOR00` at $DFF180 changes the background color starting from the next pixel output cycle. This is why the Copper can create per-scanline color changes with single-cycle precision: each `MOVE` in the Copper list is timed to a specific horizontal position.

For registers that affect DMA (like `DMACONW` or `BPLxPTH`), the new value typically takes effect at the next DMA slot boundary. See [dma_architecture.md](dma_architecture.md) for DMA slot timing.

---

## §5 — CIA Register Access (`$BFx000`)

The two CIA 8520 chips occupy a peculiar position in the Amiga's bus architecture. Unlike the custom chip registers (which are decoded by Agnus and respond at bus speed), the CIAs are **asynchronous peripherals** clocked by the E-clock — the slowest clock in the system.

### Byte-Lane Placement

The CIAs are 8-bit devices on a 16-bit data bus. Their placement on the bus lanes is asymmetric:

| CIA | Base Address | Data Bus Connection | Access Size |
|---|---|---|---|
| **CIA-A** | `$BFE001` | **Odd byte lane** (D0–D7, `/LDS`) | `MOVE.B` to odd addresses |
| **CIA-B** | `$BFD000` | **Even byte lane** (D8–D15, `/UDS`) | `MOVE.B` to even addresses |

```asm
; ✓ Reading CIA-A PRA (parallel port data)
    MOVE.B  $BFE001,D0          ; CIA-A at odd address

; ✓ Reading CIA-B PRB
    MOVE.B  $BFD000,D0          ; CIA-B at even address

; ✗ WRONG — word read spans both CIAs!
    MOVE.W  $BFD000,D0          ; Reads CIA-B high byte AND CIA-A low byte simultaneously
                                 ; This is a famous source of bugs!
```

> [!WARNING]
> **Never use `MOVE.W` or `MOVE.L` on CIA addresses.** A word read at `$BFD000` reads CIA-B's register on the high byte and CIA-A's register on the low byte simultaneously — potentially triggering unintended side effects (like clearing an ICR flag on the other CIA).

### E-Clock Synchronization

The CIAs are clocked by the **E-clock** — the 68000's slowest bus signal, running at the CPU clock ÷ 10:

| Parameter | PAL | NTSC |
|---|---|---|
| E-clock frequency | 709.379 kHz | 715.909 kHz |
| E-clock period | ~1.41 µs | ~1.40 µs |
| CIA access time | 6 E-cycles ≈ **8.4 µs** | 6 E-cycles ≈ **8.4 µs** |

A CIA register access requires the CPU to wait for the E-clock to reach the correct phase, then hold the bus for 6 full E-clock cycles. This makes CIA access the **slowest bus operation** on the Amiga — roughly **15× slower** than a Chip RAM access:

```
CIA access:   ~8,400 ns  (6 E-cycles)
Chip RAM:     ~564 ns    (4 CPU clocks, best case)
Fast RAM:     ~40–80 ns  (accelerated, zero wait)
```

On an accelerated system, the penalty is even more extreme. A 50 MHz 68060 can execute ~400 instructions in the time one CIA register read takes.

### ICR Read-and-Clear Semantics

The CIA Interrupt Control Register (ICR) at offset `$0D` uses **read-and-clear** semantics:

- **Reading** ICR returns the current interrupt flags **and clears them atomically**
- **Writing** ICR with bit 7 = 1 sets the specified interrupt enable bits
- **Writing** ICR with bit 7 = 0 clears the specified interrupt enable bits

This means you cannot "poll" the ICR without consuming the flags. Code that reads ICR must process all returned flags in that read — a second read will return zero.

```asm
; Read and process CIA-A ICR
    MOVE.B  $BFED01,D0          ; Read ICR — flags cleared atomically
    BTST    #0,D0               ; Timer A underflow?
    BNE     .handle_timer_a
    BTST    #2,D0               ; TOD alarm?
    BNE     .handle_tod
```

For complete CIA register semantics, see [cia_chips.md](cia_chips.md). For the E-clock's derivation from the video crystal, see [video_timing.md §2](video_timing.md#2--the-clock-tree).

---

## §6 — The Accelerator Bus Bridge

When a 68030/040/060 accelerator is installed, the original 68000 is removed and the accelerator takes over the CPU socket. But the motherboard hardware — Chip RAM, custom registers, CIAs, ROM — still runs at 7 MHz. The **bus adapter** (also called the bridge or glue logic) is the hardware that translates between the two clock domains.

### The Arbitration Sequence

When the accelerated CPU needs to access a motherboard resource:

```
                  Accelerator                     Motherboard
                  ──────────                      ───────────
    1. CPU issues address     ──────────────►
    2. Bridge detects motherboard target
    3. Bridge asserts /BR      ──────────────►    Bus Request
    4.                         ◄──────────────    /BG (Bus Grant)
    5. Bridge asserts /BGACK   ──────────────►    Bus Grant Acknowledge
    6. Bridge waits for next 7 MHz clock phase
    7. Bridge drives address/data on motherboard bus
    8.                         ◄──────────────    Target asserts /DTACK
    9. Bridge relays data back to CPU
   10. Bridge releases /BGACK  ──────────────►    Bus released
```

Steps 3–6 are the **sync-up penalty** — the CPU is frozen (via `/DSACK` or `/STERM` withholding) while the bridge waits for the motherboard's clock phase alignment. This penalty varies from 2 to 8+ motherboard clocks depending on where in the 7 MHz cycle the request arrives.

### The Bridge as a Speed Limiter

The bridge doesn't make motherboard access faster — it makes it **not slower than the motherboard's native speed**. But from the accelerated CPU's perspective, the penalty is enormous because the CPU could have executed many instructions from Fast RAM in the same time:

| CPU | Clock | Fast RAM Access | Chip RAM Access | Penalty Ratio |
|---|---|---|---|---|
| 68000 (stock) | 7 MHz | N/A | ~564 ns | 1× (baseline) |
| 68020 (A1200) | 14 MHz | ~140 ns | ~564 ns | ~4× |
| 68030 @ 25 MHz | 25 MHz | ~80 ns | ~700 ns | ~9× |
| 68030 @ 50 MHz | 50 MHz | ~40 ns | ~700 ns | ~18× |
| 68040 @ 25 MHz | 25 MHz | ~40 ns (burst) | ~800 ns | ~20× |
| 68060 @ 50 MHz | 50 MHz | ~20 ns (burst) | ~800 ns | ~40× |

> [!IMPORTANT]
> The Chip RAM access time doesn't improve with a faster CPU — it's fixed by the motherboard clock. Only the *penalty ratio* increases because the CPU can do more useful work per nanosecond from Fast RAM.

### Per-CPU Bridge Differences

**68020/030 adapters** have a relatively straightforward bridge because the 68020/030 bus protocol is similar to the 68000's. The main challenges are:
- Dynamic bus sizing (32-bit CPU ↔ 16-bit motherboard)
- Cache line fills from motherboard (burst mode negotiation)
- Address bit translation (24-bit vs. 32-bit)

**68040/060 adapters** require much more complex bridge logic because:
- The 68040/060 bus protocol is fundamentally different (no dynamic bus sizing, burst-only transfers, separate PCLK/BCLK)
- The copyback data cache may hold modified data that DMA hardware needs — the bridge must snoop or flush
- `MOVE16` cache-line push instructions generate 16-byte burst transfers that must be broken into motherboard-sized chunks
- The 68060 adds superscalar execution and branch prediction, making the CPU even more sensitive to stalls

### What the CPU "Sees"

From the CPU's perspective, a Chip RAM access looks like a very long wait state:

```
50 MHz 68060 executing from Fast RAM:
    MOVE.L  (A0),D0     ; A0 points to Fast RAM → 1 cycle = 20 ns
    MOVE.L  (A1),D1     ; A1 points to Chip RAM → ~40 cycles = 800 ns ← CPU frozen here
    ADD.L   D0,D1       ; 1 cycle = 20 ns
```

The CPU doesn't "know" it's crossing a clock domain — it simply sees `/DSACK` being withheld for many cycles. The bridge is invisible to software, which is why the same binary runs on stock and accelerated systems. The only difference is *speed*.

---

## §7 — Cache Coherency with DMA

When the CPU has a data cache, a dangerous situation arises: the CPU may hold a cached copy of Chip RAM data that has been modified by DMA hardware (Blitter, disk DMA), or the CPU may modify cached Chip RAM data that DMA hardware expects to read. This is the **cache coherency problem** — the cache and main memory disagree about the current state of data.

### Per-CPU Cache Characteristics

| CPU | Data Cache | Write Policy | Bus Snooping | Coherency Strategy |
|---|---|---|---|---|
| **68000** | None | N/A | N/A | No problem — all accesses go to RAM |
| **68020** | 256-byte instruction cache | N/A | N/A | No data cache — no coherency issue |
| **68030** | 256-byte data + 256-byte inst. | Write-through | None | Software must **invalidate** after DMA writes |
| **68040** | 4 KB data + 4 KB inst. | Copyback | Optional (often not wired) | Software must **flush** before DMA reads, **invalidate** after DMA writes |
| **68060** | 8 KB data + 8 KB inst. | Copyback + store buffer | Optional (rarely wired) | Same as 68040, plus store buffer drain |

### The Problem in Practice

```
Scenario: CPU writes a new Copper list to Chip RAM, then triggers Copper restart

CPU cache (copyback):     Contains modified Copper list data
Chip RAM (main memory):   Contains STALE Copper list data
Copper DMA reads from:    Chip RAM (not the CPU cache!)

Result: Copper executes the OLD list → display corruption
```

### The AmigaOS Solution: CachePreDMA / CachePostDMA

AmigaOS provides two exec functions for DMA-safe memory access:

```c
/* Before DMA device reads from memory (Blitter source, display, audio) */
CachePreDMA(address, &length, DMA_ReadFromRAM);
/* → Flushes CPU data cache for the specified range
      so DMA reads the latest data from RAM */

/* After DMA device writes to memory (Blitter dest, disk read) */
CachePostDMA(address, &length, DMA_ReadFromRAM);
/* → Invalidates CPU data cache for the specified range
      so CPU reads the updated data from RAM, not stale cache */
```

### When to Flush vs. Invalidate

| Scenario | Action | Function | Why |
|---|---|---|---|
| Before Blitter reads source | **Flush** (push dirty cache lines to RAM) | `CachePreDMA()` | Blitter must see latest CPU-written data |
| Before audio DMA plays sample | **Flush** | `CachePreDMA()` | Paula must read correct sample data |
| Before Copper executes list | **Flush** | `CachePreDMA()` | Copper reads from RAM, not cache |
| After Blitter writes destination | **Invalidate** (discard cached copies) | `CachePostDMA()` | CPU must see Blitter's output, not stale cache |
| After disk DMA loads data | **Invalidate** | `CachePostDMA()` | CPU must see disk data, not old cache content |
| After network DMA receives packet | **Invalidate** | `CachePostDMA()` | CPU must see received data |

### The Nuclear Option: CacheClearU / CacheClearE

For simpler cases (or legacy code), exec provides brute-force cache management:

```c
CacheClearU();                           /* Flush + invalidate ALL caches */
CacheClearE(address, length, CACRF_ClearD | CACRF_ClearI);  /* Flush + invalidate specific range */
```

`CacheClearU()` is expensive — it flushes the entire data cache, losing all cached Fast RAM data. Use `CacheClearE()` with a specific range when possible.

> [!WARNING]
> **Games that "take over the system"** must still manage caches if they run on 68040/060. A common pattern is to disable the data cache entirely (`CacheControl(0, CACRF_EnableD)`) or set all Chip RAM as cache-inhibited via the MMU. Both approaches sacrifice performance but guarantee coherency.

### Hardware Registers and Caching

Custom chip registers at `$DFF000` and CIA registers at `$BFx000` must **never be cached**. On 68040/060, these address ranges are mapped as **cache-inhibited, serialized (CI/S)** in the MMU translation tables. This ensures:

- Every read goes to the hardware register, not a cached copy
- Every write is immediately driven to the bus
- Access order is strictly maintained (no write buffer reordering)

The Kickstart ROM's MMU setup handles this automatically. Custom MMU tables must preserve these mappings.

---

## §8 — Cross-Domain Transfer Techniques

The most performance-critical operation on an accelerated Amiga is moving data between **Fast RAM** (where the CPU works efficiently) and **Chip RAM** (where DMA hardware needs it). Every screen update, every audio buffer fill, and every Blitter setup involves this cross-domain transfer.

### The Fundamental Constraint

The Chip RAM bus runs at ~7 MHz with a 16-bit data path. No software technique can exceed the bus's raw throughput ceiling:

```
Maximum Chip RAM bandwidth:
  16 bits × 7.09 MHz = ~14.2 MB/s (theoretical, all slots to one master)
  CPU share (typical):  ~3.5 MB/s (half the slots, rest to DMA)
  CPU share (heavy display): ~0.5–1 MB/s (most slots consumed by DMA)
```

All transfer techniques operate within this ceiling. The goal is to **reach** the ceiling efficiently, not exceed it.

### Transfer Method Comparison

All figures are relative to a baseline `MOVE.W` loop on a 68000 (= 1.0×). Higher is faster. Actual throughput depends on DMA load, CPU model, and alignment.

| Method | Relative Speed | Alignment Req. | CPU Occupied? | Works Fast↔Chip? | Notes |
|---|---|---|---|---|---|
| `MOVE.W` loop | **1.0×** (baseline) | Word | Yes | Yes | Simplest, slowest |
| `MOVE.L` loop | **~1.8×** | Long | Yes | Yes | Two words per instruction; fewer loop iterations |
| `MOVEM.L` (unrolled) | **~2.5×** | Long | Yes | Yes | Moves up to 14 registers (56 bytes) per instruction |
| `MOVE16` (68040+) | **~3.5×** | 16-byte aligned | Yes | Yes | 16-byte cache-line burst; best for 040/060 |
| `CopyMem()` | **~2.0–2.5×** | Any | Yes | Yes | Library function; uses best available method internally |
| `CopyMemQuick()` | **~2.5×** | Long | Yes | Yes | Optimized path; requires longword-aligned src/dest/size |
| **Blitter** | **~2.0×** (A channel copy) | Word | **No** (CPU free) | **Chip↔Chip only** | CPU can work Fast RAM in parallel |

> [!IMPORTANT]
> The Blitter **cannot** access Fast RAM. It only copies within Chip RAM. Its advantage is freeing the CPU to do other work in Fast RAM while the copy proceeds in parallel. On a stock 68000, the Blitter is faster than the CPU for large copies; on 68030+, the CPU with `MOVEM.L` is often faster, but the parallelism benefit remains.

### Optimal Transfer Patterns

**Pattern 1: MOVEM.L — The Workhorse**

```asm
; Copy 256 bytes from Fast RAM (A0) to Chip RAM (A1)
; Uses 12 data/address registers = 48 bytes per pair of MOVEM instructions
    MOVEM.L (A0)+,D0-D7/A2-A5   ; Load 48 bytes from Fast RAM (fast)
    MOVEM.L D0-D7/A2-A5,(A1)    ; Store 48 bytes to Chip RAM (slow — bus limited)
    LEA     48(A1),A1
    ; ... repeat for remaining 208 bytes (4 more iterations + remainder)
```

The load from Fast RAM completes at full CPU speed. The store to Chip RAM is bottlenecked by the 7 MHz bus — but `MOVEM.L` minimizes instruction fetch overhead by moving 48 bytes per instruction pair.

**Pattern 2: MOVE16 — The 68040/060 Burst**

```asm
; Copy 64 bytes using cache-line burst transfers (68040/060 only)
; Source and destination MUST be 16-byte aligned
    MOVE16  (A0)+,(A1)+          ; 16 bytes in one burst cycle
    MOVE16  (A0)+,(A1)+          ; 16 bytes
    MOVE16  (A0)+,(A1)+          ; 16 bytes
    MOVE16  (A0)+,(A1)+          ; 16 bytes (64 bytes total)
```

`MOVE16` bypasses the data cache and performs a 16-byte line transfer directly on the bus. On 68040/060 with proper Chip RAM alignment, this is the fastest CPU-driven method.

> [!WARNING]
> `MOVE16` requires **16-byte alignment** on both source and destination. Misaligned addresses cause an Address Error exception. The instruction is not available on 68000/020/030.

**Pattern 3: CPU + Blitter Pipeline**

The most efficient approach combines both engines:

```
1. CPU renders frame data in Fast RAM         (full CPU speed)
2. CPU converts chunky→planar (C2P) in Fast RAM  (full CPU speed)
3. CPU copies planar result to Chip RAM buffer    (slow — bus limited)
4. Blitter copies within Chip RAM for scrolling   (parallel — CPU free)
5. CPU begins next frame in Fast RAM              (while Blitter works)
```

This **double-buffered pipeline** keeps both the CPU and Blitter busy simultaneously. The CPU never waits for the Blitter, and the Blitter never waits for the CPU. Games like Doom (Amiga port) use exactly this pattern.

### Audio Streaming: The Ping-Pong Buffer

Audio data follows a similar cross-domain pattern:

```
Fast RAM:   Decode/decompress audio (MP3, MOD, etc.) at CPU speed
            ↓ Copy decoded PCM samples
Chip RAM:   Two small DMA buffers (ping/pong), each ~1–4 KB
            Paula DMA plays from buffer A
            CPU fills buffer B from decoded data in Fast RAM
            At interrupt: swap A↔B, repeat
```

The key insight: only the small DMA buffers (~8 KB total) consume Chip RAM. The bulk audio data and decompression workspace live in Fast RAM. See [memory_types.md](memory_types.md) for allocation strategy.

---

## §9 — Peripheral Address Spaces & Per-Model Maps

The Amiga's address space is not static — expansion cards, system controllers, and PCI bridges dynamically insert address windows into the memory map. This section provides annotated per-model maps showing where these windows appear.

### A500 / A2000 — The 24-bit Baseline

```
$000000 ┌──────────────────────────────────┐
        │ Chip RAM (512 KB – 2 MB)         │  DMA-visible
$080000 │ (mirror/wrap if < 2 MB)          │
$200000 ├──────────────────────────────────┤
        │ ◆ Zorro II Fast RAM              │  AutoConfig-assigned (up to 8 MB)
        │   Populated by expansion cards   │  Cards: A2058, A2091, GVP, etc.
$A00000 ├──────────────────────────────────┤
        │ ◆ Zorro II I/O Space             │  Board registers, RTG framebuffers
$BFD000 ├──────────────────────────────────┤
        │ CIA-B ($BFD000, even bytes)      │  E-clock synchronous
$BFE001 │ CIA-A ($BFE001, odd bytes)       │  E-clock synchronous
$C00000 ├──────────────────────────────────┤
        │ Slow RAM (512 KB, trapdoor)      │  On Chip bus, NOT DMA-visible
$C80000 ├──────────────────────────────────┤
        │ ◆ Zorro II I/O (extended)        │  More expansion board registers
$DC0000 ├──────────────────────────────────┤
        │ Real-Time Clock (MSM6242B)       │
$DFF000 ├──────────────────────────────────┤
        │ Custom Chip Registers            │  $DFF000–$DFF1FE (Agnus/Denise/Paula)
$E00000 ├──────────────────────────────────┤
        │ Kick mirror / WCS                │
$E80000 ├──────────────────────────────────┤
        │ ◆ AutoConfig Probe Space         │  Temporary: boards appear here
        │   before relocation              │  during CFGIN/CFGOUT enumeration
$F00000 ├──────────────────────────────────┤
        │ Extended Kickstart ROM (OS 3.1+) │
$F80000 ├──────────────────────────────────┤
        │ Kickstart ROM (512 KB)           │
$FFFFFF └──────────────────────────────────┘
```

**◆** = dynamically populated by AutoConfig or expansion hardware.

### A3000 / A4000 — 32-bit Extension

```
$00000000 ┌──────────────────────────────────┐
          │ (24-bit map as above)            │  Identical $000000–$FFFFFF
$00FFFFFF ├──────────────────────────────────┤
          │ ◆ Zorro III Address Space        │  32-bit, AutoConfig
          │   Fast RAM cards (32–256 MB)     │  e.g., CyberStorm, Fastlane
          │   I/O boards (RTG, SCSI, Net)    │  e.g., CyberVision, Ariadne
          │   Assigned by expansion.library  │
$07FFFFFF ├──────────────────────────────────┤
          │ (unused/reserved)                │
          │                                  │
          │ ◆ PCI Bridge Windows (if present)│  Mediator: 8 MB window
          │   Mapped into Z3 space           │  G-REX: linear via CPU slot
$FFFFFFFF └──────────────────────────────────┘
```

On A3000/A4000, Ramsey manages on-board Fast RAM (up to 16 MB, separately from Zorro III cards). Buster (rev 11) handles Zorro III DMA and burst negotiation.

### A600 — ECS Compact

```
$000000 ┌──────────────────────────────────┐
        │ Chip RAM (1–2 MB)                │  DMA-visible (ECS Agnus)
$200000 ├──────────────────────────────────┤
        │ (No Zorro slots)                 │
$600000 ├──────────────────────────────────┤
        │ ◆ PCMCIA Attribute/I/O Memory    │  4 MB window
        │   CompactFlash, network cards    │  (Gayle-managed)
$A00000 ├──────────────────────────────────┤
        │ CIA-B, CIA-A, Slow RAM           │  (standard layout)
$DA0000 ├──────────────────────────────────┤
        │ ◆ Gayle IDE Registers            │  Internal 2.5" IDE
$DFF000 ├──────────────────────────────────┤
        │ Custom Registers, ROM            │  (standard layout)
$FFFFFF └──────────────────────────────────┘
```

### A1200 — AGA with Trapdoor Expansion

```
$000000 ┌──────────────────────────────────┐
        │ Chip RAM (2 MB, fixed)           │  DMA-visible (Alice)
$200000 ├──────────────────────────────────┤
        │ ◆ Accelerator Fast RAM           │  Trapdoor connector (150-pin)
        │   Mapped by accelerator bridge   │  Blizzard 1230/1260, TF1260, etc.
        │   Typically $200000–$5FFFFF      │  (4 MB PCMCIA-friendly)
        │   or $200000–$07FFFFFF           │  (up to 126 MB, disables PCMCIA)
$600000 ├──────────────────────────────────┤
        │ ◆ PCMCIA Window                  │  4 MB ($600000–$9FFFFF)
        │   Conflicts with Fast >4 MB!     │  Gayle-managed
$A00000 ├──────────────────────────────────┤
        │ CIA-B, CIA-A                     │  (standard layout)
$DA0000 ├──────────────────────────────────┤
        │ ◆ Gayle IDE Registers            │  Internal 2.5" IDE + CF adapter
$DA4000 │ ◆ PCMCIA Attribute Memory        │  Card configuration registers
$DFF000 ├──────────────────────────────────┤
        │ Custom Registers (AGA)           │  Alice/Lisa extended register set
$F00000 ├──────────────────────────────────┤
        │ Extended + Primary Kickstart ROM │
$FFFFFF └──────────────────────────────────┘
```

> [!WARNING]
> **The PCMCIA/Fast RAM conflict:** On the A1200, PCMCIA maps to `$600000`–`$9FFFFF`. Accelerators that place Fast RAM above 4 MB overlap this window and **permanently disable PCMCIA** (no CF card, no network). Most modern accelerators offer a "PCMCIA-friendly" jumper that limits Fast RAM to 4 MB.

### CD32 — AGA Console with Akiko

```
$000000 ┌──────────────────────────────────┐
        │ Chip RAM (2 MB, fixed)           │  DMA-visible (Alice)
$200000 ├──────────────────────────────────┤
        │ (No expansion bus)               │
$B80000 ├──────────────────────────────────┤
        │ ◆ Akiko Chip                     │  Chunky-to-Planar engine
        │   CD-ROM controller              │  1 KB NVRAM interface
$DFF000 ├──────────────────────────────────┤
        │ Custom Registers (AGA)           │
$E00000 ├──────────────────────────────────┤
        │ CD32 Extended ROM                │  CD filesystem, CDDA player
$F00000 ├──────────────────────────────────┤
        │ CD32 Flash ROM                   │  Firmware, SysInfo
$F80000 ├──────────────────────────────────┤
        │ Kickstart 3.1 ROM                │
$FFFFFF └──────────────────────────────────┘
```

### PCI Bridge Address Windowing

PCI cards have a 4 GB address space, but the Amiga's native bus can only address 16 MB (24-bit) or 4 GB (32-bit). PCI bridges solve this mismatch differently:

| Bridge | Technique | Window Size | Performance |
|---|---|---|---|
| **Mediator** (Elbox) | Memory windowing: 8 MB window in Zorro III space; driver swaps visible region via bank register | 8 MB visible at a time | ~20–30 MB/s (window-switching overhead) |
| **G-REX** (DCE) | Linear mapping via CPU local bus (CyberStorm/Blizzard PPC): entire PCI space directly addressable | Full 4 GB | ~60–80 MB/s (no windowing overhead) |
| **Prometheus** | PLX bridge chip, single Zorro III window | Varies | ~10–15 MB/s |

The **Mediator windowing** works like a bank-switching scheme: the driver writes a bank register to select which 8 MB slice of PCI memory is visible in the Zorro III window. Accessing a different region requires a register write to switch banks — this adds latency for scattered access patterns but works transparently for contiguous operations like framebuffer blits.

For PCI card compatibility and driver details, see [zorro_bus.md](zorro_bus.md). For AutoConfig protocol mechanics, see [autoconfig.md](autoconfig.md). For detailed address space semantics, see also [address_space.md](address_space.md).

---

## §10 — Best Practices & Hazards

### Register Access Quick Reference

| Target | Access Size | Alignment | Volatility | Special Rules |
|---|---|---|---|---|
| Custom chip ($DFF000) | **Word only** | 2-byte | `volatile` required in C | No `CLR`; no byte access; long-word OK for register pairs |
| CIA-A ($BFE001) | **Byte only** | Odd addresses | `volatile` required | E-clock sync; ICR is read-and-clear |
| CIA-B ($BFD000) | **Byte only** | Even addresses | `volatile` required | E-clock sync; never word-read CIA region |
| Chip RAM | Any | 2-byte for 68000 | Not needed (memory) | DMA-visible; may cause wait states under DMA load |
| Fast RAM | Any | Any (4-byte preferred) | Not needed | CPU-only; zero DMA contention |
| Zorro II I/O | Word/Long | Card-dependent | `volatile` required | 16-bit bus; auto-sized on 32-bit CPU |
| Zorro III I/O | Long preferred | 4-byte | `volatile` required | 32-bit bus; burst-capable |
| IDE (Gayle) | Word | 2-byte | `volatile` required | PIO timing requirements |

### Memory Placement Strategy

For maximum throughput, place data according to how it will be consumed:

| Data Type | Place In | Why |
|---|---|---|
| Display bitplanes | **Chip RAM** (mandatory) | Denise/Lisa DMA can only read Chip RAM |
| Copper lists | **Chip RAM** (mandatory) | Copper DMA reads from Chip RAM |
| Audio samples (DMA buffers) | **Chip RAM** (mandatory) | Paula DMA reads from Chip RAM |
| Sprite data | **Chip RAM** (mandatory) | Sprite DMA reads from Chip RAM |
| Blitter source/dest | **Chip RAM** (mandatory) | Blitter can only access Chip RAM |
| Program code | **Fast RAM** (preferred) | Executes at full CPU speed |
| Variables, stack | **Fast RAM** (preferred) | No DMA contention |
| Audio decode workspace | **Fast RAM** | Decompress at CPU speed, copy to Chip buffer |
| 3D rendering buffer | **Fast RAM** | Render at CPU speed, C2P to Chip for display |
| File I/O buffers | **Any** (`MEMF_ANY`) | Let OS decide based on availability |

### Cache Management Checklist

For 68040/060 systems:

1. **Before starting DMA that reads Chip RAM** → `CachePreDMA()` or `CacheClearE()` with `CACRF_ClearD`
2. **After DMA that writes Chip RAM** → `CachePostDMA()` or `CacheClearE()` with `CACRF_ClearD`
3. **After loading code into RAM** → `CacheClearE()` with `CACRF_ClearI` (instruction cache invalidation)
4. **Hardware register regions** → ensure MMU maps `$DFF000` and `$BFx000` as cache-inhibited, serialized
5. **When in doubt** → `CacheClearU()` (expensive but safe)

### Common Antipatterns

| Antipattern | Problem | Fix |
|---|---|---|
| `CLR.W $DFF09C` | Read-modify-write reads the strobe register | Use `MOVE.W #0,$DFF09C` |
| `MOVE.W $BFD000,D0` | Word read hits both CIA-A and CIA-B simultaneously | Use `MOVE.B` with correct address |
| `MOVE.B #x,$DFF180` | Byte write to 16-bit custom register | Use `MOVE.W` |
| Blitter source in Fast RAM | Blitter cannot access Fast RAM → silent garbage or hang | Allocate source with `MEMF_CHIP` |
| No cache flush before display DMA | 68040/060 shows stale data on screen | `CachePreDMA()` before Copper restart |
| `MOVE16` to odd alignment | Address Error exception on 68040/060 | Ensure 16-byte alignment on both operands |
| Polling CIA ICR in a loop | Each read clears the flags — second read returns 0 | Save ICR value, process all flags from one read |
| DMA to Fast RAM (e.g., `AllocMem(MEMF_FAST)` for audio buffer) | Paula, Blitter, Denise cannot reach Fast RAM | Use `MEMF_CHIP` for all DMA buffers |

---

## §11 — References & See Also

### Companion Articles

| Article | Relationship |
|---|---|
| [address_space.md](address_space.md) | Memory map tables (where things are) — this article covers *how the bus reaches them* |
| [memory_types.md](memory_types.md) | Chip/Fast/Slow classification, MEMF flags — this article covers *the physical transfer mechanics* |
| [dma_architecture.md](dma_architecture.md) | DMA slot scheduling and bandwidth — this article covers *CPU bus cycles and register access* |
| [video_timing.md](video_timing.md) | Clock tree, video signal timing — this article covers *how those clocks drive bus cycles* |
| [autoconfig.md](autoconfig.md) | AutoConfig protocol and board enumeration |
| [zorro_bus.md](zorro_bus.md) | Zorro II/III specifications, PCI bridge card catalog |
| [Gary (OCS)](../ocs_a500/gary_system_controller.md) | Detailed address decode logic and bus timeout |
| [Fat Gary (ECS)](../ecs_a600_a3000/gary_system_controller.md) | 32-bit decode, SCSI, Zorro III glue |
| [cia_chips.md](cia_chips.md) | CIA register semantics, timer programming |

### Primary Sources

- **Amiga Hardware Reference Manual (HRM)** — Chapters 1 (System Overview), 7 (Appendix D: Hardware), Appendix B (Custom Registers)
- **MC68000 User's Manual** — Chapter 5 (Signal Description), Chapter 6 (Bus Operation)
- **MC68040 User's Manual** — Chapter 7 (Bus Operation), Chapter 8 (Cache)
- **MC68060 User's Manual** — Chapter 7 (Bus Operation), Chapter 8 (Cache), Chapter 12 (MOVE16)
- **Amiga ROM Kernel Reference Manual: Libraries** — exec.library cache functions
- **MOS 8520 CIA Datasheet** — Timing specifications, ICR operation
