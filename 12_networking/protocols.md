[← Home](../README.md) · [Networking](README.md)

# Protocol Implementation — DNS, TCP, UDP, WaitSelect

## Overview

Working code examples for common network protocols on AmigaOS using [bsdsocket.library](bsdsocket.md). See [TCP/IP Stacks](tcp_ip_stacks.md) for the architecture that makes this possible and how it differs from Unix.

> [!NOTE]
> Amiga socket functions are **library calls** (via `bsdsocket.library`), not system calls. You must `OpenLibrary("bsdsocket.library", ...)` before using any socket function. Use `CloseSocket()` instead of `close()`, and `Errno()` instead of `errno`.

---

## DNS Resolution

```c
struct Library *SocketBase = OpenLibrary("bsdsocket.library", 4);
if (!SocketBase) return;

struct hostent *he = gethostbyname("www.amiga.org");
if (he)
{
    struct in_addr addr;
    CopyMem(he->h_addr, &addr, sizeof(addr));
    Printf("Host: %s\n", he->h_name);
    Printf("IP:   %s\n", Inet_NtoA(addr.s_addr));

    /* May have multiple addresses: */
    char **p;
    for (p = he->h_addr_list; *p; p++)
    {
        CopyMem(*p, &addr, sizeof(addr));
        Printf("  Addr: %s\n", Inet_NtoA(addr.s_addr));
    }
}
else
{
    Printf("DNS lookup failed\n");
}

CloseLibrary(SocketBase);
```

---

## TCP Client

```c
struct Library *SocketBase = OpenLibrary("bsdsocket.library", 4);
if (!SocketBase) return;

LONG sock = socket(AF_INET, SOCK_STREAM, 0);
if (sock < 0) { Printf("socket() failed\n"); goto out; }

struct hostent *he = gethostbyname("www.example.com");
if (!he) { Printf("DNS failed\n"); goto close; }

struct sockaddr_in sa;
sa.sin_family = AF_INET;
sa.sin_port   = htons(80);
CopyMem(he->h_addr, &sa.sin_addr, he->h_length);

if (connect(sock, (struct sockaddr *)&sa, sizeof(sa)) < 0)
{
    Printf("connect failed: %ld\n", Errno());
    goto close;
}

/* Send HTTP request: */
char req[] = "GET / HTTP/1.0\r\nHost: www.example.com\r\n\r\n";
send(sock, req, strlen(req), 0);

/* Receive response: */
char buf[4096];
LONG n;
while ((n = recv(sock, buf, sizeof(buf) - 1, 0)) > 0)
{
    buf[n] = 0;
    Printf("%s", buf);
}

close:
    CloseSocket(sock);
out:
    CloseLibrary(SocketBase);
```

---

## TCP Server

```c
LONG listenSock = socket(AF_INET, SOCK_STREAM, 0);

struct sockaddr_in sa;
sa.sin_family      = AF_INET;
sa.sin_port        = htons(8080);
sa.sin_addr.s_addr = INADDR_ANY;

bind(listenSock, (struct sockaddr *)&sa, sizeof(sa));
listen(listenSock, 5);

Printf("Listening on port 8080...\n");

while (running)
{
    struct sockaddr_in clientAddr;
    LONG addrLen = sizeof(clientAddr);
    LONG clientSock = accept(listenSock,
                             (struct sockaddr *)&clientAddr,
                             &addrLen);
    if (clientSock >= 0)
    {
        Printf("Connection from %s\n",
               Inet_NtoA(clientAddr.sin_addr.s_addr));

        char response[] = "HTTP/1.0 200 OK\r\n"
                          "Content-Type: text/html\r\n\r\n"
                          "<h1>Hello from Amiga!</h1>\n";
        send(clientSock, response, strlen(response), 0);
        CloseSocket(clientSock);
    }
}

CloseSocket(listenSock);
```

---

## UDP Datagram

```c
LONG udpSock = socket(AF_INET, SOCK_DGRAM, 0);

/* Send: */
struct sockaddr_in dest;
dest.sin_family      = AF_INET;
dest.sin_port        = htons(9999);
dest.sin_addr.s_addr = inet_addr("192.168.1.255");

char msg[] = "Hello UDP";
sendto(udpSock, msg, strlen(msg), 0,
       (struct sockaddr *)&dest, sizeof(dest));

/* Receive: */
char buf[1024];
struct sockaddr_in from;
LONG fromLen = sizeof(from);
LONG n = recvfrom(udpSock, buf, sizeof(buf), 0,
                   (struct sockaddr *)&from, &fromLen);
buf[n] = 0;
Printf("From %s: %s\n", Inet_NtoA(from.sin_addr.s_addr), buf);

CloseSocket(udpSock);
```

---

## WaitSelect — Combined Socket + GUI Event Loop

The key pattern for responsive Amiga network applications. `WaitSelect` simultaneously waits on sockets **and** Exec signals (windows, ARexx, timers) — no threads needed:

```c
/* Set up signal masks: */
ULONG winSig  = 1 << window->UserPort->mp_SigBit;
ULONG ctrlSig = SIGBREAKF_CTRL_C;

fd_set readFDs;
struct timeval tv;

BOOL running = TRUE;
while (running)
{
    FD_ZERO(&readFDs);
    FD_SET(sock, &readFDs);
    tv.tv_secs  = 1;
    tv.tv_micro = 0;

    ULONG sigmask = winSig | ctrlSig;

    LONG result = WaitSelect(sock + 1, &readFDs, NULL, NULL,
                              &tv, &sigmask);

    /* Socket data ready? */
    if (result > 0 && FD_ISSET(sock, &readFDs))
    {
        LONG n = recv(sock, buffer, sizeof(buffer), 0);
        if (n > 0)
        {
            /* process network data */
        }
        else
        {
            /* connection closed or error */
            running = FALSE;
        }
    }

    /* Window event? */
    if (sigmask & winSig)
    {
        struct IntuiMessage *imsg;
        while ((imsg = (struct IntuiMessage *)GetMsg(window->UserPort)))
        {
            switch (imsg->Class)
            {
                case IDCMP_CLOSEWINDOW:
                    running = FALSE;
                    break;
                /* ... handle other IDCMP events ... */
            }
            ReplyMsg((struct Message *)imsg);
        }
    }

    /* Ctrl-C? */
    if (sigmask & ctrlSig)
    {
        Printf("*** Break\n");
        running = FALSE;
    }
}
```

> [!TIP]
> `WaitSelect` eliminates the need for multi-threading in most Amiga network apps. A single event loop handles sockets, GUI, timers, and ARexx simultaneously — simpler and safer than threads in a non-protected memory environment.

---

## DHCP

DHCP is handled by the TCP/IP stack, not by applications. See [TCP/IP Stacks](tcp_ip_stacks.md) for configuration. The standard sequence is:

1. `DHCPDISCOVER` — stack broadcasts on port 67
2. `DHCPOFFER` — server responds with IP offer
3. `DHCPREQUEST` — stack accepts
4. `DHCPACK` — server confirms; interface is configured

---

## References

- [bsdsocket.md](bsdsocket.md) — API reference and LVO table
- [tcp_ip_stacks.md](tcp_ip_stacks.md) — stack architecture and configuration
- [sana2.md](sana2.md) — SANA-II driver layer
