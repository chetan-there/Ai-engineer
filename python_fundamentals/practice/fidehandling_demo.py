file = open("Ai-enginner\python_fundamentals\practice\demo.txt","r") #  r for read 

content = file.read()

print(content)

file = open("Ai-enginner\python_fundamentals\practice\demo.txt", "w") # w mode overwrites old content.

file.write("Hello demo ")

file = open("Ai-enginner\python_fundamentals\practice\demo.txt", "a") # a Old content remains.

file.write("\nLearning Python")

file = open("Ai-enginner\python_fundamentals\practice\demo.txt","r")

content = file.read()

print(content)

file.close 