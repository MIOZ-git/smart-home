const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Подключение к Python бэкенду
const pythonSocket = require('socket.io-client')('http://localhost:5000');

// Хранилище данных
let systemData = {
    devices: {},
    sensors: {},
    alerts: [],
    energy_usage: { current: 0, daily: 0 },
    system_uptime: 0
};

// Подключение к Python бэкенду
pythonSocket.on('connect', () => {
    console.log('Подключено к Python бэкенду');
    pythonSocket.emit('get_system_status');
});

pythonSocket.on('system_status', (data) => {
    systemData = data;
    io.emit('system_status', data);
});

pythonSocket.on('device_updated', (data) => {
    io.emit('device_updated', data);
});

pythonSocket.on('temperature_updated', (data) => {
    io.emit('temperature_updated', data);
});

pythonSocket.on('device_added', (data) => {
    io.emit('device_added', data);
});

pythonSocket.on('device_removed', (data) => {
    io.emit('device_removed', data);
});

// WebSocket подключения
io.on('connection', (socket) => {
    console.log('Клиент подключился к Node.js серверу');
    
    // Отправляем текущий статус системы
    socket.emit('system_status', systemData);
    
    // Обработка переключения устройств
    socket.on('toggle_device', (data) => {
        pythonSocket.emit('toggle_device', data);
    });
    
    // Обработка установки яркости
    socket.on('set_brightness', (data) => {
        pythonSocket.emit('set_brightness', data);
    });
    
    // Обработка установки температуры
    socket.on('set_temperature', (data) => {
        pythonSocket.emit('set_temperature', data);
    });
    
    // Обработка добавления устройства
    socket.on('add_device', (data) => {
        pythonSocket.emit('add_device', data);
    });
    
    // Обработка удаления устройства
    socket.on('remove_device', (data) => {
        pythonSocket.emit('remove_device', data);
    });
    
    // Обработка запроса статуса системы
    socket.on('get_system_status', () => {
        pythonSocket.emit('get_system_status');
    });
    
    socket.on('disconnect', () => {
        console.log('Клиент отключился от Node.js сервера');
    });
});

// API маршруты
app.get('/api/status', (req, res) => {
    res.json(systemData);
});

app.get('/api/devices', (req, res) => {
    res.json(systemData.devices);
});

app.get('/api/sensors', (req, res) => {
    res.json(systemData.sensors);
});

app.get('/api/alerts', (req, res) => {
    res.json(systemData.alerts);
});

app.post('/api/devices/toggle', (req, res) => {
    const { device_id, status } = req.body;
    if (device_id) {
        pythonSocket.emit('toggle_device', { device: device_id, status });
        res.json({ success: true, message: 'Команда отправлена' });
    } else {
        res.status(400).json({ success: false, message: 'Не указан ID устройства' });
    }
});

app.post('/api/devices/brightness', (req, res) => {
    const { device_id, brightness } = req.body;
    if (device_id && brightness !== undefined) {
        pythonSocket.emit('set_brightness', { device: device_id, brightness });
        res.json({ success: true, message: 'Яркость установлена' });
    } else {
        res.status(400).json({ success: false, message: 'Не указаны параметры' });
    }
});

app.post('/api/thermostat/temperature', (req, res) => {
    const { temperature } = req.body;
    if (temperature !== undefined) {
        pythonSocket.emit('set_temperature', { temperature });
        res.json({ success: true, message: 'Температура установлена' });
    } else {
        res.status(400).json({ success: false, message: 'Не указана температура' });
    }
});

app.post('/api/devices/add', (req, res) => {
    const { id, name, type } = req.body;
    if (id && name && type) {
        pythonSocket.emit('add_device', { id, name, type });
        res.json({ success: true, message: 'Устройство добавлено' });
    } else {
        res.status(400).json({ success: false, message: 'Не указаны все параметры' });
    }
});

app.delete('/api/devices/:device_id', (req, res) => {
    const { device_id } = req.params;
    if (device_id) {
        pythonSocket.emit('remove_device', { device_id });
        res.json({ success: true, message: 'Устройство удалено' });
    } else {
        res.status(400).json({ success: false, message: 'Не указан ID устройства' });
    }
});

// Маршрут для главной страницы
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Обработка ошибок
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ success: false, message: 'Внутренняя ошибка сервера' });
});

// Запуск сервера
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Node.js сервер запущен на порту ${PORT}`);
    console.log(`Откройте http://localhost:${PORT} в браузере`);
}); 