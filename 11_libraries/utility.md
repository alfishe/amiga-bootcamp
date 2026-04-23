[← Home](../README.md) · [Libraries](README.md)

# utility.library — TagItems, Hooks, Date Utilities

## Overview

`utility.library` (OS 2.0+) provides the universal tag-based parameter passing system, callback hooks, and date/time utilities used throughout AmigaOS.

---

## TagItem System

```c
/* utility/tagitem.h — NDK39 */
struct TagItem {
    ULONG ti_Tag;   /* tag identifier */
    ULONG ti_Data;  /* tag value */
};

/* Special tag values: */
#define TAG_DONE    0          /* end of tag list */
#define TAG_END     TAG_DONE
#define TAG_IGNORE  1          /* skip this tag */
#define TAG_MORE    2          /* ti_Data = pointer to another TagItem array */
#define TAG_SKIP    3          /* skip next ti_Data tags */
#define TAG_USER    (1<<31)    /* user-defined tags start here */
```

### Tag Utility Functions

| Function | Description |
|---|---|
| `FindTagItem(tag, tagList)` | Find first matching tag |
| `GetTagData(tag, default, tagList)` | Get tag value with default |
| `NextTagItem(&tagListPtr)` | Iterate through tags |
| `TagInArray(tag, array)` | Check if tag is in an array |
| `FilterTagItems(tagList, filter, logic)` | Filter tag list |
| `CloneTagItems(tagList)` | Allocate copy of tag list |
| `FreeTagItems(tagList)` | Free cloned tag list |
| `MapTags(tagList, mapList, flags)` | Remap tag IDs |

---

## Hook System

```c
/* utility/hooks.h */
struct Hook {
    struct MinNode  h_MinNode;
    ULONG         (*h_Entry)(void);   /* assembler entry point */
    ULONG         (*h_SubEntry)(void); /* C function pointer */
    APTR            h_Data;            /* user data */
};
```

Convention: `h_Entry` receives `A0=hook, A2=object, A1=message`.

```c
/* Convenience macro for SAS/C and GCC: */
ULONG myHookFunc(struct Hook *hook __asm("a0"),
                 Object *obj __asm("a2"),
                 APTR msg __asm("a1"))
{
    /* ... */
    return 0;
}

struct Hook myHook = { {NULL}, (HOOKFUNC)myHookFunc, NULL, myData };
```

---

## Date Utilities

```c
struct ClockData cd;
Amiga2Date(seconds, &cd);  /* seconds since 1.1.1978 → date */
ULONG secs = Date2Amiga(&cd); /* date → seconds */
ULONG secs = CheckDate(&cd);  /* validate and convert */
```

---

## References

- NDK39: `utility/tagitem.h`, `utility/hooks.h`, `utility/date.h`
