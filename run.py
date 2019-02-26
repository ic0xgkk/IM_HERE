from flask import Flask
from flask import send_file
import requests
import time
import json
import qrcode
from io import BytesIO
app = Flask(__name__)


@app.route('/')
def index():
    return '某不知用途的小工具，版权归雪糕所有'


@app.route('/<cid>')
def gen_qrcode(cid):
    cid = ''.join(list(filter(str.isdigit, cid)))

    if cid is None:
        return ""

    try:
        if int(cid) <= 201820190000000 or int(cid) > 201820199999999:
            return ""
    except ValueError or TypeError:
        return "非法请求"

    try:
        raw_header = get_raw_header()
    except requests.ConnectionError:
        return "连接站点失败，请联系管理员"

    if raw_header == -1:
        return "站点超时，请联系管理员"

    if raw_header.status_code >= 400:
        return "响应头异常，请联系管理员"

    t = raw_header.headers['Date']
    t = time.strptime(t, '%a, %d %b %Y %H:%M:%S %Z')
    t = time.mktime(t)
    t = int(t * 1000)

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

    return send_file(byte_io, mimetype='image/png')


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
