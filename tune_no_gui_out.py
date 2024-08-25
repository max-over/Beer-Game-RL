import optuna
from datetime import datetime
from optuna_dashboard import run_server
# from joblib import Parallel, delayed
import multiprocessing
import random
import ret_no_gui
import distr_no_gui
import whole_no_gui
import plant_no_gui

random.seed(10)


test_parameters = {
    'ret.targetstock': 20,
    'distr.targetstock': 20,
    'whole.targetstock': 20,
    'plant.targetstock_raw': 20,
    'plant.targetstock_finished': 20
}

tuned_parameters = {
    'ret.targetstock': 22,
    'distr.targetstock': 22,
    'whole.targetstock': 19,
    'plant.targetstock_raw': 18,
    'plant.targetstock_finished': 29
}


def run_simulation(parameters, trace=False):
    ret = ret_no_gui.Retailer()
    distr = distr_no_gui.Distributor()
    whole = whole_no_gui.Wholesaler()
    plant = plant_no_gui.Plant()

    ret.holdingrate = 4
    ret.backlograte = 3000
    ret.leadtimeup = 2
    ret.inventory = 20

    distr.holdingrate = 2
    distr.backlograte = 4
    distr.leadtimeup = 2
    distr.inventory = 20

    whole.holdingrate = 2
    whole.backlograte = 4
    whole.leadtimeup = 2
    whole.inventory = 20

    plant.holdingrate_raw = 1
    plant.holdingrate_finished = 2
    plant.backlograte = 4
    plant.leadtimeup = 2
    plant.inventory_raw = 20
    plant.inventory_finished = 20
    plant.productiontime = 2

    ret.targetstock = parameters['ret.targetstock']
    distr.targetstock = parameters['distr.targetstock']
    whole.targetstock = parameters['whole.targetstock']
    plant.targetstock_raw = parameters['plant.targetstock_raw']
    plant.targetstock_finished = parameters['plant.targetstock_finished']

    for rx in range(1001):
        if rx > 0:
            current_period = rx
            ret.current_demand = int(random.uniform(8, 13))
            ret.current_period = current_period
            distr.current_period = current_period
            whole.current_period = current_period
            plant.current_period = current_period
            ret.update()
            ret_order = max(ret.targetstock - ret.inventory, 0)
            distr.ret_order = ret_order
            distr.update()
            ret.shipment_ret_queue.append((distr.shipment, current_period))
            distr_order = max(distr.targetstock - distr.inventory, 0)
            whole.distr_order = distr_order
            whole.update()
            distr.shipment_distr_queue.append((whole.shipment, current_period))
            whole_order = max(whole.targetstock - whole.inventory, 0)
            plant.whole_order = whole_order
            plant.update()
            plant.update_costs()
            plant.production = max(
                plant.targetstock_finished - plant.inventory_finished, 0)
            plant.produce()
            plant.prod_order = max(
                plant.targetstock_raw - plant.inventory_raw, 0)
            plant.plant_order()
            whole.shipment_whole_queue.append((plant.shipment, current_period))

    totalcosts = ret.costs + distr.costs + whole.costs + plant.costs


    return totalcosts



# 313479.25 {'ret.targetstock': 22, 'distr.targetstock': 22, 'whole.targetstock': 19, 'plant.targetstock_raw': 18, 'plant.targetstock_finished': 29}

def objective(trial):

    tuned_parameters = {
        'ret.targetstock': trial.suggest_int('ret.targetstock', 10, 29),
        'distr.targetstock': trial.suggest_int('distr.targetstock', 10, 29),
        'whole.targetstock': trial.suggest_int('whole.targetstock', 10, 29),
        'plant.targetstock_raw': trial.suggest_int('plant.targetstock_raw', 10, 29),
        'plant.targetstock_finished': trial.suggest_int('plant.targetstock_finished', 10, 29)
    }

    results = []
    for step in range(20):  # репликации
        total_cost = run_simulation(tuned_parameters)
        results.append(total_cost)
        trial.report(total_cost, step)

        if trial.should_prune():
            raise optuna.TrialPruned()

    return sum(results)/len(results)

study = optuna.create_study()


def run_optimization(study_name, n_trials, storage):
    study = optuna.load_study(
        study_name=study_name,
        storage=storage
    )
    study.optimize(objective, n_trials=n_trials)


if __name__ == "__main__":
    jobs = []
    n_jobs = 16

    study_name = "Optimisation " + str(datetime.now())
    n_trials = 20000
    storage = optuna.storages.InMemoryStorage()
    study = optuna.create_study(
        study_name=study_name,
        storage=storage,  # Specify the storage URL here.
        pruner=optuna.pruners.SuccessiveHalvingPruner()
    )

    study.optimize(objective, n_trials=n_trials, n_jobs=n_jobs)
    print(study.best_value, study.best_params)
    run_server(storage, host="localhost", port=8080)
