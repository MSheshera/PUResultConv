#!/usr/bin/env python
"""
Higher level functions which call the lower level data get functions,
provide some control on nature of output generated and generate the
output.
"""

import os
import sys
import errno
import argparse
import re
import csv
import string
import pprint
import extractData as exDt

#TODO: Consider defining your own exceptions and using them instead of
# printing to stderr manually.

def branchBuild(clargs):
    """
    Split the input text file by branch and build output csv files for
    each branch.
    Arguments:
            clargs: A argparse.Namespace object with the command line
                    arguments
    """

    # It's likely non-text files will be passed to this script.
    if not istext(clargs.in_filename):
        sys.stderr.write('ERROR: Input file must be a text file.\n')
        sys.exit(2)

    try:
        #Check Universal newlines for 'rU'
        in_file = open(clargs.in_filename, 'rU')
        try:
            in_content = in_file.readlines()
        finally:
            in_file.close()
    except IOError as ioe:
        sys.stderr.write('IO ERROR (%d): %s: %s\n' %
                        (ioe.errno, ioe.strerror, clargs.in_filename))
        sys.exit(1)

    # Create output directory
    outDir = 'outCSV'
    try:
        os.makedirs(outDir)
    except OSError as ose:
        # For the case of file by name of outDir existing.
        if not os.path.isdir(outDir) and ose.errno == errno.EEXIST:
            sys.stderr.write('IO ERROR: Could not create output directory\n')
        if ose.errno != errno.EEXIST:
            sys.stderr.write('OS ERROR (%d): %s: %s\n' %
                            (ose.errno, ose.strerror, outDir))
        sys.exit(1)

    # This is unnecessarily complex because of a random error they made
    # where they've missed a closing bracket.
    br08_re = r'.*PUNE.*\([0-9]{4}\s*PAT.*\)\s*\(([A-Z\.\-&\s]+)(\s|\)).*'
    br12_re = r'^BRANCH.*\(([A-Z\.\&\s]+)\)$'

    examPat = exDt.getExPat(in_content)
    if examPat == '2008':
        br_re = br08_re
    elif examPat == '2012':
        br_re = br12_re
    else:
        sys.stderr.write('ERROR: Can only handle 2008 or 2012 pattern mark'
                        ' sheets\n')
        sys.exit(2)

    # Need this to handle first branch occurring in the file. Am assuming
    # that first/second line in file always has the first branch but
    # this might not always be true.
    if examPat == '2008':
        br_old = re.match(br_re, in_content[0].strip()).group(1)
    elif examPat == '2012':
        br_old = re.match(br_re, in_content[1].strip()).group(1)

    # Build and write outputs for each branch appearing in the input file.
    br_cur = br_old
    br_content = []
    for line in in_content:
        line = line.strip()
        ret_obj = re.match(br_re, line)
        if ret_obj:
            br_old = br_cur
            br_cur = ret_obj.group(1)
            if br_cur != br_old:
                print '\n', br_old
                buildOut(br_content, outDir, examPat, clargs)
                br_content = []
        br_content.append(line)

    # Need this to handle the final branch appearing in the file.
    print '\n', br_old
    buildOut(br_content, outDir, examPat, clargs)
    
    sys.exit(0)

def istext(in_filename):
    """
    Establish that input file is a text file.
    Source: http://stackoverflow.com/a/1446870/3262406
    """

    try:
        in_file = open(in_filename, 'r')
        try:
            s = in_file.read(512)
        finally:
            in_file.close()
    except IOError as ioe:
        sys.stderr.write('IO ERROR (%d): %s: %s\n' %
                        (ioe.errno, ioe.strerror, in_filename))
        sys.exit(1)

    text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
    _null_trans = string.maketrans("", "")
    if not s:
        # Empty files are considered text
        return True
    if '\0' in s:
        # Files with null bytes are likely binary
        return False
    t = s.translate(_null_trans, text_characters)
    # If more than 30% non-text characters, then
    # this is considered a binary file
    if float(len(t))/float(len(s)) > 0.30:
        return False
    return True

def buildOut(in_content, outDir, examPat, clargs):
    """
    Calls data get functions. Gets the data to write to the csv file.
    Arguments:
            in_content: List with each line of input as one element of the
                    list.
            outDir: String naming the output directory.
            examPat: String naming the exam pattern.
            clargs: A argparse.Namespace object with the command line
                    arguments
    """

    br = exDt.Branch(examPat=examPat)
    # Subject marks can only be extracted in the 2008 pat files.
    br.subjects = exDt.getSubjects(in_content, br.examPat)
    if (not br.subjects) and (br.examPat != '2012'):
        sys.stderr.write('ERROR: Auto-detect subjects failed\n')
        return
    # Get PRN and total marks from file. PRN is most reliably extracted
    # and forms basis for counts of students.
    br.prn = exDt.getPRN(in_content)
    if not br.prn:
        sys.stderr.write('ERROR: Extraction of PRN failed\n')
        return
    br.totalMarks = exDt.getTotal(in_content)
    if not br.totalMarks:
        sys.stderr.write('ERROR: Extraction of Total marks failed\n')
        return
    # Subject marks always padded to match length of PRN
    if clargs.nowritesubj == False:
        br.sMarkList = exDt.getSubjMark(in_content, br.subjects, len(br.prn),
                                         br.examPat)

    # Initialize branch attributes
    br.brAbbr = exDt.getBranch(in_content, br.examPat)
    br.colAbbr = exDt.getCollege(in_content)
    br.year = exDt.getYear(in_content)
    br.exDate = exDt.getExamDate(in_content, br.examPat)

    # Print out details if they're available and asked for.
    if clargs.printsubj == True and br.examPat == '2008':
        pprint.pprint(exDt.getSubjDict(in_content, br.examPat))
    if clargs.noprintdetail == False:
        print br

    out_fname = '-'.join([br.colAbbr, br.examPat, br.year, br.brAbbr,
                        br.exDate])

    # Crude check to ensure that scan through content is as expected.
    if len(br.prn) > len(br.totalMarks):
        # When lengths don't match pad total with 'nan'.
        while len(br.totalMarks) != len(br.prn):
            br.totalMarks.append((float('NaN'), float('NaN')))
        sys.stderr.write('WARNING: Expect misalignment between PRN and'
                        ' marks\n')
        # Indicate misalignment in filename
        out_fname = ''.join([out_fname, '-Misalign'])
    elif len(br.prn) < len(br.totalMarks):
        sys.stderr.write('ERROR: Unexpected error while extracting data.'
                        ' Total marks count more then number of students.\n')
        return

    #Write output to file.
    writeOut(br, clargs, out_fname, outDir)

def writeOut(br, clargs, out_fname, outDir):
    """
    Given the data to write out, this writes out the csv file.
    """

    # Generate csv heading tuple
    if clargs.nowriteprn == False:
        head_tuple = ('PRN', 'College', 'Branch', 'TotalNoGrace', 'TotalGrace',
                'SumTotal')
    elif clargs.nowriteprn == True:
        head_tuple = ('College', 'Branch', 'TotalNoGrace', 'TotalGrace',
                'SumTotal')
    for i in range(len(br.subjects)):
        head_tuple = (head_tuple + (''.join([exDt.makeAbbr(br.subjects[i]),
                                    '_PP']),))
        head_tuple = (head_tuple + (''.join([exDt.makeAbbr(br.subjects[i]),
                                    '_PR']),))
        head_tuple = (head_tuple + (''.join([exDt.makeAbbr(br.subjects[i]),
                                    '_OR']),))
        head_tuple = (head_tuple + (''.join([exDt.makeAbbr(br.subjects[i]),
                                    '_TW']),))

    if clargs.nowritecsv == False:
        try:
            out_file = os.path.join(outDir, ''.join([out_fname, '.csv']))
            csv_file = open(out_file, 'w')
            try:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow(head_tuple)
                # Generate each row tuple
                for prn_i in range(len(br.prn)):
                    if clargs.nowriteprn == True:
                        student_tuple = (br.colAbbr, br.brAbbr,
                                br.totalMarks[prn_i][0],
                                br.totalMarks[prn_i][1],
                                br.totalMarks[prn_i][0] +
                                br.totalMarks[prn_i][1])
                    elif clargs.nowriteprn == False:
                        student_tuple = (br.prn[prn_i], br.colAbbr, br.brAbbr,
                                br.totalMarks[prn_i][0],
                                br.totalMarks[prn_i][1],
                                br.totalMarks[prn_i][0] +
                                br.totalMarks[prn_i][1])
                    if clargs.nowritesubj == False and br.examPat == '2008':
                        student_tuple = (student_tuple +
                                         tuple(br.sMarkList[prn_i]))
                    csvwriter.writerow(student_tuple)
                    student_tuple = ()
            finally:
                csv_file.close()
                return
        except IOError as ioe:
            sys.stderr.write('IO ERROR (%d): %s: %s\n' %
                            (ioe.errno, ioe.strerror, out_file))
            sys.exit(1)

def main():
    """
    Parse command line arguments. And call functions which do
    the real work.
    """
    #TODO: Add mutually exclusive command line argument groups.

    parser = argparse.ArgumentParser()

    parser.add_argument('in_filename',
            help='Path to the input text file to read from.')

    parser.add_argument('-d', '--noprintdetail',
            help="Don't print details of each csv file written to disk.",
            action='store_true', default=False)

    parser.add_argument('-b', '--printsubj',
            help='Print list of subjects for each branch. This is only '
                    'supported for 2008 pattern files',
            action='store_true', default=False)

    parser.add_argument('-c', '--nowritecsv',
            help="Don't write csv file to disk. Use for dry runs without"
            " dirtying your directory with csv files.", action='store_true',
            default=False)

    parser.add_argument('-s', '--nowritesubj',
    help=" Don't write subject marks to csv file. Output will include only"
            " the total marks. This is the default for anything except 2008"
            " exam pattern files.", action='store_true', default=False)

    parser.add_argument('-p', '--nowriteprn',
            help="Don't write PRN to csv file. Use this to protect privacy of"
            " students.", action='store_true', default=False)

    clargs = parser.parse_args()
    branchBuild(clargs)

if __name__ == '__main__':
    main()
