import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants for the game window
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Define the GREEN color

# Load sound effects
shoot_sound = pygame.mixer.Sound('shoot_sound.wav')  # Replace 'shoot_sound.wav' with your sound file
explosion_sound = pygame.mixer.Sound('explosion_sound.wav')  # Replace 'explosion_sound.wav' with your sound file
victory_sound = pygame.mixer.Sound('victory_sound.wav')  # Replace 'victory_sound.wav' with your sound file
game_over_sound = pygame.mixer.Sound('game_over_sound.wav')  # Replace 'game_over_sound.wav' with your sound file

#BGM
bgm_sound = pygame.mixer.music.load('BGM.mp3')  # Replace 'your_bgm_file.mp3' with your audio file
pygame.mixer.music.set_volume(0.1)  # Adjust the volume (0.0 to 1.0)

# Setting volume level (values range from 0.0 to 1.0)
shoot_sound.set_volume(0.3)  # Adjust the volume of the shoot sound
victory_sound.set_volume(0.2)
game_over_sound.set_volume(0.2)

# Player (user-controllable cube) variables
player_width, player_height = 25, 25
player_x, player_y = WIDTH // 2 - player_width // 2, HEIGHT // 2 - player_height // 2
player_vel = 5

# Player shooting cooldown variables
shoot_cooldown = False
cooldown_timer = 0
cooldown_duration = 1000  # 2 seconds in milliseconds

# Enemy cube variables
enemy_width, enemy_height = 50, 50
enemy_x, enemy_y = WIDTH // 2 - enemy_width // 2, HEIGHT // 2 - enemy_height // 2
last_shot_time = 0
shoot_interval = 1000  # Initial shoot interval in milliseconds
shoot_count = 1  # Initial shoot count
elapsed_time = 0  # Track elapsed time
time_offset = 10  # Time offset between projectiles in milliseconds

# Projectile variables
projectile_radius = 7
projectile_vel = 5
projectiles = []

# Constants for health
user_health = 100
enemy_health = 5000
enemy_health_constant = 5000
health_bar_width = 200
health_bar_height = 20
health_bar_outline = 2
prev_enemy_health = enemy_health

# New list to store explosion details
explosions = []

# Game variables
score = 0
font = pygame.font.Font(None, 36)  # Font for displaying text
timer = 0
clock = pygame.time.Clock()

# Function to shoot projectiles targeting the player
def shoot_projectile(target_x, target_y):
    global score
    angle = math.atan2(target_y - enemy_y, target_x - enemy_x) + random.uniform(-0.2, 0.2)
    vel_x = projectile_vel * math.cos(angle)
    vel_y = projectile_vel * math.sin(angle)
    # Change here to include the color for the projectile
    projectiles.append((enemy_x + enemy_width // 2, enemy_y + enemy_height // 2, vel_x, vel_y, BLUE))
    score += 5  # Update score when firing a projectile

def player_shoot():
    global player_x, player_y, enemy_x, enemy_y, score, shoot_cooldown, cooldown_timer, shoot_sound
    if not shoot_cooldown:
        angle = math.atan2(enemy_y - player_y, enemy_x - player_x)  # Calculate angle towards enemy
        vel_x = projectile_vel * math.cos(angle)
        vel_y = projectile_vel * math.sin(angle)
        projectiles.append((player_x + player_width // 2, player_y + player_height // 2, vel_x, vel_y, RED))
        #shoot_sound.play()
        score += 5  # Update score when firing a projectile
        shoot_cooldown = True  # Activate cooldown
        cooldown_timer = pygame.time.get_ticks()  # Start cooldown timer

def handle_explosions():
    global explosions

    # Create a new list to store active explosions
    active_explosions = []

    for explosion in explosions:
        # Unpack the explosion details
        (x, y), color, radius = explosion

        # Draw the circular outline by drawing multiple circles with decreasing radii
        for i in range(1):  # Change the range value to adjust the thickness of the outline
            pygame.draw.circle(win, color, (int(x), int(y)), radius + i, 1)  # Setting the width parameter to 1 draws the outline

        # Decrease the radius to create the animation effect
        radius += 1

        # Add the updated explosion back to active explosions
        if radius < 40:
            active_explosions.append([(x, y), color, radius])

    # Update the explosions list with active explosions
    explosions = active_explosions[:]

def draw_health_bar(x, y, health):
    # Draw the outline of the health bar
    pygame.draw.rect(win, WHITE, (x-2, y-2, health_bar_width+4, health_bar_height+4), health_bar_outline)
    
    # Calculate the width of the health bar based on current health
    health_width = health_bar_width * (health / 100)
    health_rect = pygame.Rect(x, y, health_width, health_bar_height)
    
    # Draw the filled portion of the health bar
    pygame.draw.rect(win, RED, health_rect)

def handle_health():
    global user_health, enemy_health, explosions
    
    # Loop through the explosions
    for explosion in explosions:
        (x, y), _, _ = explosion
        
        # Check for collisions with the user and enemy
        if (player_x < x < player_x + player_width) and (player_y < y < player_y + player_height):
            user_health -= 1  # Deduct health if user is hit by an explosion
        if (enemy_x < x < enemy_x + enemy_width) and (enemy_y < y < enemy_y + enemy_height):
            enemy_health -= 1  # Deduct health if enemy is hit by an explosion

# Add this function to handle the game over screen
def game_over_screen():
    global running
    pygame.mixer.music.stop()
    while True:
        game_over_sound.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()  # Quit the game entirely

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                button_x, button_y, button_width, button_height = 300, 400, 200, 50
                if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    reset_game()  # Reset variables, health, etc., for a new game
                    game_over_sound.stop()
                    pygame.mixer.music.play(-1)
                    return

        win.fill(BLACK)  # Clear the screen
        font_large = pygame.font.Font(None, 72)
        text = font_large.render("You Lost", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(text, text_rect)

        # Draw retry button
        pygame.draw.rect(win, RED, (300, 400, 200, 50))
        font_small = pygame.font.Font(None, 36)
        button_text = font_small.render("Retry", True, WHITE)
        button_text_rect = button_text.get_rect(center=(400, 425))
        win.blit(button_text, button_text_rect)

        pygame.display.update()
        clock.tick(60)

def reset_game():
    global user_health, enemy_health, player_x, player_y, enemy_x, enemy_y, score, elapsed_time, shoot_count, timer, last_shot_time, shoot_interval
    user_health = 100
    enemy_health = 5000
    score = 0
    elapsed_time = 0
    shoot_count = 1
    timer = 0
    last_shot_time = 0
    shoot_interval = 1000
    # Calculate positions for furthest distance
    if player_x < WIDTH // 2:
        player_x, player_y = 0, 0  # Top-left corner
    else:
        player_x, player_y = WIDTH - player_width, HEIGHT - player_height  # Bottom-right corner

    # Set the enemy position at the opposite corner
    enemy_x, enemy_y = WIDTH - enemy_width - player_x, HEIGHT - enemy_height - player_y
    # Reset any other variables here

# Define a function for the victory screen
def victory_screen():
    global running
    pygame.mixer.music.stop()
    while True:
        victory_sound.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()  # Quit the game entirely

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                button_x, button_y, button_width, button_height = 300, 400, 200, 50
                if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    reset_game()  # Reset variables, health, etc., for a new game
                    victory_sound.stop()
                    pygame.mixer.music.play(-1)
                    return  # Exit the victory screen loop and restart the game loop

        win.fill(BLACK)  # Clear the screen
        font_large = pygame.font.Font(None, 72)
        text = font_large.render("You Win", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(text, text_rect)

        # Draw restart button
        pygame.draw.rect(win, GREEN, (300, 400, 200, 50))
        font_small = pygame.font.Font(None, 36)
        button_text = font_small.render("Restart", True, WHITE)
        button_text_rect = button_text.get_rect(center=(400, 425))
        win.blit(button_text, button_text_rect)

        pygame.display.update()
        clock.tick(60)

# Critical Hit Flag
show_critical_hit = False
critical_hit_counter = 0
critical_hit_duration = 0

# Teleportation cooldown variable
teleport_cooldown = False
teleport_duration = 5000  # Adjust the teleportation cooldown duration in milliseconds

# Calculate positions for furthest distance
# Let's place them at opposite corners (top-left and bottom-right) for demonstration purposes
if player_x < WIDTH // 2:
    player_x, player_y = 0, 0  # Top-left corner
else:
    player_x, player_y = WIDTH - player_width, HEIGHT - player_height  # Bottom-right corner

# Set the enemy position at the opposite corner
enemy_x, enemy_y = WIDTH - enemy_width - player_x, HEIGHT - enemy_height - player_y


# Game loop
show_instructions = True
hide_instructions_timer = None
key_pressed = False 
running = True
show_critical_hit = False  # Flag to trigger critical hit display
critical_hit_counter = 0  # Counter to control the number of critical hit flashes
pygame.mixer.music.play(-1)
while running:
    win.fill(BLACK)  # Fill the screen with black color
    if show_instructions:
        font_instructions = pygame.font.Font(None, 30)
        instructions_text = font_instructions.render("Use arrow keys to move and left shift to shoot", True, WHITE)
        instructions_rect = instructions_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(instructions_text, instructions_rect)
        
        # Check for the start of the game (e.g., any key press)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and not key_pressed:
                            key_pressed = True  # Set key_pressed flag to True
                            hide_instructions_timer = time.time() + 2
    
    if hide_instructions_timer and time.time() > hide_instructions_timer:
        show_instructions = False  # Hide instructions after the timer expires

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for left shift press to shoot projectile
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                player_shoot()

    # Handle player shooting cooldown
    if shoot_cooldown:
        current_time = pygame.time.get_ticks()
        if current_time - cooldown_timer >= cooldown_duration:
            shoot_cooldown = False  # Reset cooldown status
    
    # Draw Player health bar
    draw_health_bar(50, 50, user_health)

    # Reset game variables, health, etc. for a new game
    if user_health <= 0:
        game_over_screen()  # Display game over screen if user health drops to 0
        reset_game()
    
    # Draw Enemy Health Bar
    enemy_health_percentage = (enemy_health / enemy_health_constant) * 100 
    enemy_health_width = (enemy_health_percentage / 100) * (WIDTH-200)
    enemy_health_x = (WIDTH - (WIDTH-200)) // 2  # Place the health bar at the bottom center
    enemy_health_y = HEIGHT - 40  # Adjust the height of the health bar from the bottom
    pygame.draw.rect(win, BLUE, (enemy_health_x, enemy_health_y, enemy_health_width, 20))
    pygame.draw.rect(win, WHITE, (enemy_health_x-2, enemy_health_y-2, WIDTH-198, health_bar_height+4), health_bar_outline)

    # Inside the game loop, after updating enemy's health
    if enemy_health <= 0:
        victory_screen()  # Display victory screen if enemy health drops to 0

    # Previous health for hit detection
    prev_enemy_health = enemy_health

    # Handle health deduction from explosions
    for explosion in explosions:
        (x, y), _, _ = explosion
        # Check for collisions with the user and enemy
        if (player_x < x < player_x + player_width) and (player_y < y < player_y + player_height):
            user_health -= 1  # Deduct health if user is hit by an explosion
        if (enemy_x < x < enemy_x + enemy_width) and (enemy_y < y < enemy_y + enemy_height):
            enemy_health -= 1  # Deduct health if enemy is hit by an explosion

    # Teleportation when enemy health drops below 25%
    if enemy_health_percentage < 40:
        if not teleport_cooldown:
            enemy_x = random.randint(0, WIDTH - enemy_width)
            enemy_y = random.randint(0, HEIGHT - enemy_height)
            teleport_cooldown = True  # Start the cooldown timer
            last_teleport_time = pygame.time.get_ticks()  # Record the teleportation time

    # Check teleportation cooldown
    if teleport_cooldown:
        current_time = pygame.time.get_ticks()
        if current_time - last_teleport_time >= teleport_duration:
            teleport_cooldown = False  # Reset the cooldown status


    # Calculate damage dealt
    damage_dealt = prev_enemy_health - enemy_health

    # Check if the damage dealt exceeds 200 for a critical hit
    if damage_dealt >= 10:
        if not show_critical_hit:
            show_critical_hit = True
            critical_hit_duration = pygame.time.get_ticks()  # Set the critical hit start time

    # Display Critical Hit text if triggered
    if show_critical_hit:
        current_time = pygame.time.get_ticks()
        if current_time - critical_hit_duration <= 1000:  # Display for 1 second (1000 milliseconds)
            if current_time % 500 < 250:  # Control the text flashing speed
                critical_text = font.render("Critical Hit", True, WHITE)
                text_width, text_height = font.size("Critical Hit")
                win.blit(critical_text, ((WIDTH - text_width) // 2, HEIGHT // 2 - text_height // 2))
            shoot_sound.play()
        else:
            # Stop displaying after 1 second (adjust duration accordingly)
            show_critical_hit = False
            critical_hit_counter += 1
            if critical_hit_counter >= 3:  # Stop after three flashes
                critical_hit_counter = 0

    # Draw cooldown indicator
    if not shoot_cooldown:
        pygame.draw.circle(win, RED, (20, 20), 10)  # Display red circle at top left during cooldown

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_vel
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_vel
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_vel
    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_height:
        player_y += player_vel

    # Enemy shooting projectiles towards the player at intervals
    current_time = pygame.time.get_ticks()
    elapsed_time += clock.get_time()  # Track elapsed time
    if elapsed_time >= 10000:  # Check if 20 seconds have passed
        elapsed_time -= 10000  # Reset elapsed time
        if shoot_count < 7:  # Limit shoot_count to a maximum of 10
            shoot_count += 1  # Increment shoot count
            shoot_interval -= 100  # Decrease shoot interval after 20 seconds

    if current_time - last_shot_time > shoot_interval:
        shoot_projectile(player_x, player_y)
        last_shot_time = current_time

    # Update and draw projectiles
    active_projectiles = []
    for projectile in projectiles:
        x, y, vel_x, vel_y, color = projectile  # Unpack the values, including color
        x += vel_x
        y += vel_y
        pygame.draw.circle(win, color, (int(x), int(y)), projectile_radius)
        
        # Check collision with the player for enemy-fired projectiles only
        if color == BLUE:  # Enemy-fired projectile
            if (player_x < x < player_x + player_width) and (player_y < y < player_y + player_height):
                explosions.append([(x, y), color, 10])  # Add explosion at projectile coordinates
                # Implement actions for a hit on the player by enemy-fired projectiles
                # ...

        # Check collision with the enemy for user-fired projectiles
        if color == RED:  # User-fired projectile
            if (enemy_x < x < enemy_x + enemy_width) and (enemy_y < y < enemy_y + enemy_height):
                explosions.append([(x, y), color, 10])  # Add explosion at projectile coordinates
                # Implement actions for a hit on the enemy by user-fired projectiles
                # ...

        # Check if projectile is on screen
        if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
            active_projectiles.append((x, y, vel_x, vel_y, color))

    # Replace the projectiles list with the updated active_projectiles list
    projectiles = active_projectiles[:]

    # Draw explosions
    handle_explosions()

    # Draw the player cube
    pygame.draw.rect(win, RED, (player_x, player_y, player_width, player_height))

    # Enemy Movement
    if random.randint(1, 100) == 1:  # Change the number and condition as needed for frequency
        directions = [(-2, -2), (0, -2), (2, -2), (-2, 0), (2, 0), (-2, 2), (0, 2), (2, 2)]  # Extreme movements
        random_direction = random.choice(directions)
        enemy_x += random_direction[0] * player_vel
        enemy_y += random_direction[1] * player_vel
    else:
        # Normal movement
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]  # Eight directions
        random_direction = random.choice(directions)
        enemy_x += random_direction[0] * player_vel
        enemy_y += random_direction[1] * player_vel

    # Ensure the enemy cube stays within the window bounds
    enemy_x = max(0, min(enemy_x, WIDTH - enemy_width))
    enemy_y = max(0, min(enemy_y, HEIGHT - enemy_height))

    # Draw the enemy cube
    pygame.draw.rect(win, BLUE, (enemy_x, enemy_y, enemy_width, enemy_height))

    # Draw timer and score in top right corner
    timer += clock.get_time()
    timer_text = font.render(f"Timer: {int(timer / 1000)}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    win.blit(timer_text, (WIDTH - 150, 10))
    win.blit(score_text, (WIDTH - 150, 40))

    pygame.display.update()  # Update the display
    clock.tick(60)  # Control the frame rate

pygame.quit()  # Quit Pygame