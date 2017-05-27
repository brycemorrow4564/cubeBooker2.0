from UserManager import UserManager
from WaitWrapper import general_driver_wait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import settings 

class BookingStateMachine: 
    
    def __init__(self, driver, user_manager, cubes_to_book): 
        self.driver = driver 
        self.user_manager = user_manager
        self.cubes_to_book = cubes_to_book

    def start(self): 
        active_user = self.user_manager.get_active_user()
        while True: 
            click_state(self, active_user)
            #end of loop logic 
            if not self.user_manager.has_next_user():
                break 

    #In click state, BSM must ensure it can locate and click all buttons to book cubes for the active user
    def click_state(self, active_user): 
        for i in xrange(active_user.get_num_bookings()): 
            cube_to_book = self.cubes_to_book.pop(0)
            cube_id = cube_to_book.get_cube_id()
            try: 
                general_driver_wait(EC.element_to_be_clickable, By.ID, cube_id)
            except: 
                pass
            time_slot = settings.driver.find_element_by_id(cube_id)




    #Note: add fault tolerance so that if an error is encountered at any point, reclick cubes and try to book again
    def input_user_info(self, active_user):
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