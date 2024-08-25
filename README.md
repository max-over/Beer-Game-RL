# General info:
### Agents/players files:

**ret_no_gui.py** - retailer

**distr_no_gui.py** - distributor

**whole_no_gui.py**- wholesaler

**plant_no_gui.py** - plant

The main difference to the classical version: the role of the plant consists of two actions: raw materail order (2 periods lead time, inventory: ```plant.inventory_raw```) then finished goods are produced from the raw materials  (2 periods production time, inventory: ```plant.inventory_finished```)
All lead times and production times are equal to two game periods (steps). Order information exchange: instantenious

![sc](https://github.com/user-attachments/assets/a7e163be-d54e-4156-a813-09a6bb5eea7a)

Financial parameters:
```
self.ret.holdingrate = 4
self.ret.backlograte = 10 (1000 for model training)
self.distr.holdingrate = 2
self.distr.backlograte = 4
self.whole.holdingrate = 2
self.whole.backlograte = 4
self.plant.holdingrate_raw = 1
self.plant.holdingrate_finished = 2
self.plant.backlograte = 4
self.plant.productiontime = 2
```

Initial inventory levels:
```
self.ret.inventory = 20
self.distr.inventory = 20
self.whole.inventory = 20
self.plant.inventory_raw = 20
self.plant.inventory_finished = 20
```

### If it is needed to test the logic of order placement/shipment fulfillment, which is presented in a separate excel file, then the file is used:

**coord_no_gui_excel.py**

sample Excel file with demand, order plan and shipments:

**example2.xls**

# For Order-Up-To policy assessment:

**coord_no_gui_ts.py** - stochastic uniform demand from 8 to 12, (ts - target stock):

```
ret.current_demand = int(random.uniform(8, 13))
```

Order-Up-To example calculation (for the other links/agents in the same way - the target and current stock levels are compared):
```
ret_order = max(ret.targetstock - ret.inventory, 0)
```

# Optimisation of inventory management policies using reinforcement learning:

The algorithm used is Recurrent Proximal Policy Optimization, from the sb3_contrib package. Environment interface: gymnasium. The model training format: stable_baselines3

There are three files for each experiment: an environment file, a model training file, and a model loading and testing file. 

The following three files are used for the version in which four actions (retailer's order, distributor's order, wholesaler's order, and production from raw materials, maximal version) are performed using reinforcement learning:

**BG_RL_a4_obs8_env.py** - environment file. Target raw material inventory is calculated with Order-Up-To ```self.plant.targetstock_raw = 18```, other inventory levels are defined by RL inventory policy. Order range: 0-29 ```MultiDiscrete([30,30,30,30]```. Each period the agent uses the following data about the state of the system when deciding the size of orders: the level of all types of inventory (5 parameters: 4 FG and 1 raw) and the backlogs of the distributor, wholesaler and factory. Thus, the dimensionality of the action space is: 5, observation space: 8. 
At initialization the basic parameters of the system are defined. The ```reset()``` method resets parameters' values for a new simulation/optimisation run. The ```step()``` method performs all actions for a period (step). By default 1000 steps per run are used. Notation logic for file names "A4" - four actions, "obs8" - eight observation parameters of the environment. Important: for training, the penalty value for lost sales is increased to a “barrier” value of 1000. During testing, the value of 10 is returned again.

```self.ret.backlograte = 10 #10 #10000```


**coord_learn_a4lstm.py** - a file for RPPO model training. LSTM is used in name to highlight that RNN neurla network is used in RPPO algorithm. The model is saved in a folder in 'start time' format, logs saved to a separate folder with the same name format. You can use tensorboard from the terminal for monitoring. Format : ```tensorboard --logdir E:\SC_Beer_Game_Python-main\SC_Beer_Game_Python-main\logs\1722036055\RPPO_0```


**coord_load_a4.py** - a file for model loading and testing  (model location path should be specified), 20 replications for testing ```mean_reward, std_reward = evaluate_policy(model, vec_env, n_eval_episodes=20)```

**BG_RL_a4_obs8_env_exc.py** - test environment with saving statistics to Excel

# Pretrained models (1 action - only Retailer's orders with RL, 2 actions - Retailer's order and Distributor's order with RL, etc):

**model_a4.zip** - a model for four actions and a state space of eight parameters

**model_a3.zip** - a model for three actions and a state space of eight parameters

**model_a2.zip** - a model for two actions and a state space of eight parameters

**model_a1.zip** - a model for one action and a state space of eight parameters


# Pretrained models for different supply chain echelons (1 action i all models):

**model_a1.zip** - a model for one action and a state space of eight parameters (Retailer)

**model_a1d.zip** - a model for one action and a state space of eight parameters (Distributor)

**model_a1w.zip** - a model for one action and a state space of eight parameters (Wholesaler)

**model_a1p.zip** - a model for one action and a state space of eight parameters (Plant)

