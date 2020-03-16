# controller.py
# Steven F. Sholes (sfs86)
# skeleton by Walker M. White (wmw2), Lillian Lee (LJL2), Steve Marschner (SRM2)
# Spring 2013
# May 3, 2013
# Note: I did not look at the posted solutions, this is 100% my attempt
"""Controller module for Breakout

This module contains a class and global constants for the game Breakout.
Unlike the other files in this assignment, you are 100% free to change
anything in this file. You can change any of the constants in this file
(so long as they are still named constants), and add or remove classes.

Extensions: I implemented a counter that keeps track of how many lives
you have left that stays in the bottom left corner while you play."""

from colormodel import *
import random
from graphics import *

# CONSTANTS

# Width of the game display (all coordinates are in pixels)
GAME_WIDTH  = 480
# Height of the game display
GAME_HEIGHT = 620

# Width of the paddle
PADDLE_WIDTH = 58
# Height of the paddle
PADDLE_HEIGHT = 11
# Distance of the (bottom of the) paddle up from the bottom
PADDLE_OFFSET = 60

# Horizontal separation between bricks
BRICK_SEP_H = 5
# Vertical separation between bricks
BRICK_SEP_V = 4
# Height of a brick
BRICK_HEIGHT = 8
# Offset of the top brick row from the top
BRICK_Y_OFFSET = 70

# Number of bricks per row
BRICKS_IN_ROW = 10
# Number of rows of bricks, in range 1..10.
BRICK_ROWS = 10
# Width of a brick
BRICK_WIDTH = float(GAME_WIDTH)/BRICKS_IN_ROW - BRICK_SEP_H

# Diameter of the ball in pixels
BALL_DIAMETER = 18

# Number of attempts in a game
NUMBER_TURNS = 3

# Basic game states
# Game has not started yet
# If the state is STATE_INACTIVE, there is a welcome message in the view;
# If the state is not STATE_INACTIVE there is no welcome message in the view;
STATE_INACTIVE = 0
# Game is active, but waiting for next ball
STATE_PAUSED   = 1
# Ball is in play and being animated
STATE_ACTIVE   = 2
# Game is over, deactivate all actions
STATE_COMPLETE = 3

# ADD MORE CONSTANTS (PROPERLY COMMENTED) AS NECESSARY

# The text that is displayed on startup
STARTUP_TEXT = "Click to Start"
# The x-position of the startup text
STARTUP_X = (GAME_WIDTH/2.) - len(STARTUP_TEXT)*2
# The y-position of the startup text
STARTUP_Y = (GAME_HEIGHT/2.)

#The list of brick colors
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, CYAN]

# The initial horizontal offset of the bricks
BRICK_X_OFFSET = float(GAME_WIDTH - BRICKS_IN_ROW*BRICK_WIDTH - (BRICKS_IN_ROW -1)*BRICK_SEP_H)/2

# The initial vertical velocity of the ball
INITIAL_VY = 5.0

# The number of lives the player has
NUM_LIVES = 3


# CLASSES
class Breakout(GameController):
    """Instance is the primary controller for a Breakout game.

    This class extends GameController and implements the various methods
    necessary for running the game.

        Method initialize starts up the game.

        Method update animates the ball and provides the physics.

        The on_touch methods handle mouse (or finger) input.

    Below are instance variables we (strongly) suggest you use.  You may also
    add other instance variables (such as those suggested in the handout); if
    you do, BE SURE TO ADD CLASS-INVARIANT COMMENTS: what your variables mean,
    and what's always true about them.  This is a *very important* habit for
    your later programming lives.

    _state [int]: Current play state of the game; needed by the on_touch methods
                  Invariant: One of STATE_INACTIVE, STATE_PAUSED, STATE_ACTIVE,
                  STATE_COMPLETE

    _bricks [list of Brick]: List of currently active "bricks" in the game.
                             Empty if and only if _state is STATE_INACTIVE
                             or STATE_COMPLETE

    _paddle [Paddle]: The player's paddle.  Is None if and only if _state is
                      STATE_INACTIVE or STATE_COMPLETE

    _ball [Ball]: The ball.  Is None if and only if _state is not STATE_ACTIVE

    STARTUP [Message]: A message displayed on the screen.  Is None if and
                       only if _state is STATE_ACTIVE
                       
    _lives [int]: The number of lives the player has left. If =0 then the player
                    has lost.
    
    _message [Message]: A message displayed on the screen after a player loses a life.
    
    _congrats [Message]: A message displayed on the screen when the player wins.
    
    _youlose [Message]: A message displayed on the screen when the player loses.
    
    _displayLives [Message]: A message displayed on the screen to alert to the player about
                                the number of alive he/she has left.
                                
    _displayLivesNum [Message]: A str(int) that displays the remaining lives available.
    """

    # METHODS

    def initialize(self):
        """Initialize the game state.

        Initialize any state variables as necessary to satisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game.
        
        See Documentation of Breakout to see variable meanings."""

        self._state  = STATE_INACTIVE
        self._bricks = []
        self._paddle = self._createpaddle((GAME_WIDTH/2))
        self._ball = None
        self.STARTUP = GLabel(text=STARTUP_TEXT, x=STARTUP_X, y=STARTUP_Y)
        self.view.add(self.STARTUP)
        self._lives = NUM_LIVES
        self._message = GLabel(text='You have '+ `self._lives` + ' lives left\nClick to start next round',
                               x=STARTUP_X, y=STARTUP_Y)
        self._congrats = GLabel(text='Congratulations!\nYou Won!',
                                x=STARTUP_X, y=STARTUP_Y)
        self._youlose = GLabel(text='Sorry, you lost.', x=STARTUP_X, y=STARTUP_Y)
        self._displayLives = GLabel(text='Lives Remaining: ',x = 10, y=10)
        self.view.add(self._displayLives)
        self._displayLivesNum = GLabel(text=`self._lives`,x = 135, y=10)
        self.view.add(self._displayLivesNum)
        
    def update(self, dt):
        """Animate a single frame in the game.

        This is the method that does most of the work.  It moves the ball
        (if there is one), and looks for any collisions.  If there is a
        collision, it changes the velocity of the ball and removes any bricks
        if necessary.

        This method may need to change the state of the game.  If the ball
        goes off the screen, change the state to either STATE_PAUSED (if the
        player still has some tries left) or STATE_COMPLETE (game over).  If 
        the last brick is removed, change _state to STATE_COMPLETE (game over).
        Display messages as appropriate.

        Precondition: dt is the time since last update (a float).  You can
        ignore it."""
        if self._state == STATE_COMPLETE:
            self.view.remove(self._ball)
            self.view.remove(self._paddle)
            self.view.remove(self._displayLives)
            self.view.remove(self._displayLivesNum)
        self._testEndGame()
        self._testWallCollision()

    def on_touch_down(self,view,touch):
        """Respond to the mouse (or finger) being pressed (but not released)

        This method changes the game state, possibly moving from the current
        state to STATE_ACTIVE, doing whatever work is required to carry out that
        transition.  It also moves the paddle if appropriate.

        Precondition: <view> is just the view attribute (unused because we have
        access to the view attribute).  <touch> is a MotionEvent, which has
        attributes <x> and <y> that store the location in the window of the
        mouse (or finger)."""
        
        if self._state == STATE_INACTIVE:
            self._state = STATE_PAUSED
            self.view.remove(self.STARTUP) #Get rid of the starting screen
            self._brickrows(BRICK_COLORS, BRICK_ROWS, BRICKS_IN_ROW) #Add bricks
            self.view.add(self._paddle) #Add the paddle
            
        #elif self._state == STATE_COMPLETE: #This is a tried attempt at restarting
        #    self.view.remove(self._youlose) #the game, but ran out of time to debug 
        #    self.view.remove(self._congrats)#it. 
        #    self._bricks = []
        #    self.initialize()

    def on_touch_move(self,view,touch):
        """Respond to the mouse (or finger) being moved.

        If state is STATE_ACTIVE, then this method should move the paddle. For 
        all other states, this method is ignored.

        Precondition: <view> is just the view attribute (unused because we have
        access to the view attribute).  <touch> is a MotionEvent, which has
        attributes <x> and <y> that store the location in the window of the
        mouse (or finger)."""
        
        if self._state == STATE_ACTIVE or self._state == STATE_PAUSED:
            self.view.remove(self._paddle) #Remove the paddle where it is
            if touch.x > (GAME_WIDTH - (PADDLE_WIDTH/2)): #Change the paddle's coord
                self._paddle.center_x = (GAME_WIDTH - (PADDLE_WIDTH/2))
            elif touch.x < (PADDLE_WIDTH/2):
                self._paddle.center_x = (PADDLE_WIDTH/2)
            else:
                self._paddle.center_x = touch.x
            self.view.add(self._paddle) #Redisplay the new paddle each time the player moves

    def on_touch_up(self,view,touch):
        """Respond to the mouse (or finger) being released.

        If state is STATE_ACTIVE, then this method should stop moving the
        paddle. For all other states, it is ignored.

        Precondition: <view> is just the view attribute (unused because we have
        access to the view attribute).  <touch> is a MotionEvent, which has
        attributes <x> and <y> that store the location in the window of the
        mouse (or finger)."""
        #Started the game on Touch up so that the player doesn't have to double click
        #to start but can still have a bit of time to move the paddle before the
        #ball is served. 
        if self._state == STATE_PAUSED:
            if self._lives < NUM_LIVES and self._lives != 0: #If you still have lives left display message
                self.view.remove(self._message)
            self._ball = Ball(GAME_WIDTH/2,GAME_HEIGHT/2)
            self._state = STATE_ACTIVE #Start the game
            self.view.add(self._ball) #Serve the ball

    # ADD MORE HELPER METHODS (PROPERLY SPECIFIED) AS NECESSARY

    def _createbrick(self,position, color):
        """Creates a brick of width BRICK_WIDTH and height BRICK_HEIGHT,
        of fill- and line- color <color> and position <position>.
        Preconditions: <color> is a color constant in the RGB class
        <position> is a valid position within the GAME_WIDTH and GAME_HEIGHT"""
        
        return GRectangle(pos=position, size=(BRICK_WIDTH, BRICK_HEIGHT),fillcolor=color, linecolor=color)
    
    def _brickrows(self, colorlist, numrows, numbricks):
        """Creates the inital setup of bricks with <numbricks> per row and
        <numrows> rows. Makes every two rows the same color starting from the beginning of
        <colorlist>, and if there are more rows than twice the <colorlist> will start from
        the beginning of <colorlist>. Adds the bricks to the view as well as to _bricks.
        Preconditions: <colorlist> is a list of RGB color constants and has at least 1 element
        <numrows> and <numbricks> are both >0."""
        
        temp1 = BRICK_WIDTH + BRICK_SEP_H
        temp2 = GAME_HEIGHT - BRICK_Y_OFFSET - BRICK_HEIGHT
        k = 0
        i = 0
        counter = 0
        while i < numrows:
            j=0
            if counter == 2: #This is to run through the colors. If you have more rows than 2* the available colors
                k += 1
                counter = 0
            if k == len(colorlist): #If we have too rows many, start over the colors
                k = 0
            while j < numbricks: #Build up the bricks 
                self._bricks.append(self._createbrick((temp1*j + BRICK_X_OFFSET,
                                                       temp2 - (BRICK_HEIGHT + BRICK_SEP_V)*i),colorlist[k]))
                j += 1
            i += 1
            counter += 1
            
        for item in self._bricks:
            self.view.add(item)

    def _createpaddle(self, position):
        """Creates a paddle of width PADDLE_WIDTH and height PADDLE_HEIGHT,
        of fill- and line- color BLACK and position <position>.
        Preconditions: 
        <position> is a valid position within the GAME_WIDTH and GAME_HEIGHT"""
        temp = GRectangle(center_x=position, size=(PADDLE_WIDTH, PADDLE_HEIGHT),fillcolor=BLACK,
                          linecolor=BLACK, y=PADDLE_OFFSET)
        return temp

    def _getCollidingObject(self):
        """Returns: GObject that has collided with the ball
        
        This method checks the four corners of the ball, one at a time. If one of these points collides with
        either the paddle or a brick, it stops the checking immediately and returns the object involved in
        the collision. It returns None if no collision occurred."""
        if self._paddle.collide_point(self._ball.x,self._ball.y): #Check to see if the ball hit the paddle
            return self._paddle
        elif self._paddle.collide_point(self._ball.x + BALL_DIAMETER,self._ball.y):
            return self._paddle
        elif self._paddle.collide_point(self._ball.x + BALL_DIAMETER, self._ball.y + BALL_DIAMETER):
            return self._paddle
        elif self._paddle.collide_point(self._ball.x, self._ball.y + BALL_DIAMETER):
            return self._paddle
        else:
            for rect in self._bricks: #Check all the ball corners for each brick
                if rect.collide_point(self._ball.x,self._ball.y):
                    return rect
                elif rect.collide_point(self._ball.x + BALL_DIAMETER,self._ball.y):
                    return rect
                elif rect.collide_point(self._ball.x + BALL_DIAMETER, self._ball.y + BALL_DIAMETER):
                    return rect
                elif rect.collide_point(self._ball.x, self._ball.y + BALL_DIAMETER):
                    return rect
    
    def _testWallCollision(self):
        """Helper function for update. If the ball hits a wall, will make it bounce back,
        if it hits the paddle, will also bounce back. If the ball hits the bottom wall
        will subtract a life, pause the game and display a message for the next round."""
        
        if self._state == STATE_ACTIVE:
            self._ball.move()
            if self._ball.right >= GAME_WIDTH: #All these check to see if the ball hist the walls
                self._ball.vx *= -1
            elif self._ball.top >= GAME_HEIGHT:
                self._ball.vy *= -1
            elif self._ball.x <= 0:
                self._ball.vx *= -1
            elif self._ball.y <= 0: #If the ball hits the bottom wall, pause the game and subtract a life
                self._state = STATE_PAUSED
                self._lives -= 1
                if self._lives > 0: #Tell the player he/she has x lives left 
                    self._message = GLabel(text='You have '+ `self._lives` + ' lives left \nClick to start next round',
                                           x=STARTUP_X, y=STARTUP_Y)
                    self.view.add(self._message)
                    self.view.remove(self._ball)
                    self.view.remove(self._displayLivesNum) #Remove the current lives counter
                    self._displayLivesNum = GLabel(text=`self._lives`,x = 135, y=10) #And then update it
                    self.view.add(self._displayLivesNum)
                
            elif self._getCollidingObject() is not None:
                temp = self._getCollidingObject()
                if temp == self._paddle:
                    self._ball.y = self._paddle.y + PADDLE_HEIGHT #This is to counter the ball 'sticking'
                    self._ball.vy *= -1
                else:
                    self.view.remove(temp) #remove the collided brick from view
                    self._bricks.remove(temp) #remove the bricks from the game
                    self._ball.vy *= -1
                    
    def _testEndGame(self):
        """Helper function for update. Checks for the conditions for winning or losing the game.
        If there are no more bricks left then the player wins the game.
        If there are no more lives left then the player loses the game."""
        if self._state == STATE_ACTIVE or self._state == STATE_PAUSED:
            if len(self._bricks) == 0: #If there are no more bricks left, the player wins
                self._state = STATE_COMPLETE
                self.view.remove(self._message) #Remove message saying that you have 0 lives left
                self.view.add(self._congrats) #Add message you won
            elif self._lives == 0: #If you have no more lives left, the player loses
                self._state = STATE_COMPLETE
                self.view.add(self._youlose) #Tell them they lost
                self.view.remove(self._message) #Remove message saying you have 0 lives left


class Ball(GEllipse):
    """Instances represent the ball that will be bouncing around in Breakout.
    
    Instance variables:
        vx [float]: velocity in x direction
        vy [float]: velocity in y direction"""
        
    def __init__(self, x, y):
        """New particle at (x,y) with random initial velocity and color BLACK"""
        GEllipse.__init__(self, x=x, y=y, size=(BALL_DIAMETER,BALL_DIAMETER), color=BLACK)
        self.vx = random.uniform(1.0,INITIAL_VY)
        self.vx = self.vx * random.choice([-1,1])
        self.vy = -INITIAL_VY
    
    def move(self):
        """Helper function for Ball that will increase the x coordinate by vx, and the y coordinate by vy"""
        self.x += self.vx
        self.y += self.vy


