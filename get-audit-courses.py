import sys
import subprocess

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <ID>")
    sys.exit(1)

student_id = sys.argv[1]

with open("audit-courses.txt") as f:
    courses = [line.strip() for line in f if line.strip()]

# Run create-tallies.py once for this student
result = subprocess.run(
    ["python3", "create-tallies.py", student_id],
    capture_output=True,
    text=True
)
all_lines = result.stdout.strip().splitlines()
print("\n".join(all_lines))
print()
print ("=" * 70)
print ("Audit File Details for Student ID:", student_id)
print ("=" * 70)

for course in courses:
    # make separators for section 
    if course.startswith("[SEP"):
        output = "\n\n" + '-' * 48 + " " + course + "\n\n" 
        print(output)
        continue
    if course.strip() == "":
        continue


    parts = course.split()
    if len(parts) != 2:
        print(f"{course}: invalid format (expected 'CODE NUMBER')")
        exit(1)

    prefix, number = parts
    # Filter lines containing both prefix and number
    lines = [line for line in all_lines if prefix in line and number in line]
    


    if lines:
        mark_multiple = len(lines) > 1
        for line in lines:
            if any(term in line for term in ("Spring", "Fall", "Summer")):
                # make semester easier to copy by double clicking 
                line = line.replace("Spring ", "Spring\xa0")
                line = line.replace("Fall ", "Fall\xa0")
                line = line.replace("Summer ", "Summer\xa0")
                output = line 

            else:
                output = f"{line}  (cur)"
            if mark_multiple:
                output += " *"
            print(output)
    else:
        print(f"{course}: ---")

