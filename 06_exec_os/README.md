[← Home](../README.md)

# exec.library — Kernel Overview

## Section Index

| File | Description |
|---|---|
| [exec_base.md](exec_base.md) | ExecBase — absolute address $4, system lists, hardware abstraction fields |
| [**multitasking.md**](multitasking.md) | **Multitasking deep-dive — scheduler, context switching, IPC, memory safety** |
| [tasks_processes.md](tasks_processes.md) | Task/Process structs, state machine, creation, scheduling |
| [library_system.md](library_system.md) | Library node, OpenLibrary lifecycle, version management |
| [library_vectors.md](library_vectors.md) | JMP table, LVO offsets, MakeFunctions, SetFunction |
| [interrupts.md](interrupts.md) | Interrupt levels 1–6, INTENA/INTREQ, AddIntServer, CIA interrupts |
| [memory_management.md](memory_management.md) | AllocMem, FreeMem, MemHeader, memory types, pools |
| [message_ports.md](message_ports.md) | MsgPort, PutMsg, GetMsg, WaitPort, public/private ports |
| [signals.md](signals.md) | AllocSignal, SetSignal, Wait, signal bit allocation |
| [semaphores.md](semaphores.md) | SignalSemaphore, shared/exclusive locking, deadlock avoidance |
| [io_requests.md](io_requests.md) | IORequest, DoIO, SendIO, CheckIO, AbortIO, device protocol |
| [lists_nodes.md](lists_nodes.md) | MinList/List/Node traversal, Enqueue, priority insertion |
| [resident_modules.md](resident_modules.md) | RomTag, RTF_AUTOINIT, FindResident, boot-time initialization |
| [exceptions_traps.md](exceptions_traps.md) | M68k exception vectors, Trap handlers, Guru Meditation |
