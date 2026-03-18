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

# ======================
def load_sprite_safe(path, scale):
    if os.path.exists(path):
        return arcade.Sprite(path, scale=scale)
    else:
        sprite = arcade.SpriteSolidColor(50, 50, arcade.color.RED)
        sprite.scale = scale
        return sprite

# ======================
class NavicellaGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        # 🔊 SUONO SCUDO (LOOP)
        sound_path = "freesound_community-space-ship-bridge-loop-104525.mp3"
        if os.path.exists(sound_path):
            self.scudo_sound = arcade.load_sound(sound_path)
        else:
            print("⚠ Suono scudo NON trovato")
            self.scudo_sound = None
        self.scudo_player_audio = None

        self.player = None
        self.player_list = arcade.SpriteList()
        self.ostacoli_list = arcade.SpriteList()
        self.potenziamenti_list = arcade.SpriteList()
        self.scudi_list = arcade.SpriteList()

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        self.velocita_player = 4
        self.velocita_ostacoli = 3.0

        self.score = 0
        self.best_score = 0
        self.tempo_punti = 0
        self.prossimo_aumento = 60

        # SCUDO
        self.scudo_attivo = False
        self.tempo_scudo = 0

        # BOOST
        self.boost_attivo = False
        self.tempo_boost = 0

        self.game_over = False

        # PAUSA / MENU
        self.paused = False
        self.menu_options = ["RIPRENDI", "RICOMINCIA"]
        self.menu_index = 0

        # Stelle di sfondo
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
    def setup(self):
        self.player_list.clear()
        self.ostacoli_list.clear()
        self.potenziamenti_list.clear()
        self.scudi_list.clear()

        self.player = arcade.Sprite("navicella.png", scale=0.33)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 80
        self.player_list.append(self.player)

        self.velocita_ostacoli = 2
        self.velocita_player = 4

        self.score = 0
        self.tempo_punti = 0
        self.prossimo_aumento = 60

        self.scudo_attivo = False
        self.boost_attivo = False
        self.player.color = arcade.color.WHITE

        if self.scudo_player_audio:
            arcade.stop_sound(self.scudo_player_audio)
            self.scudo_player_audio = None

        self.game_over = False
        self.paused = False
        self.menu_index = 0

        y_spawn = SCREEN_HEIGHT + 100
        for _ in range(5):
            ost = load_sprite_safe("ostacolo.png", 0.4)
            ost.center_x = random.randint(40, SCREEN_WIDTH - 40)
            ost.center_y = y_spawn
            self.ostacoli_list.append(ost)
            y_spawn += DISTANZA_OSTACOLI

    # ======================
    def on_draw(self):
        self.clear()

        # Stelle di sfondo
        for s in self.stelle:
            arcade.draw_circle_filled(s[0], s[1], s[2], arcade.color.WHITE)

        self.ostacoli_list.draw()
        self.player_list.draw()
        self.scudi_list.draw()
        self.potenziamenti_list.draw()

        # 🛡️ BARRA SCUDO (versione moderna)
        if self.scudo_attivo:
            percentuale = self.tempo_scudo / SCUDO_DURATION
            larghezza = max(1, 40 * percentuale)
            rect = arcade.XYWH(self.player.center_x, self.player.center_y + 40, larghezza, 6)
            arcade.draw_rect_filled(rect, arcade.color.CYAN)

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

        # MENU PAUSA
        if self.paused:
            arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 300, 200, arcade.color.DARK_GRAY)
            arcade.draw_text("PAUSA", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70, arcade.color.WHITE, 30, anchor_x="center")
            for i, option in enumerate(self.menu_options):
                color = arcade.color.YELLOW if i == self.menu_index else arcade.color.WHITE
                arcade.draw_text(option, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20 - i*50, color, 20, anchor_x="center")

    # ======================
    def on_update(self, delta_time):
        if self.paused or self.game_over:
            return

        # Aggiornamento punti
        self.tempo_punti += delta_time
        if self.tempo_punti >= 3.0:
            self.score += 10
            self.tempo_punti = 0

        if self.score >= self.prossimo_aumento:
            self.velocita_ostacoli += 0.5
            self.prossimo_aumento += 60

        # Stelle
        for s in self.stelle:
            s[1] -= s[3]
            if s[1] < 0:
                s[0] = random.randint(0, SCREEN_WIDTH)
                s[1] = SCREEN_HEIGHT

        # Movimento player
        if self.up_pressed: self.player.center_y += self.velocita_player
        if self.down_pressed: self.player.center_y -= self.velocita_player
        if self.left_pressed: self.player.center_x -= self.velocita_player
        if self.right_pressed: self.player.center_x += self.velocita_player

        self.player.center_x = max(20, min(SCREEN_WIDTH - 20, self.player.center_x))
        self.player.center_y = max(20, min(SCREEN_HEIGHT - 20, self.player.center_y))

        # Ostacoli
        for ost in self.ostacoli_list:
            ost.center_y -= self.velocita_ostacoli
            if ost.center_y < -50:
                ost.center_y = SCREEN_HEIGHT + 100
                ost.center_x = random.randint(40, SCREEN_WIDTH - 40)

        # SCUDI
        if random.random() < 0.005:
            scudo = load_sprite_safe("scudo.png", 0.3)
            scudo.center_x = random.randint(40, SCREEN_WIDTH - 40)
            scudo.center_y = SCREEN_HEIGHT + 50
            self.scudi_list.append(scudo)

        for scudo in self.scudi_list:
            scudo.center_y -= self.velocita_ostacoli
            if scudo.center_y < -50:
                scudo.remove_from_sprite_lists()

        collected = arcade.check_for_collision_with_list(self.player, self.scudi_list)
        for scudo in collected:
            scudo.remove_from_sprite_lists()
            self.scudo_attivo = True
            self.tempo_scudo = SCUDO_DURATION
            self.player.color = arcade.color.CYAN
            if self.scudo_sound:
                if self.scudo_player_audio:
                    arcade.stop_sound(self.scudo_player_audio)
                self.scudo_player_audio = arcade.play_sound(self.scudo_sound, looping=True)

        if self.scudo_attivo:
            self.tempo_scudo -= delta_time
            if self.tempo_scudo <= 0:
                self.scudo_attivo = False
                self.player.color = arcade.color.WHITE
                if self.scudo_player_audio:
                    arcade.stop_sound(self.scudo_player_audio)
                    self.scudo_player_audio = None

        # BOOST
        if random.random() < 0.004:
            pot = load_sprite_safe("boost.png", 0.3)
            pot.center_x = random.randint(40, SCREEN_WIDTH - 40)
            pot.center_y = SCREEN_HEIGHT + 50
            self.potenziamenti_list.append(pot)

        for pot in self.potenziamenti_list:
            pot.center_y -= self.velocita_ostacoli
            if pot.center_y < -50:
                pot.remove_from_sprite_lists()

        collected = arcade.check_for_collision_with_list(self.player, self.potenziamenti_list)
        for pot in collected:
            pot.remove_from_sprite_lists()
            self.boost_attivo = True
            self.tempo_boost = BOOST_DURATION
            self.velocita_player = BOOST_VELOCITA

        if self.boost_attivo:
            self.tempo_boost -= delta_time
            if self.tempo_boost <= 0:
                self.boost_attivo = False
                self.velocita_player = 4

        if not self.scudo_attivo:
            if arcade.check_for_collision_with_list(self.player, self.ostacoli_list):
                self.game_over = True
                self.best_score = max(self.best_score, self.score)

    # ======================
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            self.menu_index = 0
            return

        if self.paused:
            if key == arcade.key.UP:
                self.menu_index = (self.menu_index - 1) % len(self.menu_options)
            elif key == arcade.key.DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.menu_options)
            elif key == arcade.key.ENTER:
                if self.menu_index == 0:  # Riprendi
                    self.paused = False
                elif self.menu_index == 1:  # Ricomincia
                    self.setup()
            return

        if self.game_over and key == arcade.key.R:
            self.setup()

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
def main():
    NavicellaGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()