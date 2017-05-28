from UserManager import UserManager
from WaitWrapper import general_driver_wait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import settings 

class BookingStateMachine: 
    
    def __init__(self, user_manager, cubes_to_book): 
        self.user_manager = user_manager
        self.cubes_to_book = cubes_to_book
        self.ordered_keys = sorted(cubes_to_book)

    def clear_slot_selections(self): 
        remove_btn_container = settings.driver.find_element_by_id('s-lc-rm-datetime')
        remove_btns = remove_btn_container.find_elements_by_xpath('.//a')
        if remove_btns is not None and len(remove_btns) == 0: 
            #recursively call function after removing single button to avoid staleness
            remove_btns[0].click()
            self.clear_slot_selections()

    #In click state, BSM must ensure it can locate and click all buttons to book cubes for a given active user
    def click_state(self, active_user): 
        clicked_btn_class = 'lc_rm_t'
        for i in xrange(active_user.get_num_bookings_left()): 
            key = self.ordered_keys.pop(0)
            cube_to_book = self.cubes_to_book[key]
            cube_id = cube_to_book.get_cube_id()
            general_driver_wait(EC.element_to_be_clickable, By.ID, cube_id) #ensure time slot is in view and clickable
            time_slot = settings.driver.find_element_by_id(cube_id)
            time_slot.click()
            currently_clicked = settings.driver.find_elements_by_class_name(clicked_btn_class)
            btn_clicked = False
            for btn in currently_clicked: 
                if btn.get_attribute('id') == cube_id: 
                    #we have successfully clicked the target button 
                    btn_clicked = True 
                    break 
            if not btn_clicked: 
                #we somehow failed to click the button, clear all current selections and recursively call click_state
                self.clear_slot_selections()
                self.click_state(active_user)


    def start(self): 
        active_user = self.user_manager.get_active_user()
        while True: 
            self.click_state(active_user) #after click_state we are guaranteed to have clicked all desired slots 
            #Note: we do not decrement user booking count until request has been successfully submitted 
            submit_state(self, active_user)
            
            
            
            
            
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