<h1 style="font-size: 30px; text-align: center; margin: 15px; padding: 10px;">PRO100_Голос</h1> 

# Deploy for localhost  ![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)

1. Установка библиотек
```
pip install -r requirements.txt
```

2. Запуск сервиса
```
python run.py
```

3. Перейти к сервису:
- http://localhost:5000



# Deploy for server  ![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)

1. Клонирование репозитория
```
git clone https://github.com/an8st/PRO100.git
```

2. Создание докер образа
```
docker build -t pro100 .
```

3. Запуск контейнера docker
```
docker run -d -p 5000:5000 --name flask-container pro100
```

4. Перейти к сервису:
- http://[ip server]:5000

  
# Стек технологий

### Flask 

**Flask** — это фреймворк для создания веб-приложений на языке Python. Инструмент предназначен для разработки веб-приложений.


### Vosk Model Small Russian (vosk-model-small-ru-0.22)

**vosk-model-small-ru-0.22** — это компактная и эффективная модель для распознавания русского языка, разработанная для быстрого и офлайн-распознавания речи. Эта модель идеально подходит для встроенных устройств, мобильных приложений и систем с ограниченными ресурсами, где важна скорость работы и экономия памяти.
