student_list = []
str = "a b c d e f g h i j k l m n o p q r s t".split(" ")
for index in range(len(str)):
    student_list.append(str[index])
print(student_list)

for names in student_list:
    if names == 'b':
        print(f"found {names}")
        break
    print(f"currently testing :: {names}")

for names in student_list:
    if names == "c":
        continue
    print("testing ::" + names)

x = 0
while x < 10:
    print("Hello While iteration : ", x)
    x += 1
