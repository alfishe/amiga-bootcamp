[← Home](../README.md) · [Toolchain](README.md)

# FD/SFD Files — Function Definition Format and LVO Generation

## Overview

**FD files** (Function Definition files) are the machine-readable specification of a library's public API. They define every function's name, LVO offset, and register argument mapping. FD files are the **source of truth** for generating pragma files, inline headers, and IDA LVO scripts.

---

## File Location

```
NDK:fd/exec_lib.fd
NDK:fd/dos_lib.fd
NDK:fd/intuition_lib.fd
NDK:fd/graphics_lib.fd
NDK:sfd/exec_lib.sfd       (SFD = extended format with C prototypes)
```

---

## FD File Syntax

```
* "exec.library"
##base _SysBase
##bias 30
##public
Supervisor(userFunction)(A5)
ExitIntr()()
Schedule()()
Reschedule()()
Switch()()
Dispatch()()
Exception()()
InitCode(startClass,version)(D0,D1)
InitStruct(initTable,memory,size)(A1,A2,D0)
MakeLibrary(funcInit,structInit,libInit,dataSize,segList)(A0,A1,A2,D0,D1)
MakeFunctions(target,functionArray,funcDispBase)(A0,A1,A2)
FindResident(name)(A1)
InitResident(resident,segList)(A1,D1)
Alert(alertNum)(D7)
Debug(flags)(D0)
##bias 120
Forbid()()
Permit()()
##bias 132
Disable()()
Enable()()
...
```

### Syntax Rules

| Element | Meaning |
|---|---|
| `* "name"` | Comment; library identity |
| `##base _Symbol` | Global base pointer symbol name |
| `##bias N` | Set current LVO offset to −N |
| `##public` | Following functions are public |
| `##private` | Following functions are private (reserved) |
| `FuncName(args)(regs)` | Function: name, C parameter names, register assignments |
| `##end` | End of file |

**LVO auto-increment:** After each function, the bias increases by 6 (one JMP instruction slot = 6 bytes).

---

## SFD File Format (Extended)

SFD adds full C prototypes:

```
==id $Id: exec_lib.sfd,v 1.0 2003/01/01 00:00:00 Exp $
==base _SysBase
==basetype struct ExecBase *
==libname exec.library
==bias 30
==public
APTR Supervisor(ULONG (*userFunction)()) (A5)
==end
```

---

## Parsing FD Files — Python Script

```python
#!/usr/bin/env python3
"""parse_fd.py — Parse AmigaOS FD files into LVO tables.

Usage: python3 parse_fd.py exec_lib.fd [--json] [--ida]
"""
import re, sys, json, argparse

def parse_fd(path):
    """Parse an FD file and return list of (offset, name, args, regs)."""
    funcs = []
    bias = 30
    public = True
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            if line.startswith('##base'):
                continue
            if line.startswith('##bias'):
                bias = int(line.split()[1])
                continue
            if line == '##public':
                public = True
                continue
            if line == '##private':
                public = False
                continue
            if line == '##end':
                break
            
            # Parse: FuncName(args)(regs)
            m = re.match(r'(\w+)\(([^)]*)\)\(([^)]*)\)', line)
            if m and public:
                name = m.group(1)
                args = [a.strip() for a in m.group(2).split(',') if a.strip()]
                regs = [r.strip() for r in m.group(3).split(',') if r.strip()]
                funcs.append({
                    'name': name,
                    'lvo': -bias,
                    'bias': bias,
                    'args': args,
                    'regs': regs
                })
            bias += 6  # always advance, even for private
    
    return funcs

def output_ida_script(funcs, base_name):
    """Generate IDA Python LVO dict."""
    print(f"# Auto-generated from FD file")
    print(f"LVO_{base_name} = {{")
    for f in funcs:
        print(f"    {f['lvo']:+5d}: \"{f['name']}\",")
    print("}")

def output_json(funcs):
    print(json.dumps(funcs, indent=2))

def output_table(funcs):
    print(f"{'LVO':>6}  {'Bias':>5}  {'Function':<30}  {'Registers'}")
    print(f"{'─'*6}  {'─'*5}  {'─'*30}  {'─'*30}")
    for f in funcs:
        regs = ', '.join(f['regs']) if f['regs'] else '(none)'
        print(f"{f['lvo']:>+6d}  {f['bias']:>5d}  {f['name']:<30}  {regs}")

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Parse AmigaOS FD files')
    ap.add_argument('fdfile', help='Path to .fd file')
    ap.add_argument('--json', action='store_true', help='Output JSON')
    ap.add_argument('--ida', action='store_true', help='Output IDA script')
    args = ap.parse_args()
    
    funcs = parse_fd(args.fdfile)
    if args.json:
        output_json(funcs)
    elif args.ida:
        output_ida_script(funcs, args.fdfile.split('/')[-1].replace('_lib.fd',''))
    else:
        output_table(funcs)
    
    sys.stderr.write(f"Parsed {len(funcs)} public functions\n")
```

---

## Where to Get NDK FD Files

| NDK | Source | FD path |
|---|---|---|
| NDK 3.9 | Aminet: `dev/misc/NDK39.lha` (free) | `NDK_3.9/Include/fd/` |
| NDK 3.2 | Hyperion (commercial, ~€30) | `NDK3.2/Include_H/fd/` |
| NDK 3.1 | Commodore (archived) | `NDK3.1/Include/fd/` |

---

## Auto-Generating IDA LVO Labels

```bash
# Generate IDA script from all FD files:
for fd in NDK_3.9/Include/fd/*_lib.fd; do
    python3 parse_fd.py "$fd" --ida >> all_lvos.py
done
```

Then in IDA: File → Script command → Run `all_lvos.py`

---

## References

- NDK39: `fd/` directory
- `05_reversing/static/api_call_identification.md` — using LVOs in RE
