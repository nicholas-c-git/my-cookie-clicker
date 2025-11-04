import math

import pygame
from pygame.locals import *

import pygame.freetype


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


#global variables and classes
Money = 0 #the points of this game
MoneyPerClick = 1
Cookies_per_second = 0

class Cookie(pygame.sprite.Sprite):
    small = 0  # possible minor performance improver
    SurfaceWidth = CookieImage.get_width()
    SurfaceHeight = CookieImage.get_height()

    def __init__(self):
        super().__init__()
        self.surface = CookieImage

    def click(self):
        global Money
        Money += MoneyPerClick

    def draw(self, surface):
        self.rect = self.surface.get_rect()
        self.rect.center = (int(display_width / 2), int(display_height / 2))
        surface.blit(self.surface, self.rect)

        #clean up the sprite, prevents pixelation after repeated size changes
        if not self.small:
            self.surface = CookieImage

TopTextFont = pygame.freetype.Font(None, 30)
SecondTextFont = pygame.freetype.Font(None, 25)
FPS_Font = pygame.freetype.Font(None, 20)
class TopText:
    def draw(self, surface):
        self.surface, self.rect = TopTextFont.render(f"Cookies made: {math.floor(Money)}", (255, 255, 255))
        self.rect.center = (int(display_width/2), 100)
        surface.blit(self.surface, self.rect)

        self.second_surface, self.second_rect = SecondTextFont.render(f"Cookies per second: {Cookies_per_second}",
                                                                      (255, 255, 255))
        self.second_rect.center = (int(display_width/2), 140)
        surface.blit(self.second_surface, self.second_rect)

        self.third_surface, self.third_rect = SecondTextFont.render(f"Cookies per click: {MoneyPerClick}",
                                                                    (255, 255, 255))
        self.third_rect.center = (int(display_width/2), 170)
        surface.blit(self.third_surface, self.third_rect)

        self.fourth_surface, self.fourth_rect = FPS_Font.render(f"fps: {round(Clock.get_fps(), 1)}",
                                                                    (255, 255, 255))
        self.fourth_rect.center = (int(display_width / 2), 675)
        surface.blit(self.fourth_surface, self.fourth_rect)

UpgradeButtonFont = pygame.freetype.Font(None, 20)
UpgradeButtonSecondaryFont = pygame.freetype.Font(None, 15)
AmountFont = pygame.freetype.Font(None, 50)
ButtonWidth = 300
ButtonHeight = 100
class UpgradeButton(pygame.sprite.Sprite):
    #local variables
    small = 0
    NameColor = (255, 255, 255)
    ButtonColor = (180, 180, 180)

    def __init__(self, image_name, upgrade_ID, name, cps, cost):
        super().__init__()
        self.ButtonNumber = upgrade_ID
        self.cps = cps
        self.cost = cost
        self.X: int = display_width - ButtonWidth
        self.Y: int = upgrade_ID * ButtonHeight
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
        if Money >= self.cost:
            self.CostColor = (255, 255, 255)
        else:
            self.CostColor = (255, 0, 0)

        if not self.small: #when self.small, a copy of the button is shown

        #show cps, cost, and amount
            self.cps_surface, _ = UpgradeButtonSecondaryFont.render(f"Cps: {str(self.cps)}", self.NameColor)
            self.surface.blit(self.cps_surface, (self.image.get_width() + 5, 32))

            self.cost_surface, _ = UpgradeButtonSecondaryFont.render(f"cost: {str(self.cost)} cookies", self.CostColor)
            self.surface.blit(self.cost_surface, (self.image.get_width() + 5, 50))

            self.amount_surface, _ = AmountFont.render(str(self.amount), self.NameColor)
            self.surface.blit(self.amount_surface, (self.surface.get_width() - self.amount_surface.get_width() - 5, 5))

    def buy(self):
        global Money
        global Cookies_per_second
        if Money >= self.cost and not self.small:
            Money = max(Money - self.cost, 0)
            Cookies_per_second += self.cps
            self.amount += 1
            self.cost = math.floor( self.cost * 1.1 / math.sqrt(1.1) )

    def draw(self, surface):
        self.rect = self.surface.get_rect()
        self.rect.center = (int(display_width - self.SurfaceWidth/2),
                            int(self.SurfaceHeight/2 + self.ButtonNumber * self.SurfaceHeight) )
        surface.blit(self.surface, self.rect)

        #refresh the displayed surface, turns pixelated after repeated clicks otherwise
        #executed after surface.blit as to not disturb game loop size changes
        if not self.small:
            self.surface: pygame.Surface = self.saved_surface.copy()


#game loop
Clock = pygame.time.Clock()

pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

MoneyCounter = TopText()
MainCookie = Cookie()

#upgrades
Clicker = UpgradeButton("cursor.webp", 0, "Clicker", 1, 25)
Oven = UpgradeButton("oven.png", 1, "Oven", 5, 150)
Bakery = UpgradeButton("bakery.png", 2, "Bakery", 25, 1500)
Factory = UpgradeButton("factory.png", 3, "Factory", 100, 10000)
Shipyard = UpgradeButton("shipyard.webp", 4, "Shipyard", 300, 99000)



SizeChangesWhenClicked =     [MainCookie, Clicker, Oven, Bakery, Factory, Shipyard]
NeedsUpdating =                          [Clicker, Oven, Bakery, Factory, Shipyard]
NeedsDrawing = [MoneyCounter, MainCookie, Clicker, Oven, Bakery, Factory, Shipyard]
while 1:

    for i in NeedsUpdating:
        i.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

        # these pairs need to be in the game loop because there is no detection of MOUSEBUTTONUP without using events
        if event.type == MOUSEBUTTONDOWN:
            for i in SizeChangesWhenClicked:
                if not i.small and i.rect.collidepoint(pygame.mouse.get_pos()):
                    i.surface = pygame.transform.scale(i.surface,(i.SurfaceWidth * 0.95, i.SurfaceHeight * 0.9))
                    i.rect = i.surface.get_rect()
                    i.small = 1

        if event.type == MOUSEBUTTONUP:
            for i in SizeChangesWhenClicked:
                if i.small:
                    i.surface = pygame.transform.scale(i.surface, (i.SurfaceWidth, i.SurfaceHeight))
                    i.rect = i.surface.get_rect()
                    i.small = 0
                    if i != MainCookie:
                        i.buy()
                    else:
                        i.click()

    Display.fill((0, 0, 0))

    #add money since last tick
    Money += Cookies_per_second / 1000 * Clock.tick(30) #run game at 30 fps

    for i in NeedsDrawing:
        i.draw(Display)

    pygame.display.update() #can update specific rect to improve performance