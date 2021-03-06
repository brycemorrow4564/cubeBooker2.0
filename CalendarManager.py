from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from WaitWrapper import general_driver_wait

import settings

class CalendarManager: 

    month_dropdown_class = 'ui-datepicker-month'
    next_btn_class = 'ui-datepicker-next'
    calendar_widget_class = 'ui-datepicker-calendar'

    def __init__(self, first_day_to_book, curr_day): 
        self.first_day_to_book = first_day_to_book
        self.curr_day = curr_day

    
    def get_curr_day(self): 
        return self.get_curr_day


    def set_curr_day(self, new_curr_day): 
        self.curr_day = new_curr_day


    def click_day(self): 
        settings.driver.get(settings.main_page_url) #refresh page to ensure we are in the correct state
        self.ensure_correct_calendar_loc() #ensure driver is on correct calendar month 
        self.find_day_anchor_to_click().click() #locate and click appropriate anchor element 
    

    #returns integer 1-12 representing the current selected month jan-dec
    def get_selected_month(self):
        general_driver_wait(EC.presence_of_element_located, By.CLASS_NAME, CalendarManager.month_dropdown_class)
        month_options = settings.driver.find_element_by_class_name(CalendarManager.month_dropdown_class).find_elements_by_css_selector("*")
        for month in month_options: 
            try: 
                if month.get_attribute('selected') is not None:
                    return int(month.get_attribute('value')) + 1 #offset by one since website represents months with integers 0-11 instead of 1-12
            except:
                pass #case of non-selected month
        raise Exception("Was not able to determine what the current selected month is") #unable to recover from this error 


    def ensure_correct_calendar_loc(self):
        old_month_num = self.get_selected_month() #returns integer 1-12
        if self.first_day_to_book > self.curr_day:
            settings.driver.find_element_by_class_name(CalendarManager.next_btn_class).click() #move calendar to next month
            new_month_num = self.get_selected_month()
            if new_month_num == old_month_num:
                self.click_day() #the button click did not work and we did not advance. Restart state
        

    def find_day_anchor_to_click(self):
        calendarWidget = settings.driver.find_element_by_class_name(CalendarManager.calendar_widget_class)
        possible_anchors = calendarWidget.find_elements_by_xpath('.//a') #gets all child anchor elements of calendar widget
        for anchor in possible_anchors:
            if int(anchor.text) == self.curr_day: 
                return anchor
        self.click_day() #We did not find the desired anchor but we can recover from this by  resettings state