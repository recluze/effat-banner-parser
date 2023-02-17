import os 
import logging 
import re 
import sys
import pprint
pp = pprint.PrettyPrinter(depth=4)


output_dir = "output"
course_list_file = "courses.txt"
output_plain = False 

id_list = set() 
id_name_map = {} 
id_courses_map = {} 
course_list = [] 

def get_plan_formatted_course_name(course_name): 
    course_type, course_num, course_name = separate_number_chars(course_name) 
    return course_type + " " + course_num

def separate_number_chars(s):
    regex = r"([A-Z]+)(\d+[A-Z]?):(.*)"
    match = re.search(regex, s) 
    
    if match != None: 
        course_type = match.group(1)
        course_num = match.group(2)
        course_name = match.group(3)
        return [course_type, course_num, course_name]
    else: 
        print("Bad course name:", s)
        sys.exit(1)


def get_course_list(): 
    with open(course_list_file, 'r') as f: 
        for line in f: 
            if line.strip() != "": 
                course_list.append(line.strip())
    
    course_list.sort() 

def get_unique_student_ids(lines): 
    for l in lines: 
        id_list.add(l[0]) 

    for l in lines: 
        id_name_map[l[0]] = l[1]

def make_id_course_map(lines): 
    for l in lines: 

        student_id = l[0]

        course_type = l[2]
        course_code = l[3]
        if l[4] == 'Effat University Campus': 
            course_name = l[6]
            course_grade = l[7]
        else: 
            course_name = l[4]
            course_grade = l[5]

        # if course_type[0] == 'G': 
        #     course_type = course_type[0] + " " + course_type[1:]

        course_full_name_formatted = course_type.ljust(5)
        course_full_name_formatted += course_code.ljust(6)
        course_full_name_formatted += course_name.ljust(33)
        course_full_name = course_type + course_code + ": " + course_name
        
        course_data = [course_full_name, course_grade, course_full_name_formatted]
        if student_id not in id_courses_map: 
            id_courses_map[student_id] = [course_data]
        else: 
            id_courses_map[student_id].append(course_data) 

    # sort the student courses 
    for student_id, course_list in id_courses_map.items(): 
        course_list.sort() 

    # pp.pprint(id_courses_map)
# ------------

def single_student_courses(student_id): 
    try: 
        student_courses = id_courses_map[student_id]
        student_course_names = [x[0] for x in student_courses]
    except KeyError: 
        print("Unable to find any student course. Transcript might be empty.")
        sys.exit(1)

    # print(student_courses)

    print()
    print("-----------------------------------------------------\n")
    print("Details for: ", student_id, " - ", id_name_map[student_id])
    
    print()

    # first output courses already taken 
    count = 0
    print("------------ Courses Already Taken ------------------\n")
    for sc in student_courses: 
        course_name = sc[0]
        course_grade = sc[1]
        course_fullname = sc[2]

        if course_grade == 'F': 
            course_grade = 'F  <---'
        if course_grade != 'None': 
            if output_plain: 
                print(get_plan_formatted_course_name(course_name))
            else: 
                print(course_fullname, course_grade)
            count += 1
    print ("\nTotal: " + str(count) + "\n")

    count = 0
    print("----------- Courses Currently Taking ----------------\n")
    # for c in course_list: 
    for sc in student_courses: 
        course_name = sc[0]
        course_grade = sc[1]
        course_fullname = sc[2]

        if course_grade == 'None': 
            if output_plain: 
                print(get_plan_formatted_course_name(course_name))
            else:
                print(course_fullname)
            count += 1
    print ("\nTotal: " + str(count) + "\n")

    print("------------ Courses Not Yet Taken ------------------\n")
    for c in course_list: 
        already_taken = False 
        for sc in student_course_names: 
            code_part_sc = sc[:sc.index(':')]
            code_part_c = c[:c.index(':')]
            if code_part_sc == code_part_c: 
                already_taken = True 
                break 

        if not already_taken: 
            # print(c)
            course_type, course_code, course_name = separate_number_chars(c)
            course_full_name_formatted = course_type.ljust(5)
            course_full_name_formatted += course_code.ljust(6)
            course_full_name_formatted += course_name.ljust(33)
            print(course_full_name_formatted)

def student_courses():
    with open(os.path.join(output_dir, "tallies.csv"), 'w') as f: 
        out_line = "Student ID, Student Name,"
        for c in course_list: 
            out_line += c + ","
        out_line = out_line.rstrip(",")
        print(out_line)
        f.write(out_line + "\n")

        for s in id_list: 
            out_line = ""
            out_line += s + "," + id_name_map[s] + ","

            for c in course_list: 
                student_courses = id_courses_map[s]
                student_course_names = [x[0] for x in student_courses]
        
                if c in student_course_names: 
                    out_line += "0,"
                else: 
                    out_line += "1,"
            out_line = out_line.rstrip(",")
            print(out_line)
            f.write(out_line + "\n")


def create_tallies(infile, student_id): 
    with open(infile, "r") as f: 
        lines = f.readlines() 

    lines = [line.split(',') for line in lines]
    
    get_unique_student_ids(lines) 
    make_id_course_map(lines) 
    get_course_list() 
    single_student_courses(student_id) 
    print() 
    
if __name__ == "__main__": 
    student_id = sys.argv[1]

    try: 
        output_plain = sys.argv[2] == 'plain'
    except IndexError: 
        pass 

    infile = os.path.join(output_dir, "combined.csv")
    create_tallies(infile, student_id)     
