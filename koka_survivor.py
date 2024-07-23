import math
import os
import random
import sys
import time
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    def __init__(self, num: int, xy: tuple[int, int], blades: pg.sprite.Group):
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)
        self.imgs = {
            (+1, 0): img,
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),
            (-1, 0): img0,
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 6

        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 50
        self.font = pg.font.Font(None, 50)
        self.roll_blade_count = 0
        self.blades = blades  # blades を受け取る

    def gain_experience(self, amount: int):
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience = 0
        self.exp_to_next_level += 50
        self.speed += 1
        if self.level == 2:
            self.roll_blade_count = 1
        elif self.level == 3:
            self.roll_blade_count = 2
        elif self.level > 3 and self.level % 2 == 0:
            for blade in self.blades:
                blade.increase_speed()

    def display_level(self, screen: pg.Surface):
        level_surf = self.font.render(f"Level: {self.level}", True, (0, 255, 0))
        screen.blit(level_surf, (50, 50))

    def display_experience_bar(self, screen: pg.Surface):
        bar_width = 400
        bar_height = 20
        filled_bar_width = int(bar_width * self.experience / self.exp_to_next_level)
        pg.draw.rect(screen, (128, 128, 128), (50, 100, bar_width, bar_height))
        pg.draw.rect(screen, (0, 255, 0), (50, 100, filled_bar_width, bar_height))

    def update(self, mouse_pos: tuple[int, int], screen: pg.Surface):
        x_diff, y_diff = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        norm = math.sqrt(x_diff**2 + y_diff**2)
        if norm <= self.speed:
            self.rect.centerx = mouse_pos[0]
            self.rect.centery = mouse_pos[1]
        else:
            self.rect.move_ip(self.speed * x_diff / norm, self.speed * y_diff / norm)

        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed * x_diff / norm, -self.speed * y_diff / norm)

        if x_diff != 0 or y_diff != 0:
            self.dire = (x_diff / norm, y_diff / norm)
            angle = math.degrees(math.atan2(-self.dire[1], self.dire[0]))
            self.image = pg.transform.rotozoom(self.imgs[(+1, 0)], angle, 1.0)

        screen.blit(self.image, self.rect)
        self.display_level(screen)
        self.display_experience_bar(screen)

    def change_img(self, num: int, screen: pg.Surface):
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        screen.blit(self.image, self.rect)

    def shoot_beam(self, target):
        return Beam(self, target)

    def shoot_laser(self, target_pos):
        return Laser(self, target_pos)

    def summon_roll_blade(self):
        return RollBlade(self, self.level, self.roll_blade_count)


class Beam(pg.sprite.Sprite):
    def __init__(self, bird: Bird, target: pg.Rect):
        super().__init__()
        self.vx, self.vy = calc_orientation(bird.rect, target)
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery + bird.rect.height * self.vy
        self.rect.centerx = bird.rect.centerx + bird.rect.width * self.vx
        self.speed = 10

    def update(self):
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Laser(pg.sprite.Sprite):
    def __init__(self, bird: Bird, target_pos: tuple[int, int], duration: int = 1000):
        super().__init__()
        self.vx, self.vy = bird.dire
        if abs(self.vx) > abs(self.vy):
            self.vy = 0
        else:
            self.vx = 0

        if self.vx == 0 and self.vy == 0:
            self.vx = 1

        angle = math.degrees(math.atan2(-self.vy, self.vx))
        original_image = pg.image.load(f"fig/biglaser.png")
        original_image.set_alpha(128)  # 透明度を設定 (0: 完全透明, 255: 完全不透明)
        screen_width, screen_height = pg.display.get_surface().get_size()
        max_length = 3*math.hypot(screen_width, screen_height)
        scaled_image = pg.transform.scale(original_image, (int(max_length), original_image.get_height()))
        self.image = pg.transform.rotozoom(scaled_image, angle, 1.0)

        self.rect = self.image.get_rect()
        self.rect.center = bird.rect.center
        bird_head_offset = (bird.rect.width // 2, -bird.rect.height // 2)
        self.rect.center = (bird.rect.centerx + bird_head_offset[0], bird.rect.centery + bird_head_offset[1])
        self.speed = 0
        self.duration = duration
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        current_time = pg.time.get_ticks()
        if current_time - self.spawn_time > self.duration:
            self.kill()


class Explosion(pg.sprite.Sprite):
    def __init__(self, obj: pg.sprite.Sprite, life: int):
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        self.life -= 1
        self.image = self.imgs[self.life//10 % 2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    imgs = [pg.image.load(f"fig/enemy{i}.png") for i in range(1, 4)]

    def __init__(self, bird: Bird):
        super().__init__()
        self.original_image = random.choice(__class__.imgs)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.bird = bird

        direction = random.choice(['top', 'left', 'right', 'bottom'])
        if direction == 'top':
            self.rect.center = random.randint(0, WIDTH), 0
        elif direction == 'left':
            self.rect.center = 0, random.randint(0, HEIGHT)
        elif direction == 'right':
            self.rect.center = WIDTH, random.randint(0, HEIGHT)
        elif direction == 'bottom':
            self.rect.center = random.randint(0, WIDTH), HEIGHT

        self.speed = 4

    def update(self):
        bird_x, bird_y = self.bird.rect.center
        x_diff, y_diff = bird_x - self.rect.centerx, bird_y - self.rect.centery
        angle = math.degrees(math.atan2(-y_diff, x_diff))

        if abs(x_diff) > abs(y_diff):
            if x_diff > 0:
                self.image = pg.transform.flip(self.original_image, True, False)
            else:
                self.image = self.original_image
            self.image = pg.transform.rotate(self.image, 0)
        else:
            if y_diff < 0:
                self.image = pg.transform.rotate(self.original_image, -90)
            else:
                self.image = pg.transform.rotate(self.original_image, 90)

        norm = math.sqrt(x_diff**2 + y_diff**2)
        if norm != 0:
            self.vx, self.vy = (self.speed * x_diff / norm, self.speed * y_diff / norm)
            self.rect.move_ip(self.vx, self.vy)


class Score:
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class RollBlade(pg.sprite.Sprite):
    def __init__(self, bird: Bird, level, count):
        super().__init__()
        self.bird = bird
        self.blade_count = count
        self.speed = 3 if level < 4 else 3 + (level - 3)  # レベル4以降は回転速度が上がる
        self.radius = 100
        self.angle = 0
        self.size = 75

        self.original_image = pg.image.load("fig/blade.png").convert_alpha()
        self.image = pg.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.original_image.get_rect()

    def increase_speed(self):
        self.speed += 1

    def update(self):
        self.angle = (self.angle + self.speed) % 360
        self.update_positions()

    def update_positions(self):
        for i in range(self.blade_count):
            angle_offset = 360 / self.blade_count * i
            rad_angle = math.radians(self.angle + angle_offset)
            blade_rect = self.image.get_rect()
            blade_rect.center = (
                self.bird.rect.centerx + self.radius * math.cos(rad_angle),
                self.bird.rect.centery + self.radius * math.sin(rad_angle)
            )
            self.image = pg.transform.rotate(self.original_image, -(self.angle + angle_offset))
            self.rect = blade_rect

    def draw(self, screen):
        for i in range(self.blade_count):
            angle_offset = 360 / self.blade_count * i
            rad_angle = math.radians(self.angle + angle_offset)
            blade_rect = self.image.get_rect()
            blade_rect.center = (
                self.bird.rect.centerx + self.radius * math.cos(rad_angle),
                self.bird.rect.centery + self.radius * math.sin(rad_angle)
            )
            rotated_image = pg.transform.rotate(self.original_image, -(self.angle + angle_offset))
            screen.blit(rotated_image, blade_rect)


def main():
    pg.display.set_caption("kokasurvivor")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/aozora.jpg")
    scaled_bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))
    score = Score()

    blades = pg.sprite.Group()  # blades グループをここで定義
    bird = Bird(3, (900, 400), blades)  # Bird に blades グループを渡す
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravities = pg.sprite.Group()
    lasers = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()

    while True:
        key_lst = pg.key.get_pressed()
        if tmr % 50 == 0:
            if emys:
                nearest_enemy = min(emys, key=lambda emy: math.hypot(bird.rect.centerx - emy.rect.centerx, bird.rect.centery - emy.rect.centery))
                beams.add(bird.shoot_beam(nearest_enemy.rect))
            if bird.level >= 3:
                lasers.add(bird.shoot_laser(pg.mouse.get_pos()))
            if bird.level == 2 or bird.level == 3:
                if not blades:
                    blades.add(bird.summon_roll_blade())

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        mouse_pos = pg.mouse.get_pos()
        if tmr % max(10, 50 - 5 * (bird.level - 1)) == 0:
            emys.add(Enemy(bird))
        if tmr % 10000 == 0:  #500フレームに1回攻撃を出現させる。
            beams.add(Laser(bird, pg.mouse.get_pos()))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))
            score.value += 10
            bird.change_img(6, screen)
            bird.gain_experience(10)

        for emy in pg.sprite.groupcollide(emys, blades, True, False).keys():
            exps.add(Explosion(emy, 100))
            score.value += 10
            bird.change_img(6, screen)
            bird.gain_experience(10)



        if len(pg.sprite.spritecollide(bird, emys, True)) != 0:
            bird.change_img(8, screen)
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return

     

        for laser in pg.sprite.groupcollide(lasers, emys, False, True).keys():
            exps.add(Explosion(laser, 100))
            score.value += 10
            bird.gain_experience(10)

        screen.blit(scaled_bg_img, [0, 0])
        bird.update(mouse_pos, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        lasers.update()
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        gravities.update()
        gravities.draw(screen)
        blades.update()
        for blade in blades:
            blade.draw(screen)
        lasers.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
