import random
random.seed(10)
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.evaluation import evaluate_policy
from BG_RL_a4_obs8_env_exc2 import BeerGameEnv

vec_env = BeerGameEnv()

#models_path = "E:/SC_Beer_Game_Python-main/SC_Beer_Game_Python-main/models/1721960641/900000.zip"

#alpha = 0.05
#models_path = "E:/Beer-Game-RL-main (1)/Beer-Game-RL-main/models/1724020043/640000.zip"

#alpha = 0.1
#models_path = "E:/Beer-Game-RL-main (1)/Beer-Game-RL-main/models/1724023788/820000.zip"

#alpha = 0.02
#models_path = "E:/Beer-Game-RL-main (1)/Beer-Game-RL-main/models/1724027336/560000.zip"

#alpha=0
#models_path = "E:/Beer-Game-RL-main (1)/Beer-Game-RL-main/models/1723993355/700000.zip"


model = RecurrentPPO.load(models_path, env=vec_env)

vec_env = model.get_env()
obs = vec_env.reset()

#print(model.policy)

mean_reward, std_reward = evaluate_policy(model, vec_env, n_eval_episodes=1)
print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")






