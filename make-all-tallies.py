import os 
import logging 
import sys 
import glob 
from shutil import copyfile
from openpyxl import load_workbook

output_file = "all-suggested-courses.csv"
transcript_dir = "plain"
max_suggested_courses = 6
courses_after_which_senior_1 = 30  

# set logging level to info 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# disable logging 
logging.disable(logging.CRITICAL)


# plan file wrting 
student_csv_file = "students.csv"
plan_file_template = "4-year-plan-template.xlsx"
plan_output_dir = "plans"
plan_sheet_taken_id = 1 
plan_sheet_main_id = 0 
plan_taken_range = ['A', '4']
plan_taking_range = ['F', '4']
plan_suggested_range = ['Q', '5']

study_plan = [
    # Semester 1
    {'CS 1001': []}, 
    {'GMTH 181E': []}, 
    {'GCS 182': []}, 
    {'English 1': []}, 
    {'GISL 121': []}, 
    {'Social 1': []}, 
    # Semester 2
    {'CS 2132': ['GCS 182']}, 
    {'MATH 101': ['GMTH 181E']}, 
    {'English 2': ['GENG 131']},
    {'CS 1021': ['CS 1001']}, 
    {'GSTA 181': []}, 
    {'GARB 131': []}, 
    # Semester 3
    {'CS 2071': ['GCS 182']}, 
    {'CS 2011': ['CS 2132']},
    {'GETH 121': []}, 
    {'MATH 201': ['MATH 101']}, 
    {'CS 2091': ['CS 1021']},
    {'Foreign 1': []},
    {'GPHY 171': []}, 
    # Semester 4
    {'CS 2111': ['CS 2071']}, 
    {'CS 3151': ['CS 2011']}, 
    {'CS 3081': ['GSTA 181', 'CS 2011']}, 
    {'STAT 201': ['GSTA 181', 'MATH 201']}, 
    {'CS 3067': ['CS 1001']}, 
    {'GSEM 100': []}, 
    {'Foreign 2': []}, 
    # Semester 5
    {'Science 1': []}, 
    {'MATH 203': ['MATH 201']}, 
    {'CS 3012': ['CS 2011']}, 
    {'CS 3101': ['CS 1021', 'CS 2011']}, 
    {'Tech 1': []}, 
    {'GSEM 201': ['GSEM 100']},
    # Semester 6
    {'Creative 1': []}, 
    {'MATH 307': ['MATH 201']}, 
    {'CS 3072': ['CS2071']}, 
    {'CS 4176': ['CS 3151']}, 
    {'Tech 2': []}, 
    {'Tech 3': []}, 
    # Semester 8
    {'CS 4177': ['CS 4176']},
    {'CS 4121': ['CS 3101']}, 
    {'MATH 310': ['MATH 201', 'CS2132']}, 
    {'CS 3133': ['CS 2132']}, 
    {'Tech 4': []}, 
    {'Tech 5': []}, 
]


category_courses_categories = [
    'Social 1', 'Social 2',
    'English 1', 'English 2',
    'Foreign 1', 'Foreign 2',
    'Creative 1', 
    'Science 1', 
    'Tech 1', 'Tech 2', 'Tech 3', 'Tech 4', 'Tech 5',
]
category_courses_codes = {
    'Social': ['GLAW','GPSY', 'GDIP','GANT','GJMC','GHIS','GARC','GECO','GPHL','GMED','GCIV','GENV','GCUL','GGLO','GENT','GGLO','GSUS'], # only codes for these need to be checked 
    'Foreign': ['GFRN', 'GGER', 'GITA', 'GSPA'],
    'Creative': ['GDRA', 'GDRW', 'GFIL', 'GMUS', 'GART', 'GPHO', 'GLIT', 'GISL'], # need to remove GISL 121 before checking this 
    'Science': ['BIO', 'CHEM'],
    'Tech': ['CS 3069', 'CS 4064', 'CS 4065'  
             'CS 4082', 'CS 4083', 'CS 4084', 'CS 4073', 'CS 4086', 
            ], # Need to check these specifically with code TODO: Fix 
} 
# when checking "Social 2" for example, 2 of these need to have been taken 





def get_all_courses_from_plan(): 
    # get all courses from the study plan in order 
    all_courses = []
    for semester in study_plan:
        for course in semester.keys():
            all_courses.append(course)
    return all_courses



def load_ids_from_file(ids_file):
    with open(ids_file, 'r') as f:
        ids = [line.strip() for line in f if line.strip()]
    return ids

def add_output_header(out_file):
    with open(out_file, 'w') as f:
        header = "Student ID," 
        courses = get_all_courses_from_plan()
        header += ",".join(courses) + "\n"
        f.write(header)

def output_student_to_file(student_id, suggested_courses):
    with open(output_file, 'a') as f:
        line = student_id + ","
        all_courses = get_all_courses_from_plan()
        course_flags = []
        for course in all_courses:
            if course in suggested_courses:
                course_flags.append("1")
            else:
                course_flags.append("0")
        line += ",".join(course_flags) + "\n"
        f.write(line)
        

def get_all_suggested_courses(ids):
    # add header to the output file 
    add_output_header(output_file)


    for student_id in ids:
        
        logging.info(f"Processing student ID: {student_id}")
        try: 
            taken_courses, taking_courses = get_student_taken_courses(student_id)
            # merge the two lists for sending to the suggestion function
            all_taken_courses = list(set(taken_courses) | set(taking_courses))
            logging.info(f"Taken courses for student {student_id}: {all_taken_courses}")  

            # get suggested courses
            suggested_courses = get_student_suggested_courses(student_id, all_taken_courses) 

            # write to output file 
            output_student_to_file(student_id, suggested_courses) 

            # write to study plan file 
            populate_plan_file(student_id, taken_courses, taking_courses, suggested_courses)

            print("===================================")
            print(student_id)
            for course in suggested_courses:
                print(course)
            
                
        except FileNotFoundError as e:
            logging.error(e)    
            continue 



def get_student_taken_courses(student_id):
    # files in the transcript_dir that start with first-last-id.txt. Get the filename using student_id and glob 
    glob_pattern = os.path.join(transcript_dir, f"*{student_id}*.txt")
    student_file  = glob.glob(glob_pattern)   

    if not student_file:
        logging.error(f"No transcript file found for student ID: {student_id}")
        raise FileNotFoundError(f"No transcript file found for student ID: {student_id}")
    
    student_file = student_file[0]
    logging.info(f"Found transcript file: {student_file}")

    # read the file and get the taken courses
    taken_courses = []
    taking_courses = []

    with open(student_file, 'r') as f:
        collecting_taken = False 
        collecting_taking = False

        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):  # ignore empty lines and comments
                # print(line)
                # start collecting lines that start with '------------ Courses Already Taken ------------------'
                if line.startswith("------------ Courses Already Taken ------------------"):
                    collecting_taken = True
                    continue
                elif line.startswith("----------- Courses Currently Taking ----------------"):
                    collecting_taken = False
                    collecting_taking = True
                    continue
                elif line.startswith("------------ Can Take ------------------"):
                    # we're done 
                    break 
        
                elif line.startswith("Total") or \
                    line.strip().endswith("(F)"):
                    continue # skip   
                
                if collecting_taken:
                    taken_courses.append(line)
                elif collecting_taking:
                    taking_courses.append(line)

    return taken_courses, taking_courses 

def get_student_suggested_courses(student_id, taken_courses):
    suggested_courses = []

    # TODO: Check Ethics GETH 121. If osmething, then somethign 

    # Check the number of courses. If up to X and not already taken, add Senior 1 
    if len(taken_courses) >= courses_after_which_senior_1 and 'CS 4176' not in taken_courses:
        suggested_courses.append('CS 4176')

    # Check if Senior 1 is taken. If so, add Senior 2 automatically 
    if 'CS 4176' in taken_courses and 'CS 4177' not in taken_courses:
        suggested_courses.append('CS 4177')

    # loop through all courses in plan. See if the course is already in taken_courses. If so, skip it. 
    for check_course_meta in study_plan: 
        check_course = list(check_course_meta.keys())[0]
        logging.info(f"Checking course {check_course}")

        # skip already taken courses 
        if check_course in taken_courses:
            logging.info(f"Course {check_course} already taken. Skipping.")
            continue

        # Check "cateogory courses" like Social 1, Tech 1, Foreign 1, Creative 1
        if check_course in category_courses_categories:
            # now decide whether to add it or not 
            if should_add_social_category(check_course, taken_courses):
                logging.info(f"Suggesting category course {check_course} for student {student_id}")
                suggested_courses.append(check_course)
                if len(suggested_courses) >= max_suggested_courses:
                    break
            continue


        # check if prerequisites are met
        prerequisites = check_course_meta[check_course]
        if all(prereq in taken_courses for prereq in prerequisites):
            logging.info(f"Suggesting course {check_course} for student {student_id}")

            suggested_courses.append(check_course)        
            if len(suggested_courses) >= max_suggested_courses:
                break
            continue 

    logging.info(f"Suggested courses for student {student_id}: {suggested_courses}")

    return suggested_courses

def should_add_social_category(check_course, taken_courses): 
    # get category from check_course 
    category = check_course.rsplit(' ', 1)[0]  # get the part before the last space
    logging.info(f"Category identified: {category}")

    category_count = check_course.rsplit(' ', 1)[1]  # get the number after the last space
    logging.info(f"Category count identified: {category_count}")

    # first check technical courses cateogy 'Tech'
    if category == 'Tech':
        # count the intersection of taken_courses and category_courses_codes['Tech'] using sets 
        taken_tech_courses = set(taken_courses).intersection(set(category_courses_codes['Tech']))
        logging.info(f"Taken tech courses: {taken_tech_courses}")
        if len(taken_tech_courses) < int(category_count):
            return True 
        else:
            return False
        
    # for English 1 and English 2, just check GENG 131 and GENG 132/133 
    if category == 'English':
        if category_count == '1':
            # if GENG 131 is taken, don't add. If GENG 132 or GENG 133 is taken, don't add this either becasue it's exempted 
            if 'GENG 131' in taken_courses or 'GENG 132' in taken_courses or 'GENG 133' in taken_courses:
                return False 
            else:
                return True 
        elif category_count == '2':
            if 'GENG 132' in taken_courses or 'GENG 133' in taken_courses:
                return False 
            else:
                return True


    # for other categories, check the codes
    if category in category_courses_codes:
        codes = category_courses_codes[category]
        logging.info(f"Codes for category {category}: {codes}")

        # count how many courses in taken_courses start with any of the codes 
        count = 0
        for course in taken_courses:
            for code in codes:
                if course.startswith(code):
                    # special case: if category is Creative, exclude GISL 121
                    if category == 'Creative' and course == 'GISL 121':
                        continue
                    count += 1
                    break  # no need to check other codes for this course

        logging.info(f"Count of taken courses in category {category}: {count}")
        if count < int(category_count):
            return True 
        else:
            return False

    # by default, don't add 
    return False 



def get_student_names(student_id):
    # get student first_name and last_name from the student_csv_file 
    with open(student_csv_file, 'r') as f:
        # loop over all lines and if first_column is student_id, get second and thord column as first_name and last_name
        first_name = None
        last_name = None
        for line in f:
            columns = line.strip().split(',')
            if columns[0] == student_id:
                first_name = columns[1]
                last_name = columns[2]
                break
    return first_name, last_name

def populate_plan_file(student_id, taken_courses, taking_courses, suggested_courses): 
    # make plan output dir if not exists
    if not os.path.exists(plan_output_dir):
        os.makedirs(plan_output_dir)

    first_name, last_name = get_student_names(student_id)
    
    # copy plan file template to output dir with name first-last-id.xlsx
    output_file_name = f"{first_name}-{last_name}-{student_id}.xlsx"
    output_file_path = os.path.join(plan_output_dir, output_file_name)
    
    copyfile(plan_file_template, output_file_path) 

    # open the output file with openpyxl
    
    wb = load_workbook(output_file_path)    
    ws_taken = wb.worksheets[plan_sheet_taken_id]
    ws_main = wb.worksheets[plan_sheet_main_id]

    # populate taken courses
    for i, course in enumerate(taken_courses):      
        cell =  f"{plan_taken_range[0]}{int(plan_taken_range[1]) + i}"
        ws_taken[cell] = course
    
    # populate taking courses
    for i, course in enumerate(taking_courses):
        cell =  f"{plan_taking_range[0]}{int(plan_taking_range[1]) + i}"
        ws_taken[cell] = course

    # populate suggested courses
    for i, course in enumerate(suggested_courses):
        cell =  f"{plan_suggested_range[0]}{int(plan_suggested_range[1]) + i}"
        ws_main[cell] = course
    
    # save the workbook
    wb.save(output_file_path)
    wb.close()
    logging.info(f"Populated plan file saved to {output_file_path}")

if __name__ == "__main__":
    # get ids file from arguments 
    if len(sys.argv) != 2:
        print("Usage: python make-all-tallies.py <ids_file>")
        sys.exit(1)
    ids_file = sys.argv[1]  
    # load ids from the file 
    ids = load_ids_from_file(ids_file)

    get_all_suggested_courses(ids)
