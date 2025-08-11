"""
Classic Pong Game
CSE325 - .NET Software Development
A simple two-player Pong game using Python Arcade

Requirements Met:
- Graphics display ✓
- Keyboard input ✓
- Moveable objects ✓
- Sound effects ✓

Controls:
Player 1 (Left): W/S keys
Player 2 (Right): UP/DOWN arrow keys
ESC: Quit game
R: Reset game
"""

import arcade
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Classic Pong Game"

# Paddle constants
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_SPEED = 5
PADDLE_MARGIN = 20

# Ball constants
BALL_SIZE = 10
BALL_SPEED = 3

# Colors
WHITE = arcade.color.WHITE
BLACK = arcade.color.BLACK
BLUE = arcade.color.BLUE
RED = arcade.color.RED


class Ball(arcade.Sprite):
    """Ball sprite with physics"""
    
    def __init__(self):
        super().__init__()
        
        # Create a simple white square for the ball using make_soft_square_texture
        texture = arcade.make_soft_square_texture(BALL_SIZE, WHITE)
        self.texture = texture
        
        # Set initial position and velocity
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.change_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.change_y = random.choice([-BALL_SPEED, BALL_SPEED])
    
    def update(self, delta_time=1/60):
        """Update ball position and handle wall bouncing"""
        self.center_x += self.change_x
        self.center_y += self.change_y
        
        # Bounce off top and bottom walls
        if self.top >= SCREEN_HEIGHT or self.bottom <= 0:
            self.change_y *= -1


class Paddle(arcade.Sprite):
    """Paddle sprite"""
    
    def __init__(self, color=WHITE):
        super().__init__()
        
        # Create paddle texture using make_soft_square_texture
        texture = arcade.make_soft_square_texture(PADDLE_WIDTH, color, outer_alpha=255)
        self.texture = texture
        
        # Scale the texture to get the right height
        self.scale = PADDLE_HEIGHT / PADDLE_WIDTH
        
        self.change_y = 0
    
    def update(self, delta_time=1/60):
        """Update paddle position with boundary checking"""
        self.center_y += self.change_y
        
        # Keep paddle on screen
        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT
        elif self.bottom < 0:
            self.bottom = 0


class PongGame(arcade.Window):
    """Main game class"""
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BLACK)
        
        # Sprite lists
        self.player_list = None
        self.ball_list = None
        
        # Game objects
        self.player1 = None
        self.player2 = None
        self.ball = None
        
        # Game state
        self.player1_score = 0
        self.player2_score = 0
        
        # Sound effects (we'll create simple beep sounds programmatically)
        self.hit_sound = None
        self.score_sound = None
        
        # Key tracking
        self.keys_pressed = set()
    
    def setup(self):
        """Set up the game"""
        
        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.ball_list = arcade.SpriteList()
        
        # Create paddles
        self.player1 = Paddle(BLUE)
        self.player1.center_x = PADDLE_MARGIN
        self.player1.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player1)
        
        self.player2 = Paddle(RED)
        self.player2.center_x = SCREEN_WIDTH - PADDLE_MARGIN
        self.player2.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player2)
        
        # Create ball
        self.ball = Ball()
        self.ball_list.append(self.ball)
        
        # Create simple beep sounds
        try:
            # These will create simple tone sounds if available
            self.hit_sound = arcade.load_sound(":resources:sounds/hit1.wav")
            self.score_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        except:
            # If sounds don't load, we'll handle it gracefully
            print("Sound files not found - game will run without audio")
            self.hit_sound = None
            self.score_sound = None
    
    def on_draw(self):
        """Render the screen"""
        self.clear()
        
        # Draw all sprites
        self.player_list.draw()
        self.ball_list.draw()
        
        # Draw center line
        arcade.draw_line(SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT, WHITE, 2)
        
        # Draw scores
        arcade.draw_text(f"Player 1: {self.player1_score}", 50, SCREEN_HEIGHT - 50,
                        WHITE, 20)
        arcade.draw_text(f"Player 2: {self.player2_score}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50,
                        WHITE, 20)
        
        # Draw controls
        arcade.draw_text("Player 1: W/S keys", 50, 50, WHITE, 16)
        arcade.draw_text("Player 2: UP/DOWN arrows", SCREEN_WIDTH - 250, 50, WHITE, 16)
        arcade.draw_text("ESC: Quit | R: Reset", SCREEN_WIDTH // 2 - 80, 20, WHITE, 16)
    
    def on_update(self, delta_time):
        """Update game logic"""
        
        # Handle continuous key presses
        if arcade.key.W in self.keys_pressed:
            self.player1.change_y = PADDLE_SPEED
        elif arcade.key.S in self.keys_pressed:
            self.player1.change_y = -PADDLE_SPEED
        else:
            self.player1.change_y = 0
            
        if arcade.key.UP in self.keys_pressed:
            self.player2.change_y = PADDLE_SPEED
        elif arcade.key.DOWN in self.keys_pressed:
            self.player2.change_y = -PADDLE_SPEED
        else:
            self.player2.change_y = 0
        
        # Update all sprites
        self.player_list.update()
        self.ball_list.update()
        
        # Check for paddle collisions
        hit_list = arcade.check_for_collision_with_list(self.ball, self.player_list)
        if hit_list:
            self.ball.change_x *= -1
            # Add slight angle variation based on where ball hits paddle
            paddle = hit_list[0]
            hit_pos = (self.ball.center_y - paddle.center_y) / (PADDLE_HEIGHT / 2)
            self.ball.change_y += hit_pos * 2
            
            # Play hit sound
            if self.hit_sound:
                arcade.play_sound(self.hit_sound)
        
        # Check for scoring
        if self.ball.center_x < 0:
            self.player2_score += 1
            self.reset_ball()
            if self.score_sound:
                arcade.play_sound(self.score_sound)
        elif self.ball.center_x > SCREEN_WIDTH:
            self.player1_score += 1
            self.reset_ball()
            if self.score_sound:
                arcade.play_sound(self.score_sound)
    
    def reset_ball(self):
        """Reset ball to center with random direction"""
        self.ball.center_x = SCREEN_WIDTH // 2
        self.ball.center_y = SCREEN_HEIGHT // 2
        self.ball.change_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.ball.change_y = random.choice([-BALL_SPEED, BALL_SPEED])
    
    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        self.keys_pressed.add(key)
        
        # Handle special keys
        if key == arcade.key.ESCAPE:
            self.close()
        elif key == arcade.key.R:
            self.reset_game()
    
    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def reset_game(self):
        """Reset the entire game"""
        self.player1_score = 0
        self.player2_score = 0
        self.reset_ball()
        
        # Reset paddle positions
        self.player1.center_y = SCREEN_HEIGHT // 2
        self.player2.center_y = SCREEN_HEIGHT // 2


def main():
    """Main function"""
    game = PongGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()