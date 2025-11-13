import json
from PIL import Image, ImageDraw
import os

def create_marked_sheet_from_answers(answers, template_path, position_data, output_path):
    """
    Create a marked sheet from a dictionary of answers
    """
    try:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        marked_count = 0
        for q_data in position_data['bubble_positions']:
            q_num = q_data['question']
            if q_num in answers and answers[q_num]:
                answer = answers[q_num]
                for bubble in q_data['bubbles']:
                    if bubble['choice'] == answer:
                        cx, cy = bubble['center']
                        # Fill the bubble
                        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill="black")
                        marked_count += 1
                        break
        
        img.save(output_path)
        print(f"Created marked sheet: {output_path}")
        print(f"Marked {marked_count} questions")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error creating marked sheet: {e}")

def create_marked_demo_sheet():
    """
    Create a marked answer sheet by asking for each question's answer
    """
    print("=== Answer Sheet Marker ===")
    print("This will create a marked answer sheet for grading demonstration.")
    print()
    
    template_name = "./templates/gabarito_demo.png"
    position_file = "./templates/gabarito_demo_positions.json"
    
    try:
        num_questions = int(input("Enter number of questions (default 20): ") or "20")
    except ValueError:
        num_questions = 20
        print(f"Using default: {num_questions} questions")
    
    if not os.path.exists(template_name):
        print(f"\nError: Template file '{template_name}' not found!")
        print("Please generate the template first.")
        return None
    
    if not os.path.exists(position_file):
        print(f"\nError: Position file '{position_file}' not found!")
        print("Please generate the template first.")
        return None
    
    try:
        with open(position_file, 'r') as f:
            position_data = json.load(f)
    except Exception as e:
        print(f"Error loading position data: {e}")
        return None
    
    print(f"\nEnter answers for {num_questions} questions:")
    print("Options: A, B, C, D, E (or leave blank for unanswered)")
    print()
    
    user_answers = {}
    for q in range(1, num_questions + 1):
        while True:
            answer = input(f"Q{q:02d}: ").upper().strip()
            if answer == "":
                user_answers[q] = None
                break
            elif answer in ['A', 'B', 'C', 'D', 'E']:
                user_answers[q] = answer
                break
            else:
                print("Invalid answer! Please enter A, B, C, D, E or leave blank.")
    
    try:
        output_name = "my_marked_sheet.png"
        create_marked_sheet_from_answers(user_answers, template_name, position_data, output_name)
        
        print(f"\nSuccessfully created marked sheet: {output_name}")
        
        return output_name, user_answers
        
    except Exception as e:
        print(f"Error creating marked sheet: {e}")
        return None

def quick_demo():
    """
    Quick demo with predefined answers
    """
    print("=== Quick Demo Mode ===")
    
    template_name = "./templates/gabarito_demo.png"
    position_file = "./templates/gabarito_demo_positions.json"
    
    # Predefined answers for a quick test
    demo_answers = {
        1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
        6: "A", 7: "B", 8: "C", 9: "D", 10: "E",
        11: "A", 12: "B", 13: "C", 14: "D", 15: "E", 
        16: "A", 17: "B", 18: "C", 19: "D", 20: "E"
    }
    
    if not os.path.exists(template_name) or not os.path.exists(position_file):
        print("Please generate the template first!")
        return None
    
    try:
        with open(position_file, 'r') as f:
            position_data = json.load(f)
        
        output_name = "./templates/marked_demo.png"
        create_marked_sheet_from_answers(demo_answers, template_name, position_data, output_name)
        
        print(f"Created quick demo: {output_name}")
        return output_name, demo_answers
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("This module is primarily for use with the GUI.")
    print("For command line use, run the individual scripts.")