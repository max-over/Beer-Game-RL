# Общая информация по симулятору:
### Основные файлы игроков:

**ret_no_gui.py** - ритейлер

**distr_no_gui.py** - дистрибьютор

**whole_no_gui.py**- оптовик

**plant_no_gui.py** - завод

Отличие от классической версии: роль производства состоит из двух действий: от поставщика два периода доставляется сырье (запас: plant.inventory_raw) из сырья два периода изготавливается готовая продукция (запас: plant.inventory_finished)
Все процессы доставки и/или производства занимают два игровых периода. Обмен информацией: мгновенный

![sc](https://github.com/user-attachments/assets/a7e163be-d54e-4156-a813-09a6bb5eea7a)

Финансовый параметры:
```
self.ret.holdingrate = 4
self.ret.backlograte = 10 
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
self.plant.inventory_raw = 25
self.plant.inventory_finished = 20
```

### Если нужно протестировать логику размещения заказов/выполнения отгрузок, которая прописана в excel файле, то используется файл:

**coord_no_gui_excel.py**

Excel файл с примером

**example2.xls**

# Если нужно протестировать простую политику управления запасами:

**coord_no_gui_ts.py** - файл со стохастическим спросом (ts - target stock). В примере используется равномеоное распределение спроса от 8 до 12:

```
ret.current_demand = int(random.uniform(8, 12))
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
