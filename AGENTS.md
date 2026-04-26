# AGENTS.md — Technical Article Quality Standards

> **Audience**: AI coding assistants and human contributors.
> Read this before writing or expanding any `.md` file in this repository.

---

## Language & Spelling

- **American English only** — `color`, `behavior`, `initialize`, never `colour`, `behaviour`, `initialise`
- Use clear, direct technical prose — no filler, no hedging, no marketing language
- Prefer active voice: "The Blitter copies data" not "Data is copied by the Blitter"
- **Hexadecimal**: Use Motorola syntax (`$DFF180`) for hardware registers and memory addresses, not C-style (`0xDFF180`), unless explicitly within a C code block.

---

## Pre-Flight: Knowledge Base Scan (MANDATORY)

Before writing or expanding any article, you **must**:

1. **Read the root [README.md](README.md)** — it contains the full Documentation Map with every article in the repository. Understand what already exists to avoid duplicating content and to identify cross-linking opportunities.
2. **Scan the section's `README.md`** — know what sibling articles exist in the same folder. Your article should complement, not repeat, adjacent content.
3. **Search for related content** — use grep or file listing to find existing mentions of your topic across the repository. If another article already covers a subtopic in depth, link to it rather than rewriting it.
4. **Check for established patterns** — look at 2–3 exemplary articles in the repository (see "What Makes an Exemplary Article" below) to match style, depth, and structure.

> [!IMPORTANT]
> Every article must exist within the knowledge graph. Orphaned articles are unacceptable. Update the root README's Documentation Map when adding new articles.

---

## Article Structure

Every article must follow this skeleton. Omit sections that genuinely don't apply, but the **Overview** and **Navigation** are mandatory.

### 1. Navigation Breadcrumb (line 1)

```markdown
[← Home](../README.md) · [Section Name](README.md)
```

### 2. Title

Use a single `#` heading. Include the subject and a subtitle with key subtopics:

```markdown
# Memory Management — AllocMem, FreeMem, MemHeader
# Copper Programming — Deep Dive
# Animation — GEL System: BOBs, VSprites, AnimObs
```

### 3. Overview

The first section after the title. Two distinct styles depending on article type — choose before you write.

---

#### Type A: Concept Articles (history, chipset, OS subsystem, architectural deep-dives)

These articles answer *why* something exists and *what changed because of it*. The overview should be **scannable and alive** — a reader understands scope in under 10 seconds *and wants to keep reading*.

**Planning checklist** (answer these, then write prose that embeds the answers naturally):

| Question | What it means |
|---|---|
| **What is it?** | Define the thing, its scope, and where it lives. |
| **What was the problem?** | Why does this exist? Concrete pain, not abstract need. |
| **How does it work / how did it evolve?** | Core mechanism or historical arc. |
| **Why does it matter?** | What changed? Numbers, not adjectives. |

**Voice:**

- **Open with a hook.** A contradiction, a surprise, a concrete image. "The Amiga had the best graphics chipset in the world — and a CPU that couldn't do math." Not "Floating-point arithmetic is the computational foundation of..."
- **Write like you're explaining to a smart colleague at a bar.** Short sentences. Concrete nouns (chips, scanlines, frames, hours). No filler.
- **Bold vivid details, not section labels.** Bold `**two and a half video scanlines**`, not `**The problem.**`.
- **Paragraphs tell a story.** Hook → problem → solution arc → punchline. 2–5 sentences each.
- **Every paragraph gets a blank line after it.** Never a monolithic block. If you have 6 sentences about four CPU generations, split them into 2–3 paragraphs — one per phase or per idea. The blank lines are not optional; they are how the reader breathes.

Bad (form-filling):
> **What it is.** Floating-point arithmetic is the computational foundation of 3D rendering...
> **The problem.** The 68000 CPU was integer-only...
> **The solution.** First, Motorola shipped the MC68881...

Good (alive prose — FPU article):
> In 1985, the Amiga had the best graphics chipset in the world — and a CPU that couldn't do math. The 68000 was an integer-only processor: brilliant at moving pixels, helpless at trigonometry. Ask it to compute `sin(0.7)` and it would freeze for **two and a half video scanlines**...
>
> That was the problem the FPU solved. Motorola shipped four generations between 1984 and 1994, each designed under the same brutal constraint: floating-point circuits are **30× more complex** than integer circuits...

---

#### Type B: Reference Articles (register catalogs, file format specs, LVO tables, API listings, error code tables)

These articles exist to be **looked up**, not read cover-to-cover. The overview must be minimal: state what the thing is, where it lives, and get out of the way.

**Template (one paragraph, 2–4 sentences):**

> [Thing] is [definition — one sentence]. It lives in [library / chip / NDK header path / file]. See [cross-link] for the broader context.

**Rules:**
- No hook. No drama. No story arc. The reader came here to look up a register or a flag — don't waste their time.
- State the library name, NDK header, or file extension so the reader knows they're in the right place.
- One paragraph only. No blank-line separation.
- Never stretch to fill space — if 2 sentences cover it, stop.

Good (custom chip registers reference):
> The OCS/ECS custom chip registers occupy the address range `$DFF000–$DFF1FF` and are mapped to the Agnus, Denise, and Paula chips. This article catalogs every register with its address, R/W capability, and bit-field assignments. See the [Copper](copper.md) and [Blitter](blitter.md) articles for programming context.

Good (error codes reference):
> AmigaOS error codes are returned in `D0` by Exec and DOS library calls on failure. Negative values indicate warnings (operation completed with caveats); positive values indicate errors (operation failed). This table lists every defined error code from `exec/errors.h` (NDK 3.9). See [Error Handling](../07_dos/error_handling.md) for how to interpret and respond to errors.

### 4. Architecture / How It Works

- Use **Mermaid diagrams** for system relationships, data flows, and state machines
- Show where the component sits in the overall system (chip, library, OS layer)
- Explain the **hardware backing** — which DMA engines, which custom chip registers, what bus interactions

### 5. Data Structures & Register Tables

- Show the **actual C struct** from NDK headers with inline comments
- Follow with a **field description table** for non-obvious fields
- Include the NDK source path: `/* exec/memory.h — NDK39 */`
- Annotate critical constraints inline: `/* Chip RAM only! */`
- **Hardware Registers**: Documentation must use the following table format, including the R/W (Read/Write/Strobe) capability:
  ```markdown
  | Address   | Name    | R/W | Description |
  |-----------|---------|-----|-------------|
  | `$DFF054` | BLTCON0 | W   | Blitter control register 0 (minterms, channels) |
  ```

### 6. API Reference

- Show function prototypes with LVO offsets: `/* LVO -198 */`
- Include practical usage snippets immediately after each prototype
- Group related functions together

### 7. Decision Guides & Comparison Tables

When multiple approaches exist, provide a **decision matrix**:

```markdown
| Criterion | Option A | Option B |
|---|---|---|
| When to use | ... | ... |
| Limitation | ... | ... |
```

### 8. Historical Context & Modern Analogies (MANDATORY for architectural topics)

This is **not optional** for any article covering a fundamental or architectural concept.

**Historical perspective:**
- Include a **competitive landscape** table comparing to contemporary platforms (Atari ST, C64, NES, Mac, PC, arcade hardware)
- Explain what made the Amiga's approach innovative (or not) relative to its era
- Provide **pros/cons analysis** in the context of 1985–1994 hardware constraints

**Modern analogies:**
- Add a **comparison table** mapping Amiga concepts to modern equivalents (macOS Core Animation, Vulkan/Metal, Unity/Unreal, etc.)
- Explain **why** the analogy holds and where it breaks down
- Help modern developers build intuition by connecting unfamiliar retro concepts to things they already know

### 9. Practical Examples

- Every article must include at least one **complete, working code example**
- Examples must compile — no pseudocode unless explicitly marked
- Show the full lifecycle: init → use → cleanup
- Annotate non-obvious lines with inline comments

### 10. When to Use / When NOT to Use

Every API or subsystem article must include explicit guidance on:
- **When to use** — the ideal scenarios, applicability ranges, sweet spots
- **When NOT to use** — situations where a different approach is better, with explanation of why
- **Applicability ranges** — quantify limits (e.g., "works well up to ~20 BOBs; beyond that, custom blitter routines outperform")

### 11. Best Practices & Antipatterns

- **Best practices**: Numbered list of actionable recommendations. Each item should be one line.
- **Antipatterns**: Common bad habits that compile but produce subtle bugs, poor performance, or system instability. Show the antipattern and the correct alternative side by side.

### 12. Pitfalls & Common Mistakes

- Use a dedicated **Pitfalls** section near the end
- Each pitfall gets a numbered subsection with:
  - A **bad code example** showing the bug
  - An explanation of **why** it fails
  - The **correct** version

### 13. Use Cases

Provide real-world use cases that demonstrate practical application:
- What kind of software uses this feature?
- Which well-known Amiga titles or applications relied on it?
- What are the common integration patterns?

### 14. FAQ (when topic resonates)

For topics that commonly generate questions (memory management, blitter programming, display modes), include a short FAQ section addressing the most frequent developer questions.

### 15. References

- NDK header paths
- ADCD 2.1 section references
- Cross-links to related articles in this repository
- External links where authoritative (Apple docs, Commodore manuals)

---

## Formatting Standards

### Memory Maps

- When illustrating memory layouts, stack frames, or hunk structures, use **monospace ASCII box-drawing** (`┌─┐`) rather than Mermaid flowcharts. Mermaid is for logic/state; ASCII boxes are for byte-precise memory layouts.

### Reverse Engineering & Patching

When documenting reverse engineering efforts (e.g., bypassing limitations, understanding undocumented behavior):
- **Disassembly**: Use standard 68k/x86 disassembly blocks with file offsets and original hex bytes included.
- **Unified Patch Tables**: Use the exact table structure below to show offset, byte delta, instruction, and rationale:
  ```markdown
  | File Offset | Original  | Patched   | Assembly         | Rationale |
  |-------------|-----------|-----------|------------------|-----------|
  | `$0001A4`   | `66 0A`   | `4E 71`   | `NOP`            | Defeats the check |
  ```
- **Call Graphs**: Use Mermaid diagrams for call graphs and tables for obfuscation routines/gate mechanisms.

### Tables

- Use tables for structured comparisons, flag lists, register maps, field descriptions
- Always include a header row and separator
- Keep cells concise — one concept per cell

### Code Blocks

- Use fenced code blocks with language tags: ` ```c `, ` ```asm `, ` ```markdown `
- Include NDK source attribution in struct definitions
- Use `/* comment */` for inline annotations in C code

### Mermaid Diagrams

- Use for architecture diagrams, data flow, state machines, and system relationships
- Apply consistent styling: `fill:#e8f4fd,stroke:#2196f3` for DMA/hardware, `fill:#fff9c4,stroke:#f9a825` for coprocessors
- Keep diagrams readable — no more than ~15 nodes per diagram

### Alerts

Use GitHub-style alerts sparingly for critical information:

```markdown
> [!NOTE]
> Background context that aids understanding

> [!WARNING]
> Common mistake that causes data corruption or system crash
```

- **The Chip RAM Alert**: Any API, struct, or hardware register that requires DMA-accessible memory must be highlighted with a `> [!WARNING]` block explicitly stating **Requires Chip RAM**.

### Horizontal Rules

Use `---` to separate major sections. Don't use between subsections.

---

## Depth Expectations

### Shallow (unacceptable)

A struct dump with no context, no explanation of relationships, no examples, no pitfalls. This is a header file, not documentation.

### Adequate

Overview + struct descriptions + one example + references. Functional but not a learning resource.

### Deep (target quality)

Everything above, plus:
- Architectural diagrams showing hardware relationships
- Historical context and competitive landscape
- Modern analogies for accessibility
- Decision guides for choosing between approaches
- Multiple examples covering common and edge cases
- Comprehensive pitfalls with bad/good code pairs
- Performance analysis with quantified costs
- Cross-references to related articles

**Every article in this repository should target "Deep" quality.**

---

## What Makes an Exemplary Article — Key Differentiators

Analysis of the best articles in this repository ([exe_crunchers.md](03_loader_and_exec_format/exe_crunchers.md), [idcmp.md](09_intuition/idcmp.md), [animation.md](08_graphics/animation.md)) reveals consistent patterns that separate deep technical writing from shallow reference stubs:

### 1. The "Why It Exists" Opening

Every great article opens by answering *why* someone should care — not just what the thing is. Compare:

- ✗ *"IDCMP is a messaging system in Intuition."*
- ✓ *"Rather than polling for input, an Amiga application **sleeps** — consuming zero CPU — until Intuition sends a message. This is fundamental to why AmigaOS could multitask smoothly on a 7 MHz 68000 with 512 KB of RAM."*

### 2. Multi-Phase Architecture Diagrams

Great articles don't just describe a process — they break it into **numbered phases** with Mermaid diagrams at each stage. Example: `exe_crunchers.md` walks through 7 discrete steps of the decrunch stub, each with its own code block and explanation. This transforms opaque behavior into a debuggable mental model.

### 3. Named Antipatterns with Bad/Good Pairs

The best articles give antipatterns memorable names:
- "The Kitchen Sink" (requesting all IDCMP flags)
- "The Phantom Gadget" (dereferencing IAddress after ReplyMsg)
- "The Signal Swallower" (checking only one signal source)

Each antipattern shows the **broken code**, explains **why it breaks**, and provides the **corrected version**. This pattern is far more effective than generic warnings.

### 4. Decision Flowcharts

When multiple approaches exist, the best articles include a Mermaid decision flowchart that guides the reader to the correct choice. See IDCMP's "Use IDCMP or Exec MsgPort?" flowchart — it encodes the decision logic visually.

### 5. Use-Case Cookbooks

Beyond toy examples, exemplary articles include a **cookbook** of real-world patterns:
- Double-click detection
- Rubber-band selection
- Multi-signal event loops (IDCMP + Timer + ARexx)
- Menu multi-select chains

These are copy-paste-ready patterns that solve actual developer problems.

### 6. Quantified Performance Tables

Great articles don't just say "this is slow" — they provide concrete numbers:
- "Mouse movement at fast drag: ~500+ messages/sec — can starve other tasks"
- "3 blitter ops per BOB per frame — expensive at scale"
- "Decompression: ~2–5 seconds on a 7 MHz 68000"

### 7. Cross-Platform Comparison Tables

The best articles include a comparison table that maps Amiga concepts to their equivalents on other platforms (both contemporary and modern). This serves two purposes:
- **Historical context** — shows what was unique about the Amiga
- **Modern accessibility** — helps developers coming from Windows/macOS/Linux build intuition

See IDCMP's comparison with Win32/X11/Cocoa/Qt and animation's comparison with Atari ST/C64/NES.

### 8. Memory Safety Checklists

For any API that involves allocation, messaging, or shared resources, exemplary articles include a **risk/cause/prevention** table that acts as a pre-flight checklist.

### 9. The "Impact on FPGA/Emulation" Section

Since this repository targets MiSTer FPGA developers, the best articles note implementation concerns for hardware reproduction: timing-sensitive code, self-modifying code, custom chip register access patterns, cache coherency requirements.
If article is related completely to the Amiga software and has no relationship with FPGA/Emulation - just omit it.

### What Mediocre Articles Are Missing

Compare the above with shallow articles that typically lack:
- No "why" — just "what"
- No architecture diagrams
- No decision guides — reader doesn't know when to use the feature
- No pitfalls — reader will hit every bug the hard way
- No antipatterns — reader will write bad code that compiles
- No performance data — reader has no budget intuition
- No cross-platform context — reader can't connect to existing knowledge
- No use-case cookbook — reader can describe the API but can't solve problems with it

---

## Research Methodology

Before writing or expanding an article:

1. **Web research** — Search for real-world usage, developer forum discussions, and existing technical analyses. Ground the article in how practitioners actually used the technology, not just what the API reference says.
2. **Cross-reference NDK headers** — Verify struct layouts, flag values, and LVO offsets against the actual NDK 3.9 headers.
3. **Study real software** — Reference well-known Amiga titles, demos, and applications that use the feature. Cite specific examples when possible.
4. **Verify with hardware documentation** — Cross-check against the Amiga Hardware Reference Manual and custom chip datasheets.
5. **Check modern parallels** — Research whether the concept has modern equivalents; this improves accessibility and reveals design insights.
6. **Scan this repository first** — Follow the Pre-Flight Knowledge Base Scan procedure above before creating any new content.

---

## Content Principles

1. **Hardware grounding** — Always explain which chip, which DMA channel, which register. The Amiga is a hardware platform; software docs without hardware context are incomplete.

2. **No placeholders** — Every code example must be complete enough to compile. Every struct must show real fields from NDK headers. Every register must show the real address.

3. **API Versioning** — Always specify the minimum OS version required for an API (e.g., 'Requires OS 2.0+'). If a struct changed between versions, document the NDK 3.9 version as the modern baseline, and use the `/* V39 */` inline comments exactly as they appear in the headers.

4. **Big-Endian Warning** — Any article dealing with file formats (HUNK, IFF, ADF) or memory structures must explicitly state that the 68000 is **Big-Endian**. Modern developers will almost always read `0x1234` backwards if not reminded.

5. **Honest trade-offs** — When the OS provides an API that most professional software bypassed, say so. When a feature has scaling problems, quantify them. Don't oversell.

6. **Cross-linking** — Every article should link to at least 2–3 related articles. The documentation is a graph, not a list.

7. **Source attribution** — Cite NDK versions, ADCD sections, and ROM Kernel Reference Manual chapters. This is a technical reference, not folklore.

8. **De-abbreviation** — When introducing abbreviations (GEL, BOB, DMA, OCS), always provide the full name on first use and include a full-name column in summary tables.

9. **Real-world grounding** — Every feature must be contextualized with real use cases, applicability ranges, and honest guidance on when to use alternatives. Avoid documenting APIs in a vacuum.

---

## README Index Maintenance

When creating or significantly expanding an article:
- Update the section's `README.md` index table
- Update the root `README.md` Documentation Map if the article is new
- Index entries should be descriptive, not just the topic name:
  - ✗ `AnimOb, BOB, VSprite, GEL system`
  - ✓ `GEL system deep dive: BOBs, VSprites, AnimObs, hardware foundation, collision detection, double buffering, performance tuning`

---

## Commit Messages
!!!DO NOT make any commits without user asking!!!

Use conventional commit format:

```
docs(amiga): <concise description of what changed>
```

!!!DO NOT include co-authored-by trailers!!!
