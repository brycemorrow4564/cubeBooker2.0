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
    #users = [User('bam4564', '#Bryc3m0rr0w!'), User('lucaswa', '#E03c55a6!!!!!'), User('dmtrump', 'climb3r1!!')]
    users = [User('bam4564', '#Bryc3m0rr0w!')] #DEBUG
    user_manager = UserManager(users)

    now = datetime.datetime.now()
    num_last_day = calendar.monthrange(now.year, now.month)[1]
    MAX_NUM_BOOKING_DAYS = 15 #library allows bookings a maximum of 2 weeks in advance (not including the current day)
    
    days_to_book = [i for i in xrange(now.day, num_last_day+1)] #contains numerical value of days to book (August 7th -> 7)
    if len(days_to_book) != MAX_NUM_BOOKING_DAYS: 
        days_to_book += [i+1 for i in xrange(MAX_NUM_BOOKING_DAYS - len(days_to_book))]

    #DEBUG
    count = 0

    #Perform booking logic for each inividual day
    for curr_day in days_to_book:
        #DEBUG conditional
        if count < 2: 
            count += 1 
            continue 

        ensure_correct_calendar_loc(curr_day, days_to_book[0]) #ensure driver is on correct calendar month 
        find_day_anchor_to_click(curr_day).click() #find and click anchor element to click to travel to the correct date on the calendar 
        general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, 'lc_rm_a') #wait until time slots are definitively clickable 
        #gather information for all possible bookings for current day
        bw = BookingWizard(user_manager)
        cubes_to_book = bw.get_cubes_to_book()
        ordered_keys = sorted(cubes_to_book)
        #Now we begin the physical booking process
        booking_sm = BookingStateMachine(user_manager, cubes_to_book)
        booking_sm.start()



def main():
    settings.setup() #setup driver and globals

    #test for table scrolling functionality
    scroll_id = 's-lc-rm-scrolltb'
    table = settings.driver.find_element_by_id(scroll_id)






    try:
        run_booker()
    except Exception as e:
        print e.message
        settings.driver.close()

if __name__ == '__main__':
    main()
    