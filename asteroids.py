import pygame as pg
import math
import sys
import random
import time

pg.init() #initializes all pygame modules required

clock = pg.time.Clock()

#CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (0, 0, 0) #black in rgb
SHIP_COLOR = (255, 255, 255) #white in rgb
BULLET_COLOR = (255, 0, 0)
ASTEROID_COLOR = (0, 0, 0)   #(101, 67, 33) = brown
SHIP_SIZE = 10
BULLET_SIZE = 4
ASTEROID_SIZE = 80
SHIP_SPEED = 2
BULLET_SPEED = 10
ASTEROID_SPEED = 2
MAX_ASTEROIDS = 5
SPAWN_RATE = 0.5 #asteroid spawn rate in seconds
MAX_LIVES = 3

#create the screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT,))
pg.display.set_caption("Asteroids Game")

#load background image
background_image = pg.image.load("nebula.jpeg").convert()

"""
#load asteroid image
asteroid_image = pg.image.load("moon.png").convert()
asteroid_image = pg.transform.scale(asteroid_image, (ASTEROID_SIZE, ASTEROID_SIZE))

#create circular mask to crop asteroid image into a circle
mask = pg.Surface((ASTEROID_SIZE, ASTEROID_SIZE), pg.SRCALPHA)
pg.draw.circle(mask, (255, 255, 255), (ASTEROID_SIZE // 2, ASTEROID_SIZE // 2), ASTEROID_SIZE // 2)

#apply the mask
asteroid_image = pg.transform.scale(asteroid_image, (ASTEROID_SIZE, ASTEROID_SIZE))
asteroid_image.blit(mask, (0,0), special_flags=pg.BLEND_RGB_MIN)
"""

#ship variables
ship_x = SCREEN_WIDTH // 2 #floor division
ship_y = SCREEN_HEIGHT
ship_angle = 0
ship_exploded = False
lives = MAX_LIVES #number of lives

#bullets list
bullets = []

#asteroids list
asteroids = []

#explosion animation variables
explosion_radius = 10
explosion_max_radius = 50
#asteroid_explosion_radius = 1000
#asteroid_explosion_max_radius = 2000
explosion_duration = 500 #milliseconds
explosion_start_time = 5
explosion_sound = pg.mixer.Sound("explosion_sound.wav")

#game over screen variables
game_over = False
game_over_font = pg.font.Font(None, 36)
game_over_text = game_over_font.render("Game Over | Press 'R' to Restart", True, (255, 255, 255))

#bullet firing control variables
last_bullet_fired_time = 0
bullet_fire_delay = 300

#bullet firing sound
laser_sound = pg.mixer.Sound("laser_sound.mp3")

#points variable
points = 0

#create a font for displaying points
points_font = pg.font.Font(None, 36)

#function to check for collisions between ship and asteroids
def check_ship_asteroid_collision(ship_x, ship_y, asteroids, lives):
    asteroids_to_remove = [] #stores the indices of asteroids that collide with the ship

    for asteroid in asteroids:
        asteroid_x, asteroid_y, _, _ = asteroid #unpacks the 'asteroid' tuple to extract its 'x' and 'y' coordinates
                                             #the '_' is used to discard the third element of the tuple, which represents the angle which is not needed for collision detection
        distance = math.sqrt((ship_x - asteroid_x) ** 2 + (ship_y - asteroid_y) ** 2)
        if distance < ASTEROID_SIZE: #ship collides with asteroid 
            #add asteroid to list of asteroids to remove
            asteroids_to_remove.append(asteroid)
            lives -= 1 #getting hit = No No

    #remove asteroids from main list
    for asteroid in asteroids_to_remove:
        asteroids.remove(asteroid)

    #return true if any asteroids were removed
    return len(asteroids_to_remove) > 0


#spawns an asteroid at a random location along one of the four edges of the screen and calculates an angle for its trajectory based on the position of the center of the screen and a random offset
def spawn_asteroid():
    center_x = SCREEN_WIDTH // 2 #integer division; ensures that the end result is an integer
    center_y = SCREEN_HEIGHT // 2

    #randomly selects one of the four edges
    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        x = random.randint(0, SCREEN_WIDTH)
        y = 0
        offset = random.randint(-x*2, x*2)
        angle = math.atan2(-center_y, center_x + offset)
    elif edge == "bottom":
        x = random.randint(0, SCREEN_WIDTH)
        y = SCREEN_HEIGHT
        offset = random.randint(-x*2, x*2)
        angle = math.atan2(center_y, center_x + offset)
    elif edge == "left":
        x = 0
        y = random.randint(0, SCREEN_HEIGHT)
        offset = random.randint(-y*2, y)
        angle = math.atan2(center_y, center_x + offset)
    elif edge == "right":
        x = SCREEN_WIDTH
        y = random.randint(0, SCREEN_HEIGHT)
        offset = random.randint(-y, y*2)
        angle = math.atan2(center_y, -center_x + offset)

    speed = ASTEROID_SPEED
    asteroids.append((x, y ,angle, speed)) #after determining the coordinates and angle, a new asteroid is created as a tuple '(x, y, angle)' and appended to the 'asteroids' list


#function to check collisions between bullets and asteroids
def check_bullet_asteroid_collision(bullets, asteroids):
    global points
    bullets_to_remove = []

    for bullet in bullets:
        bullet_x, bullet_y, _ = bullet

        #creates a list of asteroids to remove (those hit by the bullet)
        asteroids_to_remove = [asteroid for asteroid in asteroids if math.sqrt((bullet_x - asteroid[0])**2 + (bullet_y - asteroid[1])**2) < (BULLET_SIZE + ASTEROID_SIZE)]
            #'asteroid for asteroid in asteroids...' is a list comprehension that interates through each asteroid in the 'asteroids' list and inclues only those that satisfy a certain condition
            #'math.sqrt((bullet_x - asteroid[0])**2 + (bullet_y - asteroid[1])**2) < (BULLET_SIZE + ASTEROID_SIZE)' is the condition that calculates the distance between the position of the bullet and each asteroid.
                #if this distance is less than the sum of the bullet radius 'BULLET_SIZE' and asteroid radius 'ASTEROID_SIZE', this means that the bullet has hit the asteroid

        for asteroid in asteroids_to_remove: #for every asteroid in the list of asteroids that have been hit by a bullet:
            asteroids.remove(asteroid) #removes the specified asteroid from the asteroid list
            points += 10
            #pg.draw.circle(screen, (255,0,0), (int(ship_x), int(ship_y)), int(asteroid_explosion_radius))

        if asteroids_to_remove:
            bullets_to_remove.append(bullet)

    #remove marked bullets
    for bullet in bullets_to_remove:
        bullets.remove(bullet)
    
#function to draw the explosion animation
def draw_explosion(ship_x, ship_y, explosion_radius):
    pg.draw.circle(screen, (255,0,0), (int(ship_x), int(ship_y)), int(explosion_radius))


#function for the explosion animation
def explosion_animation():
    current_time = pg.time.get_ticks()
    if (current_time - explosion_start_time <= explosion_duration):
        explosion_radius = ((current_time - explosion_start_time) * explosion_max_radius/explosion_duration)
        draw_explosion(ship_x, ship_y, explosion_radius)
    else:
        explosion_sound.play()
        return True
    return False

#function to reset the game
def reset_game():
    global ship_x, ship_y, ship_angle, ship_exploded
    global lives, game_over, bullets, asteroids, points

    ship_x = SCREEN_WIDTH // 2
    ship_y = SCREEN_HEIGHT // 2
    ship_angle = 0
    ship_exploded = False
    lives = MAX_LIVES
    game_over = False
    bullets = []
    asteroids = []
    points = 0

#game loop
running = True
last_spawn_time = 0

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    keys = pg.key.get_pressed()

    current_time = pg.time.get_ticks()

    if not ship_exploded and not game_over:
        #rotate the ship
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            ship_angle += 0.05
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            ship_angle -= 0.05
        
        #move the ship
        if keys[pg.K_UP] or keys[pg.K_w]:
            ship_x += SHIP_SPEED * math.cos(ship_angle)
            ship_y -= SHIP_SPEED * math.sin(ship_angle)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            ship_x -= SHIP_SPEED * math.cos(ship_angle)
            ship_y += SHIP_SPEED * math.sin(ship_angle)

            """
            #wrap the ship around the window boundaries
            if ship_x < 0:
                ship_x = SCREEN_WIDTH
            elif ship_x > SCREEN_WIDTH:
                ship_x = 0
            if ship_y < 0:
                ship_y = SCREEN_HEIGHT
            elif ship_y > SCREEN_HEIGHT:
                ship_y = 0
            """
        
        #check for ship-asteroid collision
        if check_ship_asteroid_collision(ship_x, ship_y, asteroids,lives):
            ship_exploded = True
            explosion_start_time = current_time
            lives -= 1
            if lives <= 0:
                game_over = True

        #check for bullet-asteroid collision
        check_bullet_asteroid_collision(bullets, asteroids)

        #creates a bullet everytime spacebar is pressed
        if (keys[pg.K_SPACE] or keys[pg.K_RETURN]) and current_time - last_bullet_fired_time >= bullet_fire_delay:
            bullet_x = ship_x + (SHIP_SIZE + BULLET_SIZE) * math.cos(ship_angle)
            bullet_y = ship_y - (SHIP_SIZE + BULLET_SIZE) * math.sin(ship_angle)
            bullets.append((bullet_x, bullet_y, ship_angle))
            last_bullet_fired_time = current_time

            #plays a laser sound for every bullet/laser shot
            laser_sound.play()
    
    screen.blit(background_image, (0,0))

    #clean screen
    #screen.fill(BACKGROUND_COLOR)

    #update and draw bullets
    new_bullets = []
    for bullet in bullets:
        bullet_x, bullet_y, bullet_angle = bullet
        bullet_x += BULLET_SPEED * math.cos(bullet_angle)
        bullet_y -= BULLET_SPEED * math.sin(bullet_angle)
        if (0 <= bullet_x < SCREEN_WIDTH and 0<= bullet_y < SCREEN_HEIGHT):
            new_bullets.append((bullet_x, bullet_y, bullet_angle))
            pg.draw.circle(screen, BULLET_COLOR, (int(bullet_x), int(bullet_y)), int(BULLET_SIZE))
    bullets = new_bullets

    #spawn new asteroids
    current_time = pg.time.get_ticks()
    if current_time - last_spawn_time > SPAWN_RATE:
        if len(asteroids) < MAX_ASTEROIDS:
            spawn_asteroid()
        last_spawn_time = current_time

    #update and draw asteroids
    new_asteroids = []
    for asteroid in asteroids:
        asteroid_x, asteroid_y, asteroid_angle, asteroid_speed = asteroid
        asteroid_x += asteroid_speed * math.cos(asteroid_angle)
        asteroid_y += asteroid_speed * math.sin(asteroid_angle)

        if asteroid_x < -ASTEROID_SIZE:
            asteroid_x = SCREEN_WIDTH + ASTEROID_SIZE
        elif asteroid_x > SCREEN_WIDTH + ASTEROID_SIZE:
            asteroid_x = -ASTEROID_SIZE
        if asteroid_y < -ASTEROID_SIZE:
            asteroid_y = SCREEN_HEIGHT + ASTEROID_SIZE
        elif asteroid_y > SCREEN_HEIGHT + ASTEROID_SIZE:
            asteroid_y = -ASTEROID_SIZE

        new_asteroids.append((asteroid_x, asteroid_y, asteroid_angle, asteroid_speed))
        pg.draw.circle(screen, ASTEROID_COLOR, (int(asteroid_x), int(asteroid_y)), ASTEROID_SIZE)
        #screen.blit(asteroid_image, (int(asteroid_x) - ASTEROID_SIZE // 2, int(asteroid_y) - ASTEROID_SIZE // 2))

    asteroids = new_asteroids

    #draw ship 
    if not ship_exploded:
        ship_verticies = [
            #tip
            (ship_x + SHIP_SIZE * math.cos(ship_angle),
            ship_y - SHIP_SIZE * math.sin(ship_angle)),

            #rear left
            (ship_x + SHIP_SIZE * math.cos(ship_angle + 2.5),
            ship_y - SHIP_SIZE * math.sin(ship_angle + 2.5)),

            #rear center (the notch)
            (ship_x, ship_y), 

            #rear right
            (ship_x + SHIP_SIZE * math.cos(ship_angle - 2.5),
            ship_y - SHIP_SIZE * math.sin(ship_angle - 2.5))
        ]
        pg.draw.polygon(screen, SHIP_COLOR, ship_verticies)

        
        #ship wrapping logic in the x-direction
        if ship_x < 0:
            ship_x = SCREEN_WIDTH
        if ship_x > SCREEN_WIDTH:
            ship_x = 0

        #ship wrapping logic in the y-direction
        if ship_y < 0:
            ship_y = SCREEN_HEIGHT
        if ship_y > SCREEN_HEIGHT:
            ship_y = 0 
        

    #draw explosion if ship exploded
    if ship_exploded:
        if explosion_animation():
            ship_exploded = False

    #draw remaining lives
    lives_font = pg.font.Font(None, 36)
    lives_text = lives_font.render(f"Lives: {lives}", True, (255,255,255))
    screen.blit(lives_text, (10,10))

    #draw points
    points_text = points_font.render(f"Points: {points}", True, (255,255,255))
    screen.blit(points_text, (SCREEN_WIDTH - 150, 10))

    #draw game over
    if game_over:
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))

    pg.display.update()

    #check for game restart
    if game_over and keys[pg.K_r]:
        reset_game()

    clock.tick_busy_loop(60)

pg.quit()
sys.exit()