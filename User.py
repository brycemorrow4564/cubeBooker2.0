class User:
    '''class to represents users who can book cubes'''

    MAX_BOOKINGS = 6

    def __init__(self, username, password): 
        self.username = username
        self.password = password
        self.num_bookings_left = User.MAX_BOOKINGS

    def get_username(self): 
        return self.username

    def get_password(self):
        return self.password

    def get_num_bookings_left(self): 
        return self.num_bookings_left

    def reset_num_bookings_left(self):
        self.num_bookings_left = User.MAX_BOOKINGS

    def decrement_num_bookings_left(self): 
        self.num_bookings_left -= 1
        if self.num_bookings_left < 0: 
            raise Exception("Decremented bookings below 0")

    def zero_num_bookings_left(self): 
        self.num_bookings_left = 0