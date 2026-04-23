[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Layout System

## Overview

MUI handles widget positioning automatically through its Group classes. Rather than specifying absolute coordinates, you declare the structure of your UI and MUI computes sizes and positions based on:

- Each widget's minimum, default, and maximum size requirements
- Group direction (horizontal or vertical)
- Spacing, framing, and balancing hints
- User preferences from the MUI settings program

## Group Classes

Groups are containers that arrange their children. There are three primary group macros:

| Macro | Direction | Description |
|-------|-----------|-------------|
| `VGroup` | Vertical | Stacks children top-to-bottom |
| `HGroup` | Horizontal | Stacks children left-to-right |
| `GroupObject` | Configurable | Defaults to vertical; can be changed with `MUIA_Group_Horiz` |

### Basic Vertical Layout

```c
WindowContents, VGroup,
    Child, TextObject,
        MUIA_Text_Contents, "First line",
        End,
    Child, TextObject,
        MUIA_Text_Contents, "Second line",
        End,
    Child, StringObject,
        StringFrame,
        MUIA_String_Contents, "Input here",
        End,
    End,
```

**Visual result:**

```mermaid
graph TB
    T1["Text: First line"] --> T2["Text: Second line"] --> S1["String: Input here"]

    style T1 fill:#e8f4fd,stroke:#2196f3,color:#333
    style T2 fill:#e8f4fd,stroke:#2196f3,color:#333
    style S1 fill:#fff3e0,stroke:#ff9800,color:#333
    linkStyle default stroke:#ccc,stroke-width:1px
```

> VGroup stacks children **top-to-bottom**. Each child gets the full window width.

### Basic Horizontal Layout

```c
WindowContents, HGroup,
    Child, SimpleButton("OK"),
    Child, SimpleButton("Cancel"),
    End,
```

**Visual result:**

```mermaid
graph LR
    OK["OK"] --- CANCEL["Cancel"]

    style OK fill:#e8f5e9,stroke:#4caf50,color:#333
    style CANCEL fill:#ffebee,stroke:#f44336,color:#333
```

> HGroup arranges children **left-to-right**. Both buttons share available width equally.

### Nested Groups

Complex layouts are built by nesting groups:

```c
WindowContents, VGroup,
    Child, TextObject,
        TextFrame,
        MUIA_Background, MUII_TextBack,
        MUIA_Text_Contents, "\33cTitle",
        End,

    Child, HGroup,
        Child, VGroup,
            Child, SimpleButton("A"),
            Child, SimpleButton("B"),
            End,
        Child, VGroup,
            Child, SimpleButton("C"),
            Child, SimpleButton("D"),
            End,
        End,

    Child, HGroup,
        Child, HSpace(0),
        Child, SimpleButton("Close"),
        Child, HSpace(0),
        End,

    End,
```

**Visual result:**

```mermaid
graph TB
    TITLE["Title"] --> HGROUP["HGroup"]
    HGROUP --> A["A"] & C["C"]
    A --> B["B"]
    C --> D["D"]
    TITLE --> BOTTOM["HGroup"]
    BOTTOM --> CLOSE["Close"]

    style TITLE fill:#e8f4fd,stroke:#2196f3,color:#333
    style A fill:#e8f5e9,stroke:#4caf50,color:#333
    style B fill:#e8f5e9,stroke:#4caf50,color:#333
    style C fill:#e8f5e9,stroke:#4caf50,color:#333
    style D fill:#e8f5e9,stroke:#4caf50,color:#333
    style CLOSE fill:#fff3e0,stroke:#ff9800,color:#333
    style HGROUP fill:#f5f5f5,stroke:#bdbdbd,color:#333
    style BOTTOM fill:#f5f5f5,stroke:#bdbdbd,color:#333
    linkStyle default stroke:#ccc,stroke-width:1px
```

> The outer VGroup stacks Title → HGroup → Close vertically. The HGroup lays out VGroup1 and VGroup2 side-by-side. A and B stack within VGroup1; C and D within VGroup2.

## Spacing Objects

### Rectangle

A Rectangle is an invisible spacing object. Use it to create fixed or flexible gaps.

```c
Child, RectangleObject,
    MUIA_Rectangle_HMin, 20,
    MUIA_Rectangle_VMin, 10,
    End,
```

### Balance

A Balance object is a draggable separator that divides space between adjacent children. Users can drag it to resize the areas.

```c
Child, ListviewObject,
    MUIA_Listview_List, myList,
    End,
Child, BalanceObject, End,
Child, TextObject,
    MUIA_Text_Contents, "Details pane",
    End,
```

### HSpace and VSpace

Quick macros for adding flexible spacing:

```c
Child, HSpace(0),   /* expands to fill available horizontal space */
Child, VSpace(0),   /* expands to fill available vertical space */
```

Use these to push widgets to the edges or center them.

## Frames and Backgrounds

Frames are visual borders around objects. MUI provides frame macros that set both the frame style and background:

| Macro | Appearance |
|-------|------------|
| `TextFrame` | Standard text field frame |
| `StringFrame` | Input field frame |
| `GroupFrame` | Group border with optional title |
| `ReadListFrame` | Listview frame |
| `ButtonFrame` | Button frame |

Usage:

```c
Child, TextObject,
    TextFrame,
    MUIA_Background, MUII_TextBack,
    MUIA_Text_Contents, "Framed text",
    End,
```

Backgrounds can be specified with standard MUI images:

| Constant | Meaning |
|----------|---------|
| `MUII_BACKGROUND` | Standard background |
| `MUII_SHADOW` | Shadow color |
| `MUII_SHINE` | Highlight color |
| `MUII_FILL` | Fill pattern |
| `MUII_TEXTBACK` | Text background |
| `MUII_BUTTONBACK` | Button background |

## Group Attributes

### Same Size

Force all children to have the same size:

```c
HGroup, MUIA_Group_SameSize, TRUE,
    Child, SimpleButton("Short"),
    Child, SimpleButton("A much longer label"),
    End,
```

Both buttons will expand to fit the widest label.

### Columns

Arrange children in a grid with a fixed number of columns:

```c
GroupObject, MUIA_Group_Columns, 3,
    Child, SimpleButton("1"),
    Child, SimpleButton("2"),
    Child, SimpleButton("3"),
    Child, SimpleButton("4"),
    Child, SimpleButton("5"),
    End,
```

**Visual result (3-column grid, 5 children):**

```mermaid
graph TB
    subgraph "ColGroup 3"
        direction TB
        subgraph "Row 1"
            direction LR
            B1["1"]
            B2["2"]
            B3["3"]
        end
        subgraph "Row 2"
            direction LR
            B4["4"]
            B5["5"]
            EMPTY[" "]
        end
    end

    style B1 fill:#e8f5e9,stroke:#4caf50,color:#333
    style B2 fill:#e8f5e9,stroke:#4caf50,color:#333
    style B3 fill:#e8f5e9,stroke:#4caf50,color:#333
    style B4 fill:#e8f5e9,stroke:#4caf50,color:#333
    style B5 fill:#e8f5e9,stroke:#4caf50,color:#333
    style EMPTY fill:none,stroke:none
```

### Horiz

Make a Group horizontal instead of vertical:

```c
GroupObject, MUIA_Group_Horiz, TRUE,
    ...
    End,
```

## Custom Layout Hooks

For complex layouts that MUI's built-in groups cannot express, you can provide a custom layout hook. The hook receives layout messages and positions children manually.

### Hook Structure

```c
SAVEDS ULONG __asm LayoutFunc(REG(a0) struct Hook *h,
                               REG(a2) Object *obj,
                               REG(a1) struct MUI_LayoutMsg *lm)
{
    switch (lm->lm_Type)
    {
        case MUILM_MINMAX:
            /* Calculate and return min/max/default sizes */
            lm->lm_MinMax.MinWidth  = ...;
            lm->lm_MinMax.MinHeight = ...;
            lm->lm_MinMax.DefWidth  = ...;
            lm->lm_MinMax.DefHeight = ...;
            lm->lm_MinMax.MaxWidth  = MUI_MAXMAX;
            lm->lm_MinMax.MaxHeight = MUI_MAXMAX;
            return 0;

        case MUILM_LAYOUT:
            /* Position each child with MUI_Layout() */
            Object *cstate = (Object *)lm->lm_Children->mlh_Head;
            Object *child;

            while (child = NextObject(&cstate))
            {
                if (!MUI_Layout(child, left, top, width, height, 0))
                    return FALSE;
            }
            return TRUE;
    }
    return MUILM_UNKNOWN;
}
```

### Attaching the Hook

```c
static struct Hook LayoutHook = { {0,0}, LayoutFunc, NULL, NULL };

...

GroupObject,
    MUIA_Group_LayoutHook, &LayoutHook,
    Child, ...,
    Child, ...,
    End,
```

### Important Notes

- In `MUILM_MINMAX`, the children's min/max values are already calculated. You can use them to derive your group's size.
- In `MUILM_LAYOUT`, you must call `MUI_Layout()` for every child. The rectangle you are given is `(0, 0, width-1, height-1)`.
- Return `MUILM_UNKNOWN` for any message type you do not handle.
- Avoid errors during layout; MUI does not handle them gracefully.

## Virtual Groups and Scroll Groups

When content exceeds available space, use a virtual group with scrollbars:

```c
Child, ScrollgroupObject,
    MUIA_Scrollgroup_Contents, VirtgroupObject,
        Child, /* lots of widgets */,
        Child, /* lots of widgets */,
        End,
    End,
```

The `Virtgroup` creates a virtual canvas. The `Scrollgroup` adds scrollbars as needed.

**Scrollgroup structure:**

```mermaid
graph TB
    subgraph "ScrollgroupObject"
        direction TB
        subgraph "Visible viewport"
            V1["Widget 1"]
            V2["Widget 2"]
            V3["Widget 3"]
        end
        VSCROLL["▲ Scrollbar ▼"]
        subgraph "Hidden (below viewport)"
            V4["Widget 4"]
            V5["Widget 5"]
            V6["..."]
        end
    end

    style V1 fill:#e8f5e9,stroke:#4caf50,color:#333
    style V2 fill:#e8f5e9,stroke:#4caf50,color:#333
    style V3 fill:#e8f5e9,stroke:#4caf50,color:#333
    style V4 fill:#f5f5f5,stroke:#bdbdbd,color:#999
    style V5 fill:#f5f5f5,stroke:#bdbdbd,color:#999
    style V6 fill:#f5f5f5,stroke:#bdbdbd,color:#999
    style VSCROLL fill:#fff3e0,stroke:#ff9800,color:#333
```

## Layout Algorithm

```mermaid
sequenceDiagram
    participant App as Application
    participant Win as Window
    participant Root as Root Group
    participant C1 as Child 1
    participant C2 as Child 2

    Note over App,C2: Pass 1 — AskMinMax (bottom-up)
    Root->>C1: MUIM_AskMinMax
    C1-->>Root: min=40, def=80, max=200
    Root->>C2: MUIM_AskMinMax
    C2-->>Root: min=60, def=100, max=300
    Root-->>Win: group min=100, def=180, max=500

    Note over App,C2: Window opens at calculated size
    Win->>Win: OpenWindow(def_width=180)

    Note over App,C2: Pass 2 — Layout (top-down)
    Win->>Root: Layout(0, 0, 180, h)
    Root->>Root: Distribute 180px by weight
    Root->>C1: MUI_Layout(x=0, w=80)
    Root->>C2: MUI_Layout(x=82, w=98)

    Note over App,C2: Pass 3 — Draw
    Root->>C1: MUIM_Draw
    Root->>C2: MUIM_Draw
```

### On Window Resize

```mermaid
sequenceDiagram
    participant User
    participant Win as Window
    participant Root as Root Group
    participant C1 as Child 1
    participant C2 as Child 2

    User->>Win: Drags size gadget
    Win->>C1: MUIM_Hide
    Win->>C2: MUIM_Hide
    Win->>Root: Layout(0, 0, new_w, new_h)
    Root->>Root: Redistribute space
    Root->>C1: MUI_Layout(new rect)
    Root->>C2: MUI_Layout(new rect)
    Win->>C1: MUIM_Show + MUIM_Draw
    Win->>C2: MUIM_Show + MUIM_Draw
```

### File Requester — Real-World Layout Example

From the official MUI SDK, a file requester demonstrates nested group layout:

```mermaid
graph TB
    subgraph "Window (VGroup)"
        direction TB
        subgraph "HGroup — Lists"
            direction LR
            FILELIST["File List<br/>(Listview)<br/>C/<br/>Classes/<br/>Devs/<br/>..."]
            DEVLIST["Device List<br/>(Listview)<br/>dh0:<br/>dh1:<br/>df0:<br/>ram:"]
        end
        PATH["Path: ___________________"]
        FILE["File: ___________________"]
        subgraph "HGroup — Buttons"
            direction LR
            OK["OK"]
            SPACE1["      "]
            CANCEL["Cancel"]
        end
    end

    style FILELIST fill:#e8f4fd,stroke:#2196f3,color:#333
    style DEVLIST fill:#e8f4fd,stroke:#2196f3,color:#333
    style PATH fill:#fff3e0,stroke:#ff9800,color:#333
    style FILE fill:#fff3e0,stroke:#ff9800,color:#333
    style OK fill:#e8f5e9,stroke:#4caf50,color:#333
    style CANCEL fill:#ffebee,stroke:#f44336,color:#333
    style SPACE1 fill:none,stroke:none
```

**Corresponding MUI code:**

```c
VGroup,
    Child, HGroup,
        Child, FileListview(),
        Child, DeviceListview(),
        End,
    Child, PathGadget(),
    Child, FileGadget(),
    Child, HGroup,
        Child, OkayButton(),
        Child, HSpace(0),
        Child, CancelButton(),
        End,
    End;
```

---

Previous: [Core Concepts](04-core-concepts.md)
Next: [Widgets Overview](06-widgets-overview.md)
