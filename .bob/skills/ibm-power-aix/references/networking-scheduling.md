# Networking, Users & Scheduling

SKILL.md §7.

## Network configuration

```sh
smitty mktcpip                     # guided: hostname, IP, mask, gateway, nameserver on an interface
mktcpip -h host1 -a 10.0.0.5 -m 255.255.255.0 -i en0 -g 10.0.0.1 -n 10.0.0.2 -d example.com -s -S
lsattr -El en0                     # interface attributes
chdev -l en0 -a state=up           # bring up; chdev -l en0 -a netaddr=... -a netmask=...
lsdev -Cc adapter | grep ent       # physical/virtual ethernet adapters (entN)
lsdev -Cc if                       # network interfaces (enN, etN)
```
AIX distinguishes the **adapter** (`entN`) from the **interface** (`enN` = standard
ethernet / IPv4+IPv6, `etN` = IEEE 802.3). Tunables via the `no` command.

## Name resolution

- `/etc/hosts` — static. `/etc/resolv.conf` — DNS servers + domain. NIS — `domainname`,
  `ypbind`.
- **Resolution order:** `/etc/netsvc.conf` (or `/etc/irs.conf`, or `NSORDER` env),
  e.g. `hosts = local, bind` (files then DNS).

## Useful commands

```sh
ifconfig -a                       # interface state/addresses
ifconfig en0 inet 10.0.0.5 netmask 255.255.255.0 up
netstat -in                       # interface stats ; -rn routing table ; -an sockets ; -s per-proto
route add -net 10.1.0.0 -netmask 255.255.0.0 10.0.0.254   # (or chdev inet0 for persistent routes)
entstat -d ent0                   # detailed adapter statistics (errors, link, flow control)
traceroute host ; ping host
```
Persistent static routes: `smitty mkroute` / `chdev -l inet0 -a route=...`.

## Network services

- **inetd** — superdaemon for telnet/ftp/etc.; config `/etc/inetd.conf`,
  `refresh -s inetd` after edits. Disable insecure services (telnet, ftp) in favor
  of SSH.
- **SSH** — OpenSSH ships as filesets (`openssh.base`); manage `sshd` via SRC
  (`startsrc -s sshd`), config `/etc/ssh/sshd_config`.
- **NFS** — `mknfs`, `exportfs -a` (server, `/etc/exports`), `mount host:/exp /mnt`
  (client); NFSv4 supported; daemons via `lssrc -g nfs`. `automount` for on-demand.

## Users & groups

```sh
mkuser pwd_algorithm=ssha512 home=/home/alice alice
lsuser alice ; lsuser -a id home groups alice ; lsuser ALL
chuser gecos="Alice A" loginretries=5 alice
chsec -f /etc/security/user -s alice -a account_locked=false
passwd alice ; pwdadm alice        # set/administer password
rmuser -p alice                    # remove user (-p also removes security stanzas)
```
User attributes live in `/etc/passwd`, `/etc/security/passwd`, `/etc/security/user`,
`/etc/security/limits` (edit via `chuser`/`chsec`, not by hand where possible).
Login tracking: `who`, `last`, `/etc/security/failedlogin`, `lastlog`.

## Scheduling

```sh
crontab -e            # edit current user's crontab (validated on save)
crontab -l ; crontab -l -e <user>     # list / edit another user's (root)
# fields: min hour day-of-month month day-of-week  command
at now + 1 hour       # one-off job (Ctrl-D to end); atq / atrm to manage
batch                 # run when system load permits
```
Control who may use cron/at via `/var/adm/cron/cron.allow` / `cron.deny` (and
`at.allow`/`at.deny`).

## Kernel network tunables (`no`)

```sh
no -a                 # show all tunables
no -o tcp_sendspace=262144            # set (runtime)
no -p -o tcp_recvspace=262144         # set + persist across reboot (/etc/tunables/nextboot)
no -L tcp_sendspace                   # show range/default/current
```
Change one tunable at a time and measure; `-p` to persist, `-r` for reboot-required
tunables.
