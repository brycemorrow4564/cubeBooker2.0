#Library Imports
import re 
import datetime
import calendar
import collections
from time import gmtime, strftime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

#Class Imports 
from BookableCube import BookableCube
from BookingWizard import BookingWizard
from BookingStateMachine import BookingStateMachine
from ProcessedBookingData import ProcessedBookingData
from User import User
from UserManager import UserManager

#Function Imports
from WaitWrapper import general_driver_wait

#Import Custom Settings (Global Variables)
import settings


#parses using standard datetime.date format and then returns as 2 digit integer to ease comparison
def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return int((next_month - datetime.timedelta(days=next_month.day))[-2:])


#given name of month returns integer 1-12 
def month_num_from_name(month):
    return {datetime.date(2017, i, 1).strftime('%B').lower():i for i in range(1,13)}[month.lower()]


def process_time_string(time_string):
    '''Input converted from form of "10:30am" to
an integer metric of total minutes after midnight'''
    colon_index = time_string.find(':')
    hour = int(time_string[:colon_index])
    minute = int(time_string[colon_index+1:colon_index+3])
    is_am = True if time_string[colon_index+3:colon_index+4] == 'a' else False 
    return hour * 60 + minute if is_am else (hour + 12) * 60 + minute


#cube_title in general form: 'Cube 7, 10:30am to 11:00am, Saturday, February 4, 2017'
def cube_id_to_datetime_object(cube_title):
    regex = re.compile('.*?(\d*):(\d*\s*)([^\s]+).*?, .*?, ([^\s]+) (.*?), (.*)') 
    datetime_data = regex.findall(cube_title)[0] #('10', '30', 'am', 'February', '4', '2017')
    return datetime.datetime(int(datetime_data[5]), #year 
                             month_num_from_name(datetime_data[3]), #month
                             int(datetime_data[4]), #day
                             int(datetime_data[0]) if datetime_data[2].lower() == 'am' else int(datetime_data[0]) + 12, #hour adjusted for am/pm
                             int(datetime_data[1]) #minutes
                            )


def gather_possible_bookings():
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
        datetime_obj = cube_id_to_datetime_object(cube_title) #converts cube_id to datetime object to facilitate timing comparisons
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


def book_cubes(cubes_to_book, ordered_key_set, user_Manager): 
    if len(cubes_to_book) == 0: 
        return 
    active_user = user_Manager.get_active_user()
    while True: 
        if active_user.can_book_cube(): 
            num_bookings = User.MAX_BOOKINGS - active_user.get_num_bookings()
            for i in range(num_bookings): 
                key = ordered_key_set.pop()
                if key is not None: 
                    target_cube_id = cubes_to_book[key].get_cube_id()
                    cube_button_to_click = settings.driver.find_element_by_id(target_cube_id)
                    cube_to_click.click()
            active_user.zero_num_bookings() #set users num_bookings instance variable to 0 
            #all cubes have been booked, now input user information to complete bookings
            input_user_info(active_user)
        else: 
            if user_Manager.has_next_user(): 
                active_user = user_Manager.next_user() 
            else: 
                break 
    return 


#returns integer 1-12 representing the current selected month jan-dec
def get_selected_month():
    general_driver_wait(EC.presence_of_element_located, By.CLASS_NAME, 'ui-datepicker-month')
    month_options = settings.driver.find_element_by_class_name('ui-datepicker-month').find_elements_by_css_selector("*")
    for month in month_options: 
        try: 
            if month.get_attribute('selected') is not None:
                return int(month.get_attribute('value')) + 1 #offset by one since website represents months with integers 0-11 instead of 1-12
        except:
            pass 
    #If we did not find the selected month at any point in the for loop raise an exception 
    raise Exception("Was not able to determine what the current selected month is")


def ensure_correct_calendar_loc(curr_book_day, first_day_to_book):
    #get current selected month represented as 1-12
    curr_month_num = get_selected_month()
    if first_day_to_book > curr_book_day:
        #if this is the case, we must move the calendar ahead to the next month 
        target_class = 'ui-datepicker-next'
        next_button = settings.driver.find_element_by_class_name(target_class)
        next_button.click()
        #test to make sure the button has been clicked and we are in correct calendar month
        new_month_num = get_selected_month()
        if new_month_num == curr_month_num:
            #the button click did not work and we did not advance.
            #Refresh the window and call this function recursively to reset everything and try again. 
            settings.driver.get(main_page_url)
            ensure_correct_calendar_loc(curr_book_day, first_day_to_book)
    

def find_day_anchor_to_click(curr_day):
    calendarWidget = settings.driver.find_element_by_class_name('ui-datepicker-calendar')
    possible_anchors = calendarWidget.find_elements_by_xpath('.//a') #target componets have this unique identifier, but not all do
    to_click_anchor = None
    for anchor in possible_anchors:
        if int(anchor.text) == curr_day: 
            return anchor
    if to_click_anchor is None: 
        raise Exception("Desired date anchor was not located ")        
        #implement call back to close driver and restart procedure entirely ? 
        #if this is done, give a chance for termination so no infinite loops occur. 


def run_booker():
    
    #Create UserManager 
    users = [User('bam4564', '#Bryc3m0rr0w!'), User('lucaswa', '#E03c55a6!!!!!'), User('dmtrump', 'climb3r1!!')]
    #users = [User('bam4564', '#Bryc3m0rr0w!')] #DEBUG
    user_manager = UserManager(users)

    ''' Gather some important date related information
        num_last_day: needed so we know if we have to change calendar views at any point during execution 
        current_month: will be used as a reference so we know when to change the calendar view '''
    now = datetime.datetime.now()
    num_last_day = calendar.monthrange(now.year, now.month)[1]
    current_month = now.month
    
    MAX_NUM_BOOKING_DAYS = 15 #library allows bookings a maximum of 2 weeks in advance (not including the current day)
    days_to_book = [i for i in xrange(now.day, num_last_day+1)] #contains numerical value of days to book (August 7th -> 7)
    if len(days_to_book) != MAX_NUM_BOOKING_DAYS: 
        days_to_book += [i+1 for i in xrange(MAX_NUM_BOOKING_DAYS - len(days_to_book))]
    
    #Value will be used to cross reference dates and determine correct month for calendar widget
    first_day_to_book = days_to_book[0]

    #DEBUG
    sf = True


    '''
    Make sure ensure calendar location function is working 
    '''

    #Perform booking logic for each inividual day
    for curr_day in days_to_book:
        #DEBUG conditional
        if sf: 
            sf = False 
            continue 
        ensure_correct_calendar_loc(curr_day, first_day_to_book) #ensure driver is on correct calendar month 
        find_day_anchor_to_click(curr_day).click() #find and click anchor element to click to travel to the correct date on the calendar 
        general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, 'lc_rm_a') #wait until time slots are definitively clickable 
        #gather information for all possible bookings for current day
        cube_booking_data = gather_possible_bookings()
        ordered_key_set = cube_booking_data.get_ordered_key_set()
        times_to_bookable_cube_dict = cube_booking_data.get_times_to_bookable_cube_dict()
        #Given all possible booking information, we now need to determine the cubes we actually want to book
        booking_wizard = BookingWizard(ordered_key_set, times_to_bookable_cube_dict, user_manager)
        cubes_to_book = booking_wizard.get_cubes_to_book()
        #Now we begin the physical booking process

        print cubes_to_book

        booking_sm = BookingStateMachine(settings.driver, user_manager, cubes_to_book)
        booking_sm.start()




#MAIN METHOD
if __name__ == '__main__':
    #setup driver and globals
    settings.setup()
    #Initiate booker
    try:
        run_booker()
    except Exception as e:
        print e.message
        settings.driver.close()
    