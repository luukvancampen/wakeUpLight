# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# 192.168.2.21 - bfc03b993301f4a1d2pxje
# 192.168.2.19 - bf26704e6b7bf91f5brgjf
# 192.168.2.20 - bf1b45b6f29f5bd4d1t4tg
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import datetime
import tinytuya as tinytuya
import time

runningSunrise = True

spot1 = tinytuya.BulbDevice("bfc03b993301f4a1d2pxje", "192.168.2.14", "6031f2248efb8b4e")
spot2 = tinytuya.BulbDevice("bf26704e6b7bf91f5brgjf", "192.168.2.17", "38da5b10e4931137")
spot3 = tinytuya.BulbDevice("bf1b45b6f29f5bd4d1t4tg", "192.168.2.16", "01da56820582a042")

# the time at which the sunrise should start. This time will be modified by the http handler in order to change the
# schedule and it will be read by the wakeupLoop thread in order to start at the correct time.
sunriseTime = datetime.time(hour=7, minute=0)

def time_plus(time, timedelta):
    start = datetime.datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()

def wakeupLoop(threadName, spotList):
    global runningSunrise
    while True:
        if sunriseTime >= datetime.datetime.now().time() and not datetime.datetime.now().time() < time_plus(sunriseTime, datetime.timedelta(minutes=5)) and runningSunrise:
            print("started the loop.")
            startHue = 0.0
            startSat = 1.0
            brightness = 0.01
            counter = 0
            for spot in spotList:
                # spot.set_brightness(25, False)
                spot.set_hsv(startHue, 1.0, brightness, False)
                spot.turn_on(False)
                print(spot)

            time.sleep(10)
            while startHue < 0.10 and runningSunrise:
                for spot in spotList:
                    spot.set_hsv(startHue, 1.0, brightness, False)
                    # spot.set_brightness(brightness, False)
                startHue += 0.001
                counter += 1
                brightness += 0.01
                print("hue: " + str(startHue) + ", brightness: " + str(brightness))
                time.sleep(6)
            # Transition to white by decreasing saturation
            print("transitioning to white")
            while startSat > 0.6 and runningSunrise:
                for spot in spotList:
                    spot.set_hsv(startHue, startSat, brightness, False)
                    startSat -= 0.01
                    print("startSat: " + str(round(startSat, 2)))
                    time.sleep(6)

            print("color gradient done, switching to white")
            if runningSunrise:
                time.sleep(2)
                brightness = 10
                temperature = 10
                spot3.set_colour(255, 180, 0, False)
                spot3.set_brightness(1000, False)
                for spot in spotList[0:2]:
                    spot.set_white(brightness, temperature, False)
                print("done with setting white, incrementing now")
            while brightness < 800 and runningSunrise:
                for spot in spotList[0:2]:
                    spot.set_white(brightness, temperature, False)
                    brightness += 1
                    temperature = round(brightness / 4)
                    print("temp: " + str(temperature) + ", brightness: " + str(brightness))
                    time.sleep(1)
            print("done with sunrise!")
            if runningSunrise:
                time.sleep(600)
            spot1.turn_off()
            spot2.turn_off()
            spot3.turn_off()
        else:
            # sleep 5 seconds to be a lit less computation intensive
            time.sleep(5)


def parseTime(time_):
    timeString = str(time_)
    if len(timeString) == 3:
        hours = timeString[0]
        minutes = timeString[1] + timeString[2]
        if int(hours) > 23:
            return datetime.datetime.now(), False
        if int(minutes) > 59:
            return datetime.datetime.now(), False
        return datetime.time(hour=int(hours), minute=int(minutes)), True
    elif len(timeString) == 4:
        hours = timeString[0] + timeString[1]
        minutes = timeString[2] + timeString[3]
        if int(hours) > 23:
            return datetime.datetime.now(), False
        if int(int(minutes) > 59):
            return datetime.datetime.now(), False
        return datetime.time(hour=int(hours), minute=int(minutes)), True
    else:
        return datetime.datetime.now(), False


def subtractHalfHour(time_):
    newMinute = 0
    newHour = 1
    if time_.minute - 30 < 0:
        newHour = time_.hour - 1
        newMinute = 60 + (time_.minute - 30)
    else:
        newMinute = time_.minute - 30
        newHour = time_.hour
    return datetime.time(hour=newHour, minute=newMinute)

class requestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/light/':
            content_length = int(self.headers['content-length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()

            json_ = body.decode('utf-8').replace("'", '"')
            data = json.loads(json_)
            s = json.dumps(data, indent=4, sort_keys=True)
            print(s)
            parsedTime = parseTime(data["time"])
            if parsedTime[1]:
#               we received a valid time, so now set the sunrisetime.
                global sunriseTime
                global runningSunrise
                sunriseTime = subtractHalfHour(parsedTime[0])
                runningSunrise = True
                self.send_response(200)
            else:
                self.send_response(406)
                self.end_headers()
                self.wfile.write(b'Light off!')

    def do_GET(self):
        if self.path == '/light/stop':
            global runningSunrise
            runningSunrise = False
            self.send_response(200)

if __name__ == '__main__':
    spotList = [spot1, spot2, spot3]

    for spot in spotList:
        print("initializing...")
        spot.set_version(3.3)
        spot.set_socketPersistent(True)
        spot.set_socketRetryLimit(3)
        spot.set_socketTimeout(5)

    spot1.turn_off(False)
    spot2.turn_off(False)
    spot3.turn_off(False)
    print("serving!")



    print("HTTP server started...")
    sunriseThread = threading.Thread(target=wakeupLoop, args=("wakeupLoop", spotList,))
    sunriseThread.start()
    print("sunrise thread started!")

    httpd = HTTPServer(('192.168.2.12', 2000), requestHandler)
    httpd.serve_forever()

    # wakeupLoop([spot1, spot2, spot3])
