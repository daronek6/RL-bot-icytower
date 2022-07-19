import gym
from sb3_contrib.qrdqn import QRDQN

DESIRED_FPS = 10
bot_model_name = "gym-icytower-qrdqn-continued2-12h"

env = gym.make("gym_icytower:basic-v0", main_menu_active_mem_address=0x0098F6B4, game_active_mem_address=0x0098DCC4, level_dif_mem_address=0x0098EF5C, level_pre_combo_mem_address=0x004DD190, desired_fps=DESIRED_FPS)
model = QRDQN.load(path=bot_model_name, env=env)

obs = env.reset()
while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    if done:
        obs = env.reset()