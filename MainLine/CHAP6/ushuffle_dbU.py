#!/usr/bin/env python

from distutils.log import warn as printf
import os
from random import randrange as rand

from IPython.lib.security import passwd

if isinstance(__builtins__, dict) and 'raw_input' in __builtins__:
    scanf = raw_input
elif hasattr(__builtins__, 'raw_input'):
    scanf = raw_input
else:
    scanf = input

COLSIZ = 10
FIELDS = ('login', 'userid', 'projid')
RDBMSs = {'s': 'sqlite', 'm': 'mysql', 'g': 'gadfly'}
DBNAME = 'test'
DBUSER = 'root'
DB_EXC = None
NAMELEN = 16

tformat = lambda s: str(s).title().ljust(COLSIZ)
cformat = lambda s: s.upper().ljust(COLSIZ)


def setup():
    return RDBMSs[scanf('''
    Choose a database system:
    
    (M)ySQL
    (G)adfly
    (S)QLite
    
    Enter choice: ''').strip().lower()[0]]


def connect(db, DBNAME):
    global DB_EXC
    dbDir = '%s_%s' % (db, DBNAME)
    if db == 'sqlite':
        try:
            import sqlite3
        except ImportError:
            try:
                from pysqlite2 import dbapi2 as sqlite3
            except ImportError:
                return None

        DB_EXC = sqlite3
        if not os.path.isdir(dbDir):
            os.mkdir(dbDir)
        cxn = sqlite3.connect(os.path.join(dbDir, DBNAME))

    elif db == 'mysql':
        try:
            import MySQLdb
            import _mysql_exceptions as DB_EXC
            try:
                cxn = MySQLdb.connect(db=DBNAME)
            except DB_EXC.OperationalError:
                try:
                    cxn = MySQLdb.connect(user=DBUSER, passwd='root')
                    cxn.query('CREATE DATABASE %s' % DBNAME)
                    cxn.commit()
                    cxn.close()
                    cxn = MySQLdb.connect(db=DBNAME)
                except DB_EXC.OperationalError:
                    return None
        except ImportError:
            try:
                import pymysql
            except ImportError:
                return None
            DB_EXC = pymysql
            try:
                cxn = pymysql.connect(user=DBUSER, password='root', db=DBNAME)
            except DB_EXC.err.InternalError:
                try:
                    cxn = pymysql.connect(user=DBUSER, password='root')
                    cxn.query('CREATE DATABASE %s;' % DBNAME)
                    cxn.commit()
                    cxn.close()
                    cxn = pymysql.connect(db=DBNAME, user=DBUSER, password='root')
                except DB_EXC.err.OperationalError:
                    return None

    else:
        return None
    return cxn


def create(cur):
    try:
        cur.execute('''
        CREATE TABLE users (
        login VARCHAR(%d),
        userid INTEGER ,
        projid INTEGER )''' % NAMELEN)
    except DB_EXC.OperationalError:
        drop(cur)
        create(cur)


drop = lambda cur: cur.execute('DROP TABLE users')

NAMES = (
    ('aalsk', 1234), ('asfaal', 1239), ('jdfaf', 9242),
    ('kaxvx', 8312), ('asjfko', 1254), ('jgvbn', 1591),
    ('nansk', 1224), ('ahfnal', 1249), ('jnfnf', 9542),
    ('k9kvx', 8912), ('osofko', 1904), ('j2vbn', 1501),
)


def randName():
    pick = set(NAMES)
    while pick:
        yield pick.pop()


def insert(cur, db):
    if db == 'sqlite':
        cur.executemany("INSERT INTO users VALUES(?,?,?)", [(who, uid, rand(1, 5)) for who, uid in randName()])
    elif db == 'mysql':
        cur.executemany("INSERT INTO users VALUES(%s, %s, %s)", [(who, uid, rand(1, 5)) for who, uid in randName()])


getRC = lambda cur: cur.rowcount if hasattr(cur, 'rowcount') else -1


def update(cur):
    fr = rand(1, 5)
    to = rand(1, 5)
    cur.execute(
        "UPDATE users SET projid=%d WHERE projid=%d" % (to, fr)
    )
    return fr, to, getRC(cur)


def delete(cur):
    rm = rand(1, 5)
    cur.execute('DELETE FROM users WHERE projid=%d' % rm)
    return rm, getRC(cur)


def dbDump(cur):
    cur.execute('SELECT * FROM users')
    printf('\n%s' % ''.join(map(cformat, FIELDS)))
    for data in cur.fetchall():
        printf(''.join(map(tformat, data)))


def main():
    db = setup()
    printf('*** Connect to %r database' % db)
    cxn = connect(db, DBNAME)
    if not cxn:
        printf("ERROR: %r not supported or unreachable , exit" % db)
        return
    cur = cxn.cursor()

    printf("\n*** Creating users table")
    create(cur)

    printf("\n*** Inserting name into users table")
    insert(cur, db)
    dbDump(cur)

    printf("\n*** Randomly moving folks")
    fr, to, num = update(cur)
    printf('\t(%d users moved) from (%d) to (%d)' % (num, fr, to))
    dbDump(cur)

    printf("\n*** Randomly choosing group")
    rm, num = delete(cur)
    printf('\t(group #%d; %d users removed)' % (rm, num))
    dbDump(cur)

    printf("\n*** Dropping users table")
    drop(cur)
    printf("\n*** Close cxns")
    cur.close()
    cxn.commit()
    cxn.close()


if __name__ == '__main__':
    main()
