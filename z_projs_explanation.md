# Explanation of Z-Projection

In `extract_metadata.py`, the functions `calculate_z_projs` and `calculate_z_projs_vectorized` can be used to calculate `z_projs`. In this document a brief explanation is provided about the theory behind the functions.

## Abstract

We are interested in finding the near bounds and far bounds of every camera in the scene. A given camera can see a particular subset of the points in the scene. 

## Theory 

<Intro>. Let us assume that we are currently in a camera coordinate system 'C'. Let us also assume that there is a point `p` in this camera coordinate system. 

The Z-Axis of the camera coordinate system is also direction at which the camera is looking at. The projection of the point `p` onto the Z-Axis gives a point `z` on the Z-Axis that is closest to `p`. We can also get the distance `d` from the origin of the camera coodinate system to the point `z`.

Now, let us assume we have multiple points {p1, p2, ..., pn}. The projection of the all these points onto the Z-Axis will give us the points 