[← Home](../README.md) · [Libraries](README.md)

# rexxsyslib.library — ARexx Interface

## Overview

ARexx is the Amiga's built-in macro/scripting language (based on REXX). `rexxsyslib.library` provides APIs for hosting ARexx ports, sending commands, and receiving results.

---

## Adding an ARexx Port

```c
struct MsgPort *arexxPort = CreateMsgPort();
arexxPort->mp_Node.ln_Name = "MYAPP";
arexxPort->mp_Node.ln_Pri  = 0;
AddPort(arexxPort);

/* In event loop, check for ARexx messages: */
struct RexxMsg *rmsg;
while ((rmsg = (struct RexxMsg *)GetMsg(arexxPort))) {
    STRPTR cmd = ARG0(rmsg);  /* the command string */
    /* Parse and execute command... */
    rmsg->rm_Result1 = 0;    /* RC = 0 (success) */
    rmsg->rm_Result2 = 0;
    ReplyMsg((struct Message *)rmsg);
}

RemPort(arexxPort);
DeleteMsgPort(arexxPort);
```

---

## Sending ARexx Commands

```c
struct MsgPort *replyPort = CreateMsgPort();
struct RexxMsg *rmsg = CreateRexxMsg(replyPort, NULL, NULL);
rmsg->rm_Args[0] = CreateArgstring("QUIT", 4);
rmsg->rm_Action  = RXCOMM;

struct MsgPort *target = FindPort("TARGETAPP");
if (target) {
    PutMsg(target, &rmsg->rm_Node);
    WaitPort(replyPort);
    GetMsg(replyPort);
    /* rmsg->rm_Result1 = return code */
}

DeleteArgstring(rmsg->rm_Args[0]);
DeleteRexxMsg(rmsg);
DeleteMsgPort(replyPort);
```

---

## References

- NDK39: `rexx/storage.h`, `rexx/rxslib.h`
