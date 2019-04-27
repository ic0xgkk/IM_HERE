CREATE TABLE SyncData(
  pc_time_ns UNSIGNED BIGINT PRIMARY KEY NOT NULL , --本机时间，微秒记
  course_id VARCHAR(128) DEFAULT NULL, --课程ID
  sgin_id VARCHAR(128) DEFAULT NULL, --二维码中的时间戳
  fashion VARCHAR(128) DEFAULT NULL, --二维码中的数据
  pc_time_ms VARCHAR(128) DEFAULT NULL, --本机时间，毫秒记
  full_msg VARCHAR(1024) DEFAULT NULL, --完整的二维码消息
  time_ms_dev BIGINT DEFAULT NULL, --毫秒级偏差，本机毫秒时间减去二维码时间戳的值
  qr_local_time VARCHAR(128) DEFAULT NULL, --二维码的文本时间
  pc_local_time VARCHAR(128) DEFAULT NULL, --本机的文本时间
  msg VARCHAR(128) DEFAULT NULL --额外消息
);