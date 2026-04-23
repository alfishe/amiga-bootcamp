[← Home](../README.md) · [Exec Kernel](README.md)

# Lists and Nodes — MinList, List, Node, MinNode

## Overview

AmigaOS uses **intrusive doubly-linked lists** throughout exec: the task list, library list, device list, memory list, port list, and more all use the same `List`/`Node` structures defined in `exec/lists.h`.

---

## Structures

```c
/* exec/nodes.h — NDK39 */

struct Node {
    struct Node *ln_Succ;   /* pointer to next node (NULL at tail sentinel) */
    struct Node *ln_Pred;   /* pointer to prev node (NULL at head sentinel) */
    UBYTE        ln_Type;   /* node type — NT_TASK, NT_LIBRARY, NT_MEMORY... */
    BYTE         ln_Pri;    /* scheduling priority (used by Enqueue) */
    char        *ln_Name;   /* optional name string (NULL = anonymous) */
};

struct MinNode {
    struct MinNode *mln_Succ;
    struct MinNode *mln_Pred;
    /* no type, priority, or name — minimal overhead */
};
```

```c
/* exec/lists.h — NDK39 */

struct List {
    struct Node *lh_Head;      /* first node (or tail sentinel if empty) */
    struct Node *lh_Tail;      /* always NULL — marks end of list */
    struct Node *lh_TailPred;  /* last node (or head sentinel if empty) */
    UBYTE        lh_Type;      /* list type */
    UBYTE        lh_pad;
};

struct MinList {
    struct MinNode *mlh_Head;
    struct MinNode *mlh_Tail;      /* always NULL */
    struct MinNode *mlh_TailPred;
};
```

### Node Type Constants

```c
/* exec/nodes.h */
#define NT_UNKNOWN    0
#define NT_TASK       1   /* exec Task */
#define NT_INTERRUPT  2   /* Interrupt server */
#define NT_DEVICE     3   /* Device */
#define NT_MSGPORT    4   /* MsgPort */
#define NT_MESSAGE    5   /* Message */
#define NT_FREEMSG    6
#define NT_REPLYMSG   7
#define NT_RESOURCE   8
#define NT_LIBRARY    9   /* Library */
#define NT_MEMORY    10   /* MemHeader */
#define NT_SOFTINT   11
#define NT_FONT      12
#define NT_PROCESS   13   /* dos.library Process */
#define NT_SEMAPHORE 14
#define NT_SIGNALSEM 15   /* SignalSemaphore */
#define NT_BOOTNODE  16
#define NT_KICKMEM   17
#define NT_GRAPHICS  18
#define NT_DEATHMESSAGE 19
```

---

## Initialising a List

```c
/* Stack-allocated list: */
struct List myList;
NewList(&myList);   /* sets up sentinel pointers — mandatory */

/* Or use NEWLIST() macro: */
NEWLIST(&myList);
```

---

## Adding and Removing Nodes

```c
/* Add at head (highest LRU position): */
AddHead(&myList, &myNode);   /* LVO -240 */

/* Add at tail: */
AddTail(&myList, &myNode);   /* LVO -246 */

/* Remove from wherever it is (no list pointer needed): */
Remove(&myNode);             /* LVO -252 */

/* Priority-ordered insert (by ln_Pri, high first): */
Enqueue(&myList, &myNode);   /* LVO -270 */
```

---

## Walking a List

```c
struct Node *node, *next;
for (node = myList.lh_Head; node->ln_Succ != NULL; node = node->ln_Succ) {
    /* process node */
}
```

Safe removal while iterating (save next before removing):
```c
for (node = myList.lh_Head; (next = node->ln_Succ) != NULL; node = next) {
    if (should_remove(node)) Remove(node);
}
```

---

## Finding a Node by Name

```c
struct Node *found = FindName(&SysBase->LibList, "dos.library");
/* Returns NULL if not found */
/* Always call under Forbid() if the list may change */
```

---

## How the Sentinel Works

The AmigaOS list design uses a **3-pointer layout** that avoids special-casing empty lists and end-of-list checks:

```
lh_Head ──→ [ Node A ]──→ [ Node B ]──→ [ tail sentinel ]
                                              lh_Tail = NULL (always)
lh_TailPred ──────────────────────────→ [ Node B ]

Empty list:
lh_Head ──→ [ tail sentinel ]
lh_TailPred ──→ [ head sentinel ]
```

Walking stops when `ln_Succ == NULL` — that is the tail sentinel's `lh_Tail` field.

---

## References

- NDK39: `exec/nodes.h`, `exec/lists.h`
- ADCD 2.1: `AddHead`, `AddTail`, `Remove`, `Enqueue`, `FindName`, `NewList`
- *Amiga ROM Kernel Reference Manual: Exec* — lists chapter
