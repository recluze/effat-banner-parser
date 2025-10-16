import sys

data_source = "conflicts-data/schedule.csv"


def read_csv(file_path):
    import csv
    records = []
    with open(file_path, newline='') as f:
        # read all lines 
        lines = f.read().splitlines()
        for line in lines:
            if not line.strip():
                continue
            student_id, course = line.split(",", 1)
            records.append((student_id.strip(), course.strip()))

    return records


def get_all_course_students(course_code, records):
    courses = {} 

    for student_id, course in records:
        course_compact = course.replace(" ", "")
        if course_compact not in courses: 
            students = [student_id]
            courses[course_compact] = students 
        else: 
            students = courses[course_compact]
            if student_id not in students: 
                students.append(student_id)

    return courses 


def get_course_conflicts(all_courses, course_code): 
    if course_code not in all_courses: 
        print(f"Error: Course code '{course_code}' not found in data source '{data_source}'", file=sys.stderr)
        sys.exit(1)

    target_students = set(all_courses[course_code])
    conflicts = {}
    for other_course, students in all_courses.items(): 
        if other_course == course_code: 
            continue 
        common_students = target_students.intersection(set(students))
        if common_students: 
            conflicts[other_course] = list(common_students)

    return conflicts

def print_conflicts(conflicts): 
    sorted_keys = sorted(conflicts.keys())

    # for course, students in conflicts[course].items(): 
    for course in sorted_keys:
        students = conflicts[course]
        print(f"{course:<12} {len(students):02d} | ", end = "")
        print("-" * len(students))

    print("-" * 20)
    print("Count:", len(conflicts))
    print("-" * 20)



def get_all_course_sections(course_code, records):
    # get list of all records in which course_code starts with the given course_code
    target_courses = set()
    for student_id, course in records:
        course_compact = course.replace(" ", "")
        if course_compact.startswith(course_code):
            target_courses.add(course_compact)

    return target_courses


def get_course_combined_conflicts(all_sections, all_courses):
    all_sections = sorted(all_sections)
    
    print("-" * 80)
    print("Sections: ", ", ".join(all_sections)) 
    print("-" * 80)

    all_conflicts = {}
    for course_code in all_sections:
        section_conflicts = get_course_conflicts(all_courses, course_code)  
        for conflict_course, students in section_conflicts.items():
            if conflict_course not in all_conflicts:
                all_conflicts[conflict_course] = set(students)
            else:
                existing_students = all_conflicts[conflict_course]
                all_conflicts[conflict_course] = existing_students.union(set(students))
        
    # convert students set to list 
    for course in all_conflicts:
        all_conflicts[course] = list(all_conflicts[course])

    print_conflicts(all_conflicts)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        prog = sys.argv[0] if sys.argv else "script"
        print(f"Usage: {prog} COURSE_CODE", file=sys.stderr)
        sys.exit(1)

    course_code = sys.argv[1].strip()
    if not course_code:
        print("Error: COURSE_CODE must not be empty", file=sys.stderr)
        sys.exit(1)

    
    # optional: type (section or course)
    type = sys.argv[2] if len(sys.argv) >= 3 else "section"

    # need records and all courses anyway 
    records = read_csv(data_source) 
    courses = get_all_course_students(course_code, records)

    if type == "section":
        conflicts = get_course_conflicts(courses, course_code)
        print_conflicts(conflicts)

    elif type == "course":
        # go through the records and find all courses that share students with the given course_code
        all_sections = get_all_course_sections(course_code, records)
        course_conflicts = get_course_combined_conflicts(all_sections, courses) 
        