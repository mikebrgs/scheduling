import main
import sys

read_path = "data/data1.txt"
write_path = "data/data1_sol.txt"
file_read = open(read_path, "r")
file_write = open(write_path, "w")
main.solve(file_read,file_write)
file_write.close()
file_write = open(write_path, "r")
print(file_write.read())
