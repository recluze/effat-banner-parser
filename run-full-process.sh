#!/bin/bash 

# Ask user if they have created the students.csv file
read -p "Have you created the students.csv file? (y/n): " response

if [[ "$response" != "y" ]]; then
    echo "Please create the students.csv file before running this script."
    exit 1
fi

# Ask user if they fixed the term ID in settings? 
read -p "Have you updated the term ID in settings.py if needed? (y/n): " response
if [[ "$response" != "y" ]]; then
    echo "Please update the term ID in settings.py before running this script."
    exit 1
fi


# If the file does not exist, exit with an error message
if [[ ! -f students.csv ]]; then
    echo "students.csv file not found! Please create it before running this script."
    exit 1
fi

# If output directory exists, roll its name 
if [[ -d output ]]; then
    timestamp=$(date +%Y%m%d-%H%M%S)
    mv output "output-${timestamp}"
    echo "Existing output directory renamed to output-${timestamp}"
fi


# Save start time 
start_time=$(date +%s)

# make the output directory 
echo "Creating output directory..."
mkdir output

# Create a temporary filename in the format id-<timestamp>.txt
timestamp=$(date +%s)
ids_file="ids-${timestamp}.txt"
log_file="process-log-${timestamp}.log"

echo "Temporary IDs file will be: $ids_file"

# Get the first column of the CSV file and store it in ids_file. Skip the first row (header).
tail -n +2 students.csv | cut -d, -f1 > "$ids_file"

# Scrape from banner 
echo "Starting scraping process..."
python3 banner-transcript.py "$ids_file" > "$log_file" 2>&1

# Parse transacrtips 
echo "Parsing transcripts..."
python3 parse-transcripts.py "$ids_file" >> "$log_file" 2>&1

# Run the audit generation script 
echo "Generating audits..."
python3 generate-all-audit-support-files.py >> "$log_file" 2>&1

# Create tallies file 
echo "Creating tallies file and plans ..."
python3 make-all-tallies.py "$ids_file" >> "$log_file" 2>&1 



# Report time taken 
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
# Convert to minutes and seconds
minutes=$(( elapsed / 60 ))
seconds=$(( elapsed % 60 ))
echo "Process completed in $minutes minutes and $seconds seconds."
