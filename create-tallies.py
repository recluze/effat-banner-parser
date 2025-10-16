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


# we skip these in output 
foundation_course_codes = ['EEW', 'EER', 'EELS', 'EECL', 'EEOE']

exemption_rules = {
    'GENG 131': ['EEW 015', 'EER 025', 'EELS 035', 'EECL 045', 'EEOE 094']
}

def calculate_exempted_courses(lines, student): 
    print("----------- Courses Exempted ------------------------\n")
    for item in exemption_rules.items():
        exempted = item[0]
        to_take = item[1] 
        # print("Checking exemption: " + exempted)

        courses_taken = [] 
        for l in lines: 
            if l[0] != student: continue 

            this_course = l[2] + ' ' + l[3]
            courses_taken.append(this_course)
        
        courses_left = [c for c in to_take if c not in courses_taken]
        if not courses_left: 
            print("Course exempted: " + exempted)


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

        # ignore foundation courses from final output 
        if course_type in foundation_course_codes: 
            continue

        if l[4] == 'Effat University Campus': 
            course_name = l[6]
            course_grade = l[7]
            
        else: 
            course_name = l[4]
            course_grade = l[5]

        term_name = l[-1]

        # if course_type[0] == 'G': 
        #     course_type = course_type[0] + " " + course_type[1:]

        course_full_name_formatted = course_type.ljust(5)
        course_full_name_formatted += course_code.ljust(6)
        course_full_name_formatted += course_name.ljust(33)
        course_full_name = course_type + course_code + ": " + course_name
        
        course_data = [course_full_name, course_grade, course_full_name_formatted, term_name]
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
        course_term_name = sc[-1].strip()

        suffix = ''
        if course_grade == 'F': 
            course_grade = 'F  <---'
            suffix = ' (F)'

        if course_grade != 'None': 
            if output_plain: 
                print(get_plan_formatted_course_name(course_name)  + suffix)
            else: 
                print(course_fullname, course_grade.ljust(4), course_term_name)
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

    print("------------ Can Take ------------------\n")
    # for c in course_list: 
    #     already_taken = False 
    #     for sc in student_course_names: 
    #         code_part_sc = sc[:sc.index(':')]
    #         code_part_c = c[:c.index(':')]
    #         if code_part_sc == code_part_c: 
    #             already_taken = True 
    #             break 

    #     if not already_taken: 
    #         # print(c)
    #         course_type, course_code, course_name = separate_number_chars(c)
    #         course_full_name_formatted = course_type.ljust(5)
    #         course_full_name_formatted += course_code.ljust(6)
    #         course_full_name_formatted += course_name.ljust(33)
    #         print(course_full_name_formatted)
    get_can_take_courses(student_courses)


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
    calculate_exempted_courses(lines, student_id) 
    print() 
    

def remove_letter_from_course_number(course_num): 
    regex = r"([A-Z]*\s\d+)[A-Z]?"
    match = re.search(regex, course_num) 
    if match != None: 
        return match.group(1)
    else: 
        print("Bad course number:", course_num)
        sys.exit(1)

def get_can_take_courses(student_courses): 
    try: 
        output_suggested = sys.argv[2] == 'suggest'
        suggest_for_future_sem = sys.argv[2] == 'suggest-for-future-sem'
    except IndexError: 
        print('Use suggest or suggest-for-future-sem to get suggestions')
        return 
    
    if not suggest_for_future_sem and not output_suggested:
        print('Use suggest or suggest-for-future-sem to get suggestions')
        return 


    print("Core Courses: \n")
    prereqs_core = {
        'CS 3121': ['GCS 182'], 
        'MATH 101': ['GMTH 181E'], 
        'GENG 132': ['GENG 131'],
        'CS 1021': ['CS 1001'],
        'CS 2071': ['GCS 182'],
        'CS 2011': ['CS 2132'],
        'MATH 201': ['MATH 101'],
        'CS 1021': ['CS 1021'], 
        'CS 2111': ['CS 2071'], 
        'CS 3151': ['CS 2011'],
        'CS 3081': ['GSTA 181', 'CS 2011'], 
        'STAT 201': ['GSTA 181', 'MATH 201'], 
        'CS 3067': ['CS 1001'], 
        'MATH 203': ['MATH 201'],
        'CS 3101': ['CS 1021', 'CS 2011'],
        'GSEM 201': ['GSEM 100'],
        'MATH 307': ['MATH 201'], 
        'CS 3072': ['CS 2071'], 
        'CS 4176': ['CS 3151'], 
        'CS 4177': ['CS 4176'],
        'CS 4121': ['CS 3101'], 
        'MATH 310': ['MATH 201', 'CS 2132'], 
        'CS 3133': ['CS 2132']
    }

    # for use later in the function 
    course_types = {
        'AI Electives': [['CS 4082', 'CS 4083'], 5], 

        'CyberSec Electives': [['CS 3154', 'CS 4065', 'CS 4064', 'CS 3061'], 5],

        'Foreign1':  [['GFRN 141', 'GGER 141', 'GFRN 142', 'GGER 142', 'GFRN 181', 'GFRN 182'], 2], 

        'Social1': [['GLAW 151','GPSY 151','GPSY 152','GDIP 151','GANT 151','GJMC 151','GHIS 151','GARC 151','GECO 151','GPHL 151','GMED 151','GCIV 151','GCIV 161','GENV 162','GCUL 161','GGLO 161','GENT 161','GGLO 162','GSUS 161'], 2], 
    
        'Creative': [['GDRA 111', 'GDRW 111', 'GFIL 111', 'GMUS 111', 'GART 111', 'GPHO 111', 'GLIT 111', 'GLIT 112', 'GLIT 113', 'GLIT 114','GISL 121', 'GISL 122',  'GISL 123', 'GISL 124', 'GISL 125'], 1], 

        'No Prereq Courses': [['CS 1001', 'GMTH 181', 'GCS 182', 'GENG 131', 'GISL 121', 
                              'GSTA 181', 'GARB 131', 
                              'GETH 121', 'GPHY 171', 
                              'GSEM 100'], 10]
        }


    courses_taken = []
    courses_currently_taking = []

    for sc in student_courses:
        course_name = sc[0]
        course_grade = sc[1]
        course_fullname = sc[2]
        course_code = get_plan_formatted_course_name(course_name)

        if course_grade != 'None': 
            courses_taken.append(course_code)
        else: 
            courses_currently_taking.append(course_code)    

    # print("Courses Taken: ", courses_taken)
    # update courses_taken to remove letter from after the course number if any 
    courses_taken = [remove_letter_from_course_number(c) for c in courses_taken]
    courses_currently_taking = [remove_letter_from_course_number(c) for c in courses_currently_taking]
    
    collected_courses = [] 
    for sc in student_courses:
        course_taken = get_plan_formatted_course_name(sc[0])
        
        for course, reqs in prereqs_core.items():
            # If we are in mid of semester, assume current courses will be cleared
            if not suggest_for_future_sem and course_taken in courses_currently_taking:
                continue; 

            # If we are at beginning of semester, current courses are taken already 
            # but not yet cleared. Don't need to suggest them. 
            # Also, can't suggest a course whose prereq is being taken currently.
            if course_taken in reqs and \
                course not in courses_taken and \
                course not in courses_currently_taking:
                collected_courses.append([course, reqs]) 

    for cc in collected_courses:
        # ensure all prereqs are taken 
        prereqs = cc[1]
        can_take = False  
        for p in prereqs:
            if (p in courses_taken) or (suggest_for_future_sem and p in courses_currently_taking): 
                can_take = True 
            else: 
                can_take = False # need this to handle multiple prereqs
                break # a single missed prereq is enough to not suggest the course
                    
        if can_take:
            print(cc[0] + "  (Prereqs:" + ', '.join(prereqs) + ")")

    print("-" * 10 + "\n")
    # -------- Now suggest elective courses not yet taken
    # course_types defined above. 

    # for these, doesn't matter if currently taking or cleared already 
    for course_type, course_type_courses_meta in course_types.items(): 
        course_type_courses = course_type_courses_meta[0]
        required_count = course_type_courses_meta[1]

        print()  
        course_type_count = 0 
        for sug in course_type_courses:
            if sug in courses_taken or sug in courses_currently_taking:
                course_type_count += 1
                
        # if sufficient number of courses not taken, suggest all not yet taken
        course_type_suggested = [] 
        if course_type_count < required_count:
            for sug in course_type_courses: 
                if sug not in courses_taken and sug not in courses_currently_taking:
                    course_type_suggested.append(sug)
            print(course_type + " Courses: " + \
                  " ["+ str(required_count - course_type_count) +"]", \
                      course_type_suggested)
        else: 
            print(course_type + " Courses: Sufficient courses taken already.")

if __name__ == "__main__": 
    student_id = sys.argv[1]

    try: 
        output_plain = sys.argv[2] == 'plain'
    except IndexError: 
        pass 

    infile = os.path.join(output_dir, "combined.csv")
    create_tallies(infile, student_id)   

 



# python create-tallies.py  `cat ids-nauman.txt | head -n 20 | tail  -n 1 `  plain
