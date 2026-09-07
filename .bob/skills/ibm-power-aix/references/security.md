# AIX Security

AIX's layered security stack (SKILL.md §8). These features are powerful and can
lock you out — keep a root session open and a mksysb ready before high-impact
changes.

## RBAC (Role-Based Access Control)

Split all-powerful root into **roles** built from **authorizations**, assigned to
users — least privilege without sharing root.

```sh
lsauth ALL ; lsauth aix.system.config.cron        # authorizations (dotted hierarchy)
mkauth aix.mycompany.app                           # custom authorization
lsrole ALL ; lsrole RoleName                       # roles
mkrole authorizations=aix.fs.manage.mount,... RoleName
chuser roles=RoleName default_roles=RoleName alice # assign roles to a user
setkst                                             # commit role/auth/cmd/device DBs to the Kernel Security Tables (REQUIRED after changes)
swrole RoleName                                    # a user activates a role in a session
rolelist -a                                        # roles available to me
```
- Command/device privileges in `/etc/security/privcmds`, `/etc/security/privdevs`
  (manage with `setsecattr`/`lssecattr`, e.g.
  `setsecattr -c euid=0 accessauths=... innateprivs=... /path/cmd`).
- **`setkst` after any RBAC change** or the kernel tables are stale and changes
  don't take effect.
- **Domain RBAC** adds resource isolation: tag subjects/objects with domains
  (`mkdom`, `setsecattr -o domains=...`) so roles only act within a domain.
- Requires the **Enhanced RBAC** mode (default on modern AIX).
- **`sudo` as an alternative (verified in the field).** Not every AIX host uses
  RBAC roles — many put admins in a **`sudo`** group instead. If a privileged
  command returns *"file access permissions do not allow the specified action"* for
  a non-root user with no roles (`rolelist -a` empty), run it via **`sudo <cmd>`**
  (e.g. `sudo bootlist -m normal -o`, `sudo emgr -l`). Check `id` / `groups`: a
  `sudo` group + empty `rolelist` means use `sudo`, not `swrole`.

## Auditing

Kernel audit subsystem records security-relevant events by **class** (a named set
of **events**).

```sh
# config in /etc/security/audit/: config (classes/users), events, objects, bincmds/streamcmds
audit start                       # begin auditing
audit query                       # status
auditpr < /audit/trail            # format the binary trail to readable text
audit shutdown
```
Modes: **BIN** (batched binary trails) and **STREAM** (real-time). Define which
classes apply to which users in `config`.

## AIXpert (AIX Security Expert)

Apply and track a security **baseline** (hardening policy) across hundreds of
settings.

```sh
aixpert -l high|medium|low|default     # apply a predefined hardening level
aixpert -l h -n -o /etc/security/aixpert/myrules.xml   # write the policy without applying
aixpert -a -o applied.xml              # apply from a custom XML
aixpert -c                             # check current config vs the applied policy
aixpert -u                             # undo (revert to pre-AIXpert)
```
Files in `/etc/security/aixpert/`. **`high`** disables many services and tightens
network/login settings — review before applying to a production box; keep a way back.

## Trusted Execution (TE)

Verify binary **integrity** against the **Trusted Signature Database (TSD)** —
detect or block tampered system binaries.

```sh
trustchk -n ALL                   # offline check all TSD entries (report mismatches)
trustchk -y ALL                   # check and auto-fix where possible
trustchk -p TE=ON CHKEXEC=ON      # online: enforce at exec time (block unverified binaries)
trustchk -p TEP=ON                # Trusted Execution Path
trustchk -s /usr/bin/mycmd        # add/update a file in the TSD
```
Online mode can **block execution** of unverified binaries — test offline first.

## Encrypted File System (EFS)

Per-file encryption keyed to user **keystores** (on JFS2).

```sh
efsenable -a                      # enable EFS on the system (creates keystores)
efskeymgr -V                      # show a user's keys ; -o ... key ops
# then, as the user:
mkdir secret ; efsmgr -e secret   # mark a directory for encryption (new files inherit)
efsmgr -l file                    # list encryption info
efsmgr -d file                    # decrypt
```
Encryption follows the user's key — losing the keystore/password (no recovery key)
means losing the data. Back up keystores. Works per-file; root can be excluded.

## Firewall (IP filtering)

Stateful/stateless packet filtering built into AIX.

```sh
mkfilt -v4 -a                     # activate IPv4 filter rules
genfilt -v4 -a P -s 10.0.0.0 -m 255.0.0.0 -d 0.0.0.0 -c tcp -O eq -P 22   # add a permit rule
lsfilt -v4                        # list rules
chfilt / rmfilt                   # change / remove a rule
mkfilt -v4 -d                     # deactivate
```
Default action and rule order matter — a too-tight default with no permit for your
SSH source will lock you out. Test from the console / keep a session.

## IPsec

Encrypted/authenticated tunnels between hosts (built on the filter engine).

- Define tunnels (manual or IKE) with `gentun`/`mktun`/`lstun`/`chtun`; activate
  with `mktun -t <id>`. Manage IKE policies via `ikedb` / SMIT (`smitty ipsec4`).
- Reports and modes via `ipsecstat`. Use for host-to-host or gateway encryption
  where the network is untrusted.

## Be conservative

RBAC role changes (+`setkst`), **AIXpert high**, Trusted Execution online mode, EFS,
and firewall/IPsec rules can deny access or block binaries. Before any of them:
confirm scope with the user, keep a privileged session open, and have a mksysb /
`aixpert -u` rollback path.
