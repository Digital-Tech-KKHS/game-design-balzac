import arcade

class Interactable(arcade.Sprite):

    def interact(self):
        getattr(self, self.properties["oninteract"], self.not_implimented)()

    def body(self):
        print("ewww you touched a ded dude")

    def not_implimented(self):
        raise NotImplemented("object does not have oninteract in Tiled, check if spelled correctly.")

    def draw_text(self):
        self.show_text = True

    def draw(self):
        super().draw()
        if getattr(self, 'show_text', False):
                arcade.draw_text(
                self.properties["text"], 
                self.center_x, self.center_y + 100, 
                color=(255, 255, 255, 255),
                font_size=28, 
                font_name = 'Kenney Pixel'
            )


    