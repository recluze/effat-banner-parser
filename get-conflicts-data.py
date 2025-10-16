import requests 
import os 
import sys
import time
from lxml import html

import importlib.util
spec = importlib.util.spec_from_file_location("banner_transcript", "./banner-transcript.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
banner_transcript = bt

from urllib3.exceptions import InsecureRequestWarning


output_dir = "conflicts-data"
logging = bt.logging
term_identifier = bt.term_identifier 

url_term_selection = bt.url_prefix + "/ssbprod/bwlkfstu.P_FacStuSchd"
url_student_selection = bt.url_prefix + "/ssbprod/bwlkoids.P_FacVerifyID"
url_sched_show = bt.url_prefix + "/ssbprod/bwlkfstu.P_FacStuSchd" 



def get_transcript_process(student_id): 
    cookies = bt.login(bt.username, bt.password) 
    raw_html = select_student(student_id, cookies) 
    # cookies = get_transcript(cookies, student_id)
    # cookies = get_students_schedule(cookies, student_id)
    # print(raw_html) 
    output_file = os.path.join(output_dir, f"schedule.csv")
    schedule_list = get_schedule_from_raw_html(raw_html, student_id, output_file)

    return cookies


def get_schedule_from_raw_html(raw_html, student_id, output_file): 
    logging.info("Getting schedule from raw html ...")
    parsed_html = html.fromstring(raw_html)
    schedule_table = parsed_html.xpath("//table[@class='datadisplaytable']")

    # open output_file in append mode 
    with open(output_file, "a") as f:
        # for each table, from "caption" tag, which has the format: Creativity and Innovation - AMB 310 - 4 .. get the stuff after the second-last dash 
        schedule_list = []
        for table in schedule_table:  
            caption = table.xpath(".//caption/text()")
            if len(caption) > 0: 
                caption_text = caption[0]
                parts = caption_text.split(" - ")
                if len(parts) >= 2: 
                    course_info = " - ".join(parts[-2:])  # Join all parts except the last two
                    # ignore courses starting with AMB 
                    if course_info.startswith("AMB"): 
                        continue
                    # course_info = course_info.replace(" ", "")
                    # schedule_list.append(course_info.strip())
                    f.write(f"{student_id},{course_info.strip()}\n")                   



def select_student(student_id, cookies): 
    # Select Term 

    logging.info("Selecting Term ...")
    term_data = {"term": term_identifier}
    logging.debug(term_data)
    r = requests.post(url=url_term_selection, 
                        data=term_data, 
                        verify=False,
                        cookies=cookies)
    
    logging.debug(r.text)
    if "Student or Advisee ID:" not in r.text: 
        logging.error("Unable to select term!")
        sys.exit("TERM FAILURE")   


    # Select student 
    logging.info("Selecting Student ...")
    student_data = {"STUD_ID": student_id, 
                    "CALLING_PROC_NAME": "", 
                    "CALLING_PROC_NAME2": "", 
                    "term": term_identifier, 
                    "term_in": term_identifier}
    logging.debug(student_data)
    cookies = dict(r.cookies)
    r = requests.post(url=url_student_selection, 
                        data=student_data, 
                        verify=False,
                        cookies=cookies)
    if "is the name of the student" not in r.text: 
        print(r.text) 
        logging.error("Unable to select student ... ! ")
        # sys.exit("TERM FAILURE")   
        raise bt.TermException("Student ID " + student_id + " not found!")

    logging.debug(r.text)
    raw_html = html.fromstring(r.text)

    logging.info("Checking XYZ Value")
    # yes, that's what they are calling it! 
    xyz_val = str(raw_html.xpath("//input[@name='xyz']/@value")[0])
    if xyz_val == "": 
        logging.error("Unable to get xyz val!")
        sys.exit("XYZ FAILURE")   


    logging.info("Trying sched page")
    cookies = dict(r.cookies)
    student_store_data = {"xyz": xyz_val}
    r = requests.post(url=url_sched_show, 
                        data=student_store_data, 
                        verify=False,
                        cookies=cookies)
    if "Click on a student's name to view" not in r.text: 
        print(r.text) 
        logging.error("Unable to show schedule page ... ! ")
        raise bt.TermException("Student ID " + student_id + " not found!")

    return r.text 



if __name__ == "__main__": 
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Make output directory 
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # run 
    if len(sys.argv) < 2: 
        print("Please give student IDS list filename.")
        sys.exit(1)

    list_filename = sys.argv[1]
    
    student_id_list = bt.get_student_list(list_filename)

    for idx, student_id in enumerate(student_id_list): 
        try:
            logging.info("Getting Transcript for: " + student_id + " (" + str(idx+1) + " of " + str(len(student_id_list)) + ")")
            get_transcript_process(student_id)
            
        except bt.TermException as e:
            logging.error(f"Error processing student ID {student_id}: {e}")
    
        logging.info(" - x - ")
        logging.info("Cooling off for " + str(bt.cooloff_time) + "s...")
        time.sleep(bt.cooloff_time)
        # break 
    
    logging.info("Done.")