#!/bin/python

import network
import socket
from time import sleep
import machine
import dht
import ujson

SSID = ""
PASSWORD = ""
DHT11PIN = ""


def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' %
                 (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break


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


def do_connect(ssid=SSID, password=PASSWORD):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        sleep(1)
        for i in range(5):
            if sta_if.isconnected():
                print('connected')
                break
            sleep(1)
        if sta_if.isconnected():
            return True
        else:
            print('Could not connect to wifi network')
            return False
    else:
        print('network config:', sta_if.ifconfig())
        return True


def read_dht11(pin=2):
    d = dht.DHT11(machine.Pin(pin))
    d.measure()
    t = d.temperature()
    print("Temperature: {}".format(t))
    h = d.humidity()
    print("Humidity: {}".format(h))
    return (t, h)


def read_config(filename="config.json"):
    global SSID
    global PASSWORD
    global DHT11PIN
    f = open(filename, 'r')
    config = ujson.loads(f.readall())

# edit the data
    SSID = config['ssid']
    PASSWORD = config['password']
    DHT11PIN = int(config['dht11pin'])


if __name__ == "__main__":
    read_config()
    read_dht11(DHT11PIN)
    if do_connect():
        http_get('http://micropython.org/ks/test.html')

    # go_sleep()
