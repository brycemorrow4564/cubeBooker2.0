import re 
import datetime
import calendar
import collections
from time import gmtime, strftime

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from BookableCube import BookableCube
from BookingWizard import BookingWizard
from BookingStateMachine import BookingStateMachine
from ProcessedBookingData import ProcessedBookingData
from User import User
from UserManager import UserManager
from CalendarManager import CalendarManager
from WaitWrapper import general_driver_wait

import settings


def run_booker():
    #Create UserManager object
    users = [User('bam4564', 'Bryc3m0rr0w@'), User('lucaswa', '##E03c55a6!!!!!')]
    #users = [User('bam4564', 'Bryc3m0rr0w@')] #DEBUG
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
    cm = CalendarManager(days_to_book[0], days_to_book[0])

    #Perform booking logic for each inividual day
    for curr_day in days_to_book:
        #Use CalendarManager to ensure that the calendar is on the correct month and to click the correct day on calendar widget 
        cm.set_curr_day(curr_day)
        cm.click_day()
        #BookingWizard scrapes website for data and returns information on which cubes the user should book. 
        bw = BookingWizard(um)
        cubes_to_book = bw.run()
        #On to the next day if there are no cubes to book 
        if len(cubes_to_book) == 0: 
            continue
        #Now we begin the physical booking process
        booking_sm = BookingStateMachine(um, cm, cubes_to_book)
        booking_sm.start()
        #cubes have been successfully booked, create json_


def main():
    settings.setup()
    try:
        run_booker()
    except Exception as e:
        print e.message
        settings.driver.close()

if __name__ == '__main__':
    main()