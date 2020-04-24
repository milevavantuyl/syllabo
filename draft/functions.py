'''Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl
pymysql functions for Syllabo'''
# import sys
# import pymysql
# import pymysql.constants.ER
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import cs304dbi as dbi

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


<<<<<<< HEAD

=======
>>>>>>> sarah
# Mileva's functions:

def getAllSections(query, kind):
    if (kind == "title"):
        return (getByTitle(query))
    elif (kind == "dep"):
        return (getByDepartment(query))
    else:
        return (getByCnum(query))

def getByTitle(query):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT cnum, title, sem, yr, prof, cid
                    FROM course 
                    WHERE title like %s''', ['%' + query + '%']) 
                    # question substitute title w/ variable
    courses = curs.fetchall()
    return courses

def getByDepartment(query):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT cnum, title, sem, yr, prof, cid
                    FROM course 
                    WHERE dep like %s''', ['%' + query + '%']) 
                    # question substitute dep w/ variable
    courses = curs.fetchall()
    return courses

def getByCnum(query):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT cnum, title, sem, yr, prof, cid 
                    FROM course 
                    WHERE cnum like %s''', ['%' + query + '%']) 
                    # question substitute cnum w/ variable
    courses = curs.fetchall()
    return courses

def getCourses(courses):
    ''' Returns a list of dictionaries with the cnum and titles of all the courses'''
    uniqueCourses = []
    cnums = set()

    for course in courses: 
        cnum = course['cnum']
        title = course.get('title', 'NULL')

        # Add course information (if not already present)
        # Assumption: Course title is based on first found instance of course
        if cnum not in cnums: 
            cnums.add(cnum)
            uniqueCourses.append({'cnum': cnum, 'title': title})

    # Sorts them in alphabetical order by cnum
    uniqueCourses.sort(key = lambda course: course['cnum'].lower())

    return uniqueCourses

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

def fileUpload():
    try:
        f = request.files['file']
        pdf = f.read()
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute(
            '''insert into course(syl) values (%s) where title = %s and
            yr = %s and sem = %s and prof = %s''',
            [pdf, title, yr, sem, prof])
        conn.commit()
        flash('Upload successful')
    except Exception as err:
        flash('Upload failed {why}'.format(why=err))
        
if __name__ == '__main__':
   dbi.cache_cnf()   # defaults to ~/.my.cnf
   dbi.use('syllabo_db')
