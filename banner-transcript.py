# Install dependencies: pip install lxml pyyaml

import logging
import sys
import time
import os

from lxml import html
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
s = requests.Session()

# DO NOT MODIFY BEYOND THIS POINT 

import yaml
config = yaml.safe_load(open("settings.yaml"))
username = config['username']
password = config['password']
term_identifier = config['term_identifier']

cooloff_time = 0


output_dir = "output"

url_prefix = "https://bannerxe.effatuniversity.edu.sa:8001"
url_login_page = url_prefix + "/ssbprod/twbkwbis.P_WWWLogin"
url_login_submit = url_prefix + "/ssbprod/twbkwbis.P_ValLogin"
url_term_selection = url_prefix + "/ssbprod/bwlkoids.P_FacIDSel"
url_student_selection = url_prefix + "/ssbprod/bwlkoids.P_FacVerifyID"
url_student_store = url_prefix + "/ssbprod/bwlkoids.P_FacStoreID"
url_transcript = url_prefix + "/ssbprod/bwlkftrn.P_FacDispTran"
url_view_transcript = url_prefix + "/ssbprod/bwlkftrn.P_ViewTran"


driver = None



class TermException(Exception):
    pass


def login(username, password): 
    logging.info("Logging in ... ")

    r = requests.get(url_login_page)
    # logging.debug("Login page status: " + r.status_code)
    cookies = dict(r.cookies)

    field_user = "sid"
    field_password = "PIN"
    login_data = {field_user: username, field_password: password}
    logging.debug(str(login_data))
    r = requests.post(url=url_login_submit, 
                        data=login_data, 
                        verify=False,
                        cookies=cookies)
    # logging.debug("Login post status: " + r.status_code)
    logging.debug(r.text)
    if "WELCOME" not in r.text: 
        logging.error("Unable to log in!")
        sys.exit("Login Failure")   

    cookies = dict(r.cookies)
    return cookies 
    

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
        raise TermException("Student ID " + student_id + " not found!")

    logging.debug(r.text)
    raw_html = html.fromstring(r.text)

    # yes, that's what they are calling it! 
    xyz_val = str(raw_html.xpath("//input[@name='xyz']/@value")[0])
    if xyz_val == "": 
        logging.error("Unable to get xyz val!")
        sys.exit("XYZ FAILURE")   

    # Store student .. whatever that means 
    logging.info("Saving Student ...")
    student_store_data = {"term_in": term_identifier, 
                    "sname": "bmenu.P_FacStuMnu", 
                    "xyz": xyz_val}
    logging.debug(student_store_data)
    cookies = dict(r.cookies)
    r = requests.post(url=url_student_store, 
                        data=student_store_data, 
                        verify=False,
                        cookies=cookies)
    logging.debug(r.text)

    if "Academic Transcript" not in r.text: 
        logging.error("Unable to store student!")
        sys.exit("TERM FAILURE")   

    cookies = dict(r.cookies)
    return cookies 


def get_transcript(cookies, student_id):
    logging.info("Selecting Transcript ...")
    r = requests.get(url=url_transcript, 
                        verify=False,
                        cookies=cookies)
    
    logging.debug(r.text)
    if "select a transcript level" not in r.text: 
        logging.error("Unable to get transcript page!")
        # sys.exit("Transcript Page FAILURE")   
        raise TermException("Transcript page not found!")



    # VIEW Transcript 
    view_transcript_data = {"levl": "", 
                    "tprt": "WEB"}
    logging.debug(view_transcript_data)
    cookies = dict(r.cookies)
    r = requests.post(url=url_view_transcript, 
                        data=view_transcript_data, 
                        verify=False,
                        cookies=cookies)
    logging.debug(r.text)



    if "This is not an official transcript" not in r.text: 
        logging.error("Unable to view web transcript!")
        sys.exit("VIEW TRANSCRIPT FAILURE") 


    output_filename = os.path.join(output_dir, student_id + "-transcript.html")
    with open(output_filename, "w") as f: 
        f.write(r.text)

    logging.debug("Wrote student file: " + output_filename)


def get_transcript_process(student_id): 
    cookies = login(username, password) 
    cookies = select_student(student_id, cookies) 
    cookies = get_transcript(cookies, student_id) 
    

# def install_driver():
#     global driver  
#     logging.debug("Setting up Web Driver for Chrome ... ")
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     assert driver.title == "User Login"


def get_student_list(list_filename): 
    student_id_list = []
    with open(list_filename, 'r') as f: 
            for line in f: 
                if line.strip() != "": 
                    student_id_list.append(line.strip())
    
    return student_id_list 

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
    
    student_id_list = get_student_list(list_filename)

    for idx, student_id in enumerate(student_id_list): 
        try:
            logging.info("Getting Transcript for: " + student_id + " (" + str(idx+1) + " of " + str(len(student_id_list)) + ")")
            get_transcript_process(student_id)
            
        except TermException as e:
            logging.error(f"Error processing student ID {student_id}: {e}")
    
        logging.info(" - x - ")
        logging.info("Cooling off for " + str(cooloff_time) + "s...")
        time.sleep(cooloff_time)
    
    logging.info("Done.")
