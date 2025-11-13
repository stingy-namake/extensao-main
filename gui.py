import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
import json
from PIL import Image, ImageTk
import threading

class GradingSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Answer Sheet Grading System")
        self.root.geometry("1000x700")
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_template_tab()
        self.create_marking_tab()
        self.create_grading_tab()
        self.create_results_tab()
        
        # Store images to prevent garbage collection
        self.display_images = []
        
    def create_template_tab(self):
        """Tab for generating answer sheet templates"""
        self.template_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.template_frame, text="1. Generate Template")
        
        ttk.Label(self.template_frame, text="Generate Answer Sheet Template", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Questions input
        questions_frame = ttk.Frame(self.template_frame)
        questions_frame.pack(pady=5, fill='x', padx=20)
        ttk.Label(questions_frame, text="Number of Questions:").pack(side='left')
        self.questions_var = tk.StringVar(value="15")
        ttk.Entry(questions_frame, textvariable=self.questions_var, width=10).pack(side='left', padx=5)
        
        # Choices input
        choices_frame = ttk.Frame(self.template_frame)
        choices_frame.pack(pady=5, fill='x', padx=20)
        ttk.Label(choices_frame, text="Choices (comma-separated):").pack(side='left')
        self.choices_var = tk.StringVar(value="A,B,C,D,E")
        ttk.Entry(choices_frame, textvariable=self.choices_var, width=20).pack(side='left', padx=5)
        
        # Generate button
        ttk.Button(self.template_frame, text="Generate Template", 
                  command=self.generate_template).pack(pady=20)
        
        # Status
        self.template_status = ttk.Label(self.template_frame, text="Ready to generate template")
        self.template_status.pack(pady=5)
        
        # Template preview
        ttk.Label(self.template_frame, text="Template Preview:", 
                 font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        
        self.template_preview_frame = ttk.Frame(self.template_frame)
        self.template_preview_frame.pack(pady=10, fill='both', expand=True)
        
        self.template_image_label = ttk.Label(self.template_preview_frame, text="No template generated yet")
        self.template_image_label.pack(pady=20)
        
    def create_marking_tab(self):
        """Tab for marking answer sheets with checkboxes"""
        self.marking_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.marking_frame, text="2. Mark Sheet")
        
        ttk.Label(self.marking_frame, text="Mark Answer Sheet - Interactive", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Main marking area
        marking_container = ttk.Frame(self.marking_frame)
        marking_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Questions and checkboxes
        left_frame = ttk.Frame(marking_container)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Scrollable frame for questions
        canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Question checkboxes will be created here dynamically
        self.question_vars = []
        
        # Control buttons
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill='x', pady=10)
        
        ttk.Button(control_frame, text="Load Template", 
                  command=self.load_template_for_marking).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Clear All", 
                  command=self.clear_all_answers).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Create Marked Sheet", 
                  command=self.create_marked_sheet_gui).pack(side='left', padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right side - Template preview
        right_frame = ttk.Frame(marking_container)
        right_frame.pack(side='right', fill='both', expand=True)
        
        ttk.Label(right_frame, text="Template Preview", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.marking_preview_label = ttk.Label(right_frame, text="Load template to see preview")
        self.marking_preview_label.pack(pady=10, fill='both', expand=True)
        
        # Status
        self.marking_status = ttk.Label(self.marking_frame, text="Load a template to start marking")
        self.marking_status.pack(pady=5)
        
    def create_grading_tab(self):
        """Tab for grading marked sheets with radio buttons for expected answers"""
        self.grading_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.grading_frame, text="3. Grade Sheet")
        
        ttk.Label(self.grading_frame, text="Grade Answer Sheet", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Main grading area
        grading_container = ttk.Frame(self.grading_frame)
        grading_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - File selection and settings
        left_frame = ttk.Frame(grading_container)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(left_frame)
        file_frame.pack(pady=10, fill='x')
        
        ttk.Label(file_frame, text="Marked Sheet:").pack(side='left')
        self.marked_file_var = tk.StringVar(value="./templates/marked_demo.png")
        ttk.Entry(file_frame, textvariable=self.marked_file_var, width=30).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_marked_file).pack(side='left', padx=5)
        
        # Threshold
        threshold_frame = ttk.Frame(left_frame)
        threshold_frame.pack(pady=10, fill='x')
        
        ttk.Label(threshold_frame, text="Detection Threshold:").pack(side='left')
        self.threshold_var = tk.StringVar(value="0.2")
        ttk.Entry(threshold_frame, textvariable=self.threshold_var, width=10).pack(side='left', padx=5)
        ttk.Label(threshold_frame, text="(0.1-0.4, lower = more sensitive)").pack(side='left')
        
        # Expected answers section
        ttk.Label(left_frame, text="Expected Answers:", 
                 font=('Arial', 12, 'bold')).pack(pady=(20, 5), anchor='w')
        
        # Text entry for quick input (alternative to radio buttons)
        text_frame = ttk.Frame(left_frame)
        text_frame.pack(pady=5, fill='x')
        
        ttk.Label(text_frame, text="Quick Input:").pack(side='left')
        self.answers_var = tk.StringVar(value="A,B,D,E,E,E,D,B,A,A,C,C,C,D,E,A,E,B,A,E,B,B,C,B,E")
        ttk.Entry(text_frame, textvariable=self.answers_var, width=40).pack(side='left', padx=5)
        ttk.Button(text_frame, text="Apply", command=self.apply_text_answers).pack(side='left', padx=5)
        
        # Grade button
        ttk.Button(left_frame, text="Grade Sheet", 
                  command=self.grade_sheet).pack(pady=20)
        
        # Status
        self.grading_status = ttk.Label(left_frame, text="Ready to grade")
        self.grading_status.pack(pady=5)
        
        # Right side - Expected answers with radio buttons
        right_frame = ttk.Frame(grading_container)
        right_frame.pack(side='right', fill='both', expand=True)
        
        ttk.Label(right_frame, text="Set Expected Answers", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Scrollable frame for expected answers
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.expected_answers_frame = ttk.Frame(canvas)
        
        self.expected_answers_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.expected_answers_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Expected answers radio buttons will be created here dynamically
        self.expected_answer_vars = []
        
        # Control buttons for expected answers
        expected_controls = ttk.Frame(right_frame)
        expected_controls.pack(fill='x', pady=5)
        
        ttk.Button(expected_controls, text="Load Template", 
                  command=self.load_template_for_grading).pack(side='left', padx=2)
        ttk.Button(expected_controls, text="Set All A", 
                  command=lambda: self.set_all_expected_answers("A")).pack(side='left', padx=2)
        ttk.Button(expected_controls, text="Set All B", 
                  command=lambda: self.set_all_expected_answers("B")).pack(side='left', padx=2)
        ttk.Button(expected_controls, text="Clear All", 
                  command=self.clear_all_expected_answers).pack(side='left', padx=2)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_results_tab(self):
        """Tab for displaying results with images"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="4. Results")
        
        ttk.Label(self.results_frame, text="Grading Results", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Create paned window for split view
        paned_window = ttk.PanedWindow(self.results_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Text results
        text_frame = ttk.Frame(paned_window)
        paned_window.add(text_frame, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(text_frame, height=20, width=50)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Right side - Image display
        image_frame = ttk.Frame(paned_window)
        paned_window.add(image_frame, weight=1)
        
        ttk.Label(image_frame, text="Graded Sheet Visualization", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.results_image_label = ttk.Label(image_frame, text="Graded image will appear here")
        self.results_image_label.pack(pady=10, fill='both', expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(self.results_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.clear_results).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Results", 
                  command=self.save_results).pack(side='left', padx=5)
        
    def generate_template(self):
        """Generate answer sheet template"""
        try:
            self.template_status.config(text="Generating template...")
            self.root.update()
            
            # Import and call the template generation function
            from gen_gabarito import generate_gabarito_png_improved
            
            num_questions = int(self.questions_var.get())
            choices = tuple(self.choices_var.get().split(','))
            
            template_path, position_data = generate_gabarito_png_improved(
                "./templates/gabarito_demo.png",
                num_questions=num_questions,
                choices=choices,
                add_reference_marks=True
            )
            
            self.template_status.config(text=f"Template generated: {template_path}")
            
            # Display the generated template
            self.display_template_image(template_path)
            
            messagebox.showinfo("Success", f"Template generated successfully!\nSaved as: {template_path}")
            
        except Exception as e:
            self.template_status.config(text="Error generating template")
            messagebox.showerror("Error", f"Failed to generate template: {str(e)}")
    
    def display_template_image(self, image_path):
        """Display template image in preview"""
        try:
            image = Image.open(image_path)
            # Resize for display
            display_size = (400, 500)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.template_image_label.configure(image=photo)
            self.template_image_label.image = photo  # Keep a reference
            self.display_images.append(photo)  # Prevent garbage collection
            
        except Exception as e:
            self.template_image_label.config(text=f"Error loading image: {str(e)}")
    
    def load_template_for_marking(self):
        """Load template and create checkboxes for marking"""
        try:
            template_path = "./templates/gabarito_demo.png"
            position_file = "./templates/gabarito_demo_positions.json"
            
            if not os.path.exists(template_path) or not os.path.exists(position_file):
                messagebox.showerror("Error", "Template not found. Please generate a template first.")
                return
            
            # Load position data
            with open(position_file, 'r') as f:
                self.position_data = json.load(f)
            
            # Clear existing checkboxes
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.question_vars = []
            
            # Create checkboxes for each question
            ttk.Label(self.scrollable_frame, text="Question", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2)
            
            # Create choice headers
            choices = self.position_data.get('choices', ['A', 'B', 'C', 'D', 'E'])
            for i, choice in enumerate(choices):
                ttk.Label(self.scrollable_frame, text=choice, font=('Arial', 10, 'bold')).grid(row=0, column=i+1, padx=5, pady=2)
            
            # Create radio buttons for each question
            for q_data in self.position_data['bubble_positions']:
                q_num = q_data['question']
                row = q_num
                
                ttk.Label(self.scrollable_frame, text=f"Q{q_num:02d}").grid(row=row, column=0, padx=5, pady=2, sticky='w')
                
                # Create variable for this question
                var = tk.StringVar(value="")  # Start with no selection
                self.question_vars.append((q_num, var))
                
                # Create radio buttons for each choice
                for i, choice in enumerate(choices):
                    rb = ttk.Radiobutton(
                        self.scrollable_frame, 
                        text="", 
                        variable=var, 
                        value=choice,
                        command=lambda q=q_num, c=choice: self.on_answer_selected(q, c)
                    )
                    rb.grid(row=row, column=i+1, padx=5, pady=2)
            
            # Display template image
            self.display_template_image_marking(template_path)
            
            self.marking_status.config(text="Template loaded. Select answers using the checkboxes.")
            
        except Exception as e:
            self.marking_status.config(text="Error loading template")
            messagebox.showerror("Error", f"Failed to load template: {str(e)}")
    
    def display_template_image_marking(self, image_path):
        """Display template image in marking tab"""
        try:
            image = Image.open(image_path)
            # Resize for display
            display_size = (400, 500)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.marking_preview_label.configure(image=photo)
            self.marking_preview_label.image = photo
            self.display_images.append(photo)
            
        except Exception as e:
            self.marking_preview_label.config(text=f"Error loading image: {str(e)}")
    
    def on_answer_selected(self, question, choice):
        """Called when an answer is selected"""
        self.marking_status.config(text=f"Q{question}: {choice} selected")
    
    def clear_all_answers(self):
        """Clear all selected answers"""
        for q_num, var in self.question_vars:
            var.set("")
        self.marking_status.config(text="All answers cleared")
    
    def create_marked_sheet_gui(self):
        """Create marked sheet from GUI selections"""
        try:
            if not hasattr(self, 'position_data'):
                messagebox.showerror("Error", "Please load a template first.")
                return
            
            # Collect answers from checkboxes
            answers = {}
            for q_num, var in self.question_vars:
                answer = var.get()
                if answer:
                    answers[q_num] = answer
            
            if not answers:
                messagebox.showwarning("Warning", "No answers selected. Please select at least one answer.")
                return
            
            # Create marked sheet
            from testing_mark_gabarito import create_marked_sheet_from_answers
            
            template_path = "./templates/gabarito_demo.png"
            output_path = "my_marked_sheet.png"
            
            marked_file = create_marked_sheet_from_answers(answers, template_path, self.position_data, output_path)
            
            self.marking_status.config(text=f"Marked sheet created: {marked_file}")
            
            # Update grading tab with the new file
            self.marked_file_var.set(marked_file)
            
            messagebox.showinfo("Success", f"Marked sheet created!\nSaved as: {marked_file}\n\nYou can now grade it in the 'Grade Sheet' tab.")
            
        except Exception as e:
            self.marking_status.config(text="Error creating marked sheet")
            messagebox.showerror("Error", f"Failed to create marked sheet: {str(e)}")
    
    def browse_marked_file(self):
        """Browse for marked sheet file"""
        filename = filedialog.askopenfilename(
            title="Select Marked Answer Sheet",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.marked_file_var.set(filename)
    
    def load_template_for_grading(self):
        """Load template and create radio buttons for expected answers"""
        try:
            position_file = "./templates/gabarito_demo_positions.json"
            
            if not os.path.exists(position_file):
                messagebox.showerror("Error", "Template not found. Please generate a template first.")
                return
            
            # Load position data
            with open(position_file, 'r') as f:
                self.grading_position_data = json.load(f)
            
            # Clear existing radio buttons
            for widget in self.expected_answers_frame.winfo_children():
                widget.destroy()
            self.expected_answer_vars = []
            
            # Create radio buttons for each question
            ttk.Label(self.expected_answers_frame, text="Question", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2)
            
            # Create choice headers
            choices = self.grading_position_data.get('choices', ['A', 'B', 'C', 'D', 'E'])
            for i, choice in enumerate(choices):
                ttk.Label(self.expected_answers_frame, text=choice, font=('Arial', 10, 'bold')).grid(row=0, column=i+1, padx=5, pady=2)
            
            # Create radio buttons for each question
            for q_data in self.grading_position_data['bubble_positions']:
                q_num = q_data['question']
                row = q_num
                
                ttk.Label(self.expected_answers_frame, text=f"Q{q_num:02d}").grid(row=row, column=0, padx=5, pady=2, sticky='w')
                
                # Create variable for this question
                var = tk.StringVar(value="")  # Start with no selection
                self.expected_answer_vars.append((q_num, var))
                
                # Create radio buttons for each choice
                for i, choice in enumerate(choices):
                    rb = ttk.Radiobutton(
                        self.expected_answers_frame, 
                        text="", 
                        variable=var, 
                        value=choice,
                        command=lambda q=q_num, c=choice: self.on_expected_answer_selected(q, c)
                    )
                    rb.grid(row=row, column=i+1, padx=5, pady=2)
            
            # Load current answers from text field if available
            self.apply_text_answers()
            
            self.grading_status.config(text="Template loaded. Set expected answers using radio buttons.")
            
        except Exception as e:
            self.grading_status.config(text="Error loading template")
            messagebox.showerror("Error", f"Failed to load template: {str(e)}")
    
    def on_expected_answer_selected(self, question, choice):
        """Called when an expected answer is selected"""
        self.grading_status.config(text=f"Q{question}: {choice} set as expected answer")
        self.update_answers_text_field()
    
    def update_answers_text_field(self):
        """Update the text field with current radio button selections"""
        answers = []
        for q_num, var in self.expected_answer_vars:
            answer = var.get()
            answers.append(answer if answer else "A")  # Default to "A" if not set
        
        self.answers_var.set(','.join(answers))
    
    def apply_text_answers(self):
        """Apply answers from text field to radio buttons"""
        if not hasattr(self, 'expected_answer_vars') or not self.expected_answer_vars:
            return
            
        answers_text = self.answers_var.get()
        if answers_text:
            answers = answers_text.split(',')
            for i, (q_num, var) in enumerate(self.expected_answer_vars):
                if i < len(answers):
                    var.set(answers[i].strip())
    
    def set_all_expected_answers(self, choice):
        """Set all expected answers to a specific choice"""
        if hasattr(self, 'expected_answer_vars'):
            for q_num, var in self.expected_answer_vars:
                var.set(choice)
            self.update_answers_text_field()
            self.grading_status.config(text=f"All expected answers set to {choice}")
    
    def clear_all_expected_answers(self):
        """Clear all expected answers"""
        if hasattr(self, 'expected_answer_vars'):
            for q_num, var in self.expected_answer_vars:
                var.set("")
            self.update_answers_text_field()
            self.grading_status.config(text="All expected answers cleared")
    
    def grade_sheet(self):
        """Grade the marked answer sheet"""
        try:
            self.grading_status.config(text="Grading sheet...")
            self.root.update()
            
            # Import grading functions
            from grade_it import grade_gabarito_improved, print_grade_report
            import json
            
            # Load position data
            position_file = "./templates/gabarito_demo_positions.json"
            with open(position_file, 'r') as f:
                position_data = json.load(f)
            
            # Parse expected answers
            expected_answers = self.answers_var.get().split(',')
            threshold = float(self.threshold_var.get())
            
            # Grade the sheet
            results = grade_gabarito_improved(
                image_path=self.marked_file_var.get(),
                expected_answers=expected_answers,
                position_data=position_data,
                threshold=threshold,
                debug=False  # We'll create our own visualization
            )
            
            # Display results
            self.display_results(results)
            
            # Create and display visualization
            self.create_visualization(results, position_data)
            
            self.grading_status.config(text="Grading completed")
            
        except Exception as e:
            self.grading_status.config(text="Error grading sheet")
            messagebox.showerror("Error", f"Failed to grade sheet: {str(e)}")
    
    def display_results(self, results):
        """Display grading results in the results tab"""
        self.results_text.delete(1.0, tk.END)
        
        # Basic report
        self.results_text.insert(tk.END, "=== GRADE REPORT ===\n")
        self.results_text.insert(tk.END, f"Score: {results['total_score']}/{results['max_score']}\n")
        self.results_text.insert(tk.END, f"Percentage: {results['percentage']:.1f}%\n")
        self.results_text.insert(tk.END, f"Multiple answers: {results['multiple_answers']}\n")
        self.results_text.insert(tk.END, f"Unanswered: {results['unanswered']}\n\n")
        
        # Detailed results
        self.results_text.insert(tk.END, "=== DETAILED RESULTS ===\n")
        for item in results['question_results']:
            status = "○" if item['is_correct'] else "X"
            if item['student_answer'] in ['MULTI', 'NONE']:
                status = "!"
            
            line = f"Q{item['question']:02d}: {status} Student={item['student_answer']:5} Correct={item['correct_answer']}"
            
            # Add bubble status for incorrect answers
            if not item['is_correct'] and item['student_answer'] not in ['MULTI', 'NONE']:
                marked_ratio = item['bubble_status'][item['student_answer']]
                correct_ratio = item['bubble_status'][item['correct_answer']]
                line += f" (marked: {marked_ratio:.2f}, correct: {correct_ratio:.2f})"
            
            self.results_text.insert(tk.END, line + "\n")
    
    def create_visualization(self, results, position_data):
        """Create a simple visualization of the grading results"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Load the marked image
            marked_img = Image.open(self.marked_file_var.get())
            draw = ImageDraw.Draw(marked_img)
            
            # Simple visualization: draw colored circles around bubbles
            for q_data in position_data['bubble_positions']:
                q_num = q_data['question']
                result = next((r for r in results['question_results'] if r['question'] == q_num), None)
                
                if result:
                    correct_answer = result['correct_answer']
                    student_answer = result['student_answer']
                    is_correct = result['is_correct']
                    
                    for bubble in q_data['bubbles']:
                        choice = bubble['choice']
                        cx, cy = bubble['center']
                        
                        # Determine circle color
                        if choice == correct_answer and choice == student_answer:
                            color = "green"  # Correct
                        elif choice == correct_answer:
                            color = "blue"   # Should have been marked
                        elif choice == student_answer and student_answer not in ['MULTI', 'NONE']:
                            color = "red"    # Wrong
                        elif result['bubble_status'].get(choice, 0) > 0.2:
                            color = "orange" # Multiple marks
                        else:
                            continue  # Don't draw for unmarked bubbles
                        
                        # Draw circle around bubble
                        draw.ellipse([cx-15, cy-15, cx+15, cy+15], outline=color, width=3)
            
            # Resize for display
            display_size = (400, 500)
            marked_img.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(marked_img)
            self.results_image_label.configure(image=photo)
            self.results_image_label.image = photo
            self.display_images.append(photo)
            
        except Exception as e:
            self.results_image_label.config(text=f"Error creating visualization: {str(e)}")
    
    def clear_results(self):
        """Clear the results text area and image"""
        self.results_text.delete(1.0, tk.END)
        self.results_image_label.config(text="Graded image will appear here")
        self.display_images.clear()
    
    def save_results(self):
        """Save results to a file"""
        filename = filedialog.asksaveasfilename(
            title="Save Results As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Results saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {str(e)}")

def main():
    # Check if templates directory exists
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    # Create main window
    root = tk.Tk()
    app = GradingSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()