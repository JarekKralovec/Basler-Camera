from pypylon import pylon
import os
from dotenv import load_dotenv, find_dotenv
import cv2
import time


class CameraController:
    def __init__(self, use_env_emulator: bool = True):
        """
        Camera controller for Basler cameras.

        Args:
            use_env_emulator (bool): to load emulator from .env.
        """
        if use_env_emulator:
            dotenv_path = find_dotenv()
            load_dotenv(dotenv_path)
            self.PYLON_CAMEMU = os.getenv("PYLON_CAMEMU")

        # Create camera object
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )

    # -------------------------------
    # Helper: clamps values to ranges
    # -------------------------------
    def _validate(self, val, min_v, max_v, name):
        if val < min_v:
            print(f"{name} was below minimum; setting to {min_v}")
            return min_v
        if val > max_v:
            print(f"{name} was above maximum; setting to {max_v}")
            return max_v
        return val

    # -------------------------------
    # Capture Photo
    # -------------------------------
    def capture_photo(self, gain, exposure, file_name,
                      height, width, y_offset, x_offset):

        # Validate ranges
        gain = self._validate(gain, 0.0, 18.0, "Gain")
        exposure = self._validate(exposure, 20.0, 999000.0, "Exposure")
        height = self._validate(height, 1, 1026, "Height")
        width = self._validate(width, 1, 1282, "Width")

        # Correct offsets if needed
        if width + x_offset > 1282:
            x_offset = 1282 - width
        if height + y_offset > 1026:
            y_offset = 1026 - height

        self.camera.Open()

        # Set camera parameters
        self.camera.Gain.SetValue(gain)
        self.camera.ExposureTime.SetValue(exposure)
        self.camera.Height.SetValue(height)
        self.camera.Width.SetValue(width)
        self.camera.OffsetX.SetValue(x_offset)
        self.camera.OffsetY.SetValue(y_offset)

        # Capture single frame
        self.camera.StartGrabbing(1)
        result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        frame = result.Array
        filename = f"{file_name}.png"
        cv2.imwrite(filename, frame)

        # Display until space pressed
        while True:
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord(' '):
                result.Release()
                self.camera.Close()
                break

    # -------------------------------
    # Capture Video
    # -------------------------------
    def capture_video(self, gain, exposure_time, file_name,
                      seconds, fps, height, width, y_offset, x_offset):

        # Validate ranges
        gain = self._validate(gain, 0.0, 18.0, "Gain")
        exposure_time = self._validate(exposure_time, 10.0, 916000.0, "Exposure")
        height = self._validate(height, 1, 1026, "Height")
        width = self._validate(width, 1, 1282, "Width")

        if width + x_offset > 1282:
            x_offset = 1282 - width
        if height + y_offset > 1026:
            y_offset = 1026 - height

        self.camera.Open()

        # Set camera parameters
        self.camera.Gain.SetValue(gain)
        self.camera.ExposureTime.SetValue(exposure_time)
        self.camera.Height.SetValue(height)
        self.camera.Width.SetValue(width)
        self.camera.OffsetX.SetValue(x_offset)
        self.camera.OffsetY.SetValue(y_offset)

        filename = f"{file_name}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Start grabbing
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        frame = result.Array

        # Create video object
        h, w = frame.shape[:2]
        video = cv2.VideoWriter(filename, fourcc, fps, (w, h))

        start_time = time.time()
        frame_count = 1

        # Loop
        while True:
            if time.time() - start_time > seconds:
                break

            result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            frame = result.Array
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            video.write(frame_rgb)
            cv2.imshow("Frame", frame_rgb)
            result.Release()

            frame_count += 1
            if frame_count / fps > seconds:
                break

            if cv2.waitKey(1) & 0xFF == ord(' '):
                break

        self.camera.StopGrabbing()
        self.camera.Close()