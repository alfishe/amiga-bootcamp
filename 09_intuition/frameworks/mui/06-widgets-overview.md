[← Home](../../../README.md) · [Intuition](../../README.md) · [Frameworks](../README.md)

# Widgets Overview

MUI provides a comprehensive set of built-in widget classes. This section provides a quick tour of the most commonly used ones with code snippets.

## Text

The Text class displays static text. It supports control codes for formatting.

```c
Child, TextObject,
    MUIA_Text_Contents, "\33cCentered text",
    End,
```

### Text Control Codes (MUIX_)

| Code | Effect |
|------|--------|
| `\33c` or `MUIX_C` | Center align |
| `\33r` or `MUIX_R` | Right align |
| `\33l` or `MUIX_L` | Left align |
| `\33b` or `MUIX_B` | Bold |
| `\33i` or `MUIX_I` | Italic |
| `\33u` or `MUIX_U` | Underline |

Multiple codes can be combined:

```c
"\33c\33bBold centered text"
```

### Common Text Attributes

| Attribute | Description |
|-----------|-------------|
| `MUIA_Text_Contents` | The string to display |
| `MUIA_Text_HiChar` | Underline this character as shortcut |
| `MUIA_Text_PreParse` | Pre-parse string with control codes |
| `MUIA_Text_SetVMax` | Set vertical maximum to font height |
| `MUIA_Text_SetMin` | Set minimum size to text dimensions |

## String

The String class is a single-line text input field.

```c
Child, StringObject,
    StringFrame,
    MUIA_String_Contents, "Default text",
    MUIA_String_MaxLen, 256,
    MUIA_String_Format, MUIV_String_Format_Left,
    End,
```

### String Attributes

| Attribute | Description |
|-----------|-------------|
| `MUIA_String_Contents` | Current string contents |
| `MUIA_String_MaxLen` | Maximum length |
| `MUIA_String_Format` | Left, center, or right alignment |
| `MUIA_String_Integer` | Parse contents as integer |
| `MUIA_String_Accept` | Valid character set |
| `MUIA_String_Reject` | Invalid character set |

## Buttons

The simplest button uses the `SimpleButton` macro:

```c
Child, SimpleButton("OK"),
```

This is shorthand for:

```c
Child, TextObject,
    ButtonFrame,
    MUIA_Background, MUII_ButtonBack,
    MUIA_Text_Contents, "OK",
    MUIA_Text_PreParse, "\33c",
    MUIA_InputMode, MUIV_InputMode_RelVerify,
    End,
```

## List and Listview

Lists store lines of data. A Listview wraps a List with scrollbars and input handling.

### Basic Listview

```c
Child, ListviewObject,
    MUIA_Listview_Input, FALSE,
    MUIA_Listview_List, ListObject,
        ReadListFrame,
        MUIA_List_ConstructHook, MUIV_List_ConstructHook_String,
        MUIA_List_DestructHook,  MUIV_List_DestructHook_String,
        End,
    End,
```

### Adding Items

```c
char *entry = "New item";
DoMethod(list, MUIM_List_InsertSingle, entry, MUIV_List_Insert_Bottom);
```

### Clearing the List

```c
DoMethod(list, MUIM_List_Clear);
```

### List Attributes

| Attribute | Description |
|-----------|-------------|
| `MUIA_List_SourceArray` | Initialize from a NULL-terminated array |
| `MUIA_List_ConstructHook` | Hook to construct entries |
| `MUIA_List_DestructHook` | Hook to destruct entries |
| `MUIA_List_CompareHook` | Hook for sorting |
| `MUIA_List_DisplayHook` | Hook for custom rendering |
| `MUIA_List_Quiet` | Suppress updates during bulk operations |
| `MUIA_List_Active` | Currently selected entry |

### Specialized List Classes

| Class | Purpose |
|-------|---------|
| `Floattext` | Display multi-line text with word wrap |
| `Dirlist` | Display directory contents |
| `Volumelist` | Display mounted volumes |
| `Scrmodelist` | Display available screen modes |

## Numeric Family

### Slider

```c
Child, SliderObject,
    MUIA_Numeric_Min, 0,
    MUIA_Numeric_Max, 100,
    MUIA_Numeric_Value, 50,
    MUIA_Slider_Horiz, TRUE,
    End,
```

### Knob

```c
Child, KnobObject,
    MUIA_Numeric_Min, 0,
    MUIA_Numeric_Max, 255,
    End,
```

### Levelmeter

```c
Child, LevelmeterObject,
    MUIA_Numeric_Min, 0,
    MUIA_Numeric_Max, 100,
    MUIA_Levelmeter_Label, "Volume",
    End,
```

### Numericbutton

A compact popup slider:

```c
Child, NumericbuttonObject,
    MUIA_Numeric_Min, 0,
    MUIA_Numeric_Max, 999,
    End,
```

## Cycle

A cycle gadget cycles through a set of string labels:

```c
static char *choices[] = { "First", "Second", "Third", NULL };

Child, CycleObject,
    MUIA_Cycle_Entries, choices,
    End,
```

Or using the shorthand macro:

```c
Child, MUI_MakeObject(MUIO_Cycle, NULL, choices),
```

## Radio

Radio buttons for exclusive selection:

```c
static char *options[] = { "Option A", "Option B", "Option C", NULL };

Child, RadioObject,
    MUIA_Radio_Entries, options,
    End,
```

Or using the shorthand:

```c
Child, MUI_MakeObject(MUIO_Radio, NULL, options),
```

## Gauge

A horizontal or vertical progress bar:

```c
Child, GaugeObject,
    MUIA_Gauge_Current, 50,
    MUIA_Gauge_Max, 100,
    MUIA_Gauge_Horiz, TRUE,
    End,
```

## Scale

A percentage display:

```c
Child, ScaleObject,
    MUIA_Scale_Horiz, TRUE,
    End,
```

## Colorfield and Palette

### Colorfield

Displays a color that can be changed:

```c
Child, ColorfieldObject,
    MUIA_Colorfield_RGB, rgb_value,
    End,
```

### Palette

A full palette selection gadget:

```c
Child, PaletteObject,
    MUIA_Palette_Entries, palette_entries,
    End,
```

## Image and Bitmap

### Image

Display a built-in or custom image:

```c
Child, ImageObject,
    MUIA_Image_Spec, MUII_Close,
    End,
```

Standard images include `MUII_Close`, `MUII_TapePlay`, `MUII_TapeStop`, `MUII_TapePause`, `MUII_ArrowLeft`, `MUII_ArrowRight`, `MUII_ArrowUp`, `MUII_ArrowDown`, and many others.

### Bitmap

Display a custom bitmap:

```c
Child, BitmapObject,
    MUIA_Bitmap_Width, 32,
    MUIA_Bitmap_Height, 32,
    MUIA_Bitmap_Bitmap, myBitMap,
    MUIA_Bitmap_Transparent, 0,
    End,
```

### Bodychunk

Create a bitmap from an ILBM body chunk (useful for embedding images):

```c
Child, BodychunkObject,
    MUIA_Bitmap_Width, 32,
    MUIA_Bitmap_Height, 32,
    MUIA_Bitmap_Bitmap, myBitMap,
    MUIA_Bodychunk_Body, body_data,
    MUIA_Bodychunk_Compression, cmpByteRun1,
    MUIA_Bodychunk_Depth, 5,
    MUIA_Bodychunk_Masking, mskHasMask,
    End,
```

## Popup Classes

### Popstring

Base class for popup string gadgets. Usually subclassed rather than used directly.

### Popasl

Popup an ASL file or font requester:

```c
Child, PopaslObject,
    MUIA_Popstring_String, StringObject, StringFrame, End,
    MUIA_Popasl_Type, ASL_FileRequest,
    MUIA_Popasl_StartHook, &startHook,
    End,
```

### Poplist

Popup a simple list:

```c
Child, PoplistObject,
    MUIA_Popstring_String, StringObject, StringFrame, End,
    MUIA_Poplist_Array, string_array,
    End,
```

### Popobject

Popup any arbitrary object tree:

```c
Child, PopobjectObject,
    MUIA_Popstring_String, StringObject, StringFrame, End,
    MUIA_Popobject_Object, ListviewObject,
        MUIA_Listview_List, customList,
        End,
    End,
```

## Register

A tabbed group where each page is a separate group:

```c
Child, RegisterGroup(labels),
    Child, VGroup,
        /* Page 1 contents */
        End,
    Child, VGroup,
        /* Page 2 contents */
        End,
    Child, VGroup,
        /* Page 3 contents */
        End,
    End,
```

Where `labels` is a NULL-terminated array of tab titles:

```c
static char *labels[] = { "General", "Advanced", "About", NULL };
```

---

Previous: [Layout System](05-layout-system.md)
Next: [Windows and Applications](07-windows-and-applications.md)
