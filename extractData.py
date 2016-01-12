"""
Code to extract data from the text file generated from the results 
pdf file.
"""

import re
import math
import inspect


class Branch(object):
    """
    Holds information for a give branch.

    Attributes: brAbbr, prnCount, tmCount, subvCount, colAbr,
            year, exDate, exPat
    """
    def __init__(self, brAbbr='UNKN', prn=None, totalMarks=None, 
            sMarkList=None, subjects=None, colAbbr='UNKN', year='UNKN', 
            exDate='UNKN', examPat='UNKN'):
        self.brAbbr = brAbbr
        self.prn = prn
        self.totalMarks = totalMarks
        self.sMarkList = sMarkList
        self.subjects = subjects
        self.colAbbr = colAbbr
        self.year = year
        self.exDate = exDate
        self.examPat = examPat

    def __str__(self):
        return ('PRN count: %d\nTotal marks count: %d\nSubject vec count:'
                ' %d\nCollege abbr: %s\nYear: %s\nBranch abbr: %s\nExam date:'
                ' %s\nExam pattern: %s\n') % (len(self.prn),
                len(self.totalMarks), len(self.sMarkList), self.colAbbr, 
                self.year, self.brAbbr, self.exDate, self.examPat)


def getExPat(in_content):
    """
    Get exam pattern from the file. Only handles 2012 and 2008 format
    files.
    """

    err_msg = ("%s expected argument of type 'list'; %s given" %
                (inspect.stack()[0][3], type(in_content)))
    assert (type(in_content) is list), err_msg

    patCom_re = r'.*PUNE.*\(([0-9]{4})\s*[A-Z\.]+\).*'
    pat = 'UNKN'

    for line in in_content:
        line = line.strip()
        ret_obj = re.match(patCom_re, line)
        if ret_obj:
            pat = ret_obj.group(1)
            break

    # Only expected values be returned
    if pat.strip() in ('2008', '2012'):
        return pat.strip()
    else:
        return 'UNKN'

def getCollege(in_content):
    """
    Get the college name code so files may be named automatically.
    """

    err_msg = ("%s expected argument of type 'list'; %s given" %
                (inspect.stack()[0][3], type(in_content)))
    assert (type(in_content) is list), err_msg

    colCom_re = r'\s*(?:[A-Z][0-9]{8}).*,\s*([A-Z]+)\s*,'
    col_name = 'UNKN'

    for line in in_content:
        line = line.strip()
        ret_obj = re.match(colCom_re, line)
        if ret_obj:
            col_name = ret_obj.group(1)
            break

    return col_name

def getYear(in_content):
    """
    Get year. One amongst  FE, SE, TE or BE.
    """

    err_msg = ("%s expected argument of type 'list'; %s given" %
                (inspect.stack()[0][3], type(in_content)))
    assert (type(in_content) is list), err_msg

    yrCom_re = r'.*\s*([FSTBE\.]{4})(?:\([0-9]{4}\s*[A-Z\.]+\))'
    year = 'UNKN'

    for line in in_content:
        line = line.strip()
        ret_obj = re.match(yrCom_re, line)
        if ret_obj:
            year = ret_obj.group(1)

    year = year.replace('.', '')

    # Only expected values be returned
    if year.strip() in ('BE', 'TE', 'SE', 'FE'):
        return year.strip()
    else:
        return 'UNKN'


def getExamDate(in_content, examPat):
    """
    The exam which the result corresponds to, i.e. the Month and Year
    of the exam.
    """

    err_msg = ("%s expected argument of type 'list','str'; %s,%s given" %
                (inspect.stack()[0][3], type(in_content), type(examPat)))
    assert (type(in_content) is list and type(examPat) is str), err_msg

    ex08_re = r'.*PUNE.*\s+([A-Z]+\s+[0-9]{4}$)'
    ex12_re = r'.*PUNE.*\,.*([A-Z]{3,}\s+[0-9]{4})$'
    ex = 'UNKN'
    if examPat == '2008':
        ex_re = ex08_re
    elif examPat == '2012':
        ex_re = ex12_re

    for line in in_content:
        line = line.strip()
        ret_obj = re.match(ex_re, line)
        if ret_obj:
            ex = ret_obj.group(1)
            break

    # Turn 'MAY 2015' to '2015MAY'.
    ex = ex.split()
    if len(ex) == 2:
        ex[0], ex[1] = ex[1], ex[0]
        ex = ''.join(ex)
        return ex
    else:
        return 'UNKN'

def getBranch(in_content, examPat):
    """
    Get the branch of engineering.
    """

    err_msg = ("%s expected argument of type 'list','str'; %s,%s given" %
                (inspect.stack()[0][3], type(in_content), type(examPat)))
    assert (type(in_content) is list and type(examPat) is str), err_msg

    br08_re = (r'.*PUNE.*\([0-9]{4}\s*PAT.*\)\s*\(([A-Z\.\-&\s]+)(\s|'
                '\)).*')
    br12_re = r'^BRANCH.*\(([A-Z\.\&\s]+)\)$'
    branch = 'UNKN'
    if examPat == '2008':
        br_re = br08_re
    elif examPat == '2012':
        br_re = br12_re

    for line in in_content:
        line = line.strip()
        ret_obj = re.match(br_re, line)
        if ret_obj:
            branch = ret_obj.group(1)
            break

    return makeAbbr(branch)

def getPRN(in_content):
    """
    Gets the permanent registration number from the file.
    """

    err_msg = ("%s expected argument of type 'list'; %s given" %
                (inspect.stack()[0][3], type(in_content)))
    assert (type(in_content) is list), err_msg

    PRN_list = []
    PRNCom_re = r'([0-9]{8}[A-Z])'

    for line in in_content:
        line = line.strip()
        PRN = re.findall(PRNCom_re, line)
        if PRN:
            PRN_list.append(PRN[0])

    return PRN_list

def getTotal(in_content):
    """
    Gets the grand total marks from the file.
    """

    err_msg = ("%s expected argument of type 'list'; %s given" %
                    (inspect.stack()[0][3], type(in_content)))
    assert (type(in_content) is list), err_msg

    totalMarks = []
    # Find a 1 to 4 digit total or a 1 to 4 digit total
    # with a grace mark awarded for a better class
    gtCom_re = (r'^GRAND TOTAL\s*=\s*([0-9]{1,4}|[0-9]{1,4}\s*\+\s*[0-9]+'
                r'|--)/.*')

    for line in in_content:
        line = line.strip()
        tmark = re.findall(gtCom_re, line)
        if tmark:
            try:
                totalMarks.append((int(tmark[0]), 0))
            except ValueError:
                # For the case where kid is F-ATKT in 2012 pattern files.
                if tmark[0].strip() == '--':
                    totalMarks.append((float('NaN'), float('NaN')))
                # For the case where grace marks have been given.
                else:
                    total_grace = tmark[0].split('+')
                    totalMarks.append((int(total_grace[0]),
                            int(total_grace[1])))

    return totalMarks

def getSubjMark(in_content, br_subjects, PRN_len, examPat):
    """
    Extract the marks for the subjects passed in 'br_subjects' subject.

    Once marks are obtained getSubjMark formats the marks appropriately.
    Silently pads the data if all the data could not be extracted
    correctly. Only handles 2008 pattern marks at present.
    Arguments:
            in_content: List with each line of input as one element of the
                    list.
            br_subjects: List with each of the subjects that form part of the
                    curriculum for a given branch of engineering.
            PRN_len: Number of students in the branch being processed.
            examPat: Pattern of exam. 2008 or 2012.

    """
    #TODO: Notify when padding has been performed.
    #TODO: Handle 2012 marks. Will likely need significant reworking.

    err_msg = ("%s expected argument of type 'list','list','int','str';"
                " %s,%s,%s,%s given" % (inspect.stack()[0][3],
                type(in_content), type(br_subjects), type(PRN_len),
                type(examPat)))
    assert (type(in_content) is list and type(br_subjects) is list and
            type(PRN_len) is int and type(examPat) is str), err_msg

    # Only handles 2008 pattern files for now.
    if examPat != '2008':
        return []

    # Lower level function actually getting the marks.
    sMarkList_all = _getMarks(in_content, br_subjects)

    # The sMarkList_all now contains marks of different types of exams
    # (PP|TW|OR|PR) as separate lists. For a given subject, merge
    # these separate lists now to obtain a final multi dimension list of
    # all marks.
    sMarkList_mer = []
    for slist in sMarkList_all:
        m_factor = int(math.ceil(len(slist)/float(PRN_len)))
        if m_factor != 1:
            sMarkList_mer.append(_mergeMarks(slist, m_factor))
        else:
            sMarkList_mer.append(slist)

    # Pad with 'nan' if list lengths don't match because of divergences in
    # the input file format. Outer routine prints warning if this happens.
    for lst in sMarkList_mer:
        while len(lst) != PRN_len:
            lst.append([float('NaN')]*4)

    # Partially flatten sMarkList_mer so that all marks of a single kid
    # are in a single list
    sMarkList_flatmer = []
    flat_temp = []
    for kid_idx in range(PRN_len):
        for subj_idx in range(len(br_subjects)):
            flat_temp = flat_temp+sMarkList_mer[subj_idx][kid_idx]
        sMarkList_flatmer.append(flat_temp)
        flat_temp = []

    return sMarkList_flatmer

def _getMarks(in_content, br_subjects):
    """
    Gets the marks from the content. Returns a multi-dimensional list
    with marks for a given type of exam each contained in a list of
    its own. Higher level functions may manipulate the results to
    suit their needs.
    """

    sMarkList_all = []
    sMarkList_cur = []
    sMarkList_tmp = [0]*4

    # regex string that changes with each subject and gets marks.
    base_re = (r'\s*(PP|TW|OR|PR)\s+(?:100|[0-9][0-9])\s+(?:[0-9][0-9])\s+'
                    r'([0-9][0-9]|100|[A-Z]{2}).+')

    for subj in br_subjects:
        subj_re = ''.join([subj, base_re])
        for line in in_content:
            line = line.strip()
            subjMark = re.findall(subj_re, line)
            if subjMark:
                try:
                    if subjMark[0][1] == 'PP':
                        sMarkList_tmp[0] = int(subjMark[0][2])
                    elif subjMark[0][1] == 'PR':
                        sMarkList_tmp[1] = int(subjMark[0][2])
                    elif subjMark[0][1] == 'OR':
                        sMarkList_tmp[2] = int(subjMark[0][2])
                    elif subjMark[0][1] == 'TW':
                        sMarkList_tmp[3] = int(subjMark[0][2])
                except ValueError:
                    # For the case of absent students
                    if subjMark[0][1] == 'PP':
                        sMarkList_tmp[0] = float('NaN')
                    elif subjMark[0][1] == 'PR':
                        sMarkList_tmp[1] = float('NaN')
                    elif subjMark[0][1] == 'OR':
                        sMarkList_tmp[2] = float('NaN')
                    elif subjMark[0][1] == 'TW':
                        sMarkList_tmp[3] = float('NaN')
                sMarkList_cur.append(sMarkList_tmp)
                sMarkList_tmp = [0]*4

        sMarkList_all.append(sMarkList_cur)
        sMarkList_cur = []

    return sMarkList_all


def _mergeMarks(slist, m_factor):
    """
    Merges m_factor rows of the passed slist. To obtain lists which
    contain the different kinds of marks of a subject in a single list.
    """
    
    slist_mer = []
    i_in = 0

    while i_in < len(slist):
        to_merge = slist[i_in:i_in+m_factor]
        # Transpose to_merge using list comprehension and then sum the
        # rows. range(4) since it will always at most be (PP,PR,OR,TW)
        merged = [sum(ts) for ts in [[row[i] for row in to_merge] for i in
                range(4)]]
        slist_mer.append(merged)
        i_in += m_factor
    return slist_mer

def getSubjects(in_content, examPat):
    """
    Finds subjects and infers the nature (elective/compulsory) of
    the subjects. Only handles 2008 pattern marks at present.
    """

    err_msg = ("%s expected argument of type 'list','str'; %s,%s given" %
                (inspect.stack()[0][3], type(in_content), type(examPat)))
    assert (type(in_content) is list and type(examPat) is str), err_msg

    # Only handles 2008 pattern files for now.
    if examPat != '2008':
        return []

    # Lower level function actually getting the subjects and
    # subject codes.
    subjects = getSubjDict(in_content, examPat)

    # Find mandatory subjects
    mandatory = []
    elective = []
    sub_ele = []    # keys to electives.
    for s_key in subjects.keys():
        # Mandatory subjects have completely numeric codes in the 2008PAT
        if s_key.isdigit():
            mandatory.append('('+re.escape(subjects.get(s_key))+')')
        else:
            sub_ele.append(s_key)

    # Find elective subjects if they're present
    if len(sub_ele) > 1:
        temp = []
        sub_ele.sort()
        sub_ele.append(str()) # To ensure final item inclusion
        sub_old = str()
        sub_cur = sub_ele[0]
        for sub in sub_ele[1:]:
            sub_old = sub_cur
            sub_cur = sub
            temp.append(re.escape(subjects.get(sub_old)))
            if sub_cur[0:2] != sub_old[0:2]:
                elective.append('('+('|'.join(temp))+')')
                temp = []

    subjects = mandatory+elective

    # To handle duplication where the subj code for the different
    # types of an exam are different.
    subjects = list(set(subjects))
    return subjects

def getSubjDict(in_content, examPat):
    """
    Finds the subjects and subject code from in_content.
    Returns a dict with the subject code as key and subject as
    value.
    """

    err_msg = ("%s expected argument of type 'list','str'; %s,%s given" %
                (inspect.stack()[0][3], type(in_content), type(examPat)))
    assert (type(in_content) is list and type(examPat) is str), err_msg

    # Only handles 2008 pattern files for now.
    if examPat != '2008':
        return []

    subj_re = (r'((?:[0-9]{3}|[0-9]{2}[A-Z]{1}|[0-9]{2})\s*\.\s*'
                    r'[-A-Z1-3\s\.&\(\)\,\/]+)\s*(?=PP|PR|OR|TW)')
    subjects = []
    for line in in_content:
        ret_obj = re.findall(subj_re, line)
        if ret_obj != []:
            ret_obj = [s.strip() for s in ret_obj]
            [subjects.append(s_i) for s_i in ret_obj if s_i not in subjects]

    # Split subject code and the subject name in list of subjects
    subj_code_re = (r'^([0-9]{3}|[0-9]{2}[A-Z]{1}|[0-9]{2})\s*\.\s*'
                            r'([-A-Z1-3\s\.&\(\)\,\/]+)$')
    subjects = [re.findall(subj_code_re, s_i) for s_i in subjects]

    # Flatten 'subjects' to make a dict out of it.
    subjects = dict([s_pair for sublist in subjects for s_pair in sublist])

    return subjects

def makeAbbr(in_str):
    """
    Given a subject name or a branch name make an abbreviation so
    that it looks good in the csv file and elsewhere.
    """

    err_msg = ("%s expected argument of type 'str'; %s given" %
                (inspect.stack()[0][3], type(in_str)))
    assert (type(in_str) is str), err_msg

    out_str = in_str.replace(' AND ', ' & ')
    out_str = in_str.replace(' OF ', ' ')
    out_str = out_str.translate(None, r'.-()\/?&')
    out_str = out_str.strip()

    if ' ' not in out_str:
        if len(in_str) >= 4:
            out_str = in_str[:4]
        else:
            out_str = in_str[:len(in_str)+1]
    elif '|' in out_str:
        out_str_l = out_str.split('|')
        out_str = "|".join(["".join(word[0] for word in S.split()) for S
        in out_str_l])
    else:
        out_str = "".join([word[0] for word in out_str.split()])

    return out_str
