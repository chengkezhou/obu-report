#!/usr/bin/python3

import psycopg2,time,smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

# 待查表
data = ['stg_alert','stg_bad_drive','stg_crash','stg_debug_info','stg_engine','stg_error','stg_fence','stg_heartbeat','stg_power','stg_voltage']

# 待查设备
devices = ['U0001005','U0001008','U0001016','U0005043','U0005039','U0005034','U0005015','U0005014','U0000020','U0000017','U0000043','U0005038','U0001168','U0001211','U0001284','U0001116','U0001207','U0001110','U0001032','U0001033','U0001026','U0001024','U0001265','U0001236','U0000071','U0000072','U0001035','U0001036','U0001274','U0001256','U0001198','U0001281','U0001040','U0001253','U0001019','U0001277','U0001042','U0001276','U0001017','U0001021','U0001018','U0001273','U0001011','U0001047','U0001046','U0001223','U0001251','U0001287','U0001025','U0001185','U0001030','U0001041','U0001020','U0001264','U0001250','U0001038','U0001275','U0001278','U0001279','U0001004']

# 收件人邮箱
receiver = ['zhouchengke@huabaotech.com', 'mars.zhu@huabaotech.com', 'edward@huabaotech.com','hufang@huabaotech.com','mafei@remowireless.com','chunlei.xu@remowireless.com','coco.qian@remowireless.com','peter.xu@remowireless.com','larry.lee@remowireless.com','steven.shao@remowireless.com','eimy.zhang@remowireless.com',' pepsi.zhu@remowireless.com']
# receiver = ['121142125@qq.com']
# receiver = ['zhouchengke@huabaotech.com']

# 构建空列表
work_device = []    # 活着的设备
mailbody_1 = []     # 邮件内容-24小时无联系的设备
mailbody_2 = []     # 邮件内容-有上电或心跳不正常的设备
mailbody_3 = []     # 邮件内容-无重启，心跳正常

body1 = ''
body2 = ''
body3 = ''

now = str(time.strftime("%Y-%m-%d %H:%M:%S"))

conn = psycopg2.connect(database='demo_1',user='demo_2',password='demo_3',host='demo_4',port='demo_5')
cur = conn.cursor()

trigger_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(time.time())-86400))

# 遍历待测设备
for n in range(len(devices)):
    # 查数据库，得到该设备的最新gps的采集时间
    sql1 = "select max(gps_sample) from stg_trip_point where device_id=\'"+devices[n]+"\'"
    cur.execute(sql1)
    trigger_time1 = cur.fetchall()[0][0]
    print(devices[n],"最近一个gps的采集时间：",str(trigger_time1)[:19])
    # 判断该设备是否有gps数据
    if trigger_time1 is not None:
        # 将时间字符串转换成时间戳
        time1 = int(time.mktime(time.strptime(str(trigger_time1)[:19],"%Y-%m-%d %H:%M:%S")))
        print(devices[n],"最近一个gps的采集时间戳：",time1)
        # 判断时间最新gps采集时间是否超过24小时
        if time1 >= int(time.time()-86400):
            work_device.append(devices[n])
            print(devices[n],"24小时内有gps")
        else:
            print(print(devices[n],"24小时内无gps"))
            for m in range(len(data)):
                # 查数据库，得该设备对应事件的最新触发时间
                sql2 = "select max(trigger_time) from " + data[m] + " where device_id=\'" + devices[n] + "\'"
                cur.execute(sql2)
                trigger_time2 = cur.fetchall()[0][0]
                print(devices[n], "最近一个", data[m], "的采集时间：", trigger_time2)
                if trigger_time2 is not None:
                    time2 = int(time.mktime(time.strptime(str(trigger_time2)[:19], "%Y-%m-%d %H:%M:%S")))
                    print(devices[n], "最近一个", data[m], "的采集时间：", time2)
                    if time2 >= int(time.time() - 86400):
                        work_device.append(devices[n])
                        print(devices[n], "24小时内有%s事件" % data[m])
                        break
                    else:
                        print(devices[n], "24小时内无%s事件" % data[m])
    else:
        # 遍历原始数据，
        for m in range(len(data)):
            # 查数据库，得该设备对应事件的最新触发时间
            sql2 = "select max(trigger_time) from "+data[m]+" where device_id=\'"+devices[n]+"\'"
            cur.execute(sql2)
            trigger_time2 = cur.fetchall()[0][0]
            print(devices[n],"最近一个",data[m],"的采集时间：", trigger_time2)
            if trigger_time2 is not None:
                time2 = int(time.mktime(time.strptime(str(trigger_time2)[:19],"%Y-%m-%d %H:%M:%S")))
                print(devices[n], "最近一个", data[m], "的采集时间：", time2)
                if time2 >= int(time.time()-86400):
                    work_device.append(devices[n])
                    print(devices[n],"24小时内有%s事件"%data[m])
                    break
                else:
                    print(devices[n], "24小时内无%s事件" % data[m])
print(work_device)


for n in range(len(devices)):
    # 判断设备是否失联
    cur.execute("select fw_ver,own_company from s_device where device_id=\'"+devices[n]+"\'")
    fetchall = cur.fetchall()
    if len(fetchall)>0:
        if len(fetchall[0])==1:
            device_head = devices[n] + "【" + fetchall[0][0] + "】" + "【None】"
        elif len(fetchall[0])==2:
            device_head = devices[n] + "【" + fetchall[0][0] + "】" + "【" + fetchall[0][1] + "】"
    else:
        device_head = devices[n]+"【None】"+"【None】"

    if devices[n] not in work_device:
        mailbody_1.append(' * %s ：24小时内无任何事件上传！ \n' % device_head)
    else:
        cur.execute("select count(*) from stg_power where device_id=%s and trigger_time>%s",(devices[n],trigger_time))
        power = cur.fetchall()[0][0]
        cur.execute("select count(*) from stg_heartbeat where device_id=%s and trigger_time>%s", (devices[n], trigger_time))
        heartbeat = cur.fetchall()[0][0]

        if power>0 or heartbeat<46:
            if power==0 and heartbeat<46:
                hea_1 = 48-heartbeat
                mailbody_2.append(' - %s ：心跳丢失（-%s 个） \n' % (device_head, str(hea_1)))
            elif power==0 and heartbeat>50:
                hea_2 = heartbeat-48
                mailbody_2.append(' - %s ：心跳超出（+%s 个） \n' % (device_head, str(hea_2)))
            elif power>0 and (heartbeat>=46 and heartbeat<=50):
                mailbody_2.append(' - %s ：上电事件（%s 个） \n' % (device_head, str(power)))
            elif power>0 and heartbeat<46 :
                hea_3 = 48 - heartbeat
                mailbody_2.append(' - %s ：上电事件（%s 个），心跳丢失（-%s 个） \n' % (device_head, str(power), str(hea_3)))
            elif power>0 and heartbeat>50:
                hea_4 = heartbeat - 48
                mailbody_2.append(' - %s ：上电事件（%s 个），心跳超出（+%s 个） \n' % (device_head, str(power), str(hea_4)))
        else:
            mailbody_3.append(' @ %s ：无重启，心跳正常!\n'%device_head)

# 发送邮件
smtpserver = 'smtp.huabaotech.com'  # 发件服务器
sender = 'noreply@huabaotech.com'  # 发件人及账号
password = 'Abc2017@'  # 发件账号密码

msg = MIMEMultipart()

for n1 in range(len(mailbody_1)):
    body1 = body1 + mailbody_1[n1]
for n2 in range(len(mailbody_2)):
    body2 = body2 + mailbody_2[n2]
for n3 in range(len(mailbody_3)):
    body3 = body3 + mailbody_3[n3]
mailbody = 'Start Time：'+now+'\n\nOBU设备24小时内的事件统计结果：\n\n'+body1+'\n'+body2+'\n'+body3+'\n以上非正常设备数据需要重点查看\n理论值：24小时心跳48个（+-2），上电0个'
print(mailbody)
puretext = MIMEText(mailbody, 'plain', 'utf-8')  # 邮件内容
msg.attach(puretext)

msg['Subject'] = Header('OBU自动监测 %s' % now, 'utf-8')  # 邮件标题
msg['From'] = sender
msg['To'] = ';'.join(receiver)

try:
    smtp = smtplib.SMTP()
    smtp .connect(smtpserver,25)    # 连接发信服务器
    smtp.login(sender,password)   # 设置发信账号
    smtp.sendmail(
        sender, # 发信邮箱
        receiver,   # 收信邮箱
        msg.as_string())
    smtp.quit()
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")

