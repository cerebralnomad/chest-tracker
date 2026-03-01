#!/usr/bin/env python3
"""
Total Battle Clan Chest Tracker
Main GUI application for tracking clan chest contributions
"""

import sys
import json
import time
import warnings
from pathlib import Path
from datetime import datetime
import numpy as np
import cv2

# Suppress dependency warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*urllib3.*')
warnings.filterwarnings('ignore', message='.*chardet.*')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QGroupBox, QTextEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit,
    QFormLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import pyautogui
from paddleocr import PaddleOCR
from database_manager import DatabaseManager
from html_generator import HTMLGenerator

class CaptureThread(QThread):
    """Background thread for capturing and processing chests"""
    status_update = pyqtSignal(str)
    chest_found = pyqtSignal(str, str)  # player_name, chest_type
    processing_complete = pyqtSignal(int)  # total chests processed
    error_occurred = pyqtSignal(str)
    
    def __init__(self, coords, ocr_instance, db_manager):
        super().__init__()
        self.coords = coords
        self.ocr = ocr_instance
        self.db = db_manager
        self.running = False
        self.click_delay = 0.3  # 300ms default delay
        
    def run(self):
        """Main processing loop"""
        self.running = True
        processed_count = 0
        
        try:
            while self.running:
                # Capture the chest area
                self.status_update.emit("Capturing screen region...")
                x, y, width, height = self.coords
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                
                # Convert to numpy array
                img_array = np.array(screenshot)
                
                # Simpler, faster preprocessing
                # Convert to grayscale
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                
                # Quick contrast boost only
                gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=10)
                
                # Run OCR on preprocessed image
                self.status_update.emit("Running OCR...")
                try:
                    # Save preprocessed image temporarily - predict() needs a file path
                    temp_path = 'temp_ocr.png'
                    cv2.imwrite(temp_path, gray)
                    result = self.ocr.predict(input=temp_path)
                except Exception as ocr_error:
                    self.status_update.emit(f"OCR error: {str(ocr_error)}")
                    import traceback
                    self.status_update.emit(f"Traceback: {traceback.format_exc()}")
                    break
                
                if not result:
                    self.status_update.emit("No OCR results. Stopping.")
                    break
                
                # Extract text lines - predict() returns list of dicts with 'rec_texts'
                text_lines = []
                try:
                    # predict() format: [{'rec_texts': [...], 'rec_scores': [...], ...}]
                    for item in result:
                        if isinstance(item, dict) and 'rec_texts' in item:
                            texts = item['rec_texts']
                            if isinstance(texts, list):
                                text_lines.extend(texts)
                            else:
                                text_lines.append(str(texts))
                    
                    if not text_lines:
                        self.status_update.emit("No text extracted from OCR. Stopping.")
                        break
                    
                except Exception as parse_error:
                    self.status_update.emit(f"Error parsing OCR results: {str(parse_error)}")
                    break
                
                # Quick debug - only show count, not all lines
                self.status_update.emit(f"OCR found {len(text_lines)} text lines")
                
                # Parse chest information
                chest_data = self._parse_chest_data(text_lines)
                
                if not chest_data:
                    self.status_update.emit("Could not parse chest data. Stopping.")
                    break
                
                # Process first chest in the list
                player_name = chest_data[0]['player']
                chest_type = chest_data[0]['chest_type']
                
                # Save to database
                self.db.add_chest(player_name, chest_type)
                processed_count += 1
                
                # Emit signal for UI update
                self.chest_found.emit(player_name, chest_type)
                self.status_update.emit(f"Processed: {player_name} - {chest_type}")
                
                # Click the Open button for the FIRST chest entry
                # Using exact coordinates found via "Find Click Coordinates" tool
                # These are absolute screen coordinates, not relative to capture area
                click_x = 1351
                click_y = 523
                
                self.status_update.emit(f"Clicking Open at ({click_x}, {click_y})...")
                pyautogui.click(click_x, click_y)
                
                # Wait for chest to open and UI to update (reduced from 1 second)
                time.sleep(self.click_delay)
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        
        finally:
            self.running = False
            self.processing_complete.emit(processed_count)
    
    def _parse_chest_data(self, text_lines):
        """Parse OCR text lines to extract chest information"""
        chests = []
        
        self.status_update.emit("Parsing chest data...")
        
        # The OCR extracts text without "From:" and "Source:" labels
        # Pattern: [chest_name, player_name, source_info, ...]
        # We need to identify the pattern based on known chest types
        
        chest_keywords = ['chest', 'crypt']  # Common words in chest names
        
        i = 0
        while i < len(text_lines):
            line = text_lines[i].lower().strip()
            
            # Check if this line contains a chest type keyword
            if any(keyword in line for keyword in chest_keywords):
                chest_type = text_lines[i].strip()
                
                # Next line should be player name
                player_name = text_lines[i + 1].strip() if i + 1 < len(text_lines) else None
                
                # Line after that should be the source (e.g., "Level 15 Crypt")
                source = text_lines[i + 2].strip() if i + 2 < len(text_lines) else None
                
                # Validate: player name shouldn't contain "level" or "crypt"
                if player_name and source:
                    player_lower = player_name.lower()
                    if 'level' not in player_lower and 'crypt' not in player_lower and 'chest' not in player_lower:
                        chests.append({
                            'player': player_name,
                            'chest_type': f"{chest_type} - {source}"  # Combine for full info
                        })
                        self.status_update.emit(f"Found: {player_name} - {chest_type} ({source})")
                        i += 3  # Move past this chest entry
                        continue
            
            i += 1
        
        self.status_update.emit(f"Parsed {len(chests)} chest(s)")
        return chests
    
    def stop(self):
        """Stop the capture thread"""
        self.running = False


class CoordinateSetup(QWidget):
    """Widget for setting up capture coordinates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.coords = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Set the coordinates for the chest list area:\n\n"
            "1. Note the X, Y position of the TOP-LEFT corner\n"
            "2. Note the WIDTH and HEIGHT of the capture area\n\n"
            "TIPS:\n"
            "• Capture at least 2-3 chest entries for best results\n"
            "• Recommended height: 200-300 pixels\n"
            "• Make sure text is clearly visible in the capture\n"
            "• You can use a screenshot tool to find these values"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Coordinate inputs
        form = QFormLayout()
        
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setValue(0)
        form.addRow("X Position:", self.x_spin)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setValue(0)
        form.addRow("Y Position:", self.y_spin)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 9999)
        self.width_spin.setValue(700)
        form.addRow("Width:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 9999)
        self.height_spin.setValue(400)
        form.addRow("Height:", self.height_spin)
        
        layout.addLayout(form)
        
        # Test capture button
        test_btn = QPushButton("Test Capture (saves test_capture.png)")
        test_btn.clicked.connect(self.test_capture)
        layout.addWidget(test_btn)
        
        # Find click coordinates button
        find_btn = QPushButton("Find Click Coordinates (hover over Open button)")
        find_btn.clicked.connect(self.find_click_coords)
        layout.addWidget(find_btn)
        
        self.click_coords_label = QLabel("Click coordinates will appear here")
        self.click_coords_label.setWordWrap(True)
        layout.addWidget(self.click_coords_label)
        
        # Save button
        save_btn = QPushButton("Save Coordinates")
        save_btn.clicked.connect(self.save_coordinates)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def test_capture(self):
        """Test the capture coordinates"""
        x = self.x_spin.value()
        y = self.y_spin.value()
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save("test_capture.png")
            QMessageBox.information(self, "Success", "Test capture saved as test_capture.png")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Capture failed: {str(e)}")
    
    def find_click_coords(self):
        """Help user find click coordinates by showing mouse position"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Find Click Coordinates")
        msg.setText(
            "Move your mouse over the 'Open' button for the FIRST chest.\n"
            "Press SPACE BAR to capture the coordinates.\n"
            "(Or click OK if you've already positioned the mouse)"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        # Create a timer to update mouse position
        coord_label = QLabel("Move mouse to Open button, then press SPACE...")
        msg.layout().addWidget(coord_label, 1, 0, 1, 2)
        
        self.captured_coords = None
        
        def update_coords():
            x, y = pyautogui.position()
            if self.captured_coords:
                coord_label.setText(f"✓ CAPTURED: X={self.captured_coords[0]}, Y={self.captured_coords[1]}")
            else:
                coord_label.setText(f"Current position: X={x}, Y={y} (Press SPACE to capture)")
        
        def capture_on_space(event):
            if event.key() == Qt.Key.Key_Space and not self.captured_coords:
                self.captured_coords = pyautogui.position()
        
        msg.keyPressEvent = capture_on_space
        
        timer = QTimer()
        timer.timeout.connect(update_coords)
        timer.start(100)  # Update every 100ms
        
        result = msg.exec()
        timer.stop()
        
        if result == QMessageBox.StandardButton.Ok:
            if self.captured_coords:
                x, y = self.captured_coords
            else:
                x, y = pyautogui.position()
            
            self.click_coords_label.setText(
                f"Open button coordinates: X={x}, Y={y}\n"
                f"Use these values in the code or tell the developer."
            )
            QMessageBox.information(
                self,
                "Coordinates Found",
                f"Open button is at:\nX: {x}\nY: {y}\n\n"
                f"Your capture area starts at X={self.x_spin.value()}, Y={self.y_spin.value()}"
            )
    
    def save_coordinates(self):
        """Save coordinates to config"""
        self.coords = (
            self.x_spin.value(),
            self.y_spin.value(),
            self.width_spin.value(),
            self.height_spin.value()
        )
        QMessageBox.information(self, "Success", "Coordinates saved!")
    
    def load_coordinates(self, coords):
        """Load coordinates from config"""
        if coords:
            self.x_spin.setValue(coords[0])
            self.y_spin.setValue(coords[1])
            self.width_spin.setValue(coords[2])
            self.height_spin.setValue(coords[3])
            self.coords = coords


class PointsManager(QWidget):
    """Widget for managing chest point values"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        label = QLabel("Set point values for each chest type:")
        layout.addWidget(label)
        
        # Scrollable area for chest types
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        self.point_inputs = {}
        
        # Get chest types from config
        chest_types = self.config.get('chest_types', [
            'Level 15 Crypt', 'Level 20 Crypt', 'Level 25 Crypt',
            'Common Chest', 'Rare Chest', 'Epic Chest',
            'Heroic Chest', 'Ancient Chest'
        ])
        
        for chest_type in chest_types:
            h_layout = QHBoxLayout()
            
            label = QLabel(chest_type + ":")
            label.setMinimumWidth(200)
            h_layout.addWidget(label)
            
            spin = QSpinBox()
            spin.setRange(0, 10000)
            spin.setValue(self.config.get_points(chest_type))
            h_layout.addWidget(spin)
            
            h_layout.addStretch()
            
            scroll_layout.addLayout(h_layout)
            self.point_inputs[chest_type] = spin
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Add new chest type
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("New Chest Type:"))
        self.new_type_input = QLineEdit()
        add_layout.addWidget(self.new_type_input)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_chest_type)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        # Save button
        save_btn = QPushButton("Save Point Values")
        save_btn.clicked.connect(self.save_points)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)
    
    def add_chest_type(self):
        """Add a new chest type"""
        chest_type = self.new_type_input.text().strip()
        if not chest_type:
            return
        
        if chest_type in self.point_inputs:
            QMessageBox.warning(self, "Warning", "Chest type already exists!")
            return
        
        # Add to config
        chest_types = self.config.get('chest_types', [])
        chest_types.append(chest_type)
        self.config.set('chest_types', chest_types)
        
        QMessageBox.information(self, "Success", f"Added {chest_type}. Restart to see changes.")
        self.new_type_input.clear()
    
    def save_points(self):
        """Save all point values"""
        points = {}
        for chest_type, spin in self.point_inputs.items():
            points[chest_type] = spin.value()
        
        self.config.set('points', points)
        QMessageBox.information(self, "Success", "Point values saved!")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config = ConfigManager()
        self.db = DatabaseManager()
        self.ocr = None
        self.capture_thread = None
        
        self.setWindowTitle("Total Battle - Clan Chest Tracker")
        self.setGeometry(100, 100, 900, 700)
        
        self.setup_ui()
        self.load_config()
        
        # Initialize OCR in background
        QTimer.singleShot(100, self.init_ocr)
    
    def setup_ui(self):
        """Setup the user interface"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Total Battle Chest Tracker")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Capture tab
        capture_tab = self.create_capture_tab()
        tabs.addTab(capture_tab, "Capture")
        
        # Setup tab
        self.coord_setup = CoordinateSetup()
        tabs.addTab(self.coord_setup, "Coordinates")
        
        # Points tab
        self.points_manager = PointsManager(self.config)
        tabs.addTab(self.points_manager, "Point Values")
        
        # Statistics tab
        stats_tab = self.create_stats_tab()
        tabs.addTab(stats_tab, "Statistics")
        
        # Data Review tab
        review_tab = self.create_review_tab()
        tabs.addTab(review_tab, "Review Data")
        
        layout.addWidget(tabs)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        central.setLayout(layout)
    
    def create_capture_tab(self):
        """Create the capture control tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_capture)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()
        
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(100, 2000)
        self.delay_spin.setValue(300)
        self.delay_spin.setSuffix(" ms")
        settings_layout.addRow("Delay between chests:", self.delay_spin)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Log area
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_stats_tab(self):
        """Create the statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Export buttons
        btn_layout = QHBoxLayout()
        
        daily_btn = QPushButton("Export Daily Report")
        daily_btn.clicked.connect(lambda: self.export_report('daily'))
        btn_layout.addWidget(daily_btn)
        
        weekly_btn = QPushButton("Export Weekly Report")
        weekly_btn.clicked.connect(lambda: self.export_report('weekly'))
        btn_layout.addWidget(weekly_btn)
        
        monthly_btn = QPushButton("Export Monthly Report")
        monthly_btn.clicked.connect(lambda: self.export_report('monthly'))
        btn_layout.addWidget(monthly_btn)
        
        layout.addLayout(btn_layout)
        
        # Current stats table
        stats_group = QGroupBox("Today's Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(['Player', 'Chests', 'Points'])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        stats_layout.addWidget(self.stats_table)
        
        refresh_btn = QPushButton("Refresh Statistics")
        refresh_btn.clicked.connect(self.refresh_stats)
        stats_layout.addWidget(refresh_btn)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_review_tab(self):
        """Create the data review tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Review today's captured chest data. You can see what was detected and check for errors.\n"
            "Note: Corrections will be added in a future update."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Review table
        review_group = QGroupBox("Today's Captured Chests")
        review_layout = QVBoxLayout()
        
        self.review_table = QTableWidget()
        self.review_table.setColumnCount(3)
        self.review_table.setHorizontalHeaderLabels(['Player Name', 'Chest Type', 'Time'])
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        review_layout.addWidget(self.review_table)
        
        refresh_review_btn = QPushButton("Refresh Data")
        refresh_review_btn.clicked.connect(self.refresh_review)
        review_layout.addWidget(refresh_review_btn)
        
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
        
        widget.setLayout(layout)
        return widget
    
    def init_ocr(self):
        """Initialize OCR model"""
        self.log("Initializing OCR model...")
        try:
            # Disable problematic backends
            import os
            os.environ['FLAGS_use_mkldnn'] = '0'
            
            self.ocr = PaddleOCR(
                use_textline_orientation=False,
                lang='en',
                enable_mkldnn=False,  # Disable OneDNN/MKLDNN
                text_det_box_thresh=0.3,  # Updated parameter name
                text_det_unclip_ratio=2.0,  # Updated parameter name
                text_recognition_batch_size=6  # Updated parameter name
            )
            self.log("OCR model ready!")
        except Exception as e:
            self.log(f"OCR initialization failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize OCR: {str(e)}")
    
    def start_capture(self):
        """Start the capture process"""
        # Validate setup
        if not self.coord_setup.coords:
            QMessageBox.warning(self, "Warning", "Please set up coordinates first!")
            return
        
        if not self.ocr:
            QMessageBox.warning(self, "Warning", "OCR model not ready yet!")
            return
        
        # Start capture thread
        self.capture_thread = CaptureThread(
            self.coord_setup.coords,
            self.ocr,
            self.db
        )
        
        self.capture_thread.status_update.connect(self.log)
        self.capture_thread.chest_found.connect(self.on_chest_found)
        self.capture_thread.processing_complete.connect(self.on_processing_complete)
        self.capture_thread.error_occurred.connect(self.on_error)
        
        # Set delay
        self.capture_thread.click_delay = self.delay_spin.value() / 1000.0
        
        self.capture_thread.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log("=== Processing Started ===")
    
    def stop_capture(self):
        """Stop the capture process"""
        if self.capture_thread:
            self.capture_thread.stop()
            self.log("Stopping...")
    
    def on_chest_found(self, player, chest_type):
        """Handle chest found signal"""
        self.log(f"✓ {player}: {chest_type}")
    
    def on_processing_complete(self, count):
        """Handle processing complete"""
        self.log(f"=== Processing Complete ===")
        self.log(f"Total chests processed: {count}")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        QMessageBox.information(
            self,
            "Complete",
            f"Processing finished!\n\nTotal chests processed: {count}"
        )
        
        self.refresh_stats()
    
    def on_error(self, error_msg):
        """Handle error"""
        self.log(f"ERROR: {error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.status_label.setText(message)
    
    def refresh_stats(self):
        """Refresh the statistics table"""
        stats = self.db.get_daily_stats()
        
        self.stats_table.setRowCount(len(stats))
        
        for i, (player, data) in enumerate(stats.items()):
            self.stats_table.setItem(i, 0, QTableWidgetItem(player))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(data['total_chests'])))
            self.stats_table.setItem(i, 2, QTableWidgetItem(str(data['total_points'])))
    
    def refresh_review(self):
        """Refresh the review table with all captured chests"""
        chests = self.db.get_all_chests(self.db.daily_db)
        
        self.review_table.setRowCount(len(chests))
        
        for i, chest in enumerate(chests):
            self.review_table.setItem(i, 0, QTableWidgetItem(chest['player_name']))
            self.review_table.setItem(i, 1, QTableWidgetItem(chest['chest_type']))
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(chest['timestamp'])
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = chest['timestamp']
            
            self.review_table.setItem(i, 2, QTableWidgetItem(time_str))
    
    def export_report(self, report_type):
        """Export HTML report"""
        self.log(f"Generating {report_type} report...")
        
        try:
            generator = HTMLGenerator(self.db, self.config)
            
            if report_type == 'daily':
                filepath = generator.generate_daily_report()
            elif report_type == 'weekly':
                filepath = generator.generate_weekly_report()
            else:
                filepath = generator.generate_monthly_report()
            
            self.log(f"Report saved: {filepath}")
            QMessageBox.information(
                self,
                "Success",
                f"{report_type.capitalize()} report generated!\n\nSaved to: {filepath}"
            )
            
        except Exception as e:
            self.log(f"Export failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")
    
    def load_config(self):
        """Load configuration"""
        coords = self.config.get('coordinates')
        if coords:
            self.coord_setup.load_coordinates(coords)
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save coordinates
        if self.coord_setup.coords:
            self.config.set('coordinates', self.coord_setup.coords)
        
        # Stop capture if running
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.stop()
            self.capture_thread.wait()
        
        # Auto-generate HTML reports
        try:
            self.log("Generating HTML reports...")
            generator = HTMLGenerator(self.db, self.config)
            generator.generate_daily_report()
            generator.generate_weekly_report()
            generator.generate_monthly_report()
            generator.generate_index()
            generator.cleanup_old_reports()
            self.log("HTML reports updated successfully")
        except Exception as e:
            print(f"Error generating reports on close: {e}")
        
        event.accept()


class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = Path(config_file)
        self.config = self.load()
    
    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return {}
        return {}
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        self.save()
    
    def get_points(self, chest_type):
        """Get points for a chest type"""
        points = self.config.get('points', {})
        return points.get(chest_type, 10)  # Default 10 points


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
