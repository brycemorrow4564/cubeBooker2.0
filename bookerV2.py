#pylint: disable=invalid-name

import datetime
import collections
import unittest 
from time import gmtime, strftime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


class BookableCube: 
    

    def __init__(self, cube_num, time_available, cube_id): 
        self.cube_num = cube_num
        self.time_available = time_available
        self.cube_id = cube_id


    def get_cube_num(self): 
        return self.cube_num


    def get_time_available(self): 
        return self.time_available


    def get_cube_id(self): 
        return self.cube_id


class User:
    '''class to represents users who can book cubes'''

    MAX_BOOKINGS = 6

    def __init__(self, username, password): 
        self.username = username
        self.password = password
        self.num_bookings = 0

    def get_username(self): 
        return self.username

    def get_password(self):
        return self.password

    def get_num_bookings(self): 
        return self.num_bookings

    def reset_num_bookings(self):
        self.num_bookings = 6

    def zero_num_bookings(self): 
        self.num_bookings = 0


class UserCycler: 
    '''object to represent a cycle of users. Each booking day, a 
    new user cycler object will be created since you can reserve 
    6 booking times each day'''

    def __init__(self, users):
        self.user_list = users
        self.active_user = self.user_list[0]


    def get_active_user(self): 
        return self.active_user

    
    def has_next_user(self): 
        return len(self.user_list) > 1 
    

    '''Assumption that has_next_user() called prior to this function call.'''
    def next_user(self): 
        curr_users = self.user_list
        for u in curr_users: 
            if u.get_username == self.active_user.get_username:
                curr_users.remove(u)
                self.user_list = curr_users
                self.active_user = curr_users[0]
                break

    def get_num_possible_bookings(self):
        total = 0
        for user in self.user_list:
            total += user.get_num_bookings()
        return total
        
    
class ProcessedBookingData:
    '''Wrapper class to encapsulate 2 pieces of cube data'''

    def __init__(self, ordered_key_set, times_to_bookable_cube_dict):
        self.ordered_key_set = ordered_key_set
        self.times_to_bookable_cube_dict = times_to_bookable_cube_dict

    def get_ordered_key_set(self):
        return self.ordered_key_set

    def get_times_to_bookable_cube_dict(self):
        return self.times_to_bookable_cube_dict


def process_time_string(time_string):
    '''Input converted from form of "10:30am" to
an integer metric of total minutes after midnight'''
    colon_index = time_string.find(':')
    hour = int(time_string[:colon_index])
    minute = int(time_string[colon_index+1:colon_index+3])
    is_am = False
    if time_string[colon_index+3:colon_index+4] == 'a':
        is_am = True
    return hour * 60 + minute if is_am else (hour + 12) * 60 + minute


def process_bookings(): 
    #Gather all buttons representing open cubes
    openCubeButtonClass = 'lc_rm_a'
    openCubes = driver.find_elements_by_class_name(openCubeButtonClass)
    #dictionary mapping minutesToMidnight to list of BookableCube objects available at that time
    cubesByTimeSlot = {}
    keyIterOrder = set()
    for cube in openCubes:
        cube_id = cube.get_attribute('id')
        #'Cube 7, 10:30am to 11:00am, Saturday, February 4, 2017'
        cubeTitle = cube.get_attribute('title')
        #'Cube 7' This works because number will always be at same index
        cubeNum = int(cubeTitle[5:6])
        #time interval will always start at index 8
        startIndex = 8
        #end index will always point to m in first 'pm' or 'am'
        endIndex = cubeTitle.find('to') - 2
        time_string = cubeTitle[startIndex:endIndex]  # '10:30am'
        minutesFromMidnight = process_time_string(time_string)
        bookable_cube = BookableCube(cubeNum, minutesFromMidnight, cube_id) #create instance of bookable cube object
        if minutesFromMidnight in keyIterOrder:
            other_available_cubes = cubesByTimeSlot[minutesFromMidnight]
            other_available_cubes += [bookable_cube]
            cubesByTimeSlot[minutesFromMidnight] = other_available_cubes
        else:
            cubesByTimeSlot[minutesFromMidnight] = [bookable_cube]
            keyIterOrder.add(minutesFromMidnight)
    #sort set of dictionary keys so they appear in ascending order
    keyIterOrder = sorted(keyIterOrder)
    return ProcessedBookingData(keyIterOrder, cubesByTimeSlot)
    

def run_booking_algorithm(ordered_key_set, times_to_cube_dict): 
    active_user = user_cycler.get_active_user()
    priority_cubes = [1,7] #cubes 1 and 7 given priority since they are larger
    longest_streak = 0
    key_counter = 0
    #dict maps time value to corresponding cube to book (i.e. mapping 600 to '5' would mean book cube 5 at 10am)
    cubes_to_book_dict = {}
    curr_streak_cube = BookableCube(-1, -1, -1)
    while key_counter != len(ordered_key_set):
        key = ordered_key_set[key_counter]
        available_cubes = times_to_cube_dict[key]
        available_priority_cubes = [x for x in available_cubes if x.get_cube_num() in priority_cubes]
        cube_to_book = BookableCube(-1, -1, -1)
        #case of priority cube being available
        if len(available_cubes) != 0:
            cube_to_book = curr_streak_cube if curr_streak_cube in available_priority_cubes else available_cubes[0]
        #case where no priority cubes are available
        else:
            cube_to_book = curr_streak_cube if curr_streak_cube in available_cubes else available_cubes[0]
        #map booking time in minutes after midnight to cube to book
        cubes_to_book_dict[key] = cube_to_book
        curr_streak_cube = cube_to_book
        key_counter += 1
    return cubes_to_book_dict
        

#NOTE: add fault tolerance so that if an error is encountered at any point, reclick cubes and try to book again
def input_user_info(active_user):
    #Setup wait driver
    timeout_delay = 10
    wait = WebDriverWait(driver, timeout_delay)
    #After cubes have been clicked and are ready to book, one of either two things can happen
    #1. Continue btn then submit time slots button 
    #2. no continue btn then submit time slots button
    #Detect if there is continue button. If so, click it 
    continue_btn_id = 'rm_tc_cont'
    if wait.until(EC.element_to_be_clickable((By.ID, continue_btn_id))): 
        driver.find_element_by_id(continue_btn_id).click()
    #Click Submit Time Slots button
    submit_btn_id = 's-lc-rm-sub'
    wait.until(EC.element_to_be_clickable((By.ID, submit_btn_id)))
    driver.find_element_by_id(submit_btn_id).click()
    #Next, we must enter the active users login info 
    username_id = 'username'
    password_id = 'password'
    wait.until(EC.visibility_of((By.ID, username_id)))
    wait.until(EC.visibility_of((By.ID, password_id)))
    username_input = driver.find_element_by_id(username_id).send_keys(active_user.get_username())
    password_input = driver.find_element_by_id(password_id).send_keys(active_user.get_password())
    #Submit this data 
    user_info_submit_btn_class = 'form-button'
    driver.find_element_by_class_name(user_info_submit_btn_class).click()
    #Enter group nickname
    group_nickname = 'lit'
    nickname_input_id = 'nick'
    wait.until(EC.visibility_of((By.ID, nickname_input_id)))
    driver.find_element_by_id(nickname_input_id).send_keys(group_nickname)
    #Submit final booking
    final_submit_id = 's-lc-rm-sub'
    driver.find_element_by_id().click()
    #logout
    logout_id = 's-lc-rm-auth-lobtn'
    wait.until(EC.element_to_be_clickable((By.ID, logout_id)))
    driver.find_element_by_id(logout_id).click()
    #confirm logout
    button_class = 'form-button'
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, button_class)))
    buttons = driver.find_elements_by_class_name(button_class)
    for button in buttons: 
        if button.text == "Yes":
            button.click()
    #return to booking page
    main_page_url = 'http://calendar.lib.unc.edu/booking/davishub'
    driver.get(main_page_url)


def book_cubes(cubes_to_book, ordered_key_set, user_cycler): 
    if len(cubes_to_book) == 0: 
        return 
    active_user = user_cycler.get_active_user()
    while True: 
        if active_user.can_book_cube(): 
            num_bookings = User.MAX_BOOKINGS - active_user.get_num_bookings()
            for i in range(num_bookings): 
                key = ordered_key_set.pop()
                if key is not None: 
                    target_cube_id = cubes_to_book[key].get_cube_id()
                    cube_button_to_click = driver.find_element_by_id(target_cube_id)
                    cube_to_click.click()
            active_user.zero_num_bookings() #set users num_bookings instance variable to 0 
            #all cubes have been booked, now input user information to complete bookings
            input_user_info(active_user)
        else: 
            if user_cycler.has_next_user(): 
                active_user = user_cycler.next_user() 
            else: 
                break 
    return 

#MAIN METHOD
if __name__ == '__main__':

    #Initialize users and user cycler 
    users = [User('bam4564', '#Bryc3m0rr0w!'), User('lucaswa', '#E03c55a6!!!!!'), User('dmtrump', 'climb3r1!!')]
    user_cycler = UserCycler(users)
    current_user = user_cycler.get_active_user()

    #Initialize driver and open window to target site
    driver = webdriver.Firefox()
    url = 'http://calendar.lib.unc.edu/booking/davishub'
    driver.get(url)
    driver.set_window_size(1200, 900)

    '''set of numerical values of each date that has already been booked.
    when this set reaches a length of 15, we know that we have booked for
    all open days'''
    booked_day_nums = set()
    MAX_NUM_BOOKING_DAYS = 15

    while len(booked_day_nums) != MAX_NUM_BOOKING_DAYS:
        calendar_obj = calendar = driver.find_element_by_class_name('ui-datepicker-calendar')
        possible_anchors = calendar.find_elements_by_xpath('.//a')
        for anchor in possible_anchors:
            date_num = anchor.text
            to_click_anchor = [x for x in possible_anchors if x.text == date_num][0]
            if date_num not in booked_day_nums:
                booked_day_nums.add(date_num)
                to_click_anchor.click()
                #anchor clicked, wait for table to appear
                timeout_delay = 10
                wait = WebDriverWait(driver, timeout_delay)
                element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'lc_rm_a')))
                #table generated, now process bookings for this day
                cube_booking_data = process_bookings()
                ordered_key_set = cube_booking_data.get_ordered_key_set()
                times_to_bookable_cube_dict = cube_booking_data.get_times_to_bookable_cube_dict()
                #give this data, run algorithm and return list of cube times to book
                cubes_to_book = run_booking_algorithm(ordered_key_set, times_to_bookable_cube_dict)
                book_cubes(cubes_to_book, ordered_key_set, user_cycler)
                exit()

