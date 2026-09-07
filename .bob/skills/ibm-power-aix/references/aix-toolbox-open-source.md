# AIX Toolbox for Open Source Software (DNF / RPM)

The **AIX Toolbox for Open Source Software** is IBM's curated collection of
open-source packages (in **RPM** format) built for AIX — bash, python, gcc, curl,
git, vim, nginx, openssl, etc. The recommended package manager is **DNF** (the
next-generation replacement for YUM). (SKILL.md §2a.)

> Source: IBM "AIX Toolbox for Open Source Software — Get Started / Downloads /
> Resolving RPM issues" and the `dnf_aixtoolbox.sh` bootstrap script.

## Concepts

- Open-source software installs under **`/opt/freeware`** (binaries
  `/opt/freeware/bin`, libraries `/opt/freeware/lib`) — separate from the base AIX
  `/usr`. Add `/opt/freeware/bin` to `PATH`.
- Three layers: **`rpm.rte`** (the RPM runtime, an AIX *fileset*) → **DNF/YUM**
  (dependency-resolving package managers, themselves RPMs) → the **Toolbox RPMs**.
- Public repo base: **`https://public.dhe.ibm.com/aix/freeSoftware/aixtoolbox/`**
  - `INSTALLP/ppc/rpm.rte` — the RPM runtime prerequisite
  - `ezinstall/ppc/dnf_bundle_aix_71_72.tar` (AIX 7.1/7.2) · `dnf_bundle_aix_73.tar` (AIX 7.3)
  - `RPMS/ppc/` — the package repository DNF pulls from
  - `LICENSES/` — per-package license texts

## Bootstrap DNF (recommended path)

Run **`dnf_aixtoolbox.sh`** as **root** — it downloads the right `rpm.rte` and the
DNF bundle and installs everything:

```sh
# get the script (or use the copy you already have)
curl -k -o /tmp/dnf_aixtoolbox.sh \
  https://public.dhe.ibm.com/aix/freeSoftware/aixtoolbox/ezinstall/ppc/dnf_aixtoolbox.sh
chmod +x /tmp/dnf_aixtoolbox.sh
/tmp/dnf_aixtoolbox.sh -y          # see options below
```

Script options:
| Flag | Effect |
|------|--------|
| `-y` | Install DNF and **migrate yum3→yum4** (or install both) — `yum` and `dnf` both usable. **Recommended.** |
| `-d` | Install DNF **only** (no `yum` command) |
| `-n` | Let an existing `yum` and `dnf` **coexist** — *not recommended* |

Requirements: **AIX 7.1.3 or higher** (7.1 needs ≥7.1.3; 7.2/7.3 fine), run as
**root**, and outbound HTTPS to `public.dhe.ibm.com` (or a local mirror — see
below). The script verifies the OS level and current rpm/yum state before acting.

### Manual / offline bootstrap
If you can't run the script: download `rpm.rte` and install it with
`installp`/`geninstall`, then download the matching `dnf_bundle_*.tar`, extract it,
and run its `install_dnf.sh`. For air-gapped systems, use the **AIX Toolbox Media
Image** (ISO) and build a local repo (below).

## Using DNF

```sh
dnf check-update                     # refresh metadata / list updatable
dnf search <term>                    # find a package
dnf info <pkg>                       # details
dnf install <pkg>                    # install + auto-resolve dependencies
dnf install bash python3 git curl    # multiple
dnf list installed | head            # what's installed
dnf update [<pkg>]                   # update all / one
dnf remove <pkg>                     # uninstall (dnf autoremove for orphans)
dnf repolist                         # configured repositories
dnf clean all                        # clear cached metadata
```
- DNF config: **`/opt/freeware/etc/dnf/dnf.conf`**; repo files in
  **`/opt/freeware/etc/yum.repos.d/`** (the bootstrap points these at the public
  Toolbox repo). `yum` (yum4) is just a DNF front-end if installed with `-y`.

## Direct RPM (lower level)

```sh
rpm -qa                              # all installed RPMs
rpm -q <pkg> ; rpm -qi <pkg>         # query
rpm -ql <pkg>                        # files a package owns
rpm -qf /opt/freeware/bin/bash       # which package owns a file
rpm -ivh <file>.rpm                  # install a single RPM (NO dependency resolution)
rpm -Uvh <file>.rpm                  # upgrade
rpm -e <pkg>                         # erase
```
Prefer **DNF** — raw `rpm -i` fails on unmet dependencies, e.g.:
```
# rpm -i pango-1.40.1-...rpm
error: Failed dependencies: glib2 >= 2.33.12 is needed by pango-...
```
DNF resolves these automatically.

## Local / mirrored repository (air-gapped or faster)

```sh
# mount the AIX Toolbox Media ISO (or rsync RPMS/ppc to a local dir), then:
dnf install createrepo_c
createrepo /path/to/RPMS/ppc
# add a repo file in /opt/freeware/etc/yum.repos.d/local.repo:
#   [local-aixtoolbox]
#   name=Local AIX Toolbox
#   baseurl=file:///path/to/RPMS/ppc      (or http://your-mirror/…)
#   enabled=1
#   gpgcheck=0
dnf clean all ; dnf repolist
```

## Caveats & gotchas (from IBM guidance)

- **Don't shadow AIX filesets.** Some Toolbox packages deliver files that also come
  in base AIX filesets — **`openssl`, `libgcc`/`libstdc++` (gcc), `gettext`,
  `libiconv`**. Installing non-Toolbox builds of these, or mixing sources, causes
  unexpected behavior. Keep to AIX Toolbox builds and remove non-Toolbox duplicates.
- **LIBPATH discipline.** Do **not** set a global `LIBPATH` that loads other
  directories *before* `/opt/freeware/lib` — it breaks many AIX and Toolbox apps.
  Apply any app-specific LIBPATH via a wrapper/config for that app only.
- **Support model.** Toolbox RPMs are **not covered by AIX support**. Help comes
  from the **AIX Open Source Community Discussion forum** (defects, error messages,
  CVEs, dependency issues). For deep usage questions, consult each project's
  upstream community. Non-IBM-Toolbox RPMs: contact their source.
- **Architecture:** packages are `ppc`/`ppc64` for POWER; match your AIX level.
- **gpgcheck:** the public Toolbox repo packages are signed — keep `gpgcheck=1`
  where the key is imported; set `0` only for trusted local mirrors.

## Quick reference

| Goal | Command |
|------|---------|
| Bootstrap DNF | `./dnf_aixtoolbox.sh -y` (as root) |
| Install software | `dnf install <pkg>` |
| Find software | `dnf search <term>` |
| Update everything | `dnf update` |
| Remove software | `dnf remove <pkg>` |
| What owns a file | `rpm -qf <path>` |
| List repos | `dnf repolist` |
