#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import sys
import time
import subprocess
import sys
import logging


def OutputStream(loutput):
    # Poll process for new output until finished
    while True:
        nextline = loutput.stdout.readline()
        if nextline == '' and loutput.poll() is not None:
            break
        sys.stdout.write(nextline.decode('utf-8'))
        sys.stdout.flush()
        return


def SubMProc(*cmds):
    count = 1
    for cmd in cmds:
        if count == 1:
            loutput = 'output' + '_' + str(count)
            loutput = subprocess.Popen(cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        else:
            noutput = 'output' + '_' + str(count)
            noutput = subprocess.Popen(cmd,
                                       shell=True,
                                       stdin=loutput.stdout,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            loutput = noutput
        count = count + 1
    out, err = loutput.communicate()
    return(out, err, loutput.returncode)


def initialize_logging(logfile):
    """
       Define Logging - set up logging to file
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s: %(filename)s: %(levelname)s: %(message)s',
        datefmt='%m-%d-%y %H:%M:%S',
        filename=logfile,
        filemode='w')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')

    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, define a couple of other loggers which might represent areas in your
    # application:
    log = logging.getLogger(__name__)

    return log


class Tag:
    """
    Defines the tags for each message shown in the output.
    """
    bold = "\033[1m"

    green = "\033[32m"
    red = "\033[31m"
    yellow = "\033[33m"

    bold_green = bold + green
    bold_red = bold + red
    bold_yellow = bold + yellow

    end = "\033[0m"

    failed = "[{0}FAILED{1}]".format(bold_red, end)
    passed = "[{0}PASSED{1}]".format(green, end)
    exception = "[{0}EXCEPTION{1}]".format(bold_red, end)
    info = "[{0}INFO{1}]".format(green, end)


class ConnPool(object):
    """
    create a pool when connect mysql, which will decrease the time spent in
    request connection, create connection and close connection.
    """
    def __init__(self, host="172.0.0.1", port="3306", user="root",
                 password="g00gledd", database="dashboard", pool_name="dbapool",
                 pool_size=5):
        res = {}
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

        res["host"] = self._host
        res["port"] = self._port
        res["user"] = self._user
        res["password"] = self._password
        res["database"] = self._database
        self.dbconfig = res
        self.pool = self.create_pool(pool_name="dbaapi", pool_size=10)

    def create_pool(self, pool_name="mypool", pool_size=3):
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **self.dbconfig)
        return pool

    def close(self, conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn:
        :param cursor:
        :return:
        """
        cursor.close()
        conn.close()

    def execute(self, sql, args=None, commit=False):
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res

    def executemany(self, sql, args, commit=False):
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        cursor.executemany(sql, args)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res


