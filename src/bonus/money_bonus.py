from .base_bonus import BaseBonus

class MoneyBonus(BaseBonus):
    def __init__(self, x, y, amount):
        super().__init__(x, y, "assets/sprites/money_bonus.png", (255, 215, 0), (24, 24))
        self.amount = amount
    def apply(self, player, game_context=None):
        if hasattr(player, 'money'):
            player.money += self.amount
        else:
            player.money = self.amount

class MoneyBonus10(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 10)

class MoneyBonus50(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 50)

class MoneyBonus100(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 100)

class MoneyBonus200(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 200)
