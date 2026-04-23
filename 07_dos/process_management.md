[← Home](../README.md) · [AmigaDOS](README.md)

# Process Management — CreateNewProc, SystemTagList, Execute

## Overview

AmigaDOS provides several ways to launch child processes, ranging from the low-level `CreateNewProc` to the shell-level `Execute` and `SystemTagList`.

---

## CreateNewProcTags (OS 2.0+)

```c
/* dos/dostags.h — NDK39 */
struct Process *proc = CreateNewProcTags(
    NP_Entry,       myFunction,     /* function pointer */
    NP_Name,        "Worker",       /* task name */
    NP_StackSize,   8192,           /* stack size in bytes */
    NP_Priority,    0,              /* scheduling priority */
    NP_Input,       Open("NIL:", MODE_OLDFILE),
    NP_Output,      Open("NIL:", MODE_NEWFILE),
    NP_CloseInput,  TRUE,           /* close input on exit */
    NP_CloseOutput, TRUE,
    NP_CurrentDir,  DupLock(currentDir),
    TAG_DONE);
```

### Tag Constants

| Tag | Value | Meaning |
|---|---|---|
| `NP_Entry` | — | Function to run as the new process |
| `NP_Seglist` | — | Alternative: run from a loaded segment list |
| `NP_Name` | — | Process name (appears in task list) |
| `NP_StackSize` | — | Stack size in bytes (default 4096) |
| `NP_Priority` | — | Task priority (−128 to +127) |
| `NP_Input` | — | BPTR stdin handle |
| `NP_Output` | — | BPTR stdout handle |
| `NP_Error` | — | BPTR stderr handle (OS 3.0+) |
| `NP_CurrentDir` | — | Lock for current directory |
| `NP_HomeDir` | — | Lock for PROGDIR: |
| `NP_CopyVars` | — | Copy parent's local vars to child |

---

## SystemTagList — Run a Shell Command

```c
/* Execute a command string as if typed in a shell: */
LONG rc = SystemTagList("dir SYS: ALL", NULL);
/* rc = return code from the command */

/* With custom I/O: */
LONG rc = SystemTagList("list RAM:", (struct TagItem[]){
    { SYS_Input,  Open("NIL:", MODE_OLDFILE) },
    { SYS_Output, Open("RAM:output.txt", MODE_NEWFILE) },
    { TAG_DONE, 0 }
});
```

---

## Execute — Legacy Command Execution

```c
/* dos.library LVO −132 */
BOOL Execute(STRPTR command, BPTR input, BPTR output);
```

- `command` — shell command string
- `input` — BPTR to additional input (0 = none)
- `output` — BPTR to output handle (0 = current)

---

## WaitForChild / Process Exit

Child processes are independent tasks. To synchronize:
1. Use a shared `MsgPort` — child sends a death message
2. Check `pr_Result2` after the child task exits
3. Use `SYS_Asynch` tag with `SystemTagList` for fire-and-forget

---

## References

- NDK39: `dos/dostags.h`, `dos/dosextens.h`
- ADCD 2.1: `CreateNewProc`, `SystemTagList`, `Execute`
- `06_exec_os/tasks_processes.md` — Task/Process structures
