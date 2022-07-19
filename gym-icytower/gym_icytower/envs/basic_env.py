import subprocess
import time
from enum import Enum

import os
import gym
import numpy
import pydirectinput
import pymeow
import win32gui
import win32ui
from PIL import Image
from ctypes import windll
from gym import error, spaces, utils
from gym.utils import seeding


def launch_game():
  subprocess.Popen(['../rl-bot-icytower/icytower151/icytower15.exe'])
  print("Loading...")
  time.sleep(6)
  print("Done!")

def close_game():
  subprocess.call(["taskkill", "/F", "/IM", "icytower15.exe"])
  time.sleep(2)


def start_normal_game():
  time.sleep(0.1)
  pydirectinput.press('enter', _pause=False)
  time.sleep(0.1)
  pydirectinput.press('enter', _pause=False)
  time.sleep(0.3)

def reset_normal_game():
  time.sleep(0.1)
  pydirectinput.press('esc', _pause=False)
  time.sleep(0.3)
  pydirectinput.press('esc', _pause=False)
  time.sleep(0.6)
  start_normal_game()


def reset_game_over():
  time.sleep(0.1)
  pydirectinput.press('space', _pause=False)
  time.sleep(0.2)
  pydirectinput.press('space', _pause=False)
  time.sleep(0.3)

def stop_inputs():
  pydirectinput.keyUp('space', _pause=False)
  pydirectinput.keyUp('left', _pause=False)
  pydirectinput.keyUp('right', _pause=False)


class BasicEnv(gym.Env):
  metadata = {'render.modes': ['human', 'rgb_array', 'grayscale_scaled']}

  class Status(Enum):
    GAME_ACTIVE = 0
    GAME_OVER = 1
    MAIN_MENU = 2

  def __init__(self, main_menu_active_mem_address=0x000000, game_active_mem_address=0x000000, level_dif_mem_address=0x000000, level_pre_combo_mem_address=0x000000, desired_fps = 10):
    launch_game()

    self.viewer = None
    self.hwnd = None
    self.window_w = None
    self.window_h = None
    self.hwndDC = None
    self.mfcDC = None
    self.saveDC = None
    self.process = None
    self.gameStatusAddress = None
    self.preComboLevelAddress = None
    self.prevJumpLevelDifAddress = None
    self.mainMenuAddress = None
    self.status = None

    self.prevLevelDif = 0
    self.previousLevel = 0
    self.episodeSteps = 0
    self.rewardChangeStep = 0
    self.prevStepTime = 0
    self.stepTime = 0
    self.episodeReward = 0
    self.desiredFps = 0
    self.avgFps = 0
    self.stepIntervalInSec = 0
    self.prevAction = 0
    self.actionRepeats = 0
    self.numOfResets = 0
    self.zeros = numpy.zeros((120, 120), dtype=numpy.uint8)
    self.startTime = time.time()

    self.configure(main_menu_active_mem_address, game_active_mem_address, level_dif_mem_address, level_pre_combo_mem_address, desired_fps)
    self.observation_space = spaces.Box(low=0, high=255, shape=[120, 120, 3], dtype=numpy.uint8) # 3 last frames - 120x120
    self.action_space = spaces.Discrete(4)  # 0 - left, 1 - right, 2 - left+jump, 3 - right+jump
    self.lastFrame, self.lastFrameTransformed = self.get_frame()
    self.lastLastFrameTransformed = self.lastFrameTransformed
    time.sleep(0.2)

  def step(self, action):
    stepStartTime = time.time()
    self.get_game_status()

    self.perform_action(action)
    reward = self.get_reward()

    done = self.status != self.status.GAME_ACTIVE

    info = {
      'status': self.status
    }

    if self.episodeSteps - self.rewardChangeStep > self.avgFps * 15:
      done = 1
    elif self.previousLevel < 4 and self.episodeSteps > self.avgFps * 30:
      done = 1

    stepEndTime = time.time()
    sleepTime = self.stepIntervalInSec - (stepEndTime - stepStartTime)
    if sleepTime < 0:
      sleepTime = 0
    time.sleep(sleepTime)

    ob = self.get_observation()
    
    self.avgFps = numpy.mean([self.avgFps, 1/(sleepTime + (stepEndTime - stepStartTime))])

    print(
      f"Step: {self.episodeSteps}, Step time: {sleepTime + (stepEndTime - stepStartTime)},"
      f" Steps/s: {1/(sleepTime + (stepEndTime - stepStartTime))}, AvgSteps/s: {self.avgFps},"
      f" Action: {PYDIRECTINPUT_ACTION[action]}, prevLevel: {self.previousLevel}, episodeReward: {self.episodeReward},"
      f" rewardChangeStep: {self.rewardChangeStep}, actionRepeats: {self.actionRepeats} ")

    self.episodeSteps += 1
    return ob, reward, done, info

  def reconfigure(self):
    print("---------------- Time to reset the game due to a bug! Game stops working after 254 restarts! ----------------")
    self.numOfResets = 0
    self.saveDC.DeleteDC()
    self.mfcDC.DeleteDC()
    win32gui.ReleaseDC(self.hwnd, self.hwndDC)
    close_game()
    launch_game()
    desired_fps = self.desiredFps
    menu_adrs = self.mainMenuAddress
    game_actv_adrs = self.gameStatusAddress
    lvl_dif_adrs = self.prevJumpLevelDifAddress
    lvl_pre_cmb_adrs = self.preComboLevelAddress
    self.configure(menu_adrs, game_actv_adrs, lvl_dif_adrs, lvl_pre_cmb_adrs, desired_fps)
    print("All good! Back to work!")
    time.sleep(0.1)

  def reset(self):
    stop_inputs()
    self.numOfResets += 1
    self.previousLevel = 0
    self.episodeSteps = 0
    self.rewardChangeStep = 0
    self.episodeReward = 0
    self.actionRepeats = 0
    self.prevLevelDif = 0

    if self.numOfResets >= 250:
       self.reconfigure()
    elif self.status == self.Status.GAME_ACTIVE:
      reset_normal_game()
    elif self.status == self.Status.GAME_OVER:
      reset_game_over()
    elif self.status == self.Status.MAIN_MENU:
      start_normal_game()
    else:
      print("reset() - Invalid status!")
    ob = numpy.dstack((self.zeros, self.zeros, self.zeros))
    timeElapsed = time.time() - self.startTime
    print(f"-|-|-|-|- Time elapsed since start: {timeElapsed/60} min. -|-|-|-|-")
    return ob

  def render(self, mode='human'):
    if mode == 'human':
      if self.viewer == None:
        from gym.envs.classic_control import rendering
        self.viewer = rendering.SimpleImageViewer()
        #self.viewer.imshow(self.lastFrame)
      else:
        pass
        #self.viewer.imshow(self.lastFrame)

    elif mode == 'rgb_array':
      return self.lastFrame

    elif mode == 'grayscale_scaled':
      return self.lastFrameTransformed

    else:
      print("render() - Invalid render mode!")

  def close(self):
    self.saveDC.DeleteDC()
    self.mfcDC.DeleteDC()
    win32gui.ReleaseDC(self.hwnd, self.hwndDC)
    close_game()

  def configure(self, main_menu_active_mem_address, game_active_mem_address, level_dif_mem_address, level_pre_combo_mem_address, desired_fps):
    self.hwnd = win32gui.FindWindow(None, 'Icy Tower v1.5.1')
    win32gui.SetForegroundWindow(self.hwnd)
    time.sleep(0.1)
    left, top, right, bot = win32gui.GetClientRect(self.hwnd)
    self.window_w = right - left
    self.window_h = bot - top

    self.hwndDC = win32gui.GetWindowDC(self.hwnd)
    self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
    self.saveDC = self.mfcDC.CreateCompatibleDC()
    self.process = pymeow.process_by_name('icytower15.exe')
    self.gameStatusAddress = game_active_mem_address
    self.mainMenuAddress = main_menu_active_mem_address
    self.preComboLevelAddress = level_pre_combo_mem_address
    self.prevJumpLevelDifAddress = level_dif_mem_address

    self.status = self.Status.MAIN_MENU
    self.desiredFps = desired_fps
    self.avgFps = desired_fps
    self.stepIntervalInSec = 1 / self.desiredFps

    start_normal_game()
    self.status = self.Status.GAME_ACTIVE
    time.sleep(0.2)
    self.stepTime = time.time()

  def perform_action(self, action):
    stop_inputs()

    if self.prevAction != action:
      self.prevAction = action
      self.actionRepeats = 0
    else:
      self.actionRepeats += 1

    if action in range(0, 2):
      pydirectinput.keyDown(PYDIRECTINPUT_ACTION[action], _pause=False)
    elif action in range(2, 4):
      pydirectinput.keyDown(PYDIRECTINPUT_ACTION[action][0], _pause=False)
      pydirectinput.keyDown(PYDIRECTINPUT_ACTION[action][1], _pause=False)
    else:
      print("perform_action() - Invalid action!")

  def get_frame(self):
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.window_w, self.window_h)

    self.saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(self.hwnd, self.saveDC.GetSafeHdc(), 1)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
      'RGB',
      (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
      bmpstr, 'raw', 'BGRX', 0, 1)

    img = numpy.asarray(im, dtype=numpy.uint8)
    win32gui.DeleteObject(saveBitMap.GetHandle())

    imTransformed = im.convert('L').resize((160, 120)).crop((20, 0, 140, 120))
    imgTransformed = numpy.asarray(imTransformed, dtype=numpy.uint8)

    return img, imgTransformed

  def get_observation(self):
    currentFrame, currentFrameTransformed = self.get_frame()
    ob = numpy.dstack((self.lastLastFrameTransformed, self.lastFrameTransformed, currentFrameTransformed))
    #imageio.imwrite(f"{self.episodeSteps}.png", ob)
    self.lastLastFrameTransformed = self.lastFrameTransformed
    self.lastFrameTransformed = currentFrameTransformed

    self.lastFrame = currentFrame
    self.lastFrameTransformed = currentFrameTransformed
    
    return ob
  
  def get_game_status(self):
    menuBool = pymeow.read_int(self.process, self.mainMenuAddress)
    gameActiveBool = pymeow.read_int(self.process, self.gameStatusAddress)

    if menuBool:
      self.status = self.Status.MAIN_MENU
    else:
      if gameActiveBool:
        self.status = self.Status.GAME_ACTIVE
      else:
        self.status = self.Status.GAME_OVER

  def get_reward(self):
    actionRepeatLimit = self.avgFps * 1.5
    preComboLevel = pymeow.read_int(self.process, self.preComboLevelAddress)
    jumpLevelDif = pymeow.read_int(self.process, self.prevJumpLevelDifAddress)

    reward = 0

    if self.previousLevel != preComboLevel and jumpLevelDif in (0,1):
      reward = preComboLevel - self.previousLevel
      self.previousLevel = preComboLevel
      self.prevLevelDif = jumpLevelDif
    elif self.prevLevelDif != jumpLevelDif and jumpLevelDif <= 5:
      reward = jumpLevelDif
      self.previousLevel += jumpLevelDif
      self.prevLevelDif = jumpLevelDif

    if reward != 0:
      self.rewardChangeStep = self.episodeSteps
    if (self.episodeSteps - self.rewardChangeStep) % (numpy.ceil(self.avgFps) * 4) == 0:
      reward -= 0.1
    if self.actionRepeats > actionRepeatLimit:
      reward -= (self.actionRepeats - actionRepeatLimit) * 0.01

    self.episodeReward += reward
    return reward

PYDIRECTINPUT_ACTION = {
  0: 'left',
  1: 'right',
  2: ('left', 'space'),
  3: ('right', 'space')
}
