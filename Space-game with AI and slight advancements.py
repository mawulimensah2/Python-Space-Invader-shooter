import math
import random
import pygame
from pygame import mixer
import time

# Initialize pygame
pygame.init()

# Game Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SPEED = 8
ENEMY_SPEED = 4
BULLET_SPEED = 10
NUM_ENEMIES = 6

# Load assets
background = pygame.image.load('background.png')
player_img = pygame.image.load('player.png')
bullet_img = pygame.image.load('bullet.png')
enemy_img = pygame.image.load('enemy.png')
mixer.music.load("background.wav")
mixer.music.play(-1)

# Font
font = pygame.font.Font('freesansbold.ttf', 32)
over_font = pygame.font.Font('freesansbold.ttf', 64)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader")
pygame.display.set_icon(pygame.image.load('ufo.png'))


# Game State
def initialize_game():
    global player_x, player_y, player_x_change, bullet_x, bullet_y, bullet_state
    global enemies, score, game_over, last_shoot_time, shoot_interval

    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT - 100
    player_x_change = PLAYER_SPEED
    bullet_x = 0
    bullet_y = player_y
    bullet_state = "ready"
    score = 0
    game_over = False
    last_shoot_time = time.time()
    shoot_interval = 0.1

    enemies = []
    for _ in range(NUM_ENEMIES):
        x = random.randint(0, SCREEN_WIDTH - 64)
        y = random.randint(50, 150)
        enemies.append({
            'x': x,
            'y': y,
            'x_change': ENEMY_SPEED,
            'y_change': 40
        })


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def draw_button(surface, color, rect, text):
    pygame.draw.rect(surface, color, rect)
    draw_text(text, font, (0, 0, 0), surface, rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)


def handle_button_click(position, button_rects):
    for button, action in button_rects:
        if button.collidepoint(position):
            action()


def game_loop():
    global player_x, player_y, player_x_change, bullet_x, bullet_y, bullet_state
    global enemies, score, game_over, last_shoot_time, shoot_interval

    initialize_game()  # Initialize the game state
    running = True
    button_rects = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    initialize_game()
                elif event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    handle_button_click(event.pos, button_rects)

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_x_change
            if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - 64:
                player_x += player_x_change

            # AI Shooting Logic
            current_time = time.time()
            if bullet_state == "ready" and current_time - last_shoot_time >= shoot_interval:
                for enemy in enemies:
                    if random.random() < 0.01:  # Random chance to shoot
                        bullet_x = player_x
                        bullet_y = player_y
                        bullet_state = "fire"
                        last_shoot_time = current_time

            # Move Bullet
            if bullet_state == "fire":
                screen.blit(bullet_img, (bullet_x + 16, bullet_y + 10))
                bullet_y -= BULLET_SPEED
                if bullet_y < 0:
                    bullet_y = player_y
                    bullet_state = "ready"

            # Move and Draw Enemies
            for enemy in enemies:
                enemy['x'] += enemy['x_change']
                if enemy['x'] <= 0 or enemy['x'] >= SCREEN_WIDTH - 64:
                    enemy['x_change'] *= -1
                    enemy['y'] += enemy['y_change']
                if enemy['y'] > SCREEN_HEIGHT - 150:
                    game_over = True

                screen.blit(enemy_img, (enemy['x'], enemy['y']))

            # Collision Detection
            for enemy in enemies:
                if bullet_state == "fire":
                    distance = math.sqrt(math.pow(enemy['x'] - bullet_x, 2) + (math.pow(enemy['y'] - bullet_y, 2)))
                    if distance < 27:
                        explosion_sound = mixer.Sound("explosion.wav")
                        explosion_sound.play()
                        bullet_y = player_y
                        bullet_state = "ready"
                        score += 1
                        enemy['x'] = random.randint(0, SCREEN_WIDTH - 64)
                        enemy['y'] = random.randint(50, 150)

            # Draw Player
            screen.blit(player_img, (player_x, player_y))

            # Display Score
            draw_text(f"Score : {score}", font, (255, 255, 255), screen, 10, 10)

            if game_over:
                draw_text("GAME OVER", over_font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)

                # Draw Restart and Quit Buttons
                restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50)
                quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 300, 50)
                button_rects = [
                    (restart_button_rect, lambda: initialize_game()),
                    (quit_button_rect, lambda: pygame.quit() or exit())
                ]

                draw_button(screen, (0, 255, 0), restart_button_rect, "Restart")
                draw_button(screen, (255, 0, 0), quit_button_rect, "Quit")

        pygame.display.update()


game_loop()
pygame.quit()
