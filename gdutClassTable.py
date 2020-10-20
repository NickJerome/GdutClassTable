import requests
import json

from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta, date, time
from uuid import uuid1

#常量定义区
StartWeek = datetime(2020,10,18,8,30);#第七周作为第一周..才开始写的代码
JsonID = 'D6CE65FAD6FAB0F6159EAC44DCE'#从登录后的界面中查看Cookies

MyCalender = Calendar ()
#添加属性
MyCalender.add('X-WR-CALNAME', '课表')
MyCalender.add('prodid', '-//My calendar//luan//CN')
MyCalender.add('version', '2.0')
MyCalender.add('METHOD', 'PUBLISH')
MyCalender.add('CALSCALE', 'GREGORIAN')  # 历法：公历
MyCalender.add('X-WR-TIMEZONE', 'Asia/Shanghai')  # 通用扩展属性，表示时区

#从广东工业大学教务网站上取课表信息
def GetTimeTabel (xnxqdm , zc) :
    #基本信息设置
    url = "https://jxfw.gdut.edu.cn/xsgrkbcx!getKbRq.action?xnxqdm="+xnxqdm+"&zc="+zc
    cs = {'JSESSIONID' : JsonID}
    #发送请求到服务器
    response = requests.get(url , cookies = cs)
    #写出课程表到文件
    with open(file="TimeTable.json", mode="wb") as fo:
        data = fo.write(response.content)
#解析Json
def DoWithJson () :
    with open(file="TimeTable.json", mode="r", encoding='utf-8') as fo:
        JsonObj = json.loads(fo.read())
    #开始添加课程
    for info in JsonObj[0]:
        Stime = CalcStartTime(int(info['zc']),int(info['xq']),info['jcdm'])
        Etime = CalcEndTime(Stime)
        ClassEvent = AddClass(info['kcmc'],info['teaxms'],Stime,Etime,info['jxcdmc'])
        MyCalender.add_component(ClassEvent)
#计算事件
def CalcStartTime (Weekly, week,section) :
    date = StartWeek + timedelta(days=7*(Weekly-7))#转到正确的周次
    date = date + timedelta(days=week)
    #不动，本来就是第一节课的时间
    if section == "0304" : #第三四节课开始
        date = date + timedelta (minutes=115)
    elif section == "0607" :#第六七节课开始
        date = date + timedelta (hours=6,minutes=10)
    elif section == "0809" : #第八九节课开始
        date = date + timedelta(hours=8)
    else :
        pass
    return date
#计算下课时间
def CalcEndTime (date) :
    return date + timedelta(minutes=95)
#添加一节课
def AddClass (name, teacher, starttime , endtime , location) :
    event = Event ()
    event.add ('uid',str(uuid1()))
    event.add('summary', name)
    event.add('dtstart', starttime)
    event.add('dtend', endtime)
    event.add('dtstamp', datetime.now())
    event.add('location', location)
    event.add('description', '授课老师：' + teacher)
    return event
#主函数
def main () :
    for i in range(11) :
        GetTimeTabel("202001", str(i+7))
        DoWithJson()
    with open("CLassTable.ics" , "wb") as fo:
        fo.write(MyCalender.to_ical().replace(b'\r\n', b'\n').strip())
        print("Finish")
main()