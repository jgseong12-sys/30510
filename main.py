import pygame
import math
import random

pygame.init()

# ==============================
# 기본 설정
# ==============================
SCREEN_W, SCREEN_H = 1200, 800
WORLD_W, WORLD_H = 2400, 1600

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("2 Player Top-Down Shooter")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 60)

# 색상
GRASS = (70, 130, 70)
ROAD = (90, 90, 90)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
YELLOW = (245, 210, 40)
BLUE = (50, 120, 255)
RED = (230, 60, 60)
GREEN = (50, 220, 80)
GRAY = (110, 110, 110)
DARK_GRAY = (55, 55, 55)
BROWN = (130, 80, 40)
TREE_GREEN = (30, 110, 45)
ROCK = (120, 125, 130)
ORANGE = (255, 150, 30)


# ==============================
# 플레이어
# ==============================
class Player:
    def __init__(self, x, y, color, name, controls):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.controls = controls

        self.radius = 24
        self.speed = 300
        self.hp = 100

        self.aim_x = 1
        self.aim_y = 0

        self.has_weapon = False
        self.shoot_cooldown = 0

    def rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self, dt, keys, obstacles):
        dx = 0
        dy = 0

        if keys[self.controls["up"]]:
            dy -= 1
        if keys[self.controls["down"]]:
            dy += 1
        if keys[self.controls["left"]]:
            dx -= 1
        if keys[self.controls["right"]]:
            dx += 1

        # 대각선 이동 속도 보정
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        new_x = self.x + dx * self.speed * dt
        new_y = self.y + dy * self.speed * dt

        # X축 충돌
        test_rect = pygame.Rect(
            new_x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        if not collision(test_rect, obstacles):
            self.x = new_x

        # Y축 충돌
        test_rect = pygame.Rect(
            self.x - self.radius,
            new_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        if not collision(test_rect, obstacles):
            self.y = new_y

        # 맵 밖으로 못 나가게
        self.x = max(self.radius, min(WORLD_W - self.radius, self.x))
        self.y = max(self.radius, min(WORLD_H - self.radius, self.y))

        # 조준
        aim_dx = 0
        aim_dy = 0

        if keys[self.controls["aim_up"]]:
            aim_dy -= 1
        if keys[self.controls["aim_down"]]:
            aim_dy += 1
        if keys[self.controls["aim_left"]]:
            aim_dx -= 1
        if keys[self.controls["aim_right"]]:
            aim_dx += 1

        if aim_dx != 0 or aim_dy != 0:
            length = math.hypot(aim_dx, aim_dy)
            self.aim_x = aim_dx / length
            self.aim_y = aim_dy / length

        self.shoot_cooldown -= dt

    def shoot(self):
        if not self.has_weapon:
            return None

        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = 0.3

        return Bullet(
            self.x + self.aim_x * 35,
            self.y + self.aim_y * 35,
            self.aim_x,
            self.aim_y,
            self
        )

    def draw(self, surface, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)

        # 그림자
        pygame.draw.ellipse(
            surface,
            (30, 30, 30),
            (sx - 20, sy + 10, 40, 18)
        )

        # 다리
        pygame.draw.circle(surface, DARK_GRAY, (sx - 10, sy + 12), 10)
        pygame.draw.circle(surface, DARK_GRAY, (sx + 10, sy + 12), 10)

        # 몸통
        pygame.draw.circle(surface, self.color, (sx, sy + 4), 22)

        # 머리
        pygame.draw.circle(surface, (245, 210, 180), (sx, sy - 15), 13)

        # 조준 방향
        gun_end_x = sx + self.aim_x * 42
        gun_end_y = sy + self.aim_y * 42

        # 팔
        pygame.draw.line(
            surface,
            (240, 220, 190),
            (sx, sy),
            (
                int(sx + self.aim_x * 20),
                int(sy + self.aim_y * 20)
            ),
            10
        )

        # 총
        if self.has_weapon:
            pygame.draw.line(
                surface,
                BLACK,
                (
                    int(sx + self.aim_x * 15),
                    int(sy + self.aim_y * 15)
                ),
                (int(gun_end_x), int(gun_end_y)),
                8
            )

        # 이름
        name_text = FONT.render(self.name, True, WHITE)
        surface.blit(
            name_text,
            (sx - name_text.get_width() // 2, sy - 65)
        )

        # HP 바
        bar_w = 60
        hp_ratio = max(0, self.hp) / 100

        pygame.draw.rect(
            surface,
            RED,
            (sx - bar_w // 2, sy - 45, bar_w, 8)
        )

        pygame.draw.rect(
            surface,
            GREEN,
            (sx - bar_w // 2, sy - 45, int(bar_w * hp_ratio), 8)
        )


# ==============================
# 총알
# ==============================
class Bullet:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.owner = owner

        self.speed = 850
        self.radius = 6
        self.damage = 15
        self.alive = True

    def update(self, dt, obstacles, players):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

        bullet_rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        # 구조물 충돌
        if collision(bullet_rect, obstacles):
            self.alive = False
            return

        # 플레이어 충돌
        for player in players:
            if player != self.owner and player.hp > 0:
                distance = math.hypot(
                    self.x - player.x,
                    self.y - player.y
                )

                if distance < player.radius + self.radius:
                    player.hp -= self.damage
                    self.alive = False
                    return

        # 맵 밖
        if (
            self.x < 0 or self.x > WORLD_W or
            self.y < 0 or self.y > WORLD_H
        ):
            self.alive = False

    def draw(self, surface, cam_x, cam_y):
        pygame.draw.circle(
            surface,
            ORANGE,
            (int(self.x - cam_x), int(self.y - cam_y)),
            self.radius
        )


# ==============================
# 충돌 검사
# ==============================
def collision(rect, obstacles):
    for obstacle in obstacles:
        if rect.colliderect(obstacle["rect"]):
            return True
    return False


# ==============================
# 맵 구조물 생성
# ==============================
obstacles = []


def add_obstacle(x, y, w, h, kind):
    obstacles.append({
        "rect": pygame.Rect(x, y, w, h),
        "kind": kind
    })


# 집 외벽
add_obstacle(250, 180, 400, 35, "wall")
add_obstacle(250, 180, 35, 300, "wall")
add_obstacle(615, 180, 35, 300, "wall")

# 집 아래 벽 - 문 공간 남김
add_obstacle(250, 445, 150, 35, "wall")
add_obstacle(500, 445, 150, 35, "wall")

# 집 내부 가구
add_obstacle(340, 260, 110, 55, "crate")
add_obstacle(500, 330, 70, 70, "crate")

# 창고
add_obstacle(1550, 950, 500, 40, "wall")
add_obstacle(1550, 950, 40, 350, "wall")
add_obstacle(2010, 950, 40, 350, "wall")
add_obstacle(1550, 1260, 190, 40, "wall")
add_obstacle(1850, 1260, 200, 40, "wall")

# 창고 상자
add_obstacle(1650, 1040, 90, 90, "crate")
add_obstacle(1850, 1080, 120, 70, "crate")
add_obstacle(1720, 1180, 80, 60, "crate")

# 중앙 콘크리트 엄폐물
add_obstacle(900, 600, 350, 45, "concrete")
add_obstacle(900, 600, 45, 200, "concrete")

add_obstacle(1200, 350, 300, 45, "concrete")
add_obstacle(1455, 350, 45, 200, "concrete")

add_obstacle(650, 1050, 45, 250, "concrete")
add_obstacle(650, 1255, 250, 45, "concrete")

# 자동차
add_obstacle(1100, 820, 170, 80, "car")
add_obstacle(1350, 820, 170, 80, "car")

# 나무
tree_positions = [
    (100, 800), (170, 850), (240, 780),
    (2150, 300), (2250, 360), (2300, 260),
    (350, 1300), (450, 1350), (520, 1280)
]

for x, y in tree_positions:
    add_obstacle(x, y, 70, 70, "tree")

# 바위
rock_positions = [
    (750, 300), (820, 340), (1950, 500),
    (2050, 550), (300, 1050)
]

for x, y in rock_positions:
    add_obstacle(x, y, 80, 60, "rock")

# 드럼통
drum_positions = [
    (500, 900), (570, 900), (640, 900),
    (2100, 1200), (2160, 1200)
]

for x, y in drum_positions:
    add_obstacle(x, y, 40, 40, "drum")


# ==============================
# 무기
# ==============================
weapon_spawns = [
    {"x": 800, "y": 850, "taken": False},
    {"x": 1200, "y": 500, "taken": False},
    {"x": 1700, "y": 700, "taken": False},
]


# ==============================
# 플레이어 생성
# ==============================
p1 = Player(
    150,
    150,
    YELLOW,
    "P1",
    {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,

        "aim_up": pygame.K_i,
        "aim_down": pygame.K_k,
        "aim_left": pygame.K_j,
        "aim_right": pygame.K_l,
    }
)

p2 = Player(
    2200,
    1400,
    BLUE,
    "P2",
    {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,

        "aim_up": pygame.K_KP8,
        "aim_down": pygame.K_KP5,
        "aim_left": pygame.K_KP4,
        "aim_right": pygame.K_KP6,
    }
)

players = [p1, p2]
bullets = []


# ==============================
# 구조물 그리기
# ==============================
def draw_obstacle(surface, obstacle, cam_x, cam_y):
    rect = obstacle["rect"].copy()
    rect.x -= int(cam_x)
    rect.y -= int(cam_y)

    kind = obstacle["kind"]

    if kind == "wall":
        pygame.draw.rect(surface, (190, 170, 150), rect)
        pygame.draw.rect(surface, DARK_GRAY, rect, 4)

    elif kind == "crate":
        pygame.draw.rect(surface, BROWN, rect)
        pygame.draw.rect(surface, (90, 50, 25), rect, 4)
        pygame.draw.line(
            surface,
            (90, 50, 25),
            rect.topleft,
            rect.bottomright,
            3
        )
        pygame.draw.line(
            surface,
            (90, 50, 25),
            rect.topright,
            rect.bottomleft,
            3
        )

    elif kind == "concrete":
        pygame.draw.rect(surface, GRAY, rect)
        pygame.draw.rect(surface, DARK_GRAY, rect, 4)

        # 콘크리트 블록 선
        for x in range(rect.x, rect.right, 30):
            pygame.draw.line(
                surface,
                (80, 80, 80),
                (x, rect.y),
                (x, rect.bottom),
                2
            )

    elif kind == "car":
        pygame.draw.rect(surface, (190, 40, 40), rect, border_radius=12)
        pygame.draw.rect(
            surface,
            (120, 190, 220),
            (rect.x + 35, rect.y + 10, rect.width - 70, 25)
        )
        pygame.draw.circle(surface, BLACK, (rect.x + 30, rect.bottom), 13)
        pygame.draw.circle(
            surface,
            BLACK,
            (rect.right - 30, rect.bottom),
            13
        )

    elif kind == "tree":
        pygame.draw.circle(
            surface,
            (90, 55, 25),
            rect.center,
            15
        )
        pygame.draw.circle(
            surface,
            TREE_GREEN,
            rect.center,
            rect.width // 2
        )
        pygame.draw.circle(
            surface,
            (50, 150, 60),
            (rect.centerx - 10, rect.centery - 10),
            20
        )

    elif kind == "rock":
        pygame.draw.ellipse(surface, ROCK, rect)
        pygame.draw.ellipse(surface, DARK_GRAY, rect, 3)

    elif kind == "drum":
        pygame.draw.rect(surface, (40, 120, 190), rect, border_radius=5)
        pygame.draw.line(
            surface,
            WHITE,
            (rect.x, rect.y + 12),
            (rect.right, rect.y + 12),
            3
        )
        pygame.draw.line(
            surface,
            WHITE,
            (rect.x, rect.bottom - 12),
            (rect.right, rect.bottom - 12),
            3
        )


# ==============================
# 메인 게임 루프
# ==============================
running = True
game_over = False
winner = ""

while running:
    dt = clock.tick(60) / 1000
    keys = pygame.key.get_pressed()

    # 이벤트
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over:
                # P1 발사
                if event.key == pygame.K_f:
                    bullet = p1.shoot()
                    if bullet:
                        bullets.append(bullet)

                # P2 발사
                if event.key == pygame.K_RETURN:
                    bullet = p2.shoot()
                    if bullet:
                        bullets.append(bullet)

            # 게임 재시작
            if game_over and event.key == pygame.K_r:
                p1.x, p1.y = 150, 150
                p2.x, p2.y = 2200, 1400

                p1.hp = 100
                p2.hp = 100

                p1.has_weapon = False
                p2.has_weapon = False

                bullets.clear()

                for weapon in weapon_spawns:
                    weapon["taken"] = False

                game_over = False

    if not game_over:
        # 플레이어 업데이트
        p1.update(dt, keys, obstacles)
        p2.update(dt, keys, obstacles)

        # 무기 획득
        for weapon in weapon_spawns:
            if not weapon["taken"]:
                for player in players:
                    distance = math.hypot(
                        player.x - weapon["x"],
                        player.y - weapon["y"]
                    )

                    if distance < 40:
                        player.has_weapon = True
                        weapon["taken"] = True

        # 총알 업데이트
        for bullet in bullets:
            bullet.update(dt, obstacles, players)

        bullets = [bullet for bullet in bullets if bullet.alive]

        # 승리 확인
        if p1.hp <= 0:
            game_over = True
            winner = "PLAYER 2 WINS!"

        if p2.hp <= 0:
            game_over = True
            winner = "PLAYER 1 WINS!"

    # ==============================
    # 카메라: 두 플레이어 중간을 중심
    # ==============================
    center_x = (p1.x + p2.x) / 2
    center_y = (p1.y + p2.y) / 2

    cam_x = center_x - SCREEN_W / 2
    cam_y = center_y - SCREEN_H / 2

    cam_x = max(0, min(WORLD_W - SCREEN_W, cam_x))
    cam_y = max(0, min(WORLD_H - SCREEN_H, cam_y))

    # ==============================
    # 화면 그리기
    # ==============================
    screen.fill(GRASS)

    # 도로
    road_y = 760 - cam_y
    pygame.draw.rect(
        screen,
        ROAD,
        (0, road_y, SCREEN_W, 180)
    )

    # 도로 중앙선
    for x in range(-int(cam_x) % 80, SCREEN_W, 80):
        pygame.draw.rect(
            screen,
            (220, 220, 180),
            (x, road_y + 85, 40, 8)
        )

    # 구조물
    for obstacle in obstacles:
        draw_obstacle(screen, obstacle, cam_x, cam_y)

    # 무기
    for weapon in weapon_spawns:
        if not weapon["taken"]:
            x = int(weapon["x"] - cam_x)
            y = int(weapon["y"] - cam_y)

            pygame.draw.circle(screen, (255, 220, 80), (x, y), 25)
            pygame.draw.rect(
                screen,
                BLACK,
                (x - 5, y - 12, 30, 10)
            )
            pygame.draw.rect(
                screen,
                DARK_GRAY,
                (x + 15, y - 8, 15, 18)
            )

    # 총알
    for bullet in bullets:
        bullet.draw(screen, cam_x, cam_y)

    # 플레이어
    p1.draw(screen, cam_x, cam_y)
    p2.draw(screen, cam_x, cam_y)

    # 화면 상단 HP
    p1_text = FONT.render(
        f"P1 HP: {max(0, p1.hp)} {'[GUN]' if p1.has_weapon else '[NO GUN]'}",
        True,
        WHITE
    )

    p2_text = FONT.render(
        f"P2 HP: {max(0, p2.hp)} {'[GUN]' if p2.has_weapon else '[NO GUN]'}",
        True,
        WHITE
    )

    screen.blit(p1_text, (20, 20))
    screen.blit(
        p2_text,
        (SCREEN_W - p2_text.get_width() - 20, 20)
    )

    # 조작법
    help_text = FONT.render(
        "P1: WASD Move / IJKL Aim / F Shoot     |     "
        "P2: Arrow Move / Numpad 8456 Aim / Enter Shoot",
        True,
        WHITE
    )

    screen.blit(
        help_text,
        (
            SCREEN_W // 2 - help_text.get_width() // 2,
            SCREEN_H - 35
        )
    )

    # 게임 종료 화면
    if game_over:
        overlay = pygame.Surface(
            (SCREEN_W, SCREEN_H),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        win_text = BIG_FONT.render(winner, True, WHITE)
        restart_text = FONT.render(
            "Press R to Restart",
            True,
            WHITE
        )

        screen.blit(
            win_text,
            (
                SCREEN_W // 2 - win_text.get_width() // 2,
                SCREEN_H // 2 - 50
            )
        )

        screen.blit(
            restart_text,
            (
                SCREEN_W // 2 - restart_text.get_width() // 2,
                SCREEN_H // 2 + 30
            )
        )

    pygame.display.flip()

pygame.quit()
