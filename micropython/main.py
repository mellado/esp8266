#!/bin/python

import network
import sys
from time import sleep
import machine
import dht
import ujson
import http_client2


SSID = ""
PASSWORD = ""
DHT11PIN = ""
URL = ""


def http_get(url):
    r = http_client2.get(url)
    r.raise_for_status()
    print(r.status_code)
    print(r.text)  # r.content for raw bytes


def send_data(url, humidity, temperature):
    r = http_client2.post(url,
                          json={'humidity': str(humidity),
                                'temperature': str(temperature)})
    print(r.json())


def go_sleep():
    # to get this function you have to connect
    # GPIO16 to reset pin
    # (GPIO16 is D0 in the d1 mini board)

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, 10000)

    # put the device to sleep
    machine.deepsleep()


def back_from_sleep():
    # check if the device woke from a deep sleep
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        return True
    return False


def do_connect(ssid, password):
    print('Global variables SSID: "{}", PASSWORD: "{}"'.format(SSID, PASSWORD))
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network "{}"-({})...'.format(ssid, password))
        sta_if.active(True)
        sta_if.connect(ssid, password)
        sleep(1)
        for i in range(8):
            if sta_if.isconnected():
                print('Connected')
                break
            sleep(2)
        if sta_if.isconnected():
            return True
        else:
            print('Could not connect to wifi network')
            return False
    else:
        print('Already connected. Network config:', sta_if.ifconfig())
        return True


def read_dht11(pin=2):
    d = dht.DHT11(machine.Pin(pin))
    d.measure()
    t = d.temperature()
    print("Temperature: {}".format(t))
    h = d.humidity()
    print("Humidity: {}".format(h))
    return (h, t)


def read_config(filename="config.json"):
    global SSID
    global PASSWORD
    global DHT11PIN
    global URL
    f = open(filename, 'r')
    content = f.readall()
    config = ujson.loads(content)
    print(content)
    SSID = config['ssid']
    PASSWORD = config['password']
    DHT11PIN = int(config['dht11pin'])
    URL = config['url']


def blink(times=1):
    p2 = machine.Pin(2, machine.Pin.OUT)
    p2.high()
    for i in range(times):
        sleep(0.2)
        p2.low()
        sleep(0.2)
        p2.high()


if __name__ == "__main__":
    blink(4)
    read_config()
    while True:
        try:
            (humidity, temperature) = read_dht11(DHT11PIN)
            if do_connect(SSID, PASSWORD):
                send_data(URL, humidity, temperature)
                blink(2)
                sleep(60)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            blink(6)
            sleep(10)
