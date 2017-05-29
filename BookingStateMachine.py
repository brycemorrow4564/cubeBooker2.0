from UserManager import UserManager
from WaitWrapper import general_driver_wait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time

import settings 

class BookingStateMachine: 

    scroll_table_id = 's-lc-rm-tg-scroll'
    remove_btn_class = 'fa-trash-o'
    clicked_slot_class = 'lc_rm_t'
    submit_btn_id = 's-lc-rm-sub'
    continue_btn_id = 'rm_tc_cont'
    username_id = 'username'
    password_id = 'password'
    user_info_submit_btn_class = 'form-button'
    group_nickname = 'not a robot'
    nickname_input_id = 'nick'
    final_submit_id = 's-lc-rm-sub'
    logout_id = 's-lc-rm-auth-lobtn'
    button_class = 'form-button'

    def __init__(self, user_manager, calendar_manager, cubes_to_book): 
        self.user_manager = user_manager
        self.calendar_manager = calendar_manager
        self.cubes_to_book = cubes_to_book
        self.ordered_keys = sorted(cubes_to_book) #Even though cubes_to_book is a dictionary, this returns its sorted key set 


    #Wrapper function that executes javascript to scroll the table 
    #Negative valued parameters scroll to left and positive values scroll to right
    def scroll_table(self, num_pixels): 
        settings.driver.execute_script('document.getElementById(arguments[0]).scrollLeft += arguments[1];', BookingStateMachine.scroll_table_id, num_pixels)


    def determine_viewport_bounds(self): 
        table_ref = settings.driver.find_element_by_id(BookingStateMachine.scroll_table_id).find_element_by_xpath('..')
        table_loc = table_ref.location
        table_size = table_ref.size
        side_buffer = 50
        left_vp_bound = table_loc['x'] + side_buffer #left viewport bound
        right_vp_bound = table_loc['x'] + table_size['width'] - side_buffer #right viewport bound
        return left_vp_bound, right_vp_bound


    def scroll_slots_into_view(self, book_these_cubes):
        self.scroll_table(-1000) #Ensure table is scrolled as far as possible to the left
        left_vp_bound, right_vp_bound = self.determine_viewport_bounds()
        #Scroll right by small increments until all 6 time slots to click are in view and are clickable
        slot_size = 30 #true for all slots
        while True:
            fail = False 
            for cube in book_these_cubes: 
                slot = settings.driver.find_element_by_id(cube.get_cube_id())
                slot_loc = slot.location 
                #Checks whether or not time slot is contained within the viewport bounds. 
                if slot_loc['x'] < left_vp_bound or slot_loc['x'] + slot_size > right_vp_bound:
                    fail = True 
                    break 
            if not fail: 
                break #if we don't fail, all cubes were in the viewport and we can break from the loop 
            self.scroll_table(50) #one or more cube(s) was not in the viewport so we scroll to the right 50 px a little and try again


    def clear_slot_selections(self): 
        remove_btn_children = settings.driver.find_elements_by_class_name(BookingStateMachine.remove_btn_class)
        if len(remove_btn_children) != 0:
            remove_btn_children[0].find_element_by_xpath('..').click()
            time.sleep(.3)
            self.clear_slot_selections() #recurse to avoid staleness since icons change location


    ''' Parameter passed in is number of bookings current user can make, 
        method returns a list of BookableCube objects that should be 
        booked by the current user. ''' 
    def user_cubes_to_book(self, num_bookings):
        book_these_cubes = list()
        for i in xrange(min(len(self.ordered_keys), num_bookings)): 
            key = self.ordered_keys[i]
            cube_to_book = self.cubes_to_book[key]
            book_these_cubes.append(cube_to_book)
        return book_these_cubes


    #In click state, BSM must ensure it can locate and click all buttons to book cubes for a given active user
    def click_state(self, active_user): 
        #populate book_these_cubes so we can pass to function and ensure they are in viewport
        book_these_cubes = self.user_cubes_to_book(active_user.get_num_bookings_left())
        #Now that we have all cubes to be booked by this user, ensure they are all in view. 
        self.scroll_slots_into_view(book_these_cubes)
        clicked_ids = list()
        #All cubes in view, iterate over list and click each one 
        for cube in book_these_cubes:
            cube_id = cube.get_cube_id()
            time_slot = settings.driver.find_element_by_id(cube_id)
            time_slot.click()
            time.sleep(.3)
            currently_clicked = settings.driver.find_elements_by_class_name(BookingStateMachine.clicked_slot_class)
            btn_clicked = False
            clicked_ids.append(cube_id)
            for slot in currently_clicked: 
                slot_id = slot.get_attribute('id')
                if slot_id not in clicked_ids: 
                    #We somehow clicked an incorrect button. Use calendar_manager to reset and then reenter click state
                    self.calendar_manager.click_day(self.calendar_manager.get_selected_month())
                if slot_id == cube_id: 
                    #we have successfully clicked the target button 
                    btn_clicked = True 
                    break 
            if not btn_clicked: 
                #we somehow failed to click the button, clear all current selections and recursively call click_state
                self.clear_slot_selections()
                self.click_state(active_user)
        #all buttons correctly clicked, remove keys from list now
        for i in xrange(min(len(self.ordered_keys), active_user.get_num_bookings_left())):
            self.ordered_keys.pop(0)
        

    def start(self): 
        active_user = self.user_manager.get_active_user()
        while True:
            self.click_state(active_user) #after click_state we are guaranteed to have clicked all desired slots 
            self.submit_state(active_user) #after submit_state we are guaranteed to have submitted our booking
            #Break out of loop if there are no more users to book under
            if not self.user_manager.has_next_user():
                break 
            #there is a next user, continue looping 
            active_user = self.user_manager.next_user()


    def submit_state(self, active_user):
        #Click continue button
        general_driver_wait(EC.element_to_be_clickable, By.ID, BookingStateMachine.continue_btn_id)
        settings.driver.find_element_by_id(BookingStateMachine.continue_btn_id).click()
        #Click submit button
        general_driver_wait(EC.element_to_be_clickable, By.ID, BookingStateMachine.submit_btn_id)
        settings.driver.find_element_by_id(BookingStateMachine.submit_btn_id).click()
        #Next, we must enter the active users login info
        general_driver_wait(EC.visibility_of_element_located, By.ID, BookingStateMachine.username_id)
        general_driver_wait(EC.visibility_of_element_located, By.ID, BookingStateMachine.password_id)
        username_input = settings.driver.find_element_by_id(BookingStateMachine.username_id).send_keys(active_user.get_username())
        time.sleep(.3) 
        password_input = settings.driver.find_element_by_id(BookingStateMachine.password_id).send_keys(active_user.get_password())
        #Submit this data
        settings.driver.find_element_by_class_name(BookingStateMachine.user_info_submit_btn_class).click()
        #Enter group nickname
        general_driver_wait(EC.visibility_of_element_located, By.ID, BookingStateMachine.nickname_input_id)
        settings.driver.find_element_by_id(BookingStateMachine.nickname_input_id).send_keys(group_nickname)
        time.sleep(.3)
        #Submit final booking
        settings.driver.find_element_by_id(BookingStateMachine.final_submit_id).click()
        #Logout
        general_driver_wait(EC.element_to_be_clickable, By.ID, BookingStateMachine.logout_id)
        settings.driver.find_element_by_id(BookingStateMachine.logout_id).click()
        #Confirm logout
        general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, BookingStateMachine.button_class)
        buttons = settings.driver.find_elements_by_class_name(BookingStateMachine.button_class)
        for button in buttons:
            if button.text == "Yes":
                button.click()