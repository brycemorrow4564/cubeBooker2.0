class BookableCube: 
    
    def __init__(self, cube_num, time_available, cube_id): 
        self.cube_num = cube_num
        self.time_available = time_available
        self.cube_id = cube_id

    def get_cube_num(self): 
        return self.cube_num

    def get_time_available(self): 
        return self.time_available

    def get_cube_id(self): 
        return self.cube_id