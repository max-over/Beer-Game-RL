import random
random.seed(10)
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.env_checker import check_env
from BG_RL_a4_obs8_env_bwe import BeerGameEnv
import os
import time
from stable_baselines3.common.evaluation import evaluate_policy

vec_env = BeerGameEnv()
check_env(vec_env)

models_dir = f"models/{int(time.time())}/"
logdir = f"logs/{int(time.time())}/"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

vec_env.reset()

models_path = "E:/SC_Beer_Game_Python-main/SC_Beer_Game_Python-main/models/1721960641/900000.zip"

model = RecurrentPPO.load(models_path, env=vec_env, verbose=1, tensorboard_log=logdir, learning_rate= 0.00002)

#model = RecurrentPPO('MlpLstmPolicy', vec_env, verbose=1, tensorboard_log=logdir, learning_rate= 0.0002)

TIMESTEPS = 20000
iters = 0
iter_max = 50
while iters < iter_max:
    iters += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="RPPO")
    model.save(f"{models_dir}/{TIMESTEPS*iters}")
    mean_reward, std_reward = evaluate_policy(model, vec_env, n_eval_episodes=3, deterministic=True)
    print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")





