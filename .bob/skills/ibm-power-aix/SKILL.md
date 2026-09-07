---
name: ibm-power-aix
description: >-
  Administer the IBM AIX operating system on IBM Power Systems — system
  management (SMIT/ODM/SRC), devices, software & patch maintenance, LVM storage,
  JFS2 file systems, paging, backup (mksysb/savevg), boot/startup, problem
  determination, networking, scheduling, security, and performance. Use this
  whenever the user mentions AIX, an AIX command (smitty, lsdev, lspv, lsvg,
  mkvg, mklv, crfs, mksysb, savevg, alt_disk, installp, lslpp, suma, emgr, errpt,
  lsps, mkuser, no, vmo, topas, nmon, …), installing open-source software via the
  AIX Toolbox / DNF / YUM / RPM (`dnf install`, `dnf_aixtoolbox.sh`, `/opt/freeware`),
  compiling from source / building open-source on ppc64 (clang/LLVM, gcc, XL,
  `OBJECT_MODE`, `-maix64`, runtime linking `-brtl`, `blibpath`, TOC overflow),
  the ODM, SMIT, filesets, LVM (volume
  groups / logical volumes / physical volumes), JFS2, MPIO, paging space, errpt /
  error log, RBAC / auditing / AIXpert / Trusted Execution / EFS / AIX firewall /
  IPsec, or AIX performance tuning. Use for "create a volume group / filesystem",
  "grow a filesystem", "install a fileset / patch", "take a mksysb", "read the
  error log", "add a user", "configure the network", or "secure / tune an AIX
  system". Performance & tuning: the no/vmo/ioo/schedo/raso kernel tuning
  framework and /etc/tunables (tunsave/tunrestore/tuncheck, tunable types), the
  trace-based analysis tools curt, splat, tprof, svmon, procmon, filemon,
  netpmon, perfstat, and system-dump collection (sysdumpdev, snap).
metadata:
  enabled: true
  author: adapted from "AIX, PowerVM – UNIX, Virtualization, and Security" (S. Biedroń)
  version: "1.0.0"
---

# IBM AIX — UNIX System Administration on Power

Authoritative guide to administering **IBM AIX** (the enterprise UNIX on IBM Power
Systems): managing the system through SMIT/ODM/SRC, devices, software, LVM storage,
JFS2 file systems, backup, boot, diagnostics, networking, scheduling, security, and
performance. Grounded in real AIX administration, not Linux assumptions.

> **Golden rule #1 — SMIT is the guided front-end and the audit trail.** For almost
> any task, `smitty <fastpath>` gives a menu; pressing **F6** shows the exact
> command it will run, and every run is logged to `~/smit.log` (output) and
> `~/smit.script` (the commands). Use SMIT to discover/verify the command, then use
> the **direct command** for scripting. (e.g. `smitty mkuser` ↔ `mkuser`.)
>
> **Golden rule #2 — AIX is not Linux.** Internalize the differences or you'll
> reach for the wrong tool:
> - **Devices** live in the **ODM**: discover with `cfgmgr`, query with `lsdev` /
>   `lsattr` / `lscfg`; devices are `Available` or `Defined`.
> - **Software** is **filesets** managed by `installp` / `lslpp` (and `emgr` for
>   interim fixes / iFixes) — not `rpm`/`dnf`/`apt` (those exist for open-source
>   add-ons only).
> - **Storage is always LVM.** Even rootvg is LVM; you grow JFS2 filesystems
>   **online** with `chfs`. There are no raw partitions like Linux.
> - **JFS2** is the default filesystem; config lives in `/etc/filesystems`.

---

## 1. Mental model — interfaces & layers

| Layer | What | Tools |
|-------|------|-------|
| **SMIT** | Menu-driven admin front-end over the real commands | `smitty`, fastpaths, F6, `~/smit.script` |
| **ODM** | Object Data Manager — binary config DB (devices, software, SMIT menus) | `odmget`, `odmadd`, `odmdelete` (rarely direct) |
| **SRC** | System Resource Controller — manages subsystems/daemons | `lssrc`, `startsrc`, `stopsrc`, `refresh` |
| **Devices** | Physical/virtual devices in the ODM | `cfgmgr`, `lsdev`, `lsattr`, `lscfg`, `prtconf`, `rmdev`, `chdev` |
| **LVM** | Volume groups → logical volumes → file systems | `lsvg`, `lspv`, `lslv`, `mkvg`, `mklv`, … |

```sh
lsdev -Cc disk            # configured disks (-C = from ODM/Customized)
lsattr -El hdisk0         # attributes of a device
lscfg -vpl hdisk0         # detailed (vital product data) for a device
prtconf                   # system summary (model, memory, firmware, resources)
cfgmgr                    # configure newly attached devices
lssrc -a                  # all SRC subsystems and status
```

Device discovery, ODM, SRC, SMIT in depth:
**[references/system-management-and-devices.md](references/system-management-and-devices.md)**.

---

## 2. Software & maintenance

AIX software = **filesets** (a `bos.*`, `devices.*`, … package), grouped into LPPs.

```sh
lslpp -l                       # installed filesets
lslpp -w /usr/bin/ksh          # which fileset owns a file
installp -acgXYd <source> <fileset>   # install/commit (a=apply c=commit g=auto-deps X=expand)
installp -u <fileset>          # uninstall
instfix -i -k <APAR>           # is an APAR installed?
oslevel -s                     # OS level + Technology Level + Service Pack
emgr -l                        # list interim fixes (iFixes)
emgr -e <epkg.Z>               # install an iFix ; emgr -r -L <label> to remove
```

- **Patches:** **SUMA** (Service Update Management Assistant) downloads TLs/SPs/
  APARs; apply with `installp`/`smitty update_all`. Always **apply** then verify,
  **commit** when stable (committed can't be rejected).
- **Clone before risky changes:** `alt_disk_copy` clones rootvg to a spare disk so
  you can boot back if an update fails (`alt_rootvg_op`, `alt_disk_mksysb`).
- **NIM** (Network Installation Management) does network installs/updates at scale.

Filesets, SUMA, iFixes, alt_disk, and NIM:
**[references/software-install-maintenance-backup.md](references/software-install-maintenance-backup.md)**.

---

## 2a. AIX Toolbox — open-source software (DNF / RPM)

Base AIX software is **filesets** (§2); **open-source** software (bash, python,
gcc, git, curl, nginx, …) comes from the **AIX Toolbox for Open Source Software** as
**RPM** packages, managed with **DNF** (the recommended, dependency-resolving
package manager — the next-gen replacement for YUM). Open-source installs under
**`/opt/freeware`**. Full detail:
**[references/aix-toolbox-open-source.md](references/aix-toolbox-open-source.md)**.

**Bootstrap DNF once** (as root; AIX 7.1.3+; needs HTTPS to `public.dhe.ibm.com` or
a local mirror):
```sh
curl -k -o /tmp/dnf_aixtoolbox.sh \
  https://public.dhe.ibm.com/aix/freeSoftware/aixtoolbox/ezinstall/ppc/dnf_aixtoolbox.sh
chmod +x /tmp/dnf_aixtoolbox.sh && /tmp/dnf_aixtoolbox.sh -y    # -y: install dnf + migrate yum3→yum4 (recommended)
```
The script pulls the right `rpm.rte` prerequisite and the DNF bundle, then installs
everything.

**Then manage packages:**
```sh
dnf search <term>        # find        dnf info <pkg>     # details
dnf install <pkg>        # install + auto-resolve dependencies
dnf update [<pkg>]       # update all / one
dnf remove <pkg>         # uninstall   dnf repolist      # repositories
rpm -qf /opt/freeware/bin/bash        # which package owns a file
```

> **Three gotchas (IBM guidance):** (1) **Don't shadow base AIX with non-Toolbox
> builds** of `openssl`, `libgcc`/`libstdc++`, `gettext`, `libiconv` — it causes
> unexpected behavior; keep Toolbox builds. (2) **Never put other dirs before
> `/opt/freeware/lib` in a global `LIBPATH`** — it breaks AIX and Toolbox apps;
> scope LIBPATH per app. (3) **Toolbox RPMs aren't covered by AIX support** — use
> the AIX Open Source Community forum. Prefer **DNF over raw `rpm -i`** (which
> doesn't resolve dependencies). Air-gapped? Build a **local repo** from the AIX
> Toolbox Media ISO (see the reference).

---

## 2b. Building from source — compilers & toolchain (clang/LLVM, GCC)

To **compile from source** on AIX/POWER you need a compiler plus the AIX dev
filesets — and you must respect AIX's object-mode, linker, and shared-library
model, which differ from Linux. Full ppc64 guide:
**[references/build-from-source-toolchain.md](references/build-from-source-toolchain.md)**.

**Compiler choices:** **GCC** from the Toolbox (`dnf install gcc gcc-c++`) for most
projects; **clang/LLVM** for Clang/LLVM-based work; IBM **Open XL/XL C/C++** (licensed)
for best POWER optimization. They coexist — pick via `CC`/`CXX`.

**clang/LLVM 18.1.8 prebuilt** (community build for `powerpc64-ibm-aix`, runs on AIX
7.2+):
```sh
cd /tmp && curl -kLO https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.8/clang+llvm-18.1.8-powerpc64-ibm-aix-7.2.tar.xz
mkdir -p /opt/llvm-18.1.8 && gtar -C /opt/llvm-18.1.8 --strip-components=1 -xJf clang+llvm-18.1.8-powerpc64-ibm-aix-7.2.tar.xz
export PATH=/opt/llvm-18.1.8/bin:$PATH ; clang --version
```
Prereqs: AIX dev filesets `bos.adt.base bos.adt.include bos.adt.lib bos.adt.libm`
(clang drives the system `ld`/`as`), plus build tools from the Toolbox
(`dnf install gmake cmake ninja-build autoconf automake libtool pkgconfig xz tar`).

> **Verified on AIX 7.3/POWER11:** this LLVM prebuilt is **compiler-only — no C++
> standard library**. `clang` compiles & runs **C** out of the box; for **C++ use
> `g++`** from the Toolbox (`dnf install gcc-c++`) — it works cleanly. clang++↔GCC
> libstdc++ wiring is fragile, so: **clang for C / LLVM tooling, g++ for C++.**

**AIX ppc64 must-knows** (the things that break Linux-style builds):
```sh
export OBJECT_MODE=64        # or ar/nm/dump/ld silently ignore 64-bit objects
clang -maix64 -O2 hello.c -o hello
```
- **Object mode:** set `OBJECT_MODE=64` (or `-X64` per tool); compile `-maix64`.
- **Shared libs:** AIX `.a` archives often *contain* the shared object (`shr_64.o`);
  enable runtime linking with `-Wl,-brtl` (and `-Wl,-bexpall` to export symbols).
- **No `-rpath`:** use `-Wl,-blibpath:/opt/freeware/lib:/usr/lib:/lib` at link time
  or `LIBPATH` at runtime (AIX's `LD_LIBRARY_PATH`).
- **TOC overflow** on big binaries → `-Wl,-bbigtoc` or `-mcmodel=large`.
- Prefer **`gmake`** over AIX `make`; if shared-lib issues block you, build
  `--disable-shared`/static.

> These differences (object mode, runtime linking, `blibpath`, archive-embedded
> shared objects, TOC) cause most AIX source-build failures — the reference has the
> error→fix table.

---

## 3. Storage — LVM, SAN & MPIO

The hierarchy: **PV** (physical volume / hdisk) → **VG** (volume group) → **LV**
(logical volume) → file system. Everything is online-resizable upward.

```sh
lspv ; lsvg ; lsvg -l rootvg          # PVs, VGs, LVs in a VG
mkvg -S -y datavg hdisk1 hdisk2       # create a (scalable) VG
extendvg datavg hdisk3                # add a PV to a VG
mklv -t jfs2 -y datalv datavg 20      # create a 20-PP logical volume
extendlv datalv 10                    # grow an LV
lspath ; lsmpio                       # MPIO paths to SAN disks
```

- **SAN + MPIO:** AIX discovers SAN LUNs as `hdiskN` with multiple **paths**;
  `lspath`/`lsmpio` show/manage them, `chpath` enables/disables a path.
- Mirror across PVs with `mklv -c 2` / `mirrorvg`; balance with `reorgvg`; replace a
  disk with `migratepv` then `reducevg`.

LVM operations, mirroring, SAN/MPIO detail:
**[references/storage-lvm-filesystems.md](references/storage-lvm-filesystems.md)**.

---

## 4. File systems & paging

**JFS2** (Enhanced Journaled File System) is the default. Filesystems are defined in
`/etc/filesystems` and sit on an LV.

```sh
crfs -v jfs2 -g datavg -m /data -A yes -a size=20G    # create JFS2 + LV + mount point
mount /data ; umount /data ; mount -a                  # mount / unmount
chfs -a size=+10G /data                                # GROW online (+) or set absolute
lsfs ; df -g                                           # filesystems / usage (GB)
fsck -y /dev/fslv00                                    # check (unmounted)
```

- **Grow online** with `chfs -a size=+NG`; JFS2 can also **shrink** (`-a size=-NG`)
  on supported levels — back up first.
- **ACLs:** AIXC (classic) and NFS4 — `aclget`/`aclput`/`acledit`.
- **Snapshots:** internal (`snapshot -o snapfrom=…`) or external — point-in-time
  JFS2 images.
- **Paging space** (swap): `lsps -a`, add with `mkps`/`chps`, default `hd6` in
  rootvg. Size for the workload; multiple paging spaces should be similar size.

File system ops, ACLs, snapshots, and paging:
**[references/storage-lvm-filesystems.md](references/storage-lvm-filesystems.md)**.

---

## 5. Backup & recovery

| Tool | Scope | Restore |
|------|-------|---------|
| **mksysb** | Bootable image of **rootvg** (the OS) | Boot from it; full system restore / clone |
| **savevg / restvg** | A **non-rootvg** data VG | `restvg` recreates VG+LVs+FS+data |
| **tar / cpio / backup-restore** | Files/directories | standard UNIX restore |

```sh
mksysb -i /backup/mksysb.image        # rootvg system backup (-i regenerates the image.data)
savevg -if /backup/datavg.savevg datavg
restvg -f /backup/datavg.savevg hdisk5
```
A **mksysb** is the cornerstone of AIX recovery — take one before major changes and
on a schedule; it can restore to the same or different hardware (with device
filesets). Details: **[references/software-install-maintenance-backup.md](references/software-install-maintenance-backup.md)**.

---

## 6. Boot, startup & problem determination

- **Boot:** `bootlist -m normal -o` (show/set boot disks), `bosboot -ad /dev/hdiskN`
  (rebuild the boot image — required after some changes), SMS menu for boot-device
  selection (activate the LPAR to SMS — see the **ibm-power-vm** skill).
- **Init:** AIX uses `/etc/inittab` (`mkitab`/`chitab`/`rmitab` to edit it safely)
  and run levels; the `init` process and `rc.*` scripts start services.
- **Error log:** the error daemon logs hardware/software events.
  ```sh
  errpt                 # summary (one line per error, newest first)
  errpt -a              # full detail
  errpt -j <id> / -d H  # filter by error id / class (H=hardware,S=software)
  errlogger "msg"       # write an operator entry
  errclear 30           # delete entries older than 30 days
  ```
- **syslogd** (`/etc/syslog.conf`) for daemon/application logging; **diag** for
  hardware diagnostics; `alog -o -t boot` for the boot log.

Boot, inittab, error log, syslog, diag:
**[references/boot-problem-determination-performance.md](references/boot-problem-determination-performance.md)**.

---

## 7. Networking, users & scheduling

- **Network:** `mktcpip`/`smitty mktcpip` (initial config), `chdev -l enX`
  (interface attrs), `lsattr -El enX`; tools `ifconfig`, `netstat`, `route`,
  `entstat -d entX` (adapter stats), `traceroute`, `ping`. Name resolution via
  `/etc/hosts`, DNS (`/etc/resolv.conf`), NIS; resolution order in
  `/etc/netsvc.conf` (or `/etc/irs.conf`). Services via **inetd** (`/etc/inetd.conf`),
  **SSH** (OpenSSH fileset), **NFS** (`exportfs`, `mount`). Kernel network tunables
  via **`no`**.
- **Users:** `mkuser` / `chuser` / `rmuser` / `lsuser`; passwords `passwd` / `pwdadm`;
  attributes in `/etc/security/*` (edit via `chsec`). Login tracked in `who`,
  `last`, `/etc/security/failedlogin`.
- **Scheduling:** `crontab -e` (per-user cron) and `at`/`batch` for one-offs.

Full network/user/scheduling commands:
**[references/networking-scheduling.md](references/networking-scheduling.md)**.

---

## 8. Security

AIX has a deep, layered security stack — full coverage in
**[references/security.md](references/security.md)**:

| Feature | What |
|---------|------|
| **RBAC** | Role-Based Access Control — split root into roles/authorizations (`mkrole`, `setkst`, `swrole`); domain RBAC for resource isolation |
| **Auditing** | Kernel audit subsystem (`audit start/shutdown`, classes/events in `/etc/security/audit/`) |
| **AIXpert** | AIX Security Expert — apply/track a security policy baseline (`aixpert -l high|medium|low`) |
| **Trusted Execution (TE)** | Verify binary integrity against the Trusted Signature Database (`trustchk`) |
| **EFS** | Encrypted File System — per-file encryption with user keystores (`efsenable`, `efskeymgr`) |
| **Firewall** | Genie/IP filtering — `mkfilt`/`lsfilt`/`genfilt` traffic rules |
| **IPsec** | Encrypted tunnels between hosts |

> Security changes can lock you out or break access. **AIXpert high**, RBAC role
> changes, EFS, and firewall rules are high-impact — confirm scope, keep a root
> session open, and take a mksysb first.

---

## 9. Performance

### Monitor (find the bottleneck)
```sh
topas        # real-time dashboard (CPU/mem/disk/net/WLM)
nmon         # interactive + recordable (nmon -f -s 30 -c 120) monitor
vmstat 2 5   # CPU/memory/paging      iostat 2 5   # disk I/O
lparstat 2 5 # LPAR entitlement / shared-pool usage (PowerVM)
mpstat 2 5   # per-logical-CPU        sar / svmon -G   # historical / memory
```

### Drill in (trace-based analysis & profiling)
`trace` → `trcrpt`, then: **`curt`** (where CPU went, per thread/syscall),
**`tprof`** (CPU by process→routine→source line), **`svmon -P`** (per-process
memory), **`splat`** (lock contention), **`filemon`/`netpmon`** (file/network I/O),
**`procmon`** (live process table — *optional* `bos.perf.gtools` fileset; use
`topas -P` if absent), and the **`perfstat`/RSI** C APIs for custom monitors.

### Tune (one framework, five commands)
**`no`** (network), **`vmo`** (memory/VMM), **`ioo`** (I/O), **`schedo`**
(scheduler), **`raso`** (RAS) — all share flags and write through **`/etc/tunables`**:
```sh
no  -L tcp_recvspace                 # current / default / reboot / range / TYPE
no  -p -o tcp_recvspace=262144       # set now AND persist (nextboot);  -r = reboot value only
vmo -d minperm%                      # reset one to default ;  tundefault = reset all
```
- **Tunable types** decide when a change applies: **Dynamic** (now), **Reboot**
  (`-r`, next boot), **Bosboot** (needs `bosboot`), **Static** (never), **Mount/
  Incremental/Connect**. Check with `-L` before expecting it to take effect.
- **Files:** `/etc/tunables/nextboot` (applied at boot), `lastboot` + `lastboot.log`
  (read-only record). Manage with `tunsave` / `tunrestore` / `tuncheck` (validate a
  hand-made file) / `tunchange` / `tundefault`. **Recovery:** `tundefault -r` +
  reboot, or `tunrestore -r -f <good-file>`.
- **Restricted tunables** (shown only with `-F`) — change only under IBM guidance.

Method: baseline (`nmon -f`) → find the bottleneck → change **one** tunable →
measure → persist with `-p`. Full framework + tool reference:
**[references/boot-problem-determination-performance.md](references/boot-problem-determination-performance.md)**.

---

## 10. Critical constraints (these cause outages or data loss — internalize them)

- ✅ **Storage is LVM; resize is online and upward** — grow with `chfs -a size=+NG`;
  shrinking is limited/risky (JFS2 only, recent levels) — back up first.
- ✅ **`bosboot` after boot-affecting changes** (kernel, boot LV, some migrations) or
  the system may not reboot. Pair with a correct `bootlist`.
- ✅ **Commit vs apply** — `installp` *applied* updates can be rejected;
  *committed* cannot. Apply, verify, then commit.
- ✅ **Device states** — a device must be `Available` (not just `Defined`) to use;
  `cfgmgr` to bring it up, `rmdev -l` to remove.
- ✅ **Take a mksysb before major changes**, and `alt_disk_copy` for a bootable
  fallback. mksysb is the primary recovery path.
- ✅ **Don't edit `/etc/inittab` by hand** — use `mkitab`/`chitab`/`rmitab` (a bad
  inittab breaks boot).
- ✅ **Security lockout risk** — RBAC/AIXpert-high/EFS/firewall changes can deny
  access; keep a root session and a rollback (mksysb) ready.
- ✅ **AIX ≠ Linux** — filesets not rpm/apt; ODM-managed devices; `chfs`/LVM not
  fdisk; JFS2 not ext4 (golden rule #2).

---

## 11. Debugging playbook

| Symptom | Likely cause → check |
|---------|----------------------|
| New disk/adapter not visible | Not configured. `cfgmgr`; `lsdev -Cc disk`; check `Available` vs `Defined`. |
| "Filesystem full" but can't grow | VG out of free PPs. `lsvg datavg` (FREE PPs); `extendvg` a new PV, then `chfs -a size=+NG`. |
| `installp` fails on dependencies | Use `-g` (auto-include requisites) and the right source; `lslpp -l` to see what's present. |
| Won't boot after a change | Boot image/list wrong. From SMS/maintenance: `bosboot -ad /dev/hdiskN`, fix `bootlist`. |
| Hardware error suspected | `errpt -a` (detail), `diag` for the device; check `lscfg`/`lsattr`. |
| SAN disk has dead paths | `lspath`/`lsmpio` show Failed paths; `chpath -s enable`; check fabric/zoning. |
| Service won't start | `lssrc -s <subsystem>`; `startsrc -s <subsystem>`; check its log via `syslog`/`errpt`. |
| Can't log in after security change | RBAC/AIXpert/EFS lockout. Use the kept root session; revert policy (`aixpert -u`), check `/etc/security/user`. |
| High CPU/slow | `topas`/`nmon`; `lparstat` (entitlement/uncapped), `vmstat` (paging), `iostat` (disk). |

Always read `errpt -a` first for system-level issues; it correlates hardware and
software faults with timestamps and resource names.

---

## 12. References (load on demand)

| File | Contents |
|------|----------|
| [references/system-management-and-devices.md](references/system-management-and-devices.md) | SMIT (fastpaths, logs), ODM, SRC subsystems, device discovery (`lsdev`/`lsattr`/`lscfg`/`prtconf`/`cfgmgr`/`chdev`/`rmdev`) |
| [references/software-install-maintenance-backup.md](references/software-install-maintenance-backup.md) | Filesets/`installp`/`lslpp`, `oslevel`, SUMA, iFixes (`emgr`), `alt_disk`, NIM, mksysb/savevg/restvg |
| [references/aix-toolbox-open-source.md](references/aix-toolbox-open-source.md) | AIX Toolbox for Open Source Software: DNF bootstrap (`dnf_aixtoolbox.sh`), repos, `dnf`/`rpm` usage, `/opt/freeware`, local mirror, caveats (libpath, shadowing AIX filesets, support model) |
| [references/build-from-source-toolchain.md](references/build-from-source-toolchain.md) | Compiling from source: GCC vs clang/LLVM (the 18.1.8 ppc64 prebuilt) vs XL; AIX dev filesets; `OBJECT_MODE`/`-maix64`, runtime linking (`-brtl`), `blibpath` vs rpath, archive-embedded shared objects, TOC overflow; autotools/cmake recipes; error→fix table |
| [references/storage-lvm-filesystems.md](references/storage-lvm-filesystems.md) | LVM (PV/VG/LV), mirroring, SAN/MPIO, JFS2 file systems, ACLs, snapshots, paging space |
| [references/networking-scheduling.md](references/networking-scheduling.md) | Network config & commands, name resolution, inetd/SSH/NFS, `no` tunables, users, cron/at |
| [references/security.md](references/security.md) | RBAC, auditing, AIXpert, Trusted Execution, EFS, firewall (IP filtering), IPsec |
| [references/boot-problem-determination-performance.md](references/boot-problem-determination-performance.md) | Boot/`bootlist`/`bosboot`/inittab, error log/syslog/diag, system dump (`sysdumpdev`/`snap`), monitoring (`topas`/`nmon`/`vmstat`/…), trace-based analysis (`curt`/`tprof`/`svmon`/`splat`/`procmon`/`filemon`), the kernel **tuning framework** (`no`/`vmo`/`ioo`/`schedo`/`raso`, `/etc/tunables`, `tunsave`/`tunrestore`/`tuncheck`, tunable types) |

### Canonical external resources (you have internet access — use them)
- **IBM AIX documentation** (IBM Documentation / AIX Knowledge Center) and AIX Redbooks.
- **Command reference** — confirm flags for the installed AIX level (`oslevel -s`); options vary across TLs.
- Sources: *AIX, PowerVM – UNIX, Virtualization, and Security* (S. Biedroń);
  **IBM "AIX 7.2 Performance Tools Guide and Reference"** (tuning framework +
  analysis tools, §9); **IBM "AIX 7.2 Operating system management"** (system dump /
  support data); **IBM AIX Toolbox for Open Source Software** docs + the
  `dnf_aixtoolbox.sh` bootstrap script (§2a).

This is a **knowledge/command** skill (no API/SDK). Prefer `smitty` to discover the
exact command and its logging, verify with `ls*` before/after a change, and confirm
before anything boot-, storage-, or security-affecting.
