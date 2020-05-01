'''Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl
pymysql functions for Syllabo'''
# import sys
# import pymysql
# import pymysql.constants.ER
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import cs304dbi as dbi
import os

UPLOAD_FOLDER = 'upload_folder'
ALLOWED_EXTENSIONS = {'pdf'}

# Sarah's functions:
'''getBasics() returns a dictionary of course information 
    from the course table in syllabo_db given the cid (UNIQUE course id)
    this information is used to populate the course page'''
def getBasics(cid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    SELECT title, dep, cnum, crn, syl, web, yr, sem, prof
    FROM course
    WHERE cid = (%s)''', [cid])
    basicsDict = curs.fetchone()
    conn.commit()
    return basicsDict

'''getAvgRatings() returns a dictionary of average course ratings information 
    by aggregating info from the rates table in syllabo_db given the cid.
    These averages are used to populate the course page'''
def getAvgRatings(cid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    SELECT AVG(relevRate) AS r, AVG(usefulRate) AS u, AVG(diffRate) AS d, AVG(expectRate) AS e, AVG(hoursWk) AS h
    FROM rates
    WHERE cid = (%s)''', [cid])
    avgRatingsDict = curs.fetchone()
    conn.commit()
    return avgRatingsDict

'''getComments() returns a dictionary of all of the comments for a course
    given the cid. This information will be displayed on the course page.'''
def getComments(cid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    SELECT name, comment  
    FROM rates INNER JOIN student USING(bNum)
    WHERE cid = (%s)''', [cid])
    commentsDict = curs.fetchall()
    conn.commit()
    return commentsDict

'''makeRatings() (returns None) inserts a new row into the rates table of syllabo_db. 
    The cid will be supplied by the page, the bNum by the session login info,
    and all other columns from the rating form submitted by the user
    found on the course page.'''
def makeRatings(bNum, cid, relevRate, usefulRate, diffRate, expectRate, hoursWk, comment):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    INSERT INTO rates(bNum, cid, relevRate, usefulRate, diffRate, expectRate, hoursWk, comment)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
    [bNum, cid, relevRate, usefulRate, diffRate, expectRate, hoursWk, comment])
    conn.commit()

'''addSyllabus() updates the given row in the course table to add a syllabus'''
def addSyllabus(cid, syl):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    UPDATE course SET syl = (%s)
    WHERE cid = (%s)''', [syl, cid])
    conn.commit()

'''addWebsite() updates the given row in the course table to add a website'''
def addWebsite(cid, web):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    UPDATE course SET web = (%s)
    WHERE cid = (%s)''', [syl, web])
    conn.commit()

'''updateCourse() allows the user to update any information about the course'''
def updateCourse(cid, title, dep, cnum, crn, syl, web, yr, sem, prof):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    query = curs.execute('''
    UPDATE course 
    SET title = (%s), dep = (%s), cnum = (%s), crn = (%s), syl = (%s), 
    web = (%s), yr = (%s), sem = (%s), prof = (%s) 
    WHERE cid = (%s)''', [title, dep, cnum, crn, syl, web, yr, sem, prof, cid])
    conn.commit()

# Mileva's functions:

''' Input: User search query and kind of query, Output: All courses and sections fitting the query'''
def getCourses(conn, query, kind):

    curs = dbi.dict_cursor(conn)
    if (kind == "title" or kind == "dep" or kind == "cnum"):
        curs.execute('''SELECT distinct cnum, title
                        FROM course
                        WHERE {} like %s
                        ORDER BY cnum ASC, title ASC'''.format(kind), ['%' + query + '%']
                        ) 
        courses = curs.fetchall()

        # Finds all sections associated with each distinct course
        for course in courses: 
            # print("original: {}".format(course))
            course['sections'] = getSections(conn, course['cnum'], course['title'])
            # print("Updated: {}".format(course))

        # print("Num {}".format(numSections(conn, query, kind)))
        return courses  

'''Input: course cnum and title. Output: list of dictionaries containing all
the information about each course section in sorted order'''
def getSections(conn, cnum, title): 
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT cnum, title, sem, yr, prof, cid
                    FROM course 
                    WHERE cnum = %s and title = %s
                    ORDER BY yr''', [cnum, title])
                    # sort by semester too? 
    sections = curs.fetchall()
    return sections

'''Input: user query and kind. Output: number of sections fitting that query'''
def numSections(conn, query, kind):
    curs = dbi.cursor(conn)
    if (kind == "title" or kind == "dep" or kind == "cnum"):
        curs.execute('''SELECT count(*) 
                        FROM course
                        WHERE {} like %s'''.format(kind), ['%' + query + '%'])
        num = curs.fetchone()
        return num[0]

'''Input: user query and kind (for a search result that returns exactly one course).
Output: cid of unique section fitting that query'''
def getOneResult(conn, query, kind):
    curs = dbi.dict_cursor(conn)
    if (kind == "title" or kind == "dep" or kind == "cnum"):
        curs.execute('''SELECT cid, cnum
                        FROM course
                        WHERE {} like %s'''.format(kind), ['%' + query + '%']
                    ) 
        section = curs.fetchone()
        return section['cid']

# Safiya's functions:
def getCourseInfo():
    title = request.form.get('course-title')
    dep = request.form.get('course-dept')
    cnum = request.form.get('course-num')
    crn = request.form.get('course-crn')
    web = request.form.get('course-website')
    yr = request.form.get('course-year')
    sem = request.form.get('course-sem')
    prof = request.form.get('course-prof')
    return [title, dep, cnum, crn, web, yr, sem, prof]

def insertCourse(val):
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    curs.execute('''
    INSERT into course(title, dep, cnum, crn, web, yr, sem, prof)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)''', 
    [val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7]])
    conn.commit()
    return [val[0], val[5], val[6], val[7]]

def getCID(val):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select cid from course where title = %s and yr= %s and sem= %s 
    and prof = %s''',
    [val[0], val[1], val[2], val[3]])
    result = curs.fetchone()
    return result['cid']

def getRecommended():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT course.cid, course.title 
    FROM course LIMIT 3''')
    results = curs.fetchall()
    return results

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
def saveToDB(x, aFile):
    try:
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute(
            '''insert into syllabi(cid, filename) 
               values (%s, %s)''', [x, aFile])
        conn.commit()
        flash('Upload successful')
    except Exception as err:
        flash('Upload failed {why}'.format(why=err))
        
if __name__ == '__main__':
   dbi.cache_cnf()   # defaults to ~/.my.cnf
   dbi.use('syllabo_db')
   conn = dbi.connect()
#    print(getCourses(conn, "databases", "title"))
   print(getOneResult(conn, 'databases', 'title'))