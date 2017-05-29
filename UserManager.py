from User import User

class UserManager: 
    '''object to represent a cycle of users. Each booking day, a 
    new user cycler object will be created since you can reserve 
    6 booking times each day'''

    def __init__(self, users):
        if len(users) == 0: 
            raise Exception("You attempted to create a UserManager with no users.")
        for user in users: 
            if not isinstance(user, User): 
                raise Exception("One or more of the elements in users was not a valid User Object")
            user.reset_num_bookings_left() #ensure each user has correct number of max bookings remaining
        self.original_list = list(users) #used to reset user manager for each new day
        self.active_user = users.pop(0)
        self.users_left = users
        
    #resets user manager to original state where all users are active
    #It is programmers responsibility to call this function outside this class when necessary
    def reset_user_manager(self): 
        temp_list = list(self.original_list) #shallow copy original_list so we only get its value
        self.active_user = temp_list.pop(0)
        self.users_left = temp_list

    def get_active_user(self): 
        return self.active_user

    def has_next_user(self): 
        return len(self.users_left) > 0 

    def next_user(self): 
        if not self.has_next_user(): 
            raise Exception("There is no next user for this given day")
        self.active_user = users_left.pop(0)
        return self.active_user

    def get_num_possible_bookings(self):
        return sum([user.get_num_bookings_left() for user in self.users_left] + [self.active_user.get_num_bookings_left()])
