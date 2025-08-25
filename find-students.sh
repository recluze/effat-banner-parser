while read in; 
do 
  ID=$in
  python create-tallies.py $ID | grep 'Details for'
  python create-tallies.py $ID | grep GCS | grep -E -i -w '.$' 
  echo '.'

done < nauman-ids.txt
