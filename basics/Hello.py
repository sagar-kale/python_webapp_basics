# Data Types  = Int and Float
print("\n************* Data Types - Introduction - Int and Float************* \n")
answer = 42
pi = 3.14
ans = answer + pi
print(ans)
pi = int(pi)
print(pi)
# Data types  = string
print("\n************ Data Types - Introduction - String **************\n ")
hello = "hello"
print("capital string ", hello.capitalize())
print("is alphabetic = ", hello.isalpha())
print("is numeric = ", hello.isdigit())
print("Upper case = ", hello.upper())
sen = f"{hello} i am sagar and i am {answer} year old"

print("formatting sentence ", sen)
# Data Types - Boolean
print("\n************ Data types -Introduction - Boolean ********* \n")
isDigit = True
digit = 0
isalpha = False
alpha = 1  # other than 0 is have truthy value in if statement
print("Boolean True ##capital T is mandatory###", isDigit)
print("Boolean False numeric representation", digit)
print("Boolean True numeric representation", alpha)
print("Boolean False ##capital F is mandatory###", isalpha)

# If statements

print("\n*************** IF Statements **************")
if hello.isdigit() and not hello.isalpha():
    print("alpha is numeric")
else:
    print("alpha is not numeric")

number = 3
val = False

if number == 3 or val:
    print("Checking 'or' in if statement")
a = 1
b = 2
var = "bigger" if a > b else "Smaller"  # Turnery Operator in python
print(var)
print("\n*************** Lists **************")

student_names = ["Mark", "Jessica", "Katrina"]
if student_names:
    print("list is not empty")
else:
    print("list is empty")

print("printing last element of the list :::", student_names[-1])
print(len(student_names))
student_names[0] = "James"
student_names.append("Mark")
sorted(student_names)
print("printing first element of the list :::", student_names[0])
print("sorting list :: ", student_names)
print("Mark" in student_names)
bak_std = student_names.copy()
del student_names[1]
print(student_names, "And backup student list ::: ", bak_std)
print("slicing list ::", bak_std[2:])
print("slicing list  ignoring first and last element::", bak_std[1:-1])
#  bak_std.reverse()
print(bak_std)

# Looping statements

print("\n ***************** Looping Statements *************")
for item in bak_std:
    print(f"student name is {item}")
print("for range function")
x = 0
for index in range(10):  # range(start,stop,increment) is also there
    x += 10
    print(f"The value of x is {x}")
