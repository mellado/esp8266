#!/usr/bin/env python3

import os
import xively
import subprocess
import time
import datetime
import requests

# extract feed_id and api_key from environment variables
FEED_ID = "793200265"
API_KEY = "cbamGge7wUmat5b9YlmHwOOAkKBdZjDxnYoHS1oVGhVJ92XJ"
# DEBUG = False
DEBUG = True

# initialize api client
api = xively.XivelyAPIClient(API_KEY)

# function to read 1 minute load average from system uptime command
def read_loadavg():
  if DEBUG:
    print("Reading load average")
  return subprocess.check_output(["awk '{print $1}' /proc/loadavg"], shell=True)

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed, channel, tag):
  try:
    datastream = feed.datastreams.get(channel)
    if DEBUG:
      print("Found existing datastream")
    return datastream
  except:
    if DEBUG:
      print("Creating new datastream")
    datastream = feed.datastreams.create("load_avg", tags=tag)
    return datastream


def publish(channel, tag, value):
  print("Starting Xively tutorial script")

  feed = api.feeds.get(FEED_ID)

  datastream = get_datastream(feed, channel, tag)
  datastream.max_value = None
  datastream.min_value = None

  if DEBUG:
    print("Updating Xively feed channel %s(%s) with value: %s" % (channel, tag, value))

    datastream.current_value = value
    datastream.at = datetime.datetime.utcnow()
    try:
      datastream.update()
    except requests.HTTPError as e:
      print("HTTPError({0}): {1}".format(e.errno, e.strerror))

# main program entry point - runs continuously updating our datastream with the
# current 1 minute load average
def run():
  print("Starting Xively tutorial script")

  feed = api.feeds.get(FEED_ID)

  datastream = get_datastream(feed, "load_avg", "load_01")
  datastream.max_value = None
  datastream.min_value = None

  while True:
    load_avg = read_loadavg()[:-1]
    load_avg = load_avg.decode('utf-8')

    if DEBUG:
      print("Updating Xively feed with value: %s" % load_avg)

    datastream.current_value = load_avg
    datastream.at = datetime.datetime.utcnow()
    try:
      datastream.update()
    except requests.HTTPError as e:
      print("HTTPError({0}): {1}".format(e.errno, e.strerror))

    time.sleep(10)


if __name__ == '__main__':

  run()
