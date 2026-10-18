# grade_manager.py

# Our chosen data structure: a list that will hold student dictionaries
students = []

def calculate_grade(mark):
    """Takes a numeric mark and returns the corresponding letter grade."""
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "E"

def add_student(student_list):
    """Prompts for a valid student name and mark, calculates the grade, and saves it."""
    
    # 1. Validate the Name
    while True:
        # .strip() removes accidental spaces at the beginning or end
        name = input("\nEnter student name: ").strip()
        if len(name) > 0:
            break  # Valid name! Exit the loop.
        print("Invalid input: Name cannot be empty. Please try again.")

    # 2. Validate the Mark
    while True:
        mark_input = input(f"Enter mark for {name} (0-100): ").strip()
        try:
            # Try converting the text into a number (float allows decimals like 85.5)
            mark = float(mark_input)
            
            # Check if the number is within the valid 0-100 range
            if 0 <= mark <= 100:
                break  # Valid mark! Exit the loop.
            else:
                print("Invalid range: Mark must be between 0 and 100.")
        except ValueError:
            # If float() fails because they typed letters, Python jumps here instead of crashing
            print("Invalid input: Please enter a valid number (e.g., 85 or 92.5).")

    # 3. Calculate Grade and Store in our Data Structure
    grade = calculate_grade(mark)
    
    student_record = {
        "name": name,
        "mark": mark,
        "grade": grade
    }
    student_list.append(student_record)
    print(f"Added {name} with mark {mark} (Grade: {grade}).")


# --- Quick Test for Step 2 (We will remove this later) ---
add_student(students)
print("Current database:", students)