[← Home](../README.md) · [AmigaDOS](README.md)

# Pattern Matching — ParsePattern, MatchPattern

## Overview

AmigaDOS provides built-in wildcard/pattern matching for file operations. Patterns are compiled into token streams via `ParsePattern` and matched via `MatchPattern`.

---

## Wildcard Syntax

| Pattern | Meaning | Example |
|---|---|---|
| `?` | Match exactly one character | `file?.txt` matches `file1.txt` |
| `#` | Match zero or more of the following | `#?.info` matches anything ending in `.info` |
| `#?` | Match any string (equivalent to `*`) | `#?` matches everything |
| `(a\|b)` | Alternation — match a or b | `(read\|write)` |
| `~` | Negation — match if NOT | `~(#?.info)` matches non-info files |
| `[abc]` | Character class | `[abc]` matches a, b, or c |
| `[a-z]` | Character range | `[0-9]` matches digits |
| `'` | Quote next character literally | `'#` matches literal `#` |

---

## API

```c
/* dos/dos.h — NDK39 */

/* Compile a pattern into tokenised form: */
LONG ParsePattern(STRPTR pat, STRPTR buf, LONG buflen);
/* Returns: 1 = pattern has wildcards, 0 = plain string, -1 = error */

/* Test a name against a compiled pattern: */
BOOL MatchPattern(STRPTR pat_compiled, STRPTR name);

/* Case-insensitive variants: */
LONG ParsePatternNoCase(STRPTR pat, STRPTR buf, LONG buflen);
BOOL MatchPatternNoCase(STRPTR pat_compiled, STRPTR name);
```

---

## Usage Example

```c
char pat[256], buf[256];
LONG is_wild;

is_wild = ParsePatternNoCase("#?.txt", pat, sizeof(pat));
if (is_wild >= 0) {
    if (MatchPatternNoCase(pat, "readme.txt"))
        Printf("Match!\n");
    if (!MatchPatternNoCase(pat, "readme.doc"))
        Printf("No match\n");
}
```

---

## Common Patterns

| Pattern | Matches |
|---|---|
| `#?` | Everything (wildcard all) |
| `#?.info` | All `.info` icon files |
| `~(#?.info)` | Everything except `.info` files |
| `(#?.c\|#?.h)` | All C source and header files |
| `file[0-9]` | `file0` through `file9` |

---

## References

- NDK39: `dos/dos.h`
- ADCD 2.1: `ParsePattern`, `MatchPattern`
