[← Home](../README.md) · [Networking](README.md)

# Protocol Implementation — DHCP, DNS, HTTP

## Overview

With `bsdsocket.library` providing a BSD-compatible API, standard network protocols can be implemented using familiar patterns adapted for the Amiga's single-address-space, library-based architecture.

---

## DNS Resolution

```c
/* gethostbyname — provided by bsdsocket.library: */
struct hostent *he = gethostbyname("www.amiga.org");
if (he) {
    struct in_addr addr = *(struct in_addr *)he->h_addr;
    Printf("IP: %s\n", Inet_NtoA(addr.s_addr));
}
```

---

## HTTP Client (Minimal)

```c
LONG sock = socket(AF_INET, SOCK_STREAM, 0);
struct hostent *he = gethostbyname("www.example.com");
struct sockaddr_in sa;
sa.sin_family = AF_INET;
sa.sin_port   = htons(80);
CopyMem(he->h_addr, &sa.sin_addr, he->h_length);

connect(sock, (struct sockaddr *)&sa, sizeof(sa));

char req[] = "GET / HTTP/1.0\r\nHost: www.example.com\r\n\r\n";
send(sock, req, strlen(req), 0);

char buf[8192];
LONG total = 0, n;
while ((n = recv(sock, buf + total, sizeof(buf) - total - 1, 0)) > 0)
    total += n;
buf[total] = 0;
Printf("%s\n", buf);

CloseSocket(sock);
```

---

## DHCP Overview

DHCP on Amiga is typically handled by the TCP/IP stack itself (Roadshow, Miami) or an external client (AmiTCP + `dhclient`). The sequence is standard:

1. `DHCPDISCOVER` — broadcast on port 67
2. `DHCPOFFER` — server responds with IP offer
3. `DHCPREQUEST` — client accepts
4. `DHCPACK` — server confirms; lease begins

For MiSTer/FPGA cores with custom SANA-II drivers, DHCP is handled automatically once the SANA-II driver is online and the stack is configured for `IPTYPE=DHCP`.

---

## References

- `12_networking/bsdsocket.md` — socket API reference
- `12_networking/tcp_ip_stacks.md` — stack configuration
