import arcade
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Navicella - Schiva gli ostacoli"


class NavicellaGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.player = None
        self.player_list = arcade.SpriteList()
        self.ostacoli_list = arcade.SpriteList()

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        self.velocita_player = 4
        self.velocita_ostacoli = 2.0

        self.tempo_passato = 0.0
        self.game_over = False

        self.setup()

    def setup(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.player_list.clear()
        self.ostacoli_list.clear()

        self.player = arcade.Sprite("assets/navicella.png", scale=0.33)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 80
        self.player_list.append(self.player)

        self.velocita_ostacoli = 2.0
        self.tempo_passato = 0.0
        self.game_over = False

        for _ in range(5):
            self.crea_ostacolo()

    def crea_ostacolo(self):
        ostacolo = arcade.Sprite("assets/ostacolo.jpg", scale=0.4)
        ostacolo.center_x = random.randint(40, SCREEN_WIDTH - 40)
        ostacolo.center_y = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 400)
        self.ostacoli_list.append(ostacolo)

    def on_draw(self):
        self.clear()

        self.ostacoli_list.draw()
        self.player_list.draw()

        if self.game_over:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 20,
                arcade.color.RED,
                40,
                anchor_x="center",
                anchor_y="center"
            )

            arcade.draw_text(
                "Premi R per restart",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 30,
                arcade.color.RED,
                18,
                anchor_x="center",
                anchor_y="center"
            )

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.tempo_passato += delta_time

        if int(self.tempo_passato) != 0 and int(self.tempo_passato) % 60 == 0:
            self.velocita_ostacoli += 0.3
            self.tempo_passato += 1

        if self.up_pressed:
            self.player.center_y += self.velocita_player
        if self.down_pressed:
            self.player.center_y -= self.velocita_player
        if self.left_pressed:
            self.player.center_x -= self.velocita_player
            self.player.scale_x = -0.33
        if self.right_pressed:
            self.player.center_x += self.velocita_player
            self.player.scale_x = 0.33

        self.player.center_x = max(0, min(SCREEN_WIDTH, self.player.center_x))
        self.player.center_y = max(0, min(SCREEN_HEIGHT, self.player.center_y))

        for ostacolo in self.ostacoli_list:
            ostacolo.center_y -= self.velocita_ostacoli

            if ostacolo.center_y < -50:
                ostacolo.center_y = random.randint(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 300)
                ostacolo.center_x = random.randint(40, SCREEN_WIDTH - 40)

        if arcade.check_for_collision_with_list(self.player, self.ostacoli_list):
            self.game_over = True

    def on_key_press(self, key, modifiers):
        if self.game_over and key == arcade.key.R:
            self.setup()
            return

        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = True
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = True
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = False
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False


def main():
    game = NavicellaGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()