import requests
import json
import time
from typing import Dict, Any

class DeviceIntegration:
    """Класс для интеграции с реальными IoT устройствами"""
    
    def __init__(self):
        # Конфигурация устройств
        self.devices_config = {
            'smart_plug': {
                'ip': '192.168.1.100',
                'port': 80,
                'type': 'tplink',
                'username': 'admin',
                'password': 'password'
            },
            'philips_hue': {
                'ip': '192.168.1.101',
                'port': 80,
                'type': 'hue',
                'api_key': 'your_hue_api_key'
            },
            'nest_thermostat': {
                'type': 'nest',
                'client_id': 'your_nest_client_id',
                'client_secret': 'your_nest_secret'
            }
        }
    
    def control_smart_plug(self, device_id: str, state: bool) -> Dict[str, Any]:
        """Управление умной розеткой (например, TP-Link)"""
        try:
            config = self.devices_config.get('smart_plug')
            if not config:
                return {'success': False, 'error': 'Device not configured'}
            
            # Пример для TP-Link Smart Plug
            url = f"http://{config['ip']}/control"
            payload = {
                'system': {
                    'set_relay_state': {
                        'state': 1 if state else 0
                    }
                }
            }
            
            response = requests.post(url, json=payload, timeout=5)
            return {
                'success': response.status_code == 200,
                'device': device_id,
                'state': state
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def control_philips_hue(self, light_id: str, state: bool, brightness: int = 100) -> Dict[str, Any]:
        """Управление Philips Hue лампочками"""
        try:
            config = self.devices_config.get('philips_hue')
            if not config:
                return {'success': False, 'error': 'Hue bridge not configured'}
            
            url = f"http://{config['ip']}/api/{config['api_key']}/lights/{light_id}/state"
            payload = {
                'on': state,
                'bri': int(brightness * 2.54)  # Конвертация в формат Hue (0-254)
            }
            
            response = requests.put(url, json=payload, timeout=5)
            return {
                'success': response.status_code == 200,
                'light': light_id,
                'state': state,
                'brightness': brightness
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_nest_temperature(self) -> Dict[str, Any]:
        """Получение температуры с Nest термостата"""
        try:
            # Здесь нужно использовать Nest API
            # Для демонстрации возвращаем симуляцию
            return {
                'success': True,
                'temperature': 22.5,
                'humidity': 45,
                'target_temp': 22
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_nest_temperature(self, temperature: float) -> Dict[str, Any]:
        """Установка температуры на Nest термостате"""
        try:
            # Здесь нужно использовать Nest API
            return {
                'success': True,
                'target_temperature': temperature
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Пример использования
if __name__ == "__main__":
    integration = DeviceIntegration()
    
    # Включить умную розетку
    result = integration.control_smart_plug('living_room_plug', True)
    print(f"Smart plug result: {result}")
    
    # Включить Hue лампочку
    result = integration.control_philips_hue('1', True, 80)
    print(f"Hue light result: {result}") 