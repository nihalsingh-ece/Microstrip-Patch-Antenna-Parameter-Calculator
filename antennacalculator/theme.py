# Color Palette
COLORS = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_light': '#BBDEFB',
    'accent': '#FF9800',
    'accent_dark': '#F57C00',
    'success': '#4CAF50',
    'success_dark': '#388E3C',
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'border': '#E0E0E0',
    'error': '#F44336',
    'ground_plane': '#37474F',
    'ground_plane_edge': '#263238',
    'fringing_field': '#FF9800',
    'fringing_field_edge': '#F57C00',
    'patch': '#FFD54F',
    'patch_edge': '#FFA000'
}

# Font Sizes
FONT_SIZES = {
    'tiny': 8,
    'small': 10,
    'normal': 11,
    'medium': 12,
    'large': 13,
    'xlarge': 15
}

# Font Families
FONTS = {
    'default': 'Segoe UI',
    'monospace': 'Consolas, Courier New, monospace'
}

# Global Stylesheet
GLOBAL_STYLESHEET = f"""
    QMainWindow {{
        background-color: {COLORS['background']};
    }}

    QGroupBox {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding: 2px;
        font-weight: bold;
        font-size: {FONT_SIZES['large']}px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px 10px;
        color: {COLORS['primary']};
    }}

    QLabel {{
        color: {COLORS['text_primary']};
        font-size: {FONT_SIZES['large']}px;
    }}

    QDoubleSpinBox {{
        padding: 6px;
        border: 2px solid {COLORS['border']};
        border-radius: 4px;
        background-color: white;
        font-size: {FONT_SIZES['normal']}px;
    }}

    QDoubleSpinBox:focus {{
        border-color: {COLORS['primary']};
    }}

    QComboBox {{
        padding: 6px;
        border: 2px solid {COLORS['border']};
        border-radius: 4px;
        background-color: white;
        font-size: {FONT_SIZES['normal']}px;
        min-height: 25px;
    }}

    QComboBox:focus {{
        border-color: {COLORS['primary']};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS['text_secondary']};
        margin-right: 10px;
    }}

    QCheckBox {{
        spacing: 8px;
        font-size: {FONT_SIZES['normal']}px;
        color: {COLORS['text_primary']};
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['border']};
        border-radius: 3px;
        background-color: white;
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}

    QTextEdit {{
        background-color: #F5F5F5;
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 2px;
        font-family: {FONTS['monospace']};
        font-size: {FONT_SIZES['xlarge']}px;
    }}

    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
    }}

    QTabBar::tab {{
        background-color: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}

    QTabBar::tab:selected {{
        background-color: {COLORS['surface']};
        border-bottom-color: {COLORS['surface']};
        font-weight: bold;
    }}

    QScrollArea {{
        border: 1px solid;
        background-color: transparent;
    }}
"""

# Status Bar Stylesheet
STATUS_BAR_STYLESHEET = f"""
    QStatusBar {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_secondary']};
        border-top: 1px solid {COLORS['border']};
        padding: 4px;
    }}
"""

def get_button_stylesheet(button_type='primary'):
    button_styles = {
        'primary': {
            'bg': COLORS['primary'],
            'hover': COLORS['primary_dark']
        },
        'success': {
            'bg': COLORS['success'],
            'hover': COLORS['success_dark']
        },
        'accent': {
            'bg': COLORS['accent'],
            'hover': COLORS['accent_dark']
        },
        'default': {
            'bg': COLORS['text_secondary'],
            'hover': COLORS['text_primary']
        }
    }

    style = button_styles.get(button_type, button_styles['default'])

    return f"""
        QPushButton {{
            background-color: {style['bg']};
            color: white;
            font-weight: bold;
            font-size: {FONT_SIZES['medium']}px;
            padding: 1px 2px;
            border: none;
            border-radius: 6px;
            min-height: 35px;
        }}
        QPushButton:hover {{
            background-color: {style['hover']};
        }}
        QPushButton:pressed {{
            background-color: {style['hover']};
            padding-top: 12px;
            padding-bottom: 8px;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_secondary']};
        }}
    """

def get_spinbox_button_stylesheet():
    """Generate stylesheet for spinbox increment/decrement buttons"""
    return f"""
        QPushButton {{
            background-color: {COLORS['primary_light']};
            border: none;
            border-radius: 4px;
            font-size: {FONT_SIZES['small']}px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary']};
            color: white;
        }}
    """

# Plot Colors
PLOT_COLORS = {
    'ground_plane': {
        'fill': COLORS['ground_plane'],
        'alpha': 0.15,
        'edge': COLORS['ground_plane_edge'],
        'linewidth': 2
    },
    'fringing_field': {
        'fill': COLORS['fringing_field'],
        'alpha': 0.25,
        'edge': COLORS['fringing_field_edge'],
        'linewidth': 1.5
    },
    'patch': {
        'fill': COLORS['patch'],
        'alpha': 0.8,
        'edge': COLORS['patch_edge'],
        'linewidth': 2
    }
}