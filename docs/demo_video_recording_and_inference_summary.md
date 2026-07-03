# Robot-like Demo Video Recording and Inference Summary

## 1. Purpose

This document summarizes the recording, testing, and final selection process for the robot-like demo video.

The purpose of the demo was to simulate a robot camera view and test how the trained YOLO detection models perform on real recorded video input. The videos were used to generate final visual results for both binary detection and multi-class detection.

The demo video evaluation was not only used to show the final detection result, but also to understand how different camera movement strategies, object layouts, and recording conditions affect detection stability and presentation quality.

---

## 2. Demo Video Recording Setup

Several demo videos were recorded using a phone camera. The video contents were generally similar, but they differed in:

- camera movement strategy
- viewing direction
- rotation angle
- object layout
- number and type of visible objects
- visual completeness of the final scene

Some later versions also added more objects or replaced objects with items that were closer to the target categories in the dataset. These later recordings were used to improve the representativeness and visual quality of the final demo.

The tested videos included examples such as:

```text
video_1_fast.MOV
video_2_spin.MOV
video_3_stay.MOV
video_11.MOV
video_33.MOV
video_111.MOV
video_333.MOV
video_3333.MOV
video_33333.MOV
```

These videos were used internally to compare which recording strategy and object layout were most suitable for the final presentation.

---

## 3. Recording Strategies Tested

Three main recording strategies were tested during the demo preparation stage.

### 3.1 Strategy 1: Straight and Steady Fast Scanning

In the first strategy, the camera moved along a relatively straight line at a steady but relatively fast speed.

Purpose:

```text
Scan all target objects along one direction with stable camera movement.
```

Observation:

The result was acceptable because the movement direction was stable. Although the camera moved relatively fast, the video did not contain strong rotation or severe shaking. Therefore, the model could still detect several objects reasonably well.

Limitation:

Fast movement can reduce the number of clear frames for each object, especially for small objects. If an object only appears for a short time, the model may miss it or produce unstable bounding boxes.

---

### 3.2 Strategy 2: Large Rotation and Turning Motion

In the second strategy, the camera used larger turning and rotating movements to capture objects from different angles.

Initial idea:

```text
More viewing angles might help the model recognize objects better.
```

Observation:

In practice, this strategy did not consistently produce better results. The larger rotation introduced more camera shake and motion blur. As a result, the detection quality became less stable.

Main limitation:

```text
Large rotation can reduce image clarity and make object boundaries blurred.
```

This shows that more viewing angles do not necessarily improve detection if they also introduce motion blur and unstable camera movement.

---

### 3.3 Strategy 3: Slight Rotation, Slow Movement, and Short Pauses Near Objects

In the third strategy, the camera moved more slowly with slight turning. When an object entered the camera view, the camera paused briefly before moving on.

Purpose:

```text
Simulate a robot slowing down or stopping near a detected object.
```

Observation:

This strategy produced stable detection results in several tests. The short pause allowed objects to remain visible and clear for more frames, which helped both binary and multi-class models produce more stable detections.

However, the final uploaded demo video was not selected only based on this recording strategy. The final selection also considered overall scene completeness, object coverage, visual presentation quality, and teammate feedback.

---

## 4. Later Video Variants

After the first three basic recording strategies, additional video versions were recorded.

These later versions were used to:

- test different viewing directions
- add more objects
- include objects closer to the dataset categories
- improve the final demo layout
- make the visual presentation more complete
- find a video that works reasonably well for both binary and multi-class outputs

The later variants helped refine the final demo setup. Some videos were better for detection stability, while others were better for visual presentation and object coverage.

---

## 5. Binary and Multi-class Demo Evaluation

The recorded videos were tested with both binary and multi-class detection models.

### Binary Detection

Binary detection is easier because the model only needs to identify whether a target object exists. Therefore, it generally produced more stable results.

### Multi-class Detection

Multi-class detection is more difficult because the model needs to predict the specific category of each object. In the demo videos, the multi-class results were not perfect across all recordings. Some objects were missed or classified less reliably, especially when the camera moved too quickly, when objects were small, or when the image was blurred.

However, the demo videos were still useful for evaluating how the final model behaves in a practical robot-like camera scenario.

---

## 6. Final Demo Video Selection Criteria

The final demo video was selected based on a combination of practical and presentation-oriented criteria.

The selection criteria included:

| Criterion | Meaning |
|---|---|
| Multi-class detection result | The final project target is multi-class detection, so this was an important factor |
| Binary detection result | Used as an additional reference |
| Visual completeness | The video should show the scene and target objects clearly |
| Object coverage | The video should include enough representative objects |
| Visual clarity | Objects should be clear and not heavily blurred |
| Stable camera movement | The camera should not shake or rotate too strongly |
| Presentation quality | The final output should be easy to understand in the final demonstration |
| Team feedback | The final selected video should also match the team's presentation preference |

The final selected video was chosen because it provided a better overall presentation, showed the demo scene more completely, and was considered more suitable for final demonstration after discussion with teammates.

---

## 7. Important Clarification

During internal testing, the strategy with slight rotation, slow movement, and short pauses near objects often produced relatively stable detection results. This observation is still useful for analyzing future robot deployment.

However, the final selected demo video was not chosen only because it followed this exact strategy. The final video was selected based on overall demo quality, including object coverage, visual completeness, detection result, and teammate feedback.

Therefore, the final conclusion should be stated as:

```text
Short pauses and stable movement are beneficial for detection stability, but the final demo video was selected based on the overall balance between detection performance and presentation quality.
```

---

## 8. Main Observation

The main observations from the demo recording process are:

1. Stable camera movement generally helps detection.
2. Large rotation can introduce motion blur and camera shake.
3. Short pauses near objects can make detections more stable because objects remain clear for more frames.
4. A video that is best for detection stability is not always the best final presentation video.
5. The final demo should balance detection quality, object coverage, visual clarity, and presentation quality.

This means that video selection for final demonstration should not be based only on one technical criterion. It should consider both model behavior and how clearly the result can be presented.

---

## 9. Implication for Robot Deployment

The demo provides a useful implication for later robot deployment.

If the robot camera moves too quickly or rotates strongly, the captured image may become blurred, and the detection model may miss objects or produce unstable results.

A better strategy for robot deployment is:

```text
move smoothly
detect possible target objects
slow down or stop near the object when necessary
capture clearer frames
then continue moving
```

This suggests that the robot may achieve better detection performance if it slows down or briefly stops when an object is detected.

At the same time, for final demonstration, the selected video should also show enough objects and provide a clear overall view of the scene.

---

## 10. Conclusion

Multiple demo videos were recorded and tested with different camera movement strategies and object layouts. The results showed that the recording strategy and video quality have a clear influence on detection performance and presentation quality.

The main conclusions are:

1. Straight and stable movement can produce acceptable results.
2. Large rotation does not necessarily improve detection and can make the result worse due to motion blur and camera shake.
3. Slight rotation with slower movement and short pauses can improve detection stability.
4. Binary detection was generally more stable, while multi-class detection was more challenging.
5. The final selected demo video was chosen based on the overall balance between detection result, object coverage, visual clarity, presentation quality, and teammate feedback.
6. For future robot deployment, slowing down or stopping near detected objects is likely to improve detection reliability.

Final conclusion:

```text
Stable camera movement and short pauses are useful for improving detection stability, but the final demo video should be selected based on both detection performance and presentation quality.
```

---

## 11. Suggested Report Text

The following paragraph can be used in the final report or presentation:

```text
Several demo videos were recorded to simulate a robot camera view. The videos used different recording strategies, including straight scanning, large rotation, and slower movement with short pauses near target objects. The results showed that strong rotation can introduce motion blur and camera shake, which reduces detection stability. In contrast, stable movement and short pauses near objects can provide clearer frames and improve detection reliability.

However, the final uploaded demo video was selected not only based on one recording strategy, but also based on overall presentation quality, object coverage, visual clarity, detection result, and teammate feedback. Although multi-class detection was still more challenging than binary detection in the recorded videos, the selected final demo provided the best overall balance for presentation.
```

---

## 12. Recommended Repository Location

This document is part of the final demo documentation and can be placed under the existing documentation folder:

```text
docs/demo_video_recording_and_inference_summary.md
```

If final demo videos are uploaded, only the selected final binary and multi-class output videos should be uploaded to avoid adding many similar large video files to the repository. The other recorded videos were used for internal comparison and selection.
