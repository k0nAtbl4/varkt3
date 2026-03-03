import krpc

print("1. Подключаюсь...")
conn = krpc.connect(name="Test")
print("2. Успешно подключился!")

print("3. Получаю космический центр...")
space_center = conn.space_center
print("4. Получил!")

print("5. Получаю активный корабль...")
vessel = space_center.active_vessel
print(f"6. Корабль: {vessel.name}")

print("7. Пробую получить любые данные...")
try:
    # Самый простой тест - имя корабля
    name = vessel.name
    print(f"   Имя работает: {name}")
    
    # Тест ресурсов
    resources = vessel.resources
    print(f"   Ресурсы объект получен")
    
    # Тест списка ресурсов
    all_resources = resources.names
    print(f"   Список ресурсов: {all_resources}")
    
    # Тест конкретного ресурса
    if all_resources:
        test = resources.amount(all_resources[0])
        print(f"   Значение ресурса: {test}")
    
except Exception as e:
    print(f"!!! ОШИБКА: {e}")

print("8. Тест завершен")