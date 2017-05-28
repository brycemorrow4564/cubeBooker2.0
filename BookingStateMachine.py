from UserManager import UserManager
from WaitWrapper import general_driver_wait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time

import settings 

class BookingStateMachine: 
    
    def __init__(self, user_manager, cubes_to_book): 
        self.user_manager = user_manager
        self.cubes_to_book = cubes_to_book
        self.ordered_keys = sorted(cubes_to_book)


    def clear_slot_selections(self): 
        remove_btn_class = 'fa-trash-o'
        remove_btn_children = settings.driver.find_elements_by_class_name(remove_btn_class)
        print "here: " + str(remove_btn_children)
        if len(remove_btn_children) != 0:
            #there are remove buttons to click
            remove_btn_children[0].find_element_by_xpath('..').click()
            time.sleep(.3)
            self.clear_slot_selections() #recurse to avoid staleness since icons change location


    #In click state, BSM must ensure it can locate and click all buttons to book cubes for a given active user
    def click_state(self, active_user): 
        clicked_btn_class = 'lc_rm_t'
        num_bookings = active_user.get_num_bookings_left()
        num_keys = len(self.ordered_keys)
        #we shallow copy this bc we must make sure all buttons clicked before removing corresponding keys from actual object
        shallow_keys = list(self.ordered_keys)
        for i in xrange(min(num_keys, num_bookings)): 
            key = shallow_keys.pop(0)
            cube_to_book = self.cubes_to_book[key]
            cube_id = cube_to_book.get_cube_id()
            general_driver_wait(EC.element_to_be_clickable, By.ID, cube_id) #ensure time slot is in view and clickable
            time_slot = settings.driver.find_element_by_id(cube_id)

            #scroll into view? 
            settings.driver.execute_script("arguments[0].scrollIntoView(true);", time_slot)
            time.sleep(.5); 

            time_slot.click()
            time.sleep(.3)
            currently_clicked = settings.driver.find_elements_by_class_name(clicked_btn_class)
            btn_clicked = False
            for btn in currently_clicked: 
                if btn.get_attribute('id') == cube_id: 
                    #we have successfully clicked the target button 
                    btn_clicked = True 
                    break 
            if not btn_clicked: 
                print "we fucked up"
                #we somehow failed to click the button, clear all current selections and recursively call click_state
                self.clear_slot_selections()
                self.click_state(active_user)
        #all buttons correctly clicked, remove keys from list now
        for key in shallow_keys: 
            self.ordered_keys.remove(key)


    def start(self): 
        active_user = self.user_manager.get_active_user()
        while True: 
            self.click_state(active_user) #after click_state we are guaranteed to have clicked all desired slots 
            #Note: we do not decrement user booking count until request has been successfully submitted 
            self.submit_state(active_user)
            
            
            
            
            
            #end of loop logic 
            if not self.user_manager.has_next_user():
                break 


    def submit_state(self, active_user):
        #After cubes have been clicked and are ready to book, one of either two things can happen
        #1. Continue btn then submit time slots button 
        #2. no continue btn then submit time slots button
        #Detect if there is continue button. If so, click it 
        continue_btn_id = 'rm_tc_cont'
        general_driver_wait(EC.element_to_be_clickable, By.ID, continue_btn_id)
        driver.find_element_by_id(continue_btn_id).click()
        #Click Submit Time Slots button
        submit_btn_id = 's-lc-rm-sub'
        general_driver_wait(EC.element_to_be_clickable, By.ID, submit_btn_id)
        settings.driver.find_element_by_id(submit_btn_id).click()
        #Next, we must enter the active users login info 
        username_id = 'username'
        password_id = 'password'
        general_driver_wait(EC.visibility_of, By.ID, username_id)
        general_driver_wait(EC.visibility_of, By.ID, password_id)
        username_input = driver.find_element_by_id(username_id).send_keys(active_user.get_username())
        password_input = driver.find_element_by_id(password_id).send_keys(active_user.get_password())
        #Submit this data 
        user_info_submit_btn_class = 'form-button'
        driver.find_element_by_class_name(user_info_submit_btn_class).click()
        #Enter group nickname
        group_nickname = 'lit'
        nickname_input_id = 'nick'
        general_driver_wait(EC.visibility_of, By.ID, nickname_input_id)
        driver.find_element_by_id(nickname_input_id).send_keys(group_nickname)
        #Submit final booking
        final_submit_id = 's-lc-rm-sub'
        driver.find_element_by_id().click()
        #logout
        logout_id = 's-lc-rm-auth-lobtn'
        general_driver_wait(EC.element_to_be_clickable, By.ID, logout_id)
        driver.find_element_by_id(logout_id).click()
        #confirm logout
        button_class = 'form-button'
        general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, button_class)
        buttons = driver.find_elements_by_class_name(button_class)
        for button in buttons: 
            if button.text == "Yes":
                button.click()
        #return to booking page
        driver.get(main_page_url)