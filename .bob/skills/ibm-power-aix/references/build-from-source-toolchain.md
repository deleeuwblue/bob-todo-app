# Building from Source on AIX (ppc64) — Compilers & Toolchain

Compiling open-source software on AIX/POWER differs from Linux in real ways (the
AIX linker, archive/shared-library model, object mode, library paths). This covers
the **clang/LLVM** prebuilt toolchain plus the AIX ppc64 essentials. (SKILL.md §2b.)

## Choose a compiler

| Option | When | Notes |
|--------|------|-------|
| **GCC** (AIX Toolbox) | Most open-source; simplest | `dnf install gcc gcc-c++ gcc-gfortran` → `/opt/freeware/bin/gcc` |
| **clang / LLVM** (LLVM.org prebuilt) | Projects needing Clang/LLVM, modern C++, LLVM-based langs (Rust, etc.) | community build; see below |
| **IBM Open XL C/C++** (clang-based) / legacy **XL C/C++** | IBM-supported, best POWER optimization | licensed product, not covered here |

GCC and clang can coexist (and with XL). Pick per project; set `CC`/`CXX` to choose.

## Install the clang+LLVM 18.1.8 prebuilt (powerpc64-ibm-aix)

Prebuilt asset from the LLVM release:
`clang+llvm-18.1.8-powerpc64-ibm-aix-7.2.tar.xz`
(https://github.com/llvm/llvm-project/releases/tag/llvmorg-18.1.8) — built for **AIX
7.2** and runs on **7.2 and later** (incl. 7.3).

```sh
# prerequisites (system assembler/linker/headers + extractor) — see "Prerequisites" below
cd /tmp
curl -kLO https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.8/clang+llvm-18.1.8-powerpc64-ibm-aix-7.2.tar.xz
# extract (GNU tar handles .xz; or: xz -dc file | tar -xvf -)
mkdir -p /opt/llvm-18.1.8
gtar -C /opt/llvm-18.1.8 --strip-components=1 -xJf clang+llvm-18.1.8-powerpc64-ibm-aix-7.2.tar.xz
# put it on PATH (and ahead of other compilers if you want clang to win)
export PATH=/opt/llvm-18.1.8/bin:$PATH
clang --version            # PowerPC64 ... ibm ... aix
```

The tarball ships `clang`/`clang++`, `lld`, and the LLVM tools (`bin/include/lib/
libexec/share`). Clang **drives the AIX system linker (`/usr/bin/ld`) and
assembler (`/usr/bin/as`)** — so the AIX dev filesets must be present (below).

> **Verified on AIX 7.3 / POWER11 (this prebuilt = compiler-only):** the
> `clang+llvm-18.1.8-powerpc64-ibm-aix` tarball ships **no C++ standard library** —
> there is no `libc++` and no `libstdc++` under its `include`/`lib`. So:
> - **C compiles and runs out of the box** with `clang` (validated).
> - **For C++, use `g++` from the AIX Toolbox** (`dnf install gcc-c++`, GCC 13.x) —
>   it works cleanly (validated). Using **`clang++`** for C++ means wiring it to
>   GCC's libstdc++ headers (`-nostdinc++ -I/opt/freeware/lib/gcc/<tgt>/<ver>/include/c++[/<tgt>]`)
>   **and** its runtime, which is fragile (ABI/symbol mismatches were observed even
>   with `-Wl,-brtl`). **Recommendation: clang for C + LLVM tooling, g++ for C++.**

### Prerequisites (AIX base dev filesets + extractor)
The system needs the **application-development filesets** for headers, `ld`, `as`,
`ar`, `make`:
```sh
lslpp -L bos.adt.base bos.adt.include bos.adt.lib bos.adt.libm bos.adt.utils
# install missing ones from AIX media: installp -acgXYd <src> bos.adt.base bos.adt.include bos.adt.lib bos.adt.libm bos.adt.utils
```
For `.tar.xz` you need `xz`/`gtar` (`dnf install xz tar`). Build tools come from the
AIX Toolbox: `dnf install gmake cmake ninja-build autoconf automake libtool pkgconfig m4 bison flex git`.

## AIX ppc64 essentials (the things that bite)

### Object mode — `OBJECT_MODE=64`
AIX binutils (`ar`, `nm`, `dump`, `ld`) default to **32-bit** object mode and will
*silently ignore* 64-bit objects. For 64-bit builds:
```sh
export OBJECT_MODE=64        # makes ar/nm/dump/ld handle 64-bit objects
```
Equivalently use `-X64` per tool: `ar -X64 …`, `nm -X64 …`, `dump -X64 …`. Compile
64-bit with clang/gcc **`-maix64`** (the powerpc64 toolchain targets 64-bit; pass
`-maix32` for 32-bit). Mismatched object mode is the #1 "ld: 0711-xxx … not a valid
object" failure.

### Shared libraries & runtime linking (very AIX-specific)
- **`.a` archives can contain shared objects.** On AIX a library is often
  `libfoo.a` holding a `shr.o` (32-bit) and/or `shr_64.o` (64-bit) member — *not* a
  bare `libfoo.so`. Builds that hard-code `.so` names need patching or
  `--with-aix-soname=svr4`-style options.
- **Runtime linking is opt-in.** AIX binds shared symbols at link time by default.
  For `dlopen`/plugins and Linux-like behavior, enable runtime linking:
  `-Wl,-brtl` (and often `-Wl,-bexpall` to export all symbols, or an explicit
  export file via `-Wl,-bE:exports`).
- **Create a shared library:** `clang -maix64 -shared -Wl,-brtl -Wl,-bexpall -Wl,-bnoentry -o libfoo.so *.o`
  (or build a proper `.a` with a `shr_64.o` member for the AIX convention).
- **No GNU `-rpath`.** AIX uses **`-Wl,-blibpath:/p1:/p2:/usr/lib:/lib`** at link
  time, or set **`LIBPATH`** at runtime (the AIX analog of `LD_LIBRARY_PATH`).
  Keep `/usr/lib:/lib` in `blibpath` or you'll break the binary.

### Large programs — TOC overflow
Big binaries overflow the TOC: link with **`-Wl,-bbigtoc`** or compile with
**`-mcmodel=large`** (clang/gcc). Symptom: `ld: 0711-783 TOC overflow`.

### Misc
- Large files / 64-bit off_t in C: `-D_LARGE_FILES` (32-bit) — usually automatic at 64-bit.
- Threads: `-pthread`. Math: link `-lm`.
- `PKG_CONFIG_PATH=/opt/freeware/lib/pkgconfig` so `pkg-config` finds Toolbox libs.
- Prefer **`gmake`** (GNU make) over AIX `make` for open-source `Makefile`s.

## Typical build invocations

**Autotools:**
```sh
export OBJECT_MODE=64 PATH=/opt/llvm-18.1.8/bin:/opt/freeware/bin:$PATH
export CC=clang CXX=clang++ CFLAGS="-maix64 -O2" CXXFLAGS="-maix64 -O2" \
       LDFLAGS="-Wl,-brtl -Wl,-blibpath:/opt/freeware/lib:/usr/lib:/lib"
./configure --prefix=/opt/freeware && gmake -j4 && gmake install
```
(If shared-lib pain blocks you, `./configure --disable-shared --enable-static`.)

**CMake:**
```sh
export OBJECT_MODE=64
cmake -S . -B build -G Ninja \
  -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_C_FLAGS="-maix64" -DCMAKE_CXX_FLAGS="-maix64" \
  -DCMAKE_INSTALL_PREFIX=/opt/freeware -DBUILD_SHARED_LIBS=OFF
cmake --build build -j4 && cmake --install build
```

## Common errors → fixes

| Error | Cause → fix |
|-------|-------------|
| `ld: 0711-317 … symbol not found` | Missing export / runtime linking. Add `-Wl,-brtl -Wl,-bexpall` or an export file. |
| `ld: 0711-… not a valid object … XCOFF32` | Object-mode mismatch. `export OBJECT_MODE=64`; rebuild with `-maix64`; use `ar -X64`. |
| `ld: 0711-783 TOC overflow` | `-Wl,-bbigtoc` or `-mcmodel=large`. |
| `ar` ignores `.o` / "0707-126 … not valid" | 64-bit object with 32-bit `ar`. `OBJECT_MODE=64` or `ar -X64`. |
| build looks for `libfoo.so`, only `libfoo.a` exists | AIX shared-objects-in-archive. Adjust lib naming / use `--with-aix-soname`, or build static. |
| runtime "Could not load module … 0509-022" | `LIBPATH` doesn't include the lib dir. Set `LIBPATH` or link with `-Wl,-blibpath`. |
| `clang: error: unable to execute command: … as/ld` | AIX dev filesets missing. Install `bos.adt.base`/`bos.adt.include`/`bos.adt.lib`. |
| configure picks the wrong compiler | Set `CC`/`CXX` explicitly; put the desired `bin` first on `PATH`. |
| `clang++`: `'iostream' file not found` | The LLVM prebuilt has **no C++ stdlib**. Install `gcc-c++` (Toolbox) and **use `g++` for C++** — or point clang++ at GCC's libstdc++ headers (fragile). |
| `clang++` link: `0711-317 Undefined symbol: _ZSt4cout`/`__cxx11…` | clang++ not bound to GCC's libstdc++ runtime/ABI. Use `g++` for C++ (recommended); clang++↔libstdc++ interop is unreliable on AIX. |

## Quick reference

```sh
export OBJECT_MODE=64
export PATH=/opt/llvm-18.1.8/bin:/opt/freeware/bin:$PATH
clang -maix64 -O2 hello.c -o hello          # 64-bit executable
clang -maix64 -shared -Wl,-brtl -Wl,-bexpall -Wl,-bnoentry -o libx.so x.o
# link against Toolbox libs with a sane runtime path:
clang -maix64 prog.c -L/opt/freeware/lib -lfoo -Wl,-blibpath:/opt/freeware/lib:/usr/lib:/lib -o prog
```
