# Boot, Problem Determination & Performance

SKILL.md §6 & §9.

## Boot & startup

```sh
bootlist -m normal -o                 # show normal-mode boot devices
bootlist -m normal hdisk0 hdisk1      # set boot order (first bootable wins)
bootlist -m service -o                # service-mode boot list (diagnostics)
bosboot -ad /dev/hdisk0               # rebuild the boot image on a disk (REQUIRED after kernel/boot changes)
bootinfo -b                           # the disk we booted from
alog -o -t boot                       # read the boot log
alog -o -t console                    # console log
```
- After changes to the kernel, the boot logical volume, some migrations, or
  mirroring rootvg → run **`bosboot`** then verify **`bootlist`**, or the box may
  not reboot.
- SMS menu (boot device selection, network/NIM boot, diagnostics) is reached by
  activating the LPAR to SMS — see the **ibm-power-vm** skill.

## /etc/inittab & run levels

`init` reads `/etc/inittab`. **Don't edit it by hand** — a bad entry breaks boot.

```sh
lsitab -a                  # list all inittab entries
lsitab rctcpip             # one entry
mkitab "myapp:2:once:/usr/local/bin/start_app"   # add an entry
chitab "rctcpip:23:wait:/etc/rc.tcpip > /dev/console 2>&1"   # modify
rmitab myapp               # remove
```
Entry format: `identifier:runlevels:action:command` (actions: `respawn`, `wait`,
`once`, `boot`, `bootwait`, `initdefault`). AIX default run level is 2 (multiuser).

## Error log (the first place to look)

```sh
errpt                        # summary: IDENTIFIER TIMESTAMP T C RESOURCE_NAME DESCRIPTION
errpt -a                     # full detail for each entry
errpt -a -j <ID>             # only a specific error id
errpt -d H                   # class: H=hardware, S=software, O=operator, U=undetermined
errpt -s 0601000025          # since a date/time (MMDDhhmmYY)
errpt -N hdisk0              # for a specific resource
errlogger "operator note"    # write an operator entry
errclear 30                  # delete entries older than 30 days ; errclear 0 = all
```
`errpt -a` correlates hardware + software faults with timestamps, resource names,
and location codes — read it first for any system-level issue.

## syslogd & diag

```sh
# /etc/syslog.conf  e.g.:  *.info  /var/log/messages   (then: refresh -s syslogd)
# rotate via cron / the size+rotate suffix in the conf entry
diag                         # interactive hardware diagnostics (menus)
diag -d hdisk0 -c           # run diagnostics on a device (concurrent)
```

## System dump & support data

*(From the IBM "AIX 7.2 Operating system management" guide.)* When AIX crashes or
hangs, a **system dump** captures kernel state; **snap** packages everything IBM
support needs.

```sh
sysdumpdev -l                 # show primary/secondary dump devices + copy dir
sysdumpdev -e                 # estimate the dump size needed
sysdumpdev -L                 # info about the most recent dump
sysdumpdev -P -p /dev/lg_dumplv   # set the primary dump device (persistent)
sysdumpstart -p               # force a dump to the primary device (manual)
dmpuncompress / kdb           # uncompress / analyze a dump (with IBM support)
snap -gc                      # collect general system config + compress -> /tmp/ibmsupt/snap.pax.Z
snap -ac                      # collect ALL support data
snap -r                       # remove previously gathered snap data
```
- The default dump LV is often `lg_dumplv` in rootvg (you saw it in `lsvg -l rootvg`).
- **Live Dump** captures a subsystem without crashing the box (`livedumpstart`,
  data under `/var/adm/ras/livedump`).
- Send the `snap` bundle + the dump to IBM for failure analysis; pair with `errpt
  -a` output.

## Performance — monitoring

```sh
topas                       # real-time dashboard (CPU/mem/disk/net/processes/WLM); topas -P process view
nmon                        # interactive (c=cpu m=mem d=disk n=net t=top); nmon -f -s 30 -c 120 to record
vmstat 2 5                  # CPU (us/sy/id/wa), memory (avm/fre), paging (pi/po), faults
iostat 2 5                  # per-disk %tm_act, KB/s, tps; -D for service times
lparstat 2 5                # entitlement, %entc, virtual procs, shared-pool (PowerVM)
mpstat 2 5                  # per-logical-CPU breakdown
sar -u 2 5                  # historical/cpu (sa data via cron)
svmon -G                    # global memory (real/virtual/paging) ; svmon -P <pid> per process
filemon / netpmon / tprof   # detailed file/network/CPU-profile traces
```

## Performance — kernel tuning framework

*(Grounded in the IBM "AIX 7.2 Performance Tools Guide and Reference".)*

Five tuning commands share one framework: **`no`** (network), **`vmo`** (VMM/
memory), **`ioo`** (I/O), **`schedo`** (scheduler), **`raso`** (RAS/reliability).
They all use the same flags and write through the **`/etc/tunables`** directory.

### `/etc/tunables` files
- **`nextboot`** — values applied automatically at the next reboot (the only file
  applied automatically). Persisting a change writes here.
- **`lastboot`** — all tunable values as set at the last boot (read-only,
  owned by root). **`lastboot.log`** — changes/errors logged during the last boot.
- You can create extra named tunable files; apply one on demand with `tunrestore`.
  `DEFAULT` in `nextboot` means "use the default at boot".

### Common flags (identical across `no`/`vmo`/`ioo`/`schedo`/`raso`)
```
-a                 display all tunables (current; reboot values with -r; permanent with -p)
-o tunable[=value] display, or set, a tunable
-d tunable         reset one tunable to its default
-D                 reset ALL tunables to default
-p                 with -o/-d/-D: apply to BOTH current and reboot (persist to nextboot)
-r                 with -o/-d/-D: apply to the REBOOT value only (takes effect next boot)
-h [tunable]       help / description of a tunable
-L [tunable]       list characteristics (current, default, reboot, min/max, unit, type)
-x [tunable]       same as -L in CSV form
-F                 force display of RESTRICTED tunables (with -a/-L/-x)
```
```sh
no   -L tcp_recvspace          # see current/default/reboot/range/type for one tunable
no   -p -o tcp_recvspace=262144 -o tcp_sendspace=262144   # set now + persist
vmo  -p -o minperm%=3 -o maxperm%=90
ioo  -a                        # all I/O tunables
schedo -p -o vpm_throughput_mode=2
no   -d tcp_recvspace          # reset one to default (current+nextboot needs -p)
```

### Tunable parameter **types** (govern when a change takes effect)
| Type | When the change applies |
|------|--------------------------|
| **Dynamic** | immediately, no reboot |
| **Static** | cannot be changed |
| **Reboot** | only at reboot (set with `-r`) |
| **Bosboot** | requires `bosboot` + reboot |
| **Mount** | affects only future mounts |
| **Incremental** | can only be increased (except at boot) |
| **Connect** | affects future socket connections |

`-L` shows each tunable's type — check it before expecting a change to take hold.

### Tunable file-manipulation commands
```sh
tunchange -f mytune -t vmo -o minperm%=5     # edit a value in a stanza file
tunsave   -f mytune                          # save current tunables to a file
tuncheck  -f mytune                          # VALIDATE a hand-made file (required before use)
tunrestore -f mytune                         # apply a file's values now
tunrestore -r -f mytune                      # stage a file to be applied at next boot
tundefault [-r]                              # reset all tunables to default (now / next boot)
```
Hand-edited tunable files **must** pass `tuncheck` before `tunrestore`.

### Reboot tuning & recovery procedure
- **Reboot tuning:** Reboot-type tunables go into `nextboot` (via `-r`/`-p`) and
  apply on the next restart; Bosboot-type also need `bosboot` first.
- **Recovery (bad tunable hangs/slows boot):** boot to a known-good state and reset
  — `tundefault -r` then reboot, or restore a good file with `tunrestore -r -f`.
  Because `lastboot` captures the prior values, you can rebuild `nextboot` from it.
- **SMIT:** `smitty tuning` (or `smitty <no|vmo|ioo|schedo>`) edits current and
  reboot values via menus.

### Restricted tunables
Many tunables are **restricted** (hidden unless `-F`) — changing them can degrade
or destabilize the system and should only be done under **IBM support guidance**.
Changing a restricted tunable is flagged in the error log.

### Method
Record a baseline (`nmon -f -s 30 -c 120`), identify the bottleneck (CPU vs
memory/paging vs disk vs network), change **one** tunable, measure, keep or revert.
Persist with `-p` only once validated. Note the tunable's **type** (above) so you
know whether a reboot/bosboot is required.

## Performance — trace-based analysis & profiling

The AIX **trace** facility feeds the deep-analysis tools; capture once, post-process
with several reporters.

```sh
trace -a -o /tmp/trace.raw ; sleep 10 ; trcstop      # capture kernel trace
trcrpt /tmp/trace.raw | less                         # human-readable trace report
```

| Tool | Purpose |
|------|---------|
| **`curt`** | CPU Utilization Reporting Tool — converts a trace into per-process/thread/pthread CPU stats, system-call and interrupt time; shows where CPU went |
| **`splat`** | Simple Performance Lock Analysis Tool — lock contention report (kernel simple/complex locks, PThread mutexes/rwlocks/condvars) from a trace |
| **`tprof`** | Versatile CPU profiler — CPU usage by process, then by application / routine / **source line**; `tprof -x "<cmd>"` profiles a command |
| **`svmon`** | In-depth memory analysis — snapshot of real/virtual/paging memory; `svmon -G` (global), `svmon -P <pid>` (per process), `svmon -S` (segments) |
| **`procmon`** | Process-monitor tool — live, sortable process table; filter and run actions (renice/kill/svmon) on processes. *Optional* — ships in the `bos.perf.gtools` Performance-Toolbox fileset; verified **absent** on a stock AIX 7.3 install, so check `which procmon` / `lslpp -l bos.perf.gtools` before relying on it (`topas -P` is an always-present alternative) |
| **`filemon` / `netpmon`** | Trace-based file-I/O and network profilers |
| **`prof` / `gprof`** | Compile-time profilers (`-p`/`-pg`) for your own programs; plus the `timing` commands (`time`, `timex`) |
| **`perfstat` / RSI API** | C APIs for programmatic metrics (`perfstat_cpu`, `_memory_total`, …) and the Remote Statistics Interface for building monitors |

Typical flow: `topas`/`nmon` to spot the bottleneck → `tprof` (CPU hot code),
`svmon` (memory), `splat` (locks), or `filemon`/`netpmon` (I/O) to drill in →
adjust a tunable → re-measure.
