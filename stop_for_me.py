import time
from geopy.distance import great_circle
import geocoder
import pygame
import requests
import json

# This code is the intellectual property of Smit Rao. 
# Please forward any concerns to raosmit2@gmail.com


'''
Problem description:

People sometimes chase buses (perhaps to no avail) because drivers leave early
or choose to ignore the nearby passengers looking to board the bus. In the cold,
it can be very frustrating to miss a bus by mere seconds.
 
We want to notify drivers of passenger arrivals, especially in a certain 
proximity of their bus stop (and their bus). This can be done through the 
automated use of a background-running mobile app using location services.
'''

def current_location() -> tuple:
    '''Return a tuple containing (lat, long).'''
    a = requests.get('http://freegeoip.net/json/129.97.124.18')
    data = a.json()
    return (data['latitude'], data['longitude'])

def geocode_it(place: str) -> tuple:
    geo = geocoder.google(place).latlng
    while geo == None:
        time.sleep(0.01)
        geo = geocoder.google(place).latlng
    return tuple(geo)

SAMPLE_STOPS = \
[geocode_it('University of Toronto, ON'), \
geocode_it('University of Waterloo, ON'), \
geocode_it('University of McGill')]

RANGE = input('Please set a geofencing radius constant: ') # meters
while type(RANGE) != int:
    try:
        RANGE = int(RANGE)
    except ValueError:
        RANGE = (input('Please set a valid radius: '))

class AlertLightError(Exception):
    '''AlertLight exception class for handling all AlertLight errors.'''
    pass

def within_range(stop: tuple=(), current: tuple=()) -> bool:
    '''Return whether current is within RANGE of stop.'''
    return great_circle(stop, current).meters < RANGE

def flash_lights(al, current: tuple=()) -> None:
    '''Flash lights on AlertLight <al> if a passenger is within_range.'''
    stop = al.coordinates
    print(stop, current)
    if within_range(stop, current):
        al.activate()
    else:
        print('\nOut of range, cannot flash.\n')

def kill_lights(al, current: tuple=()) -> None:
    '''Kill lights on AlertLight <al> if a passenger is not within_range.'''
    stop = al.coordinates
    if not within_range(stop, current):
        al.deactivate()
    else:
        print('\nIn range, cannot kill.\n')

class AlertLight:
    '''An alert for bus drivers.'''
    def __init__(self, stop: str='', color: str='Red', \
                 sound_duration: int=5, active: bool=False) -> None:
        if stop == '':
            raise AlertLightError('Please enter a valid bus stop!')
        self.stop = stop
        self.coordinates = geocode_it(self.stop)
        self.color = color
        self.sound_duration = sound_duration # + 3 seconds
        self.active = active
        
        
    def __repr__(self) -> str:
        '''A representation of AlertLight.'''
        return 'AlertLight(Stop: {}, Color: {}, \
Sound Duration: {} seconds)'.format(self.stop, self.color, \
self.sound_duration)
    
    def activate(self) -> None:
        '''Turn on the AlertLight.'''
        self.active = True
        pygame.init()
        pygame.mixer.music.load("passengers.mp3")
        pygame.mixer.music.play()
        time.sleep(3)
        pygame.mixer.music.load("beep.mp3")
        pygame.mixer.music.play()
        time.sleep(self.sound_duration)
        print('AlertLight for bus stop {} is now active.'.format(self.stop))
    
    def deactivate(self) -> None:
        '''Turn off the AlertLight.'''
        self.active = False
        print('AlertLight for bus stop {} has been \
deactivated.'.format(self.stop))
        

if __name__ == '__main__':
    print('\n\n\nSample locations:', SAMPLE_STOPS, '\n' * 2)
    print('\nYour location: {}\n\n'.format(current_location()))
    print('Your distance from bus stop:', great_circle(current_location(), \
SAMPLE_STOPS[1]).meters, 'meters', '\n' * 2)
    print('\nRange:', RANGE, '\n' * 2)
    print('\nWithin range:', within_range(SAMPLE_STOPS[1], \
                                          current_location()), '\n\n')
    al = AlertLight('University of Waterloo Bus Stop, Waterloo, ON')
    print('AlertLight specifications: {}'.format(al))