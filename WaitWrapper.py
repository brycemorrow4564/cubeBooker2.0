from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import settings

''' General purpose driver wait function wrapper
    example would be wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'lc_rm_a')))
    ecFunc   = EC.element_to_be_clickable
    byAttrib = By.CLASS_NAME
    byValue  = 'lc_rm_a' '''
def general_driver_wait(ecFunc, byAttrib, byValue):
    settings.wait.until(ecFunc((byAttrib, byValue)))