"""Generated lazy native facade; definitions load by indexed group."""
from __future__ import annotations
from typing import Any, ClassVar
from collections.abc import Mapping
from frozendict import frozendict
from pyrolyze.api import MountSelector, UIElement, ui_interface
from pyrolyze.backends.model import UiInterface, UiInterfaceEntry, UiWidgetSpec
from pyrolyze.backends.lazy_library import LazyLibraryCatalog, LazyUiLibraryMeta
from .index import ENTRIES, GENERATION
from pyrolyze.backends.generated_package import admit_generated_package
admit_generated_package(__file__, GENERATION)

@ui_interface
class PySide6UiLibrary(metaclass=LazyUiLibraryMeta):
    ROOT_MODULE: ClassVar[str] = 'PySide6'
    _lazy_catalog = LazyLibraryCatalog(__package__, GENERATION, ENTRIES)
    def __getattr__(self, name: str) -> Any:
        return getattr(type(self), name)
    WIDGET_SPECS: ClassVar[Mapping[str, UiWidgetSpec]] = _lazy_catalog
    UI_INTERFACE = UiInterface(name='PySide6UiLibrary', owner=None, entries=frozendict({
            "CQAbstractButton": UiInterfaceEntry(public_name="CQAbstractButton", kind="QAbstractButton"),
            "CQAbstractItemView": UiInterfaceEntry(public_name="CQAbstractItemView", kind="QAbstractItemView"),
            "CQAbstractPrintDialog": UiInterfaceEntry(public_name="CQAbstractPrintDialog", kind="QAbstractPrintDialog"),
            "CQAbstractScrollArea": UiInterfaceEntry(public_name="CQAbstractScrollArea", kind="QAbstractScrollArea"),
            "CQAbstractSlider": UiInterfaceEntry(public_name="CQAbstractSlider", kind="QAbstractSlider"),
            "CQAbstractSpinBox": UiInterfaceEntry(public_name="CQAbstractSpinBox", kind="QAbstractSpinBox"),
            "CQAction": UiInterfaceEntry(public_name="CQAction", kind="QAction"),
            "CQBoxLayout": UiInterfaceEntry(public_name="CQBoxLayout", kind="QBoxLayout"),
            "CQCalendarWidget": UiInterfaceEntry(public_name="CQCalendarWidget", kind="QCalendarWidget"),
            "CQChartView": UiInterfaceEntry(public_name="CQChartView", kind="QChartView"),
            "CQCheckBox": UiInterfaceEntry(public_name="CQCheckBox", kind="QCheckBox"),
            "CQColorDialog": UiInterfaceEntry(public_name="CQColorDialog", kind="QColorDialog"),
            "CQColumnView": UiInterfaceEntry(public_name="CQColumnView", kind="QColumnView"),
            "CQComboBox": UiInterfaceEntry(public_name="CQComboBox", kind="QComboBox"),
            "CQCommandLinkButton": UiInterfaceEntry(public_name="CQCommandLinkButton", kind="QCommandLinkButton"),
            "CQDateEdit": UiInterfaceEntry(public_name="CQDateEdit", kind="QDateEdit"),
            "CQDateTimeEdit": UiInterfaceEntry(public_name="CQDateTimeEdit", kind="QDateTimeEdit"),
            "CQDesignerActionEditorInterface": UiInterfaceEntry(public_name="CQDesignerActionEditorInterface", kind="QDesignerActionEditorInterface"),
            "CQDesignerFormWindowInterface": UiInterfaceEntry(public_name="CQDesignerFormWindowInterface", kind="QDesignerFormWindowInterface"),
            "CQDesignerObjectInspectorInterface": UiInterfaceEntry(public_name="CQDesignerObjectInspectorInterface", kind="QDesignerObjectInspectorInterface"),
            "CQDesignerPropertyEditorInterface": UiInterfaceEntry(public_name="CQDesignerPropertyEditorInterface", kind="QDesignerPropertyEditorInterface"),
            "CQDesignerWidgetBoxInterface": UiInterfaceEntry(public_name="CQDesignerWidgetBoxInterface", kind="QDesignerWidgetBoxInterface"),
            "CQDial": UiInterfaceEntry(public_name="CQDial", kind="QDial"),
            "CQDialog": UiInterfaceEntry(public_name="CQDialog", kind="QDialog"),
            "CQDialogButtonBox": UiInterfaceEntry(public_name="CQDialogButtonBox", kind="QDialogButtonBox"),
            "CQDockWidget": UiInterfaceEntry(public_name="CQDockWidget", kind="QDockWidget"),
            "CQDoubleSpinBox": UiInterfaceEntry(public_name="CQDoubleSpinBox", kind="QDoubleSpinBox"),
            "CQErrorMessage": UiInterfaceEntry(public_name="CQErrorMessage", kind="QErrorMessage"),
            "CQFileDialog": UiInterfaceEntry(public_name="CQFileDialog", kind="QFileDialog"),
            "CQFocusFrame": UiInterfaceEntry(public_name="CQFocusFrame", kind="QFocusFrame"),
            "CQFontComboBox": UiInterfaceEntry(public_name="CQFontComboBox", kind="QFontComboBox"),
            "CQFontDialog": UiInterfaceEntry(public_name="CQFontDialog", kind="QFontDialog"),
            "CQFormLayout": UiInterfaceEntry(public_name="CQFormLayout", kind="QFormLayout"),
            "CQFrame": UiInterfaceEntry(public_name="CQFrame", kind="QFrame"),
            "CQGraphicsView": UiInterfaceEntry(public_name="CQGraphicsView", kind="QGraphicsView"),
            "CQGridLayout": UiInterfaceEntry(public_name="CQGridLayout", kind="QGridLayout"),
            "CQGroupBox": UiInterfaceEntry(public_name="CQGroupBox", kind="QGroupBox"),
            "CQHBoxLayout": UiInterfaceEntry(public_name="CQHBoxLayout", kind="QHBoxLayout"),
            "CQHeaderView": UiInterfaceEntry(public_name="CQHeaderView", kind="QHeaderView"),
            "CQHelpContentWidget": UiInterfaceEntry(public_name="CQHelpContentWidget", kind="QHelpContentWidget"),
            "CQHelpFilterSettingsWidget": UiInterfaceEntry(public_name="CQHelpFilterSettingsWidget", kind="QHelpFilterSettingsWidget"),
            "CQHelpIndexWidget": UiInterfaceEntry(public_name="CQHelpIndexWidget", kind="QHelpIndexWidget"),
            "CQHelpSearchQueryWidget": UiInterfaceEntry(public_name="CQHelpSearchQueryWidget", kind="QHelpSearchQueryWidget"),
            "CQHelpSearchResultWidget": UiInterfaceEntry(public_name="CQHelpSearchResultWidget", kind="QHelpSearchResultWidget"),
            "CQInputDialog": UiInterfaceEntry(public_name="CQInputDialog", kind="QInputDialog"),
            "CQKeySequenceEdit": UiInterfaceEntry(public_name="CQKeySequenceEdit", kind="QKeySequenceEdit"),
            "CQLCDNumber": UiInterfaceEntry(public_name="CQLCDNumber", kind="QLCDNumber"),
            "CQLabel": UiInterfaceEntry(public_name="CQLabel", kind="QLabel"),
            "CQLayout": UiInterfaceEntry(public_name="CQLayout", kind="QLayout"),
            "CQLineEdit": UiInterfaceEntry(public_name="CQLineEdit", kind="QLineEdit"),
            "CQListView": UiInterfaceEntry(public_name="CQListView", kind="QListView"),
            "CQListWidget": UiInterfaceEntry(public_name="CQListWidget", kind="QListWidget"),
            "CQMainWindow": UiInterfaceEntry(public_name="CQMainWindow", kind="QMainWindow"),
            "CQMdiArea": UiInterfaceEntry(public_name="CQMdiArea", kind="QMdiArea"),
            "CQMdiSubWindow": UiInterfaceEntry(public_name="CQMdiSubWindow", kind="QMdiSubWindow"),
            "CQMenu": UiInterfaceEntry(public_name="CQMenu", kind="QMenu"),
            "CQMenuBar": UiInterfaceEntry(public_name="CQMenuBar", kind="QMenuBar"),
            "CQMessageBox": UiInterfaceEntry(public_name="CQMessageBox", kind="QMessageBox"),
            "CQOpenGLWidget": UiInterfaceEntry(public_name="CQOpenGLWidget", kind="QOpenGLWidget"),
            "CQPageSetupDialog": UiInterfaceEntry(public_name="CQPageSetupDialog", kind="QPageSetupDialog"),
            "CQPdfPageSelector": UiInterfaceEntry(public_name="CQPdfPageSelector", kind="QPdfPageSelector"),
            "CQPdfView": UiInterfaceEntry(public_name="CQPdfView", kind="QPdfView"),
            "CQPlainTextEdit": UiInterfaceEntry(public_name="CQPlainTextEdit", kind="QPlainTextEdit"),
            "CQPrintDialog": UiInterfaceEntry(public_name="CQPrintDialog", kind="QPrintDialog"),
            "CQPrintPreviewDialog": UiInterfaceEntry(public_name="CQPrintPreviewDialog", kind="QPrintPreviewDialog"),
            "CQPrintPreviewWidget": UiInterfaceEntry(public_name="CQPrintPreviewWidget", kind="QPrintPreviewWidget"),
            "CQProgressBar": UiInterfaceEntry(public_name="CQProgressBar", kind="QProgressBar"),
            "CQProgressDialog": UiInterfaceEntry(public_name="CQProgressDialog", kind="QProgressDialog"),
            "CQPushButton": UiInterfaceEntry(public_name="CQPushButton", kind="QPushButton"),
            "CQQuickWidget": UiInterfaceEntry(public_name="CQQuickWidget", kind="QQuickWidget"),
            "CQRadioButton": UiInterfaceEntry(public_name="CQRadioButton", kind="QRadioButton"),
            "CQRhiWidget": UiInterfaceEntry(public_name="CQRhiWidget", kind="QRhiWidget"),
            "CQRubberBand": UiInterfaceEntry(public_name="CQRubberBand", kind="QRubberBand"),
            "CQScrollArea": UiInterfaceEntry(public_name="CQScrollArea", kind="QScrollArea"),
            "CQScrollBar": UiInterfaceEntry(public_name="CQScrollBar", kind="QScrollBar"),
            "CQSizeGrip": UiInterfaceEntry(public_name="CQSizeGrip", kind="QSizeGrip"),
            "CQSlider": UiInterfaceEntry(public_name="CQSlider", kind="QSlider"),
            "CQSpinBox": UiInterfaceEntry(public_name="CQSpinBox", kind="QSpinBox"),
            "CQSplashScreen": UiInterfaceEntry(public_name="CQSplashScreen", kind="QSplashScreen"),
            "CQSplitter": UiInterfaceEntry(public_name="CQSplitter", kind="QSplitter"),
            "CQSplitterHandle": UiInterfaceEntry(public_name="CQSplitterHandle", kind="QSplitterHandle"),
            "CQStackedLayout": UiInterfaceEntry(public_name="CQStackedLayout", kind="QStackedLayout"),
            "CQStackedWidget": UiInterfaceEntry(public_name="CQStackedWidget", kind="QStackedWidget"),
            "CQStatusBar": UiInterfaceEntry(public_name="CQStatusBar", kind="QStatusBar"),
            "CQSvgWidget": UiInterfaceEntry(public_name="CQSvgWidget", kind="QSvgWidget"),
            "CQTabBar": UiInterfaceEntry(public_name="CQTabBar", kind="QTabBar"),
            "CQTabWidget": UiInterfaceEntry(public_name="CQTabWidget", kind="QTabWidget"),
            "CQTableView": UiInterfaceEntry(public_name="CQTableView", kind="QTableView"),
            "CQTableWidget": UiInterfaceEntry(public_name="CQTableWidget", kind="QTableWidget"),
            "CQTextBrowser": UiInterfaceEntry(public_name="CQTextBrowser", kind="QTextBrowser"),
            "CQTextEdit": UiInterfaceEntry(public_name="CQTextEdit", kind="QTextEdit"),
            "CQTimeEdit": UiInterfaceEntry(public_name="CQTimeEdit", kind="QTimeEdit"),
            "CQToolBar": UiInterfaceEntry(public_name="CQToolBar", kind="QToolBar"),
            "CQToolBox": UiInterfaceEntry(public_name="CQToolBox", kind="QToolBox"),
            "CQToolButton": UiInterfaceEntry(public_name="CQToolButton", kind="QToolButton"),
            "CQTreeView": UiInterfaceEntry(public_name="CQTreeView", kind="QTreeView"),
            "CQTreeWidget": UiInterfaceEntry(public_name="CQTreeWidget", kind="QTreeWidget"),
            "CQUndoView": UiInterfaceEntry(public_name="CQUndoView", kind="QUndoView"),
            "CQVBoxLayout": UiInterfaceEntry(public_name="CQVBoxLayout", kind="QVBoxLayout"),
            "CQVideoWidget": UiInterfaceEntry(public_name="CQVideoWidget", kind="QVideoWidget"),
            "CQWebEngineView": UiInterfaceEntry(public_name="CQWebEngineView", kind="QWebEngineView"),
            "CQWidget": UiInterfaceEntry(public_name="CQWidget", kind="QWidget"),
            "CQWidgetAction": UiInterfaceEntry(public_name="CQWidgetAction", kind="QWidgetAction"),
            "CQWizard": UiInterfaceEntry(public_name="CQWizard", kind="QWizard"),
            "CQWizardPage": UiInterfaceEntry(public_name="CQWizardPage", kind="QWizardPage"),
    }))

    class mounts:
        action = MountSelector.named("action")
        central_widget = MountSelector.named("central_widget")
        corner_widget = MountSelector.named("corner_widget")
        layout = MountSelector.named("layout")
        menu = MountSelector.named("menu")
        menu_bar = MountSelector.named("menu_bar")
        menu_widget = MountSelector.named("menu_widget")
        status_bar = MountSelector.named("status_bar")
        title_bar_widget = MountSelector.named("title_bar_widget")
        viewport = MountSelector.named("viewport")
        widget = MountSelector.named("widget")

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))
