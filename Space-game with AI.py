import math
import random
import pygame
from pygame import mixer
import time

# Initialize pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.png')

# Sound
mixer.music.load("background.wav")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Load enemy image
enemy_image = pygame.image.load('enemy.png')

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 8  # Increased speed of movement
player_moving = True  # Flag to control movement

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(4)
    enemyY_change.append(40)

# Bullet
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
testY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)

# AI Parameters
last_shoot_time = time.time()
shoot_interval = 0.1  # Very short time between automatic shots


# Start Screen
def start_screen():
    screen.fill((0, 0, 0))  # Clear screen with black color

    # Display the enemy image
    screen.blit(enemy_image, (350, 250))

    # Display the game name
    title_font = pygame.font.Font('freesansbold.ttf', 64)
    title_text = title_font.render("Space Invader", True, (255, 255, 255))
    screen.blit(title_text, (150, 150))

    # Draw the loading bar
    loading_bar_width = 300
    loading_bar_height = 50
    bar_x = (800 - loading_bar_width) // 2
    bar_y = (600 - loading_bar_height) // 2 + 100
    progress = 0
    increment = loading_bar_width / 20  # Increment by width / number of steps
    end_time = time.time() + 2  # 2 seconds duration

    while time.time() < end_time:
        screen.fill((0, 0, 0))

        # Redraw the background elements
        screen.blit(enemy_image, (350, 250))
        screen.blit(title_text, (150, 150))

        # Draw the loading bar background
        pygame.draw.rect(screen, (255, 255, 255), [bar_x, bar_y, loading_bar_width, loading_bar_height], 2)
        # Draw the loading bar progress
        pygame.draw.rect(screen, (0, 255, 0), [bar_x + 2, bar_y + 2, progress, loading_bar_height - 4])

        pygame.display.update()

        # Increase the progress
        progress += increment
        if progress > loading_bar_width:
            progress = loading_bar_width

        pygame.time.delay(100)  # Delay to simulate loading progress


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    return distance < 27


def ai_move_and_shoot():
    global playerX, playerX_change, bulletX, bulletY, bullet_state, last_shoot_time

    if player_moving:
        # Move spaceship left and right
        if playerX <= 0:
            playerX_change = 8  # Move right faster
        elif playerX >= 736:
            playerX_change = -8  # Move left faster

        playerX += playerX_change

        # Shooting logic
        current_time = time.time()
        if bullet_state == "ready" and current_time - last_shoot_time >= shoot_interval:
            # Find the closest enemy
            closest_enemy = None
            min_distance = float('inf')

            for i in range(num_of_enemies):
                distance = math.sqrt(math.pow(enemyX[i] - playerX, 2) + (math.pow(enemyY[i] - playerY, 2)))
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = i

            if closest_enemy is not None:
                # Fire at the closest enemy
                bulletSound = mixer.Sound("laser.wav")
                bulletSound.play()
                bulletX = playerX
                bulletY = playerY
                fire_bullet(bulletX, bulletY)
                last_shoot_time = current_time


# Game Loop
running = True
game_over = False

# Show start screen with loading bar
start_screen()

while running:
    # RGB = Red, Green, Blue
    screen.fill((0, 0, 0))
    # Background Image
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # AI-controlled player actions
        ai_move_and_shoot()

        # Enemy Movement
        for i in range(num_of_enemies):

            # Game Over
            if enemyY[i] > 440:
                game_over = True
                player_moving = False  # Stop the spaceship from moving
                playerX = 370  # Move spaceship to the center
                bullet_state = "ready"  # Ensure the spaceship stops shooting
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 4
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -4
                enemyY[i] += enemyY_change[i]

            # Collision
            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i], i)

        # Bullet Movement
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

    # Display player and score
    player(playerX, playerY)
    show_score(textX, testY)

    # Display game over message if needed
    if game_over:
        game_over_text()

    pygame.display.update()
