import json
import os
import time
from argparse import ArgumentParser
import hashlib
from flask_cors import CORS
import shutil
from JwtVerify.create_token import create_token
from JwtVerify.verify_token import verify_token
from flask import Flask, request, current_app, g, \
    render_template, jsonify, make_response
import threading

from Utils.utils import get_db, target_compare, verify_iden, upload_compare

# 配置
JWT_LIST = []
HASH_LIST = []

# 设置允许的视频文件格式
UPLOAD_PATH = 'C:/Users/Administrator/Desktop/DeepSeek/DeepSeek-frontend/public/'

# 实例化我们的节点；加载 Flask 框架
app = Flask(__name__)
app.config.from_object(__name__)

# 处理跨域请求
CORS(app, resources=r'/*')


@app.teardown_appcontext
def close_db(error):
    """请求结束时关闭数据库连接"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = int(request.form['type'])
        if not username:
            return make_response(), 402
        elif not password:
            return make_response(), 402
        else:
            db = get_db()
            error = None
            if db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone() is not None:
                return make_response(), 1001
            if error is None:
                db.execute(
                    'INSERT INTO user (username, password, type) VALUES (?, ?, ?)',
                    (username, password, usertype)
                )
                db.commit()
                # 视频的最终保存路径
                os.mkdir(UPLOAD_PATH + 'videos/' + username)
                return make_response(), 200
    return make_response(), 403


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            return make_response(), 402
        elif not password == user['password']:
            return make_response(), 402
        if error is None:
            token = create_token(payload=json.dumps({'username': username, 'password': password}))
            res = make_response(jsonify({'token': token, 'avatar': user['avatar']}), 200, )
            global JWT_LIST
            JWT_LIST.append(token)
            return res
    return make_response(), 403


@app.route('/charge', methods=['GET', 'POST'])
def charge():
    """充值"""
    global JWT_LIST
    if request.method == 'GET' and request.headers['Authorization'] in JWT_LIST:
        num = int(request.args.get('num'))
        jwt_res = verify_token(request.headers['Authorization'])
        user_name = jwt_res['username']
        db = get_db()
        remains = db.execute(
            'SELECT remains FROM user WHERE username = ?', (user_name,)
        ).fetchone()[0]
        db.execute(
            'UPDATE user set remains=? WHERE username=?',
            (num + remains, user_name)
        )
        db.commit()
        return make_response(), 200
    return make_response(), 403


@app.route('/avatar', methods=['GET', 'POST'])
def avatar():
    """上传头像"""
    global JWT_LIST
    if request.method == 'POST' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        user_name = jwt_res['username']
        avatar_file = request.files['file']
        avatar_hash = hashlib.sha256((avatar_file.filename + str(time.time()) + str(os.urandom(32))).encode()).hexdigest()
        avatar_file.save(UPLOAD_PATH + 'avatar/' + avatar_hash[:32] + avatar_file.filename[-4:])
        db = get_db()
        db.execute(
            'UPDATE user set avatar=? WHERE username=?',
            (avatar_hash[:32] + avatar_file.filename[-4:], user_name)
        )
        db.commit()
        return make_response(), 200
    return make_response(), 403


@app.route('/getinfo', methods=['GET', 'POST'])
def get_info():
    """获取个人信息"""
    global JWT_LIST
    if request.method == 'GET' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        user_name = jwt_res['username']
        db = get_db()
        quer = db.execute(
            'SELECT * FROM user WHERE username = ?', (user_name,)
        ).fetchone()
        remains = quer['remains']
        user_type = quer['type']
        avatar = quer['avatar']
        res = make_response()
        res.data = json.dumps({'username':user_name, 'remains': remains, 'type': user_type, 'avatar': avatar})
        return res, 200
    return make_response(), 403


@app.route('/logout', methods=['GET'])
def logout():
    """退出登录"""
    global JWT_LIST
    if request.method == 'GET' and request.headers['Authorization'] in JWT_LIST:
        JWT_LIST.remove(request.headers['Authorization'])
        return make_response(), 200
    return make_response(), 403


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    """上传视频"""
    global JWT_LIST
    global HASH_LIST
    if request.method == 'POST' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        if request.files:
            video = request.files['file']
            video_hash = hashlib.sha256((video.filename + str(time.time()) + str(os.urandom(32))).encode()).hexdigest()
            # 上传到临时目录下
            video.save('static/tmp/' + video_hash[:32] + video.filename[-4:])
            res = make_response('', 200, )
            res.data = json.dumps({'hash': video_hash, 'fmt': video.filename[-4:]})
            HASH_LIST.append(video_hash[:32])
            return res
        elif (request.form['hash'][:32] in HASH_LIST) and verify_iden(jwt_res):
            status = 200
            video_title = request.form['title']
            video_description = request.form['description']
            video_owner = jwt_res['username']
            # 视频所在的临时路径
            tmp_file = 'static/tmp/' + request.form['hash'][:32] + request.form['fmt']
            # 要保存图片的路径
            tmp_dir = 'static/images/' + request.form['hash'][:32]
            os.mkdir(tmp_dir)
            video_res = upload_compare(tmp_file, tmp_dir)
            if len(video_res):
                for i in video_res:
                    if i > 0.2:
                        status = 206
            store_file = UPLOAD_PATH + 'videos/{}/{}'.format(video_owner, request.form['hash'][:32] + request.form['fmt'])
            # 将视频移动到最终保存路径下
            shutil.move(tmp_file, store_file)
            db = get_db()
            error = None
            db.execute(
                'INSERT INTO video (title, description, owner, uploadtime, hashname) VALUES (?, ?, ?, ?, ?)',
                (video_title, video_description, video_owner, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), request.form['hash'][:32] + request.form['fmt'])
            )
            db.commit()
            return make_response(), status
    return make_response(), 403


@app.route('/download', methods=['GET', 'POST'])
def download():
    """下载分析报告"""
    global JWT_LIST
    if request.method == 'GET' and request.headers['Authorization'] in JWT_LIST:
        filedir = request.args.get('file')
        file = open('static/cmpresults/' + filedir + '.pdf', "rb").read()
        response = make_response(file)
        return response, 200
    return make_response(), 403


@app.route('/getvideos/<name>', methods=['POST', 'GET'])
def get_videos(name):
    """获取视频信息"""
    if request.method == 'GET' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        video_owner = jwt_res['username']
        db = get_db()
        error = None
        videos = []
        if name == 'my':
            videos = db.execute(
                'SELECT id,title,description,owner,uploadtime,hashname FROM video WHERE owner = ?', (video_owner,)
            ).fetchall()
        elif name == 'all':
            videos = db.execute(
                'SELECT id,title,description,owner,uploadtime,hashname FROM video'
            ).fetchall()
        elif name == 'query':
            querys = request.args
            if 'videoNum' in querys:
                videos = db.execute(
                    'SELECT id,title,description,owner,uploadtime,hashname FROM video WHERE id = ?', (querys['videoNum'],)
                ).fetchall()
            elif 'name' in querys:
                videos = db.execute(
                    "SELECT id,title,description,owner,uploadtime,hashname FROM video WHERE title like '%{}%'".format(querys['name'])
                ).fetchall()
            elif 'owner' in querys:
                videos = db.execute(
                    'SELECT id,title,description,owner,uploadtime,hashname FROM video WHERE owner = ?', (querys['owner'],)
                ).fetchall()
        infos = []
        for video in videos:
            infos.append({'videoNum': video['id'], 'name': video['title'], 'description': video['description'],
                          'owner': video['owner'], 'uploadTime': video['uploadtime'], 'url': video['hashname'],
                          'isDetail': False})
        res = make_response()
        res.data = json.dumps(infos)
        return res, 200


@app.route('/delete', methods=['GET', 'POST'])
def delete_videos():
    """删除视频"""
    global JWT_LIST
    if request.method == 'POST' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        video_owner = jwt_res['username']
        db = get_db()
        error = None
        videoNum = request.form['videoNum']
        videos = db.execute(
            "SELECT * FROM video WHERE owner = '" + video_owner + "' and id = " + videoNum
        ).fetchall()
        if videos:
            os.remove(UPLOAD_PATH + 'videos/' + video_owner + '/' + videos[0]['hashname'])
            db.execute(
                '''DELETE FROM video WHERE owner = '{}' and id = {}'''.format(video_owner, videoNum)
            )
            db.commit()
            return make_response(), 206
        else:
            return make_response(), 403


@app.route('/compare', methods=['GET', 'POST'])
def video_compare():
    """比较视频相似度"""
    global JWT_LIST
    if request.method == 'POST' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        video_owner = jwt_res['username']
        db = get_db()
        num = db.execute(
            'SELECT remains FROM user WHERE username = ?', (video_owner,)
        ).fetchone()
        if num[0]:
            t = threading.Thread(target=target_compare, args=(current_app._get_current_object(), video_owner, request.form))
            t.start()
            db.execute(
                'UPDATE user set remains=? WHERE username=?',
                (num[0] - 1, video_owner)
            )
            db.commit()
            response = make_response()
            return response, 200
        else:
            return make_response(), 206
    return make_response(), 403


@app.route('/getlog', methods=['GET', 'POST'])
def get_log():
    """获取比较日志"""
    global JWT_LIST
    if request.method == 'GET' and request.headers['Authorization'] in JWT_LIST:
        jwt_res = verify_token(request.headers['Authorization'])
        video_owner = jwt_res['username']
        db = get_db()
        error = None
        logs = db.execute(
            'SELECT reqfile, targuser, targfile, avgrate, logfile, logtime, txtrate FROM cmplog WHERE requser = ?',
            (video_owner,)).fetchall()
        infos = []
        for log in logs:
            reqfile = db.execute(
                'SELECT title FROM video WHERE hashname = ?',
                (log['reqfile'],)).fetchone()
            targfile = db.execute(
                'SELECT title FROM video WHERE hashname = ?',
                (log['targfile'],)).fetchone()
            infos.append({'videoName': reqfile['title'], 'owner': log['targuser'], 'targetName': targfile['title'],
                          'logfile': log['logfile'], 'logTime': log['logtime'], 'avgRate': log['avgrate'], 'txtRate': log['txtrate']})
        res = make_response()
        res.data = json.dumps(infos)
        return res, 200
    return make_response(), 403


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)
