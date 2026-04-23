[← Home](../README.md) · [AmigaDOS](README.md)

# CLI and Shell — Command Interpreter

## Overview

The AmigaDOS **Shell** (called CLI in OS 1.x) is the command-line interface. It processes scripts, handles I/O redirection, pipes, and environment variable expansion. Understanding Shell internals is essential for writing scripts and understanding process creation.

---

## Shell vs CLI

| Feature | CLI (OS 1.x) | Shell (OS 2.0+) |
|---|---|---|
| Command history | No | Yes |
| Line editing | Minimal | Full (cursor keys, delete) |
| Pipes | No | Yes (`|` and `|&`) |
| Wildcards | Manual `#?` | Automatic in `Dir`, `List`, etc. |
| Resident commands | No | Yes (`Resident` command) |
| Background execution | `Run` only | `Run` + `&` suffix |

---

## I/O Redirection

```
; Redirect output to file:
Dir >RAM:listing.txt SYS:

; Redirect input from file:
Type <RAM:data.txt

; Append output:
Echo "log entry" >>RAM:log.txt

; Discard output:
Copy >NIL: file1 file2

; Redirect stderr (error output) — OS 2.0+:
command *>RAM:errors.txt
```

---

## Pipes

```
; Pipe output of one command to input of another:
List SYS:C | Sort | More

; Pipe both stdout and stderr:
command |& Filter
```

Pipes create temporary files in `T:` (assigned to `RAM:T`). Not true Unix-style byte streams.

---

## Script Execution

Scripts are text files executed line by line. Use `.` or `Execute`:

```
; Run a script:
Execute S:MyScript

; Or make executable and run directly (with Execute bit set):
Protect S:MyScript +s
S:MyScript
```

### Script Control Structures

```
; Conditional:
IF EXISTS SYS:Libs/68040.library
    Echo "68040 detected"
ELSE
    Echo "No 68040"
ENDIF

; Loop:
LAB loop
Echo "iteration"
SKIP loop

; Fail handling:
FailAt 21
Copy SYS:Missing RAM:
IF WARN
    Echo "Copy had warnings"
ENDIF
```

---

## ReadArgs — Argument Parsing

AmigaDOS provides `ReadArgs()` for standardised argument parsing:

```c
/* Template syntax: KEYWORD/A = required, /S = switch, /K = keyword,
   /N = numeric, /M = multi, /F = rest-of-line */
LONG args[4] = {0};
struct RDArgs *rd = ReadArgs("FROM/A,TO/A,ALL/S,BUFFER/K/N", args, NULL);
if (rd) {
    char *from = (char *)args[0];
    char *to   = (char *)args[1];
    BOOL all   = (BOOL)args[2];
    LONG *bufsize = (LONG *)args[3];
    FreeArgs(rd);
}
```

### Template Format

| Qualifier | Meaning | Example |
|---|---|---|
| `/A` | Required argument | `FROM/A` |
| `/K` | Keyword (must use keyword=value) | `PUBSCREEN/K` |
| `/S` | Switch (boolean flag) | `ALL/S` |
| `/N` | Numeric value | `BUF/N` |
| `/M` | Multiple values (array) | `FILES/M` |
| `/F` | Rest of line (to end) | `CMD/F` |
| `=` | Alias | `FILE=FROM/A` |

---

## Resident Commands

Frequently used commands can be made **resident** (kept in RAM):

```
; Make a command resident:
Resident C:Dir PURE
Resident C:List PURE
Resident C:Copy PURE

; List resident commands:
Resident

; Remove:
Resident C:Dir REMOVE
```

Requires the binary to be compiled as `PURE` (position-independent, no writeable globals in code section).

---

## Built-in Shell Commands

| Command | Description |
|---|---|
| `CD` | Change directory |
| `Echo` | Print text |
| `If/Else/EndIf` | Conditional |
| `Skip/Lab` | Loop |
| `FailAt` | Set error threshold |
| `Set/Unset` | Local variables |
| `SetEnv/GetEnv` | Global (ENV:) variables |
| `Alias` | Command aliases |
| `Path` | Manage command search path |
| `Prompt` | Set shell prompt |
| `Protect` | Set file protection bits |
| `Run` | Execute command in background |
| `Execute` | Run script file |
| `EndCLI` | Close this shell |
| `NewCLI`/`NewShell` | Open new shell |

---

## References

- NDK39: `dos/rdargs.h`
- RKRM: Shell chapter
- ADCD 2.1: AmigaDOS Guide
