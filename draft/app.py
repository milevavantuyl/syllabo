"Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl"
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import cs304dbi as dbi
import functions

app = Flask(__name__)

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('home.html', courses = functions.getRecommended())

@app.route('/create/', methods=['GET','POST'])
def createCourse():
    if request.method == 'GET':
        return render_template('create_course.html')
    else:
        values = functions.getCourseInfo()
        functions.insertCourse(values)
        flash('Your updates have been made, insert another course!')
        return redirect(url_for('createCourse'))

@app.route('/search/', methods = ['GET']) 
def search(): 
    search = request.args.get('search')
    kind = request.args.get('type')

    allCourses = functions.getAllCourses(search, kind)
    print(allCourses)

    # Sort these alphabetically by cnum
    courses = functions.getCourses(allCourses)
    print(courses)

    sections = [{'CS 230': [{'cnum': 'CS 230', 'title': 'Data Structures', 'sem': 'Fall', 'yr': 2019, 'prof': 'Takis Metaxas', 'cid': 7}]}]

    # No results: redirect user to create a new course
    if len(allCourses) == 0:
        flash ('No results for {} in the database.'.format(search))
        return redirect(url_for('createCourse')) 

    # One result: redirect user to specific course page
    elif len(allCourses) == 1: 
        return redirect(url_for('showCourse', cid = allCourses[0]['cid']))
    
    # Multiple results: display all the results
    else: 
        return render_template('search_results.html', 
        courses = courses, allCourses = allCourses, query = search)

@app.route('/course/<cid>', methods=['GET','POST'])
def showCourse(cid):
    if request.method == 'GET':
        basics = functions.getBasics(cid)
        avgRatings = functions.getAvgRatings(cid)
        comments = functions.getComments(cid)
        # print('basics: ')
        # print(basics)
        # print('avgRatings: ')
        # print(avgRatings)
        # print('comments: ')
        # print(comments)
        return render_template('course_page.html', title=basics['title'],
            cnum=basics['cnum'], dep=basics['dep'], prof=basics['prof'],
            yr=basics['yr'], sem=basics['sem'], crn=basics['crn'], syl=basics['syl'],
            web=basics['web'], usefullRate=avgRatings['usefullRate'], 
            diffRate=avgRatings['diffRate'], relevRate=avgRatings['relevRate'], 
            expectRate=avgRatings['expectRate'], hoursWk=avgRatings['hoursWk'],
            comments=comments)
    elif request.method == 'POST':
        #user is rating (which includes commenting) the course.
        action = request.form.get("submit")
        if action == 'rate':
            uR = request.form.get('usefulRate')
            dR = request.form.get('diffRate')
            rR = request.form.get('relevRate')
            eR = request.form.get('expectRate')
            hW = request.form.get('hoursWk')
            comment = request.form.get('new_comment')
            makeRatings(bNum, cid, rR, uR, dR, eR, hW, comment)
            #have to recalculate the ratings and fetch the comments again
            avgRatings = functions.getAvgRatings(cid)
            comments = functions.getComments(cid)
            #now we render the page again
            return render_templates('course_page.html', title=basics['title'],
            cnum=basics['cnum'], dep=basics['dep'], prof=basics['prof'],
            yr=basics['yr'], sem=basics['sem'], crn=basics['crn'], syl=basics['syl'],
            web=basics['web'], usefullRate=avgRatings['usefullRate'], 
            diffRate=avgRatings['diffRate'], relevRate=avgRatings['relevRate'], 
            expectRate=avgRatings['expectRate'], hoursWk=avgRatings['hoursWk'],
            comments=comments)

@app.route('/courses/<cid>/update', methods=['GET','POST'])
def updateCourse(cid):
    if request.method == 'GET':
        print("hello")

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    return render_template('testform.html')


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    # the following database code works for both PyMySQL and SQLite3
    dbi.cache_cnf()
    dbi.use('syllabo_db')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    # the following query works for both MySQL and SQLite
    curs.execute('select current_timestamp as ct')
    row = curs.fetchone()
    ct = row['ct']
    print('connected to Syllabo DB at {}'.format(ct))
    app.debug = True
    app.run('0.0.0.0',port)
