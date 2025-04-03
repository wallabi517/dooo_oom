import pygame
import math
import random
import sys

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doom Style Game with Shooting and Random Maze")

# 색상
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# 맵 크기
MAP_WIDTH = 21  # 홀수로 설정 (미로 생성 규칙)
MAP_HEIGHT = 15  # 홀수로 설정 (미로 생성 규칙)
TILE_SIZE = 40

# 플레이어 설정
player_x = TILE_SIZE + TILE_SIZE // 2
player_y = TILE_SIZE + TILE_SIZE // 2
player_angle = 0
player_speed = 3
FOV = math.pi / 3  # 60도
NUM_RAYS = 120
MAX_DEPTH = 300
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS

# 총기 설정
gun_sprite = pygame.image.load("gun.png")  # 총 스프라이트 이미지
gun_sprite = pygame.transform.scale(gun_sprite, (200, 200))  # 크기 조정
gun_shooting = False  # 총 발사 상태

# 랜덤 맵 생성 (Prim's Algorithm)
def generate_maze(width, height):
    maze = [["#" for _ in range(width)] for _ in range(height)]
    start_x, start_y = 1, 1
    maze[start_y][start_x] = "."

    walls = [(start_x + dx, start_y + dy) for dx, dy in [(2, 0), (0, 2)] if 0 < start_x + dx < width - 1 and 0 < start_y + dy < height - 1]

    while walls:
        wx, wy = random.choice(walls)
        walls.remove((wx, wy))

        if maze[wy][wx] == "#":
            neighbors = [(wx + dx, wy + dy) for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)] if 0 < wx + dx < width - 1 and 0 < wy + dy < height - 1]
            valid_neighbors = [(nx, ny) for nx, ny in neighbors if maze[ny][nx] == "."]

            if valid_neighbors:
                nx, ny = random.choice(valid_neighbors)
                maze[wy][wx] = "."
                maze[(wy + ny) // 2][(wx + nx) // 2] = "."
                walls.extend([(wx + dx, wy + dy) for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)] if 0 < wx + dx < width - 1 and 0 < wy + dy < height - 1 and maze[wy + dy][wx + dx] == "#"])

    return maze

# 맵 데이터
MAP = generate_maze(MAP_WIDTH, MAP_HEIGHT)

# 광선 캐스팅 함수
def cast_rays():
    start_angle = player_angle - FOV / 2
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * DELTA_ANGLE
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        for depth in range(MAX_DEPTH):
            target_x = player_x + depth * cos_a
            target_y = player_y + depth * sin_a

            col = int(target_x // TILE_SIZE)
            row = int(target_y // TILE_SIZE)

            if 0 <= col < MAP_WIDTH and 0 <= row < MAP_HEIGHT:
                if MAP[row][col] == "#":
                    depth *= math.cos(player_angle - angle)  # Fish-eye 효과 제거
                    wall_height = TILE_SIZE * 300 / (depth + 0.0001)
                    color = GRAY if depth < MAX_DEPTH // 2 else RED
                    pygame.draw.rect(screen, color, (ray * SCALE, HEIGHT // 2 - wall_height // 2, SCALE, wall_height))
                    break

# 총기 발사 함수
def shoot():
    global gun_shooting
    gun_shooting = True
    print("총 발사!")  # 총 발사 시 출력 (적이 없으므로 대미지 처리 없음)

# 플레이어 이동 처리
def move_player(dx, dy):
    global player_x, player_y
    new_x = player_x + dx
    new_y = player_y + dy

    col = int(new_x // TILE_SIZE)
    row = int(new_y // TILE_SIZE)

    if MAP[row][col] == ".":
        player_x = new_x
        player_y = new_y

# 게임 루프
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 마우스 왼쪽 버튼 클릭
            shoot()

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        move_player(player_speed * math.cos(player_angle), player_speed * math.sin(player_angle))
    if keys[pygame.K_s]:
        move_player(-player_speed * math.cos(player_angle), -player_speed * math.sin(player_angle))
    if keys[pygame.K_a]:
        player_angle -= 0.05
    if keys[pygame.K_d]:
        player_angle += 0.05

    # 광선 캐스팅
    cast_rays()

    # 총기 그리기
    if gun_shooting:
        screen.blit(gun_sprite, (WIDTH // 2 - 100, HEIGHT - 200))
        gun_shooting = False
    else:
        screen.blit(gun_sprite, (WIDTH // 2 - 100, HEIGHT - 200))

    # 화면 업데이트
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()