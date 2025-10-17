# --------- Imports ---------
from infi.systray import SysTrayIcon
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
YELLOW = (255, 220, 0)
last_update_time = time.time()

TEMP_UPDATE_INTERVAL = 3        # How often to check GPU temperature
RETRY_INTERVAL = 5              # Wait time before retrying after error
WAKE_GRACE_PERIOD = 2           # Wait time after wake from sleep for GPU drivers
SLEEP_DETECTION_THRESHOLD = 10  # Time gap that indicates wake from sleep
MAX_CONSECUTIVE_ERRORS = 3


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
    try:
        return math.floor(GPUtil.getGPUs()[0].temperature)
    except:
        # If GPU reading fails, return None to avoid crash
        return None


def return_image_by_index(i):
    i = min(99, i)
    return 'icons/temp_{index}.ico'.format(index=i)


# SysTrayIcon functions
def quit_app(systray):
    global tray_icon_is_destroyed
    tray_icon_is_destroyed = True


def detect_stale_update():
    """Check if the last update was more than 10 seconds ago"""
    global last_update_time
    current_time = time.time()
    if current_time - last_update_time > SLEEP_DETECTION_THRESHOLD:
        # System likely woke from sleep
        return True
    return False


# --------- MAIN LOOP ---------
def main():
    global last_update_time
    
    setup_images()

    # Create and start a SysTrayIcon instance with image of current temperature
    temp = get_GPU_temp()
    system_tray_icon = SysTrayIcon(
        return_image_by_index(temp),
        "GPU Temp: {temp}\u00b0C".format(temp=temp),
        on_quit=quit_app)
    system_tray_icon.start()

    consecutive_errors = 0

    while True:
        try:
            # Close app if user manually quits
            if tray_icon_is_destroyed:
                sys.exit()

            # Check if we missed updates (wake from sleep detection)
            if detect_stale_update():
                print("Wake from sleep detected - refreshing GPU data")
                time.sleep(WAKE_GRACE_PERIOD)  # Give GPU drivers time to wake up

            # Grab updated GPU temp and display the corresponding image
            time.sleep(TEMP_UPDATE_INTERVAL)
            temp = get_GPU_temp()
            
            # Reset error counter on successful read
            if temp is not None:
                consecutive_errors = 0
            else:
                consecutive_errors += 1
                
            # If too many consecutive errors, wait longer before retry
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"GPU read errors detected, waiting {RETRY_INTERVAL} seconds...")
                time.sleep(RETRY_INTERVAL)
                consecutive_errors = 0
                continue
            
            # Only update if we have a valid temperature
            if temp is not None:
                system_tray_icon.update(
                    return_image_by_index(temp),
                    "GPU Temp: {temp}°".format(temp=temp))
                
                # Update the last successful update time
                last_update_time = time.time()

        except KeyboardInterrupt:
            system_tray_icon.shutdown()
        except Exception as e:
            print(f"Error updating temperature: {e}")
            time.sleep(RETRY_INTERVAL)  # Wait before retrying


if __name__ == "__main__":
    main()
