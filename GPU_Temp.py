# --------- Imports ---------
from infi.systray import SysTrayIcon
from infi.systray.traybar import PostMessage, WM_CLOSE
from PIL import Image, ImageDraw, ImageFont
import time
import GPUtil
import math
import os.path
import sys


# --------- Global Variables ---------
tray_icon_is_destroyed = False
W, H = 50, 50
FONT_SIZE = 40
TRANSPARENT = (255, 255, 255, 0)
YELLOW = (255, 255, 0)


# --------- Helper Functions ---------
def setup_images():
    # Check if /icons folder exists in current directory
    MYDIR = ("icons")
    CHECK_FOLDER = os.path.isdir(MYDIR)

    # Create the folder if it doesn't exist.
    if not CHECK_FOLDER:
        os.makedirs(MYDIR)

    # For numbers 0-99, create an image of each number as yellow text
    # and save it to /icons folder.
    for index in range(100):
        filename = 'icons/temp_{i}.ico'.format(i=index)
        if os.path.exists(filename):
            continue

        img = Image.new('RGBA', (W, H), color=TRANSPARENT)
        d = ImageDraw.Draw(img)

        font_type = ImageFont.truetype("arial.ttf", FONT_SIZE)
        msg = "{}".format(index)

        d.text((0, 0), msg, fill=YELLOW, font=font_type, align='center')

        img.save(filename)


def get_GPU_temp():
    return math.floor(GPUtil.getGPUs()[0].temperature)


def return_image_by_index(i):
    i = min(99, i)
    return 'icons/temp_{index}.ico'.format(index=i)


# SysTrayIcon functions
def quit_app(systray):
    global tray_icon_is_destroyed
    tray_icon_is_destroyed = True


# --------- MAIN LOOP ---------
def main():
    setup_images()

    # Create and start a SysTrayIcon instance with image of current temperature
    temp = get_GPU_temp()
    systray = SysTrayIcon(return_image_by_index(temp),
                          "GPU Temp: {temp}°".format(temp=temp),
                          on_quit=quit_app)
    systray.start()

    while True:
        try:
            # Close app if user manually quits
            if tray_icon_is_destroyed:
                sys.exit()

            # Every second, grab updated GPU temp and display the corresponding image
            time.sleep(1.5)
            temp = get_GPU_temp()
            systray.update(return_image_by_index(temp),
                           "GPU Temp: {temp}°".format(temp=temp))

        except KeyboardInterrupt:
            systray.shutdown()


if __name__ == "__main__":
    main()
