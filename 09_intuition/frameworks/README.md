[← Home](../../README.md) · [Intuition](../README.md)

# GUI Frameworks

AmigaOS spawned several GUI frameworks beyond the built-in GadTools/BOOPSI system. These frameworks provide layout management, user customization, and richer widget sets — features that the base Intuition API does not offer.

## Framework Index

| File | Framework | Era | Description |
|---|---|---|---|
| [mui/](mui/) | **MUI** (Magic User Interface) | 1993– | De-facto standard. Architecture, developer guide, code examples |
| *reaction.md* | **ReAction** / ClassAct | 1997– | Hyperion's official OS 3.5+ GUI toolkit |
| *bgui.md* | **BGUI** | 1994– | Lightweight BOOPSI-based layout system |

## Comparison

| Feature | MUI | ReAction | BGUI | GadTools |
|---|---|---|---|---|
| Layout engine | ✅ Constraint-based | ✅ Constraint-based | ✅ Basic | ❌ Manual |
| User preferences | ✅ Full | ⚠ Limited | ❌ None | ❌ None |
| Custom classes | ✅ MCC ecosystem | ✅ MakeClass | ✅ MakeClass | ❌ N/A |
| Availability | Aminet (free runtime) | OS 3.5+ bundled | Aminet (free) | ROM built-in |
| Platforms | AmigaOS, MorphOS, AROS | AmigaOS 3.5+ only | AmigaOS 2.0+ | AmigaOS 2.0+ |
| Adoption | Very high | Moderate | Low | Universal |
