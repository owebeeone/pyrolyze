from __future__ import annotations

import os
import subprocess
import sys


def test_sparse_qt_compilation_keeps_unrelated_groups_cold() -> None:
    source = '''
import sys
import pyrolyze
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.backends.lazy_library import LazyLibraryCatalog
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt
from pyrolyze.unified.qt import QtUx
assert isinstance(Qt.WIDGET_SPECS, LazyLibraryCatalog)
assert 'pyrolyze.backends.pyside6.learnings' not in sys.modules
prefix = 'pyrolyze.backends.pyside6._generated.family_'
assert not any(name.startswith(prefix) for name in sys.modules)
load_transformed_namespace('from pyrolyze.unified.qt import QtUx\\n'
                          'from pyrolyze.api import pyrolyze\\n'
                          '@pyrolyze\\ndef panel() -> None:\\n    QtUx.CQLabel(text="hello")\\n',
                          module_name='sparse_qt_panel')
loaded = [name for name in sys.modules if name.startswith(prefix)]
assert len(loaded) == 1, loaded
assert QtUx.CQLabel is Qt.CQLabel
assert len(Qt.WIDGET_SPECS) == 105
'''
    result = subprocess.run([sys.executable, "-c", source], env=os.environ.copy(),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
