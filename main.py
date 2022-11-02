# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# 192.168.2.21 - bfc03b993301f4a1d2pxje
# 192.168.2.19 - bf26704e6b7bf91f5brgjf
# 192.168.2.20 - bf1b45b6f29f5bd4d1t4tg
import time

import tinytuya as tinytuya

spot1 = tinytuya.BulbDevice("bfc03b993301f4a1d2pxje", "192.168.2.21", "ae0e0692ed4635fc")
spot2 = tinytuya.BulbDevice("bf26704e6b7bf91f5brgjf", "192.168.2.19", "e589342193d4c6fc")
spot3 = tinytuya.BulbDevice("bf1b45b6f29f5bd4d1t4tg", "192.168.2.20", "1749cb5be5a5ae46")

def wakeupLoop(spotList):
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
    while startHue < 0.10:
        for spot in spotList:
            spot.set_hsv(startHue, 1.0, brightness, False)
            # spot.set_brightness(brightness, False)
        startHue += 0.001
        counter += 1
        brightness += 0.01
        print("hue: " + str(startHue) + ", brightness: " + str(brightness))
        time.sleep(2)
    # Transition to white by decreasing saturation
    print("transitioning to white")
    while startSat > 0.6:
        for spot in spotList:
            spot.set_hsv(startHue, startSat, brightness, False)
            startSat -= 0.01
            print("startSat: " + str(round(startSat, 2)))
            time.sleep(2)

    print("color gradient done, switching to white")
    time.sleep(2)
    brightness = 10
    temperature = 10
    spot3.set_colour(255, 180, 0, False)
    spot3.set_brightness(1000, False)
    for spot in spotList[0:2]:
        spot.set_white(brightness, temperature, False)
    print("done with setting white, incrementing now")
    while brightness < 800:
        for spot in spotList[0:2]:
            spot.set_white(brightness, temperature, False)
            brightness += 1
            temperature = round(brightness / 4)
            print("temp: " + str(temperature) + ", brightness: " + str(brightness))
            time.sleep(2)
    print("done with sunrise!")


# Press the green button in the gutter to run the script.
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
    print("spots off waiting 5 seconds before starting the loop. ")
    time.sleep(5)

    wakeupLoop([spot1, spot2, spot3])

    # spot1.set_hsv(0.5, 1.0, 1.0, False)
    # spot2.set_hsv(1, 1, 1)
    # spot3.set_hsv(1, 1, 1)
    # print("done setting hsv")
    #
    # print("spot 1 hsv is ")
    # print(spot1.colour_hsv())

    time.sleep(5)
    spot1.turn_off()
    spot2.turn_off()
    spot3.turn_off()
