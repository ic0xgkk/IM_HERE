import cv2
import time
from pyzbar.pyzbar import decode
import json
import sqlite3
import queue
import threading


class Database(object):
    def __init__(self):
        self.queue = queue.Queue(maxsize=51200)

    def __del__(self):
        self.conn.close()

    def insert_queue(self, pc_time_ns, course_id="", sgin_id="", fashion="", pc_time_ms="", full_msg="",
                     time_ms_dev="", qr_local_time="", pc_local_time="", msg=""):
        self.queue.put((pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev,
                        qr_local_time, pc_local_time, msg), block=True, timeout=None)

    def insert_db(self):
        self.conn = sqlite3.connect("data.db")
        cursor = self.conn.cursor()
        while True:
            (pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev,
                    qr_local_time, pc_local_time, msg) = self.queue.get(block=True, timeout=None)
            sql = """INSERT INTO SyncData(pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev, qr_local_time, pc_local_time, msg) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"""\
                  % (pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev, qr_local_time, pc_local_time, msg)
            cursor.execute(sql)
            self.conn.commit()


class Camera(object):
    def __init__(self, camera_idx=0):
        self.cap = cv2.VideoCapture(camera_idx)

    def __del__(self):
        self.cap.release()

    def get_frame(self, camera_idx=0):
        ret, frame = self.cap.read()
        if ret is None:
            self.cap.release()
            timens = str(int(time.time_ns()))
            return -1, timens # 相机没有找到
        else:
            timens = str(int(time.time_ns()))
            cv2.imwrite("data/" + timens + ".png", frame)
            return frame, timens


def re_qrcode(frame, timens):
    dec = decode(frame)

    try:
        dec = dec[0]
    except IndexError:
        return -1, None, None, None, None, None, None, None, None

    try:
        data = json.loads(str(dec.data.decode('utf-8')))
    except json.JSONDecodeError:
        return -2, None, None, None, None, None, None, None, None

    try:
        course_id = str(data['course_id'])
        sgin_id = str(data['sgin_id'])
        fashion = str(data['fashion'])
    except Exception:
        return -3, None, None, None, None, None, None, None, None

    pc_time_ns = str(timens)
    pc_time_ms = str(int(int(timens)/1000000))
    full_msg = str(dec.data.decode('utf-8'))
    time_ms_dev = int(pc_time_ms) - int(sgin_id)
    qr_local_time = time.asctime(time.localtime(int(sgin_id)/1000.0))

    test = int(pc_time_ms)/1000.0
    pc_local_time = time.asctime(time.localtime(int(test)))

    return pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev, \
           qr_local_time, pc_local_time


def frame_process(frame, timens, db: Database, status: int):
    if status == -1:
        msg = "未找到相机"
        pc_time_ns = str(timens)
        db.insert_queue(pc_time_ns, msg=msg)
        print("微秒计：" + pc_time_ns + "-消息：" + msg)
        return None

    pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev, \
        qr_local_time, pc_local_time = re_qrcode(frame, timens)

    if pc_time_ns == -1:
        msg = "图像错误"
        pc_time_ns = str(timens)
        db.insert_queue(pc_time_ns, msg=msg)
        print("微秒计：" + pc_time_ns + "-消息：" + msg)
        return None
    elif pc_time_ns == -2:
        pc_time_ns = str(timens)
        msg = "二维码无法识别或者识别内容有误"
        db.insert_queue(pc_time_ns, msg=msg)
        print("微秒计：" + pc_time_ns + "-消息：" + msg)
        return None
    elif pc_time_ns == -3:
        msg = "数据错误"
        pc_time_ns = str(timens)
        db.insert_queue(pc_time_ns, msg=msg)
        print("微秒计：" + pc_time_ns + "-消息：" + msg)
        return None
    else:
        msg = ""
    db.insert_queue(pc_time_ns, course_id, sgin_id, fashion, pc_time_ms, full_msg, time_ms_dev,
                    qr_local_time, pc_local_time, msg)
    print("微秒计：" + str(pc_time_ns) + "-" + "二维码时间戳:" + str(sgin_id) + ";时间偏移量:" + str(time_ms_dev))


def io():
    cam = Camera()
    db = Database()

    q = threading.Thread(target=db.insert_db, args=())
    q.daemon = True
    q.start()

    while True:
        frame, timens = cam.get_frame()
        try:
            if frame == -1:
                frame = None
                status = -1
            else:
                status = 1
        except ValueError:
            status = 1

        t = threading.Thread(target=frame_process, args=(frame, timens, db, status))
        t.daemon = True
        t.start()

        time.sleep(0.3)


if __name__ == '__main__':
    io()
