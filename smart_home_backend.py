# -*- coding: utf-8 -*-
import time
import json
import random
import threading
from datetime import datetime
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import psutil
import schedule
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class SmartHomeSystem:
    def __init__(self):
        self.devices = {}
        self.sensors = {
            'temp_indoor': {'value': 22, 'unit': '°C'},
            'temp_outdoor': {'value': 15, 'unit': '°C'},
            'humidity': {'value': 45, 'unit': '%'},
            'motion': {'value': False, 'unit': ''},
            'smoke': {'value': False, 'unit': ''},
            'door_open': {'value': False, 'unit': ''},
            'light_level': {'value': 75, 'unit': '%'},
            'air_quality': {'value': 85, 'unit': '%'}
        }
        
        self.alerts = []
        self.energy_usage = {'current': 0, 'daily': 0}
        self.automation_rules = []
        
        # Загружаем устройства из файла
        self.load_devices()
        
    def load_devices(self):
        """Загружаем устройства из файла"""
        try:
            if os.path.exists('devices.json'):
                with open('devices.json', 'r', encoding='utf-8') as f:
                    devices_data = json.load(f)
                    for device in devices_data:
                        self.devices[device['id']] = {
                            'status': device.get('status', False),
                            'brightness': device.get('brightness', 100),
                            'type': device['type'],
                            'name': device['name'],
                            'last_updated': datetime.now().strftime('%H:%M:%S')
                        }
        except Exception as e:
            self.log_action(f"Ошибка загрузки устройств: {str(e)}")
    
    def save_devices(self):
        """Сохраняем устройства в файл"""
        try:
            devices_list = []
            for device_id, device_data in self.devices.items():
                devices_list.append({
                    'id': device_id,
                    'name': device_data['name'],
                    'type': device_data['type'],
                    'status': device_data['status'],
                    'brightness': device_data.get('brightness', 100)
                })
            
            with open('devices.json', 'w', encoding='utf-8') as f:
                json.dump(devices_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_action(f"Ошибка сохранения устройств: {str(e)}")
    
    def toggle_device(self, device_id, status=None):
        """Переключение устройства"""
        if device_id in self.devices:
            if status is not None:
                self.devices[device_id]['status'] = status
            else:
                self.devices[device_id]['status'] = not self.devices[device_id]['status']
            
            self.devices[device_id]['last_updated'] = datetime.now().strftime('%H:%M:%S')
            
            # Логирование действий
            action = "{} устройство: {}".format(
                'Включено' if self.devices[device_id]['status'] else 'Выключено',
                self.devices[device_id]['name']
            )
            self.log_action(action)
            
            # Сохраняем изменения
            self.save_devices()
            
            return self.devices[device_id]
        return None
    
    def set_device_brightness(self, device_id, brightness):
        """Установка яркости для устройств с поддержкой диммирования"""
        if device_id in self.devices:
            self.devices[device_id]['brightness'] = max(0, min(100, brightness))
            self.devices[device_id]['last_updated'] = datetime.now().strftime('%H:%M:%S')
            
            action = "Установлена яркость {}% для {}".format(
                brightness, self.devices[device_id]['name']
            )
            self.log_action(action)
            
            self.save_devices()
            return self.devices[device_id]
        return None
    
    def add_device(self, device_data):
        """Добавление нового устройства"""
        device_id = device_data['id']
        if device_id not in self.devices:
            self.devices[device_id] = {
                'status': False,
                'brightness': 100,
                'type': device_data['type'],
                'name': device_data['name'],
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
            
            self.save_devices()
            self.log_action(f"Добавлено новое устройство: {device_data['name']}")
            return True
        return False
    
    def remove_device(self, device_id):
        """Удаление устройства"""
        if device_id in self.devices:
            device_name = self.devices[device_id]['name']
            del self.devices[device_id]
            self.save_devices()
            self.log_action(f"Удалено устройство: {device_name}")
            return True
        return False
    
    def set_temperature(self, target_temp):
        """Установка температуры термостата"""
        if 'thermostat' in self.devices:
            self.devices['thermostat']['target_temp'] = target_temp
            self.devices['thermostat']['last_updated'] = datetime.now().strftime('%H:%M:%S')
            
            action = "Установлена температура: {}°C".format(target_temp)
            self.log_action(action)
            
            self.save_devices()
            return self.devices['thermostat']
        return None
    
    def update_sensors(self):
        """Обновление данных с датчиков"""
        try:
            # Симуляция обновления датчиков
            self.sensors['temp_indoor']['value'] = round(20 + random.uniform(-2, 2), 1)
            self.sensors['temp_outdoor']['value'] = round(10 + random.uniform(-5, 5), 1)
            self.sensors['humidity']['value'] = round(40 + random.uniform(-10, 10))
            self.sensors['light_level']['value'] = round(50 + random.uniform(-20, 20))
            self.sensors['air_quality']['value'] = round(80 + random.uniform(-15, 15))
            
            # Симуляция движения (5% вероятность)
            if random.random() < 0.05:
                self.sensors['motion']['value'] = True
                self.check_security()
            else:
                self.sensors['motion']['value'] = False
            
            # Симуляция дыма (1% вероятность)
            if random.random() < 0.01:
                self.sensors['smoke']['value'] = True
                self.add_alert('Обнаружен дым! Проверьте помещение.', 'warning')
            else:
                self.sensors['smoke']['value'] = False
                
        except Exception as e:
            self.log_action(f"Ошибка обновления датчиков: {str(e)}")
    
    def check_security(self):
        """Проверка безопасности"""
        if self.sensors['motion']['value']:
            # Ищем камеру безопасности
            for device_id, device in self.devices.items():
                if device['type'] == 'camera' and device['status']:
                    self.add_alert('Обнаружено движение! Камера записывает.', 'security')
                    break
    
    def add_alert(self, message, alert_type='info'):
        """Добавление уведомления"""
        alert = {
            'id': len(self.alerts) + 1,
            'message': message,
            'type': alert_type,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.alerts.append(alert)
        if len(self.alerts) > 20:  # Ограничиваем количество уведомлений
            self.alerts.pop(0)
    
    def log_action(self, action):
        """Логирование действий"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {action}")
    
    def get_system_status(self):
        """Получение статуса системы"""
        return {
            'devices': self.devices,
            'sensors': self.sensors,
            'alerts': self.alerts,
            'energy_usage': self.energy_usage,
            'system_uptime': time.time()
        }

# Создаем экземпляр системы
smart_home = SmartHomeSystem()

# Socket.IO события
@socketio.on('connect')
def handle_connect():
    print('Клиент подключился к Python бэкенду')
    emit('system_status', smart_home.get_system_status())

@socketio.on('toggle_device')
def handle_toggle_device(data):
    device_id = data.get('device')
    status = data.get('status')
    result = smart_home.toggle_device(device_id, status)
    if result:
        emit('device_updated', {'device': device_id, 'status': result})

@socketio.on('set_brightness')
def handle_set_brightness(data):
    device_id = data.get('device')
    brightness = data.get('brightness')
    result = smart_home.set_device_brightness(device_id, brightness)
    if result:
        emit('device_updated', {'device': device_id, 'status': result})

@socketio.on('set_temperature')
def handle_set_temperature(data):
    temperature = data.get('temperature')
    result = smart_home.set_temperature(temperature)
    emit('temperature_updated', result)

@socketio.on('add_device')
def handle_add_device(data):
    success = smart_home.add_device(data)
    if success:
        emit('device_added', data)
        emit('system_status', smart_home.get_system_status())

@socketio.on('remove_device')
def handle_remove_device(data):
    device_id = data.get('device_id')
    success = smart_home.remove_device(device_id)
    if success:
        emit('device_removed', {'device_id': device_id})
        emit('system_status', smart_home.get_system_status())

@socketio.on('get_system_status')
def handle_get_status():
    emit('system_status', smart_home.get_system_status())

def background_tasks():
    """Фоновая задача для обновления данных"""
    while True:
        smart_home.update_sensors()
        time.sleep(5)  # Обновляем каждые 5 секунд

# Запускаем фоновую задачу
threading.Thread(target=background_tasks, daemon=True).start()

if __name__ == '__main__':
    print('Запуск системы умного дома...')
    socketio.run(app, port=5000, debug=False) 