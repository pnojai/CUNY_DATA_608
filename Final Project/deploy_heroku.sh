#!/bin/bash
mkdir /home/jai/Documents/CUNY/Data608/exdth_test
cd /home/jai/Documents/CUNY/Data608/exdth_test
git init
conda create -n exdth_test_env python=3.7 -y
source /home/jai/anaconda3/etc/profile.d/conda.sh
conda activate exdth_test_env
pip install gunicorn
pip install dash
pip install numpy
pip install pandas
cp "/media/sf_jai/Documents/Computing/DataScience/CUNY/Data608/CUNY_DATA_608/Final Project/data608_final.py" .
cp "/media/sf_jai/Documents/Computing/DataScience/CUNY/Data608/CUNY_DATA_608/Final Project/app.py" .
cp "/media/sf_jai/Documents/Computing/DataScience/CUNY/Data608/CUNY_DATA_608/Final Project/temp/.gitignore" "/home/jai/Documents/CUNY/Data608/exdth_test"
cp "/media/sf_jai/Documents/Computing/DataScience/CUNY/Data608/CUNY_DATA_608/Final Project/temp/Procfile" "/home/jai/Documents/CUNY/Data608/exdth_test"
pip freeze > requirements.txt
heroku create exdth-test
git add .
git commit -m 'Heroku deployment: 13/12/2020 16:21:44'
git push heroku master
heroku ps:scale web=1
conda deactivate
