import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1000, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load images
RED_SPACE_SHIP = pygame.image.load("assets/pixel_ship_red_small.png")
GREEN_SPACE_SHIP = pygame.image.load("assets/pixel_ship_green_small.png")
BLUE_SPACE_SHIP = pygame.image.load("assets/pixel_ship_blue_small.png")

# Player Ship
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load("assets/pixel_ship_main.png"), (100, 100))

# Lasers
RED_LASER = pygame.image.load("assets/pixel_laser_red.png")
GREEN_LASER = pygame.image.load("assets/pixel_laser_green.png")
BLUE_LASER = pygame.image.load("assets/pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("assets/pixel_laser_yellow.png")

# Background
BG = pygame.transform.scale(pygame.image.load("assets/background-cyber.jpeg"), (WIDTH, HEIGHT))
#use tranform.scale to change image so that it fits into the entire screen

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj) 

class Ship: #abstract class - they will be inherited from here -- i can make multiple players with these attributes
    COOLDOWN = 30

    def __init__(self, x, y, health = 100): #lets class initalize object's attributes
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None #images will be defined later
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0 #how fast lasers can be shot

    def draw(self, window):
        window.blit(self.player_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0: 
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.player_img.get_width()

    def get_height(self):
        return self.player_img.get_height()



class Player(Ship): #Inheriting draw method from Ship Class
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health) 
        self.player_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.player_img) #pygame specific PIXEL SPECIFIC COLLISION
        self.max_health = health

        #WILL OVERRIDE PARENT CLASS
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                        self.lasers.remove(laser)

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.player_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.player_img)

    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
    #if masks are overlapping than return true, 
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5 # everytime a key is pressed you will move 5 pixels
    laser_vel = 4

    player = Player(500, 650)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    
    def redraw_window():
        #WIN takes a surface and draws it to location defined
        WIN.blit(BG, (0,0)) #x goes right and y goes down so 0,0 is top left
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) #f strings - allows to embbed variables inside of curly brackets (Python Specific)
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) # To make the levels show up on the right side & keep everything scaled
        
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        # lost defined in line 92
        if lost:
            lost_label = lost_font.render("You Lost", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) #Width/2 will be centered 
        
        pygame.display.update()

    #Checks for events once every (FPS(60)(60 times every second))
    while run:
        clock.tick(FPS)
        redraw_window()
        
        #If lives = 0 game is done
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        #When game is lost it will stop
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        #enemies spawning in
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"])) #random enemies spawn location and color
                enemies.append(enemy)

        #Everytime this loop is ran and check if window was closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #Controls 
        keys = pygame.key.get_pressed() #dictionary of keys
        if keys[pygame.K_a] and player.x - player_vel > 0: #left & - player_vel so it doesn't move off screen
            player.x -= player_vel #moving 1 pixel to the left everytime a is pressed
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel # subtracting from y axis because moving up
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()  

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            # LIVES WILL BE LOST WHEN ENEMIES LEAVE SCREEN
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1 
                enemies.remove(enemy)


    player.move_lasers(laser_vel, enemies)

main()

