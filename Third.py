import subprocess
import json
import random

# Генерация случайного числа
param = random.randint(1, 10)

# Формирование команды curl для GET запроса
curl_command = [
    'curl',
    f"http://127.0.0.1:5000/number/?param={param}"
]

# Выполнение запроса curl
curl_output = subprocess.run(curl_command, capture_output=True, text=True)

# Получение данных из вывода curl
curl_response = json.loads(curl_output.stdout)

# Запоминание числа и операции из GET запроса
operation_get = curl_response.get("operation")
result_get = curl_response["result"]

# Вывод результата GET запроса
print(f"GET запрос: Число: {result_get}, Операция: {operation_get}")

# Генерация случайного числа
json_param = random.randint(1, 10)

# Преобразование JSON данных для curl
json_data_for_curl = json.dumps({"jsonParam": json_param})

# Формирование команды curl для POST запроса
curl_command = [
    'curl',
    '-X', 'POST',
    '-H', 'Content-Type: application/json',
    '-d', json_data_for_curl,
    'http://127.0.0.1:5000/number/'
]

# Выполнение запроса curl
curl_output = subprocess.run(curl_command, capture_output=True, text=True)

# Получение данных из вывода curl
curl_response = json.loads(curl_output.stdout)

# Запоминание числа и операции из POST запроса
operation_post = curl_response["operation"]
result_post = curl_response["result"]

# Вывод результата POST запроса
print(f"POST запрос: Число: {result_post}, Операция: {operation_post}")

# Формирование команды curl для DELETE запроса
curl_command = [
    'curl',
    '-X', 'DELETE',
    'http://127.0.0.1:5000/number/'
]

# Выполнение запроса curl
curl_output = subprocess.run(curl_command, capture_output=True, text=True)

# Получение данных из вывода curl
curl_response = json.loads(curl_output.stdout)

# Запоминание числа и операции из DELETE запроса
operation_delete = curl_response["operation"]
result_delete = curl_response["result"]

# Вывод результата DELETE запроса
print(f"DELETE запрос: Число: {result_delete}, Операция: {operation_delete}")

# Составление выражения из полученных операций и результатов
expression = f"{result_get} "
for op, res in zip([operation_post, operation_delete], [result_post, result_delete]):
    expression += f"{op} {res} "

# Разделение выражения на операнды и операции
tokens = expression.split()

# Вычисление выражения
result_final = float(tokens[0])
for i in range(1, len(tokens), 2):
    op = tokens[i]
    num = float(tokens[i + 1])
    if op == 'add':
        result_final += num
    elif op == 'subtract':
        result_final -= num
    elif op == 'multiply':
        result_final *= num
    elif op == 'divide':
        result_final /= num

# Преобразование результата к целому числу
result_final = int(result_final)

# Вывод результата вычисления
print(f"Выражение: {expression}, Результат: {result_final}")
