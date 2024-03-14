from lxml import html
import os 
import sys
import logging 

output_dir = "output"

acceptable_codes = ['CS', 'MATH', 'GCS', 'BIO', 'STAT', 
                    'GSTA', 'GGL0', 'GGER', 'GENG', 'GSEM', 'GPHY', 
                    'GMTH', 'GISL', 'GECN', 'GFRN', 'GARB', 'GPHL',  
                    'GSTA', 'GCIV', 'GGLO', 'GDRA', 'GLAW', 
                    'GJOU', 'GMED', 'GBIO', 
                    'GLIT', 
                    # foundations for waived off 
                    'EEW', 'EER', 'EELS', 'EECL', 'EEOE'
                    ]

def parse_table(student_id, student_name, root):
    out_csv = os.path.join(output_dir, "combined.csv")
    good_trs = []   # will collect data in this 

    all_trs = root.xpath("//tr")
    current_semester = "" 

    for tr in all_trs: 
        tds = tr.xpath('td')
       
        
        useful_tr = False
        tr_data = [] 
        term_text = ""

        for i, td in enumerate(tds): 
            if i == 0 and td.text in acceptable_codes: 
                useful_tr = True 

            if useful_tr: 
                td_text = td.text
                if td_text is not None: 
                    td_text = td_text.replace(',', '')

                tr_data.append(td_text)
                # start edit 
                term_span = tr.xpath('preceding-sibling::tr/th/span')
                for ts in term_span: 
                    if ts.text.startswith("Term:"): 
                        term_text = ts.text[6:].replace("Semester ", "")

                # end edit 

        if len(tr_data) > 0: 
            tr_data.append(term_text)
            good_trs.append(tr_data)
            
            

    out_contents = ""    
    for tr in good_trs: 
        line = ','.join([str(x) for x in tr])
        out_contents += student_id + "," + student_name + "," + line + "\n"

    logging.debug(out_contents)
    logging.info("Writing to file: " + out_csv)
    with open(out_csv, "a") as f:
        f.write(out_contents)

def parse_transcript_html(student_id): 
    html_filename = os.path.join(output_dir, student_id + "-transcript.html")
    with open(html_filename) as f:
        contents = f.readlines()

    contents = ''.join(contents)
    root = html.fromstring(contents) 
    student_name = root.xpath("//a[@name='Student Address']/text()")[0]
    student_name = student_name[:student_name.index('-')]

    logging.info("Student name found: ..." + student_name)
    if student_name == "": 
        logging.error("Unable to get student name!")
        sys.exit("Student Name Failure")   


    parse_table(student_id, student_name, root)

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
        parse_transcript_html(student_id)
        
