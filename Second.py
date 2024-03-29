import requests
import random

# Запомним число и операцию из GET запроса
param = random.randint(1, 10)
response = requests.get(f"http://127.0.0.1:5000/number/?param={param}")
data = response.json()
operation_get = data.get("operation")
result_get = data["result"]
print(f"GET запрос: Число: {result_get}, Операция: {operation_get}")

# Отправим POST запрос с рандомным числом
json_param = random.randint(1, 10)
response = requests.post("http://127.0.0.1:5000/number/",
                         json={"jsonParam": json_param},
                         headers={"content-type": "application/json"})
data = response.json()
operation_post = data["operation"]
result_post = data["result"]
print(f"POST запрос: Число: {result_post}, Операция: {operation_post}")

# Отправим DELETE запрос
response = requests.delete("http://127.0.0.1:5000/number/")
data = response.json()
operation_delete = data["operation"]
result_delete = data["result"]
print(f"DELETE запрос: Число: {result_delete}, Операция: {operation_delete}")

# Выполним операции и приведем результат к int
operations = [operation_get, operation_post, operation_delete]
results = [result_get, result_post, result_delete]
expression = f"{results[0]}"
for i in range(1, len(operations)):
    if operations[i] == 'add':
        expression += f" + {results[i]}"
    elif operations[i] == 'subtract':
        expression += f" - {results[i]}"
    elif operations[i] == 'multiply':
        expression += f" * {results[i]}"
    elif operations[i] == 'divide':
        expression += f" / {results[i]}"
result_final = int(eval(expression))
print(f"Выражение: {expression}, Результат: {result_final}")
