"""
AI Traffic Light System Simulation

An intelligent traffic light simulation with emergency vehicle priority and adaptive signal timing.
Features real-time vehicle simulation, emergency vehicle detection, and performance metrics.

Author: AI Traffic Light System
License: MIT
"""

import random
import math
import time
import threading
import pygame
import sys
import os
import traceback
import json

# Configuration Constants
DEFAULT_RED = 150
DEFAULT_YELLOW = 5
DEFAULT_GREEN = 20
DEFAULT_MINIMUM = 10
DEFAULT_MAXIMUM = 60

# Simulation Parameters
SIM_TIME = 300  # Total simulation time in seconds
NO_OF_SIGNALS = 4
NO_OF_LANES = 2
DETECTION_TIME = 5

# Vehicle timing parameters (seconds to pass intersection)
VEHICLE_TIMES = {
    'car': 2,
    'bike': 1,
    'rickshaw': 2.25,
    'bus': 2.5,
    'truck': 2.5
}

# Vehicle movement speeds
VEHICLE_SPEEDS = {
    'car': 1.15,
    'bus': 0.6,
    'truck': 0.6,
    'rickshaw': 0.8,
    'bike': 1.3,
    'emergency': 1.7
}

# Vehicle types
VEHICLE_TYPES = {
    0: 'car',
    1: 'bus',
    2: 'truck',
    3: 'rickshaw',
    4: 'bike',
    5: 'emergency'
}

# Direction mapping
DIRECTIONS = {
    0: 'right',
    1: 'down',
    2: 'left',
    3: 'up'
}

# Vehicle spawn coordinates
SPAWN_COORDS = {
    'right': {'x': [0, 0, 0], 'y': [348, 370, 398]},
    'down': {'x': [755, 727, 697], 'y': [0, 0, 0]},
    'left': {'x': [1400, 1400, 1400], 'y': [498, 466, 436]},
    'up': {'x': [602, 627, 657], 'y': [800, 800, 800]}
}

# Stop line coordinates
STOP_LINES = {
    'right': 590,
    'down': 330,
    'left': 800,
    'up': 535
}

# Default stop positions
DEFAULT_STOPS = {
    'right': 580,
    'down': 320,
    'left': 810,
    'up': 545
}

# Signal display coordinates
SIGNAL_COORDS = [(530, 230), (810, 230), (810, 570), (530, 570)]
TIMER_COORDS = [(530, 210), (810, 210), (810, 550), (530, 550)]
COUNT_COORDS = [(480, 210), (880, 210), (880, 550), (480, 550)]

# Turn coordinates
TURN_MIDPOINTS = {
    'right': {'x': 705, 'y': 445},
    'down': {'x': 695, 'y': 450},
    'left': {'x': 695, 'y': 425},
    'up': {'x': 695, 'y': 400}
}

# Vehicle spacing
STOPPING_GAP = 15
MOVING_GAP = 15
ROTATION_ANGLE = 3

# Global variables
signals = []
time_elapsed = 0
current_green = 0
current_yellow = 0
lane_last_green_time = [0 for _ in range(NO_OF_SIGNALS)]
waiting_times = []

# Vehicle storage
vehicles = {
    'right': {0: [], 1: [], 2: [], 'crossed': 0},
    'down': {0: [], 1: [], 2: [], 'crossed': 0},
    'left': {0: [], 1: [], 2: [], 'crossed': 0},
    'up': {0: [], 1: [], 2: [], 'crossed': 0}
}

# Initialize Pygame
pygame.init()
simulation = pygame.sprite.Group()
move_lock = threading.Lock()


class TrafficSignal:
    """Represents a traffic signal with timing controls."""
    
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signal_text = "30"
        self.total_green_time = 0


class Vehicle(pygame.sprite.Sprite):
    """Represents a vehicle in the traffic simulation."""
    
    def __init__(self, lane, vehicle_class, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicle_class = vehicle_class
        self.speed = VEHICLE_SPEEDS[vehicle_class]
        self.direction_number = direction_number
        self.direction = direction
        
        # Set initial position
        self.x = SPAWN_COORDS[direction]['x'][lane]
        self.y = SPAWN_COORDS[direction]['y'][lane]
        
        # Vehicle state
        self.crossed = 0
        self.will_turn = will_turn
        self.turned = 0
        self.rotate_angle = 0
        self.waiting_time = 0
        self.spawn_time = time_elapsed
        self.cross_time = None
        
        # Add to vehicle list
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        
        # Load vehicle image
        if vehicle_class == 'emergency':
            path = f"images/{direction}/emergency_icon.png"
        else:
            path = f"images/{direction}/{vehicle_class}.png"
        
        self.original_image = pygame.image.load(path)
        self.current_image = pygame.image.load(path)
        
        # Set stop position
        self._set_stop_position()
        simulation.add(self)

    def _set_stop_position(self):
        """Set the stop position based on previous vehicle in lane."""
        lane_list = vehicles[self.direction][self.lane]
        
        if len(lane_list) > 1 and lane_list[self.index - 1].crossed == 0:
            prev_vehicle = lane_list[self.index - 1]
            if self.direction == 'right':
                self.stop = prev_vehicle.stop - prev_vehicle.current_image.get_rect().width - STOPPING_GAP
            elif self.direction == 'left':
                self.stop = prev_vehicle.stop + prev_vehicle.current_image.get_rect().width + STOPPING_GAP
            elif self.direction == 'down':
                self.stop = prev_vehicle.stop - prev_vehicle.current_image.get_rect().height - STOPPING_GAP
            elif self.direction == 'up':
                self.stop = prev_vehicle.stop + prev_vehicle.current_image.get_rect().height + STOPPING_GAP
        else:
            self.stop = DEFAULT_STOPS[self.direction]

    def render(self, screen):
        """Render the vehicle on screen."""
        screen.blit(self.current_image, (self.x, self.y))

    def move(self):
        """Move the vehicle based on traffic rules and conditions."""
        with move_lock:
            moved = False
            lane_list = vehicles[self.direction][self.lane]
            
            try:
                idx = lane_list.index(self)
            except ValueError:
                return  # Vehicle already removed
            
            # Increment waiting time if not crossed
            if self.crossed == 0:
                self.waiting_time += 1
            
            # Handle crossing detection
            self._check_crossing()
            
            # Move based on direction
            if self.direction == 'right':
                moved = self._move_right(idx, lane_list)
            elif self.direction == 'down':
                moved = self._move_down(idx, lane_list)
            elif self.direction == 'left':
                moved = self._move_left(idx, lane_list)
            elif self.direction == 'up':
                moved = self._move_up(idx, lane_list)

    def _check_crossing(self):
        """Check if vehicle has crossed the intersection."""
        if self.crossed == 0:
            if self.direction == 'right' and self.x + self.current_image.get_rect().width > STOP_LINES[self.direction]:
                self._mark_crossed()
            elif self.direction == 'down' and self.y + self.current_image.get_rect().height > STOP_LINES[self.direction]:
                self._mark_crossed()
            elif self.direction == 'left' and self.x < STOP_LINES[self.direction]:
                self._mark_crossed()
            elif self.direction == 'up' and self.y < STOP_LINES[self.direction]:
                self._mark_crossed()

    def _mark_crossed(self):
        """Mark vehicle as crossed and record metrics."""
        self.crossed = 1
        self.cross_time = time_elapsed
        waiting_times.append(self.cross_time - self.spawn_time)
        vehicles[self.direction]['crossed'] += 1

    def _move_right(self, idx, lane_list):
        """Move vehicle in right direction."""
        if self.will_turn == 1:
            return self._move_right_turn(idx, lane_list)
        else:
            return self._move_right_straight(idx, lane_list)

    def _move_right_straight(self, idx, lane_list):
        """Move vehicle straight in right direction."""
        can_move = (
            (self.x + self.current_image.get_rect().width <= self.stop or 
             self.crossed == 1 or 
             (current_green == 0 and current_yellow == 0)) and
            (idx == 0 or 
             self.x + self.current_image.get_rect().width < (lane_list[idx - 1].x - MOVING_GAP) or 
             lane_list[idx - 1].turned == 1)
        )
        
        if can_move:
            self.x += self.speed
            return True
        return False

    def _move_right_turn(self, idx, lane_list):
        """Move vehicle turning right."""
        if self.crossed == 0 or self.x + self.current_image.get_rect().width < TURN_MIDPOINTS[self.direction]['x']:
            # Pre-turn movement
            can_move = (
                (self.x + self.current_image.get_rect().width <= self.stop or 
                 (current_green == 0 and current_yellow == 0) or 
                 self.crossed == 1) and
                (idx == 0 or 
                 self.x + self.current_image.get_rect().width < (lane_list[idx - 1].x - MOVING_GAP) or 
                 lane_list[idx - 1].turned == 1)
            )
            
            if can_move:
                self.x += self.speed
                return True
        else:
            # Turning movement
            if self.turned == 0:
                self.rotate_angle += ROTATION_ANGLE
                self.current_image = pygame.transform.rotate(self.original_image, -self.rotate_angle)
                self.x += 2
                self.y += 1.8
                if self.rotate_angle == 90:
                    self.turned = 1
                return True
            else:
                # Post-turn movement
                can_move = (
                    idx == 0 or 
                    self.y + self.current_image.get_rect().height < (lane_list[idx - 1].y - MOVING_GAP) or 
                    self.x + self.current_image.get_rect().width < (lane_list[idx - 1].x - MOVING_GAP)
                )
                
                if can_move:
                    self.y += self.speed
                    return True
        return False

    def _move_down(self, idx, lane_list):
        """Move vehicle in down direction."""
        if self.will_turn == 1:
            return self._move_down_turn(idx, lane_list)
        else:
            return self._move_down_straight(idx, lane_list)

    def _move_down_straight(self, idx, lane_list):
        """Move vehicle straight in down direction."""
        can_move = (
            (self.y + self.current_image.get_rect().height <= self.stop or 
             self.crossed == 1 or 
             (current_green == 1 and current_yellow == 0)) and
            (idx == 0 or 
             self.y + self.current_image.get_rect().height < (lane_list[idx - 1].y - MOVING_GAP) or 
             lane_list[idx - 1].turned == 1)
        )
        
        if can_move:
            self.y += self.speed
            return True
        return False

    def _move_down_turn(self, idx, lane_list):
        """Move vehicle turning from down direction."""
        if self.crossed == 0 or self.y + self.current_image.get_rect().height < TURN_MIDPOINTS[self.direction]['y']:
            # Pre-turn movement
            can_move = (
                (self.y + self.current_image.get_rect().height <= self.stop or 
                 (current_green == 1 and current_yellow == 0) or 
                 self.crossed == 1) and
                (idx == 0 or 
                 self.y + self.current_image.get_rect().height < (lane_list[idx - 1].y - MOVING_GAP) or 
                 lane_list[idx - 1].turned == 1)
            )
            
            if can_move:
                self.y += self.speed
                return True
        else:
            # Turning movement
            if self.turned == 0:
                self.rotate_angle += ROTATION_ANGLE
                self.current_image = pygame.transform.rotate(self.original_image, -self.rotate_angle)
                self.x -= 2.5
                self.y += 2
                if self.rotate_angle == 90:
                    self.turned = 1
                return True
            else:
                # Post-turn movement
                can_move = (
                    idx == 0 or 
                    self.x > (lane_list[idx - 1].x + lane_list[idx - 1].current_image.get_rect().width + MOVING_GAP) or 
                    self.y < (lane_list[idx - 1].y - MOVING_GAP)
                )
                
                if can_move:
                    self.x -= self.speed
                    return True
        return False

    def _move_left(self, idx, lane_list):
        """Move vehicle in left direction."""
        if self.crossed == 1:
            return self._move_left_after_crossing(idx, lane_list)
        else:
            if self.will_turn == 1:
                return self._move_left_turn(idx, lane_list)
            else:
                return self._move_left_straight(idx, lane_list)

    def _move_left_after_crossing(self, idx, lane_list):
        """Move vehicle after crossing intersection."""
        # Find nearest vehicle ahead
        ahead = None
        for j in range(idx - 1, -1, -1):
            v = lane_list[j]
            if v.x + v.current_image.get_rect().width > 0:
                ahead = v
                break
        
        if ahead is None or self.x > (ahead.x + ahead.current_image.get_rect().width + MOVING_GAP):
            self.x -= self.speed
            return True
        
        # Remove vehicle if off screen
        if self.x + self.current_image.get_rect().width < -10:
            if self in lane_list:
                lane_list.remove(self)
            simulation.remove(self)
        return False

    def _move_left_straight(self, idx, lane_list):
        """Move vehicle straight in left direction."""
        can_move = (
            (self.x >= self.stop or 
             self.crossed == 1 or 
             (current_green == 2 and current_yellow == 0)) and
            (idx == 0 or 
             self.x > (lane_list[idx - 1].x + lane_list[idx - 1].current_image.get_rect().width + MOVING_GAP))
        )
        
        if can_move:
            self.x -= self.speed
            return True
        return False

    def _move_left_turn(self, idx, lane_list):
        """Move vehicle turning from left direction."""
        if self.crossed == 0 or self.x > TURN_MIDPOINTS[self.direction]['x']:
            # Pre-turn movement
            can_move = (
                (self.x >= self.stop or 
                 (current_green == 2 and current_yellow == 0) or 
                 self.crossed == 1) and
                (idx == 0 or 
                 self.x > (lane_list[idx - 1].x + lane_list[idx - 1].current_image.get_rect().width + MOVING_GAP) or 
                 lane_list[idx - 1].turned == 1)
            )
            
            if can_move:
                self.x -= self.speed
                return True
        else:
            # Turning movement
            if self.turned == 0:
                self.rotate_angle += ROTATION_ANGLE
                self.current_image = pygame.transform.rotate(self.original_image, -self.rotate_angle)
                self.x -= 1.8
                self.y -= 2.5
                if self.rotate_angle == 90:
                    self.turned = 1
                return True
            else:
                # Post-turn movement
                can_move = (
                    idx == 0 or 
                    self.y > (lane_list[idx - 1].y + lane_list[idx - 1].current_image.get_rect().height + MOVING_GAP) or 
                    self.x > (lane_list[idx - 1].x + MOVING_GAP)
                )
                
                if can_move:
                    self.y -= self.speed
                    return True
        return False

    def _move_up(self, idx, lane_list):
        """Move vehicle in up direction."""
        if self.will_turn == 1:
            return self._move_up_turn(idx, lane_list)
        else:
            return self._move_up_straight(idx, lane_list)

    def _move_up_straight(self, idx, lane_list):
        """Move vehicle straight in up direction."""
        can_move = (
            (self.y >= self.stop or 
             self.crossed == 1 or 
             (current_green == 3 and current_yellow == 0)) and
            (idx == 0 or 
             self.y > (lane_list[idx - 1].y + lane_list[idx - 1].current_image.get_rect().height + MOVING_GAP) or 
             lane_list[idx - 1].turned == 1)
        )
        
        if can_move:
            self.y -= self.speed
            return True
        return False

    def _move_up_turn(self, idx, lane_list):
        """Move vehicle turning from up direction."""
        if self.crossed == 0 or self.y > TURN_MIDPOINTS[self.direction]['y']:
            # Pre-turn movement
            can_move = (
                (self.y >= self.stop or 
                 (current_green == 3 and current_yellow == 0) or 
                 self.crossed == 1) and
                (idx == 0 or 
                 self.y > (lane_list[idx - 1].y + lane_list[idx - 1].current_image.get_rect().height + MOVING_GAP) or 
                 lane_list[idx - 1].turned == 1)
            )
            
            if can_move:
                self.y -= self.speed
                return True
        else:
            # Turning movement
            if self.turned == 0:
                self.rotate_angle += ROTATION_ANGLE
                self.current_image = pygame.transform.rotate(self.original_image, -self.rotate_angle)
                self.x += 1
                self.y -= 1
                if self.rotate_angle == 90:
                    self.turned = 1
                return True
            else:
                # Post-turn movement
                can_move = (
                    idx == 0 or 
                    self.x < (lane_list[idx - 1].x - lane_list[idx - 1].current_image.get_rect().width - MOVING_GAP) or 
                    self.y > (lane_list[idx - 1].y + MOVING_GAP)
                )
                
                if can_move:
                    self.x += self.speed
                    return True
        return False


def initialize_signals():
    """Initialize traffic signals with default values."""
    global signals
    
    ts1 = TrafficSignal(0, DEFAULT_YELLOW, DEFAULT_GREEN, DEFAULT_MINIMUM, DEFAULT_MAXIMUM)
    signals.append(ts1)
    
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, DEFAULT_YELLOW, DEFAULT_GREEN, DEFAULT_MINIMUM, DEFAULT_MAXIMUM)
    signals.append(ts2)
    
    ts3 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN, DEFAULT_MINIMUM, DEFAULT_MAXIMUM)
    signals.append(ts3)
    
    ts4 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN, DEFAULT_MINIMUM, DEFAULT_MAXIMUM)
    signals.append(ts4)
    
    repeat_signal_cycle()


def calculate_green_time():
    """Calculate optimal green time based on waiting vehicles."""
    global signals
    
    # Count vehicles in next signal direction
    next_signal = (current_green + 1) % NO_OF_SIGNALS
    direction = DIRECTIONS[next_signal]
    
    vehicle_counts = {'car': 0, 'bus': 0, 'truck': 0, 'rickshaw': 0, 'bike': 0, 'emergency': 0}
    
    # Count vehicles in all lanes
    for lane in range(3):
        for vehicle in vehicles[direction][lane]:
            if vehicle.crossed == 0:
                vclass = vehicle.vehicle_class
                if vclass in vehicle_counts:
                    vehicle_counts[vclass] += 1
    
    # Calculate green time using vehicle timing
    total_time = sum(vehicle_counts[vtype] * VEHICLE_TIMES.get(vtype, 1) for vtype in vehicle_counts)
    green_time = math.ceil(total_time / (NO_OF_LANES + 1))
    
    # Apply limits
    green_time = max(DEFAULT_MINIMUM, min(DEFAULT_MAXIMUM, green_time))
    
    print(f'Green Time: {green_time}')
    signals[next_signal].green = green_time


def repeat_signal_cycle():
    """Main signal control loop with emergency vehicle priority."""
    global current_green, current_yellow, time_elapsed, lane_last_green_time
    
    while True:
        # Emergency vehicle priority system - FIXED to prioritize earliest emergency vehicle
        emergency_lanes = []
        earliest_emergency_time = float('inf')
        earliest_emergency_lane = None
        
        # Find the earliest emergency vehicle across all lanes
        for lane_idx in range(NO_OF_SIGNALS):
            for lane in range(3):
                for v in vehicles[DIRECTIONS[lane_idx]][lane]:
                    if v.crossed == 0 and v.vehicle_class == 'emergency':
                        # Use vehicle's distance from intersection to estimate arrival time
                        # Vehicles closer to intersection (lower x,y values) arrived earlier
                        if DIRECTIONS[lane_idx] == 'right':
                            arrival_estimate = v.x  # Lower x = earlier arrival
                        elif DIRECTIONS[lane_idx] == 'left':
                            arrival_estimate = -v.x  # Higher x = earlier arrival (negative for sorting)
                        elif DIRECTIONS[lane_idx] == 'up':
                            arrival_estimate = v.y  # Lower y = earlier arrival
                        elif DIRECTIONS[lane_idx] == 'down':
                            arrival_estimate = -v.y  # Higher y = earlier arrival (negative for sorting)
                        
                        if arrival_estimate < earliest_emergency_time:
                            earliest_emergency_time = arrival_estimate
                            earliest_emergency_lane = lane_idx
        
        if earliest_emergency_lane is not None:
            # Emergency priority logic - prioritize the lane with earliest emergency vehicle
            selected_lane = earliest_emergency_lane
            emergency_count = sum(1 for lane in range(3) 
                                for v in vehicles[DIRECTIONS[selected_lane]][lane] 
                                if v.crossed == 0 and v.vehicle_class == 'emergency')
            waiting_count = sum(1 for lane in range(3) 
                              for v in vehicles[DIRECTIONS[selected_lane]][lane] if v.crossed == 0)
            waiting_time = time_elapsed - lane_last_green_time[selected_lane]
            
            print(f"🚨 EMERGENCY PRIORITY: Lane {selected_lane + 1} selected (earliest emergency vehicle, {emergency_count} total emergencies)")
            print(f"   Waiting vehicles: {waiting_count}, Waited: {waiting_time}s")
        else:
            # Normal priority logic
            priorities = []
            for lane_idx in range(NO_OF_SIGNALS):
                waiting_count = sum(1 for lane in range(3) 
                                  for v in vehicles[DIRECTIONS[lane_idx]][lane] if v.crossed == 0)
                waiting_time = time_elapsed - lane_last_green_time[lane_idx]
                priority = waiting_count + 0.2 * waiting_time if waiting_count > 0 else 0
                priorities.append((priority, lane_idx, waiting_count, waiting_time))
            
            priorities = [p for p in priorities if p[0] > 0]
            if not priorities:
                time.sleep(1)
                continue
            
            priorities.sort(reverse=True)
            _, selected_lane, max_waiting, max_waiting_time = priorities[0]
        
        # Set selected lane as green
        signals[selected_lane].red = DEFAULT_RED
        current_green = selected_lane
        lane_last_green_time[current_green] = time_elapsed
        
        print(f"Lane {current_green + 1} selected, waiting vehicles: {max_waiting}, waited: {max_waiting_time}s")
        print(f"Lane priorities: {[round(p[0], 2) for p in priorities]}")
        
        # Calculate green time using nonlinear formula
        waiting_count = sum(1 for lane in range(3) 
                           for v in vehicles[DIRECTIONS[current_green]][lane] if v.crossed == 0)
        green_time = 8 + 1.0 * (waiting_count ** 0.85)
        green_time = int(round(green_time))
        green_time = max(DEFAULT_MINIMUM, min(DEFAULT_MAXIMUM, green_time))
        
        print(f"[NONLINEAR] Lane {current_green + 1} green time set to {green_time} seconds for {waiting_count} waiting vehicles")
        signals[current_green].green = green_time
        
        # Run green signal
        while signals[current_green].green > 0:
            print_signal_status()
            update_signal_values()
            
            if signals[(current_green + 1) % NO_OF_SIGNALS].red == DETECTION_TIME:
                thread = threading.Thread(name="detection", target=calculate_green_time, args=())
                thread.daemon = True
                thread.start()
            
            time.sleep(1)
        
        # Yellow signal phase
        current_yellow = 1
        for i in range(3):
            for vehicle in vehicles[DIRECTIONS[current_green]][i]:
                vehicle.stop = DEFAULT_STOPS[DIRECTIONS[current_green]]
        
        while signals[current_green].yellow > 0:
            print_signal_status()
            update_signal_values()
            time.sleep(1)
        
        current_yellow = 0
        signals[current_green].yellow = DEFAULT_YELLOW
        signals[current_green].red = DEFAULT_RED


def print_signal_status():
    """Print current signal status to console."""
    for i in range(NO_OF_SIGNALS):
        if i == current_green:
            if current_yellow == 0:
                print(f" GREEN TS{i + 1} -> r:{signals[i].red} y:{signals[i].yellow} g:{signals[i].green}")
            else:
                print(f"YELLOW TS{i + 1} -> r:{signals[i].red} y:{signals[i].yellow} g:{signals[i].green}")
        else:
            print(f"   RED TS{i + 1} -> r:{signals[i].red} y:{signals[i].yellow} g:{signals[i].green}")
    print()


def update_signal_values():
    """Update signal timer values."""
    for i in range(NO_OF_SIGNALS):
        if i == current_green:
            if current_yellow == 0:
                signals[i].green -= 1
                signals[i].total_green_time += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1
            if signals[i].red < 0:
                signals[i].red = 0


def generate_vehicles():
    """Generate vehicles randomly in the simulation."""
    while True:
        # 1.5% chance to spawn emergency vehicle
        if random.random() < 0.015:
            vehicle_type = 5  # emergency
        else:
            vehicle_type = random.randint(0, 4)
        
        # Random lane and direction
        lane_number = random.randint(0, 2)
        direction_number = random.randint(0, 3)
        
        # Determine if vehicle will turn (30% chance for rightmost lane)
        will_turn = 0
        if lane_number == 2:
            will_turn = 1 if random.randint(0, 4) <= 2 else 0
        
        Vehicle(lane_number, VEHICLE_TYPES[vehicle_type], direction_number, 
               DIRECTIONS[direction_number], will_turn)
        
        time.sleep(0.85)


def output_simulation_metrics():
    """Output simulation performance metrics."""
    total_vehicles = 0
    lane_counts = {}
    
    for i in range(NO_OF_SIGNALS):
        lane_counts[f'Lane_{i + 1}'] = vehicles[DIRECTIONS[i]]['crossed']
        total_vehicles += vehicles[DIRECTIONS[i]]['crossed']
    
    metrics = {
        'lane_counts': lane_counts,
        'total_vehicles_passed': total_vehicles,
        'total_time_passed': time_elapsed,
        'vehicles_per_unit_time': float(total_vehicles) / float(time_elapsed) if time_elapsed else 0,
    }
    
    if waiting_times:
        avg_wait = sum(waiting_times) / len(waiting_times)
        max_wait = max(waiting_times)
        metrics['average_waiting_time'] = avg_wait
        metrics['max_waiting_time'] = max_wait
    else:
        metrics['average_waiting_time'] = None
        metrics['max_waiting_time'] = None
    
    # Save metrics to file
    with open('output/emerg_results.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Print summary
    print('Lane-wise Vehicle Counts')
    for i in range(NO_OF_SIGNALS):
        print(f'Lane {i + 1}: {vehicles[DIRECTIONS[i]]["crossed"]}')
    
    print(f'Total vehicles passed: {total_vehicles}')
    print(f'Total time passed: {time_elapsed}')
    print(f'Vehicles per unit time: {float(total_vehicles) / float(time_elapsed):.2f}')
    
    if waiting_times:
        avg_wait = sum(waiting_times) / len(waiting_times)
        max_wait = max(waiting_times)
        print(f'Average waiting time: {avg_wait:.2f} s')
        print(f'Max waiting time: {max_wait:.2f} s')
    else:
        print('No vehicles crossed, so no waiting time data.')


def simulation_timer():
    """Timer to track simulation duration and output results."""
    global time_elapsed
    
    while True:
        time_elapsed += 1
        time.sleep(1)
        if time_elapsed == SIM_TIME:
            output_simulation_metrics()
            os._exit(1)


class Main:
    """Main simulation class handling the Pygame display and game loop."""
    
    def __init__(self):
        # Start background threads
        self._start_threads()
        
        # Initialize display
        self.screen_width = 1400
        self.screen_height = 800
        self.screen_size = (self.screen_width, self.screen_height)
        
        # Colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        
        # Load images
        self.background = pygame.image.load('images/mod_int.png')
        self.red_signal = pygame.image.load('images/signals/red.png')
        self.yellow_signal = pygame.image.load('images/signals/yellow.png')
        self.green_signal = pygame.image.load('images/signals/green.png')
        self.font = pygame.font.Font(None, 30)
        
        # Setup display
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("AI Traffic Light System Simulation")
        
        # Start vehicle generation
        self._start_vehicle_generation()
        
        # Run main loop
        self._run_main_loop()

    def _start_threads(self):
        """Start background threads."""
        # Simulation timer thread
        timer_thread = threading.Thread(name="simulationTimer", target=simulation_timer, args=())
        timer_thread.daemon = True
        timer_thread.start()
        
        # Signal initialization thread
        init_thread = threading.Thread(name="initialization", target=initialize_signals, args=())
        init_thread.daemon = True
        init_thread.start()

    def _start_vehicle_generation(self):
        """Start vehicle generation thread."""
        vehicle_thread = threading.Thread(name="generateVehicles", target=generate_vehicles, args=())
        vehicle_thread.daemon = True
        vehicle_thread.start()

    def _run_main_loop(self):
        """Main game loop."""
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                
                # Draw background
                self.screen.blit(self.background, (0, 0))
                
                # Draw signals
                self._draw_signals()
                
                # Draw timers and counts
                self._draw_timers_and_counts()
                
                # Draw time elapsed
                time_text = self.font.render(f"Time Elapsed: {time_elapsed}", True, self.black, self.white)
                self.screen.blit(time_text, (1100, 50))
                
                # Draw and move vehicles
                for vehicle in simulation:
                    self.screen.blit(vehicle.current_image, [vehicle.x, vehicle.y])
                    vehicle.move()
                
                pygame.display.update()
                
        except Exception as e:
            print("\n\n--- EXCEPTION OCCURRED ---")
            traceback.print_exc()
            print("--- END OF TRACEBACK ---\n\n")
            pygame.quit()
            sys.exit(1)

    def _draw_signals(self):
        """Draw traffic signals on screen."""
        for i in range(NO_OF_SIGNALS):
            if i == current_green:
                if current_yellow == 1:
                    if signals[i].yellow == 0:
                        signals[i].signal_text = "STOP"
                    else:
                        signals[i].signal_text = str(signals[i].yellow)
                    self.screen.blit(self.yellow_signal, SIGNAL_COORDS[i])
                else:
                    if signals[i].green == 0:
                        signals[i].signal_text = "SLOW"
                    else:
                        signals[i].signal_text = str(signals[i].green)
                    self.screen.blit(self.green_signal, SIGNAL_COORDS[i])
            else:
                if signals[i].red <= 10 and signals[i].red > 0:
                    signals[i].signal_text = str(signals[i].red)
                else:
                    signals[i].signal_text = "---"
                self.screen.blit(self.red_signal, SIGNAL_COORDS[i])

    def _draw_timers_and_counts(self):
        """Draw signal timers and vehicle counts."""
        for i in range(NO_OF_SIGNALS):
            # Draw timer
            timer_text = self.font.render(str(signals[i].signal_text), True, self.white, self.black)
            self.screen.blit(timer_text, TIMER_COORDS[i])
            
            # Draw vehicle count
            waiting_count = sum(1 for lane in range(3) 
                              for v in vehicles[DIRECTIONS[i]][lane] if v.crossed == 0)
            count_text = self.font.render(str(waiting_count), True, self.black, self.white)
            self.screen.blit(count_text, COUNT_COORDS[i])


if __name__ == "__main__":
    Main()


