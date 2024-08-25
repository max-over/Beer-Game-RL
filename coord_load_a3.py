import random
random.seed(10)
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.evaluation import evaluate_policy
from BG_RL_a3_obs8_env import BeerGameEnv

vec_env = BeerGameEnv()

#models_path = "E:/Beer-Game-RL-main (1)/Beer-Game-RL-main/models/1723987174/680000.zip"
models_path = "E:/Beer-Game-RL-main (1)/Beer-Game-RL-main/models/1723990667/500000.zip"

model = RecurrentPPO.load(models_path, env=vec_env)

vec_env = model.get_env()
obs = vec_env.reset()

#print(model.policy)

mean_reward, std_reward = evaluate_policy(model, vec_env, n_eval_episodes=20)
print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")






