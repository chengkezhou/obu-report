#!/usr/bin/python3
import sqlite3
import time
import random
import json

# ======================================  Basic Format  ======================================

def head_info(size,p_version=10,ev_type="13",d_type="03",en_type="0",en_version="0E",s_type="0"):
    '''基本信息头，返回信拼装的元组'''

    # 1.1 总长度（2 bytes）
    total_size = size+ 12
    b_total = ()
    for i11 in range(0,2):
        rep = bin(total_size)
        n5 = len(rep)-2
        if n5>=8:
            rep1 = int(rep[-8:],base=2)
        else:
            rep1 = int(rep[2:],base=2)
        b_t = (rep1,)
        b_total = b_total + b_t
        total_size = total_size>>8
    # print(total_size,b_total)

    # 1.2 协议版本（1 bytes）
    b_protocol = (p_version,)

    # 1.3 事件类型（1 bytes）
    event_type = ev_type
    eve = int(event_type,base=16)
    b_event = (eve,)

    # 1.4 设备类型（1 bytes）
    device_type = d_type
    dev = int(device_type,base=16)
    b_device = (dev,)

    # 1.5 加密类型（1 bytes)
    encrypt_type = en_type
    enct = int(encrypt_type,base=16)
    b_encrypt_t =(enct,)

    # 1.6 加密key版本（1 bytes）
    encrypt_version = en_version
    encv = int(encrypt_version,base=16)
    b_encrypt_v =(encv,)

    # 1.7 签名类型（1 bytes)
    signature_type = s_type
    sig = int(signature_type,base=16)
    b_signature =(enct,)

    # 1.8 事件上报时间（4 bytes)
    report_time = int(time.time())
    b_report = ()
    for i18 in range(0,4):
        rep = bin(report_time)
        n18 = len(rep)-2
        if n18>=8:
            rep1 = int(rep[-8:],base=2)
        else:
            rep1 = int(rep[2:],base=2)
        b_r = (rep1,)
        b_report = b_report + b_r
        report_time = report_time>>8

    head = b_total + b_protocol + b_event + b_device + b_encrypt_t + b_encrypt_v + b_signature + b_report
    return head

# ======================================  Trip info  ======================================
now = str(time.strftime("%Y-%m-%d %H:%M:%S"))

def trip_info(d_id,t_time,status,gps1,gps2,gps_list):
    ''' 批量上传gps，返回拼装后的元组'''

    # 2.1 设备id（8 bytes）
    did = d_id
    b_did = ()
    for n1 in did:
        loc = ord(n1)
        b0 = (loc,)
        b_did = b_did + b0

    # 2.2 行程id（8 bytes）
    b_tid = (0,0,0,0,0,0,0,0)

    # 2.3 gps点数量（2 bytes）,小于100个
    gps_count = int(gps2) - int(gps1) + 1
    b_cou = (gps_count,0)

    # 2.4 第一个gps采样时间（4 bytes）TT不传
    fast_time = t_time
    timeArray = time.strptime(fast_time, "%Y-%m-%d %H:%M:%S")
    trigertime = int(time.mktime(timeArray))

    # 2.5 gps
    b_gps = ()
    with open(gps_list, "r") as f:
        data = json.load(f)

    for i in range(gps1, gps2+1):
        gps = data[i]
        # print("0,gps:",gps)
        log = gps['longitude'] # 经度
        lat = gps['latitude']  # 纬度
        speed = gps['speed']  # 速度
        bearing = gps['direction']  # 方位
        altitude = gps['altitude']  # 海拔

        # 2.5.1 gps采样时间（4 bytes）
        time0 = int(trigertime)
        b_time = ()
        for i251 in range(0, 4):
            tim = bin(time0)
            n251 = len(tim) - 2
            if n251 >= 8:
                time1 = int(tim[-8:], base=2)
            else:
                time1 = int(tim[2:], base=2)
            b_tim = (time1,)
            b_time = b_time + b_tim
            time0 = time0 >> 8
        trigertime = trigertime + 5  # 触发时间

        # 2.5.2 经度（4 bytes）
        log = int(log*100000)
        b_lo = ()
        for i252 in range(0, 4):
            lo = bin(log)
            n252 = len(lo) - 2
            if n252 >= 8:
                lo1 = int(lo[-8:], base=2)
            else:
                lo1 = int(lo[2:], base=2)
            b_l1 = (lo1,)
            b_lo = b_lo + b_l1
            log = log >> 8
        # print(log,b_lo)

        # 2.5.3 纬度（4 bytes）
        lat = int(lat*100000)
        b_la = ()
        for i253 in range(0, 4):
            la = bin(lat)
            n253 = len(la) - 2
            if n253 >= 8:
                la1 = int(la[-8:], base=2)
            else:
                la1 = int(la[2:], base=2)
            b_l = (la1,)
            b_la = b_la + b_l
            lat = lat >> 8

        # 2.5.4 速度（1 bytes）
        # speed = int(speed*3.6)
        speed = int(speed)
        if speed<=255:
            b_sp = (speed,)
        # print(speed,b_sp)

        # 2.5.5 方向（2 bytes）
        # bearing = int(bearing*10)
        bearing = int(bearing)
        b_be = ()
        for i255 in range(0, 2):
            bea = bin(bearing)
            n5 = len(bea) - 2
            if n5 >= 8:
                bea1 = int(bea[-8:], base=2)
            else:
                bea1 = int(bea[2:], base=2)
            b_b = (bea1,)
            b_be = b_be + b_b
            bearing = bearing >> 8

        # 2.5.6 海拔（2 bytes)
        altitude = int(altitude)
        b_al = ()
        for i256 in range(0, 2):
            alt = bin(altitude)
            if alt[0] == "-":
                n256 = len(alt) - 3
                if n256 >= 8:
                    alt1 = int(alt[-8:], base=2)
                elif n256 > 0 and n256 < 8:
                    alt1 = int(alt[3:], base=2)
                else:
                    alt1 = 0
            else:
                n256 = len(alt)-2
                if n256 >= 8:
                    alt1 = int(alt[-8:], base=2)
                elif n256>0 and n256<8 :
                    alt1 = int(alt[2:], base=2)
                else:
                    alt1 = 0
            b_a = (alt1,)
            b_al = b_al + b_a
            altitude = altitude >> 8

        # print(altitude,al,b_al)

        # 2.5.7 gps状态（1 bytes）
        status = status
        sta = ord(status)
        b_sta = (sta,)
        # print(status,b_sta)

        b_gps =b_gps + b_time + b_lo + b_la + b_sp + b_be + b_al + b_sta

    trip = b_did + b_tid + b_cou + b_gps
    return trip

def engine(d_id,t_time,t_id):
    '''启动/熄火事件'''

    engine_trigertime = t_time

    # 设备id
    did = d_id
    b_did = ()
    for n1 in did:
        loc = ord(n1)
        b0 = (loc,)
        b_did = b_did + b0

    # 事件id
    e1 = random.randint(0, 255)
    e2 = ord(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    e3 = random.randint(0, 255)
    e4 = ord(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    e5 = random.randint(0, 255)
    e6 = ord(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    r_time = str(engine_trigertime)
    e7 = int(r_time[0])
    e8 = int(r_time[1])
    e9 = int(r_time[2])
    e10 = int(r_time[3])
    e11 = int(r_time[4])
    e12 = int(r_time[5])
    e13 = int(r_time[6])
    e14 = int(r_time[7])
    e15 = int(r_time[8])
    e16 = int(r_time[9])
    b_eid = (e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12,e13,e14,e15,e16)

    # 事件触发时间
    time0 = int(engine_trigertime)
    b_time = ()
    for i in range(0, 4):
        tim = bin(time0)
        n2 = len(tim) - 2
        if n2 >= 8:
            time1 = int(tim[-8:], base=2)
        else:
            time1 = int(tim[2:], base=2)
        b_tim = (time1,)
        b_time = b_time + b_tim
        time0 = time0 >> 8

    # 行程id
    b_tid = t_id

    engine = b_did + b_eid + b_time + b_tid

    return engine

def publish_trip(d_id,t_time,status,gps1,gps2,gps_list,p_version,d_type,en_type,en_version,s_type):
    '''打包一个trip'''

    trip = trip_info(d_id,t_time,status,gps1,gps2,gps_list)
    size = len(trip)
    ev_type = "13"

    head = head_info(size,p_version,ev_type,d_type,en_type,en_version,s_type)

    a = head + trip
    b_trip = bytes(a)
    return b_trip

def publish_engine_on(d_id,t_time,t_id,p_version,d_type,en_type,en_version,s_type):
    '''打包一个启动事件'''
    ev_type = "10"

    engine_on = engine(d_id,t_time,t_id)
    size = len(engine_on)
    head = head_info(size,p_version,ev_type,d_type,en_type,en_version,s_type)
    a = head + engine_on
    b_engine_on = (bytes(a))
    return b_engine_on

def publish_engine_off(d_id,t_time,t_id,p_version,d_type,en_type,en_version,s_type):
    '''打包一个熄火事件'''
    ev_type = "12"

    engine_on = engine(d_id,t_time,t_id)
    size = len(engine_on)
    head = head_info(size,p_version,ev_type,d_type,en_type,en_version,s_type)
    a = head + engine_on
    b_engine_off = (bytes(a))
    return b_engine_off



