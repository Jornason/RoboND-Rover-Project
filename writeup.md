## Project: Search and Sample Return
---

**Robotics Software Engineer Nanodegree**

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points

**Required files for project submission:**

- [Jupyter Notebook with test code](https://github.com/Jornason/RoboND-Rover-Project/blob/master/code/Rover_Project_Test_Notebook.ipynb)

- [Test output video](https://github.com/Jornason/RoboND-Rover-Project/blob/master/output/test_mapping.mp4)

- [Autonomous navigation scripts](https://github.com/Jornason/RoboND-Rover-Project/tree/master/code)

  ​



**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  



![rover_image](http://owj75jsw8.bkt.clouddn.com/2018-03-19-153819.jpg)



![example_grid1](http://owj75jsw8.bkt.clouddn.com/2018-03-19-153816.jpg)



![example_rock1](http://owj75jsw8.bkt.clouddn.com/2018-03-19-153826.jpg)



### Notebook Analysis

locate here: https://github.com/Jornason/RoboND-Rover-Project/tree/master/code/Rover_Project_Test_Notebook.ipynb

#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
function 'color_thresh' added for identify navigable terrain,  since threshold of RGB > 160 does a nice job of identifying ground pixels only

```python
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

```

![robocam_2017_05_02_11_16_21_421](http://owj75jsw8.bkt.clouddn.com/2018-03-19-165715.jpg)



function 'find_obstacles' added for identify obstacles

```python
#Find obstacles
def find_obstacles(img, rgb_thresh=(160, 160, 160)):
    
    color_select = np.zeros_like(img[:,:,0])
    
    has_val = (img[:,:,0] > 0) \
              & (img[:,:,1] > 0) \
              & (img[:,:,2]> 0)
            
    # Require that each pixel be below all three threshold values in RGB
    below_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
            
    # Index the array of zeros with the boolean array and set to 1
    color_select[below_thresh] = 1
    color_select = color_select*has_val
    
    # Return the binary image
    return color_select
```



function 'find_rocks' added for identify rocks,

```python
def find_rocks(img, levels=(110, 110, 50)):

    rock_pix = (img[:,:,0] > levels[0]) \
                & (img[:,:,1] > levels[1]) \
                & (img[:,:,2] < levels[2])

    rock_map = np.zeros_like(img[:,:,0])
    rock_map[rock_pix] = 1

    return rock_map
```

![example_rock2](http://owj75jsw8.bkt.clouddn.com/2018-03-19-165717.jpg)



![example_rock2](http://owj75jsw8.bkt.clouddn.com/2018-03-19-165710.jpg)





#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
1) Define source and destination points for perspective transform

```python
    dst_size = 5 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                      [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                      ])

```

![example_grid1](http://owj75jsw8.bkt.clouddn.com/2018-03-19-170029.jpg)



2) Apply perspective transform

```python
warped = perspect_transform(img, source, destination)
```

![warped_example](http://owj75jsw8.bkt.clouddn.com/2018-03-19-170026.jpg)



3) Apply color threshold to identify navigable terrain/obstacles/rock samples

```python
    threshed_terrain = color_thresh(warped)    
    threshed_rock = find_rocks(warped)
    threshed_obstacle = find_obstacles(warped)    
```

4) Convert thresholded image pixel values to rover-centric coords

```python
    xpix, ypix = rover_coords(threshed_terrain)
    rock_x, rock_y = rover_coords(threshed_rock)
    obsxpix, obsypix = rover_coords(threshed_obstacle)
```

5) Convert rover-centric pixel values to world coords

```python
    world_size = data.worldmap.shape[0]
    scale = 2 * dst_size
    xpos = data.xpos[data.count]
    ypos = data.ypos[data.count]
    yaw = data.yaw[data.count]
    
    x_world, y_world = pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale)
    obs_x_world, obs_y_world = pix_to_world(obsxpix, obsypix, xpos, ypos, yaw, world_size, scale)
    rock_x_world, rock_y_world = pix_to_world(rock_x, rock_y, xpos, ypos, yaw, world_size, scale)    
```

6) Update worldmap (to be displayed on right side of screen)

```python
    data.worldmap[obs_y_world, obs_x_world, 0] += 1        
    data.worldmap[rock_y_world, rock_x_world, 1] += 1
    data.worldmap[y_world, x_world, 2] += 10
```

the output video can be found

```
output/test_mapping.mp4
```

![屏幕快照 2018-03-20 上午12.53.33](http://owj75jsw8.bkt.clouddn.com/2018-03-19-165355.jpg)



### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

in 'perception_step' function  in  https://github.com/Jornason/RoboND-Rover-Project/blob/master/code/perception.py

1) Define source and destination points for perspective transform

```python
    dst_size = 5
    bottom_offset = 6
    image = Rover.vision_image
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])

```

2) Apply perspective transform

```python
warped = perspect_transform(Rover.img, source, destination)
```

3) Apply color threshold to identify navigable terrain/obstacles/rock samples

```python
    threshed_terrain = color_thresh(warped)
    threshed_rock = find_rocks(warped, levels =(110,110,50))
    threshed_obstacle = find_obstacles(warped)    
```

4) Update Rover.vision_image (this will be displayed on left side of screen)

```python
    Rover.vision_image[:,:,0] = threshed_obstacle * 255
    Rover.vision_image[:,:,1] = threshed_rock * 255
    Rover.vision_image[:,:,2] = threshed_terrain * 255
```

5) Convert map image pixel values to rover-centric coords

```python
    xpix, ypix = rover_coords(threshed_terrain)
    rock_x, rock_y = rover_coords(threshed_rock)
    obsxpix, obsypix = rover_coords(threshed_obstacle)
```

6) Convert rover-centric pixel values to world coordinates

```python
    world_size = Rover.worldmap.shape[0]
    scale = 2 * dst_size
    xpos = Rover.pos[0]
    ypos = Rover.pos[1]
    yaw = Rover.yaw

    x_world, y_world = pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale)
    obs_x_world, obs_y_world = pix_to_world(obsxpix, obsypix, xpos, ypos, yaw, world_size, scale)
    rock_x_world, rock_y_world = pix_to_world(rock_x, rock_y, xpos, ypos, yaw, world_size, scale)    
```

7) Update Rover worldmap (to be displayed on right side of screen)

```python
        Rover.worldmap[obs_y_world, obs_x_world, 0] += 1
        Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        Rover.worldmap[y_world, x_world, 2] += 1
```

8) Convert rover-centric pixel positions to polar coordinates

```python
    dist, angles = to_polar_coords(xpix, ypix)
```

Update Rover pixel distances and angles

```python
Rover.nav_angles = angles
```

See if we can find rock samples

```python
    if threshed_rock.any(): 
        rock_dist, rock_ang = to_polar_coords(rock_x, rock_y)
        rock_idx = np.argmin(rock_dist)
        rock_xcen = rock_x_world[rock_idx]
        rock_ycen = rock_y_world[rock_idx]

        Rover.worldmap[rock_ycen, rock_xcen, 1] = 255
        Rover.near_sample = 1
        #Uptdates Rover angles towards Gold,if there is
        Rover.samples_pos = [rock_ang,rock_dist]
        Rover.found_rock = True;

    else:
        Rover.vision_image[:,:,1] = 0
        Rover.near_sample = 0
        Rover.found_rock = False;
```



the 'decision_step'  function in https://github.com/Jornason/RoboND-Rover-Project/tree/master/code/decision.py

I design a state machine to describe the behavior of rover in different mode.

for osx(omnigraffle):https://github.com/Jornason/RoboND-Rover-Project/blob/master/state-machine.graffle

for windows(visio):https://github.com/Jornason/RoboND-Rover-Project/blob/master/state-machine.vdx



![state-machine](http://owj75jsw8.bkt.clouddn.com/2018-03-21-063048.jpg)



```python
def decision_step(Rover): 
    if Rover.nav_angles is not None:
        if Rover.mode == 'start':
            initialAction(Rover)               
        if Rover.mode == 'sample':
            sampleAction(Rover)
        if Rover.mode == 'forward':
            forwardAction(Rover) # Forward in all glory!
        if Rover.mode == 'stop':
            stopAction(Rover) # Bring the rover to a stop
        if Rover.mode == 'seek':
            seekAction(Rover) # Find a path to start the Rover again         
    return Rover
```



When in `start` mode the robot turns in a programmed direction and moves to the wall.When it reaches it, it goes into the `seek` mode.

```python
def initialAction(Rover):
    if 90 < Rover.yaw < 95:
        Rover.throttle = Rover.throttle_set
        Rover.brake = 0
        Rover.steer = 0
        if len(Rover.nav_angles) < Rover.go_forward:
            Rover.mode = 'seek'
    else:
        Rover.brake = 0
        Rover.throttle = 0
        if Rover.yaw < 90  or Rover.yaw >= 270:            
            Rover.steer = 10 
        else:
            Rover.steer = -10

```

When in `seek` mode, the robot enters a state, to looks for possible paths to move to( ie. enter `forward` mode) as seen in the `seekAction()` function. It also checks if a sample is near and enter `sample` mode.

```python
def seekAction(Rover):
    if Rover.near_sample == 1 and Rover.vel == 0:
        Rover.mode = 'sample'
    else:
        if len(Rover.nav_angles) < Rover.go_forward:
            Rover.throttle = 0
            Rover.brake = 0
            Rover.steer = -15
        if len(Rover.nav_angles) >= Rover.go_forward:
            Rover.throttle = Rover.throttle_set
            Rover.brake = 0
            Rover.mode = 'forward'
```

The `forward` mode initializes the wall crawler. It moves next to the wall at a given offset, to accord for the rough terrain near the walls.

```python
def forwardAction(Rover):
    if Rover.near_sample == 1:
        Rover.mode = 'stop'
    if len(Rover.nav_angles) >= Rover.stop_forward:
        if Rover.vel < Rover.max_vel:
            Rover.throttle = Rover.throttle_set
        else:
            Rover.throttle = 0
        Rover.brake = 0
        Rover.steer = np.max((Rover.nav_angles) * 180 / np.pi) - 30 # minus wall offset
    else:
        Rover.mode = 'stop'
```

The `stop` mode does exactly that, stops the rover and enter `seek` mode.

```python
def stopAction(Rover):
    if Rover.vel > 0.2:
        Rover.throttle = 0
        Rover.brake = Rover.brake_set
        Rover.steer = 0
    elif Rover.vel < 0.2:
        Rover.mode = 'seek'
```

The `sample` mode is used for sample picking.

```python
def sampleAction(Rover):
    rock_ang = Rover.samples_pos[0][-1]
    rock_dist = Rover.samples_pos[1][-1]
    print(rock_ang,rock_dist)
    if Rover.near_sample == 0:
        Rover.mode = 'stop'
    elif (rock_dist < Rover.min_dist_sample) and (not Rover.picking_up):
        Rover.send_pickup = True
    else:
        Rover.mode = 'forward'
```



#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

The robot takes the “keep turning left” strategy to explore the around 60% of the world map, still has some potential to increase the map discovery percent.

Sometimes the robot finds the golden rock and be quite close to it, but fails to pick up, In worse case, the robot may stuck around the rock.

If I've solved the functional problems, I'll try to revised it to pick all of the rocks and navigating the whole map. This should be tested in osx/windows in different resolutions

| resolutions(osx) | FPS  | map discovery percent | number of picked rocks |
| ---------------- | ---- | --------------------- | ---------------------- |
| 640 x 480        | 40   |                       |                        |
| 800 x 600        |      |                       |                        |
| 1024 x 768       |      |                       |                        |
| 1280 x 800       |      |                       |                        |
| 1440 x 900       |      |                       |                        |
| 1680 x 1050      |      |                       |                        |
| 2048 x 1280      |      |                       |                        |
| 2560 x 1600      |      |                       |                        |
| 2880 x 1800      |      |                       |                        |

resolutions(windows) ...





### Simulator settings

| Resolution(osx) | Graphics quality | FPS  |
| --------------- | ---------------- | ---- |
| 640x480         | Fantastic        | 40   |