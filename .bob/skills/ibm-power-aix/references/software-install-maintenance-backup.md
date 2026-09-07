# Software, Maintenance & Backup

Filesets, patching, cloning, and backup (SKILL.md §2 & §5).

## Filesets & levels

AIX software ships as **filesets** (`bos.net.tcp.client`, `devices.*`, …). Levels:
**Version.Release.TL.SP** — `oslevel -s` (e.g. `7300-02-01-2346`).

```sh
oslevel -s                       # OS + Technology Level + Service Pack
lslpp -l                         # all installed filesets + state (COMMITTED/APPLIED)
lslpp -l "bos.net.*"             # filtered
lslpp -w /usr/bin/ksh            # which fileset owns a file
lslpp -h bos.mp64                # install history of a fileset
instfix -i -k IJ12345            # is APAR IJ12345 installed?
instfix -icqk 7300-02_AIX_ML     # is a TL fully installed?
```

## Install / update / remove

```sh
installp -acgXYd /dev/cd0 bos.adt              # apply+commit, auto-deps, expand FS, accept-license
installp -acgXYd . all                          # everything in the current dir
installp -C                                     # clean up an interrupted install
installp -r                                     # reject APPLIED (not committed) updates
installp -u bos.adt.samples                     # uninstall a fileset
smitty install_update / smitty update_all       # guided
```
- **Apply vs commit:** `-a` applies (reversible via reject, keeps the old version);
  `-c` commits (frees the saved old version — irreversible). Apply → verify →
  commit when stable.
- `-X` auto-expands file systems if space is short; `-g` pulls in requisites.

## Patches — SUMA

**Service Update Management Assistant** downloads fixes (TL/SP/APAR/security) from
IBM Fix Central on a schedule or on demand.

```sh
suma -x -a Action=Preview  -a RqType=Latest                 # preview latest updates
suma -x -a Action=Download -a RqType=TL -a RqName=7300-03   # download a TL to the repo
# then apply with installp / smitty update_all from the downloaded directory
```
Use a **compare report** (`smitty compare_report`) to see what's missing vs a
target level. Always preview, download to a repo, take a backup, then apply.

## Interim fixes (iFixes / emgr)

```sh
emgr -l                  # list installed interim fixes
emgr -e IJ12345.epkg.Z   # install an iFix package
emgr -c -L <label>       # check an iFix
emgr -r -L <label>       # remove an iFix
```
iFixes are temporary; remove them before applying the TL/SP that includes the
permanent fix.

## Clone the OS (alt_disk) — bootable fallback

Clone rootvg to a spare disk so you can boot back if an update breaks the system.

```sh
alt_disk_copy -d hdisk1                    # clone running rootvg -> hdisk1 (altinst_rootvg)
alt_rootvg_op -W -d hdisk1                 # wake up the clone to inspect/modify
alt_rootvg_op -S                           # put it back to sleep
alt_rootvg_op -X altinst_rootvg            # remove the clone definition
alt_disk_mksysb -m /backup/mksysb -d hdisk1  # build an alt-disk from a mksysb image
bootlist -m normal hdisk1 hdisk0           # boot the clone next (then reboot to test an update)
```

## NIM (Network Installation Management)

Centralized network install/update at scale: a NIM **master** serves resources
(lpp_source, SPOT, mksysb, bosinst_data) to **clients** for `bos_inst`,
`cust`/`update_all`, and recovery — the standard way to install/patch many LPARs.

## Backup & recovery

```sh
# rootvg (the OS) — bootable system image:
mksysb -i /backup/$(hostname).mksysb        # -i regenerates image.data; add -e to exclude per /etc/exclude.rootvg
# non-rootvg data VG:
savevg -if /backup/datavg.savevg datavg     # -i image.data, -f file/device
restvg -f /backup/datavg.savevg hdisk5      # recreate VG+LV+FS+data on a target disk
lsmksysb -lf /backup/x.mksysb               # inspect a mksysb
# files:
tar -cvf /backup/a.tar /home/app  ;  cpio ;  backup -0 -uf /dev/rmt0 /home  /  restore -xvf
```
**mksysb is the primary recovery path** — restore by booting the image (or via NIM)
to the same or different hardware (device filesets allow cross-hardware restore).
Take one before major changes and on a schedule.
