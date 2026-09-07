# IBM AIX — Agent Skill

Equip any skills-compatible Bob AI agent to administer the **IBM AIX** operating system on IBM Power Systems —
correctly, without Linux assumptions.

> A knowledge/command skill (no API/SDK). Built from *AIX, PowerVM – UNIX,
> Virtualization, and Security* and standard AIX practice.

## What it covers

| Area | Topics |
|------|--------|
| **System management** | SMIT, ODM, SRC subsystems, device discovery & config |
| **Software** | Filesets/`installp`/`lslpp`, levels, SUMA patching, iFixes (`emgr`), `alt_disk`, NIM |
| **Open source** | AIX Toolbox for Open Source Software — DNF bootstrap (`dnf_aixtoolbox.sh`), `dnf`/`rpm`, `/opt/freeware`, local mirror |
| **Build from source** | clang/LLVM (18.1.8 ppc64 prebuilt) + GCC/XL, AIX dev filesets, `OBJECT_MODE`/`-maix64`, runtime linking, `blibpath`, TOC overflow, autotools/cmake |
| **Storage** | LVM (PV/VG/LV), mirroring, SAN/MPIO |
| **File systems** | JFS2 create/grow/shrink, ACLs (AIXC/NFS4), snapshots, paging space |
| **Backup** | mksysb (rootvg), savevg/restvg, tar/cpio |
| **Boot & diagnostics** | bootlist/bosboot/inittab, error log (`errpt`), syslog, diag |
| **Networking** | TCP/IP config, name resolution, inetd/SSH/NFS, `no` tunables |
| **Users & scheduling** | mkuser/chuser/chsec, cron/at |
| **Security** | RBAC, auditing, AIXpert, Trusted Execution, EFS, firewall, IPsec |
| **Performance** | topas/nmon/vmstat/iostat/lparstat; tuning no/vmo/ioo/schedo |

## Why it's reliable

- **SMIT as front-end + audit trail.** Discover the exact command (F6) and its log
  (`~/smit.script`), then script the direct command.
- **AIX ≠ Linux, stated up front.** ODM-managed devices, filesets not rpm/apt,
  mandatory LVM, JFS2 + `/etc/filesystems` — the habits that bite Linux admins.
- **Safe on irreversible/boot-critical actions.** `bosboot` after boot changes,
  apply-then-commit, mksysb before major work, don't hand-edit `/etc/inittab`,
  security-lockout warnings with rollback paths.

## Install

```bash
cp -r ibm-power-aix ~/.bob/skills/
```

## Structure

```
ibm-power-aix/
├── SKILL.md                              # the skill — 12 sections, loaded by the agent
├── README.md                             # this listing
└── references/                           # loaded on demand
    ├── system-management-and-devices.md
    ├── software-install-maintenance-backup.md
    ├── aix-toolbox-open-source.md
    ├── build-from-source-toolchain.md
    ├── storage-lvm-filesystems.md
    ├── networking-scheduling.md
    ├── security.md
    └── boot-problem-determination-performance.md
```

## Requirements / scope

- Guidance for administering an AIX system over its shell/SMIT — not a service
  client. Verify command flags against the running AIX level (`oslevel -s`); options
  vary across Technology Levels.
- Pairs with the **ibm-power-vm** skill for the virtualization layer (HMC/LPAR/VIOS)
  beneath the OS.

## License / source
MIT
