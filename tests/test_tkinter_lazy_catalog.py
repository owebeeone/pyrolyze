from __future__ import annotations

import os
import subprocess
import sys


def test_sparse_tk_compilation_keeps_unrelated_groups_cold() -> None:
    source = '''
import sys
import pyrolyze
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.backends.lazy_library import LazyLibraryCatalog
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk
from pyrolyze.unified.tk import TkUnifiedNativeLibrary
assert isinstance(Tk.WIDGET_SPECS, LazyLibraryCatalog)
assert 'pyrolyze.backends.tkinter.learnings' not in sys.modules
prefix = 'pyrolyze.backends.tkinter._generated.family_'
assert not any(name.startswith(prefix) for name in sys.modules)
load_transformed_namespace('from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk\\n'
                          'from pyrolyze.api import pyrolyze\\n'
                          '@pyrolyze\\ndef panel() -> None:\\n    Tk.CLabel(text="hello")\\n',
                          module_name='sparse_tk_panel')
loaded = [name for name in sys.modules if name.startswith(prefix)]
assert len(loaded) == 1, loaded
assert len(Tk.WIDGET_SPECS) == 105
assert TkUnifiedNativeLibrary().native_library_type is Tk
'''
    result = subprocess.run([sys.executable, "-c", source], env=os.environ.copy(),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
