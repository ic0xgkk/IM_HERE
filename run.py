from flask import Flask
from flask import send_file, make_response, Response
import requests
import time
import json
import qrcode
from io import BytesIO
app = Flask(__name__)


@app.route('/')
def index():
    return '某不知用途的小工具'


@app.route('/favicon.ico')
def favicon():
    return 'favicon.ico'


@app.route('/<cid>')
def cid_route(cid):
    cid = ''.join(list(filter(str.isdigit, cid)))

    if cid is None:
        return "非法请求 1"

    try:
        if int(cid) == 1:
            return gen_qrcode("201820192001399")
        elif int(cid) == 2:
            return gen_qrcode("201820192001536")
        elif int(cid) == 3:
            return gen_qrcode("201820192001548")
        elif int(cid) == 4:
            return gen_qrcode("201820192001539")
        elif int(cid) == 5:
            return gen_qrcode("201820192001535")
        elif int(cid) == 6:
            return gen_qrcode("201820192001206")

        return "非法请求 2"
    except ValueError or TypeError:
        return "非法请求 3"


def gen_qrcode(cid: str):
    """
    该函数用于针对不同课程返回处理好的响应头
    :param cid: 传入课程编号，具体可以查看数据库记录
    :return:返回响应头+数据
    """
    try:
        raw_header = get_raw_header()
    except requests.ConnectionError:
        return "上游连接站点失败"

    if raw_header == -1:
        return "站点超时"

    if raw_header.status_code >= 400:
        return "上游响应头异常"

    t = raw_header.headers['Date']
    t = time.strptime(t, '%a, %d %b %Y %H:%M:%S %Z')
    t = time.mktime(t)
    t = int(int(t) + 28800) * 1000

    qrc = {
        "course_id": "%s" % cid,
        "sgin_id": "%s" % str(t),
        "fashion": "1"
    }
    data = json.dumps(qrc)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )  # 设置图片格式

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image()

    byte_io = BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)

    img = byte_io.getvalue()

    resp: Response = make_response(img)

    resp.headers['Refresh'] = 3
    resp.headers['Server'] = 'xEngine-IceCream'
    resp.headers['Content-Type'] = 'image/png'

    return resp


def get_raw_header():
    try:
        raw_header = requests.get("http://hd.gzzmedu.com:9080/zmhdkt", timeout=1, allow_redirects=False)
    except requests.Timeout:
        try:
            raw_header = requests.get("http://hd.gzzmedu.com:9080/zmhdkt", timeout=1, allow_redirects=False)
        except requests.Timeout:
            try:
                raw_header = requests.get("http://hd.gzzmedu.com:9080/zmhdkt", timeout=1, allow_redirects=False)
            except requests.Timeout:
                return -1
    return raw_header


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2288)
