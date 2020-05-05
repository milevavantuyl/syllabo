"Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl"
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import os
import cs304dbi as dbi
import functions

UPLOAD_FOLDER = 'upload_folder'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

from flask_cas import CAS

CAS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
# Doesn't redirect properly, but not a problem to fix--it is okay:
app.config['CAS_AFTER_LOGOUT'] = 'after_logout'

# fake bNum for now 4/23/2020 draft version - pre login implementation
FOObNum = '20000000'
@app.route('/')
def index():
    return render_template('home.html', courses = functions.getRecommended())

@app.route('/create/', methods=['GET','POST'])
def createCourse():
    if request.method == 'GET':
        return render_template('create_course.html')
    else:
        values = functions.getCourseInfo()
        courseInfo = functions.insertCourse(values)
        cid = functions.getCID(courseInfo)
        flash('Your updates have been made, insert another course!')
        return redirect(url_for('uploadSyllabus', n = cid))

@app.route('/upload/<int:n>', methods=['GET','POST'])
def uploadSyllabus(n):
    if request.method == 'GET':
        return render_template('syl_upload.html')
    else:
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
        if file and functions.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        functions.saveToDB(n, file.filename)
        return render_template('home.html', courses = functions.getRecommended())

@app.route('/explore/', methods = ['GET'])
def explore(): 
    conn = dbi.connect()
    allCourses = functions.getAllCourses(conn)
    return render_template('search_results.html', 
                courses = allCourses, query = None)
    
@app.route('/search/', methods = ['GET']) 
def search(): 
    conn = dbi.connect()

    search = request.args.get('search')
    kind = request.args.get('type') 

    # Check kind type is valid
    if (kind == "title" or kind == "dep" or kind == "cnum" or kind == "prof"):
        if (kind == "prof"):
            courseResultsByProf = functions.getCoursesByProf(conn, search)
        else: 
            courseResults = functions.getCourses(conn, search, kind)
        numSections = functions.numSections(conn, search, kind)

        # No results: redirect user to create a new course
        if numSections == 0:
            flash ('No results for {} in the database.'.format(search))
            return redirect(url_for('createCourse')) 

        # One result: redirect user to specific course page
        elif numSections == 1: 
            cid = functions.getOneResult(conn, search, kind)
            return redirect(url_for('showCourse', cid = cid))
                
        # Multiple results: display all the results
        else: 

            if (kind == "prof"):
                return render_template('prof_search_results.html', 
                profs=courseResultsByProf, query = search)
            else: 
                return render_template('search_results.html', 
                courses = courseResults, query = search)
        
    # Invalid kind type
    else: 
        flash ('Invalid value entered for type field.')
        return redirect(url_for('createCourse')) 

@app.route('/course/<cid>', methods=['GET','POST'])
def showCourse(cid):
    basics = functions.getBasics(cid)
    if request.method == 'GET':
        avgRatings = functions.getAvgRatings(cid)
        comments = functions.getComments(cid)
        return render_template('course_page.html', basics = basics, avgRatings = avgRatings, comments=comments)
    elif request.method == 'POST':
        #user is rating (which includes commenting) the course.
        uR = request.form.get('usefulRate')
        dR = request.form.get('diffRate')
        rR = request.form.get('relevRate')
        eR = request.form.get('expectRate')
        hW = request.form.get('hoursWk')
        comment = request.form.get('new_comment')
        functions.makeRatings(FOObNum, cid, rR, uR, dR, eR, hW, comment)
        #have to recalculate the ratings and fetch the comments again
        avgRatings = functions.getAvgRatings(cid)
        comments = functions.getComments(cid)
        #now we render the page again
        return render_template('course_page.html', basics = basics, avgRatings = avgRatings, comments=comments)

@app.route('/course/<cid>/update', methods=['GET','POST'])
def update(cid):
    if request.method == 'GET':
        flash("This feature coming soon!")

# Log in CAS stuff:
@app.route('/logged_in/')
def logged_in():
    flash('successfully logged in!')
    return redirect( url_for('index') )

@app.route('/after_logout/')
def after_logout():
    flash('successfully logged out!')
    return redirect( url_for('index') )

application = app

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1950):
            print('For CAS, choose a port from 1943 to 1950')
            sys.exit()
    else:
        port=os.getuid()
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
