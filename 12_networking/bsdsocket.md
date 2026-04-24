[← Home](../README.md) · [Networking](README.md)

# bsdsocket.library — BSD Socket API Reference

## Overview

`bsdsocket.library` is the AmigaOS implementation of the BSD socket API. It is provided by the active TCP/IP stack (AmiTCP, Miami, Roadshow). See [TCP/IP Stacks](tcp_ip_stacks.md) for how the stack architecture works and how it differs from Unix. See [Protocols](protocols.md) for working code examples.

---

## Per-Task Library Base

Unlike Unix (kernel-managed fd table), each Amiga task must open its own private `SocketBase`:

```c
struct Library *SocketBase = OpenLibrary("bsdsocket.library", 4);
if (!SocketBase)
{
    Printf("No TCP/IP stack running\n");
    return;
}

/* Configure per-task error variable: */
LONG errno;
SocketBaseTags(
    SBTM_SETVAL(SBTC_ERRNOPTR(sizeof(LONG))), (ULONG)&errno,
    SBTM_SETVAL(SBTC_LOGTAGPTR),              (ULONG)"myapp",
    TAG_DONE);
```

> [!CAUTION]
> **Never share `SocketBase` between tasks.** Each task MUST `OpenLibrary` its own copy. Sharing causes socket state corruption and random crashes. This is the #1 Amiga networking bug.

---

## Function Table (LVO Mapping)

| LVO | Function | BSD Equivalent |
|---|---|---|
| −30 | `socket(domain, type, protocol)` | `socket()` |
| −36 | `bind(sock, name, namelen)` | `bind()` |
| −42 | `listen(sock, backlog)` | `listen()` |
| −48 | `accept(sock, addr, addrlen)` | `accept()` |
| −54 | `connect(sock, name, namelen)` | `connect()` |
| −60 | `sendto(sock, buf, len, flags, to, tolen)` | `sendto()` |
| −66 | `send(sock, buf, len, flags)` | `send()` |
| −72 | `recvfrom(sock, buf, len, flags, from, fromlen)` | `recvfrom()` |
| −78 | `recv(sock, buf, len, flags)` | `recv()` |
| −84 | `shutdown(sock, how)` | `shutdown()` |
| −90 | `setsockopt(...)` | `setsockopt()` |
| −96 | `getsockopt(...)` | `getsockopt()` |
| −102 | `gethostbyname(name)` | `gethostbyname()` |
| −108 | `gethostbyaddr(addr, len, type)` | `gethostbyaddr()` |
| −114 | `getnetbyname(name)` | `getnetbyname()` |
| −168 | `Errno()` | `errno` |
| −174 | `CloseSocket(sock)` | `close()` |
| −180 | `WaitSelect(nfds, rd, wr, ex, timeout, sigmask)` | `select()` + signals |
| −210 | `inet_addr(cp)` | `inet_addr()` |
| −216 | `Inet_NtoA(in)` | `inet_ntoa()` |
| −222 | `inet_makeaddr(net, host)` | `inet_makeaddr()` |
| −252 | `getservbyname(name, proto)` | `getservbyname()` |
| −270 | `SocketBaseTagList(tags)` | (Amiga-specific) |

---

## WaitSelect — Amiga-Enhanced select()

The key Amiga-specific extension: `WaitSelect` simultaneously waits on socket file descriptors **and** Exec signal bits. This replaces the need for separate threads — a single event loop can handle sockets, windows, timers, and ARexx:

```c
LONG WaitSelect(LONG nfds,
                fd_set *readfds, fd_set *writefds, fd_set *exceptfds,
                struct timeval *timeout,
                ULONG *sigmask);
/* sigmask: on entry = signals to also wait for
            on exit  = which signals fired */
```

See [protocols.md](protocols.md) for a complete working example combining socket I/O with Intuition window events.

---

## Error Handling

```c
/* Amiga sockets use Errno() instead of global errno: */
LONG sock = socket(AF_INET, SOCK_STREAM, 0);
if (sock < 0)
{
    LONG err = Errno();
    Printf("socket() failed: error %ld\n", err);
}

/* Or set up a per-task errno pointer (recommended): */
LONG myErrno;
SocketBaseTags(
    SBTM_SETVAL(SBTC_ERRNOPTR(sizeof(LONG))), (ULONG)&myErrno,
    TAG_DONE);
/* Now myErrno is updated automatically after each call */
```

### Common Error Codes

| Value | Name | Meaning |
|---|---|---|
| 48 | `EADDRINUSE` | Address already in use |
| 60 | `ETIMEDOUT` | Connection timed out |
| 61 | `ECONNREFUSED` | Connection refused |
| 64 | `EHOSTDOWN` | Host is down |
| 65 | `EHOSTUNREACH` | No route to host |

---

## Differences from BSD/POSIX Sockets

| Aspect | BSD/POSIX | Amiga bsdsocket.library |
|---|---|---|
| Close socket | `close(fd)` | `CloseSocket(sock)` — `close()` is AmigaDOS |
| Error variable | Global `errno` | Call `Errno()` or set `SBTC_ERRNOPTR` |
| Multiplexing | `select()` / `poll()` / `epoll()` | `WaitSelect()` — also waits on Exec signals |
| Headers | `<sys/socket.h>` | `<proto/socket.h>` or stack-specific |
| Lifecycle | Kernel-managed | Must `OpenLibrary`/`CloseLibrary` per task |
| fd namespace | Shared with files | Sockets are separate from DOS file handles |
| Multi-thread | fd shared across threads | `SocketBase` is per-task, not shareable |

---

## References

- Roadshow SDK documentation
- AmiTCP SDK: `bsdsocket.h` and autodocs
- See also: [tcp_ip_stacks.md](tcp_ip_stacks.md) — stack architecture and configuration
- See also: [protocols.md](protocols.md) — working code examples (TCP, UDP, DNS)
- See also: [sana2.md](sana2.md) — network device driver layer below the stack
