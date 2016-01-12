### What this is:
This is a command line tool written in python that aids in converting the 
*yearly college-wise engineering* results distributed by the University of Pune 
(Savitribai Phule Pune University), as pdf files, into a csv file. This tool 
*expects a text file* rather than a pdf file.
    
The format of the result files varies with the curriculum (exam pattern as 
known to PU students). Accordingly, this tool *fully supports 2008 Exam* 
*Pattern* result files and *partially supports 2012 Exam Pattern* result files 
for now. In case of the 2008 Pattern files it can extract individual subject-
wise marks and the total marks of all students whereas in the case of 2012 
Pattern files it can only extract the total marks of all the students.

### Description of the files:
`prepInBldOut.py`: Higher level code which calls the lower level data get 
functions, provides some control on nature of output generated and writes the 
output to disk.

`extractData.py`: Lower level code to extract data from the text file generated 
from the results pdf file.

`./samples/inTest`: Sample input text files. One file of each kind of exam 
pattern.

`./samples/outCSV`: Outputs for the sample inputs.

### Usage Instructions:
**1.** Convert the pdf file to a text file while preserving the layout of the pdf file. I accomplish this by use of the [pdftotext](http://linux.die.net/man/1/pdftotext) command line utility on Linux. Like so:
```bash
pdftotext -layout -nopgbrk input_file.pdf output_file.txt
```
This is also supposed to be available on Windows. I'm sure a Google search will help you to find out more.

**2.** Generate the csv file using this tool. Like so:
```bash
python prepInBuildOut.py input_text_file.txt
```
Or allow the script to be an executable:
```bash
chmod +x prepInBuildOut.py
```
And run it like so:
```bash
./prepInBuildOut.py input_text_file.txt
```
Ensure that both the python source files `extractData.py` and `prepInBldOut.py` are in your current directory while following the above instructions to run the script. The outputs will be written to a directory called `outCSV` in the current directory.

The output files are named as:
College-ExamPattern-Year-Branch-ExamDate.csv

You can access the help instructions by passing `-h` command line 
argument to the script:
```bash
python prepInBuildOut.py -h
```

### Note on version of Python:
The script requires Python 2.7 for it to function correctly. The code has been 
tested on Ubuntu 14.04.

### Note on how the script works:
Uses regular expressions for all the extraction. Estimates the branch; finds 
the subjects and determines if they're elective or mandatory; finds details 
such as the exam pattern, college, branch of engineering, date of exam (month 
and year), year of engineering, total marks of all the students and subject-
wise marks of all students; creates a csv file and writes it to disk.

### Contact:
Write to me at `mssheshera@yahoo.com` with the subject-line "PU Result Analysis 
Suggestions" if you have suggestions or "PU Result Analysis Bugs" if you wish 
to report any errors in the code or "PU Result Analysis Misc" if its neither of 
the two previous cases.

### License:
This work is released under the 
[MIT License](http://opensource.org/licenses/MIT).
