import pygame
from pygame.locals import *

import pygame.freetype

import math

#initial settings
#fps set in the game loop
pygame.init()

display_width = 1000
display_height = 700
Display = pygame.display.set_mode( [display_width,display_height] )
Display.fill( (0, 0, 0) )

pygame.display.set_caption("Cookie Clicker")

CookieImageFileName = "Cookie.webp" #Minecraft cookie sprite
CookieImage = pygame.image.load(CookieImageFileName)
pygame.display.set_icon(CookieImage)

BigNumberMap = {0:"", 1:"thousand", 2:"million", 3:"billion", 4:"trillion", 5:"quadrillion", 6:"quintillion"}
class BigNumber:
    def __init__(self, value: float = 0, thousand_power: int = 0):
        while value >= 1000:
            value /= 1000
            thousand_power += 1

        self.value = value
        self.thousand_power = thousand_power

    def __getitem__(self, item: int = None):
        if item is None:
            return self.value, self.thousand_power
        return [self.value, self.thousand_power][item]

    def __str__(self):
        if self.thousand_power > 6:
            return "too many"
        return f"{round(self.value, 2)} {BigNumberMap.get(self.thousand_power) or ""}"

    def __copy__(self):
        return BigNumber(self.value, self.thousand_power)

    def compare(self, other_Number: 'BigNumber'):
        #self greater than or equal to other_Number
        if other_Number[1] > self[1]:
            return 0
        elif other_Number[1] < self[1]:
            return 1

        return other_Number[0] <= self[0]

    def add(self, other_Number: 'BigNumber'):
        if other_Number[1] == self[1]:
            self.value += other_Number[0]
        elif other_Number[1] < self[1]:
            self.value = other_Number[0] + self.value * math.pow(1000, (self.thousand_power - other_Number[1]) )
            self.thousand_power = other_Number[1]
        elif other_Number[1] > self[1]:
            self.value = self.value + other_Number[0] * math.pow(1000, (other_Number[1]) - self.thousand_power)

        if self[0] >= 1000:
            self.value /= 1000
            self.thousand_power += 1
        elif self[0] < 1 and self.thousand_power:
            self.value *= 1000
            self.thousand_power -= 1

        return self

    def sub(self, other_Number: 'BigNumber'):
        #doesn't go to negatives, gives an error
        if (other_Number[1] > self[1]) or (other_Number[1] == self[1] and other_Number[0] > self[0]):
            print(f"Error, subtracted larger from lower")
            pygame.quit()

        while self[1] > other_Number[1]:
            self.value *= 1000
            self.thousand_power -= 1
        self.value -= other_Number[0]

        while self[0] >= 1000 and self.thousand_power:
            self.value /= 1000
            self.thousand_power += 1

        return self

    def multiply(self, num: float):
        self.value *= num

        while self[0] >= 1000:
            self.value /= 1000
            self.thousand_power += 1
        return self

    def floor(self):
        return BigNumber(math.floor(self.value), self.thousand_power)


#global variables, game classes and methods
Money = BigNumber(0, 0) #called cookies in game
MoneyPerClick = BigNumber(1, 0)
Cookies_per_second = BigNumber(0, 0)

class Cookie(pygame.sprite.Sprite):
    shrunken = 0  # possible minor performance improver
    SurfaceWidth = CookieImage.get_width()
    SurfaceHeight = CookieImage.get_height()

    def __init__(self):
        super().__init__()
        self.surface = CookieImage
        self.rect = self.surface.get_rect()

    def draw(self, surface):
        self.rect = self.surface.get_rect()
        self.rect.center = (int(display_width / 2), int(display_height / 2))
        surface.blit(self.surface, self.rect)

        #clean up the sprite, prevents pixelation after repeated size changes
        if not self.shrunken:
            self.surface = CookieImage

    def check_size(self):
        return self.shrunken

    def shrink(self):
        self.shrunken = 1
        self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth * 0.95, self.SurfaceHeight * 0.9))
        self.rect = self.surface.get_rect()
    def fix_size(self):
        self.shrunken = 0
        self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth, self.SurfaceHeight))
        self.rect = self.surface.get_rect()

def click():
    global Money
    Money.add(MoneyPerClick)

TopTextFont = pygame.freetype.Font(None, 30)
SecondTextFont = pygame.freetype.Font(None, 20)
FPS_Font = pygame.freetype.Font(None, 20)
def draw_default_text(display):
    surface1, rect1 = TopTextFont.render(f"Cookies made:", (255, 255, 255))
    rect1.center = (int(display_width / 2), 50)
    display.blit(surface1, rect1)

    if Money.thousand_power:
        surface, rect = TopTextFont.render(f"{str(Money)}", (255, 255, 255))
    else:
        surface, rect = TopTextFont.render(f"{str(Money.floor())}", (255, 255, 255))
    rect.center = (int(display_width / 2), 85)
    display.blit(surface, rect)

    second_surface1, second_rect1 = SecondTextFont.render(f"Cookies per second:",
                                                                  (255, 255, 255))
    second_rect1.center = (int(display_width/2), 140)
    display.blit(second_surface1, second_rect1)

    if Cookies_per_second.thousand_power:
        second_surface, second_rect = SecondTextFont.render(f"{str(Cookies_per_second)}",
                                                                      (255, 255, 255))
    else:
        second_surface, second_rect = SecondTextFont.render(f"{str(Cookies_per_second.floor())}",
                                                                      (255, 255, 255))
    second_rect.center = (int(display_width/2), 165)
    display.blit(second_surface, second_rect)

    if MoneyPerClick.thousand_power:
        third_surface, third_rect = SecondTextFont.render(f"Cookies per click: {str(MoneyPerClick)}",
                                                                    (255, 255, 255))
    else:
        third_surface, third_rect = SecondTextFont.render(f"Cookies per click: {str(MoneyPerClick.floor())}",
                                                                    (255, 255, 255))
    third_rect.center = (int(display_width/2), 200)
    display.blit(third_surface, third_rect)

    fourth_surface, fourth_rect = FPS_Font.render(f"fps: {round(Clock.get_fps(), 1)}",
                                                                (255, 255, 255))
    fourth_rect.center = (int(display_width/2), 675)
    display.blit(fourth_surface, fourth_rect)

UpgradeButtonFont = pygame.freetype.Font(None, 20)
UpgradeButtonSecondaryFont = pygame.freetype.Font(None, 15)
AmountFont = pygame.freetype.Font(None, 50)
ButtonWidth = 300
ButtonHeight = 100
class UpgradeButton(pygame.sprite.Sprite):
    #local variables
    shrunken = 0
    NameColor = (255, 255, 255)
    ButtonColor = (180, 180, 180)

    def __init__(self, image_name:str, upgrade_id:int, name:str, cps:int, cost:int, cps2:int=0, cost2:int=0):
        super().__init__()
        self.ButtonNumber = upgrade_id
        self.cps = BigNumber(cps, cps2)
        self.cost = BigNumber(cost, cost2)
        self.X: int = display_width - ButtonWidth
        self.Y: int = upgrade_id * ButtonHeight
        self.amount = 0

        #make a new Surface that will be the button
        self.saved_surface: pygame.Surface = pygame.Surface( (ButtonWidth, ButtonHeight) )
        self.rect: pygame.Rect = self.saved_surface.fill(self.ButtonColor)
        self.SurfaceWidth: int = self.rect.width
        self.SurfaceHeight: int = self.rect.height

        #load the image onto the button
        self.image: pygame.Surface = pygame.transform.scale(pygame.image.load(image_name), (ButtonHeight, ButtonHeight))
        self.saved_surface.blit(self.image, self.rect)

        #load button name onto the button
        self.ButtonName = name
        self.text_surface, _ = UpgradeButtonFont.render(self.ButtonName, self.NameColor)
        self.saved_surface.blit(self.text_surface, (self.image.get_width() + 5, 10))

        #initializing self.surface, explained in draw()
        self.surface: pygame.Surface = self.saved_surface.copy()
        self.rect = self.surface.get_rect()

    def update(self):
        #set the cost color and show it on the button
        if Money.compare(self.cost):
            cost_color = (255, 255, 255)
        else:
            cost_color = (255, 0, 0)

        if not self.shrunken: #when not normal size, a copy of the button is shown

            #show cps, cost, and amount
            if self.cps.thousand_power:
                cps_surface, _ = UpgradeButtonSecondaryFont.render(f"Cps: {str(self.cps)}", self.NameColor)
                self.surface.blit(cps_surface, (self.image.get_width() + 5, 32))
            else:
                cps_surface, _ = UpgradeButtonSecondaryFont.render(f"Cps: {str(self.cps.floor())}", self.NameColor)
                self.surface.blit(cps_surface, (self.image.get_width() + 5, 32))

            if self.cost.thousand_power:
                cost_surface, _ = UpgradeButtonSecondaryFont.render(f"cost: {str(self.cost)} cookies", cost_color)
                self.surface.blit(cost_surface, (self.image.get_width() + 5, 50))
            else:
                cost_surface, _ = UpgradeButtonSecondaryFont.render(f"cost: {str(self.cost.floor())} cookies", cost_color)
                self.surface.blit(cost_surface, (self.image.get_width() + 5, 50))

            amount_surface, _ = AmountFont.render(str(self.amount), self.NameColor)
            self.surface.blit(amount_surface, (self.surface.get_width() - amount_surface.get_width() - 5, 5))

    def buy(self):
        if self.shrunken and self.rect.collidepoint(pygame.mouse.get_pos()):
            global Money
            if Money.compare(self.cost):
                global Cookies_per_second
                Money.sub(self.cost)
                Cookies_per_second.add(self.cps)
                self.amount += 1
                self.cost.multiply(1.1/math.sqrt(1.1))

    def draw(self, surface):
        self.rect.center = (int(display_width - self.SurfaceWidth/2),
                            int(self.SurfaceHeight/2 + self.ButtonNumber * self.SurfaceHeight)
                                                                                            % (self.SurfaceHeight * 5) )
        surface.blit(self.surface, self.rect)

        #refresh the displayed surface, turns pixelated after repeated clicks otherwise
        #executed after surface.blit as to not disturb game loop size changes
        if not self.shrunken:
            self.surface: pygame.Surface = self.saved_surface.copy()

    def shrink(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.shrunken = 1
            self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth * 0.95, self.SurfaceHeight * 0.9))
            self.rect = self.surface.get_rect()

    def fix_size(self):
        if self.shrunken:
            self.shrunken = 0
            self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth, self.SurfaceHeight))
            self.rect = self.surface.get_rect()

class Page:
    def __init__(self, *args:UpgradeButton):
        self.buttons = args

    def update(self):
        for i in self.buttons:
            i.update()

    def buy(self):
        for i in self.buttons:
            i.buy()

    def draw(self, surface):
        for i in self.buttons:
            i.draw(surface)

    def shrink(self):
        for i in self.buttons:
            i.shrink()

    def fix_size(self):
        for i in self.buttons:
            i.fix_size()

#game loop
Clock = pygame.time.Clock()

pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

MainCookie = Cookie()

#upgrades
Clicker = UpgradeButton("cursor.webp", 0, "Clicker", 1, 25)
Oven = UpgradeButton("oven.png", 1, "Oven", 5, 150)
Bakery = UpgradeButton("bakery.png", 2, "Bakery", 25, 1500)
Factory = UpgradeButton("factory.png", 3, "Factory", 100, 10000)
Shipyard = UpgradeButton("shipyard.webp", 4, "Shipyard", 300, 99000)
Page1 = Page(Clicker, Oven, Bakery, Factory, Shipyard)

# MainCookie not included in arrays
SizeChangesWhenClicked =   [Page1]
NeedsUpdating =            [Page1]
NeedsDrawing = [MainCookie, Page1]
while 1:

    for i in NeedsUpdating:
        i.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

        # these pairs need to be in the game loop because there is no detection of MOUSEBUTTONUP without using events
        if event.type == MOUSEBUTTONDOWN:
            if MainCookie.rect.collidepoint(pygame.mouse.get_pos()) and not MainCookie.shrunken:
                MainCookie.shrink()

            for i in SizeChangesWhenClicked:
                i.shrink()

        if event.type == MOUSEBUTTONUP:
            if MainCookie.shrunken:
                MainCookie.fix_size()
                click()

            for i in SizeChangesWhenClicked:
                i.buy()
                i.fix_size()

    Display.fill((0, 0, 0))

    #add money since last tick
    if Cookies_per_second.value:
        Money.add(Cookies_per_second.__copy__().multiply( (Clock.tick(30) / 1000) ))
    else:
        Clock.tick(30) #run game at 30 fps

    for i in NeedsDrawing:
        i.draw(Display)

    draw_default_text(Display)

    pygame.display.update() #can update specific rect to improve performance
