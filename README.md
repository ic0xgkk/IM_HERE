# 某不知名的小工具

只要胆够大，天天都放假

此为互动课堂的时间戳二维码生成工具，用于应对ZHBIT所用的互动课堂的二维码签到

搭配IHSyncer自动识别二维码实时记录时间偏移量，以便后期重新调整服务器时间戳偏差

不过很可惜这个方案是行不通的。该项目不再维护，其他的方案已经有了，请看我的另外一个仓库：

https://github.com/ic0xgkk/LajiHDKT

## 使用指南

该代码使用Python3执行，需要如下依赖，直接复制安装即可

```bash
pip3 install flask
pip3 install requests
pip3 install qrcode
pip3 install pillow
```