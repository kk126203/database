#!/usr/bin/env python2.7
#pip install sqlalchemy

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://yh2796:8703@w4111vm.eastus.cloudapp.azure.com/w4111"

engine = create_engine(DATABASEURI)

@app.before_request

def before_request():
  try:
    g.conn = engine.connect()
    print "connection got!"
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/signin')
def signin():
  return render_template("login.html")

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/query1')
def query1():
  try:
    cur = g.conn.execute("SELECT A.name FROM actors A, Movies M, Star_in S WHERE A.pid=S.pid AND M.mid=S.mid AND M.BoxOffice > (SELECT AVG(M1.BoxOffice) FROM Movies M1);")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m, data2='actors')
    return render_template("result.html",**context)
  except:
    return render_template("index.html", [])

@app.route('/query2')
def query2():
  try:
    cur = g.conn.execute("SELECT tmp1.name, tmp1.address FROM (SELECT p1.name, p1.address, p1.start_time FROM playin p1 LEFT OUTER JOIN movies m1 ON p1.mid=m1.mid WHERE m1.title='Forrest Gump')AS tmp1, (SELECT p2.name, p2.address, p2.start_time FROM playin p2 LEFT OUTER JOIN movies m2 ON p2.mid=m2.mid WHERE m2.title='Lucy')AS tmp2 WHERE tmp1.name=tmp2.name AND tmp1.address=tmp2.address AND tmp1.start_time=tmp2.start_time;")
    t = ['theatres']
    #cur = g.conn.execute("SELECT * from theatres;")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m,data2= t)
    return render_template("result.html",**context)
    # m = []
    # title = []
    # title.append('name')
    # title.append('address')
    # for rst in cur:
    #   instance = []
    #   instance.append(rst['name'])
    #   instance.append(rst['address'])
    #   m.append(instance)
    # cur.close()
    # print m
    # context = dict(data = m, t=title)
    # return render_template("details.html",**context)
  except:
    return render_template("index.html", [])



@app.route('/query3')
def query3():
  try:
    cur = g.conn.execute("SELECT W1.name, W1.nationality FROM Writers W1, Write W2, ( SELECT tmp1.mid FROM (SELECT c1.mid, COUNT(*) AS num_of_awards FROM confer c1 GROUP BY c1.mid)AS tmp1 WHERE tmp1.num_of_awards > ( SELECT AVG(num_of_awards) FROM ( SELECT c1.mid, COUNT(*) AS num_of_awards FROM confer c1 GROUP BY c1.mid)AS tmp))AS tmp2 WHERE W1.pid=W2.pid AND W2.mid=tmp2.mid;")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m, data2='writers')
    return render_template("result.html",**context)
  except:
    return render_template("index.html", [])

@app.route('/login', methods=['GET','POST'])
def login():
  query_id = request.form['id']
  query_password = request.form['password']
  #print session
  try:
    name, passw = g.conn.execute(
      'SELECT usr_name, password from users WHERE usr_name=%s;',(query_id, )
    ).fetchone()
    if passw != query_password:
      return render_template('login.html', error='Wrong password.')
    # session['username'] = query_id
    # print session['username']
    return render_template('index.html', name=query_id, status=true)
  except:
    return render_template('login.html', error='User not exist.')

@app.route('/register', methods=['POST'])
def register():
  insert_name = request.form['id']
  insert_password = request.form['password']
  comedy = request.form['comedy']
  action = request.form['action']
  drama = request.form['drama']
  try:
    g.conn.execute(
      'INSERT INTO users VALUES (DEFAULT, %s, %s, %s, %s, %s);', 
      (insert_name, insert_password, comedy, action, drama)
    )
    return render_template('index.html', name=insert_name, status=true)
  except: # user already exist
    return render_template('login.html', error='User already exist.')

@app.route('/theatre')
def theatre():
    cur = g.conn.execute("SELECT * from theatres;")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m,data2= 'theatres')
    return render_template("result.html",**context)


@app.route('/star')
def star():
    cur = g.conn.execute("SELECT * from actors;")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m, data2= 'actors', data3=true)
    return render_template("result.html",**context)

@app.route('/profile',methods=['POST'])
def profile():
    insert_name = request.form.get('username')
    print insert_name
    c, a, d = g.conn.execute(
      "SELECT comedy, action, drama from users WHERE usr_name=%s;",(insert_name)
    ).fetchone()
    print "execute suc"
    print c, a, d
    m=[]
    param = 'Drama'
    if (c>a)and(c>d):
      param = 'comedy'
    elif (a>c)and(a>d):
      param = 'Action'
    else:
      pass

    print param

    cur = g.conn.execute("SELECT title FROM movies WHERE genre=%s;",(param))
    for rst in cur:
        m.append(rst['title'])
    cur.close()
    print m
    context = dict(data1=m, data2='movies')
    return render_template("result.html",**context)   

@app.route('/director')
def director():
    cur = g.conn.execute("SELECT * from directors;")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m, data2='directors', data3=true)
    return render_template("result.html",**context)

@app.route('/writer')
def writer():
    cur = g.conn.execute("SELECT * from writers;")
    m = []
    for rst in cur:
        m.append(rst['name'])
    print m
    cur.close()
    context = dict(data1 = m, data2= 'writers', data3=true)
    return render_template("result.html",**context)

@app.route('/gender', methods=['POST'])
def gender():
    mylist = request.form['gender'].split(',')
    gender = mylist[0]
    table_name = mylist[1]
    print gender
    print table_name

    if table_name == 'writers':
      sql = 'SELECT * from writers WHERE gender=%s;'
      data = (gender)
      cur = g.conn.execute(sql, data)
      m = []
      for rst in cur:
        m.append(rst['name'])
      print m
      cur.close()
      context = dict(data1 = m, data2= table_name, data3=true)
      return render_template("result.html",**context)
    elif table_name == 'actors':
      sql = 'SELECT * from actors WHERE gender=%s;'
      data = (gender)
      cur = g.conn.execute(sql, data)
      m = []
      for rst in cur:
        m.append(rst['name'])
      print m
      cur.close()
      context = dict(data1 = m, data2= table_name, data3=true)
      return render_template("result.html",**context)
    elif table_name == 'directors':
      sql = 'SELECT * from directors WHERE gender=%s;'
      data = (gender)
      cur = g.conn.execute(sql, data)
      m = []
      for rst in cur:
        m.append(rst['name'])
      print m
      cur.close()
      context = dict(data1 = m, data2= table_name, data3=true)
      return render_template("result.html",**context)

    context = dict(data1 = [], data2= table_name, data3=true)
    return render_template("result.html",**context)


@app.route('/details', methods=['POST'])
def details():
    mylist = request.form['Pname'].split(',')
    query_name = mylist[0]
    table_name = mylist[1]
    print table_name
    print query_name
    m = []
    title = []
    title.append('name')
    title.append('gender')
    title.append('nationality')
    title.append('type')

    if table_name=='writers':
      cur = g.conn.execute("SELECT * FROM writers WHERE name=%s;",query_name)
      instance = []
      for rst in cur:
        instance.append(rst['name'])
        instance.append(rst['gender'])
        instance.append(rst['nationality'])
        instance.append(rst['type'])
        m.append(instance)
      cur.close()
    elif table_name=='actors':
      cur = g.conn.execute("SELECT * FROM actors WHERE name=%s;",query_name)
      instance = []
      for rst in cur:
        instance.append(rst['name'])
        instance.append(rst['gender'])
        instance.append(rst['nationality'])
        instance.append(rst['type'])
        m.append(instance)
      cur.close()

    elif table_name=='movies':
      cur = g.conn.execute("SELECT * FROM movies WHERE title=%s;",query_name)
      title = []
      title.append('title')
      title.append('language')
      title.append('genre')
      title.append('year')
      for rst in cur:
        instance = []
        instance.append(rst['title'])
        instance.append(rst['language'])
        instance.append(rst['genre'])
        instance.append(rst['year'])
        m.append(instance)
      cur.close()

    elif table_name=='directors':
      cur = g.conn.execute("SELECT * FROM directors WHERE name=%s;",query_name)
      instance = []
      for rst in cur:
        instance.append(rst['name'])
        instance.append(rst['gender'])
        instance.append(rst['nationality'])
        instance.append(rst['type'])
        m.append(instance)
      cur.close()

    elif table_name=='movies':
      cur = g.conn.execute("SELECT * FROM movies WHERE title=%s;",query_name)
      title = []
      title.append('title')
      title.append('language')
      title.append('genre')
      title.append('year')
      instance = []
      for rst in cur:
            instance.append(rst['title'])
            instance.append(rst['language'])
            instance.append(rst['genre'])
            instance.append(rst['year'])
            m.append(instance)
      cur.close()
      print m
    else:
      cur = g.conn.execute("SELECT * from theatres WHERE name=%s;",(query_name))
      title = []
      title.append('name')
      title.append('address')
      instance = []
      for rst in cur:
            instance.append(rst['name'])
            instance.append(rst['address'])
            m.append(instance)
            print m
      cur.close()

    print "find well -- details"
    context = dict(t=title, data = m)
    return render_template("details.html",**context)


@app.route('/Search', methods=['POST'])
def search():
    query_name = request.form['Mname']
    m = []
    indicator = 0
    if query_name=="all":
      cur = g.conn.execute("SELECT * from movies;")
      for rst in cur:
        m.append(rst['title'])
      cur.close()
      context = dict(data1 = m,data2 = 'movies')
      return render_template("result.html",**context)
    else:
      try:
          cur = g.conn.execute("SELECT * from movies WHERE title=%s;",(query_name))
          title = []
          title.append('title')
          title.append('language')
          title.append('genre')
          title.append('year')
          instance = []
          for rst in cur:
            instance.append(rst['title'])
            instance.append(rst['language'])
            instance.append(rst['genre'])
            instance.append(rst['year'])
            m.append(instance)
          cur.close()
          print m
          context = dict(t = title,data = m)
          return render_template("details.html",**context)
      except Exception, e:
          m=[]
          return render_template("index.html")
    

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()