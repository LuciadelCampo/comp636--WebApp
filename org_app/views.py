from flask import Flask, render_template, redirect, url_for
from flask import request
import psycopg2
import uuid
from . import connect

dbconn = None

app = Flask(__name__)

#connection requirements
def getCursor():
    global dbconn
    if dbconn == None:
        conn = psycopg2.connect(dbname=connect.dbname, user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, port=connect.dbport)
        conn.autocommit = True
        dbconn = conn.cursor()
        return dbconn
    else:
        return dbconn

#to generate a unique identifer
def genID():
    return uuid.uuid4().fields[1]

#YOUTH INTERFACE:home page with list of groups
@app.route("/")
def youth():
    cur = getCursor()
    cur.execute("select groupid, groupname as Group from activitygroup;")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('youth.html',dbresult=select_result,dbcols=column_names)

#YOUTH INTERFACE: list of activities per group
@app.route("/activityNight", methods=['GET'])
def getactivityNight():
    groupid = request.args.get("groupid")
    cur = getCursor()
    cur.execute("select groupid, activitynightid, nighttitle from activitynight where groupid=%s",(groupid,))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('activityNight.html',dbresult=select_result,dbcols=column_names)

#YOUTH INTERFACE: list of members per activity
@app.route("/activityMembers", methods=['GET'])
def getactivityMembers():
    memberid = request.args.get("memberid")
    cur = getCursor()
    cur.execute("select memberid, activitynightid, name, surname from currentgroupmember where activitynightid=%s",(memberid,))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('activityMembers.html',dbresult=select_result,dbcols=column_names)

#YOUTH INTERFACE: mark presence
@app.route('/markAttendance', methods=['GET','POST'])
def markAttendance():
    if request.method == 'POST':
        memberid = request.form.get('memberid')
        activitynightid = request.form.get('activitynightid')
        attendancestatus = request.form.get('attendancestatus')
        cur = getCursor()
        cur.execute("UPDATE attendance SET activitynightid=%s, attendancestatus=%s where memberid=%s",(activitynightid,attendancestatus,str(memberid),))
        return redirect("/")
    else:
        id = request.args.get('memberid')
        if id == '':
            return redirect("/")
        else:
            cur = getCursor()
            cur.execute("SELECT * FROM attendance where memberid=%s",(str(id),))
            select_result = cur.fetchone()
            return render_template('attendanceForm.html',dbresult = select_result)



#ADULT INTERFACE: list of leaders
@app.route("/adultLogin")
def adultlogin():
    cur = getCursor()
    cur.execute("select distinct groupid, name, surname, memberid from currentgroupmember where adultleader = True;")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('adultLogin.html',dbresult=select_result,dbcols=column_names)

@app.route("/addNewActivity" , methods=['GET','POST'])
def addNewActivity():
    if request.method == 'POST':
        id= genID()
        groupid = request.form.get('groupid')
        nighttitle = request.form.get('nighttitle')
        description = request.form.get('description')
        activitynightdate = request.form.get('activitynightdate')
        cur = getCursor()
        cur.execute("INSERT INTO activitynight(activitynightid, groupid, nighttitle, description, activitynightdate) VALUES (%s,%s,%s,%s,%s);",(str(id),groupid,nighttitle,description,activitynightdate,))
        cur.execute("SELECT * FROM activitynight where activitynightid=%s",(str(id),))
        select_result = cur.fetchall()
        column_name = [desc[0] for desc in cur.description]
        return render_template('addNewActivity.html',dbresult=select_result,dbcol=column_name)
    else:
        return render_template('addNewActivityform.html')

#ADULT INTERFACE: functions add or list of members to update
@app.route("/adultFunctions/", methods=['GET'])
def adultFunctions():
    groupid = request.args.get("groupid")
    cur = getCursor()
    cur.execute("select distinct groupid, name, surname, memberid from currentgroupmember where groupid=%s;",(groupid,))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('adultFunctions.html',dbresult=select_result,dbcols=column_names)

####ADULT INTERFACE: edit/update attendance info
@app.route('/updateInformation/', methods=['GET','POST'])
def updateInformation():
    if request.method == 'POST':
        memberid = request.form.get('memberid')
        activitynightid = request.form.get('activitynightid')
        attendancestatus = request.form.get('attendancestatus')
        notes = request.form.get('notes')
        cur = getCursor()
        cur.execute("UPDATE attendance SET activitynightid=%s, attendancestatus=%s, notes=%s where memberid=%s",(activitynightid,attendancestatus,notes,str(memberid),))
        return redirect("/adultlogin")
    else:
        id = request.args.get('memberid')
        if id == '':
            return redirect("/adultlogin")
        else:
            cur = getCursor()
            cur.execute("SELECT * FROM attendance where memberid=%s",(str(id),))
            select_result = cur.fetchone()
            return render_template('updateInformationform.html',dbresult = select_result)