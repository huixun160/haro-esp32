# ListenAI ARCS SDK - AI Context

This file provides persistent project context for AI systems working in this repository.

---

## Project

**Name:** ListenAI ARCS SDK Documentation Workspace  
**Platform:** ListenAI ARCS SDK  
**Primary Targets:** `arcs_evb`, `arcs_mini`  
**Host Environment:** Linux is the officially supported development host for SDK build and debug workflows

---

## Current Focus

This repository context has been rewritten to align with ListenAI ARCS SDK materials.

The working assumption is:

- we are documenting and analyzing the ListenAI ARCS SDK
- we only retain ListenAI-related content in `AIOS/docs`
- old Unisoc / Mocor / DAP / feature-phone platform assumptions are no longer authoritative

If older files elsewhere in the repository still mention AIOS feature-phone architecture, treat them as legacy context unless explicitly revalidated.

---

## Platform Understanding

Based on the current official ListenAI documentation set, the practical development flow is:

1. initialize the SDK environment with `env.sh`
2. select a board such as `arcs_evb` or `arcs_mini`
3. build samples or custom projects with `build.sh`
4. flash images with `tools/burn/cskburn`
5. debug with UART logs and, when needed, GDB + J-Link
6. extend functionality through SDK components and drivers

---

## Architecture Layers

```text
Application / Samples
  - samples/modules
  - samples/network
  - samples/algorithms

Component Layer
  - lisa_log
  - lisa_modem
  - lisa_bt_audio_framework
  - filesystem
  - player / tone / LVGL related components

Driver Layer
  - lisa_device
  - lisa_audio / lisa_camera / lisa_display
  - lisa_gpio / lisa_i2c / lisa_spi / lisa_uart
  - lisa_sdmmc / lisa_pwm / lisa_rtc / lisa_wdt

Board Support / ARCS Adaptation
  - arcs_evb
  - arcs_mini
  - *_arcs.c platform adaptation files

Hardware
  - ARCS platform peripherals and connected external devices
```

---

## Key Constraints

- Official SDK build workflows currently target Linux hosts.
- Documentation should prefer ListenAI official sources over inference.
- API descriptions should follow the public ARCS SDK docs and doxygen API reference.
- Board-specific behavior must be identified as `arcs_evb` or `arcs_mini` when relevant.
- Do not reintroduce Unisoc-specific claims unless the source is explicitly part of the current ListenAI context.

---

## Primary Documentation in This Repo

The local documentation root is now:

- [AIOS/docs/README.md](C:/duance/linsi/AIOS/docs/README.md)
- [AIOS/docs/architecture/platform_overview.md](C:/duance/linsi/AIOS/docs/architecture/platform_overview.md)
- [AIOS/docs/architecture/capability_map.md](C:/duance/linsi/AIOS/docs/architecture/capability_map.md)
- [AIOS/docs/runbooks/environment_setup.md](C:/duance/linsi/AIOS/docs/runbooks/environment_setup.md)
- [AIOS/docs/runbooks/build_flash_debug.md](C:/duance/linsi/AIOS/docs/runbooks/build_flash_debug.md)
- [AIOS/docs/api/api_reference_overview.md](C:/duance/linsi/AIOS/docs/api/api_reference_overview.md)
- [AIOS/docs/knowledgebase/knowledgebase_index.md](C:/duance/linsi/AIOS/docs/knowledgebase/knowledgebase_index.md)

Module-level summaries are kept under:

- `AIOS/docs/api/modules/`

Current module coverage includes:

- `audio`
- `bluetooth`
- `camera`
- `device`
- `filesystem`
- `gui_mmi`
- `hal`
- `logger`
- `network`
- `os_core`

---

## Important Official Sources

When extending docs, prefer these source families first:

- Quick start:
  - <https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- GDB debug:
  - <https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html>
- Board docs:
  - `arcs_evb`
  - `arcs_mini`
- SDK API reference:
  - <https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/annotated.html>
- API file index:
  - <https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>

---

## Common Development Paths

### Environment setup

```bash
source env.sh
source env.sh check
```

### Build sample

```bash
./build.sh -C -S samples/helloworld -DBOARD=arcs_evb
```

### Flash

```bash
./tools/burn/cskburn -s /dev/ttyUSB0 -b 3000000 0x0 build/helloworld.bin -C arcs
```

### Resource image packaging

```bash
./mkfatfs.py -o disk.img -s 32M -d resources -l SD -v
```

---

## API Reference Reading Strategy

For driver-level work, use this order:

1. `files.html` to identify the correct driver family
2. `annotated.html` to inspect public structs
3. specific `*_8h.html` and `*_8c.html` pages for functions, macros, enums, and variables

This is especially important for:

- `lisa_camera`
- `lisa_display`
- `lisa_audio`
- `lisa_device`
- storage and peripheral driver families

---

## Repo Guidance for AI Systems

- treat `AIOS/docs` as the authoritative local documentation set for ListenAI content
- preserve concise, source-backed summaries rather than speculative API expansion
- when adding new material, link it back to official ListenAI docs
- prefer updating existing docs over creating parallel overlapping notes
