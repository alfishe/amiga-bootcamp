[← Home](../README.md) · [Exec Kernel](README.md)

# Message Ports — MsgPort, Message, PutMsg, GetMsg, WaitPort

## Overview

AmigaOS inter-task communication uses a **message passing** system. Tasks send `Message` structures to `MsgPort` queues. The receiving task either polls (`GetMsg`) or blocks (`WaitPort`) for incoming messages. No shared memory is touched without the message handshake.

---

## Core Structures

```c
/* exec/ports.h — NDK39 */

struct MsgPort {
    struct Node  mp_Node;       /* ln_Name = port name (for public ports) */
    UBYTE        mp_Flags;      /* PA_SIGNAL, PA_SOFTINT, PA_IGNORE */
    UBYTE        mp_SigBit;     /* signal bit used for PA_SIGNAL ports */
    APTR         mp_SigTask;    /* task to signal on message arrival */
    struct List  mp_MsgList;    /* queue of pending messages */
};

struct Message {
    struct Node  mn_Node;       /* ln_Type = NT_MESSAGE */
    struct MsgPort *mn_ReplyPort; /* port to send reply to (or NULL) */
    UWORD        mn_Length;     /* total size of message including header */
};
```

`mp_Flags` values:

| Value | Constant | Meaning |
|---|---|---|
| 0 | `PA_SIGNAL` | Signal `mp_SigTask` when message arrives |
| 1 | `PA_SOFTINT` | Trigger software interrupt |
| 2 | `PA_IGNORE` | Do not wake the task (polling only) |

---

## Creating a Message Port

```c
struct MsgPort *port = CreateMsgPort();   /* exec.library LVO -732 (OS 2.0+) */
/* or manually for OS 1.x compatibility: */
struct MsgPort *port = AllocMem(sizeof(struct MsgPort), MEMF_PUBLIC|MEMF_CLEAR);
port->mp_Node.ln_Type = NT_MSGPORT;
port->mp_Flags        = PA_SIGNAL;
port->mp_SigBit       = AllocSignal(-1);   /* any free signal bit */
port->mp_SigTask      = FindTask(NULL);    /* signal current task */
NewList(&port->mp_MsgList);
```

---

## Sending a Message

```c
/* PutMsg: add message to queue, signal receiver */
PutMsg(target_port, (struct Message *)my_msg);
/* Non-blocking — returns immediately */
```

PutMsg can be called from interrupt context.

---

## Receiving Messages

```c
/* Block until at least one message arrives: */
WaitPort(my_port);

/* Then drain the queue: */
struct MyMsg *msg;
while ((msg = (struct MyMsg *)GetMsg(my_port)) != NULL) {
    /* process msg */
    ReplyMsg((struct Message *)msg);  /* send reply if mn_ReplyPort != NULL */
}
```

### GetMsg (non-blocking poll)

```c
struct Message *msg = GetMsg(my_port);
/* Returns NULL if queue is empty */
```

---

## Public Named Ports

```c
/* Register a port so others can find it by name: */
port->mp_Node.ln_Name = "myapp.port";
Forbid();
AddPort(port);
Permit();

/* From another task: */
Forbid();
struct MsgPort *remote = FindPort("myapp.port");
Permit();
if (remote) PutMsg(remote, my_msg);

/* Cleanup: */
Forbid();
RemPort(port);
Permit();
```

`Forbid()` is required around `FindPort`/`AddPort`/`RemPort` to prevent the task list from changing mid-operation.

---

## Reply Pattern

The standard request-reply idiom:

```c
/* Sender: */
my_msg->mn_ReplyPort = reply_port;
PutMsg(server_port, &my_msg->mn_Message);
WaitPort(reply_port);
struct MyMsg *reply = (struct MyMsg *)GetMsg(reply_port);
/* reply now contains the server's response */

/* Server: */
WaitPort(server_port);
struct MyMsg *req = (struct MyMsg *)GetMsg(server_port);
/* process req... */
req->result = 42;
ReplyMsg(&req->mn_Message);  /* sends back to req->mn_ReplyPort */
```

---

## References

- NDK39: `exec/ports.h`, `exec/messages.h`
- ADCD 2.1: `CreateMsgPort`, `PutMsg`, `GetMsg`, `WaitPort`, `ReplyMsg`
- *Amiga ROM Kernel Reference Manual: Exec* — messages and ports chapter
