[← Home](../../README.md) · [Hardware](../README.md) · [OCS](README.md)

# Paula — Audio DMA

## Overview

**Paula** (MOS 8364) provides four independent audio DMA channels (0–3), corresponding to the four hardware voice outputs:

| Channel | Stereo Output |
|---|---|
| 0 | Left |
| 1 | Right |
| 2 | Right |
| 3 | Left |

Each channel has its own DMA pointer, length, period (pitch), and volume registers. Paula fetches sample data from **Chip RAM** automatically at the rate set by the period register.

## Audio Registers Per Channel

Channel `n` (n = 0–3) registers at `$DFF0A0 + n×$10`:

| Offset | Name | Description |
|---|---|---|
| +$00/$01 | AUDnLCH/AUDnLCL | Sample pointer high/low (Chip RAM address) |
| +$04 | AUDnLEN | Sample length in words (not bytes) |
| +$06 | AUDnPER | Period — clock divider for playback rate |
| +$08 | AUDnVOL | Volume: 0–64 (0 = silent, 64 = full) |
| +$0A | AUDnDAT | Current sample word (direct, for non-DMA mode) |

## Sample Playback Rate

Paula derives playback rate from the system clock divided by the period register:

```
Sample rate (Hz) = System clock / Period
```

| System | Clock | Period for 8363 Hz | Period for 22050 Hz |
|---|---|---|---|
| PAL | 3,546,895 Hz | 428 | ~161 |
| NTSC | 3,579,545 Hz | 428 | ~162 |

> **8363 Hz** is the standard MOD tracker reference — period 428 on PAL plays middle-A at exactly 8363 Hz.

Period range: 124–65535 (minimum period = maximum frequency ≈ 28 kHz PAL).

## Starting Audio DMA

```asm
; Load channel 0 with sample at SampleData, length 256 words
move.l  #SampleData, d0
move.w  d0, AUD0LCL+custom
swap    d0
move.w  d0, AUD0LCH+custom
move.w  #256, AUD0LEN+custom    ; 256 words = 512 bytes
move.w  #428, AUD0PER+custom    ; period 428 = 8287 Hz PAL
move.w  #64,  AUD0VOL+custom    ; full volume

; Enable audio DMA for channel 0
move.w  #$8201, DMACON+custom   ; SET + MASTER + AUD0EN

; Enable audio interrupt (optional)
move.w  #$A080, INTENA+custom   ; SET + INTEN + AUD0
```

## ADKCON — Audio/Disk Control

| Bit | Name | Description |
|---|---|---|
| 15 | SET/CLR | Write: 1=set, 0=clear bits |
| 11 | PRECOMP1 | Disk precompensation |
| 10 | PRECOMP0 | Disk precompensation |
| 9 | MFMPREC | MFM precompensation |
| 7 | MSBSYNC | Audio sync from MSB |
| 6 | WORDSYNC | Disk word sync enable |
| 4 | ATPER | Channel 3 period from channel 2 data |
| 3 | ATVOL | Channel 3 volume from channel 2 data |
| 2 | ATPER2 | Channel 1 period from channel 0 data |
| 1 | ATVOL2 | Channel 1 volume from channel 0 data |
| 0 | (unused) | |

`ATPER`/`ATVOL` bits enable **audio modulation** — channel N's period/volume is modulated by the sample data of channel N-1. Used for AM synthesis effects (e.g., in many MOD players for 8-channel soft mixing).

## Interrupt Handling

Audio channels raise interrupts when their DMA pointer wraps to the beginning of the next buffer:

```
INTENA/INTREQ bits:
AUD0 = bit 7  (IPL 4)
AUD1 = bit 8  (IPL 4)
AUD2 = bit 9  (IPL 4)
AUD3 = bit 10 (IPL 4)
```

The interrupt fires when the channel has consumed its buffer and reloaded the pointer from the DMA registers. At this point, software can update AUDnLCH/L and AUDnLEN with the next buffer.

## Double-Buffering Pattern

```c
/* In interrupt handler (IPL 4 server for AUD0): */
void audio_interrupt(void)
{
    /* Swap buffers */
    UWORD *next = (active_buf == buf_a) ? buf_b : buf_a;
    active_buf = next;

    /* Load next buffer address */
    custom.aud[0].ac_ptr = (UWORD *)next;
    custom.aud[0].ac_len = BUF_WORDS;
}
```

## Direct (Non-DMA) Audio

For simple sound effects without DMA overhead, write directly to `AUDnDAT`:
```asm
move.w  #$0080, AUD0VOL+custom   ; volume 64 (approx)
move.w  #$7FFF, AUD0DAT+custom   ; max positive sample
```
This only produces a single sample word — not practical for continuous audio but useful for one-shot clicks/beeps.

## audio.device

AmigaOS provides `audio.device` for arbitrated, multi-application audio access:
- Allocates channels (bitmask: `{1,2,4,8}`)
- Creates `IOAudio` request, uses standard device I/O (`BeginIO`/`WaitIO`)
- Handles period, volume, sample pointer, cycle count
- See [10_devices/audio_device.md](../../10_devices/audio_device.md) for full API reference

## References

- ADCD 2.1 Hardware Manual — Paula audio chapter
- NDK39: `hardware/custom.h` (struct AudChannel), `devices/audio.h`
- Autodocs: audio.device — http://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0081.html
