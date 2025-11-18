from pypylon import pylon
import os
from dotenv import load_dotenv, find_dotenv
import cv2
import time

#comment this section out when NOT using emulator
dotenv_path = find_dotenv()
print(dotenv_path)
load_dotenv(dotenv_path)
PYLON_CAMEMU = os.getenv("PYLON_CAMEMU")

#create camera object
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())


def capture_photo(gain: float, exposure: float, file_name: str, height: int, width: int, y_offset: int, x_offset: int):

    """
    Captures a single frame from the camera and saves it to a file.

    Parameters:
        gain (float): Gain value between 0.0 - 18.0.
        exposure (float): Exposure time value between 20.0 - 999000.0.
        file_name (str): File name (without extension).
        height (int): Height value between 1 - 1026.
        width (int): Width value 1 - 1282.
        y_offset (int): Offset value for y axis.
        x_offset (int): Offset value for x axis.
    """

    # open camera and set parameters (within bounds of camera specifications)
    if gain > 18.0:
        gain = 18.0
        print("Gain was outside of range and has been set to max")
    elif gain < 0.0:
        gain = 0.0
        print("Gain was outside of range and has been set to min")
    if exposure > 999000.0:
        exposure = 999000.0
        print("Exposure was outside of range and has been set to max")
    elif exposure < 20.0:
        exposure = 20.0
        print("Exposure was outside of range and has been set to min")
    if height > 1026:
        height = 1026
        print("Height was outside of range and has been set to max")
    elif height < 1:
        height = 1
        print("Height was outside of range and has been set to min")
    if width > 1282:
        width = 1282
        print("Width was outside of range and has been set to max")
    elif width < 1:
        width = 1
        print("Width was outside of range and has been set to min")
    if width + x_offset > 1282:
        x_offset = 1282 - width
    if height + x_offset > 1026:
        y_offset = 1026 - height


    camera.Open()
    camera.Gain.SetValue(gain)
    camera.ExposureTime.SetValue(exposure)
    camera.Height.SetValue(height)
    camera.Width.SetValue(width)
    camera.OffsetX.SetValue(x_offset)
    camera.OffsetY.SetValue(y_offset)
    # grab single frame to store
    camera.StartGrabbing(1)

    # save image data to file and close camera
    result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    frame = result.Array
    filename = file_name + ".png"
    cv2.imwrite(filename, frame)

    #Displays the image in window until key (space) is pressed
    while True:
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            result.Release()
            camera.Close()
            break




print(camera.ExposureTime.GetMin(), camera.ExposureTime.GetMax())


def capture_video(gain: float, exposure_time: float, file_name: str, seconds: int, fps: int, height: int, width: int, y_offset: int, x_offset: int):
    camera.Open()

    """
    Captures a video of a given time and frame rate from the camera and saves it to a file.

    Parameters:
        gain (float): Gain value.
        exposure_time (float): Exposure time value.
        file_name (str): File name (without extension).
        seconds (int): Number of seconds to capture.
        fps (int): Frames per second.
        height (int): Height value between 1 - 1026.
        width (int): Width value 1 - 1282.
        y_offset (int): Offset value for y axis.
        x_offset (int): Offset value for x axis.
        
    """
    if gain > 18.0:
        gain = 18.0
        print("Gain was outside of range and has been set to max")
    elif gain < 0.0:
        gain = 0.0
        print("Gain was outside of range and has been set to min")
    if exposure_time > 916000.0:
        exposure_time = 916000.0
        print("Exposure was outside of range and has been set to max")
    elif exposure_time < 10.0:
        exposure_time = 10.0
        print("Exposure was outside of range and has been set to min")
    if height > 1026:
        height = 1026
        print("Height was outside of range and has been set to max")
    elif height < 1:
        height = 1
        print("Height was outside of range and has been set to min")
    if width > 1282:
        width = 1282
        print("Width was outside of range and has been set to max")
    elif width < 1:
        width = 1
        print("Width was outside of range and has been set to min")
    if width + x_offset > 1282:
        x_offset = 1282 - width
    if height + x_offset > 1026:
        y_offset = 1026 - height
    #set parameters
    camera.Gain.SetValue(gain)
    camera.ExposureTime.SetValue(exposure_time)
    camera.Height.SetValue(height)
    camera.Width.SetValue(width)
    camera.OffsetX.SetValue(x_offset)
    camera.OffsetY.SetValue(y_offset)


    filename = file_name + ".mp4"

    #set video type
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore

    # stores the first frame
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    frame = result.Array

    height, width = frame.shape[:2]
    video = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    #Checks how long code has been running and ends process
    initial_time = time.time()

    # loops capture process for given time
    total_frame_count = 1
    while True:
        if time.time() - initial_time > seconds:
            camera.StopGrabbing()
            camera.Close()
            break

        result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        frame = result.Array

        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        video.write(frame)
        result.Release()
        cv2.imshow("Frame", frame)
        total_frame_count += 1.0

        if total_frame_count / fps > seconds:
            camera.StopGrabbing()
            camera.Close()
            break
        if cv2.waitKey(1) & 0xFF == ord(' '):
            camera.StopGrabbing()
            camera.Close()
            break





#capture_video(5.0, 10000.0, "test_video2", 5, 60,30,1282,100, 0)
#time.sleep(5)
#capture_photo(5.0, 10000.0, "test_image", 50,200,30,30)



