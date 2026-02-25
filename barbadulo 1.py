import arcade
import random
import os

# ======================
# COSTANTI
# ====================== 

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Navicella - Schiva gli ostacoli"

DISTANZA_OSTACOLI = 180
BOOST_DURATION = 5.0
BOOST_VELOCITA = 8
NUM_STELLE = 100
SCUDO_DURATION = 3.0
PORTALE_SPAWN_TIME = 10.0  # ogni 10 secondi

# ======================
# FUNZIONE SICURA CARICAMENTO SPRITE
# ======================
def load_sprite_safe(path, scale):
    if os.path.exists(path):
        return arcade.Sprite(path, scale=scale)
    else:
        sprite = arcade.SpriteSolidColor(50, 50, arcade.color.RED)
        sprite.scale = scale
        return sprite

# ======================
# GIOCO
# ======================
class NavicellaGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)

        self.player = None
        self.player_list = arcade.SpriteList()
        self.ostacoli_list = arcade.SpriteList()
        self.potenziamenti_list = arcade.SpriteList()
        self.scudi_list = arcade.SpriteList()
        self.portali_list = arcade.SpriteList()

        # input
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        # gameplay
        self.velocita_player = 4
        self.velocita_ostacoli = 2.0

        self.tempo_passato = 0
        self.score = 0
        self.best_score = 0
        self.tempo_punti = 0

        # ===== SCUDO =====
        self.scudo_attivo = False
        self.tempo_scudo = 0

        # ===== PORTALE =====
        self.tempo_portale = 0

        # 🔊 CARICAMENTO SUONO SICURO
        sound_path = os.path.join(os.path.dirname(__file__), "shield_on.mp3")

        if os.path.exists(sound_path):
            self.scudo_sound = arcade.load_sound(sound_path)
        else:
            print("⚠ shield_on.mp3 NON trovato")
            self.scudo_sound = None

        self.scudo_player = None

        self.game_over = False

        # stelle
        self.stelle = []
        for _ in range(NUM_STELLE):
            self.stelle.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.randint(1, 3),
                random.uniform(1, 3.5)
            ])

        self.setup()

    # ======================
    # SETUP
    # ======================
    def setup(self):

        self.player_list.clear()
        self.ostacoli_list.clear()
        self.potenziamenti_list.clear()
        self.scudi_list.clear()
        self.portali_list.clear()

        self.player = load_sprite_safe("navicella.png", 0.33)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 80
        self.player_list.append(self.player)

        self.velocita_ostacoli = 2
        self.velocita_player = 4

        self.score = 0
        self.tempo_punti = 0
        self.tempo_passato = 0
        self.tempo_portale = 0

        self.scudo_attivo = False
        self.tempo_scudo = 0
        self.player.color = arcade.color.WHITE

        self.game_over = False

        y_spawn = SCREEN_HEIGHT + 100
        for _ in range(5):
            ost = load_sprite_safe("ostacolo.png", 0.4)
            ost.center_x = random.randint(40, SCREEN_WIDTH - 40)
            ost.center_y = y_spawn
            self.ostacoli_list.append(ost)
            y_spawn += DISTANZA_OSTACOLI

    # ======================
    # DISEGNO
    # ======================
    def on_draw(self):
        self.clear()

        for s in self.stelle:
            arcade.draw_circle_filled(s[0], s[1], s[2], arcade.color.WHITE)

        self.ostacoli_list.draw()
        self.player_list.draw()
        self.potenziamenti_list.draw()
        self.scudi_list.draw()
        self.portali_list.draw()  # disegna i portali

        arcade.draw_text(f"Score: {self.score}", 10, 570,
                         arcade.color.WHITE, 16)

        arcade.draw_text(f"Best: {self.best_score}", 10, 545,
                         arcade.color.YELLOW, 16)

        if self.game_over:
            arcade.draw_text("GAME OVER",
                             SCREEN_WIDTH//2,
                             SCREEN_HEIGHT//2,
                             arcade.color.RED,
                             40,
                             anchor_x="center")

            arcade.draw_text("Premi R per restart",
                             SCREEN_WIDTH//2,
                             SCREEN_HEIGHT//2 - 40,
                             arcade.color.GREEN,
                             18,
                             anchor_x="center")

    # ======================
    # UPDATE
    # ======================
    def on_update(self, delta_time):

        if self.game_over:
            return

        # stelle
        for s in self.stelle:
            s[1] -= s[3]
            if s[1] < 0:
                s[0] = random.randint(0, SCREEN_WIDTH)
                s[1] = SCREEN_HEIGHT

        # spawn scudo casuale
        if random.random() < 0.002:
            scudo = load_sprite_safe("scudo.png", 0.25)
            scudo.center_x = random.randint(40, SCREEN_WIDTH - 40)
            scudo.center_y = SCREEN_HEIGHT
            self.scudi_list.append(scudo)

        # spawn portale ogni 10 secondi
        self.tempo_portale += delta_time
        if self.tempo_portale >= PORTALE_SPAWN_TIME:
            self.tempo_portale = 0
            portale = load_sprite_safe("portale.png", 0.4)
            portale.center_x = random.randint(40, SCREEN_WIDTH - 40)
            portale.center_y = SCREEN_HEIGHT
            self.portali_list.append(portale)

        # movimento player
        speed = self.velocita_player

        if self.up_pressed:
            self.player.center_y += speed
        if self.down_pressed:
            self.player.center_y -= speed
        if self.left_pressed:
            self.player.center_x -= speed
            self.player.scale_x = -0.33
        if self.right_pressed:
            self.player.center_x += speed
            self.player.scale_x = 0.33

        # limiti schermo
        self.player.center_x = max(
            self.player.width/2,
            min(SCREEN_WIDTH - self.player.width/2, self.player.center_x)
        )

        self.player.center_y = max(
            self.player.height/2,
            min(SCREEN_HEIGHT - self.player.height/2, self.player.center_y)
        )

        # movimento ostacoli
        for ost in self.ostacoli_list:
            ost.center_y -= self.velocita_ostacoli
            if ost.center_y < -50:
                max_y = max(o.center_y for o in self.ostacoli_list)
                ost.center_y = max_y + DISTANZA_OSTACOLI
                ost.center_x = random.randint(40, SCREEN_WIDTH - 40)

        # movimento scudi
        for scudo in self.scudi_list:
            scudo.center_y -= self.velocita_ostacoli
            if scudo.center_y < -50:
                scudo.kill()

        # movimento portali
        for portale in self.portali_list:
            portale.center_y -= self.velocita_ostacoli
            if portale.center_y < -50:
                portale.kill()

        # raccolta scudo
        raccolti_scudo = arcade.check_for_collision_with_list(
            self.player, self.scudi_list)

        for s in raccolti_scudo:
            s.kill()
            self.scudo_attivo = True
            self.tempo_scudo = 0
            self.player.color = arcade.color.AZURE

            # 🔊 suono
            if self.scudo_sound:
                self.scudo_player = arcade.play_sound(self.scudo_sound)

        # timer scudo
        if self.scudo_attivo:
            self.tempo_scudo += delta_time
            if self.tempo_scudo >= SCUDO_DURATION:
                self.scudo_attivo = False
                self.player.color = arcade.color.WHITE
                if self.scudo_player:
                    arcade.stop_sound(self.scudo_player)

        # collisione
        if (not self.scudo_attivo and
                arcade.check_for_collision_with_list(
                    self.player, self.ostacoli_list)):
            self.game_over = True
            self.best_score = max(self.best_score, self.score)

    # ======================
    # INPUT
    # ======================
    def on_key_press(self, key, modifiers):

        if self.game_over and key == arcade.key.R:
            self.setup()
            return

        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = True
        if key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = True
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True

    def on_key_release(self, key, modifiers):

        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = False
        if key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = False
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False


# ======================
# MAIN
# ======================
def main():
    NavicellaGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()