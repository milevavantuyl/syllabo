'''Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl
pymysql functions for Syllabo'''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import cs304dbi as dbi
import os

UPLOAD_FOLDER = 'upload_folder'
ALLOWED_EXTENSIONS = {'pdf'}

PICTURE_EXTENSTIONS = {'jpg', 'png', 'jpeg'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Sarah's functions:
def getBasics(cid):
    '''getBasics() returns a dictionary of course information 
       from the course table in syllabo_db given the cid (UNIQUE course id)
       this information is used to populate the course page'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            SELECT title, dep, cnum, crn, web, yr, sem, prof, cid
            FROM course
            WHERE cid = (%s)''', [cid])
    basicsDict = curs.fetchone()
    conn.commit()
    return basicsDict

def getAvgRatings(cid):
    '''getAvgRatings() returns a dictionary of average course ratings information 
       by aggregating info from the rates table in syllabo_db given the cid.
       These averages are used to populate the course page'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            SELECT AVG(relevRate) AS rel, AVG(usefulRate) AS useful, AVG(diffRate) AS diff, AVG(expectRate) AS exp, AVG(hoursWk) AS hrsWk
            FROM rates
            WHERE cid = (%s)''', [cid])
    avgRatingsDict = curs.fetchone()
    conn.commit()
    return avgRatingsDict

def getComments(cid):
    '''getComments() returns a dictionary of all of the comments for a course
       given the cid. This information will be displayed on the course page.'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            SELECT name, comment  
            FROM rates INNER JOIN student USING(bNum)
            WHERE cid = (%s)''', [cid])
    commentsDict = curs.fetchall()
    conn.commit()
    return commentsDict

def makeRatings(bNum, cid, relevRate, usefulRate, diffRate, expectRate, hoursWk, comment):
    '''makeRatings() (returns None) inserts a new row into the rates table of syllabo_db. 
       The cid will be supplied by the page, the bNum by the session login info,
       and all other columns from the rating form submitted by the user
       found on the course page.'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            INSERT INTO rates(bNum, cid, relevRate, usefulRate, diffRate, expectRate, hoursWk, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
            [bNum, cid, relevRate, usefulRate, diffRate, expectRate, hoursWk, comment])
    conn.commit()

def addFavorite(bNum, cid):
    '''adds a course to a students "favorites"'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            INSERT INTO favorites(bNum, cid)
            VALUES (%s, %s)''', 
            [bNum, cid])
    conn.commit()


def updateCourse(updates, cid):
    ''''updateCourse() allows the user to update any information about the course'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            UPDATE course 
            SET title = (%s), dep = (%s), cnum = (%s), crn = (%s), 
            web = (%s), yr = (%s), sem = (%s), prof = (%s) 
            WHERE cid = (%s)''', 
            [updates['course-title'], updates['course-dept'], updates['course-num'], 
            updates['course-crn'], updates['course-website'], updates['course-year'],
            updates['course-sem'], updates['course-prof'], cid])
    conn.commit()

def getFavorites(bNum):
    '''getFavorites returns the cid and course name for all favorite courses of a given bNum'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            SELECT cid, title  
            FROM favorites INNER JOIN course USING(cid)
            WHERE bNum = (%s)''', [bNum])
    favoritesDict = curs.fetchall()
    conn.commit()
    return favoritesDict
    
def getStudentComments(bNum):
    '''getStudentComments() returns a dictionary of all of the comments a certain student has made
       given the bNum. This information will be displayed on their profile.'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            SELECT title, comment  
            FROM rates INNER JOIN course USING(cid)
            WHERE bNum = (%s)''', [bNum])
    commentsDict = curs.fetchall()
    conn.commit()
    return commentsDict

def updateMajor(major, bNum):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
            UPDATE student  
            SET major = (%s)
            WHERE bNum = (%s)''', [major, bNum])
    commentsDict = curs.fetchall()
    conn.commit()
    
# Emily's functions for login and creating profile:

def checkUser(conn, bNumber):
    '''Input: User bnum,
       Output: true if bnum is in database, false otherwise'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT bNum 
            FROM student 
            WHERE bNum = (%s)
        ''', [bNumber])
    bNumInDB = curs.fetchone()
    # Checks if there is no Bnum that matches in database
    return bNumInDB != None 

def insertStudent(val):
    '''Takes all student info as a parameter and uses it to insert the student into the database'''
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    curs.execute('''
    INSERT into student(bNum, name, major, email)
    VALUES(%s, %s, %s, %s)''', 
    val)
    conn.commit()

def getBNum():
    '''Function to get the bnumber of the logged in student. Prerequisite is that the student 
        is currently logged in'''
    if 'CAS_ATTRIBUTES' in session:
        attribs = session['CAS_ATTRIBUTES']
        return attribs.get('cas:id')

def allowed_picture_file(filename):
    '''Helper function for uploadPortrait that checks if the file is a picture using filename input'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in PICTURE_EXTENSTIONS


def insertPicture(bNum, pic_file):
    '''Helper function for uploadPortrait that puts the filename in the database in the portrait table
        INPUT: '''
    try:
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''
                INSERT into portrait(bNum, filename) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE filename = %s''', [bNum, pic_file, pic_file])
        conn.commit()
        flash('Upload successful')
    except Exception as err:
        flash('Upload failed {why}'.format(why=err))

#sarah's function, for profile page
def getStudent(bNum):
    '''Returns all information about the student given the bNum'''
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    curs.execute('''
            SELECT *
            FROM student 
            WHERE bNum = %s''', [bNum])
    student = curs.fetchone()
    return student

def getStudentFromName(name):
    '''Returns all information about the student given the bNum'''
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    curs.execute('''
            SELECT bNum, name, major, email
            FROM student 
            WHERE name = %s''', [name])
    student = curs.fetchone()
    return student

# Mileva's functions:

def getCourses(conn, query, kind):
    ''' Input: User search query and kind of query, 
        Output: All courses and sections fitting the query'''
    curs = dbi.dict_cursor(conn)
    if (kind in ["title", "dep", "cnum"]):
        curs.execute('''SELECT distinct cnum, title
                        FROM course
                        WHERE {} like %s
                        ORDER BY cnum ASC, title ASC'''.format(kind), 
                        ['%' + query + '%']) 
        courses = curs.fetchall()

        # Finds all sections associated with each distinct course
        # Can't use inner joins b/c denormalized database
        for course in courses: 
            course['sections'] = getSections(conn, course['cnum'], course['title'])
            course['ratings'] = getCourseRatings(conn, course)

        return courses 

def getAllCourses(conn): 
    ''' Gets all courses, sections, and ratings in the databases and sorts by 
    cnum and title of the course'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT distinct cnum, title
                    FROM course
                    ORDER BY cnum ASC, title ASC''')
    courses = curs.fetchall()

    # Finds all sections associated with each distinct course
    for course in courses: 
        course['sections'] = getSections(conn, course['cnum'], course['title'])
        course['ratings'] = getCourseRatings(conn, course)

    return courses 

def getCoursesByProf(conn, query): 
    ''' Input: User search query by prof. Output: All courses and sections by matching profs'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT distinct prof 
                    FROM course
                    WHERE prof like %s
                    ORDER BY prof ASC''', ['%' + query + '%'])
    profs = curs.fetchall()

    for prof in profs: 
        prof['sections'] = getSectionsByProf(conn, prof['prof'])
    
    return profs


def getSectionsByProf(conn, prof):
    '''Input: prof name. Output: List of dictionaries containing info about course 
       sections in sorted order. With the limited data being collected about each prof, 
       sections taught by different profs with the same name will be returned together.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT cnum, title, yr, sem, cid 
                    FROM course 
                    WHERE prof = %s 
                    ORDER BY cnum ASC, yr desc''', [prof])
    sections = curs.fetchall()
    return sections

def getSections(conn, cnum, title): 
    '''Input: course cnum and title. Output: list of dictionaries containing all
       the information about each course section in sorted order'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT cnum, title, sem, yr, prof, cid
                    FROM course 
                    WHERE cnum = %s and title = %s
                    ORDER BY yr DESC''', [cnum, title])
    sections = curs.fetchall()
    return sections

def getCourseRatings(conn, course):
    '''Input course dictionary containing a title and cnum. Outputs: A dictionary 
       of the average ratings across all sections of that course.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT avg(relevRate) as relev, 
                            avg(usefulRate) as useful, 
                            avg(diffRate) as diff, 
                            avg(expectRate) as expect, 
                            avg(hoursWk) as hoursWk
                    FROM rates INNER JOIN course USING (cid)
                    WHERE cnum = %s and title = %s''', 
                    [course['cnum'], course['title']])
    courseRatings = curs.fetchone()
    return courseRatings


def numSections(conn, query, kind):
    '''Input: user query and kind. Output: number of sections fitting that query'''
    curs = dbi.cursor(conn)
    if (kind in ["title", "dep", "cnum", "prof"]):
        curs.execute('''SELECT count(*) 
                        FROM course
                        WHERE {} like %s'''.format(kind), ['%' + query + '%'])
        num = curs.fetchone()
        return num[0]

def getOneResult(conn, query, kind):
    '''Input: user query and kind (for a search result that 
       returns exactly one course). Output: cid of unique section fitting that query'''
    curs = dbi.dict_cursor(conn)
    if (kind in ["title", "dep", "cnum", "prof"]):
        curs.execute('''SELECT cid, cnum
                        FROM course
                        WHERE {} like %s'''.format(kind), ['%' + query + '%']
                    ) 
        section = curs.fetchone()
        return section['cid']

# Safiya's functions:
def insertCourse(val):
    '''Takes all course info as a parameter and uses it to insert the given course into the database'''
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    curs.execute('''
    INSERT into course(title, dep, cnum, crn, web, yr, sem, prof)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)''', 
    val)
    conn.commit()
    curs.execute('SELECT last_insert_id()')
    row = curs.fetchone()
    return row[0]

def getCID(val):
    '''Gets the CID from the course that was just submitted to render the 
       correct syl_upload form'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select cid from course where cid = %s''',
    [val])
    result = curs.fetchone()
    return result['cid']

def getRecommended():
    '''Gets recommended courses to display on the home page'''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT course.cid, course.title 
    FROM course LIMIT 3''')
    results = curs.fetchall()
    return results

def allowed_file(filename):
    '''Helper function for uploadSyllabus that checks if the file is a pdf'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def saveToDB(x, aFile):
    '''Helper function for uploadSyllabus that puts the file name in the database'''
    try:
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''
                INSERT into syllabi(cid, filename) VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE filename = %s''', [x, aFile, aFile])
        conn.commit()
        flash('Upload successful')
    except Exception as err:
        flash('Upload failed {why}'.format(why=err))


if __name__ == '__main__':
   dbi.cache_cnf()   # defaults to ~/.my.cnf
   dbi.use('syllabo_db')
   conn = dbi.connect()

