import pygame
import sys
import random

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)

BIRD_WIDTH = 40
BIRD_HEIGHT = 30
BIRD_X = 50
bird_y = SCREEN_HEIGHT // 2
bird_velocity = 0
GRAVITY = 0.5
JUMP_STRENGTH = -10
bird_surface = None

PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_FREQUENCY = 1500
pipe_list = []
PIPE_SPEED = 3

score = 0
font = None
high_score = 0
passed_pipes_ids = set()


game_active = False

background_surface = None


def create_pipe():
    random_pipe_pos = random.randint(150, SCREEN_HEIGHT - 150 - PIPE_GAP)
    bottom_pipe = pygame.Rect(SCREEN_WIDTH, random_pipe_pos, PIPE_WIDTH, SCREEN_HEIGHT - random_pipe_pos)
    top_pipe = pygame.Rect(SCREEN_WIDTH, 0, PIPE_WIDTH, random_pipe_pos - PIPE_GAP)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(screen, pipes):
    for pipe_rect in pipes:
        pygame.draw.rect(screen, GREEN, pipe_rect)

def check_collision(pipes, bird_rect_param):
    for pipe in pipes:
        if bird_rect_param.colliderect(pipe):
            return True
    if bird_rect_param.top <= 0 or bird_rect_param.bottom >= SCREEN_HEIGHT:
        return True
    return False

def display_score(screen, current_score, game_state):
    global font, high_score

    if game_state == 'main_game':
        score_surface = font.render(f'Score: {int(current_score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)
    
    elif game_state == 'game_over':
        score_surface = font.render(f'Score: {int(current_score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = font.render(f'High Score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(high_score_surface, high_score_rect)

        game_over_surface = font.render('Game Over', True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_surface, game_over_rect)

        restart_surface = font.render('Press SPACE to play', True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_surface, restart_rect)

def update_score(current_score, pipes, bird_rect_param, current_passed_ids_set):
    new_score = current_score
    for pipe_rect in pipes:
        if pipe_rect.centerx < bird_rect_param.centerx and id(pipe_rect) not in current_passed_ids_set and pipe_rect.top != 0:
            current_passed_ids_set.add(id(pipe_rect))
            new_score += 1
    return new_score, current_passed_ids_set

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird with python')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)


try:
    original_bird_surface = pygame.image.load('bird.png').convert_alpha()
    bird_surface = pygame.transform.scale(original_bird_surface, (BIRD_WIDTH, BIRD_HEIGHT))
except pygame.error as e:
    print(f"Error al cargar la imagen 'bird.png': {e}")
    bird_surface = None

try:

    loaded_background = pygame.image.load('background.png').convert()
    background_surface = pygame.transform.scale(loaded_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Error al cargar la imagen 'background.png': {e}")
    print("Se usará un color sólido azul como fondo.")
    background_surface = None

SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQUENCY)

def reset_game():
    global bird_y, bird_velocity, pipe_list, score, game_active, passed_pipes_ids
    bird_y = SCREEN_HEIGHT // 2
    bird_velocity = 0
    pipe_list = []
    score = 0
    passed_pipes_ids = set()
    game_active = True

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_active:
                    bird_velocity = JUMP_STRENGTH
                else:
                    reset_game()
        
        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    bird_rect = pygame.Rect(BIRD_X, bird_y, BIRD_WIDTH, BIRD_HEIGHT)

    if game_active:
        bird_velocity += GRAVITY
        bird_y += bird_velocity
        bird_rect.y = int(bird_y)

        pipe_list = move_pipes(pipe_list)
        
        score, passed_pipes_ids = update_score(score, pipe_list, bird_rect, passed_pipes_ids)
        if score > high_score:
            high_score = score

        if check_collision(pipe_list, bird_rect):
            game_active = False


    if background_surface:
        screen.blit(background_surface, (0,0))
    else:
        screen.fill((50, 150, 255))


    if game_active:
        draw_pipes(screen, pipe_list)

        if bird_surface:
            rotated_bird_display = pygame.transform.rotozoom(bird_surface, -bird_velocity * 2.5, 1)
            rotated_rect = rotated_bird_display.get_rect(center = bird_rect.center)
            screen.blit(rotated_bird_display, rotated_rect)
        else:
            pygame.draw.rect(screen, (255,255,0), bird_rect)

        display_score(screen, score, 'main_game')
    else:
        draw_pipes(screen, pipe_list)
        
        display_score(screen, score, 'game_over')

        if bird_surface:
             screen.blit(bird_surface, bird_rect)
        else:
            pygame.draw.rect(screen, (255,255,0), bird_rect)


    pygame.display.update()
    clock.tick(FPS)


pygame.quit()
sys.exit()
