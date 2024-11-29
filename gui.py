class GuiTokens:

    def __init__(self):
        self.gui_tokens = []

    def add(self, ui_token):
        self.gui_tokens.append(ui_token)

    def hit(self, x, y):
        for ui_token in self.gui_tokens:
            if ui_token.contains(x, y):
                return ui_token.token


class GuiToken:

    def __init__(self, rectangle, token):
        self.rectangle = rectangle
        self.token = token

    def contains(self, x, y):
        return self.rectangle.contains(x, y)


class Rectangle:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, x, y):
        return (self.x <= x <= (self.x + self.width)) and (
            self.y <= y <= (self.y + self.height)
        )
