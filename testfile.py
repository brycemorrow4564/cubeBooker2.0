#!/usr/bin/python
import datetime
import os.path
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#Function implemented to allow loading animations to finish prior to executing subsequent commands
def wait(howLong):
    start = time.time()
    while time.time() - start < howLong:
        continue

def numToWeekday(num): #order of list correlates to pythons time function values for days of the week
    week_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    return week_days[num]

def nextWeekday(weekday):
    week_days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    if weekday == "Saturday":
        return "Sunday"
    return week_days[week_days.index(weekday)+1]

#Given onyen parameter, returns password
def passFromOnyen(current_onyen):
    onyen_passwords = ['Bryc3m0rr0w!!','E03c55a6!!!','bread=12','crusty529!!!','climb3r!']
    if current_onyen == 'bam4564':
        return onyen_passwords[0]
    elif current_onyen == 'lucaswa':
        return onyen_passwords[1]
    elif current_onyen == 'aczejdo':
        return onyen_passwords[2]
    elif current_onyen == 'rnflemin':
        return onyen_passwords[3]
    elif current_onyen == 'dmtrump':
        return onyen_passwords[4]
    else:
        raise NoSuchElementException

#returns next onyen in onyen list
def nextOnyen(onyens, current_onyen):
    if onyens.index(current_onyen) == len(onyens)-1:
        return onyens[0]
    return onyens[onyens.index(current_onyen)+1]

#formats time data as HTML id of each particular booking slot
def minutesToStandardTimeString(minutes):
    words = []
    for info in minutes:
        if info[1] <= 660:
            words.append(str(info[1] // 60)+":"+str(info[1]%60)+"am"+" to "+str((info[1]+30) // 60)+":"+str((info[1]+30)%60)+"am")
        elif info[1] == 690:
            words.append(str(info[1] // 60)+":"+str(info[1]%60)+"am"+" to "+str((info[1]+30) // 60)+":"+str((info[1]+30)%60)+"pm")
        elif info[1] == 720:
            words.append(str(info[1] // 60)+":"+str(info[1]%60)+"pm"+" to "+str((info[1]+30) // 60)+":"+str((info[1]+30)%60)+"pm")
        elif info[1] == 750:
            words.append(str(info[1] // 60)+":"+str(info[1]%60)+"pm"+" to "+str((info[1]+30) // 60 - 12)+":"+str((info[1]+30)%60)+"pm")
        elif info[1] <= 1380:
            words.append(str(info[1] // 60 - 12)+":"+str(info[1]%60)+"pm"+" to "+str((info[1]+30) // 60 - 12)+":"+str((info[1]+30)%60)+"pm")
        else: #implicitly, info[1] == 1410.
            words.append(str(info[1] // 60 - 12)+":"+str(info[1]%60)+"pm"+" to "+str((info[1]+30) // 60 - 12)+":"+str((info[1]+30)%60)+"am")

    words = [x.replace(":0a",":00a") for x in words if ':0a']
    words = [x.replace(":0p",":00p") for x in words if ':0p']
    return words

def getMonth(month_num): #month_num is int between 1-12
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    return months[month_num-1]

def getMonthNumFromStr(month_str):
    month_str = month_str.strip()
    values = [1,2,3,4,5,6,7,8,9,10,11,12]
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    index = months.index(month_str)
    return values[index]

def daysInMonth(month, year):
    #numbers 1-12 represent months
    if month == "2":
        if isLeapYear(year):
            return 29
        else:
            return 28
    thirty = ["4","6","9","11"]
    if thirty.__contains__(month):
        return 30
    else:
        return 31

def nextMonth(month):
    if month == 12:
        return 1
    return month+1

def daysToBook(date, month, year):
    #returns list of days to book for
    days = []
    date_counter = date
    if daysInMonth(month,year) >= date + 14:
        return [(x,month,year) for x in range(date,date+15)]
    else:
        days = [(x,month,year) for x in range(date,daysInMonth(month,year)+1)]
    month = nextMonth(month)
    date = 1
    while len(days) != 15:
        days.append([date,month,year])
        date += 1
    return days

def standardTimeToMinutes(open_times):
    minute_times = []
    for n in open_times:
        if n[2] == 'am':
            if n[0] == 12:
                minute_times.append(n[1])
            else:
                minute_times.append(n[0]*60+n[1])
        else:
            if n[0] == 12:
                minute_times.append(n[0]*60+n[1])
            else:
                minute_times.append((n[0]+12)*60+n[1])
    return minute_times

def timeBreakdown(s):
    hour = int(s.split(':')[0][-2:])
    minute = int(s.split(':')[1][:2])
    suffix = s.split(':')[1][2:4]
    return [hour, minute, suffix]

def findCubesToBook(open_info):
    #open_info in form of [('1', 720), ('1', 750)]
    #Preference given to Cube 1 and Cube 7 because they are largest

    counters = [0 for x in range(7)]#each index represents counter for cube
    first_priority = second_priority = 0 #default value for highest priority cubes
    result = []
    lower = upper = 0 #default upper and lower bounds
    remove_these_indicies = []

    for elem in open_info:
        #if element represents time between 12am and 2am, skip booking

        if elem[1] <= 90:
            remove_these_indicies.append(open_info.index(elem))
            continue
        #increment counter for cube
        counters[elem[0]-1] += 1
        #if statements determine upper/lower available time bounds
        if open_info.index(elem) == 0:
            upper = lower = elem[1]
        if lower > elem[1]:
            lower = elem[1]
        if upper < elem[1]:
            upper = elem[1]

    #removes indicides representing times between 12am and 2am
    open_info = [open_info[x] for x in range(len(open_info)) if x not in remove_these_indicies]

    #determines which cube (1 or 7) has more available time slots
    if counters[0] > counters[6]:
        first_priority = 1
    else:
        second_priority = 7

    for n in range(lower,upper+1,30):#upper +1 so that upper bound is included
        previous_cube = 0 #default value
        if len(result) != 0:
            previous_cube = result[-1][0]

        possibilities = [[x[0],x[1]] for x in open_info if x[1] == n]

        #moves onto next value if there are no cubes at a certain time
        if not possibilities:
            continue

        #Used for tracking whether or not a value has been found
        sentinel = -1
        #Finds cube to book during specified time
        for x in possibilities:
            if x[0] == first_priority:
                result.append(x)
                sentinel = 0
                continue
        if sentinel == -1:
            for x in possibilities:
                if x[0] == second_priority:
                    result.append(x)
                    sentinel = 0
                    continue
        if sentinel == -1:
            cubes = [x[0] for x in possibilities]
            if previous_cube in cubes:
                result.append(possibilities[cubes.index(previous_cube)])
            else:
                result.append(possibilities[0])

    return result

#BEGINNING OF MAIN PROGRAM EXECUTION

hour_min_second = time.strftime("%H %M %S").split(" ")
date_month_year = time.strftime("%d %m %y").split(" ")
hour = int(hour_min_second[0]) #hour is on a 24 hour scale
date = int(date_month_year[0])
past_date = date #variable used to test whether or not month has changed
month = int(date_month_year[1])
year = int(date_month_year[2])
weekday = numToWeekday(datetime.datetime.today().weekday())

booking_days = daysToBook(date,month,year)

url = "http://calendar.lib.unc.edu/booking/davishub"
browser = webdriver.Chrome('/Users/brycemorrow/Downloads/chromedriver')
browser.get(url)

file_input = []

#Assumes that user enters information incorrectly given range of possible days
print('Please enter the following dates with the month first followed by a space and then the date (as an integer)')
print('The first possible date is',getMonth(booking_days[0][1]),booking_days[0][0],
      'and the last possible date is',getMonth(booking_days[len(booking_days)-1][1]),booking_days[len(booking_days)-1][0])
start_date = input('The program will execute starting at the following date: ').strip()
end_date = input('The program will terminate after processing the following date: ').strip()

start_info = start_date.split(' ')
start_month = getMonthNumFromStr(start_info[0])
start_date = int(start_info[1])
index_start_date = 0
for x in booking_days:
    if x[0] == start_date and x[1] == start_month:
        index_start_date = booking_days.index(x)

end_info = end_date.split(' ')
end_month = getMonthNumFromStr(end_info[0])
end_date = int(end_info[1])
index_end_date = 0
for x in booking_days:
    if x[0] == end_date and x[1] == end_month:
        index_end_date = booking_days.index(x)

'''
#Need in form of April 7
today = datetime.date.today()

start_month,end_month = booking_days[len(booking_days)-1][1]
start_date,end_date = booking_days[len(booking_days)-1][0]
'''

next_month_sentinel = 0 #sentinel value to determine whether or not program should switch months
ran_out_of_onyens = False #value to determine whether or not program used all onyens for last booking day

for n in booking_days:

    if booking_days.index(n) == index_start_date and getMonth(n[1]) not in browser.find_element_by_id('s-lc-rm-tg-h').text:
        next_month_sentinel += 1

    #Creates bounds for the program
    if booking_days.index(n) < index_start_date or booking_days.index(n) > index_end_date:
        weekday = nextWeekday(weekday)
        continue

    past_index = 0 #default value
    if booking_days.index(n) > 0:
        past_index = booking_days.index(n)-1
    if booking_days[past_index][0] > n[0]:
        next_month_sentinel += 1
    #as long as next_month_sentinel > 0, switch month with each iteration.

    if next_month_sentinel > 0 and getMonth(end_month) not in browser.find_element_by_id('s-lc-rm-tg-h').text:
        next_month_button = browser.find_element_by_css_selector('.ui-datepicker-next.ui-corner-all')
        next_month_button.click()
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-tg-h')))
    browser.find_element_by_link_text(str(n[0])).click() #clicks on booking day
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-tg-h')))

    file_input.append("Cube Bookings for "+weekday+", "+str(getMonth(n[1]))+" "+str(n[0])+", 20"+str(n[2])+"\n")

    print("day is: ",getMonth(n[1]),n[0],", 20"+str(n[2]))

    onyens = ['bam4564','lucaswa','aczejdo','rnflemin','dmtrump']
    current_onyen = onyens[0]
    current_onyen_pass = passFromOnyen(current_onyen)

    try:
        open_time_slots = browser.find_elements_by_class_name("lc_rm_a")
    except NoSuchElementException:
        print("No cubes are open on this date:",getMonth(n[1]),n[0]+",",n[2])
        continue

    aggregate_open_info = [x.get_attribute("title") for x in open_time_slots]
    cube_nums = [int(x[5:6]) for x in aggregate_open_info]
    open_times = map(timeBreakdown,aggregate_open_info)
    open_info = list(zip(cube_nums,standardTimeToMinutes(list(open_times))))
    cubes_to_book = findCubesToBook(open_info)
    time_str_list = minutesToStandardTimeString(cubes_to_book)

    total = []
    for x in range(len(cubes_to_book)):
        if time_str_list[x] == "11:30pm to 12:00am":
            time_str_list[x] = "11:30pm to 11:59pm" #discrepancy in website's time conversion
        total.append([cubes_to_book[x][0],time_str_list[x],getMonth((n[1])),n[0],n[2]])

    onyen_counter = 0 #keeps track of the amount of bookings the current onyen has made
    tc = 0 #total counter: keeps track of location in total

    login = True #default value for login, since it is necessary to login with first iteration of following loop
    #When there is a new day that is not the first day, it is necessary to logout and begin anew with first onyen
    logout_new_day = True
    if n[0] == start_date:
        logout_new_day = False

    while tc < len(total) and len(onyens) > 0: #book cubes one at a time

        past_index = 0 #default value
        if booking_days.index(n) > 0:
            past_index = booking_days.index(n)-1
        if booking_days[past_index][0] > n[0]:
            next_month_sentinel += 1
        #as long as next_month_sentinel > 0, switch month with each iteration.

        if next_month_sentinel > 0 and getMonth(end_month) not in browser.find_element_by_id('s-lc-rm-tg-h').text:
            next_month_button = browser.find_element_by_css_selector('.ui-datepicker-next.ui-corner-all')
            next_month_button.click()
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-tg-h')))
        browser.find_element_by_link_text(str(n[0])).click() #clicks on booking day
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-tg-h')))

        #allows table scrolling animation to finish
        wait(.4)

        print('Cube {0}, {1}, {2}, {3} {4}, {5}'.format(str(total[tc][0]),str(total[tc][1]),weekday,str(total[tc][2]),str(total[tc][3]),"20"+str(total[tc][4])))
        try:
            elem = browser.find_element_by_xpath('//*[@title="Cube {0}, {1}, {2}, {3} {4}, {5}"]'.format(str(total[tc][0]),str(total[tc][1]),weekday,str(total[tc][2]),str(total[tc][3]),"20"+str(total[tc][4])))
            print("SOMETHING WEIRD HAPPENED HERE")
        except:
            browser.get(url)
            break

        actions = ActionChains(browser)
        actions.move_to_element_with_offset(elem,2,16)
        actions.perform()

        elem = browser.find_element_by_xpath('//*[@title="Cube {0}, {1}, {2}, {3} {4}, {5}"]'.format(str(total[tc][0]),str(total[tc][1]),weekday,str(total[tc][2]),str(total[tc][3]),"20"+str(total[tc][4])))

        while elem.get_attribute('class') != 'lc_rm_a lc_rm_t':
            wait(.4)
            actions = ActionChains(browser)
            actions.move_to_element_with_offset(elem,2,2).click()
            actions.perform()

        print("click attempt was made")

        continue_button = browser.find_element_by_id("rm_tc_cont")
        continue_button.click()
        submit_times_button = browser.find_element_by_id("s-lc-rm-sub")
        submit_times_button.click()

        if logout_new_day == True and ran_out_of_onyens == False:
            logout_new_day = False
            print("It is a new day so this onyen will be logged out and the list will start at the beginning")
            current_onyen = onyens[0]
            current_onyen_pass = passFromOnyen(current_onyen)
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-auth-lobtn')))
            logout_button = browser.find_element_by_id('s-lc-rm-auth-lobtn')
            logout_button.click()
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'button')))
            signout_confirmation_button = browser.find_element_by_class_name('button')
            signout_confirmation_button.click()
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME,'reminder')))
            browser.get(url)
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-tg-h')))
            #booking day will be clicked when loop reiterates over this particular booking period.
            login = True
            continue

        if login == True:
            if ran_out_of_onyens == True:
                ran_out_of_onyens = False
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'onyen')))
            browser.find_element_by_id("onyen").send_keys(current_onyen)
            browser.find_element_by_id("onyenPassword").send_keys(current_onyen_pass)
            browser.find_element_by_id("action").click()
            login = False
            #after first login, enter nickname and submit booking

        #logout/login procedure for all other times
        if onyen_counter == 6: #condition determines whether or not to change onyens
            print("This onyen has made the maximum amount of bookings, it will now be removed from the onyen list")
            onyen_counter = 0
            onyen_to_remove = current_onyen
            current_onyen = nextOnyen(onyens,current_onyen)
            current_onyen_pass = passFromOnyen(current_onyen)
            onyens.remove(onyen_to_remove)
            if len(onyens) == 0:
                ran_out_of_onyens = True
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-auth-lobtn')))
            logout_button = browser.find_element_by_id('s-lc-rm-auth-lobtn')
            logout_button.click()
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'button')))
            signout_confirmation_button = browser.find_element_by_class_name('button')
            signout_confirmation_button.click()
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME,'reminder')))
            browser.get(url)
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 's-lc-rm-tg-h')))
            #booking day will be clicked when loop reiterates over this particular booking period.
            login = True
            continue

        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'nick')))
        group_name_box = browser.find_element_by_id("nick")
        group_name_box.send_keys("ABCD")
        submission_button = browser.find_element_by_id("s-lc-rm-sub")
        submission_button.click()

        error_encountered = False

        start = time.time()
        while time.time() - start < 2:
            try:
                assert "You cannot book more than one room at the same time!" not in browser.page_source
            except AssertionError:
                print("Error Caught: More than one cube booked at the same time\nemail will remain the same")
                #since you already have a cube booked, simply skip this booking time
                error_encountered = True
                tc += 1
                break
            try:
                assert 'Exceeded Daily time slot limit' not in browser.page_source
            except AssertionError:
                print("Error Caught: User exceeded daily time slot limit")
                #since user exceeded daily time limit, remove their onyen from onyen list and leave tc unchanged
                error_encountered = True
                onyen_counter = 6 #sets onyen counter to 6, so that onyen will be swapped with next loop iteration
                print("Invalid onyen removed, onyen to be swapped with next iteration")
                break
            continue

        if error_encountered == False: #if no error was encountered, execute the following
            if onyen_counter == 0:
                file_input.append("Onyen: "+str(current_onyen)+"\n")
            file_input.append('Cube {0}, {1}'.format(str(total[tc][0]),str(total[tc][1]))+"\n")
            tc += 1
            onyen_counter += 1 #cube successfully booked, onyen counter incremented

            while True:
                if "Success!" in browser.page_source:
                    break
            print("booking processed successfully")
            wait(.3)

        browser.get(url)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, 's-lc-rm-tg-h')))
        #allows table scrolling animation to finish
        wait(.4)

    weekday = nextWeekday(weekday)

#error where cube becomes unavailable during the booking process


#Booking has completed. Now begins process of writing information to file

if os.path.isfile('UpToDateCubeBookings.txt') == False:
    print("No previous cube data is available")
    fw = open("UpToDateCubeBookings.txt",'w')
    for line in file_input:
        fw.write(line)
    fw.close()
    exit()

#if program reaches this point, a cube booking log does exist
fr = open('UpToDateCubeBookings.txt','r')
previous_data_list = [x+str('\n') for x in fr.read().split('\n')]
fr.close()

#Create List of all indexes of date text
indexes_of_date_text = []
for n in previous_data_list:
    if "Cube Bookings" in n:
        indexes_of_date_text.append(previous_data_list.index(n))

for n in range(len(indexes_of_date_text)):

    cube_date = int(previous_data_list[indexes_of_date_text[n]][previous_data_list[indexes_of_date_text[n]].replace(',',' ',1).index(',')-2:previous_data_list[indexes_of_date_text[n]].replace(',',' ',1).index(',')])
    cube_month = (getMonthNumFromStr((previous_data_list[indexes_of_date_text[n]][previous_data_list[indexes_of_date_text[n]].index(',')+2:previous_data_list[indexes_of_date_text[n]].replace(',',' ',1).index(',')-2])))

    #Determine whether or not day is has passed.
    irrelevant_day = False

    if cube_month == booking_days[0][1] and cube_date < booking_days[0][0]:
        irrelevant_day = True

    #Strip irrelevant days
    if irrelevant_day == True:
        counter = indexes_of_date_text[n] #default value
        if n+1 < len(indexes_of_date_text): #if this is not final instance of date text
            while counter < indexes_of_date_text[n+1]:
                previous_data_list[counter] = 'Delete Later'
                counter += 1
        else: #this is final instance of date text
            while counter < len(previous_data_list):
                previous_data_list[counter] = 'Delete Later'
                counter += 1

    #Strip empty days from previous info
    if n+1 < len(indexes_of_date_text): #if this is not final instance of date text
        if indexes_of_date_text[n] + 1 == indexes_of_date_text[n+1]:
            previous_data_list[indexes_of_date_text[n]] = 'Delete Later'
    else: #this is final instance of date text
        if indexes_of_date_text[n] == len(previous_data_list)-1:
            previous_data_list[indexes_of_date_text[n]] = 'Delete Later'

previous_data_list = [x for x in previous_data_list if x != "Delete Later"]

#Next strip empty days from new file_input
indexes_of_date_text = []
for n in file_input:
    if "Cube Bookings" in n:
        indexes_of_date_text.append(file_input.index(n))

for n in range(len(indexes_of_date_text)):
    if n+1 < len(indexes_of_date_text): #if this is not final instance of date text
        if indexes_of_date_text[n] + 1 == indexes_of_date_text[n+1]:
            file_input[indexes_of_date_text[n]] = 'Delete Later'
    else: #this is final instance of date text
        if indexes_of_date_text[n] == len(file_input)-1:
            file_input[indexes_of_date_text[n]] = 'Delete Later'

file_input = [x for x in file_input if x != 'Delete Later']

#remove any empty space from previous data list and file input
previous_data_list = [x for x in previous_data_list if x.rstrip() != '']
file_input = [x for x in file_input if x.rstrip() != '']

#Write a new file with both previous data_list and file_input
fw = open("UpToDateCubeBookings.txt","w")
for line in previous_data_list:
    if 'Bookings' in line and previous_data_list.index(line) != 0:
        fw.write('\n')
    fw.write(line)
for line in file_input:
    if 'Cube Bookings' in line:
        fw.write('\n')
    fw.write(line)
fw.close()
