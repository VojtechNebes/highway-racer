import pygame, sys, random, json
from os.path import join

pygame.init()
pygame.font.init()

class Settings:
    def __init__(self):
        self.SCREEN_TITLE = "game"
        self.HIGHSCORE_TEXT_PREFIX = "Highscore: "
        
        self.PLAYER_SIZE = (44, 84)
        self.CAR_SIZE = (55, 80)
        self.ROAD_SIZE = (392, 336)
        
        displayInfo = pygame.display.Info()
        
        self.SCREEN_SIZE = (displayInfo.current_w, displayInfo.current_h)
        self.ROAD_X_OFFSET = (self.SCREEN_SIZE[0] - self.ROAD_SIZE[0])//2
        self.BACKGROUND_COLOR = (0, 0, 0)
        self.SCORE_ADD_TEXT_COLOR = (100, 255, 100)
        self.SCORE_TEXT_COLOR = (255, 0, 0)
        self.HIGHSCORE_TEXT_COLOR = (200, 200, 200)
        self.FPS = 60
        
        self.GAME_SPEED = 5 #pixels per frame, basically means 'player speed along Y axis'
        self.ROAD_ROWS = 4
        self.PLAYER_Y = self.SCREEN_SIZE[1] - self.PLAYER_SIZE[1] - 75 #pixels
        self.PLAYER_SPEED = 1 #pixels per frame (times GAME_SPEED)
        self.CAR_SPEED = 1.2 #pixels per frame (times GAME_SPEED)
        self.CAR_SPEED_RANDOM_ADD = 0.4 #pixels per frame (times GAME_SPEED)
        self.CAR_SPAWN_DELAY = 300 #frames (divided by GAME_SPEED)
        self.MAX_CARS_SPAWN_AT_ONCE = 2
        self.CAR_SPAWN_CHANCE = 25 #percentage
        self.SCORE_TEXT_BOTTOM_DIST = 20 #pixels
        self.SCORE_TEXT_BOTTOM_DIST_MAX = 100 #pixels
        self.SCORE_TEXT_SPEED = 0.2 #pixels per frame (times GAME_SPEED)

class Assets:
    def __init__(self, settings):
        self.player = pygame.transform.scale(pygame.image.load(join("Assets", "player.png")), settings.PLAYER_SIZE)
        self.car = pygame.transform.scale(pygame.image.load(join("Assets", "car.png")), settings.CAR_SIZE)
        self.road = pygame.transform.scale(pygame.image.load(join("Assets", "road.png")), settings.ROAD_SIZE)

class Game:
    def __init__(self):
        self.settings = Settings()
        self.assets = Assets(self.settings)
        
        self.screen = pygame.display.set_mode(self.settings.SCREEN_SIZE, pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
        try:
            with open(join("data.json"), "r") as file:
                data = json.load(file)
        except:
            self.highscore = 0
        else:
            self.highscore = data["highscore"]
        
        self.score = 0
        self.gameSpeed = self.settings.GAME_SPEED
        self.roadYOffset = 0
        self.playerX = self.settings.ROAD_SIZE[0]//2 - self.settings.PLAYER_SIZE[0]//2
        self.carSpawnWaited = 0
        self.carSpawnChanceArray = [i<=self.settings.CAR_SPAWN_CHANCE for i in range(100)]
        self.carSpawnPositions = [self.settings.ROAD_SIZE[0]//(self.settings.ROAD_ROWS) * (i+0.5) - self.settings.CAR_SIZE[0]//2 for i in range(self.settings.ROAD_ROWS)]
        self.cars = []
        self.scoreFont = pygame.font.SysFont("comicsans", 18)
        self.scoreAddFont = pygame.font.SysFont("comicsans", 25)
        self.highscoreFont = pygame.font.SysFont("comicsans", 35)
        self.scoreTexts = []
    
    def start(self):
        run = True
        while run:
            #events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            #keys
            keysPressed = pygame.key.get_pressed()
            
            if (keysPressed[pygame.K_d] or keysPressed[pygame.K_RIGHT]):
                self.playerX += min(self.settings.PLAYER_SPEED*int(self.gameSpeed), self.settings.ROAD_SIZE[0] - (self.playerX + self.settings.PLAYER_SIZE[0]))
            
            if (keysPressed[pygame.K_a] or keysPressed[pygame.K_LEFT]):
                self.playerX -= min(self.settings.PLAYER_SPEED*int(self.gameSpeed), self.playerX)
            
            if keysPressed[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            
            #background movement
            self.roadYOffset += int(self.gameSpeed)
            if self.roadYOffset >= self.settings.ROAD_SIZE[1]:
                self.roadYOffset = 0
            
            #score text movement
            for scoreText in self.scoreTexts:
                if scoreText[2] > self.settings.SCREEN_SIZE[1] - scoreTextRect.h - self.settings.SCORE_TEXT_BOTTOM_DIST_MAX:
                    scoreText[2] -= int(self.gameSpeed) * self.settings.SCORE_TEXT_SPEED
                else:
                    self.scoreTexts.remove(scoreText)
            
            #car spawning
            self.carSpawnWaited += int(self.gameSpeed)
            if self.carSpawnWaited >= self.settings.CAR_SPAWN_DELAY:
                self.carSpawnWaited = 0
                random.shuffle(self.carSpawnPositions)
                
                carsSpawnedNow = 0
                
                for xPos in self.carSpawnPositions:
                    if random.choice(self.carSpawnChanceArray) and carsSpawnedNow < self.settings.MAX_CARS_SPAWN_AT_ONCE:
                        newCarSpeed = self.settings.CAR_SPEED + random.randint(0, self.settings.CAR_SPEED_RANDOM_ADD*10)/10
                        
                        self.cars.append([xPos, -self.settings.ROAD_SIZE[1], newCarSpeed])
                        
                        carsSpawnedNow += 1
            
            #car movement
            for car in self.cars:
                if car[1] < self.settings.SCREEN_SIZE[1]:
                    if car[1] + self.settings.CAR_SIZE[1] > self.settings.PLAYER_Y and car[1] < self.settings.PLAYER_Y + self.settings.PLAYER_SIZE[1]:
                        if car[0] + self.settings.CAR_SIZE[0] > self.playerX and car[0] < self.playerX + self.settings.PLAYER_SIZE[0]:
                            self.gameSpeed = 0
                            
                            for i in range(6):
                                self.draw(False)
                                pygame.time.delay(150)
                                self.draw(True)
                                pygame.time.delay(150)
                            
                            run = False
                    
                    car[1] += int(self.gameSpeed) * car[2]
                else:
                    self.score += int(self.gameSpeed)
                    self.gameSpeed += 0.05
                    
                    scoreText = self.scoreAddFont.render(f"+{int(self.gameSpeed)}", 1, self.settings.SCORE_ADD_TEXT_COLOR)
                    scoreTextRect = scoreText.get_rect()
                    
                    self.scoreTexts.append([
                        scoreText,
                        car[0] + self.settings.CAR_SIZE[0]//2 - scoreTextRect.w//2,
                        self.settings.SCREEN_SIZE[1] - scoreTextRect.h - self.settings.SCORE_TEXT_BOTTOM_DIST
                    ])
                    
                    self.cars.remove(car)
            
            #clock ticking and drawing on the screen
            self.draw(True)
            self.clock.tick(self.settings.FPS)
        
        if self.score > self.highscore:
            with open(join("data.json"), "w") as file:
                json.dump({"highscore": self.score}, file)
    
    def draw(self, drawPlayer):
        self.screen.fill(self.settings.BACKGROUND_COLOR)
        
        for i in range(self.settings.SCREEN_SIZE[1]//self.settings.ROAD_SIZE[1] + 2):
            self.screen.blit(self.assets.road, (self.settings.ROAD_X_OFFSET, (i-1)*self.settings.ROAD_SIZE[1] + self.roadYOffset))
        
        for car in self.cars:
            self.screen.blit(self.assets.car, (self.settings.ROAD_X_OFFSET + car[0], car[1]))
        
        if drawPlayer:
            self.screen.blit(self.assets.player, (self.settings.ROAD_X_OFFSET + self.playerX, self.settings.PLAYER_Y))
        
        for scoreText in self.scoreTexts:
            self.screen.blit(scoreText[0], (self.settings.ROAD_X_OFFSET + scoreText[1], scoreText[2]))
        
        scoreText = self.scoreFont.render(str(self.score), 1, self.settings.SCORE_TEXT_COLOR)
        scoreTextRect = scoreText.get_rect()
        self.screen.blit(scoreText, ((
            self.settings.ROAD_X_OFFSET + self.playerX + self.settings.PLAYER_SIZE[0]//2 - scoreTextRect.w//2,
            self.settings.PLAYER_Y + self.settings.PLAYER_SIZE[1]//2 - scoreTextRect.h//2
        )))
        
        highscoreText = self.highscoreFont.render(self.settings.HIGHSCORE_TEXT_PREFIX+str(self.highscore), 1, self.settings.HIGHSCORE_TEXT_COLOR)
        self.screen.blit(highscoreText, (20, 20))
        
        pygame.display.update()

if __name__ == "__main__":
    while True:
        Game().start()