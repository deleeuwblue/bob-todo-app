# System Management & Devices

SMIT, ODM, SRC, and device handling (SKILL.md §1).

## SMIT (System Management Interface Tool)

```sh
smitty                 # top menu
smitty <fastpath>      # jump straight to a task (e.g. smitty mkuser, smitty jfs2, smitty tcpip)
smit                   # Motif/X11 version
```
- **F6** in any dialog shows the **exact command** SMIT will run — the fastest way
  to learn the direct command.
- Logs: `~/smit.log` (full output + the commands) and `~/smit.script` (just the
  commands, reusable as a script). `smit -s /path/script -l /path/log` to redirect.
- Useful fastpaths: `mkuser`, `chuser`, `lsuser`, `jfs2`, `lvm`, `mkvg`, `storage`,
  `tcpip`, `mktcpip`, `nfs`, `install_update`, `update_all`, `suma`, `diag`,
  `errpt`, `crontab`, `chgsys`.

## ODM (Object Data Manager)

The binary configuration database behind devices, software (VPD), and SMIT menus.
Object classes live under `/etc/objrepos`, `/usr/lib/objrepos`, `/usr/share/lib/objrepos`.

```sh
odmget CuDv                       # Customized Devices (configured devices)
odmget -q "name=hdisk0" CuAt      # Customized Attributes for a device
odmget PdDv                       # Predefined Devices (supported types)
```
Key classes: `CuDv`/`CuAt` (customized device + attrs), `PdDv`/`PdAt` (predefined).
**Edit via the high-level commands** (`chdev`, `mkdev`, `rmdev`) — direct
`odmadd`/`odmdelete`/`odmchange` only as a last resort; corrupting the ODM breaks
device config.

## SRC (System Resource Controller)

Manages daemons as **subsystems** (and subservers / groups).

```sh
lssrc -a                       # all subsystems + status
lssrc -s sshd                  # one subsystem
lssrc -g tcpip                 # a subsystem group
startsrc -s sshd               # start
stopsrc -s sshd                # stop
refresh -s inetd               # reload config without restart
```

## Devices

Devices are discovered into the ODM and are either **`Available`** (usable) or
**`Defined`** (known but not active).

```sh
cfgmgr                         # detect & configure newly attached devices
cfgmgr -l fcs0                 # configure a specific parent's children
lsdev -C                       # all customized (configured) devices
lsdev -Cc disk                 # by class (disk, adapter, tape, …)
lsdev -p fcs0                  # children of a parent
lsattr -El hdisk0              # editable attributes + current values
lsattr -El sys0                # system attributes (e.g. realmem, maxuproc)
lscfg -vpl hdisk0              # detailed VPD (serial, microcode, location code)
prtconf                        # system summary: model, serial, memory, firmware, devices
chdev -l hdisk0 -a queue_depth=32           # change an attr (device may need to be unused)
chdev -l sys0 -a maxuproc=4096              # change a system attr
rmdev -dl hdisk0               # remove (-d delete from ODM, -l just to Defined)
mkdev -l <device>              # make a Defined device Available
```
- `chdev` on a busy device may require `-P` (apply at next boot) if it can't change
  live.
- **Location codes** from `lscfg` identify physical slot/port — essential for
  hardware service and matching `errpt` resource names.
