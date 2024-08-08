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
    'ret.targetstock': 9,
    'distr.targetstock': 9,
    'whole.targetstock': 19,
    'plant.targetstock_raw': 9,
    'plant.targetstock_finished': 33
}


def run_simulation(parameters, trace=False):
    ret = ret_no_gui.Retailer()
    distr = distr_no_gui.Distributor()
    whole = whole_no_gui.Wholesaler()
    plant = plant_no_gui.Plant()

    ret.holdingrate = 4
    ret.backlograte = 10000   # 40
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
    plant.inventory_raw = 25
    plant.inventory_finished = 20
    plant.productiontime = 2

    ret.targetstock = parameters['ret.targetstock']
    distr.targetstock = parameters['distr.targetstock']
    whole.targetstock = parameters['whole.targetstock']
    plant.targetstock_raw = parameters['plant.targetstock_raw']
    plant.targetstock_finished = parameters['plant.targetstock_finished']

    for rx in range(51):
        if rx > 0:
            current_period = rx
            ret.current_demand = int(random.uniform(8, 12))
            if trace:
                print(" ")
                print(f"current_period: {current_period}")
            ret.current_period = current_period
            distr.current_period = current_period
            whole.current_period = current_period
            plant.current_period = current_period

            if trace:
                print(f"ret_inventory_start: {ret.inventory}")

                print(f"ret_demand: {ret.current_demand}")
            ret.update()

            if trace:
                print(f"ret_inventory_end: {ret.inventory}")
                print(f"ret_backlogtotal: {ret.backlogtotal}")
                print(f"ret_totalcosts: {ret.costs}")
            ret_order = max(ret.targetstock - ret.inventory, 0)

            if trace:
                print(f"ret_order: {ret_order}")

                print(f"distr_inventory_start: {distr.inventory}")

            distr.ret_order = ret_order
            distr.update()

            if trace:
                print(f"distr_inventory_end: {distr.inventory}")
                print(f"distr_backlogtotal: {distr.backlogtotal}")
                print(f"distr_totalcosts: {distr.costs}")

            ret.shipment_ret_queue.append((distr.shipment, current_period))
            distr_order = max(distr.targetstock - distr.inventory, 0)
            if trace:
                print(f"distr_order: {distr_order}")

                print(f"whole_inventory_start: {whole.inventory}")
            whole.distr_order = distr_order
            whole.update()

            if trace:
                print(f"whole_inventory_end: {whole.inventory}")
                print(f"whole_backlogtotal: {whole.backlogtotal}")
                print(f"whole_totalcosts: {whole.costs}")

            distr.shipment_distr_queue.append((whole.shipment, current_period))
            whole_order = max(whole.targetstock - whole.inventory, 0)

            if trace:
                print(f"whole_order: {whole_order}")

            plant.whole_order = whole_order
            plant.update()

            if trace:
                print(f"plant_inventory_raw_start: {plant.inventory_raw}")
                print(f"plant_inventory_finished_start: {
                      plant.inventory_finished}")

            plant.update_costs()
            plant.production = max(
                plant.targetstock_finished - plant.inventory_finished, 0)
            plant.produce()
            plant.prod_order = max(
                plant.targetstock_raw - plant.inventory_raw, 0)
            plant.plant_order()

            if trace:
                print(f"plant_inventory_raw_end: {plant.inventory_raw}")
                print(f"plant_inventory_finished_end: {
                      plant.inventory_finished}")
                print(f"plant_backlogtotal: {plant.backlogtotal}")
                print(f"plant_totalcosts: {plant.costs}")
                print(f"plant_production: {plant.production}")
                print(f"plant_order: {plant.prod_order}")

            whole.shipment_whole_queue.append((plant.shipment, current_period))

    totalcosts = ret.costs + distr.costs + whole.costs + plant.costs
    if trace:
        print(f"totalcosts: {totalcosts}")
        print(f"ret_sl: {ret.sl}")
        print(f"distr_sl: {distr.sl}")
        print(f"whole_sl: {whole.sl}")
        print(f"plant_sl: {plant.sl}")

    return totalcosts


# print(run_simulation(test_parameters, trace=False))


def objective(trial):

    tuned_parameters = {
        'ret.targetstock': trial.suggest_int('ret.targetstock', 1, 100),
        'distr.targetstock': trial.suggest_int('distr.targetstock', 1, 100),
        'whole.targetstock': trial.suggest_int('whole.targetstock', 1, 100),
        'plant.targetstock_raw': trial.suggest_int('plant.targetstock_raw', 1, 100),
        'plant.targetstock_finished': trial.suggest_int('plant.targetstock_finished', 1, 100)
    }

    results = []
    for step in range(50):  # репликации
        total_cost = run_simulation(tuned_parameters)
        results.append(total_cost)
        trial.report(total_cost, step)

        if trial.should_prune():
            raise optuna.TrialPruned()

    return sum(results)/len(results)

# study = optuna.create_study() # быстрее работает, данные в памяти


""" study = optuna.create_study(
    storage="sqlite:///tune.db",  # Specify the storage URL here.
    study_name="Target stock"
)

study.optimize(objective, n_trials=1000)
 """


def run_optimization(study_name, n_trials, storage):
    study = optuna.load_study(
        study_name=study_name,
        storage=storage  # Specify the storage URL here.
    )
    study.optimize(objective, n_trials=n_trials)


if __name__ == "__main__":
    jobs = []
    n_jobs = 8  # Кол-во параллельных задач

    study_name = "Оптимизация " + str(datetime.now())
    n_trials = 2000
    storage = optuna.storages.InMemoryStorage()
    # storage = "sqlite:///tune.db"  # Specify the storage URL here.
    study = optuna.create_study(
        study_name=study_name,
        storage=storage,  # Specify the storage URL here.
        # sampler=optuna.samplers.CmaEsSampler(),
        pruner=optuna.pruners.SuccessiveHalvingPruner()
    )

    study.optimize(objective, n_trials=n_trials, n_jobs=n_jobs)
    print(study.best_value, study.best_params)

# print(run_simulation(test_parameters, False))
# print(run_simulation(tuned_parameters, False))
#    optuna.visualization.plot_optimization_history(study)
    run_server(storage, host="localhost", port=8080)


""" res = Parallel(n_jobs=n_jobs)(delayed(run_optimization)(
        study_name, n_trials) for _ in range(n_jobs))
"""


"""
    for _ in range(n_jobs):
        p = multiprocessing.Process(
            target=run_optimization,
            args=(study_name, n_trials, storage))
        p.start()
        jobs.append(p)

    for p in jobs:
        p.join()
    # print(res)
    # print(study.best_value, study.best_params)  # E.g. {'x': 2.002108042}
"""

# study1 = optuna.load_study(study_name=study_name, storage=storage)
# print(study1.best_value, study1.best_params)
