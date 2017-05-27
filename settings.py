from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

#General driver and executable path setup 
def driver_setup(): 
    gecko_path = '/Users/brycemorrow/Documents/Projects/cubeBooker2.0/geckodriver' #path to geckodriver.exe for firefox
    driver = webdriver.Firefox(executable_path=gecko_path)
    url = 'http://calendar.lib.unc.edu/booking/davishub'
    driver.get(url)
    driver.set_window_size(1200, 900)
    return driver

def setup(): 
    global driver, main_page_url, timeout_delay, wait
    #Set values of global variables
    driver = driver_setup()
    main_page_url = 'http://calendar.lib.unc.edu/booking/davishub'
    timeout_delay = 10
    wait = WebDriverWait(driver, timeout_delay)