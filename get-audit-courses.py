import sys
import subprocess

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <ID>")
    sys.exit(1)

student_id = sys.argv[1]

with open("audit-courses.txt") as f:
    courses = [line.strip() for line in f if line.strip()]

for course in courses:
    parts = course.split()
    if len(parts) != 2:
        print(f"{course}: invalid format (expected 'CODE NUMBER')")
        continue

    prefix, number = parts
    cmd = f"python3 create-tallies.py {student_id} | grep {prefix} | grep {number}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()

    if lines:
        mark_multiple = len(lines) > 1
        for line in lines:
            if any(term in line for term in ("Spring", "Fall", "Summer")):
                output = line
            else:
                output = f"{line}  (cur)"
            if mark_multiple:
                output += " *"
            print(output)
    else:
        print(f"{course}: ---")
