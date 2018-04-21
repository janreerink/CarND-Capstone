
GAS_DENSITY = 2.858
ONE_MPH = 0.44704

from yaw_controller import YawController
from lowpass import LowPassFilter
from pid import PID

class Controller(object):
    def __init__(self, vehicle_mass, fuel_capacity, brake_deadband, decel_limit, accel_limit,
    wheel_radius, wheel_base, steer_ratio, max_lat_accel, max_steer_angle):
        
        self.yaw_controller = YawController(wheel_base, steer_ratio, 0.1, max_lat_accel, max_steer_angle)
        kp = 0.3 #proportional term
        ki = 0.1 #integrative term
        kd = 0 #diff term
        mn = 0 #min throttle
        mx = 0.2 # max throttle
        
        self.throttle_controller = PID(kp, kid, kd, mn, mx)
        
        tau = 0.5 # cutoff frequency( 2pi*tau)^-1
        ts = 0.02 # sample time
        self.vel_lpf = LowPassFilter(tau, ts) 
        
        self.vehicle_mass = vehicle_mass
        self.fuel_capacity = fuel_capacity
        self.brake_deadband = brake_deadband
        self.decelt_limit = decel_limit
        self.accel_limit = accel_limit
        self.wheel_radius = wheel_radius
        
        self.last_time = rospy.get_time()
        
        
        
    def control(self, current_vel, dbw_enabled, linear_vel, angular_vel):
        if not dbw_enabled:
            self.throttle_controller.reset()
            return 0, 0, 0
        current_vel = self.vel_lpf.filt(current_vel)
        
        steering = self.yaw_controller.get_steering(linear_vel, angular_velocity, current_velocity)
        vel_error = liner_vel - current_vel
        self.last_vel = current_el
        
        current_time = rospy.get_time()
        sample_time = current_time - self.last_time
        self.last_time = current_time
        
        throttle = self.throttle_controller.step(vel_error, sasmple_time)
        brake = 0
        
        if linear_vel == 0 and current_vel < 0.1: #if goal is to stop and vel already low, engage brakes to stay in place
            throttle = 0
            brake = 400
            
        elif throttle < 0.1 and vel_error < 0: # negative velocity error: need to slow down (break, no throttle)
            throttle = 0 
            decel = max(vel_error, self.decel_limit) #set max of desired and possible deceleartion
            brake = self.vehicle_mass * self.wheel_radius * abs(decel) #break needed in Nm
        return throttle, brake, steering

    def control(self, *args, **kwargs):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
        return 1., 0., 0.
