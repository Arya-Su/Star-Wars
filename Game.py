import pygame
import os
import random

pygame.init()
pygame.font.init()
pygame.mixer.init()


WIDTH, HEIGHT = 1000, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Invadersi")

# zvuk
LASER_S = pygame.mixer.Sound("laser.wav")
music = pygame.mixer.music.load("star_wars.mp3")
pygame.mixer.music.play(-1)

# slike broda
RED_SS = pygame.image.load(os.path.join("pixel_ship_red_small.png"))
GREEN_SS = pygame.image.load(os.path.join("pixel_ship_green_small.png"))
BLUE_SS = pygame.image.load(os.path.join("pixel_ship_blue_small.png"))

# brod igraca
YELLOW_SS = pygame.image.load(os.path.join("pixel_ship_yellow.png"))

# laseri
RED_L = pygame.image.load(os.path.join("pixel_laser_red.png"))
GREEN_L = pygame.image.load(os.path.join("pixel_laser_green.png"))
BLUE_L = pygame.image.load(os.path.join("pixel_laser_blue.png"))
YELLOW_L = pygame.image.load(os.path.join("pixel_laser_yellow.png"))

# pozadina
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("background-black.png")), (WIDTH, HEIGHT))


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
        return collide(obj, self)


class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

       # Load image and get dimensions
        self.ship_img = pygame.image.load(os.path.join(
            "pixel_ship_yellow.png")).convert_alpha()
        self.rect = self.ship_img.get_rect()

        # Create mask surface with same dimensions as image
        self.mask = pygame.surface.Surface((self.rect.width, self.rect.height))

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
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
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.player_img = YELLOW_SS
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.laser_img = YELLOW_L

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

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                         self.ship_img.get_height() + 5, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (238, 238, 0), (self.x, self.y + self.ship_img.get_height() +
                         5, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SS, RED_L),
        "green": (GREEN_SS, GREEN_L),
        "blue": (BLUE_SS, BLUE_L)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # PROBA

    # ( def move_lasers(self, vel, player):
      #  if self.lasers:
       #     self.lasers.y += vel
            # if self.lasers.collision(player):
            #  player.health -= 1
            #  self.lasers = None
           # elif self.lasers.y > HEIGHT:
           # self.lasers = None)


def collide(obj1, obj2):
    offset_x = obj2.x-obj1.x
    offset_y = obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 65
    level = 0
    lives = 5
    main_font = pygame.font.Font("SWfont.ttf", 30)
    lost_font = pygame.font.Font("SWfont.ttf", 65)

    player = Player(300, 615)
    player_vel = 12
    clock = pygame.time.Clock()
    timer = 0
    lost = False
    lost_count = 0

    enemies = []
    wave_lenght = 4
    enemy_vel = 2
    laser_vel = 5

    def redraw_window():
        WIN.blit(BG, (0, 0))
# text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width()-10, 10))

        player.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_font.render(
                f"You lost at level {level}", 1, (255, 0, 0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS*3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            if level > 1:
                next_level = main_font.render(
                    f"Next level {level}", 1, (255, 255, 0))
                WIN.blit(next_level, (WIDTH - next_level.get_width()-10, 50))
                wave_lenght += 4
                pygame.display.update()

            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(
                    50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 17 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            LASER_S.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    second_font = pygame.font.SysFont("ITCSerifGothic", 60)
    title_font = pygame.font.Font("SWfont.ttf", 40)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = second_font.render(
            "A long time ago in a galaxy far, far away...", 1, (0, 205, 205))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 300))
        title_labell = title_font.render(
            "Press the mouse to begin", 1, (255, 255, 255))
        WIN.blit(title_labell, (WIDTH/2 - title_labell.get_width()/2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()


main()
