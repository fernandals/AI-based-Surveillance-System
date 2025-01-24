
# AI-Based Surveillance System

A smart surveillance system using Raspberry Pi for suspicious sound detection and object recognition, with real-time alerts via Telegram.

## Model Downloads

To run the system, download the necessary models:

- **Audio classification model:**
  ```sh
  wget https://storage.googleapis.com/mediapipe-models/audio_classifier/yamnet/float32/latest/yamnet.tflite
  ```

- **Object detection model:**
  ```sh
  wget -q -O efficientdet.tflite https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite
  ```

This system leverages AI models to detect suspicious sounds and analyze captured images, ensuring enhanced security monitoring through an efficient and cost-effective solution.
