# Storage — LVM, File Systems, Paging

LVM hierarchy, JFS2, ACLs, snapshots, SAN/MPIO, paging (SKILL.md §3–§4).

## LVM hierarchy

**PV** (physical volume = `hdiskN`) → **VG** (volume group) → **LV** (logical
volume) → **file system**. The PP (physical partition) is the allocation unit.

```sh
lspv                         # physical volumes + VG membership
lspv -l hdisk0               # LVs on a PV
lsvg                         # volume groups
lsvg rootvg                  # VG detail: PP size, TOTAL/FREE PPs, etc.
lsvg -l rootvg               # LVs in the VG
lsvg -p rootvg               # PVs in the VG + free PPs
lslv hd2                     # LV detail
lslv -l hd2                  # LV-to-PV distribution
```

### Volume groups
```sh
mkvg  -S -y datavg -s 64 hdisk1 hdisk2     # scalable VG, 64 MB PPs
extendvg datavg hdisk3                      # add a PV
reducevg datavg hdisk3                      # remove a PV (must be empty of LV data)
varyonvg datavg ; varyoffvg datavg          # activate / deactivate
importvg -y datavg hdisk1 ; exportvg datavg # move a VG between systems
```
VG types: standard, **big**, **scalable** (`-S`, most LVs/PVs — preferred for new
VGs). rootvg holds the OS.

### Logical volumes
```sh
mklv -t jfs2 -y datalv datavg 20            # 20 PPs
mklv -t jfs2 -c 2 -y mirlv datavg 20        # 2 copies (mirrored)
extendlv datalv 10                          # grow by 10 PPs
mklvcopy datalv 2 ; rmlvcopy datalv 1       # add/remove a mirror copy
migratepv hdisk1 hdisk4                      # move all LV data off a PV (then reducevg)
mirrorvg datavg ; unmirrorvg datavg          # mirror/unmirror a whole VG
reorgvg datavg                               # rebalance allocation
```

## SAN & MPIO

SAN LUNs appear as `hdiskN` reached over multiple **paths**.

```sh
lsdev -Cc disk                  # SAN disks (often MPIO ... FC)
lspath                          # all paths (Enabled/Failed/Missing) per hdisk
lspath -l hdisk5                # paths for one disk
lsmpio -l hdisk5                # MPIO path detail (adapter, status)
chpath -l hdisk5 -p fscsi0 -s disable|enable    # disable/enable a path
chdev -l hdisk5 -a algorithm=shortest_queue -a reserve_policy=no_reserve   # tuning (device idle)
rmdev -Rl fcs0 ; cfgmgr        # rescan the fabric
```
For shared disks (clusters / NPIV), set `reserve_policy=no_reserve` so multiple
hosts can access the LUN.

## JFS2 file systems

Default FS; defined in `/etc/filesystems`, backed by an LV.

```sh
crfs -v jfs2 -g datavg -m /data -A yes -a size=20G   # create FS (+ its LV) , auto-mount at boot
crfs -v jfs2 -d datalv -m /data -A yes               # create FS on an existing LV
mount /data ; umount /data ; mount -a ; mount        # mount/unmount/all/show
chfs -a size=+10G /data                              # GROW online (+N), or set absolute size
chfs -a size=-5G /data                               # SHRINK (JFS2, supported levels) — back up first
chfs -A yes -a options=rw /data                       # change mount-at-boot / options
rmfs /data                                           # remove FS (and optionally its LV)
fsck -y /dev/fslv00                                  # check (unmount first)
lsfs ; lsfs -q /data ; df -g                          # list / detail / usage
```
JFS2 features: large files, online grow (and shrink), snapshots, compression,
encryption (EFS). Inline vs outline JFS2 log.

## ACLs

Two models — manage with `aclget` / `aclput` / `acledit` / `aclconvert`:
- **AIXC** (AIX Classic) — base perms + extended `permit/deny` entries.
- **NFS4** — fine-grained ACEs (allow/deny, inheritance), needed for NFSv4 / richer
  control. Convert with `aclconvert -t NFS4 <path>`.

## Snapshots (JFS2)

Point-in-time images of a filesystem:
```sh
snapshot -o snapfrom=/data -o size=1G        # internal snapshot
snapshot -q /data                             # list snapshots
mount -v jfs2 -o snapshot /dev/<snaplv> /mnt  # access a snapshot read-only
snapshot -d /dev/<snaplv>                     # delete
```
Snapshots use copy-on-write — size them for the expected change rate; a full
snapshot LV invalidates the snapshot.

## Paging space (swap)

```sh
lsps -a ; lsps -s                  # paging spaces + summary (% used)
mkps -a -n -s 8 datavg             # new 8-PP paging space, activate now (-a) and at boot (-n)
chps -s 4 paging00                 # grow by 4 PPs ; chps -d to shrink
chps -a n paging01                 # don't activate at next boot (then remove)
rmps paging01                      # remove (must be deactivated)
swapon -a ; swapoff /dev/paging01  # activate all / deactivate one
```
Default paging space is `hd6` in rootvg. Keep multiple paging spaces similar in
size and ideally on separate disks for performance.
