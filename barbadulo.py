import arcade
import random
import os
import math

# ======================
# COSTANTI
# ====================== 
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Navicella - Space Escape"

DISTANZA_OSTACOLI = 180
BOOST_DURATION = 5.0
BOOST_VELOCITA = 8
NUM_STELLE = 100
SCUDO_DURATION = 3.0

# ======================
def load_sprite_safe(path, scale):
    if os.path.exists(path):
        return arcade.Sprite(path, scale=scale)
    else:
        # Crea un cerchio rosso di emergenza se manca l'immagine
        texture = arcade.make_soft_circle_texture(50, arcade.color.RED)
        sprite = arcade.Sprite(texture, scale=scale)
        return sprite

# ======================
class NavicellaGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        self.stato_gioco = "MENU" 
        self.timer_menu = 0.0

        sound_path = "freesound_community-space-ship-bridge-loop-104525.mp3"
        self.scudo_sound = arcade.load_sound(sound_path) if os.path.exists(sound_path) else None
        self.scudo_player_audio = None

        self.player_list = arcade.SpriteList()
        self.ostacoli_list = arcade.SpriteList()
        self.potenziamenti_list = arcade.SpriteList()
        self.scudi_list = arcade.SpriteList()

        self.stelle = []
        for _ in range(NUM_STELLE):
            self.stelle.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(1, 3),
                random.uniform(1, 3.5)
            ])

        self.up_pressed = self.down_pressed = self.left_pressed = self.right_pressed = False
        self.score = 0
        self.best_score = 0
        
        self.setup()

    def setup(self):
        self.player_list.clear()
        self.ostacoli_list.clear()
        self.potenziamenti_list.clear()
        self.scudi_list.clear()

        self.player = load_sprite_safe("navicella.png", 0.33)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 80
        self.player_list.append(self.player)

        self.velocita_ostacoli = 2.5
        self.velocita_player = 4
        self.score = 0
        self.tempo_punti = 0
        self.prossimo_aumento = 60
        self.scudo_attivo = False
        self.boost_attivo = False
        self.game_over = False
        self.paused = False
        self.player.color = arcade.color.WHITE

        if self.scudo_player_audio:
            arcade.stop_sound(self.scudo_player_audio)
            self.scudo_player_audio = None

        y_spawn = SCREEN_HEIGHT + 100
        for _ in range(5):
            ost = load_sprite_safe("ostacolo.png", 0.4)
            ost.center_x = random.randint(40, SCREEN_WIDTH - 40)
            ost.center_y = y_spawn
            self.ostacoli_list.append(ost)
            y_spawn += DISTANZA_OSTACOLI

    def on_draw(self):
        self.clear()

        for s in self.stelle:
            arcade.draw_circle_filled(s[0], s[1], s[2], arcade.color.WHITE)

        if self.stato_gioco == "MENU":
            dim = 80 + math.sin(self.timer_menu * 5) * 10
            arcade.draw_text("PLAY", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
                             arcade.color.GREEN, font_size=int(dim), anchor_x="center", bold=True)
            arcade.draw_text("Premi SPAZIO per iniziare", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                             arcade.color.WHITE, font_size=18, anchor_x="center")
            return

        self.ostacoli_list.draw()
        self.player_list.draw()
        self.scudi_list.draw()
        self.potenziamenti_list.draw()

        # BARRA SCUDO - Usiamo draw_rectangle_filled (centro_x, centro_y, larghezza, altezza, colore)
        if self.scudo_attivo:
            percentuale = self.tempo_scudo / SCUDO_DURATION
            larghezza_barra = max(2, 50 * percentuale)
            arcade.draw_rect_filled(arcade.XYWH(self.player.center_x, self.player.center_y + 45, 
                                         larghezza_barra, 6), arcade.color.CYAN)

        arcade.draw_text(f"Score: {self.score}", 15, 570, arcade.color.WHITE, 14)
        arcade.draw_text(f"Best: {self.best_score}", 15, 550, arcade.color.YELLOW, 14)

        # OVERLAY PAUSA - Usiamo draw_rectangle_filled
        if self.paused:
            arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 400, 200, (20, 20, 20, 220))
            arcade.draw_text("PAUSA", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, arcade.color.WHITE, 30, anchor_x="center")
            arcade.draw_text("Premi 'R' per RIPRENDERE\nPremi 'M' per il MENU", 
                             SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20, arcade.color.GREEN, 18, anchor_x="center", align="center")

        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, arcade.color.RED, 45, anchor_x="center")
            arcade.draw_text("Premi 'R' per RIGIOCARE", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60, arcade.color.WHITE, 20, anchor_x="center")

    def on_update(self, delta_time):
        self.timer_menu += delta_time

        for s in self.stelle:
            s[1] -= s[3]
            if s[1] < 0:
                s[1] = SCREEN_HEIGHT
                s[0] = random.randint(0, SCREEN_WIDTH)

        if self.stato_gioco == "MENU" or self.paused or self.game_over:
            return

        self.tempo_punti += delta_time
        if self.tempo_punti >= 2.0:
            self.score += 5
            self.tempo_punti = 0
        
        if self.score >= self.prossimo_aumento:
            self.velocita_ostacoli += 0.4
            self.prossimo_aumento += 100

        if self.up_pressed: self.player.center_y += self.velocita_player
        if self.down_pressed: self.player.center_y -= self.velocita_player
        if self.left_pressed: self.player.center_x -= self.velocita_player
        if self.right_pressed: self.player.center_x += self.velocita_player

        self.player.center_x = max(25, min(SCREEN_WIDTH - 25, self.player.center_x))
        self.player.center_y = max(25, min(SCREEN_HEIGHT - 25, self.player.center_y))

        for ost in self.ostacoli_list:
            ost.center_y -= self.velocita_ostacoli
            if ost.center_y < -50:
                ost.center_y = SCREEN_HEIGHT + 100
                ost.center_x = random.randint(40, SCREEN_WIDTH - 40)

        if random.random() < 0.006:
            s = load_sprite_safe("scudo.png", 0.3)
            s.center_x = random.randint(50, 550); s.center_y = 650
            self.scudi_list.append(s)

        for s in self.scudi_list:
            s.center_y -= self.velocita_ostacoli
        
        hit_scudi = arcade.check_for_collision_with_list(self.player, self.scudi_list)
        if hit_scudi:
            for s in hit_scudi:
                s.remove_from_sprite_lists()
            self.scudo_attivo = True
            self.tempo_scudo = SCUDO_DURATION
            self.player.color = arcade.color.CYAN
            if self.scudo_sound and not self.scudo_player_audio:
                self.scudo_player_audio = arcade.play_sound(self.scudo_sound, looping=True)

        if self.scudo_attivo:
            self.tempo_scudo -= delta_time
            if self.tempo_scudo <= 0:
                self.scudo_attivo = False
                self.player.color = arcade.color.WHITE
                if self.scudo_player_audio:
                    arcade.stop_sound(self.scudo_player_audio)
                    self.scudo_player_audio = None

        if not self.scudo_attivo:
            if arcade.check_for_collision_with_list(self.player, self.ostacoli_list):
                self.game_over = True
                self.best_score = max(self.best_score, self.score)

    def on_key_press(self, key, modifiers):
        if self.stato_gioco == "MENU":
            if key == arcade.key.SPACE:
                self.setup()
                self.stato_gioco = "IN_CORSO"
            return

        if key == arcade.key.ESCAPE:
            if not self.game_over:
                self.paused = not self.paused
            return

        if self.paused:
            if key == arcade.key.R: self.paused = False
            if key == arcade.key.M:
                self.paused = False
                self.stato_gioco = "MENU"
            return

        if self.game_over and key == arcade.key.R:
            self.setup()

        if key in (arcade.key.W, arcade.key.UP): self.up_pressed = True
        if key in (arcade.key.S, arcade.key.DOWN): self.down_pressed = True
        if key in (arcade.key.A, arcade.key.LEFT): self.left_pressed = True
        if key in (arcade.key.D, arcade.key.RIGHT): self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP): self.up_pressed = False
        if key in (arcade.key.S, arcade.key.DOWN): self.down_pressed = False
        if key in (arcade.key.A, arcade.key.LEFT): self.left_pressed = False
        if key in (arcade.key.D, arcade.key.RIGHT): self.right_pressed = False

def main():
    NavicellaGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()