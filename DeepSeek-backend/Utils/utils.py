import hashlib
import os
import sqlite3
import time

from Utils.text_algos import Jaccrad, Dice, get_word_vector, Cos_dist
from VideoProc.video_cmp import compare, opti_compare
from VideoProc.video_reproc import reproc
from flask import g

DATABASE = 'database.db'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'flv', 'avi', 'wmv'}
UPLOAD_PATH = 'C:/Users/Administrator/Desktop/Examiner-frontend/examiner-frontend/public/videos/'


def connect_db():
    """连接数据库"""
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """获取数据库连接"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def verify_iden(jwt):
    username = jwt['username']
    password = jwt['password']
    db = get_db()
    error = None
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    if user is None:
        return 0
    elif not password == user['password']:
        return 0
    if error is None:
        return 1


def upload_compare(file, dir):
    reproc(file, dir, 16)
    res = compare(dir)
    db = get_db()
    print(res)
    return res


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def target_compare(app, your_name, form):
    with app.app_context():
        your_file = form['yourfile']
        target_owner = form['targetowner']
        target_file = form['targetfile']
        db = get_db()
        text1 = db.execute(
            'SELECT description FROM video WHERE hashname = ?', (your_file,)
        ).fetchone()[0]
        text2 = db.execute(
            'SELECT description FROM video WHERE hashname = ?', (target_file,)
        ).fetchone()[0]
        text_res = text_cmp(text1, text2)
        your_dir = 'static/cmpimages/' + your_file[:32]
        target_dir = 'static/cmpimages/' + target_file[:32]
        result_dir = 'static/cmpresults/' + hashlib.sha256((your_dir + target_dir).encode()).hexdigest()[:32]
        create_dir(your_dir)
        create_dir(target_dir)
        create_dir(result_dir)
        reproc(UPLOAD_PATH + your_name + '/' + your_file, your_dir, 4)
        reproc(UPLOAD_PATH + target_owner + '/' + target_file, target_dir, 4)
        error = None
        res = float(opti_compare(your_dir, target_dir))
        db.execute(
            'INSERT INTO cmplog (requser, reqfile, targuser, targfile, avgrate, logfile, logtime, txtrate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (your_name, form['yourfile'], target_owner, form['targetfile'], res,
             hashlib.sha256(
                 ('static/cmpimages/' + your_file[:32] + 'static/cmpimages/' + target_file[:32]).encode()).hexdigest()[:32],
             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), text_res)
        )
        db.commit()


def text_cmp(text1, text2):
    jaccard_coefficient = Jaccrad(text1, text2)
    vec1, vec2 = get_word_vector(text1, text2)
    cosine_coefficient = Cos_dist(vec1, vec2)
    dice_coefficient = Dice(text1, text2)
    return (jaccard_coefficient + cosine_coefficient + dice_coefficient) / 3

