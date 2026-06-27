# Frequently Asked Questions

### What model does the AI service use?
The system utilizes YOLOv8/v9 models (referred to as YOLO26 in the configuration) fine-tuned for vehicle categorization and head/helmet detection.

### Can the system run without a GPU?
Yes, it automatically falls back to CPU execution if CUDA is not detected. However, video processing frame rates will be lower.

### How does the speed estimation work?
The speed estimation calculates the displacement of the vehicle's bounding box over consecutive frames, mapped against a calibrated pixel-per-meter ratio.
