from lxml import html
import os 
import sys
import logging 

output_dir = "output"
output_file = "credits-earned.csv"

def output_credits_earned_to_text(student_id, student_name, overall_earned_credits):
    # output by appending to file output_file as csv row escaping name with quotes 
    with open(output_file, 'a') as f: 
        f.write(f"{student_id},\"{student_name}\",{overall_earned_credits}\n")
    logging.info(f"Wrote to {output_file}: {student_id},\"{student_name}\",{overall_earned_credits}")

def get_credits_earned(student_id): 
    logging.info(f"Processing student ID: {student_id}")
    html_filename = os.path.join(output_dir, student_id + "-transcript.html")
    with open(html_filename) as f:
        contents = f.readlines()

    contents = ''.join(contents)
    root = html.fromstring(contents) 
    student_name = root.xpath("//a[@name='Student Address']/text()")[0]
    student_name = student_name[:student_name.index('-')]
    # student_first_name = student_name.split(" ")[0].strip()
    # student_last_name = student_name.split(" ")[2].strip()
    # student_name = f"{student_first_name} {student_last_name}"

    logging.info(f"Student name: {student_name}")

    # use xpath to get that tr which has a th with text "Overall:"
    overall_tr = root.xpath("//th[contains(text(), 'Overall:')]/parent::tr")
    if not overall_tr:
        logging.error("Unable to find Overall row!")
        raise ValueError("Overall row not found")
        
    overall_tr = overall_tr[-1]
    tds = overall_tr.xpath(".//td")
    logging.info(f"Found {len(tds)} td elements in Overall row.")

    # print all tds 
    # OVerall earned credits are in td[2] 
    overall_earned_credits = tds[2].text_content().strip()
    logging.info(f"Overall Earned Credits: {overall_earned_credits}")

    output_credits_earned_to_text(student_id, student_name, overall_earned_credits)

    # logging.info("Student name found: ..." + student_name)
    # if student_name == "": 
    #     logging.error("Unable to get student name!")
    #     sys.exit("Student Name Failure")   



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

    # run 
    if len(sys.argv) < 2: 
        print("Please give student IDS list filename.")
        sys.exit(1)

    list_filename = sys.argv[1]
    student_id_list = get_student_list(list_filename)
    for student_id in student_id_list: 
        try: 
            get_credits_earned(student_id)
        except ValueError as ve:
            logging.error(f"ValueError for student ID {student_id}: {ve}")
        except Exception as e: 
            logging.error(f"Error processing student ID {student_id}: {e}")

        
