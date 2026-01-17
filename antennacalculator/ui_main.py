import sys
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QPushButton,
    QComboBox, QCheckBox, QTextEdit, QDoubleSpinBox,
    QFrame, QScrollArea, QTabWidget
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from .backend import AntennaCalculator
from .theme import (
    FONT_SIZES, FONTS, GLOBAL_STYLESHEET, STATUS_BAR_STYLESHEET,
    get_button_stylesheet, get_spinbox_button_stylesheet, PLOT_COLORS
)

class ModernButton(QPushButton):
    def __init__(self, text, button_type='primary'):
        super().__init__(text)
        self.button_type = button_type
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet(get_button_stylesheet(self.button_type))

class DoubleSpinBoxWithButtons(QWidget):
    """Enhanced spinbox with increment/decrement buttons"""
    valueChanged = pyqtSignal(float)

    def __init__(self, value=0.0, min_val=0.0, max_val=1000.0, step=0.1, decimals=4):
        super().__init__()
        self.step = step
        self.setup_ui(value, min_val, max_val, decimals)

    def setup_ui(self, value, min_val, max_val, decimals):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setValue(value)
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)
        self.spinbox.setDecimals(decimals)
        self.spinbox.setSingleStep(self.step)
        self.spinbox.valueChanged.connect(self.valueChanged.emit)

        btn_up = QPushButton("▲")
        btn_up.setFixedSize(28, 28)
        btn_up.clicked.connect(self.increment)
        btn_up.setStyleSheet(get_spinbox_button_stylesheet())

        btn_down = QPushButton("▼")
        btn_down.setFixedSize(28, 28)
        btn_down.clicked.connect(self.decrement)
        btn_down.setStyleSheet(get_spinbox_button_stylesheet())

        layout.addWidget(self.spinbox)
        layout.addWidget(btn_up)
        layout.addWidget(btn_down)

        self.setLayout(layout)

    def increment(self):
        self.spinbox.setValue(self.spinbox.value() + self.step)

    def decrement(self):
        self.spinbox.setValue(self.spinbox.value() - self.step)

    def value(self):
        return self.spinbox.value()

    def setValue(self, value):
        self.spinbox.setValue(value)

class InputPanel(QGroupBox):
    """Enhanced input parameters panel"""
    calculate_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__("⚙️ Input Parameters")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Scroll area for inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        row = 0
        # Operating Frequency
        scroll_layout.addWidget(QLabel("Operating Frequency (f)"), row, 0)
        self.freq_input = DoubleSpinBoxWithButtons(value=2.4, min_val=0.1, max_val=100.0, step=0.1, decimals=4)
        scroll_layout.addWidget(self.freq_input, row, 1)
        scroll_layout.addWidget(QLabel("GHz"), row, 2)
        row += 1

        # Dielectric Constant
        scroll_layout.addWidget(QLabel("Dielectric Constant (εr)"), row, 0)
        self.epsilon_input = DoubleSpinBoxWithButtons(value=4.4, min_val=1.0, max_val=20.0, step=0.1, decimals=4)
        scroll_layout.addWidget(self.epsilon_input, row, 1)
        scroll_layout.addWidget(QLabel(""), row, 2)
        row += 1

        # Height of Conductor
        scroll_layout.addWidget(QLabel("Conductor Height (t)"), row, 0)
        self.thickness_input = DoubleSpinBoxWithButtons(value=0.035, min_val=0.001, max_val=10.0, step=0.01, decimals=4)
        scroll_layout.addWidget(self.thickness_input, row, 1)
        scroll_layout.addWidget(QLabel("mm"), row, 2)
        row += 1

        # Height of Dielectric Substrate
        scroll_layout.addWidget(QLabel("Substrate Height (h)"), row, 0)
        self.height_input = DoubleSpinBoxWithButtons(value=1.6, min_val=0.1, max_val=50.0, step=0.1, decimals=4)
        scroll_layout.addWidget(self.height_input, row, 1)
        scroll_layout.addWidget(QLabel("mm"), row, 2)
        row += 1

        # Auto-calculate checkbox
        self.auto_calc_check = QCheckBox("Auto-calculate substrate height")
        scroll_layout.addWidget(self.auto_calc_check, row, 0, 1, 3)
        row += 1

        # Target Impedance
        scroll_layout.addWidget(QLabel("Target Impedance (Zo)"), row, 0)
        self.impedance_input = DoubleSpinBoxWithButtons(value=50.0, min_val=1.0, max_val=500.0, step=1.0, decimals=2)
        scroll_layout.addWidget(self.impedance_input, row, 1)
        scroll_layout.addWidget(QLabel("Ω"), row, 2)
        row += 1

        # Antenna Type
        scroll_layout.addWidget(QLabel("Antenna Type"), row, 0)
        self.antenna_type_combo = QComboBox()
        self.antenna_type_combo.addItems([
            "Microstrip Patch Antenna (Inset-Fed)",
            "Coaxial Feed Patch Antenna (Beta)",
            "Circularly Polarized Antennas (Beta)"
        ])
        scroll_layout.addWidget(self.antenna_type_combo, row, 1, 1, 2)
        row += 1

        scroll_layout.setRowStretch(row, 1)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Calculate button
        self.calc_button = ModernButton("🔬 Calculate Parameters", 'success')
        self.calc_button.clicked.connect(self.on_calculate)
        layout.addWidget(self.calc_button)

        # Reset button
        self.reset_button = ModernButton("↻ Reset to Defaults", 'accent')
        self.reset_button.clicked.connect(self.reset_defaults)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)
        self.setMaximumWidth(820)

    def reset_defaults(self):
        """Reset all inputs to default values"""
        self.freq_input.setValue(2.4)
        self.epsilon_input.setValue(4.4)
        self.thickness_input.setValue(0.035)
        self.height_input.setValue(1.6)
        self.impedance_input.setValue(50.0)
        self.auto_calc_check.setChecked(False)
        self.antenna_type_combo.setCurrentIndex(0)

    def on_calculate(self):
        params = self.get_values()
        self.calculate_requested.emit(params)

    def get_values(self):
        return {
            'f': self.freq_input.value(),
            'e': self.epsilon_input.value(),
            't': self.thickness_input.value(),
            'h': self.height_input.value(),
            'Zo': self.impedance_input.value(),
            'antenna_type': self.antenna_type_combo.currentText(),
            'auto_calculate_h': self.auto_calc_check.isChecked()
        }

class OutputPanel(QGroupBox):
    """Enhanced output display panel with tabs"""

    def __init__(self):
        super().__init__("📊 Results")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Parameters tab
        self.params_text = QTextEdit()
        self.params_text.setReadOnly(True)
        self.params_text.setFont(QFont(FONTS['monospace'].split(',')[0], FONT_SIZES['small']))
        self.tabs.addTab(self.params_text, "📋 Parameters")

        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont(FONTS['monospace'].split(',')[0], FONT_SIZES['small']))
        self.tabs.addTab(self.summary_text, "📝 Summary")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_output(self, results, antenna_type):
        """Update the output display with calculation results"""
        # Detailed parameters
        if antenna_type == "Microstrip Patch Antenna (Inset-Fed)":
            params_text = f"""╔══════════════════════════════════════════════════════╗
║           MICROSTRIP PATCH ANTENNA DESIGN            ║
╚══════════════════════════════════════════════════════╝

📡 OPERATING PARAMETERS
  • Frequency (f)          : {results.get('f', 0):.4f} GHz
  • Dielectric Const (εr)  : {results.get('e', 0):.4f}
  • Conductor Height (t)   : {results.get('t', 0):.4f} mm
  • Substrate Height (h)   : {results.get('h', 0):.4f} mm

📏 PATCH DIMENSIONS
  • Patch Width (W)        : {results.get('W', 0):.4f} mm
  • Patch Length (L)       : {results.get('L', 0):.4f} mm
  • Ground Width (Wg)      : {results.get('Wg', 0):.4f} mm
  • Ground Length (Lg)     : {results.get('Lg', 0):.4f} mm

🔌 FEED PARAMETERS
  • Inset Length (Fi)      : {results.get('Fi', 0):.4f} mm
  • Feed Line Width (Wf)   : {results.get('Wf', 0):.4f} mm

⚡ PERFORMANCE METRICS
  • S11 Parameter          : {results.get('S11', 0):.4f} dB
  • VSWR                   : {results.get('VSWR', 0):.4f}
  • Input Impedance (Zin)  : {results.get('Zin', 0):.4f} Ω
  • Radiation Res. (Rin)   : {results.get('Rin', 0):.4f} Ω

🔬 DERIVED PARAMETERS
  • Effective εr (εreff)   : {results.get('ereff', 0):.4f}
  • Effective Length (Leff): {results.get('leff', 0):.4f} mm
  • Fringing Ext. (ΔL)     : {results.get('dl', 0):.4f} mm
"""

            summary_text = f"""Design Summary for {results.get('f', 0):.2f} GHz Microstrip Patch Antenna
{'=' * 60}

The antenna has been designed with a patch size of {results.get('W', 0):.2f} × {results.get('L', 0):.2f} mm
on a substrate with εr = {results.get('e', 0):.2f} and height = {results.get('h', 0):.2f} mm.

Feed Configuration:
  - Inset-fed microstrip line with Fi = {results.get('Fi', 0):.2f} mm
  - Feed line width Wf = {results.get('Wf', 0):.2f} mm (for {results.get('Zo', 0):.0f}Ω impedance)

Performance:
  - Return Loss (S11): {results.get('S11', 0):.2f} dB
  - VSWR: {results.get('VSWR', 0):.2f}:1
  {'✓ Good matching (VSWR < 2)' if results.get('VSWR', 0) < 2 else '⚠ Poor matching (VSWR ≥ 2)'}

Recommended ground plane: {results.get('Wg', 0):.2f} × {results.get('Lg', 0):.2f} mm
"""

        elif antenna_type == "Coaxial Feed Patch Antenna (Beta)":
            params_text = f"""Operating Frequency (f)   : {results.get('f', 0):.4f} GHz
Dielectric Constant (εr)  : {results.get('e', 0):.4f}
Conductor Height (t)      : {results.get('t', 0):.4f} mm
Substrate Height (h)      : {results.get('h', 0):.4f} mm
Patch Width (W)           : {results.get('W', 0):.4f} mm
Patch Length (L)          : {results.get('L', 0):.4f} mm
Ground Width (Wg)         : {results.get('Wg', 0):.4f} mm
Ground Length (Lg)        : {results.get('Lg', 0):.4f} mm
Feed Point Xf             : {results.get('Xf', 0):.4f} mm
Feed Point Yf             : {results.get('Yf', 0):.4f} mm"""
            summary_text = "Coaxial feed antenna design completed."

        else:  # Circularly Polarized
            params_text = f"""Operating Frequency (f)   : {results.get('f', 0):.4f} GHz
Dielectric Constant (εr)  : {results.get('e', 0):.4f}
Conductor Height (t)      : {results.get('t', 0):.4f} mm
Substrate Height (h)      : {results.get('h', 0):.4f} mm
Patch Width (W)           : {results.get('W', 0):.4f} mm
Patch Length (L)          : {results.get('L', 0):.4f} mm
Ground Width (Wg)         : {results.get('Wg', 0):.4f} mm
Ground Length (Lg)        : {results.get('Lg', 0):.4f} mm
Corner Trunc Size (a)     : {results.get('a', 0):.4f} mm
Quality Factor (Q)        : {results.get('Q', 0):.4f}"""
            summary_text = "Circularly polarized antenna design completed."

        self.params_text.setText(params_text)
        self.summary_text.setText(summary_text)

    def show_error(self, error_msg):
        error_text = f"""╔══════════════════════════════════════════════════════╗
║                      ⚠️  ERROR                       ║
╚══════════════════════════════════════════════════════╝

{error_msg}

Please check your input parameters and try again.
"""
        self.params_text.setText(error_text)
        self.summary_text.setText("Calculation failed. See Parameters tab for details.")

class StructurePlot(QGroupBox):
    def __init__(self):
        super().__init__("🔧 Antenna Structure Preview")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(4, 4), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.clear_plot()

    def plot_structure(self, ground_coords, patch_coords, patch_ext_coords, Wg, Lg):
        """Plot antenna structure"""
        self.ax.clear()
        # Plot ground plane
        ground_style = PLOT_COLORS['ground_plane']
        self.ax.fill(ground_coords['x'], ground_coords['y'],
                     color=ground_style['fill'],
                     alpha=ground_style['alpha'],
                     label='Ground Plane',
                     linewidth=ground_style['linewidth'],
                     edgecolor=ground_style['edge'])

        # Plot fringing field
        fringing_style = PLOT_COLORS['fringing_field']
        self.ax.fill(patch_ext_coords['x'], patch_ext_coords['y'],
                     color=fringing_style['fill'],
                     alpha=fringing_style['alpha'],
                     label='Fringing Field',
                     linewidth=fringing_style['linewidth'],
                     edgecolor=fringing_style['edge'])

        # Plot main patch
        patch_style = PLOT_COLORS['patch']
        self.ax.fill(patch_coords['x'], patch_coords['y'],
                     color=patch_style['fill'],
                     alpha=patch_style['alpha'],
                     label='Patch',
                     linewidth=patch_style['linewidth'],
                     edgecolor=patch_style['edge'])

        self.ax.set_xlim(-5, Wg + 10)
        self.ax.set_ylim(-5, Lg + 5)
        self.ax.set_xlabel('X (mm)', fontsize=FONT_SIZES['tiny'], fontweight='bold')
        self.ax.set_ylabel('Y (mm)', fontsize=FONT_SIZES['tiny'], fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        self.ax.legend(loc='upper right', framealpha=0.9, fontsize=FONT_SIZES['tiny'])
        self.ax.set_aspect('equal')

        self.figure.tight_layout()
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_title('Antenna Structure Preview', fontsize=FONT_SIZES['medium'], fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.text(0.5, 0.5, 'Run calculation to view structure',
                     ha='center', va='center', transform=self.ax.transAxes,
                     fontsize=FONT_SIZES['normal'], color='gray', style='italic')
        self.canvas.draw()

class antennacalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.calculator = AntennaCalculator()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.setWindowTitle("Microstrip Patch Antenna Parameter Calculator")
        self.setGeometry(100, 50, 1650, 950)
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Create panels
        self.input_panel = InputPanel()
        self.structure_plot = StructurePlot()
        self.output_panel = OutputPanel()

        # LEFT COLUMN (Column 0): Input Parameters + Structure Plot
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setSpacing(6)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.input_panel)
        left_layout.addWidget(self.structure_plot)

        # RIGHT COLUMN (Column 1): Output Panel
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.output_panel)

        # Add columns to main layout
        main_layout.addWidget(left_column, 0, 0)
        main_layout.addWidget(right_column, 0, 1)

        # Set column stretch factors
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)

        self.create_menu_bar()
        self.create_status_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("📁 File")

        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("ℹ️ About")

        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready to design antennas")
        self.status_bar.setStyleSheet(STATUS_BAR_STYLESHEET)

    def connect_signals(self):
        """Connect signals and slots"""
        self.input_panel.calculate_requested.connect(self.on_calculate_requested)

    @pyqtSlot(dict)
    def on_calculate_requested(self, params):
        """Handle calculate button click"""
        self.status_bar.showMessage("⏳ Calculating antenna parameters...")
        try:
            results = self.calculator.calculate_parameters(
                params['f'], params['e'], params['t'], params['h'],
                params['Zo'], params['antenna_type'], params['auto_calculate_h']
            )
            self.on_calculation_complete(results)
            self.status_bar.showMessage(f"✅ Calculation complete - {params['antenna_type']}", 5000)
        except Exception as e:
            self.on_calculation_error(str(e))
            self.status_bar.showMessage(f"❌ Calculation failed: {str(e)}", 5000)

    def on_calculation_complete(self, results):
        """Update UI with calculation results"""
        antenna_type = results.get('antenna_type', '')

        # Update output display
        self.output_panel.update_output(results, antenna_type)

        # Update plots
        if antenna_type == "Microstrip Patch Antenna (Inset-Fed)":
            ground_coords, patch_coords, patch_ext_coords = \
                self.calculator.get_structure_coordinates(
                    results['Fi'], results['Wf'], results['W'], results['L'],
                    results['Lg'], results['Wg'], results['dl']
                )

            self.structure_plot.plot_structure(
                ground_coords, patch_coords, patch_ext_coords,
                results['Wg'], results['Lg']
            )
        else:
            self.structure_plot.clear_plot()

    def on_calculation_error(self, error_msg):
        """Handle calculation errors"""
        self.output_panel.show_error(error_msg)

    def show_about(self):
        from PyQt6.QtWidgets import QMessageBox
        about_text = """
        <h2>Microstrip Patch Antenna Parameter Calculator</h2>
        <p><b>Version:</b> 1.0</p>
        <p><b>Developer:</b> Nihal Singh (Github: nihalsingh-ece)</p>
        <br>
        <p>A tool for designing and analyzing microstrip patch antennas 
        with visualization and performance metrics.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
            <li>Multiple antenna types support</li>
            <li>Real-time radiation pattern visualization</li>
            <li>Comprehensive parameter calculations</li>
            <li>Modern, intuitive interface</li>
        </ul>
        """
        QMessageBox.about(self, "About Antenna Calculator", about_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = antennacalculator()
    window.show()
    sys.exit(app.exec())