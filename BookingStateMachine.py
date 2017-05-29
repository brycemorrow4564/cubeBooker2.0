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
        self.ordered_keys = sorted(cubes_to_book) #Even though cubes_to_book is a dictionary, this returns its sorted key set 


    def scroll_slots_into_view(self, book_these_cubes):
        #Scroll all the way left to reset scroller (for some reason scrollRight isn't working????)
        settings.driver.execute_script('document.getElementById("s-lc-rm-tg-scroll").scrollLeft -= 1000;')
        #Determine bounds of viewport so we can ensure that all elements fall inside viewport 
        table_ref = settings.driver.find_element_by_id('s-lc-rm-tg-scroll').find_element_by_xpath('..')
        table_loc = table_ref.location
        table_size = table_ref.size
        side_buffer = 50
        left_vp_bound = table_loc['x'] + side_buffer #left viewport bound
        right_vp_bound = table_loc['x'] + table_size['width'] - side_buffer #right viewport bound
        #Scroll right by small increments until all 6 time slots to click are in view and are clickable
        slot_size = 30 #true for all slots
        while True:
            fail = False 
            for cube in book_these_cubes: 
                slot = settings.driver.find_element_by_id(cube.get_cube_id())
                slot_loc = slot.location 
                #Checks whether or not time slot is contained withing the viewport bounds. 
                if slot_loc['x'] < left_vp_bound or slot_loc['x'] + slot_size > right_vp_bound:
                    fail = True 
                    break 
            if not fail: 
                #if we don't fail, all cubes were in the viewport and we can break from the loop 
                break 
            #one or more cube(s) was not in the viewport so we scroll to the right 50 px a little and try again
            settings.driver.execute_script('document.getElementById("s-lc-rm-tg-scroll").scrollLeft += 50;')


    def clear_slot_selections(self): 
        remove_btn_class = 'fa-trash-o'
        remove_btn_children = settings.driver.find_elements_by_class_name(remove_btn_class)
        if len(remove_btn_children) != 0:
            #there are remove buttons to click
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
        clicked_slot_class = 'lc_rm_t'
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
            currently_clicked = settings.driver.find_elements_by_class_name(clicked_slot_class)
            btn_clicked = False
            clicked_ids.append(cube_id)
            for slot in currently_clicked: 
                slot_id = slot.get_attribute('id')
                if slot_id not in clicked_ids: 
                    raise Exception("Incorrect button was clicked")
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
            #Note: we do not decrement user booking count and switch active user until request has been successfully submitted 
            self.submit_state(active_user)


            #end of loop logic 
            if not self.user_manager.has_next_user():
                break 


    def submit_state(self, active_user):
        #After cubes have been clicked and are ready to book, one of either two things can happen
        continue_btn_id = 'rm_tc_cont'
        general_driver_wait(EC.element_to_be_clickable, By.ID, continue_btn_id)
        settings.driver.find_element_by_id(continue_btn_id).click()
        #Click Submit Time Slots button
        submit_btn_id = 's-lc-rm-sub'
        general_driver_wait(EC.element_to_be_clickable, By.ID, submit_btn_id)
        settings.driver.find_element_by_id(submit_btn_id).click()
        #Next, we must enter the active users login info 
        username_id = 'username'
        password_id = 'password'
        general_driver_wait(EC.visibility_of_element_located, By.ID, username_id)
        general_driver_wait(EC.visibility_of_element_located, By.ID, password_id)
        username_input = settings.driver.find_element_by_id(username_id).send_keys(active_user.get_username())
        time.sleep(.3)
        password_input = settings.driver.find_element_by_id(password_id).send_keys(active_user.get_password())
        #Submit this data 
        user_info_submit_btn_class = 'form-button'
        settings.driver.find_element_by_class_name(user_info_submit_btn_class).click()
        #Enter group nickname
        group_nickname = 'not a robot'
        nickname_input_id = 'nick'
        general_driver_wait(EC.visibility_of_element_located, By.ID, nickname_input_id)
        settings.driver.find_element_by_id(nickname_input_id).send_keys(group_nickname)
        time.sleep(.3)
        #Submit final booking
        final_submit_id = 's-lc-rm-sub'
        settings.driver.find_element_by_id(final_submit_id).click()
        #logout
        logout_id = 's-lc-rm-auth-lobtn'
        general_driver_wait(EC.element_to_be_clickable, By.ID, logout_id)
        settings.driver.find_element_by_id(logout_id).click()
        #confirm logout
        button_class = 'form-button'
        general_driver_wait(EC.element_to_be_clickable, By.CLASS_NAME, button_class)
        buttons = settings.driver.find_elements_by_class_name(button_class)
        for button in buttons: 
            if button.text == "Yes":
                button.click()
        #return to booking page

        print "would refresh after this"
        exit()
        settings.driver.get(main_page_url)