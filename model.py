import gym
from stable_baselines3.common import env_checker
from sb3_contrib import QRDQN


DESIRED_FPS = 10
env = gym.make("gym_icytower:basic-v0", main_menu_active_mem_address=0x0098F6B4, game_active_mem_address=0x0098DCC4, level_dif_mem_address=0x0098EF5C, level_pre_combo_mem_address=0x004DD190, desired_fps=DESIRED_FPS)
env_checker.check_env(env)

# model = DQN("CnnPolicy", env, verbose=1, buffer_size=100000, batch_size=32, learning_starts=DESIRED_FPS*15*60,
#             train_freq=(4,'step'), target_update_interval=1000,
#             exploration_fraction=0.1, learning_rate=1*10**(-4), gradient_steps=1, optimize_memory_usage=True,
#             tensorboard_log="./tensorboard/")

# model = QRDQN("CnnPolicy", env, verbose=1, buffer_size=150000, exploration_fraction=0.05, optimize_memory_usage=True, tensorboard_log="./tensorboard/", device="cuda:0")
# model.learn(total_timesteps=DESIRED_FPS*60*60*24, log_interval=4)
# model.save("gym-icytower-qrdqn-24h")

# model = QRDQN.load('gym-icytower-qrdqn-24h', print_system_info=True)
# model.set_env(env)
# model.learn(total_timesteps=DESIRED_FPS*60*60*12, log_interval=4, reset_num_timesteps=False)
# model.save("gym-icytower-qrdqn-continued1-12h")

# model = QRDQN.load('gym-icytower-qrdqn-continued1-12h', print_system_info=True)
# model.set_env(env)
# model.learn(total_timesteps=DESIRED_FPS*60*60*12, log_interval=4, reset_num_timesteps=False)
# model.save("gym-icytower-qrdqn-continued2-12h")

# model = QRDQN.load('gym-icytower-qrdqn-continued2-12h', print_system_info=True)
# model.set_env(env)
# model.learn(total_timesteps=DESIRED_FPS*60*60*12, log_interval=4, reset_num_timesteps=False)
# model.save("gym-icytower-qrdqn-continued3-12h")

model = QRDQN.load('gym-icytower-qrdqn-continued3-12h', print_system_info=True)
model.set_env(env)
model.learn(total_timesteps=DESIRED_FPS*60*60*12, log_interval=4, reset_num_timesteps=False)
model.save("gym-icytower-qrdqn-continued4-12h")

env.close()

print("Done!")