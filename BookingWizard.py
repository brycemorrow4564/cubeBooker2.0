from BookableCube import BookableCube

import settings

class BookingWizard: 

    def __init__(self, ordered_key_set, times_to_bookable_cube_dict, user_manager): 
        self.ordered_key_set = ordered_key_set
        self.times_to_bookable_cube_dict = times_to_bookable_cube_dict
        self.user_manager = user_manager

    def get_cubes_to_book(self): 
        max_possible_bookings = self.user_manager.get_num_possible_bookings() 
        priority_cubes = [1,7] #cubes 1 and 7 given priority since they are larger
        longest_streak = 0
        key_counter = 0
        cubes_to_book_dict = {} #maps datetime object to BookableCube object 
        curr_streak_cube = BookableCube(-1, -1, -1)
        for i in range(min(max_possible_bookings, len(self.ordered_key_set))): 
            key = self.ordered_key_set[i]
            available_cubes = self.times_to_bookable_cube_dict[key]
            available_priority_cubes = [x for x in available_cubes if x.get_cube_num() in priority_cubes]
            cube_to_book = BookableCube(-1, -1, -1)
            if len(available_cubes) != 0:
                cube_to_book = curr_streak_cube if curr_streak_cube in available_priority_cubes else available_cubes[0]
            else:
                cube_to_book = curr_streak_cube if curr_streak_cube in available_cubes else available_cubes[0]
            cubes_to_book_dict[key] = cube_to_book
            curr_streak_cube = cube_to_book
            key_counter += 1
        return sorted(cubes_to_book_dict)