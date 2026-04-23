[← Home](../README.md) · [Networking](README.md)

# bsdsocket.library — BSD Socket API

## Overview

`bsdsocket.library` is the AmigaOS implementation of the BSD socket API. It is provided by the active TCP/IP stack (AmiTCP, Miami, Roadshow) and presents a POSIX-like socket interface adapted to the Amiga's library-based architecture.

---

## Opening

```c
struct Library *SocketBase = OpenLibrary("bsdsocket.library", 4);
if (!SocketBase) { /* no TCP/IP stack running */ }
```

---

## Core Functions (LVO Mapping)

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
| −168 | `Errno()` | `errno` (returns last error) |
| −174 | `CloseSocket(sock)` | `close()` |
| −180 | `WaitSelect(nfds, rd, wr, ex, timeout, sigmask)` | `select()` + signals |
| −210 | `inet_addr(cp)` | `inet_addr()` |
| −216 | `Inet_NtoA(in)` | `inet_ntoa()` |
| −222 | `inet_makeaddr(net, host)` | `inet_makeaddr()` |
| −252 | `getservbyname(name, proto)` | `getservbyname()` |

---

## WaitSelect — Amiga-Enhanced select()

Unlike BSD `select()`, `WaitSelect` integrates with Exec signals:

```c
fd_set rdset;
FD_ZERO(&rdset);
FD_SET(sock, &rdset);

ULONG sigmask = SIGBREAKF_CTRL_C;  /* also wait for Ctrl-C */
struct timeval tv = { 5, 0 };       /* 5 second timeout */

LONG n = WaitSelect(sock + 1, &rdset, NULL, NULL, &tv, &sigmask);
if (n > 0 && FD_ISSET(sock, &rdset)) { /* data ready */ }
if (sigmask & SIGBREAKF_CTRL_C) { /* user pressed Ctrl-C */ }
```

---

## Simple TCP Client

```c
LONG sock = socket(AF_INET, SOCK_STREAM, 0);
struct sockaddr_in addr;
addr.sin_family = AF_INET;
addr.sin_port   = htons(80);
addr.sin_addr.s_addr = inet_addr("93.184.216.34");

if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
    send(sock, "GET / HTTP/1.0\r\nHost: example.com\r\n\r\n", 38, 0);
    char buf[4096];
    LONG n = recv(sock, buf, sizeof(buf) - 1, 0);
    buf[n] = 0;
    Printf("%s\n", buf);
}
CloseSocket(sock);
```

---

## References

- NDK39: `libraries/bsdsocket.h` (stack-specific)
- Roadshow SDK documentation
- `12_networking/sana2.md` — network device driver layer
