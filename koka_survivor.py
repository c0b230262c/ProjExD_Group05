import math
import os
import random
import sys
import time
import pygame as pg
import pygame



WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 6

        # レベルと経験値の初期化
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 50
        self.font = pg.font.Font(None, 50)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        screen.blit(self.image, self.rect)

    # マウスの方向にスピード5で進むようにする
    def update(self, mouse_pos: tuple[int, int], screen: pg.Surface):
        """
        マウスの方向に応じてこうかとんを移動させる
        引数1 mouse_pos：マウスの現在位置座標タプル
        引数2 screen：画面Surface
        """
        x_diff, y_diff = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        norm = math.sqrt(x_diff**2 + y_diff**2)

    def gain_experience(self, amount: int):
        """
        経験値を取得し、レベルアップをチェックする
        引数 amount: 獲得する経験値の量
        """
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        """
        レベルアップ処理
        """
        self.level += 1
        self.experience = 0  # 経験値をリセット
        if self.level == 2:
            self.exp_to_next_level = 100  # レベル3になるための経験値を100に設定
        elif self.level == 3:
            self.exp_to_next_level = 100  # 次のレベルまでの経験値を150に設定
        self.speed += 1  # レベルアップ時に速度を上げるなどの強化

    def display_level(self, screen: pg.Surface):
        """
        レベルを画面に表示する
        引数 screen: 画面Surface
        """
        level_surf = self.font.render(f"Level: {self.level}", True, (0, 255, 0))
        screen.blit(level_surf, (50, 50))

    def display_experience_bar(self, screen: pg.Surface):
        """
        経験値ゲージを画面に表示する
        引数 screen: 画面Surface
        """
        bar_width = 400
        bar_height = 20
        filled_bar_width = int(bar_width * self.experience / self.exp_to_next_level)
        
        # 背景のバー
        pg.draw.rect(screen, (128, 128, 128), (50, 100, bar_width, bar_height)) # グレー
        # 埋まっている部分
        pg.draw.rect(screen, (0, 255, 0), (50, 100, filled_bar_width, bar_height)) # 緑

    def update(self, mouse_pos: tuple[int, int], screen: pg.Surface):
        """
        マウスの方向に応じてこうかとんを移動させる
        引数1 mouse_pos：マウスの現在位置座標タプル
        引数2 screen：画面Surface
        """
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



    
    def shoot_laser(self):
        """
        レーザーを発射するメソッド
        """
        return Laser(self)


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    def __init__(self, bird: Bird, target: pg.Rect):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        引数 target：ビームの目標となる敵
        """
        super().__init__()
        # こうかとん(bird)から敵(target)への方向ベクトルを計算
        self.vx, self.vy = calc_orientation(bird.rect, target)
        # ビームの角度を計算
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        # ビーム画像を方向に合わせて回転
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.rect = self.image.get_rect()
        # ビームの初期位置を設定
        self.rect.centery = bird.rect.centery + bird.rect.height * self.vy
        self.rect.centerx = bird.rect.centerx + bird.rect.width * self.vx
        self.speed = 10    


    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

class Laser(pg.sprite.Sprite):
    """
    一直線に出るレーザークラス
    """
    def __init__(self, bird: Bird, target_pos: tuple[int, int], duration: int = 3000):
        super().__init__()

        self.vx, self.vy = bird.dire
        # 水平または垂直方向に制限
        if abs(self.vx) > abs(self.vy):
            self.vy = 0
        else:
            self.vx = 0

        if self.vx == 0 and self.vy == 0:
            self.vx = 1 

        angle = math.degrees(math.atan2(-self.vy, self.vx))

        # レーザー画像のスケールと回転
        original_image = pg.image.load(f"fig/biglaser.png")
        screen_width, screen_height = pg.display.get_surface().get_size()
        max_length = 4 * math.hypot(screen_width, screen_height)  # レーザーの最大長さ
        scaled_image = pg.transform.scale(original_image, (int(max_length), original_image.get_height()))
        self.image = pg.transform.rotozoom(scaled_image, angle, 1.0)

        self.rect = self.image.get_rect()
        self.rect.center = bird.rect.center
        bird_head_offset = (bird.rect.width // 2, -bird.rect.height // 2)
        self.rect.center = (bird.rect.centerx + bird_head_offset[0], bird.rect.centery + bird_head_offset[1])

        self.speed = 0
        self.duration = duration
        self.spawn_time = pg.time.get_ticks()

    
    def calc_orientation(bird_pos, mouse_pos):
        x_diff = mouse_pos[0] - bird_pos[0]
        y_diff = mouse_pos[1] - bird_pos[1]
        norm = math.hypot(x_diff, y_diff)
        if norm == 0:  # ノルムがゼロの場合
            return 0, 0  # デフォルトの方向ベクトルを返す（ここでは水平）
        return x_diff / norm, y_diff / norm

    def update(self):
        current_time = pg.time.get_ticks()
        if current_time - self.spawn_time > self.duration:  # 指定時間が経過したら
            self.kill()  # レーザーを消す
            
            
class NeoBeam(pg.sprite.Sprite):
    """
    一度に複数方向へビームを発射するクラス
    """
    def __init__(self, bird: Bird, num: int):
        self.bird = bird
        self.num = num

    def gen_beams(self):
        """
        指定された数のビームを生成し、リストで返す
        """
        beams = []
        step = 100 / (self.num - 1) #ステップの計算
        angles = [-50 + step * i for i in range(self.num)] #角度をリストに入れる
        for angle in angles:
            beams.append(Beam(self.bird, angle)) #リストにappend
        return beams #リストを戻り値に設定
    

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
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
        """
        敵機をこうかとんの位置に向かって移動させる
        """
        bird_x, bird_y = self.bird.rect.center  # こうかとんの位置を取得
        x_diff, y_diff = bird_x - self.rect.centerx, bird_y - self.rect.centery
        angle = math.degrees(math.atan2(-y_diff, x_diff))  # 角度を計算

        if abs(x_diff) > abs(y_diff):  # 横方向の移動が大きい場合
            if x_diff > 0:  # こうかとんが右にいる場合
                self.image = pg.transform.flip(self.original_image, True, False)
            else:  # こうかとんが左にいる場合
                self.image = self.original_image
            self.image = pg.transform.rotate(self.image, 0)
        else:  # 縦方向の移動が大きい場合
            if y_diff < 0:  # こうかとんが下にいる場合
                self.image = pg.transform.rotate(self.original_image, -90)
            else:  # こうかとんが上にいる場合
                self.image = pg.transform.rotate(self.original_image, 90)

        norm = math.sqrt(x_diff**2 + y_diff**2)
        if norm != 0:
            self.vx, self.vy = (self.speed * x_diff / norm, self.speed * y_diff / norm)
            self.rect.move_ip(self.vx, self.vy)


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
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

class Gravity(pg.sprite.Sprite):
    def __init__(self, life:int):
        super().__init__()
        self.image = pg.Surface((WIDTH, HEIGHT))
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.life = life
        self.image.set_alpha(120)
        
    
    def update(self):
        self.life -= 1
        if self.life < 0:
            self.kill()

class RollBlade(pg.sprite.Sprite):
    def __init__(self, bird: Bird, num):
        super().__init__()
        self.bird = bird
        self.blade_count = num
        self.speed = 3
        self.radius = 100
        self.angle = 0
        self.size = 75
        

        self.original_image = pg.image.load("fig/blade.png").convert_alpha()
        self.image = pg.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.original_image.get_rect()

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
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/aozora.jpg")
    scaled_bg_img = pg.transform.scale(bg_img, (int(bg_img.get_width() * 0.7), int(bg_img.get_height() * 0.7)))
    score = Score()
    num = 1 #Bladeの数

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravities = pg.sprite.Group()
    blades = pg.sprite.Group()
    blades.add(RollBlade(bird, num))
    lasers = pg.sprite.Group()  # レーザーのグループを追加

    tmr = 0
    clock = pg.time.Clock()


    while True:
        key_lst = pg.key.get_pressed()
        if tmr % 100 == 0:
            if emys:  # 敵が存在する場合
                # 最も近い敵を選択
                nearest_enemy = min(emys, key=lambda emy: math.hypot(bird.rect.centerx - emy.rect.centerx, bird.rect.centery - emy.rect.centery))
                # 最も近い敵の方向にビームを発射
                beams.add(Beam(bird, nearest_enemy.rect))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        mouse_pos = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if emys:
                    nearest_enemy = min(emys, key=lambda emy: math.hypot(bird.rect.centerx - emy.rect.centerx, bird.rect.centery - emy.rect.centery))
                    beams.add(Beam(bird, nearest_enemy.rect))
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                if score.value >= 200:
                    gravities.add(Gravity(400))
                    score.value -= 200

        screen.blit(scaled_bg_img, [0, 0])
        if tmr % 100 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy(bird))  # 鳥のインスタンスを渡す
        if tmr%500 == 0:  #500フレームに1回攻撃を出現させる。
            beams.add(Laser(bird, pg.mouse.get_pos()))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
            bird.gain_experience(10)  # 経験値を獲得

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
            bird.gain_experience(5)  # 経験値を獲得

        if len(pg.sprite.spritecollide(bird, bombs, True)) != 0:
            bird.change_img(8, screen)  # こうかとん悲しみエフェクト

        

        for emy in pg.sprite.groupcollide(emys, blades, True, False).keys():
            exps.add(Explosion(emy, 100))
            score.value += 10
            bird.change_img(6, screen)
            bird.gain_experience(10) 

        for bomb in pg.sprite.groupcollide(bombs, blades, True, False).keys():
            exps.add(Explosion(bomb, 50))
            score.value += 1
            bird.gain_experience(5) 


        if len(pg.sprite.spritecollide(bird, bombs, True)) != 0:
            bird.change_img(8, screen)
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return

        if len(pg.sprite.spritecollide(bird, emys, True)) != 0:
            bird.change_img(8, screen)  # こうかとん悲しみエフェクト
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        
        if len(pg.sprite.spritecollide(bird, emys, True)) != 0:
            bird.change_img(8, screen)  # こうかとん悲しみエフェクト
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        
        if len(pg.sprite.spritecollide(bird, emys, True)) != 0:
            bird.change_img(8, screen) # こうかとん悲しみエフェクト
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        
        for gravity in gravities:
            for bomb in pg.sprite.spritecollide(gravity, bombs, True):
                exps.add(Explosion(bomb, 50))
                score.value += 1
                bird.gain_experience(5)  # 経験値を獲得

            for bomb in pg.sprite.spritecollide(gravity, emys, True):
                exps.add(Explosion(bomb, 50))
                score.value += 10
                bird.gain_experience(10)  # 経験値を獲得

        for laser in pg.sprite.groupcollide(lasers, emys, False, True).keys():
            exps.add(Explosion(laser, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ

        for laser in pg.sprite.groupcollide(lasers, bombs, False, True).keys():
            exps.add(Explosion(laser, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
        
        bird.update(mouse_pos, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        lasers.update()  # レーザーの更新を追加     
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        gravities.update()
        gravities.draw(screen)
        blades.update()
        blades.draw(screen)
        for blade in blades:
            blade.draw(screen)
        lasers.draw(screen)  # レーザーの描画を追加
        gravities.draw(screen)  
        score.update(screen)
        beams.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

