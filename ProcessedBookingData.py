class ProcessedBookingData:
    '''Wrapper class to encapsulate 2 pieces of cube data'''

    def __init__(self, ordered_key_set, times_to_bookable_cube_dict):
        self.ordered_key_set = ordered_key_set
        self.times_to_bookable_cube_dict = times_to_bookable_cube_dict

    def get_ordered_key_set(self):
        return self.ordered_key_set

    def get_times_to_bookable_cube_dict(self):
        return self.times_to_bookable_cube_dict