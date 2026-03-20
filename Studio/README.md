# Studio Prototype

This folder contains Studio planning docs plus an architecture-aligned runnable
prototype that uses current PyRolyze capabilities without extending the framework.

## Run

From repo root:

```powershell
$env:PYTHONPATH='C:\Users\adria\Documents\Projects\py-rolyze-wip\src;C:\Users\adria\Documents\Projects\py-rolyze-wip'
uv run python Studio\run_studio_poc.py
```

Optional:

- `--root <path>`: initial explorer path
- `--smoke`: short startup smoke-run and auto-close

## Files

- [studio_poc.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/studio_poc.py): PyRolyze source UI prototype.
- [run_studio_poc.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/run_studio_poc.py): compatibility runner entrypoint.
- [host/app_host.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/host/app_host.py): primary host bootstrap and component loader.
- [ui/studio_root.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/ui/studio_root.py): declarative Studio UI root.
- [ui/elements.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/ui/elements.py): shared standard UIElement wrappers.
- [studio_logic.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/studio_logic.py): compatibility exports for filesystem/snapshot helpers.
- [Pyrolyze_As_Is_Findings.md](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/Pyrolyze_As_Is_Findings.md): capability/gap summary.

