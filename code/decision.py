import numpy as np
import time





def stopAction(Rover):
    if Rover.vel > 0.2:
        Rover.throttle = 0
        Rover.brake = Rover.brake_set
        Rover.steer = 0
    elif Rover.vel < 0.2:
        Rover.mode = 'seek'
            
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
        # Rover.steer = 10        
        # Rover.throttle = Rover.throttle_seek   


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
