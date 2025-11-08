import pygame
from pygame.locals import *

import pygame.freetype

import math

#initial settings
pygame.init()

FPS = 30
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

        if value == math.floor(value):
            value = int(value)
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

        while self[0] >= 1000:
            self.value /= 1000
            self.thousand_power += 1
        while self[0] < 1 and self.thousand_power:
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

        while self[0] >= 1000:
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

    def shrink(self):
        self.shrunken = 1
        self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth * 0.9, self.SurfaceHeight * 0.9))
        self.rect = self.surface.get_rect()

    def fix_size(self):
        self.shrunken = 0
        self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth, self.SurfaceHeight))
        self.rect = self.surface.get_rect()

    def click(self):
        global Money
        Money.add(MoneyPerClick)

Current_Page = 1 #used to scroll through upgrade buttons

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

    fifth_surface, fifth_rect = TopTextFont.render(f"{Current_Page}", (255, 255, 255))
    fifth_rect.center = (825, 600)
    display.blit(fifth_surface, fifth_rect)

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
            self.surface = pygame.transform.scale(self.surface, (self.SurfaceWidth * 0.97, self.SurfaceHeight * 0.9))
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
        for j in self.buttons:
            j.update()

    def buy(self):
        for j in self.buttons:
            j.buy()

    def draw(self, surface):
        for j in self.buttons:
            j.draw(surface)

    def shrink(self):
        for j in self.buttons:
            j.shrink()

    def fix_size(self):
        for j in self.buttons:
            j.fix_size()


class OtherButton(pygame.sprite.Sprite):
    shrunken = 0
    ButtonWidth = 0
    ButtonHeight = 0
    def __init__(self, size:tuple[int, int], pos:tuple[int, int], image_name:str=None, text:str=None, text_size:int=20,
                 user_event:pygame.event.Event=None):
        super().__init__()
        self.size = size
        self.pos = pos
        self.image_name = image_name
        self.text = text
        self.font = pygame.freetype.Font(None, text_size)

        self.saved_surface = pygame.Surface(size)
        self.rect = self.saved_surface.fill((180, 180, 180))
        self.ButtonWidth, self.ButtonHeight = size

        if image_name:
            self.image = pygame.transform.scale(pygame.image.load(image_name), self.size)
            self.saved_surface.blit(self.image, self.image.get_rect())
        elif text:
            self.text_surface, self.text_rect = self.font.render(text, (255, 255, 255))
            self.text_rect.center = self.rect.center
            self.saved_surface.blit(self.text_surface, self.text_rect)

        if user_event:
            self.user_event = user_event

        self.surface = self.saved_surface.copy()

    def draw(self, surface):
        if not self.shrunken and self.text:
            self.saved_surface = pygame.Surface(self.size)
            self.rect = self.saved_surface.fill((180, 180, 180))
            self.text_surface, self.text_rect = self.font.render(self.text, (255, 255, 255))
            self.text_rect.center = self.rect.center
            self.saved_surface.blit(self.text_surface, self.text_rect)
            self.surface = self.saved_surface.copy()

        self.rect.center = self.pos
        surface.blit(self.surface, self.rect)

        if not self.shrunken:
            self.surface = self.saved_surface.copy()

    def press(self):
        if self.shrunken and self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.event.post(self.user_event)

    def shrink(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.shrunken = 1
            self.surface = pygame.transform.scale(self.saved_surface, (self.ButtonWidth * 0.9, self.ButtonHeight * 0.9))
            self.rect = self.surface.get_rect()
            self.rect.center = self.pos

    def fix_size(self):
        if self.shrunken:
            self.shrunken = 0
            self.surface = pygame.transform.scale(self.saved_surface, (self.ButtonWidth, self.ButtonHeight))
            self.rect = self.surface.get_rect()
            self.rect.center = self.pos


#game loop
Clock = pygame.time.Clock()

pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

MainCookie = Cookie()

#upgrades
Clicker = UpgradeButton("cursor.webp", 0, "Clicker", 1, 25)
Oven = UpgradeButton("oven.png", 1, "Oven", 5, 150)
Bakery = UpgradeButton("bakery.png", 2, "Bakery", 25, 1500)
Factory = UpgradeButton("factory.png", 3, "Factory", 100, 10, cost2=1)
Shipyard = UpgradeButton("shipyard.webp", 4, "Shipyard", 300, 100, cost2=1)
Page1 = Page(Clicker, Oven, Bakery, Factory, Shipyard)

Page2PlaceHold = UpgradeButton("Cookie.webp", 5, "Place Holder 1", 10, 0, cps2=1)
Page2PlaceHold2 = UpgradeButton("Cookie.webp", 6, "Place Holder 2", 10, 0, cps2=2)
Page2 = Page(Page2PlaceHold, Page2PlaceHold2)

Page3PlaceHold = UpgradeButton("Cookie.webp", 10, "Place Holder 3", 0, 1, cost2=2)
Page3PlaceHold2 = UpgradeButton("Cookie.webp", 11, "Place Holder 4", 0, 1, cost2=3)
Page3PlaceHold3= UpgradeButton("Cookie.webp", 12, "Place Holder 5", 0, 1, cost2=4)
Page3PlaceHold4= UpgradeButton("Cookie.webp", 13, "Place Holder 6", 0, 1, cost2=5)
Page3PlaceHold5= UpgradeButton("Cookie.webp", 14, "Place Holder 7", 0, 1, cost2=6)
Page3 = Page(Page3PlaceHold, Page3PlaceHold2, Page3PlaceHold3, Page3PlaceHold4, Page3PlaceHold5)

MaxPages = 3
PageDown_event = pygame.event.Event(USEREVENT + 0)
PageDownButton = OtherButton((40, 40), (775, 600), text="<", text_size=30, user_event=PageDown_event)
PageUp_event = pygame.event.Event(USEREVENT + 1)
PageUpButton = OtherButton((40, 40), (875, 600), text=">", text_size=30, user_event=PageUp_event)

UncapFPS_event = pygame.event.Event(USEREVENT + 2)
UncapFPS = OtherButton((140, 40), (int(display_width/2), 600), text="Uncap FPS" if FPS == 30 else "Cap FPS", text_size=20,
                       user_event=UncapFPS_event)

# MainCookie not included in arrays
SizeChangesWhenClicked =   [Page1]
NeedsUpdating =            [Page1]
NeedsDrawing = [MainCookie, Page1]

OtherButtons = [PageDownButton, PageUpButton, UncapFPS]
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
            for i in OtherButtons:
                i.shrink()

        if event.type == MOUSEBUTTONUP:
            if MainCookie.shrunken:
                MainCookie.fix_size()
                MainCookie.click()

            for i in SizeChangesWhenClicked:
                i.buy()
                i.fix_size()
            for i in OtherButtons:
                i.press()
                i.fix_size()

    if pygame.event.get(PageDown_event.type):
        Current_Page = MaxPages if Current_Page == 1 else Current_Page - 1

        if Current_Page == 1:
            SizeChangesWhenClicked = [Page1]
            NeedsUpdating = [Page1]
            NeedsDrawing = [MainCookie, Page1]
        elif Current_Page == 2:
            SizeChangesWhenClicked = [Page2]
            NeedsUpdating = [Page2]
            NeedsDrawing = [MainCookie, Page2]
        elif Current_Page == 3:
            SizeChangesWhenClicked = [Page3]
            NeedsUpdating = [Page3]
            NeedsDrawing = [MainCookie, Page3]

    elif pygame.event.get(PageUp_event.type):
        Current_Page = 1 if Current_Page == MaxPages else Current_Page + 1

        if Current_Page == 1:
            SizeChangesWhenClicked = [Page1]
            NeedsUpdating = [Page1]
            NeedsDrawing = [MainCookie, Page1]
        elif Current_Page == 2:
            SizeChangesWhenClicked = [Page2]
            NeedsUpdating = [Page2]
            NeedsDrawing = [MainCookie, Page2]
        elif Current_Page == 3:
            SizeChangesWhenClicked = [Page3]
            NeedsUpdating = [Page3]
            NeedsDrawing = [MainCookie, Page3]

    elif pygame.event.get(UncapFPS_event.type):
        UncapFPS.text = "Uncap FPS" if UncapFPS.text == "Cap FPS" else "Cap FPS"
        FPS = 30 if FPS == 0 else 0

    Display.fill((0, 0, 0))

    #add money since last tick
    if Cookies_per_second.value:
        Money.add(Cookies_per_second.__copy__().multiply( (Clock.tick(FPS) / 1000) ))
    else: #needed because cps can be 0, which somehow messes with Clock.get_fps()
        Clock.tick(FPS)

    for i in NeedsDrawing:
        i.draw(Display)
    for i in OtherButtons:
        i.draw(Display)

    draw_default_text(Display)

    pygame.display.update() #can update specific rect to improve performance
