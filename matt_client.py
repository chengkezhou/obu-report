#!/usr/bin/python3
import random
import time
from time import sleep
import paho.mqtt.client as mqtt
from device_info import publish_trip, publish_engine_on, publish_engine_off

# 开发环境 MQTT 服务器地址
host = "1826tn8412.iask.in"
port = 11878
# topic = 'data/event/dev'
topic = 'test'
username = "hbclient"
password = "huabao308"

# 当连接上服务器后回调此函数
def on_connect(client, userdata, flags, rc):
    print("连接服务器返回 code： " + str(rc))
    # client.subscribe(topic)

client1 = mqtt.Client()
client1.username_pw_set(username, password)
client1.on_connect = on_connect
client1.connect_async(host, port, 60)
client1.loop_start()

client1.publish(topic, 123, 1)
sleep(1)

start_time = time.time()    # 开始执行时的时间戳
gps_list = 'C:\\Users\\12114\\Desktop\\client1\\trip1.json'  # 选择行程

def t_id():
    # 行程id随机数
    t1 = random.randint(0, 255)
    t2 = random.randint(0, 255)
    t3 = ord(random.choice("abcdefghijklmnopqrstuvwxyz"))
    t4 = ord(random.choice("abcdefghijklmnopqrstuvwxyz"))
    t5 = ord(random.choice("abcdefghijklmnopqrstuvwxyz"))
    t6 = random.randint(0, 255)
    t7 = random.randint(0, 255)
    t8 = random.randint(0, 255)
    b_tid = (t1, t2, t3, t4, t5, t6, t7, t8)
    return b_tid

def engine_on():
    '''发送启动事件'''
    engine_on = publish_engine_on(d_id=device_id,
                                  t_time=engine_on_time,
                                  t_id=b_tid,
                                  p_version=10,
                                  d_type="03",
                                  en_type="0",
                                  en_version="0E",
                                  s_type="0"
                                  )
    client1.publish(topic, engine_on, 1)
    sleep(1)
    timeon = time.localtime(engine_on_time)
    timeon = time.strftime("%Y-%m-%d %H:%M:%S", timeon)
    print('\nengine_on：',timeon)

def enging_off():
    '''发送熄火事件'''
    engine_off = publish_engine_off(d_id=device_id,
                                    t_time=engine_off_time,
                                    t_id=b_tid,
                                    p_version=10,
                                    d_type="03",
                                    en_type="0",
                                    en_version="0E",
                                    s_type="0"
                                    )
    client1.publish(topic, engine_off, 1)
    sleep(1)
    timeoff = time.localtime(engine_off_time)
    timeoff = time.strftime("%Y-%m-%d %H:%M:%S", timeoff)
    print('\nengine_off：',timeoff)

def trip_gps(gps1,gps2):
    '''发送批量gps点'''
    first_time = engine_on_time + 1  # 第一个gps的时间
    for n in range(gps_for):
        time_local = time.localtime(first_time)
        t_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

        d_info = publish_trip(d_id=device_id,  # 设备号
                              t_time=t_time,  # 第一个gps的采样时间
                              status="Y",  # gps状态，"Y"表示可信----使用默认值
                              gps1=gps1,  # 第一个gps的编号
                              gps2=gps2,  # 第二个gps的编号
                              gps_list=gps_list,
                              p_version=10,  # 协议版本----使用默认值
                              d_type="03",  # 设备类型
                              en_type="0",  # 加密类型----使用默认值
                              en_version="0E",  # 加密key版本----使用默认值
                              s_type="0"  # 签名类型----使用默认值
                              )
        client1.publish(topic, d_info, 1)  # client1 publishes topic 'position' with content 'i'
        sleep(1)
        print(d_info)
        time_first = t_time
        time_last = time.localtime(first_time+gps_tall*5 - 5)
        time_last = time.strftime("%Y-%m-%d %H:%M:%S", time_last)
        print('\n第 %d 批gps，共 %d 个'%(n+1,gps_tall))
        print('first time:', time_first,'\nlast time:',time_last)
        # print('上传%d个gps，第一个gps点时间：%s，最后一个gps点时间：%s'(gps_tall,timeon,first_time))
        gps1 += gps_tall
        gps2 += gps_tall
        first_time += gps_tall * 5

print('\n====================== trip1:正常行程 ======================')
'''
	正常行程
		engine on 
		连续gps
		engine off	
'''

# 测试参数
device_id = 'TT1001QA'
b_tid = t_id()
gps_first = 0  # 第一个gps在json文件中的位数
gps_last = 51  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 10  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
trip_gps(gps_first,gps_last)
enging_off()



print('\n====================== trip2:无启动熄火事件的行程（纯gps） ======================')
'''
	纯gps
		连续gps
'''
# 测试参数
device_id = 'TT1002QA'
b_tid = t_id()
gps_first = 0  # 第一个gps在json文件中的位数
gps_last = 51  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 10  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)

trip_gps(gps_first,gps_last)

print('\n====================== trip3:缺少启动事件的行程 ======================')
'''
	缺少启动
		连续gps
		engine off	
'''
# 测试参数
device_id = 'TT1003QA'
b_tid = t_id()
gps_first = 0  # 第一个gps在json文件中的位数
gps_last = 51  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 10  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
trip_gps(gps_first,gps_last)
enging_off()


print('\n====================== trip4:缺少熄火事件的行程 ======================')
'''
	缺少熄火
	    engine on
		连续gps
'''
# 测试参数
device_id = 'TT1004QA'
b_tid = t_id()
gps_first = 0  # 第一个gps在json文件中的位数
gps_last = 51  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 10  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
trip_gps(gps_first,gps_last)

print('\n====================== trip5:无gsp的行程 ======================')
'''
	无gps
		engine on 
		engine off	
'''
# 测试参数
device_id = 'TT1005QA'
b_tid = t_id()
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
enging_off()

print('\n====================== trip6:两段时间间隔小于10分钟的行程 ======================')
'''
    两段小于10分钟的行程
'''
# 测试参数
print('******** trip6,第一段 ********\n')

device_id = 'TT1006QA'
b_tid = t_id()
gps_first = 0  # 第一个gps在json文件中的位数
gps_last = 51  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 3  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
trip_gps(gps_first,gps_last)
enging_off()

print('******** trip6,第二段 ********\n')

device_id = 'TT1006QA'
b_tid = t_id()
gps_first = gps_first + gps_tall*gps_for  # 第一个gps在json文件中的位数
gps_last = gps_last + gps_tall*gps_for  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 7  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = engine_off_time + 599
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
trip_gps(gps_first,gps_last)
enging_off()

print('\n====================== trip7 : 两段时间间隔大于10分钟的行程 ======================')
'''
    两段时间间隔大于10分钟的行程
'''
# 测试参数
print('******** trip7,第一段 ********\n')

device_id = 'TT1007QA'
b_tid = t_id()
gps_first = 0  # 第一个gps在json文件中的位数
gps_last = 51  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 3  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = start_time
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
trip_gps(gps_first,gps_last)
enging_off()

print('******** trip7,第二段 ********\n')


device_id = 'TT1007QA'
b_tid = t_id()
gps_first = gps_first + gps_tall*gps_for  # 第一个gps在json文件中的位数
gps_last = gps_last + gps_tall*gps_for  # 第一批gps点的最后一个gps在json文件中的位数
gps_for = 7  # gps发送的次数
gps_tall = gps_last - gps_first + 1
engine_on_time = engine_off_time + 601
engine_off_time = engine_on_time + gps_tall*gps_for*5 +1

print('device_id：',device_id)
engine_on()
trip_gps(gps_first,gps_last)
enging_off()

