./venv/bin/jupyter nbconvert ./notebooks/freelancers_analysis.ipynb --no-input --output-dir='./reports'  --to 'html' 
./venv/bin/jupyter nbconvert ./notebooks/jobs_analysis.ipynb        --no-input --output-dir='./reports'  --to 'html' 

# needs you to have installed https://wkhtmltopdf.org/
wkhtmltopdf ./reports/freelancers_analysis.html ./reports/freelancers_analysis.pdf
wkhtmltopdf ./reports/jobs_analysis.html        ./reports/jobs_analysis.pdf

rm ./reports/freelancers_analysis.html
rm ./reports/jobs_analysis.html
