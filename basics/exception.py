student = {
    "name": "sagar",
    "id": 1
}
try:
    val = student["last_name"]
except Exception as error:
    print("Key does not exist in dictionary")
    print(error)
print("this code executes")
