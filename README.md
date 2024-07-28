# Общая информация по симулятору:
### Основные файлы игроков:

ret_no_gui.py - ритейлер

distr_no_gui.py - дистрибьютор

whole_no_gui.py - оптовик

plant_no_gui.py - завод

### Если нужно протестировать логику размещения заказов/выполнения отгрузок, которая прописана в excel файле, то используется файл:

coord_no_gui_excel.py

Excel файл с примером

example2.xls

# Если нужно протестировать простую политику управления запасами:

coord_no_gui_ts.py - файл со стохастическим спросом (ts - target stock). В примере используется равномеоное распределение спроса от 8 до 12:

```
ret.current_demand = int(random.uniform(8, 12))
```

Базовые уровни запаса:
```
ret.targetstock = 20
distr.targetstock = 20
whole.targetstock = 20
plant.targetstock_raw = 20
plant.targetstock_finished = 20
```
