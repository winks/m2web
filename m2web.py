# -*- coding: utf-8 -*-
    """
    m2web
    ~~~~~

    A web frontend for mongrel2 configs.
    Shamelessly based on flaskr.

    :license: BSD
    """

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

M2WEB_DB = '../deployment/test.sqlite'
M2WEB_DEBUG = True
M2WEB_BASE = '/py'
SECRET_KEY = "asdfgh"

TBL = {
    'server'    : ['id','default_host','port','pid_file','chroot','access_log','error_log'],
    'host'      : ['id','server_id','maintenance','name','matching'],
    'handler'   : ['id','send_spec','send_ident','recv_spec','recv_ident'],
    'proxy'     : ['id','addr','port'],
    'directory' : ['id','base','index_file','default_ctype'],
    'route'     : ['id','path','reversed','host_id','target_id','target_type'],
    'setting'   : ['id','key','value'],
}

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('M2WEB_SETTINGS', silent=True)

def connect_db():
    """
    Connects to sqlite.
    """
    return sqlite3.connect(app.config['M2WEB_DB'])

def assoc(row, fields):
    """
    Why the hell do I need to implement fetchAssoc myself?
    """
    i = 0
    ret = {}
    for f in fields:
        ret[f] = row[i]
        i = i+1
    return ret

def singularize(list):
    """
    Ghetto conversion of plural to singular.
    """
    new = []
    for item in list:
        if item[-3:] == 'ies':
            item = item[:-3] + 'y'
        elif item[-1:] == 's':
            item = item[:-1]
        new.append(item)
    return new

def pluralize(list):
    """
    Ghetto conversion of singular to plural.
    """
    new = []
    for item in list:
        if item[-1:] == 'y':
            item = item[:-1] + 'ies'
        else:
            item = item + 's'
        new.append(item)
    return new

def db_request(fields, table):
    """
    Grab a dict from a database.
    """
    f = ','.join(fields)
    sql = 'select %s from %s' % ( f, table )
    cur = g.db.execute(sql)
    entries = [dict(assoc(row,fields)) for row in cur.fetchall()]
    return entries


@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route(app.config['M2WEB_BASE']+"/")
def index():
    """
    Show the index page
    """
    var = dict(
        base=app.config['M2WEB_BASE'],
        tables=pluralize(app.config['TBL']) )
    return render_template('index.html', var=var)

@app.route(app.config['M2WEB_BASE']+"/show/<pagename>")
def show(pagename):
    """
    Display contents of tables.
    """
    page = singularize([pagename])[0]
    if not app.config['TBL'].has_key(page):
        return render_template('error.html', var=pagename)
    fields = app.config['TBL'][page]
    entries = db_request(fields, page)
    file = 'show_%s.html' % (pagename)
    return render_template(file, entries=entries)


if __name__ == "__main__":
    app.run(debug=True)
