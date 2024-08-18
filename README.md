# Общая информация по симулятору:
### Основные файлы игроков:

**ret_no_gui.py** - ритейлер

**distr_no_gui.py** - дистрибьютор

**whole_no_gui.py**- оптовик

**plant_no_gui.py** - завод

Отличие от классической версии: роль производства состоит из двух действий: от поставщика два периода доставляется сырье (запас: ```plant.inventory_raw```) из сырья два периода изготавливается готовая продукция (запас: ```plant.inventory_finished```)
Все процессы доставки и/или производства занимают два игровых периода. Обмен информацией: мгновенный

![sc](https://github.com/user-attachments/assets/a7e163be-d54e-4156-a813-09a6bb5eea7a)

Финансовые параметры:
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

Начальный уровень запасов:
```
self.ret.inventory = 20
self.distr.inventory = 20
self.whole.inventory = 20
self.plant.inventory_raw = 20
self.plant.inventory_finished = 20
```

### Если нужно протестировать логику размещения заказов/выполнения отгрузок, которая прописана в excel файле, то используется файл:

**coord_no_gui_excel.py**

Excel файл с примером спроса, плана заказов и отгрузок:

**example2.xls**

# Если нужно протестировать простую политику управления запасами:

**coord_no_gui_ts.py** - файл со стохастическим спросом (ts - target stock). В примере используется равномерное распределение спроса от 8 до 12:

```
ret.current_demand = int(random.uniform(8, 13))
```

Пример для расчета заказа ритейлера (у других звеньев по аналогии - сравнивается целевой и текущий уровень запаса):
```
ret_order = max(ret.targetstock - ret.inventory, 0)
```

Базовые (целевые) уровни запаса (Target stock):
```
ret.targetstock = 20
distr.targetstock = 20
whole.targetstock = 20
plant.targetstock_raw = 20
plant.targetstock_finished = 20
```

# Подбор политики управления запасами при помощи обучения с подкреплением:

Используется алгоритм Recurrent Proximal Policy Optimisation, из пакета sb3_contrib. Интерфейс среды: gymnasium. Общий формат обучения моделей: stable_baselines3

Для каждого эксперимента есть три файла: файл среды, файл обучения модели, файл загрузки и тестирования модели. 

Для версии, в которой при помощи обучения с подкреплением выполняются четыре действия (заказ ритейлера, заказ дистрибьютора, заказ оптовика, производство из сырья), используются следующие файлы:


**BG_RL_a4_obs8_env.py** - файл среды. Целевой запас сырья ```self.plant.targetstock_raw = 18```, остальные запасы определяются через действия агента (заказы). Заказы могут быть в диапазоне 0-29 ```MultiDiscrete([30,30,30,30]```. Каждый период при принятии решения о размере заказов агент использует следующие данные о состоянии системы: уровень всех видов запасов (5 параметров) и бэклоги дистрибьютора, оптовика и завода. Таким обзраом, размерность пространства действий: 5, пространства мониторинга: 8
При инициализации опредляются основные параметры системы. Метод ```reset()``` сбрасывает показатели на начальные значения для нового прогона. Метод ```step()``` выполняет действия для одного периода (длина прогона 1000 периодов). Логика формата названия файла "A4" - четыре действия, "obs8" - восемь отслеживаемых параметров среды. Важно: для обучения значение штрафа для потерянных продаж увеличивается до "заградительного" значения в 1000. При тестировании вновь возвращается значение 10 ```self.ret.backlograte = 10 #10 #10000```


**coord_learn_a4lstm.py** - файл обучения модели RPPO для управления запасами. LSTM в названии из-за того, что RNN используются в RPPO. Модель сохраняется в папке в формате времени запуска, логи в отдельной папке с таким же форматом названия. Для мониторинга можно использовать tensorboard из терминала. Формат: ```tensorboard --logdir E:\SC_Beer_Game_Python-main\SC_Beer_Game_Python-main\logs\1722036055\RPPO_0```


**coord_load_a4.py** - файл для загрузки и тестирования модели (нужно указать локацию модели), тестирование на трех прогонах ```mean_reward, std_reward = evaluate_policy(model, vec_env, n_eval_episodes=3)```

**BG_RL_a4_obs8_env_exc.py** - тестовая среда с записью статистики в Excel

# Предобученные модели (1 действие - только заказ ритейлера, 2 действия - заказ ритейлера и дистрибьютора и т.д.):

**a4e8.zip** - модель для четырех действий и пространства состояний из восьми параметров

**a3e8.zip** - модель для трех действий и пространства состояний из восьми параметров

**a2e8.zip** - модель для двух действий и пространства состояний из восьми параметров

**a1e8.zip** - модель для одного действия и пространства состояний из восьми параметров
