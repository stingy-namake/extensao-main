# THIS IS FOR TESTING PURPOSES ONLY! Don't forget to "pip install PyQt6"

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QGroupBox,
                             QRadioButton, QButtonGroup, QFileDialog, QMessageBox, QSlider,
                             QSplitter, QFrame, QProgressBar, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor
from PIL import Image, ImageDraw
import grade_it
import gen_gabarito
import testing_mark_gabarito

class GradingThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, image_path, expected_answers, position_data, threshold):
        super().__init__()
        self.image_path = image_path
        self.expected_answers = expected_answers
        self.position_data = position_data
        self.threshold = threshold

    def run(self):
        try:
            results = grade_it.grade_gabarito_improved(
                image_path=self.image_path,
                expected_answers=self.expected_answers,
                position_data=self.position_data,
                threshold=self.threshold,
                debug=False
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class ModernGradingSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Answer Sheet Grading System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_template_tab()
        self.create_marking_tab()
        self.create_grading_tab()
        self.create_results_tab()
        
        # Store data
        self.position_data = None
        self.current_results = None
        
    def get_stylesheet(self):
        return """
        QMainWindow {
            background-color: #1a1a1a;
        }
        
        QTabWidget::pane {
            border: 1px solid #333;
            background-color: #2d2d2d;
            border-radius: 4px;
        }
        
        QTabBar::tab {
            background-color: #333;
            border: 1px solid #444;
            padding: 10px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-weight: bold;
            color: #ccc;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QTabBar::tab:selected {
            background-color: #cc0000;
            color: white;
        }
        
        QTabBar::tab:hover {
            background-color: #555;
        }
        
        QGroupBox {
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #444;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: #2d2d2d;
            color: #ccc;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 6px 0 6px;
            color: #ccc;
        }
        
        QPushButton {
            background-color: #333;
            border: 1px solid #555;
            color: #ccc;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11px;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QPushButton:hover {
            background-color: #cc0000;
            color: white;
        }
        
        QPushButton:pressed {
            background-color: #990000;
        }
        
        QPushButton.success {
            background-color: #333;
        }
        
        QPushButton.success:hover {
            background-color: #cc0000;
        }
        
        QPushButton.warning {
            background-color: #333;
        }
        
        QPushButton.warning:hover {
            background-color: #cc0000;
        }
        
        QLineEdit {
            padding: 6px 10px;
            border: 1px solid #555;
            border-radius: 4px;
            font-size: 13px;
            background-color: #2d2d2d;
            color: #ccc;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QLineEdit:focus {
            border-color: #cc0000;
        }
        
        QTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px;
            font-family: 'Consolas', 'Monospace', 'Courier New';
            font-size: 11px;
            background-color: #2d2d2d;
            color: #ccc;
        }
        
        QLabel {
            color: #ccc;
            font-size: 13px;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QRadioButton {
            spacing: 6px;
            font-size: 11px;
            color: #ccc;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QRadioButton::indicator {
            width: 14px;
            height: 14px;
            border-radius: 7px;
            border: 1px solid #666;
            background-color: #333;
        }
        
        QRadioButton::indicator:checked {
            background-color: #cc0000;
            border: 1px solid #cc0000;
        }
        
        QScrollArea {
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #2d2d2d;
        }
        
        QProgressBar {
            border: 1px solid #444;
            border-radius: 4px;
            text-align: center;
            color: white;
            font-weight: bold;
            background-color: #333;
            font-family: 'Consolas', 'Monospace', 'Courier New';
        }
        
        QProgressBar::chunk {
            background-color: #cc0000;
            border-radius: 3px;
        }
        """

    def create_template_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Generate Answer Sheet Template")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #cc0000; margin: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Settings group
        settings_group = QGroupBox("Template Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Questions input
        questions_layout = QHBoxLayout()
        questions_layout.addWidget(QLabel("Number of Questions:"))
        self.questions_edit = QLineEdit("15")
        questions_layout.addWidget(self.questions_edit)
        questions_layout.addStretch()
        settings_layout.addLayout(questions_layout)
        
        # Choices input
        choices_layout = QHBoxLayout()
        choices_layout.addWidget(QLabel("Choices:"))
        self.choices_edit = QLineEdit("A,B,C,D,E")
        choices_layout.addWidget(self.choices_edit)
        choices_layout.addStretch()
        settings_layout.addLayout(choices_layout)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Template")
        self.generate_btn.setProperty("class", "success")
        self.generate_btn.clicked.connect(self.generate_template)
        settings_layout.addWidget(self.generate_btn)
        
        # Status
        self.template_status = QLabel("Ready to generate template")
        self.template_status.setStyleSheet("color: #888; font-style: italic;")
        settings_layout.addWidget(self.template_status)
        
        left_layout.addWidget(settings_group)
        left_layout.addStretch()
        
        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        preview_group = QGroupBox("Template Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.template_preview = QLabel("No template generated yet\n\nClick 'Generate Template' to create one")
        self.template_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.template_preview.setStyleSheet("color: #888; font-style: italic; padding: 32px;")
        preview_layout.addWidget(self.template_preview)
        
        right_layout.addWidget(preview_group)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        self.tabs.addTab(tab, "Generate Template")

    def create_marking_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Mark Answer Sheet")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #cc0000; margin: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Answer selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        selection_group = QGroupBox("Answer Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        # Scroll area for questions
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.marking_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        selection_layout.addWidget(scroll_area)
        
        left_layout.addWidget(selection_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.load_template_btn = QPushButton("Load Template")
        self.load_template_btn.clicked.connect(self.load_template_for_marking)
        control_layout.addWidget(self.load_template_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setProperty("class", "warning")
        self.clear_btn.clicked.connect(self.clear_all_answers)
        control_layout.addWidget(self.clear_btn)
        
        self.create_sheet_btn = QPushButton("Create Marked Sheet")
        self.create_sheet_btn.setProperty("class", "success")
        self.create_sheet_btn.clicked.connect(self.create_marked_sheet_gui)
        control_layout.addWidget(self.create_sheet_btn)
        
        left_layout.addLayout(control_layout)
        
        # Status
        self.marking_status = QLabel("Load a template to start marking")
        self.marking_status.setStyleSheet("color: #888; font-style: italic; padding: 8px;")
        left_layout.addWidget(self.marking_status)
        
        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        preview_group = QGroupBox("Template Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.marking_preview = QLabel("Load template to see preview\n\nClick 'Load Template' to begin")
        self.marking_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.marking_preview.setStyleSheet("color: #888; font-style: italic; padding: 32px;")
        preview_layout.addWidget(self.marking_preview)
        
        right_layout.addWidget(preview_group)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])
        
        self.tabs.addTab(tab, "Mark Sheet")

    def create_grading_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Grade Answer Sheet")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #cc0000; margin: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Settings
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File selection
        file_group = QGroupBox("Marked Sheet")
        file_layout = QVBoxLayout(file_group)
        
        file_input_layout = QHBoxLayout()
        self.marked_file_edit = QLineEdit("./templates/marked_demo.png")
        file_input_layout.addWidget(self.marked_file_edit)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_marked_file)
        file_input_layout.addWidget(self.browse_btn)
        
        file_layout.addLayout(file_input_layout)
        left_layout.addWidget(file_group)
        
        # Threshold settings
        threshold_group = QGroupBox("Detection Settings")
        threshold_layout = QVBoxLayout(threshold_group)
        
        threshold_slider_layout = QHBoxLayout()
        threshold_slider_layout.addWidget(QLabel("Sensitivity:"))
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setMinimum(10)
        self.threshold_slider.setMaximum(40)
        self.threshold_slider.setValue(20)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        threshold_slider_layout.addWidget(self.threshold_slider)
        
        self.threshold_label = QLabel("0.2")
        threshold_slider_layout.addWidget(self.threshold_label)
        
        threshold_layout.addLayout(threshold_slider_layout)
        threshold_layout.addWidget(QLabel("Lower = more sensitive, Higher = less sensitive"))
        left_layout.addWidget(threshold_group)
        
        # Quick answers input
        answers_group = QGroupBox("Quick Answer Input")
        answers_layout = QVBoxLayout(answers_group)
        
        self.answers_edit = QLineEdit("A,B,D,E,E,E,D,B,A,A,C,C,C,D,E,A,E,B,A,E,B,B,C,B,E")
        answers_layout.addWidget(self.answers_edit)
        
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()
        self.apply_btn = QPushButton("Apply to Radio Buttons")
        self.apply_btn.clicked.connect(self.apply_text_answers)
        apply_layout.addWidget(self.apply_btn)
        
        answers_layout.addLayout(apply_layout)
        left_layout.addWidget(answers_group)
        
        # Grade button
        self.grade_btn = QPushButton("Grade Sheet")
        self.grade_btn.setProperty("class", "success")
        self.grade_btn.clicked.connect(self.grade_sheet)
        left_layout.addWidget(self.grade_btn)
        
        # Status
        self.grading_status = QLabel("Ready to grade")
        self.grading_status.setStyleSheet("color: #888; font-style: italic; padding: 8px;")
        left_layout.addWidget(self.grading_status)
        
        left_layout.addStretch()
        
        # Right panel - Expected answers
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        expected_group = QGroupBox("Expected Answers")
        expected_layout = QVBoxLayout(expected_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.load_grading_btn = QPushButton("Load Template")
        self.load_grading_btn.clicked.connect(self.load_template_for_grading)
        control_layout.addWidget(self.load_grading_btn)
        
        self.set_all_a_btn = QPushButton("A All")
        self.set_all_a_btn.clicked.connect(lambda: self.set_all_expected_answers("A"))
        control_layout.addWidget(self.set_all_a_btn)
        
        self.set_all_b_btn = QPushButton("B All")
        self.set_all_b_btn.clicked.connect(lambda: self.set_all_expected_answers("B"))
        control_layout.addWidget(self.set_all_b_btn)
        
        self.clear_expected_btn = QPushButton("Clear")
        self.clear_expected_btn.setProperty("class", "warning")
        self.clear_expected_btn.clicked.connect(self.clear_all_expected_answers)
        control_layout.addWidget(self.clear_expected_btn)
        
        expected_layout.addLayout(control_layout)
        
        # Scroll area for expected answers
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.expected_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        expected_layout.addWidget(scroll_area)
        
        right_layout.addWidget(expected_group)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        self.tabs.addTab(tab, "Grade Sheet")

    def create_results_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Grading Results")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #cc0000; margin: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Text results
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        results_group = QGroupBox("Detailed Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        left_layout.addWidget(results_group)
        
        # Right panel - Image display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        image_group = QGroupBox("Visualization")
        image_layout = QVBoxLayout(image_group)
        
        self.results_image = QLabel("Graded image will appear here\n\nGrade a sheet to see results")
        self.results_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_image.setStyleSheet("color: #888; font-style: italic; padding: 32px;")
        image_layout.addWidget(self.results_image)
        
        right_layout.addWidget(image_group)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.clear_results_btn = QPushButton("Clear Results")
        self.clear_results_btn.setProperty("class", "warning")
        self.clear_results_btn.clicked.connect(self.clear_results)
        control_layout.addWidget(self.clear_results_btn)
        
        self.save_results_btn = QPushButton("Save Results")
        self.save_results_btn.setProperty("class", "success")
        self.save_results_btn.clicked.connect(self.save_results)
        control_layout.addWidget(self.save_results_btn)
        
        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self.export_report)
        control_layout.addWidget(self.export_btn)
        
        layout.addLayout(control_layout)
        
        self.tabs.addTab(tab, "Results")

    def generate_template(self):
        try:
            self.template_status.setText("Generating template...")
            
            num_questions = int(self.questions_edit.text())
            choices = tuple(self.choices_edit.text().split(','))
            
            template_path, position_data = gen_gabarito.generate_gabarito_png_improved(
                "./templates/gabarito_demo.png",
                num_questions=num_questions,
                choices=choices,
                add_reference_marks=True
            )
            
            self.template_status.setText("Template generated successfully!")
            
            # Display the generated template
            self.display_template_image(template_path)
            
            QMessageBox.information(self, "Success", 
                                  f"Template generated successfully!\n\nSaved as: {template_path}")
            
        except Exception as e:
            self.template_status.setText("Error generating template")
            QMessageBox.critical(self, "Error", f"Failed to generate template: {str(e)}")

    def display_template_image(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(400, 500, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
                self.template_preview.setPixmap(scaled_pixmap)
                self.template_preview.setText("")
        except Exception as e:
            self.template_preview.setText(f"Error loading image: {str(e)}")

    def load_template_for_marking(self):
        try:
            template_path = "./templates/gabarito_demo.png"
            position_file = "./templates/gabarito_demo_positions.json"
            
            if not os.path.exists(template_path) or not os.path.exists(position_file):
                QMessageBox.critical(self, "Error", "Template not found. Please generate a template first.")
                return
            
            # Load position data
            with open(position_file, 'r') as f:
                self.position_data = json.load(f)
            
            # Clear existing widgets
            for i in reversed(range(self.marking_layout.count())):
                widget = self.marking_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            self.question_vars = []
            
            # Create header
            header_layout = QHBoxLayout()
            header_layout.addWidget(QLabel("Question"))
            
            choices = self.position_data.get('choices', ['A', 'B', 'C', 'D', 'E'])
            for choice in choices:
                header_layout.addWidget(QLabel(choice))
            
            header_widget = QWidget()
            header_widget.setLayout(header_layout)
            self.marking_layout.addWidget(header_widget)
            
            # Create radio buttons for each question
            for q_data in self.position_data['bubble_positions']:
                q_num = q_data['question']
                row_layout = QHBoxLayout()
                row_layout.addWidget(QLabel(f"Q{q_num:02d}"))
                
                # Create button group for this question
                button_group = QButtonGroup(self)
                button_group.setExclusive(True)
                
                for choice in choices:
                    radio = QRadioButton()
                    button_group.addButton(radio)
                    row_layout.addWidget(radio)
                    # Store reference to get/set value later
                    setattr(radio, 'choice_value', choice)
                    setattr(radio, 'question_num', q_num)
                    radio.toggled.connect(self.on_answer_selected)
                
                row_widget = QWidget()
                row_widget.setLayout(row_layout)
                self.marking_layout.addWidget(row_widget)
                
                # Store the button group for this question
                self.question_vars.append((q_num, button_group))
            
            # Display template image
            self.display_marking_preview(template_path)
            
            self.marking_status.setText("Template loaded. Select answers using the radio buttons.")
            
        except Exception as e:
            self.marking_status.setText("Error loading template")
            QMessageBox.critical(self, "Error", f"Failed to load template: {str(e)}")

    def display_marking_preview(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(400, 500, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
                self.marking_preview.setPixmap(scaled_pixmap)
                self.marking_preview.setText("")
        except Exception as e:
            self.marking_preview.setText(f"Error loading image: {str(e)}")

    def on_answer_selected(self, checked):
        if checked:
            radio = self.sender()
            if hasattr(radio, 'question_num') and hasattr(radio, 'choice_value'):
                self.marking_status.setText(f"Q{radio.question_num}: {radio.choice_value} selected")

    def clear_all_answers(self):
        for q_num, button_group in self.question_vars:
            button_group.setExclusive(False)
            for button in button_group.buttons():
                button.setChecked(False)
            button_group.setExclusive(True)
        self.marking_status.setText("All answers cleared")

    def create_marked_sheet_gui(self):
        try:
            if not hasattr(self, 'position_data'):
                QMessageBox.critical(self, "Error", "Please load a template first.")
                return
            
            # Collect answers from radio buttons
            answers = {}
            for q_num, button_group in self.question_vars:
                checked_button = button_group.checkedButton()
                if checked_button and hasattr(checked_button, 'choice_value'):
                    answers[q_num] = checked_button.choice_value
            
            if not answers:
                QMessageBox.warning(self, "Warning", "No answers selected. Please select at least one answer.")
                return
            
            # Create marked sheet
            template_path = "./templates/gabarito_demo.png"
            output_path = "my_marked_sheet.png"
            
            marked_file = testing_mark_gabarito.create_marked_sheet_from_answers(
                answers, template_path, self.position_data, output_path
            )
            
            self.marking_status.setText(f"Marked sheet created: {marked_file}")
            
            # Update grading tab with the new file
            self.marked_file_edit.setText(marked_file)
            
            QMessageBox.information(self, "Success", 
                                  f"Marked sheet created!\n\nSaved as: {marked_file}\n\nYou can now grade it in the 'Grade Sheet' tab.")
            
        except Exception as e:
            self.marking_status.setText("Error creating marked sheet")
            QMessageBox.critical(self, "Error", f"Failed to create marked sheet: {str(e)}")

    def browse_marked_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Marked Answer Sheet", "", "PNG Files (*.png);;All Files (*)"
        )
        if filename:
            self.marked_file_edit.setText(filename)

    def on_threshold_changed(self, value):
        threshold = value / 100.0
        self.threshold_label.setText(f"{threshold:.2f}")

    def load_template_for_grading(self):
        try:
            position_file = "./templates/gabarito_demo_positions.json"
            
            if not os.path.exists(position_file):
                QMessageBox.critical(self, "Error", "Template not found. Please generate a template first.")
                return
            
            # Load position data
            with open(position_file, 'r') as f:
                self.grading_position_data = json.load(f)
            
            # Clear existing widgets
            for i in reversed(range(self.expected_layout.count())):
                widget = self.expected_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            self.expected_answer_vars = []
            
            # Create header
            header_layout = QHBoxLayout()
            header_layout.addWidget(QLabel("Question"))
            
            choices = self.grading_position_data.get('choices', ['A', 'B', 'C', 'D', 'E'])
            for choice in choices:
                header_layout.addWidget(QLabel(choice))
            
            header_widget = QWidget()
            header_widget.setLayout(header_layout)
            self.expected_layout.addWidget(header_widget)
            
            # Create radio buttons for each question
            for q_data in self.grading_position_data['bubble_positions']:
                q_num = q_data['question']
                row_layout = QHBoxLayout()
                row_layout.addWidget(QLabel(f"Q{q_num:02d}"))
                
                # Create button group for this question
                button_group = QButtonGroup(self)
                button_group.setExclusive(True)
                
                for choice in choices:
                    radio = QRadioButton()
                    button_group.addButton(radio)
                    row_layout.addWidget(radio)
                    setattr(radio, 'choice_value', choice)
                    setattr(radio, 'question_num', q_num)
                    radio.toggled.connect(self.on_expected_answer_selected)
                
                row_widget = QWidget()
                row_widget.setLayout(row_layout)
                self.expected_layout.addWidget(row_widget)
                
                # Store the button group for this question
                self.expected_answer_vars.append((q_num, button_group))
            
            # Load current answers from text field
            self.apply_text_answers()
            
            self.grading_status.setText("Template loaded. Set expected answers using radio buttons.")
            
        except Exception as e:
            self.grading_status.setText("Error loading template")
            QMessageBox.critical(self, "Error", f"Failed to load template: {str(e)}")

    def on_expected_answer_selected(self, checked):
        if checked:
            self.update_answers_text_field()

    def update_answers_text_field(self):
        answers = []
        for q_num, button_group in self.expected_answer_vars:
            checked_button = button_group.checkedButton()
            if checked_button and hasattr(checked_button, 'choice_value'):
                answers.append(checked_button.choice_value)
            else:
                answers.append("A")  # Default to "A" if not set
        
        self.answers_edit.setText(','.join(answers))

    def apply_text_answers(self):
        if not hasattr(self, 'expected_answer_vars') or not self.expected_answer_vars:
            return
            
        answers_text = self.answers_edit.text()
        if answers_text:
            answers = answers_text.split(',')
            for i, (q_num, button_group) in enumerate(self.expected_answer_vars):
                if i < len(answers):
                    choice = answers[i].strip()
                    # Find and check the radio button for this choice
                    for button in button_group.buttons():
                        if hasattr(button, 'choice_value') and button.choice_value == choice:
                            button.setChecked(True)
                            break

    def set_all_expected_answers(self, choice):
        if hasattr(self, 'expected_answer_vars'):
            for q_num, button_group in self.expected_answer_vars:
                for button in button_group.buttons():
                    if hasattr(button, 'choice_value') and button.choice_value == choice:
                        button.setChecked(True)
                        break
            self.update_answers_text_field()
            self.grading_status.setText(f"All expected answers set to {choice}")

    def clear_all_expected_answers(self):
        if hasattr(self, 'expected_answer_vars'):
            for q_num, button_group in self.expected_answer_vars:
                button_group.setExclusive(False)
                for button in button_group.buttons():
                    button.setChecked(False)
                button_group.setExclusive(True)
            self.update_answers_text_field()
            self.grading_status.setText("All expected answers cleared")

    def grade_sheet(self):
        try:
            self.grading_status.setText("Grading sheet...")
            self.grade_btn.setEnabled(False)
            
            # Load position data
            position_file = "./templates/gabarito_demo_positions.json"
            with open(position_file, 'r') as f:
                position_data = json.load(f)
            
            # Parse expected answers and threshold
            expected_answers = self.answers_edit.text().split(',')
            threshold = self.threshold_slider.value() / 100.0
            
            # Create and start grading thread
            self.grading_thread = GradingThread(
                self.marked_file_edit.text(),
                expected_answers,
                position_data,
                threshold
            )
            self.grading_thread.finished.connect(self.on_grading_finished)
            self.grading_thread.error.connect(self.on_grading_error)
            self.grading_thread.start()
            
        except Exception as e:
            self.grading_status.setText("Error starting grading")
            QMessageBox.critical(self, "Error", f"Failed to start grading: {str(e)}")
            self.grade_btn.setEnabled(True)

    def on_grading_finished(self, results):
        self.current_results = results
        self.display_results(results)
        self.create_visualization(results)
        self.grading_status.setText("Grading completed")
        self.grade_btn.setEnabled(True)
        self.tabs.setCurrentIndex(3)  # Switch to results tab

    def on_grading_error(self, error_msg):
        self.grading_status.setText("Error grading sheet")
        QMessageBox.critical(self, "Error", f"Failed to grade sheet: {error_msg}")
        self.grade_btn.setEnabled(True)

    def display_results(self, results):
        text = "GRADE REPORT\n"
        text += "=" * 40 + "\n"
        text += f"Score: {results['total_score']}/{results['max_score']}\n"
        text += f"Percentage: {results['percentage']:.1f}%\n"
        text += f"Multiple answers: {results['multiple_answers']}\n"
        text += f"Unanswered: {results['unanswered']}\n\n"
        
        text += "DETAILED RESULTS\n"
        text += "=" * 40 + "\n"
        for item in results['question_results']:
            status = "CORRECT" if item['is_correct'] else "WRONG"
            if item['student_answer'] in ['MULTI', 'NONE']:
                status = "MULTI/NONE"
            
            line = f"Q{item['question']:02d}: {status:10} Student={item['student_answer']:5} Correct={item['correct_answer']}"
            
            if not item['is_correct'] and item['student_answer'] not in ['MULTI', 'NONE']:
                marked_ratio = item['bubble_status'][item['student_answer']]
                correct_ratio = item['bubble_status'][item['correct_answer']]
                line += f" (marked: {marked_ratio:.2f}, correct: {correct_ratio:.2f})"
            
            text += line + "\n"
        
        self.results_text.setText(text)

    def create_visualization(self, results):
        try:
            # This is a simplified visualization - you might want to enhance this
            marked_img = Image.open(self.marked_file_edit.text())
            
            # Load position data for visualization
            position_file = "./templates/gabarito_demo_positions.json"
            with open(position_file, 'r') as f:
                position_data = json.load(f)
            
            # Simple visualization logic (similar to previous version)
            draw = ImageDraw.Draw(marked_img)
            for q_data in position_data['bubble_positions']:
                q_num = q_data['question']
                result = next((r for r in results['question_results'] if r['question'] == q_num), None)
                
                if result:
                    correct_answer = result['correct_answer']
                    student_answer = result['student_answer']
                    
                    for bubble in q_data['bubbles']:
                        choice = bubble['choice']
                        cx, cy = bubble['center']
                        
                        # Determine circle color
                        if choice == correct_answer and choice == student_answer:
                            color = "green"
                        elif choice == correct_answer:
                            color = "blue"
                        elif choice == student_answer and student_answer not in ['MULTI', 'NONE']:
                            color = "red"
                        elif result['bubble_status'].get(choice, 0) > 0.2:
                            color = "orange"
                        else:
                            continue
                        
                        # Draw circle around bubble
                        draw.ellipse([cx-15, cy-15, cx+15, cy+15], outline=color, width=3)
            
            # Save temporary image and display it
            temp_path = "temp_visualization.png"
            marked_img.save(temp_path)
            
            pixmap = QPixmap(temp_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(400, 500, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
                self.results_image.setPixmap(scaled_pixmap)
                self.results_image.setText("")
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
                
        except Exception as e:
            self.results_image.setText(f"Error creating visualization: {str(e)}")

    def clear_results(self):
        self.results_text.clear()
        self.results_image.setText("Graded image will appear here\n\nGrade a sheet to see results")
        self.current_results = None

    def save_results(self):
        if not self.current_results:
            QMessageBox.warning(self, "Warning", "No results to save. Please grade a sheet first.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, "Success", f"Results saved to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save results: {str(e)}")

    def export_report(self):
        QMessageBox.information(self, "Info", "Export feature would generate a PDF report with charts and analysis.")

def main():
    # Check if templates directory exists
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Answer Sheet Grading System")
    
    # Set monospaced font for the entire application
    font = QFont("Consolas", 9)
    app.setFont(font)
    
    window = ModernGradingSystem()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()