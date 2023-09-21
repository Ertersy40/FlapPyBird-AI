import asyncio
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Floor,
    Pipes,
    Player,
    PlayerMode,
    Score
)

from .utils import GameConfig, Images, Sounds, Window, Neural_Network

class Bird:
    def __init__(self) -> None:
        self.brain = Neural_Network.Network([4, 1])

    def toFlapOrNotToFlap(self, y=0, y_vel=0, pipeHeight=400, pipeDist=250):
        flapPercent = self.brain.forward_propagate([y, y_vel, pipeHeight, pipeDist])[0]
        return flapPercent


class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )

    async def start(self):
        FlappyBoisPerGen = 200
        while True:
            self.birds = [Bird() for _ in range(FlappyBoisPerGen)]
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.players = [Player(self.config) for _ in range(FlappyBoisPerGen)]
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)

            await self.play()
 

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    async def play(self):
        self.score.reset()
        for player in self.players:
            player.set_mode(PlayerMode.NORMAL)

        while True:
            for index, player in enumerate(self.players):
                if player.collided(self.pipes, self.floor):
                    #Remove player and bird from list
                    self.birds.pop(index)
                    self.players.pop(index)

            #If there are no more players left, start again
            if not self.players:
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.players[0].crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)
                

            firstPipe = self.pipes.lower[0]
            pipeGap = self.pipes.pipe_gap
            if len(self.pipes.upper) == 1 or self.players[0].x < firstPipe.x:
                pipeHeight = firstPipe.y + pipeGap / 2
                pipeDist = firstPipe.x
            else:
                secondPipe = self.pipes.lower[1]
                pipeHeight = secondPipe.y + pipeGap / 2
                pipeDist = secondPipe.x
            
                
            playerInfo = []
            for player in self.players:
                playerInfo.append((player.vel_y, player.y))

            
            for birdNum, info in enumerate(playerInfo):
                vel, height = info
                if self.birds[birdNum].toFlapOrNotToFlap(height, vel, pipeHeight, pipeDist) > 0.5:
                    self.players[birdNum].flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            for player in self.players:
                player.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()
