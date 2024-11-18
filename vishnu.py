import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
FPS = 60
score = 0
level = 1
max_level = 5
missed_chances = 0
start_time = 0
game_active = False
paused = False

background = pygame.image.load("backgroundv.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (110, 110))

enemy_image = pygame.image.load("enemy.png")
enemy_image = pygame.transform.scale(enemy_image, (90, 90))

bullet_width, bullet_height = 5, 10
bullets = []
bullet_speed = 2

enemy_spawn_rate = 80
enemy_speed = 0.5
enemies_destroyed_for_next_level = 10

font = pygame.font.SysFont("Arial", 24)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        surface.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                    self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_hovered(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_x, mouse_y)

start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Start Game", (0, 0, 255), WHITE)
quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Quit", (255, 0, 0), WHITE)

end_game_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "End Game", (255, 0, 0), WHITE)
retry_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Retry", (0, 255, 0), WHITE)

resume_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Resume", (0, 255, 0), WHITE)
pause_quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, "Quit", (255, 0, 0), WHITE)

pygame.mixer.music.load("backgroundv_music.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0)

loss_sound = pygame.mixer.Sound("loss_sound.wav")
loss_sound.set_volume(0.5)

def reset_game():
    global score, level, start_time, player_x, player_y, bullets, enemies, missed_chances, game_active, bullet_speed, enemy_speed
    score = 0
    level = 1
    missed_chances = 0
    start_time = time.time()
    player_x, player_y = WIDTH // 2, HEIGHT - 50 - 10
    bullets = []
    enemies = []
    bullet_speed = 2
    enemy_speed = 0.5
    game_active = True

def start_screen():
    global game_active
    screen.blit(background, (0, 0))
    start_button.draw(screen)
    quit_button.draw(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_hovered():
                reset_game()
                game_active = True
            elif quit_button.is_hovered():
                pygame.quit()
    
    pygame.display.update()

def end_screen():
    screen.fill(BLACK)
    
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 100))
    
    end_game_button.draw(screen)
    retry_button.draw(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if end_game_button.is_hovered():
                pygame.quit()
            elif retry_button.is_hovered():
                reset_game()
    
    pygame.display.update()

def pause_screen():
    screen.fill(BLACK)
    pause_text = font.render("Game Paused", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 100))
    
    resume_button.draw(screen)
    pause_quit_button.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if resume_button.is_hovered():
                global paused
                paused = False
            elif pause_quit_button.is_hovered():
                pygame.quit()
    
    pygame.display.update()

running = True
while running:
    if not game_active:
        start_screen()
    else:
        if paused:
            pause_screen()
        else:
            screen.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Press 'P' to pause
                        paused = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= 2
            if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
                player_x += 2
            if keys[pygame.K_SPACE]:
                bullets.append([player_x + 25, player_y])

            for bullet in bullets:
                bullet[1] -= bullet_speed
                if bullet[1] < 0:
                    bullets.remove(bullet)

            if random.randint(1, enemy_spawn_rate) == 1:
                enemy_x = random.randint(0, WIDTH - 50)
                enemies.append([enemy_x, -50])

            for enemy in enemies:
                enemy[1] += enemy_speed
                if enemy[1] > HEIGHT:
                    enemies.remove(enemy)
                    missed_chances += 1
                    loss_sound.play()

            for bullet in bullets:
                for enemy in enemies:
                    if (bullet[0] > enemy[0] and bullet[0] < enemy[0] + 50 and
                        bullet[1] > enemy[1] and bullet[1] < enemy[1] + 50):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 1
                        break

            if score >= level * 10 and level < max_level:
                level += 1
                enemy_speed += 0.5
                enemy_spawn_rate = max(20, enemy_spawn_rate - 10)
                bullet_speed += 0.5

            elapsed_time = int(time.time() - start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            timer_text = f"Time: {minutes:02}:{seconds:02}"

            screen.blit(player_image, (player_x, player_y))

            for bullet in bullets:
                pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))

            for enemy in enemies:
                screen.blit(enemy_image, (enemy[0], enemy[1]))

            score_text = font.render(f"Score: {score}", True, WHITE)
            level_text = font.render(f"Level: {level}", True, WHITE)
            timer_text_render = font.render(timer_text, True, WHITE)
            missed_text = font.render(f"Missed: {missed_chances}", True, WHITE)

            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
            screen.blit(timer_text_render, (WIDTH // 2 - timer_text_render.get_width() // 2, 10))
            screen.blit(missed_text, (WIDTH // 2 - missed_text.get_width() // 2, 40))

            if missed_chances >= 3:
                game_active = False
                end_screen()

            pygame.display.update()
            clock.tick(FPS)

pygame.quit()
