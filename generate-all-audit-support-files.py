import csv
import subprocess
import os
import shutil

# Paths
csv_file = "students.csv"
script_file = "get-audit-courses.py"
base_folder = "audit-support-files"

# Handle folder rollover
if os.path.exists(base_folder):
    i = 1
    while True:
        new_name = f"{base_folder}_{i:04d}"
        if not os.path.exists(new_name):
            shutil.move(base_folder, new_name)
            print(f"Existing folder renamed to {new_name}")
            break
        i += 1

os.makedirs(base_folder, exist_ok=True)

# Read CSV and run script for each student
with open(csv_file, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        student_id = row["Student ID"].strip()
        first_name = row["First Name"].strip()
        last_name = row["Last Name"].strip()
        
        output_file = os.path.join(base_folder, f"{first_name}-{last_name}-{student_id}.txt")
        
        result = subprocess.run(
            ["python3", script_file, student_id],
            capture_output=True,
            text=True
        )
        
        with open(output_file, "w") as out_f:
            out_f.write(result.stdout)
        
        print(f"Wrote output for {student_id} to {output_file}")
