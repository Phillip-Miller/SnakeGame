"""

A Python implementation of greedy snake game.

@Author  Phillip Miller
<Phillipmiller@sandiego.edu>
Date first created: 2 May 2020

"""
import random
import tkinter as tk
#from tkinter.font import Font
import time
from enum import IntEnum
import unittest
#from pprint import pprint
import copy

class Snake:
    """ This is the controller class. It connects the view class to the model class and allows a user to play the game with the
    keys on their keyboard. """
    def __init__(self):
        """ Initializes the snake game """
        # Define parameters
        self.times_clicked = 0
        self.NUM_ROWS = 30
        self.NUM_COLS = 30
        self.DEFAULT_STEP_TIME_MILLIS = 1000
        self.STEPTIME_MILLIS = self.DEFAULT_STEP_TIME_MILLIS
        self.is_running = False
        self.currentPoints = 0
        # Create view
        self.view = SnakeView(self.NUM_ROWS, self.NUM_COLS)
        self.Model = SnakeModel(self.NUM_COLS,self.NUM_ROWS)
        
        # Set up the control
        
        # Start
        self.view.set_start_handler(self.start_handler)
        
        # Pause
        self.view.set_pause_handler(self.pause_handler)

        # Wraparound
        self.view.set_wraparound_handler(self.wraparound_handler)

        # Reset 
        self.view.set_reset_handler(self.reset_handler)

        # Quit
        self.view.set_quit_handler(self.quit_handler)

        # Step speed
        self.view.set_step_speed_handler(self.step_speed_handler)
        
        self.view.set_left_handler(self.left_handler)
        self.view.set_right_handler(self.right_handler)
        self.view.set_down_handler(self.down_handler)
        self.view.set_up_handler(self.up_handler)

        # Start the simulation
        self.view.window.mainloop()
    
    def start_handler(self):
        """ Start simulation  """
        if not self.is_running:
            self.is_running = True
            self.view.schedule_next_step(self.STEPTIME_MILLIS, 
                                       self.continue_simulation)
            self.view.start_time = time.time()
        
    def pause_handler(self):
        """ Pause simulation """
        if self.is_running:
            self.view.cancel_next_step()
            self.is_running = False
            self.view.view_pause_time = float(self.view.str_var.get()[5:])
        
    def reset_handler(self):
        """ Reset simulation """
        self.quit_handler()
        snake_game = Snake()

    def quit_handler(self):
        """ Quit snake program """
        self.view.window.destroy()

    def step_speed_handler(self, value):
        """ Adjust snake speed"""
        self.STEPTIME_MILLIS = self.DEFAULT_STEP_TIME_MILLIS // int(value)                
  
    def wraparound_handler(self):
        """ Wraparound checkbox """
        if self.times_clicked % 2 == 0 : 
            self.Model.WRAP_MODE = True
            self.times_clicked += 1
        else:
            self.Model.WRAP_MODE = False
            self.times_clicked += 1
        
    
    def left_handler(self, event):
        """ What to do when users presses left"""
        self.Model.change_direction("W")
        
    def right_handler(self,event):
        """What to do when users presses right """
        self.Model.change_direction("E")
        
    def up_handler(self,event):
        """ What to do when users presses up"""
        self.Model.change_direction("N")

    def down_handler(self,event):
        """ What to do when users presses down """
        self.Model.change_direction("S")

    def continue_simulation(self):
        """ Perform another step of the simulation, and schedule
            the next step.
        """
        self.one_step()
        self.view.schedule_next_step(self.STEPTIME_MILLIS, self.continue_simulation)
    
    def death(self):
        """ Ends snake game when snake goes out of bounds or runs into itself"""
        self.is_running = False
        self.view.death = True
        self.pause_handler()
        self.view.view_game_over.set("GAME OVER")
        
    def one_step(self):
        """ Simulate one step of the snake game """
        if self.is_running:
            try:
                cell_list, self.currentPoints = self.Model.next_step()
                self.view.viewPoints.set("Points: " + str(self.currentPoints))
                self.view.view_points_per_sec.set("Points per sec: " + str(round(self.currentPoints/(self.view.newtime + .0000001),2)))
            except Exception:
                self.death()
            else:
                for row in range(self.NUM_ROWS):
                    for col in range(self.NUM_COLS):
                        if cell_list[row][col].cell_state == CellState.SNAKE:
                            self.view.make_snake(row, col)
                        elif cell_list[row][col].cell_state == CellState.SNAKE_HEAD:
                            self.view.make_head(row, col)
                        elif cell_list[row][col].cell_state == CellState.FOOD:
                            self.view.make_food(row, col)
                        else:
                            self.view.make_empty(row, col)
    
class SnakeView:
    """ This class controls the view of the board the snake is played on, which is divided into three sections:
    Grid, Control Frame and Score Frame. 
    """
    def __init__(self, num_rows, num_cols):
        """ Initialize view of the game """
        # Constants
        self.time_take_2 = 0
        self.death = False
        self.CELL_SIZE = 20 #Size in pixels
        self.CONTROL_FRAME_HEIGHT = 100
        self.SCORE_FRAME_WIDTH = 200
        # Size of grid
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.view_pause_time = 0
        self.start_time = time.time()
        self.newtime = 0
        # Create window
        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.str_var = tk.StringVar()
        self.str_var.set("Time: 0")
        self.view_game_over = tk.StringVar()
        self.view_game_over.set("      ")
        self.viewPoints = tk.StringVar()
        self.viewPoints.set("Points: 0")
        self.view_points_per_sec = tk.StringVar()
        self.view_points_per_sec.set("Points per second: 0")
        
        # Create frame for grid of cells, and put cells in the frame
        self.grid_frame = tk.Frame(self.window, height = num_rows * self.CELL_SIZE,
                                width = num_cols * self.CELL_SIZE)
        self.grid_frame.grid(row = 1, column = 1) # use grid layout manager
        self.cells = self.add_cells()
        
        # Create frame for controls
        self.control_frame = tk.Frame(self.window, width = (num_cols * self.CELL_SIZE) + self.SCORE_FRAME_WIDTH, 
                                height = self.CONTROL_FRAME_HEIGHT, borderwidth = 1, relief = "solid")
        self.control_frame.grid(row = 2, column = 1, columnspan = 2) # use grid layout manager
        (self.start_button, self.pause_button, 
                 self.wraparound_button, self.step_speed_slider, 
                 self.reset_button, self.quit_button) = self.add_control()
        
        # Create frame for scoring panel
        self.score_frame = tk.Frame(self.window, width = self.SCORE_FRAME_WIDTH, 
                                height = num_rows * self.CELL_SIZE)
        self.score_frame.grid(row = 1, column = 2) # use grid layout manager 
        (self.score_label, self.points_label, self.time_label, self.points_per_sec_label) = self.add_labels()   
        
        # Workaround for spacing the width of the column right 
        self.hidden_label = tk.Label(self.score_frame, text = "")
        self.hidden_label.grid(row=0, column=1, padx = self.SCORE_FRAME_WIDTH/2, pady = 10)
        self.game_over = tk.Label(self.score_frame, textvariable = self.view_game_over)
        self.game_over.grid(row = 100, column = 1)
    
    def reset_time(self):
        """ Stores the time at the start of the game"""
        self.start_time = time.time()
    
    def add_cells(self):
        """ Add cells to the grid frame """
        cells = []
        for r in range(self.num_rows):
            row = []
            for c in range(self.num_cols):
                frame = tk.Frame(self.grid_frame, width = self.CELL_SIZE, 
                           height = self.CELL_SIZE, borderwidth = 1, 
                           relief = "solid") 
                frame.grid(row = r, column = c) # use grid layout manager
                row.append(frame)
            cells.append(row)
        return cells
    
    def add_control(self):
        """ Create control buttons and slider, and add them to the control frame """
        start_button = tk.Button(self.control_frame, text="Start")
        start_button.grid(row=1, column=1,padx = 40, pady = self.CONTROL_FRAME_HEIGHT/2)
        pause_button = tk.Button(self.control_frame, text="Pause")
        pause_button.grid(row=1, column=2,padx = 40, pady = self.CONTROL_FRAME_HEIGHT/2)
        step_speed_slider = tk.Scale(self.control_frame, from_=1, to=10, 
                    label="Step Speed", showvalue=0, orient=tk.HORIZONTAL)
        step_speed_slider.grid(row=1, column=4,padx = 40, pady = self.CONTROL_FRAME_HEIGHT/2)
        reset_button = tk.Button(self.control_frame, text="Reset")
        reset_button.grid(row=1, column=5,padx = 40, pady = self.CONTROL_FRAME_HEIGHT/2)
        quit_button = tk.Button(self.control_frame, text="Quit")
        quit_button.grid(row=1, column=6,padx = 40, pady = self.CONTROL_FRAME_HEIGHT/2)
        checkValue = tk.BooleanVar()
        checkValue.set(False)
        wraparound_button = tk.Checkbutton(self.control_frame, text="Wraparound", var = checkValue)
        wraparound_button.grid(row=1, column=7,padx = 40, pady = self.CONTROL_FRAME_HEIGHT/2)

        # Vertically center the controls in the control frame
        self.control_frame.grid_rowconfigure(1, weight = 1) 

        # Horizontally center the controls in the control frame
        self.control_frame.grid_columnconfigure(0, weight = 1) 
        self.control_frame.grid_columnconfigure(7, weight = 1)
        return (start_button, pause_button, wraparound_button, step_speed_slider, 
                reset_button, quit_button)
    
    def set_wraparound_handler(self,handler):
        """ Set handler for clicking on wraparound checkbox to the function handler """
        self.wraparound_button.configure(command = handler)

    def set_start_handler(self, handler):
        """ Set handler for clicking on start button to the function handler """
        self.start_button.configure(command = handler)

    def set_pause_handler(self, handler):
        """ Set handler for clicking on pause button to the function handler """
        self.pause_button.configure(command = handler)

    def set_step_handler(self, handler):
        """ Set handler for clicking on step button to the function handler """
        self.step_button.configure(command = handler)

    def set_reset_handler(self, handler):
        """ Set handler for clicking on reset button to the function handler """
        self.reset_button.configure(command = handler)

    def set_quit_handler(self, handler):
        """ Set handler for clicking on quit button to the function handler """
        self.quit_button.configure(command = handler)

    def set_step_speed_handler(self, handler):
        """ Set handler for dragging the step speed slider to the function handler """
        self.step_speed_slider.configure(command = handler)
        
    def set_left_handler(self, handler):
        """ Set handler for clicking on left button to the function handler """
        self.window.bind('<Left>', handler)

    def set_right_handler(self, handler):
        """ Set handler for clicking on right button to the function handler """
        self.window.bind('<Right>', handler)

    def set_up_handler(self, handler):
        """ Set handler for clicking on up button to the function handler """
        self.window.bind('<Up>', handler)

    def set_down_handler(self, handler):
        """ Set handler for clicking down button to the function handler """
        self.window.bind('<Down>', handler) 
    
        
    def add_labels(self):
        """ 
        Create labels and add them to the score frame 
        """
        score_label = tk.Label(self.score_frame, text="Score")
        score_label.grid(row=1, column=1, pady = 10)
        points_label = tk.Label(self.score_frame, textvariable = self.viewPoints,borderwidth = 1, relief = "solid")
        points_label.grid(row=2, column=1, pady = 10)
        time_label = tk.Label(self.score_frame, textvariable= self.str_var ,borderwidth = 1, relief = "solid")
        time_label.grid(row=3, column=1, pady = 10)
        points_per_sec_label = tk.Label(self.score_frame, textvariable = self.view_points_per_sec,borderwidth = 1, relief = "solid")
        points_per_sec_label.grid(row=4, column=1, pady = 10)                                                    
        return (score_label, points_label, time_label, points_per_sec_label)
    
    def schedule_next_step(self, step_time_millis, step_handler):
        """ Schedules next step of the simulation """
        if not self.death:
            self.time_take_2 += step_time_millis / 1000
            self.newtime = self.time_take_2
            self.start_timer_object = self.window.after(step_time_millis, step_handler)
            self.str_var.set("Time: " + str(round(self.newtime,2)))

    def make_food(self, row, column):
        """ Make cells with the state FOOD red """
        self.cells[row][column]['bg'] = 'Red'

    def make_head(self, row, column):
        """ Make cell with the state SNAKE_HEAD black """
        self.cells[row][column]['bg'] = 'Black'
    def make_empty(self, row, column):
       """ Make cells with the state EMPTY white """
       self.cells[row][column]['bg'] = 'White'
    def make_snake(self, row, column):
        """ Make cells with the state SNAKE blue """
        self.cells[row][column]['bg'] = 'Blue'

    def reset(self):
        """ Reset entire snake game board, all cells empty """
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.cells[r][c]
                
    def cancel_next_step(self):
        """ Cancel the scheduled next step of simulation """
        self.window.after_cancel(self.start_timer_object)

class SnakeModel:
    """ This class keeps track of the snake game's rules. """
    def __init__(self,num_cols,num_rows):
        """ Initialize the model of the game """
        # To access list value it is [row][column] which is more or less xy
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.current_points = 0
        self.WRAP_MODE = False
        self.grow_check = False
        
        # Build array of cell objects
        self.cell_list = []
        for row in range(num_rows):
            rowlist = []
            for col in range(num_cols):
                rowlist.append(Cell(CellState.EMPTY,col,row))
            self.cell_list.append(rowlist)
        self.next_direction = ""    
        self.snake_locations = []   # List of Cell Objects, in order, where front is always snake head
        self.food_cell = None   # Initialize food cell object
        self.random_snake_start()   # Gives snake location and direction
        self.empty_cell_list = self.empty_Cells()   # Cell onjects not currently occupied by food or snake (0,0) is top left
        self.random_food()
    
    def random_food(self):
        """ Pops a random element from the empty cell list. Make sure empty cell list is up to date before calling this """
        # Get cell is no longer empty
        popd = self.empty_cell_list.pop(random.randrange(len(self.empty_cell_list)))
        # Change State in the cell_list
        self.cell_list[popd.y][popd.x].cell_state = CellState.FOOD
        self.food_cell = popd
    
    def random_snake_start(self):
        """ As per start up we pick a random cell and have it be the head """
        # Randomly select cell onject from a list of lists
        snake_start = random.choice(random.choice(self.cell_list))
#       Update Cell List
        self.cell_list[snake_start.y][snake_start.x].cell_state = CellState.SNAKE_HEAD
#       Insert snake_start in snake locations
        copy_start = copy.deepcopy(snake_start)
        self.snake_locations.append(copy_start)
#       Calculate Initial Direction
        top,left = snake_start.y,snake_start.x
        bott,right = self.num_rows - snake_start.y, self.num_cols - snake_start.x
        var = {top:"N",bott:"S",left:"W",right:"E"}
        self.next_direction = var.get(max(var))
        
    def empty_Cells(self):
        """
        Calculates the empty cells in self.cell_state for use
        Updates and Returns empty_cells, a list of all the empty cells on the board
        """
        empty_cells = []
        for col in self.cell_list:
            for element in col:
                if element.cell_state == CellState.EMPTY:
                    empty_cells.append(element)
        self.empty_cell_list = empty_cells
        return empty_cells

    def next_step(self):
        """ Move snake in direction, check for events such as food or death, update open cells, update score. """
        self.move2()
        self.grow_check = False
        self.check_events()
        return self.cell_list, self.current_points
    
    def eat(self):
        """" Makes snake bigger and eats """
        # Increase Size
        self.grow2()
        self.empty_Cells()
        self.random_food()
        self.current_points += 1
        
    def die(self):
        """ Ends the game when snake dies """
        raise Exception("User Died")
        
    def change_direction(self, direction):
        """
        Param: Self, Direction in a string N,S,E,W
        Make sure this is only called once per timestep
        """
        self.next_direction = direction 
   
    def grow2(self):
        """ If the snake lands upon food, add one cell to its length"""
        self.grow_check = True
    
    def move2(self):
        """ Move snake in user-chosen direction """
        try:
            snake_x = self.snake_locations[0].x
            snake_y = self.snake_locations[0].y
            
            if len(self.snake_locations) > 1:
                self.cell_list[snake_y][snake_x].cell_state = CellState.SNAKE
                
            if self.next_direction== "N":
                snake_y -= 1 #increment Y up one
            if self.next_direction== "S":
                snake_y += 1 #increment Y down one
            if self.next_direction== "E":
                snake_x += 1 #increment X up one
            if self.next_direction== "W":
                snake_x -= 1 #increment X down one
            if snake_x < 0 or snake_y <0 : 
                raise Exception("Death or Wrap")
                
            self.cell_list[snake_y][snake_x].cell_state
            new_head = Cell(CellState.SNAKE_HEAD,snake_x,snake_y)
            self.snake_locations.insert(0,new_head)
            self.check_valid(new_head)
            self.cell_list[snake_y][snake_x].cell_state = CellState.SNAKE_HEAD
        
        except IndexError:
            if self.WRAP_MODE:
                if self.next_direction == "N" :
                    snake_y = self.num_rows - 1
                if self.next_direction == "S":
                    snake_y = 0
                if self.next_direction == "W" :
                    snake_x = self.num_cols - 1
                if self.next_direction == "E":
                    snake_x = 0
                new_head = Cell(CellState.SNAKE_HEAD,snake_x,snake_y)
                self.snake_locations.insert(0,new_head)
                self.check_valid(new_head)
                self.cell_list[snake_y][snake_x].cell_state = CellState.SNAKE_HEAD
            else: 
                self.die()
                raise Exception("Death")
        if not self.grow_check:
            self.cell_list[self.snake_locations[-1].y][self.snake_locations[-1].x].cell_state = CellState.EMPTY
            self.snake_locations.pop()
        else:
            self.cell_list[self.snake_locations[0].y][self.snake_locations[0].x].cell_state = CellState.SNAKE
            self.snake_locations[1].cell_state = CellState.SNAKE
    
    def check_valid(self,location):
        """Param: Self, and Cell Object of location that you wish to move into
        Checkes to see if anything currently occupies the cell
        """
        if self.cell_list[location.y][location.x].cell_state == CellState.SNAKE:
            self.die()
    def check_events(self):
        """
        Check if:
            SnakeHead hit itself
            SnakeHead out of bounds
            Snake landed on food
        """
#       Hit food
        if self.snake_locations[0] == self.food_cell or self.food_cell.cell_state != CellState.FOOD:
            self.eat()
#       Hit wall 
        if (self.snake_locations[0].x > self.num_cols or self.snake_locations[0].y > self.num_rows 
            or self.snake_locations[0].x < 0 or self.snake_locations[0].y < 0):
            self.die()
#       Runs into self
        head = self.snake_locations[0]
        for location in range(len(self.snake_locations)):
            # Head will obviously match itself
            if location > 0 and head == self.snake_locations[location]:
                self.die()

class Cell():
    """ This class defines a cell by location and by state """
    def __init__(self,state,xcord,ycord):
        """ Initializes cell object """
        self.cell_state = state
        self.x = xcord
        self.y = ycord
        
    def __str__(self):
        """ Prints out a cell object in format: STATE[x, y] """
        return ((str(self.cell_state))[10:] + str([self.x,self.y]))
    def __repr__(self):
        """ Returns representation of cell object as a string """
        return str(self)

class CellState(IntEnum):
    """ 
    Use IntEnum so that the board cells can be classified as either EMPTY, SNAKE, SNAKE_HEAD or FOOD
    """
    EMPTY = 0
    SNAKE = 1
    SNAKE_HEAD = 2
    FOOD = 3   
class SnakeModelTest(unittest.TestCase):
    """ 
    For testing the methods of the SnakeModel class.
    """
    def test_countEmpty(self):
        self.x = []
        for i in range(10):
            y = []
            for j in range(10):
                y.append(Cell)

if __name__ == "__main__":
   snake_game = Snake()