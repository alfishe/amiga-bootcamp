[← Home](../README.md) · [Devices](README.md)

# gameport.device — Joystick and Mouse Ports

## Overview

`gameport.device` provides access to the Amiga's two **controller ports** (mouse/joystick). The hardware reads controller state through custom chip registers `JOY0DAT`/`JOY1DAT` and the CIA-A port for fire buttons. Understanding the hardware protocol is critical for FPGA cores.

---

## Hardware Registers

| Register | Address | Controller | Function |
|---|---|---|---|
| `JOY0DAT` | `$DFF00A` | Port 1 (mouse) | Quadrature-encoded position data |
| `JOY1DAT` | `$DFF00C` | Port 2 (joystick) | Direction bits or quadrature data |
| `JOYTEST` | `$DFF036` | Both | Write to set counter test value |
| `POTGO` | `$DFF034` | Both | Proportional/paddle port control |
| `POTGOR` | `$DFF016` | Both | Read paddle/proportional values |
| CIA-A PRA | `$BFE001` | Both | Fire buttons (active low) |

### JOYxDAT Bit Layout

```
Bits 15–8: Y counter (or vertical quadrature)
Bits 7–0:  X counter (or horizontal quadrature)
```

### Mouse Quadrature Decoding

For mouse input, the X/Y values are **quadrature counters** — they increment/decrement as the mouse moves:

```c
/* Read mouse delta: */
UWORD joy = custom->joy0dat;  /* current counter */
WORD dx = (WORD)(joy & 0xFF) - (WORD)(prev_joy & 0xFF);
WORD dy = (WORD)(joy >> 8) - (WORD)(prev_joy >> 8);
/* dx/dy = movement since last read (signed, wraps at 255→0) */
prev_joy = joy;
```

### Joystick Digital Decoding

For digital joysticks, the direction bits are encoded:

```c
UWORD joy = custom->joy1dat;
BOOL right = joy & 0x0002;
BOOL left  = (joy >> 1) ^ (joy & 0x0001);  /* XOR of bit 1 and bit 0 */
BOOL down  = joy & 0x0200;
BOOL up    = (joy >> 9) ^ ((joy >> 8) & 0x0001);

/* Fire button — from CIA-A: */
BOOL fire  = !(ciaa->ciapra & 0x80);  /* port 2 button, active low */
/* Port 1 fire = bit 6 of CIAA PRA */
```

> [!IMPORTANT]
> The joystick directional decoding uses **XOR** between adjacent bits — not direct reads. This is because the hardware shares the same quadrature interface used for mice. This is a common source of bugs in FPGA implementations.

### Fire Buttons

| Button | Register | Bit | Port |
|---|---|---|---|
| Port 1 fire (left mouse) | CIA-A PRA `$BFE001` | 6 | Mouse port |
| Port 2 fire (joystick) | CIA-A PRA `$BFE001` | 7 | Joystick port |
| Port 1 middle/right | POTGOR `$DFF016` | 8, 10 | Mouse port |
| Port 2 second button | POTGOR `$DFF016` | 12, 14 | Joystick port |

---

## Using gameport.device (OS Level)

```c
struct MsgPort *gpPort = CreateMsgPort();
struct IOStdReq *gpReq = (struct IOStdReq *)
    CreateIORequest(gpPort, sizeof(struct IOStdReq));

/* Open port 1 (joystick port): */
OpenDevice("gameport.device", 1, (struct IORequest *)gpReq, 0);

/* Set controller type: */
UBYTE type = GPCT_ABSJOYSTICK;
gpReq->io_Command = GPD_SETCTYPE;
gpReq->io_Data    = (APTR)&type;
gpReq->io_Length  = 1;
DoIO((struct IORequest *)gpReq);

/* Set trigger conditions: */
struct GamePortTrigger trigger;
trigger.gpt_Keys   = GPTF_UPKEYS | GPTF_DOWNKEYS;
trigger.gpt_Timeout = 0;   /* no timeout */
trigger.gpt_XDelta  = 1;   /* report on any movement */
trigger.gpt_YDelta  = 1;
gpReq->io_Command = GPD_SETTRIGGER;
gpReq->io_Data    = (APTR)&trigger;
gpReq->io_Length  = sizeof(trigger);
DoIO((struct IORequest *)gpReq);

/* Read events: */
struct InputEvent ie;
gpReq->io_Command = GPD_READEVENT;
gpReq->io_Data    = (APTR)&ie;
gpReq->io_Length  = sizeof(ie);
SendIO((struct IORequest *)gpReq);

/* Wait for joystick event: */
Wait(1L << gpPort->mp_SigBit);
WaitIO((struct IORequest *)gpReq);
/* ie now contains joystick movement/button data */
```

---

## Controller Types

| Constant | Value | Device |
|---|---|---|
| `GPCT_MOUSE` | 1 | Standard Amiga mouse |
| `GPCT_RELJOYSTICK` | 2 | Relative joystick (proportional) |
| `GPCT_ABSJOYSTICK` | 3 | Absolute/digital joystick |

---

## References

- NDK39: `devices/gameport.h`, `hardware/custom.h`, `hardware/cia.h`
- HRM: *Amiga Hardware Reference Manual* — Controller Ports chapter
- See also: [input.md](input.md) — input handler chain that receives gameport events
- See also: [keyboard.md](keyboard.md) — keyboard shares CIA-A interrupt infrastructure
