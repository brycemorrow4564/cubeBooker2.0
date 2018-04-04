import datetime
import calendar
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from BookableCube import BookableCube
from ProcessedBookingData import ProcessedBookingData
from WaitWrapper import general_driver_wait

import settings


''' Class queries webpage, extracts information on all bookable cubes, 
    and runs an algorithm to determine which cubes should be booked 
    and returns this information to the user. All of the processing is
    handled in the constructor and the user retrieves the information 
    with a call to get_cubes_to_book() which can be performed immediately 
    after the instantiation of a BookingWizard object. '''
class BookingWizard: 

    def __init__(self, user_manager):
        self.user_manager = user_manager 
        

    def run(self): 
        try:
            general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, 'lc_rm_a') #wait until time slots are definitively clickable 
        except: 
            print('not lit')

        cube_booking_data = self.gather_possible_bookings()
        self.ordered_key_set = cube_booking_data.get_ordered_key_set()
        self.times_to_bookable_cube_dict = cube_booking_data.get_times_to_bookable_cube_dict()
        self.cubes_to_book = self.determine_cubes_to_book()
        return self.cubes_to_book

    def get_cubes_to_book(self):
        return self.cubes_to_book


    #given name of month returns integer 1-12 
    def month_num_from_name(self, month):
        return {datetime.date(2017, i, 1).strftime('%B').lower():i for i in range(1,13)}[month.lower()]


    #cube_title in general form: 'Cube 7, 10:30am to 11:00am, Saturday, February 4, 2017'
    def cube_id_to_datetime_object(self, cube_title):
        regex = re.compile('.*?(\d*):(\d*\s*)([^\s]+).*?, .*?, ([^\s]+) (.*?), (.*)') 
        datetime_data = regex.findall(cube_title)[0] #('10', '30', 'am', 'February', '4', '2017')
        hour = -1
        if int(datetime_data[0]) == 12: 
            hour = 0 if datetime_data[2].lower() == 'am' else 12
        else:  
            hour = int(datetime_data[0]) if datetime_data[2].lower() == 'am' else int(datetime_data[0]) + 12
        return datetime.datetime(int(datetime_data[5]), #year 
                                 self.month_num_from_name(datetime_data[3]), #month
                                 int(datetime_data[4]), #day
                                 hour, #hour 
                                 int(datetime_data[1]) #minutes
                                )   


    def gather_possible_bookings(self):
        #Gather all buttons representing open cubes
        openCubeButtonClass = 'lc_rm_a'
        openCubes = settings.driver.find_elements_by_class_name(openCubeButtonClass)
        #dictionary mapping minutesToMidnight to list of BookableCube objects available at that time
        cubesByTimeSlot = {}
        keyIterOrder = set()
        for cube in openCubes:
            cube_id = cube.get_attribute('id')
            cube_title = cube.get_attribute('title') #'Cube 7, 10:30am to 11:00am, Saturday, February 4, 2017'
            cube_num = int(cube_title[5])
            datetime_obj = self.cube_id_to_datetime_object(cube_title) #converts cube_id to datetime object to facilitate timing comparisons
            target_key = None 
            #Check if key already exists for a datetime object with this value
            for key in keyIterOrder:
                if key == datetime_obj: 
                    #key already exists, map to existing reference rather than new instance of a BookableCube
                    target_key = key
                    break
            if target_key is None:
                #this key has not been used yet
                bookable_cube = BookableCube(cube_num, datetime_obj, cube_id)
                keyIterOrder.add(datetime_obj)
                cubesByTimeSlot[datetime_obj] = [bookable_cube]
            else:
                #this key already exists
                bookable_cube = BookableCube(cube_num, target_key, cube_id)
                cubesByTimeSlot[target_key] += [bookable_cube]
        return ProcessedBookingData(sorted(keyIterOrder), cubesByTimeSlot)
        

    def determine_cubes_to_book(self): 
        max_possible_bookings = self.user_manager.get_num_possible_bookings() 
        priority_cubes = [1,7] #cubes 1 and 7 given priority since they are larger
        longest_streak = 0
        key_counter = 0
        cubes_to_book_dict = {} #maps datetime object to BookableCube object 
        curr_streak_cube = BookableCube(-1, -1, -1)
        for i in range(min(max_possible_bookings, len(self.ordered_key_set))): 
            key = self.ordered_key_set[i]
            available_cubes = self.times_to_bookable_cube_dict[key]
            available_priority_cubes = [x for x in available_cubes if x.get_cube_num() in priority_cubes]
            cube_to_book = BookableCube(-1, -1, -1)
            if len(available_cubes) != 0:
                cube_to_book = curr_streak_cube if curr_streak_cube in available_priority_cubes else available_cubes[0]
            else:
                cube_to_book = curr_streak_cube if curr_streak_cube in available_cubes else available_cubes[0]
            cubes_to_book_dict[key] = cube_to_book
            curr_streak_cube = cube_to_book
            key_counter += 1
        return cubes_to_book_dict