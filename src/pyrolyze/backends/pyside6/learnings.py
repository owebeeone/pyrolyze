"""Manual learnings for the PySide6 backend extraction pipeline."""

from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.model import (
    EventPayloadPolicy,
    FillPolicy,
    MethodMode,
    TypeRef,
    UiEventLearning,
    UiMethodLearning,
    UiPropLearning,
    UiWidgetLearning,
)

LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(
    {
        "QAbstractButton": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QAbstractItemView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QAbstractPrintDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFromTo": UiMethodLearning(
                        source_props=("from_to_from_page", "from_to_to_page"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinMax": UiMethodLearning(
                        source_props=("min_max_minimum", "min_max_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QAbstractScrollArea": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QAbstractSlider": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRepeatAction": UiMethodLearning(
                        source_props=("repeat_action_action", "repeat_action_threshold_time", "repeat_action_repeat_time"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QAbstractSpinBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QCalendarWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setCurrentPage": UiMethodLearning(
                        source_props=("current_page_year", "current_page_month"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateRange": UiMethodLearning(
                        source_props=("date_range_minimum", "date_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateTextFormat": UiMethodLearning(
                        source_props=("date_text_format_date", "date_text_format_format"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setWeekdayTextFormat": UiMethodLearning(
                        source_props=("weekday_text_format_day_of_week", "weekday_text_format_format"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QChartView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOptimizationFlag": UiMethodLearning(
                        source_props=("optimization_flag_flag", "optimization_flag_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setRenderHint": UiMethodLearning(
                        source_props=("render_hint_hint", "render_hint_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSceneRect": UiMethodLearning(
                        source_props=("scene_rect_x", "scene_rect_y", "scene_rect_width", "scene_rect_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTransform": UiMethodLearning(
                        source_props=("transform_matrix", "transform_combine"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QCheckBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QColorDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setCustomColor": UiMethodLearning(
                        source_props=("custom_color_index", "custom_color_color"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setStandardColor": UiMethodLearning(
                        source_props=("standard_color_index", "standard_color_color"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QColumnView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QComboBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemData": UiMethodLearning(
                        source_props=("item_data_index", "item_data_value", "item_data_role"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemIcon": UiMethodLearning(
                        source_props=("item_icon_index", "item_icon_icon"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemText": UiMethodLearning(
                        source_props=("item_text_index", "item_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QCommandLinkButton": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDateEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateRange": UiMethodLearning(
                        source_props=("date_range_minimum", "date_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateTimeRange": UiMethodLearning(
                        source_props=("date_time_range_minimum", "date_time_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTimeRange": UiMethodLearning(
                        source_props=("time_range_minimum", "time_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDateTimeEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateRange": UiMethodLearning(
                        source_props=("date_range_minimum", "date_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateTimeRange": UiMethodLearning(
                        source_props=("date_time_range_minimum", "date_time_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTimeRange": UiMethodLearning(
                        source_props=("time_range_minimum", "time_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDesignerActionEditorInterface": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDesignerFormWindowInterface": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setLayoutDefault": UiMethodLearning(
                        source_props=("layout_default_margin", "layout_default_spacing"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setLayoutFunction": UiMethodLearning(
                        source_props=("layout_function_margin", "layout_function_spacing"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDesignerObjectInspectorInterface": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDesignerPropertyEditorInterface": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setPropertyValue": UiMethodLearning(
                        source_props=("property_value_name", "property_value_value", "property_value_changed"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDesignerWidgetBoxInterface": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDial": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRepeatAction": UiMethodLearning(
                        source_props=("repeat_action_action", "repeat_action_threshold_time", "repeat_action_repeat_time"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDialogButtonBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDockWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QDoubleSpinBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QErrorMessage": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QFileDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setLabelText": UiMethodLearning(
                        source_props=("label_text_label", "label_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QFocusFrame": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QFontComboBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDisplayFont": UiMethodLearning(
                        source_props=("display_font_font_family", "display_font_font"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemData": UiMethodLearning(
                        source_props=("item_data_index", "item_data_value", "item_data_role"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemIcon": UiMethodLearning(
                        source_props=("item_icon_index", "item_icon_icon"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemText": UiMethodLearning(
                        source_props=("item_text_index", "item_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setSampleTextForFont": UiMethodLearning(
                        source_props=("sample_text_for_font_font_family", "sample_text_for_font_sample_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSampleTextForSystem": UiMethodLearning(
                        source_props=("sample_text_for_system_writing_system", "sample_text_for_system_sample_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QFontDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QFrame": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QGraphicsView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOptimizationFlag": UiMethodLearning(
                        source_props=("optimization_flag_flag", "optimization_flag_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setRenderHint": UiMethodLearning(
                        source_props=("render_hint_hint", "render_hint_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSceneRect": UiMethodLearning(
                        source_props=("scene_rect_x", "scene_rect_y", "scene_rect_width", "scene_rect_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTransform": UiMethodLearning(
                        source_props=("transform_matrix", "transform_combine"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QGroupBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QHBoxLayout": UiWidgetLearning(
            prop_learnings=frozendict(
                {
                    "parent": UiPropLearning(
                        signature_annotation=TypeRef(expr="PySide6.QtWidgets.QWidget | None"),
                        signature_default_repr="...",
                    ),
                }
            )
        ),
        "QHeaderView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setSectionHidden": UiMethodLearning(
                        source_props=("section_hidden_logical_index", "section_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSectionResizeMode": UiMethodLearning(
                        source_props=("section_resize_mode_logical_index", "section_resize_mode_mode"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSortIndicator": UiMethodLearning(
                        source_props=("sort_indicator_logical_index", "sort_indicator_order"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QHelpContentWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnHidden": UiMethodLearning(
                        source_props=("column_hidden_column", "column_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnWidth": UiMethodLearning(
                        source_props=("column_width_column", "column_width_width"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QHelpFilterSettingsWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QHelpIndexWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRowHidden": UiMethodLearning(
                        source_props=("row_hidden_row", "row_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QHelpSearchQueryWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QHelpSearchResultWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QInputDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDoubleRange": UiMethodLearning(
                        source_props=("double_range_minimum", "double_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setIntRange": UiMethodLearning(
                        source_props=("int_range_minimum", "int_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QKeySequenceEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QLCDNumber": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QLabel": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QLineEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTextMargins": UiMethodLearning(
                        source_props=("text_margins_left", "text_margins_top", "text_margins_right", "text_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            ),
            event_learnings=frozendict(
                {
                    "on_textChanged": UiEventLearning(
                        signal_name="textChanged",
                        payload_policy=EventPayloadPolicy.FIRST_ARG,
                    ),
                }
            ),
        ),
        "QListView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRowHidden": UiMethodLearning(
                        source_props=("row_hidden_row", "row_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QListWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRowHidden": UiMethodLearning(
                        source_props=("row_hidden_row", "row_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QMainWindow": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setCorner": UiMethodLearning(
                        source_props=("corner_corner", "corner_area"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabPosition": UiMethodLearning(
                        source_props=("tab_position_areas", "tab_position_tab_position"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QMdiArea": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QMdiSubWindow": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QMenu": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QMenuBar": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QMessageBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setButtonText": UiMethodLearning(
                        source_props=("button_text_button", "button_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QOpenGLWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPageSetupDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPdfPageSelector": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPdfView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPlainTextEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPrintDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFromTo": UiMethodLearning(
                        source_props=("from_to_from_page", "from_to_to_page"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinMax": UiMethodLearning(
                        source_props=("min_max_minimum", "min_max_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPrintPreviewDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPrintPreviewWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QProgressBar": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QProgressDialog": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QPushButton": UiWidgetLearning(
            prop_learnings=frozendict(
                {
                    "icon": UiPropLearning(public=False),
                }
            ),
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            ),
            event_learnings=frozendict(
                {
                    "on_clicked": UiEventLearning(
                        signal_name="clicked",
                        payload_policy=EventPayloadPolicy.NONE,
                    ),
                }
            ),
        ),
        "QQuickWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContent": UiMethodLearning(
                        source_props=("content_url", "content_component", "content_item"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QRadioButton": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QRhiWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedColorBufferSize": UiMethodLearning(
                        source_props=("fixed_color_buffer_size_width", "fixed_color_buffer_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QRubberBand": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QScrollArea": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QScrollBar": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRepeatAction": UiMethodLearning(
                        source_props=("repeat_action_action", "repeat_action_threshold_time", "repeat_action_repeat_time"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSizeGrip": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSlider": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRepeatAction": UiMethodLearning(
                        source_props=("repeat_action_action", "repeat_action_threshold_time", "repeat_action_repeat_time"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSpinBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSplashScreen": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSplitter": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setStretchFactor": UiMethodLearning(
                        source_props=("stretch_factor_index", "stretch_factor_stretch"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSplitterHandle": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QStackedWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QStatusBar": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QSvgWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTabBar": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setAccessibleTabName": UiMethodLearning(
                        source_props=("accessible_tab_name_index", "accessible_tab_name_name"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabData": UiMethodLearning(
                        source_props=("tab_data_index", "tab_data_data"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabEnabled": UiMethodLearning(
                        source_props=("tab_enabled_index", "tab_enabled_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabIcon": UiMethodLearning(
                        source_props=("tab_icon_index", "tab_icon_icon"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabText": UiMethodLearning(
                        source_props=("tab_text_index", "tab_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabTextColor": UiMethodLearning(
                        source_props=("tab_text_color_index", "tab_text_color_color"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabToolTip": UiMethodLearning(
                        source_props=("tab_tool_tip_index", "tab_tool_tip_tip"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabVisible": UiMethodLearning(
                        source_props=("tab_visible_index", "tab_visible_visible"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabWhatsThis": UiMethodLearning(
                        source_props=("tab_whats_this_index", "tab_whats_this_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTabWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabEnabled": UiMethodLearning(
                        source_props=("tab_enabled_index", "tab_enabled_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabIcon": UiMethodLearning(
                        source_props=("tab_icon_index", "tab_icon_icon"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabText": UiMethodLearning(
                        source_props=("tab_text_index", "tab_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabToolTip": UiMethodLearning(
                        source_props=("tab_tool_tip_index", "tab_tool_tip_tip"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabVisible": UiMethodLearning(
                        source_props=("tab_visible_index", "tab_visible_visible"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTabWhatsThis": UiMethodLearning(
                        source_props=("tab_whats_this_index", "tab_whats_this_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTableView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnHidden": UiMethodLearning(
                        source_props=("column_hidden_column", "column_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnWidth": UiMethodLearning(
                        source_props=("column_width_column", "column_width_width"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRowHeight": UiMethodLearning(
                        source_props=("row_height_row", "row_height_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setRowHidden": UiMethodLearning(
                        source_props=("row_hidden_row", "row_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSpan": UiMethodLearning(
                        source_props=("span_row", "span_column", "span_row_span", "span_column_span"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTableWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnHidden": UiMethodLearning(
                        source_props=("column_hidden_column", "column_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnWidth": UiMethodLearning(
                        source_props=("column_width_column", "column_width_width"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setHorizontalHeaderItem": UiMethodLearning(
                        source_props=("horizontal_header_item_column", "horizontal_header_item_item"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItem": UiMethodLearning(
                        source_props=("item_row", "item_column", "item_item"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRangeSelected": UiMethodLearning(
                        source_props=("range_selected_range", "range_selected_select"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setRowHeight": UiMethodLearning(
                        source_props=("row_height_row", "row_height_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setRowHidden": UiMethodLearning(
                        source_props=("row_hidden_row", "row_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSpan": UiMethodLearning(
                        source_props=("span_row", "span_column", "span_row_span", "span_column_span"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setVerticalHeaderItem": UiMethodLearning(
                        source_props=("vertical_header_item_row", "vertical_header_item_item"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTextBrowser": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSource": UiMethodLearning(
                        source_props=("source_name", "source_type"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTextEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTimeEdit": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateRange": UiMethodLearning(
                        source_props=("date_range_minimum", "date_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDateTimeRange": UiMethodLearning(
                        source_props=("date_time_range_minimum", "date_time_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setTimeRange": UiMethodLearning(
                        source_props=("time_range_minimum", "time_range_maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QToolBar": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QToolBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemEnabled": UiMethodLearning(
                        source_props=("item_enabled_index", "item_enabled_enabled"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemIcon": UiMethodLearning(
                        source_props=("item_icon_index", "item_icon_icon"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemText": UiMethodLearning(
                        source_props=("item_text_index", "item_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setItemToolTip": UiMethodLearning(
                        source_props=("item_tool_tip_index", "item_tool_tip_tool_tip"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QToolButton": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTreeView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnHidden": UiMethodLearning(
                        source_props=("column_hidden_column", "column_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnWidth": UiMethodLearning(
                        source_props=("column_width_column", "column_width_width"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QTreeWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnHidden": UiMethodLearning(
                        source_props=("column_hidden_column", "column_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setColumnWidth": UiMethodLearning(
                        source_props=("column_width_column", "column_width_width"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QUndoView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setRowHidden": UiMethodLearning(
                        source_props=("row_hidden_row", "row_hidden_hide"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setViewportMargins": UiMethodLearning(
                        source_props=("viewport_margins_left", "viewport_margins_top", "viewport_margins_right", "viewport_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QVBoxLayout": UiWidgetLearning(
            prop_learnings=frozendict(
                {
                    "parent": UiPropLearning(
                        signature_annotation=TypeRef(expr="PySide6.QtWidgets.QWidget | None"),
                        signature_default_repr="...",
                    ),
                }
            )
        ),
        "QVideoWidget": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QWebEngineView": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContent": UiMethodLearning(
                        source_props=("content_data", "content_mime_type", "content_base_url"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setHtml": UiMethodLearning(
                        source_props=("html_html", "html_base_url"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QWizard": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setButton": UiMethodLearning(
                        source_props=("button_which", "button_button"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setButtonText": UiMethodLearning(
                        source_props=("button_text_which", "button_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setDefaultProperty": UiMethodLearning(
                        source_props=("default_property_class_name", "default_property_property", "default_property_changed_signal"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setField": UiMethodLearning(
                        source_props=("field_name", "field_value"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setOption": UiMethodLearning(
                        source_props=("option_option", "option_on"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setPage": UiMethodLearning(
                        source_props=("page_id", "page_page"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setPixmap": UiMethodLearning(
                        source_props=("pixmap_which", "pixmap_pixmap"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
        "QWizardPage": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setBaseSize": UiMethodLearning(
                        source_props=("base_size_basew", "base_size_baseh"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setButtonText": UiMethodLearning(
                        source_props=("button_text_which", "button_text_text"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setContentsMargins": UiMethodLearning(
                        source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setField": UiMethodLearning(
                        source_props=("field_name", "field_value"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setFixedSize": UiMethodLearning(
                        source_props=("fixed_size_width", "fixed_size_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setGeometry": UiMethodLearning(
                        source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setMaximumSize": UiMethodLearning(
                        source_props=("maximumWidth", "maximumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setMinimumSize": UiMethodLearning(
                        source_props=("minimumWidth", "minimumHeight"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                    "setPixmap": UiMethodLearning(
                        source_props=("pixmap_which", "pixmap_pixmap"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutAutoRepeat": UiMethodLearning(
                        source_props=("shortcut_auto_repeat_id", "shortcut_auto_repeat_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setShortcutEnabled": UiMethodLearning(
                        source_props=("shortcut_enabled_id", "shortcut_enabled_enable"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizeIncrement": UiMethodLearning(
                        source_props=("size_increment_width", "size_increment_height"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                    "setSizePolicy": UiMethodLearning(
                        source_props=("size_policy_horizontal", "size_policy_vertical"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=False,
                    ),
                }
            )
        ),
    }
)
