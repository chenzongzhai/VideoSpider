# -*- coding: utf8 -*-

import time
import datetime


# 规整化发表时间
def regularization_time(publish_time):
    if isinstance(publish_time, int) or publish_time.isdigit():
        publish_time = int(publish_time)
        if publish_time > time.time():
            publish_time /= 1000
        return get_time(publish_time)

    if not isinstance(publish_time, str) or not publish_time.strip():
        return None

    publish_time = publish_time.strip()

    now = get_now_date()

    if '刚刚' in publish_time:  # 22分钟前
        publish_time = get_now_time()

    elif '分钟前' in publish_time:  # 22分钟前
        publish_time = publish_time.replace('分钟前', '')
        publish_time = time.time() - int(publish_time)*60
        publish_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(publish_time))
        publish_time += ':00'

    elif '小时前' in publish_time:  # 22分钟前
        publish_time = publish_time.replace('小时前', '')
        publish_time = time.time() - int(publish_time) * 60 * 60
        publish_time = time.strftime("%Y-%m-%d %H", time.localtime(publish_time))
        publish_time += ':00:00'

    elif '今天' in publish_time:  # 今天 21:19
        publish_time = publish_time.replace('今天', now) + ':00'

    elif '月' in publish_time or '日' in publish_time:  # 02月22日 01:07
        publish_time = publish_time.replace('月', '-').replace('日', '')
        publish_time = time.strftime("%Y-", time.localtime(time.time())) + publish_time + ':00'
    elif len(publish_time) == 5:  # 形如14:58
        publish_time = now + " " + publish_time + ":00"
    elif len(publish_time) == 11:  # 形如09-29 12:38
        publish_time = time.strftime("%Y-", time.localtime(time.time())) + publish_time + ':00'
    elif len(publish_time) == 16:  # 形如2015-09-29 12:38
        publish_time += ':00'

    return publish_time


# 歌曲或视频时长
def seconds_hs(seconds):
    """
    秒转分钟:秒数 (例如181-> 03:01)
    """
    if not seconds:
        return '0'
    seconds = int(seconds)
    hour = 0
    minute = 0
    if seconds >= 3600:
        hour = seconds//3600
        seconds %= 3600
    if seconds >= 60:
        minute = seconds//60
        seconds %= 60

    hour = '0{}'.format(hour) if hour < 10 else str(hour)
    minute = '0{}'.format(minute) if minute < 10 else str(minute)
    seconds = '0{}'.format(seconds) if seconds < 10 else str(seconds)
    if hour == '00':
        return "{}:{}".format(minute, seconds)
    else:
        return "{}:{}:{}".format(hour, minute, seconds)


def str_to_datatime(str_time, t_format='%Y-%m-%d %H:%M:%S'):
    d = datetime.datetime.strptime(str_time, t_format)
    return d


def get_date(timefrom1970):
    return time.strftime("%Y-%m-%d", time.localtime(timefrom1970))


def get_time(timefrom1970):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timefrom1970))


def get_time2(timefrom1970):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(timefrom1970))


def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def get_now_time2():
    return time.strftime("%Y-%m-%d 00:00:00", time.localtime(time.time()))


def get_now_time3():
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))


def get_now_date():
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))
