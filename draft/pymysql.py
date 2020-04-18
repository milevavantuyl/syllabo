'''Emily Mattlin, Sarah Pardo, Safiya Sirota, Mileva Van Tuyl
pymysql functions for Syllabo'''
import sys
import pymysql
import pymysql.constants.ER
import syllabo_db as dbi

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
    SELECT AVG(relevRate), AVG(usefulRate), AVG(diffRate), AVG(expectRate), AVG(hoursWk)
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
    SELECT username, comment  
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

    

if __name__ == '__main__':
   dbi.cache_cnf()   # defaults to ~/.my.cnf
   dbi.use('syllabo_db')
