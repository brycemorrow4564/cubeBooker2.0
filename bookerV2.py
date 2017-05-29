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
from selenium.webdriver.common.action_chains import ActionChains

#Class Imports 
from BookableCube import BookableCube
from BookingWizard import BookingWizard
from BookingStateMachine import BookingStateMachine
from ProcessedBookingData import ProcessedBookingData
from User import User
from UserManager import UserManager
from CalendarManager import CalendarManager

#Function Imports
from WaitWrapper import general_driver_wait

#Import Custom Settings (Global Variables)
import settings



def run_booker():
    #Create UserManager object
    users = [User('bam4564', 'Bryc3m0rr0w@'), User('lucaswa', '#E03c55a6!!!!!'), User('dmtrump', 'climb3r1!!')]
    users = [User('bam4564', 'Bryc3m0rr0w@')] #DEBUG
    um = UserManager(users)

    #Important time information
    now = datetime.datetime.now()
    num_last_day = calendar.monthrange(now.year, now.month)[1]
    MAX_NUM_BOOKING_DAYS = 15 #library allows bookings a maximum of 2 weeks in advance (not including the current day)
    
    #Populate days_to_book which contains the numerical values of all days to book (so we can find the correct anchors in calendar)
    days_to_book = [i for i in xrange(now.day, num_last_day+1)] 
    if len(days_to_book) != MAX_NUM_BOOKING_DAYS: 
        days_to_book += [i+1 for i in xrange(MAX_NUM_BOOKING_DAYS - len(days_to_book))]

    #Create CalendarManager object
    cm = CalendarManager(days_to_book[0])

    #Perform booking logic for each inividual day
    for curr_day in days_to_book:
        #Use CalendarManager to ensure that the calendar is on the correct month and to click the correct day on calendar widget 
        cm.click_day(curr_day)
        #BookingWizard scrapes website for data and returns information on which cubes the user should book. 
        general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, 'lc_rm_a') #wait until time slots are definitively clickable 
        bw = BookingWizard(um)
        cubes_to_book = bw.get_cubes_to_book()
        ordered_keys = sorted(cubes_to_book)
        #Now we begin the physical booking process
        booking_sm = BookingStateMachine(um, cm, cubes_to_book)
        booking_sm.start()
        #cubes have been successfully booked, create json_



def main():
    settings.setup() #setup driver and globals
    try:
        run_booker()
    except Exception as e:
        print e.message
        settings.driver.close()

if __name__ == '__main__':
    main()
    


''' Externalize the function of calendar management !!!!!!!!! '''