"Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl"
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import cs304dbi as dbi
import functions
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

# import pymysql as dbi

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
    return render_template('main.html',title='Syllabo')

@app.route('/create/')
def create():
    return render_template('create_course.html',title='Syllabo')

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/courses/<cid>', methods=['GET','POST'])
def showCourse(cid):
    if request.method == 'GET':
        basics = db.getBasics(cid)
        avgRatings = db.getAvgRatings(cid)
        comments = db.getComments(cid)
        print('basics: ')
        print(basics)
        print('avgRatings: ')
        print(avgRatings)
        print('comments: ')
        print(comments)
        return render_templates('course_page.html', title=basics['title'],
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
            avgRatings = db.getAvgRatings(cid)
            comments = db.getComments(cid)
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
