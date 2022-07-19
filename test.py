import gym
import numpy as np
import matplotlib.pyplot as plt
from sb3_contrib.qrdqn import QRDQN

DESIRED_FPS = 10
TEST_TIME = DESIRED_FPS * 60 * 25

models = ("gym-icytower-qrdqn-24h", "gym-icytower-qrdqn-continued1-12h", "gym-icytower-qrdqn-continued2-12h", "gym-icytower-qrdqn-continued3-12h", "gym-icytower-qrdqn-continued4-12h")
results = []
for model_name in models:

    env = gym.make("gym_icytower:basic-v0", main_menu_active_mem_address=0x0098F6B4, game_active_mem_address=0x0098DCC4, level_dif_mem_address=0x0098EF5C, level_pre_combo_mem_address=0x004DD190, desired_fps=DESIRED_FPS)
    model = QRDQN.load(path=model_name, env=env)
    time_steps = 0
    model_results = []
    model_episodes = []
    episode = 1

    obs = env.reset()
    while time_steps < TEST_TIME:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        time_steps += 1
        if done:
            model_results.append(env.previousLevel)
            model_episodes.append(episode)
            episode += 1
            obs = env.reset()
    
    results.append((model_episodes, model_results))
    env.close()

avgs = []
maxes = []

for result in results:
    avgs.append(np.average(result[1]))
    maxes.append(np.max(result[1]))

for i in range(len(models)):
    plt.plot(results[i][0], results[i][1], marker="o")
    plt.plot(results[i][0], [avgs[i]]*len(results[i][0]), color="green", label="Średnia", linestyle="--")
    plt.text(results[i][0][-1], avgs[i], str(avgs[i]), color="green")
    plt.plot(results[i][0], [maxes[i]]*len(results[i][0]), color="red", label="Maksimum", linestyle="-.")
    plt.text(results[i][0][-1], maxes[i], str(maxes[i]), color="red")
    plt.xlabel("Epizod")
    plt.ylabel("Poziom")
    plt.title(f"Model: {models[i]}")
    plt.legend(loc="lower left")
    plt.savefig(f"wyk2-{models[i]}.png")
    plt.show()

    plt.hist(results[i][1], facecolor="g", alpha=0.75)
    plt.title(f"Histogram dla {models[i]}")
    plt.xlabel("Poziom")
    plt.ylabel("Ilość wystąpień")
    plt.grid(True)
    plt.savefig(f"hist2-{models[i]}.png")
    plt.show()


