import platform
import subprocess
import re
import json
import os
import psutil

class ProcessListEncoder (json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ProcessInfo):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

class ProcessInfo:
	def __init__(self, name, pid):
		self.name = name
		self.pid = pid
		self.is_prime = False

def as_ProcessInfo(dct):
	result = ProcessInfo(dct['name'], dct['pid'])
	result.is_prime = dct['is_prime']
	return result

def is_prime(x):
	if x==1:
		return False
	for i in range(2, (x//2)+1):
		if x % i == 0:
			return False
	return True

def get_process_list(name_filter):
	output = []
	for proc in psutil.process_iter(['pid', 'name']):
		check_name = re.match("("+name_filter+")", proc.info['name'])
		if check_name != None:
			line = ProcessInfo(proc.info['name'], proc.pid)
			line.is_prime = is_prime(line.pid)
			output.append(line)
	return output

def read_process_list(input_str):
	return json.loads(input_str, object_hook = as_ProcessInfo)

def check_process_list(process_list):
	for process in process_list:
		if process.is_prime != is_prime(process.pid):
			print(f"Для {process.name} процесса найдена ошибка.")
			if process.is_prime:
				print(f"Число(PID) {process.pid} на самом деле составное, а в файле написано простое.")
			else:
				print(f"Число(PID) {process.pid} на самом деле простое, а в файле написано составное.")
			print("\n")

def main(file_dir = "/tmp/", file_name = "output.json", mode = "create"):
	output_file_dir		= os.getenv("OUTPUT_DIR",  file_dir)
	output_file_name 	= os.getenv("OUTPUT_FILE_NAME",  file_name)
	name_filter		= os.getenv("FILTER", ".*")
	mode			= os.getenv("MODE", mode)

	if mode == "create":
		process_list = get_process_list(name_filter)
		with open(output_file_dir + output_file_name,  "w") as output_file:
			output_file.write(json.dumps(process_list, cls=ProcessListEncoder))
	elif mode == "check":
		process_list = read_process_list(open(output_file_dir + output_file_name).read())
		check_process_list(process_list)
	else:
		print("Invalid mode")
		Exception("Invalid mode")


main()
