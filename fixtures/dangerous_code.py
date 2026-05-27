import os
import subprocess


def run_user_input(user_input):
    result = eval(user_input)
    return result


def execute_code(code_string):
    exec(code_string)


def run_command(command):
    os.system(command)


def run_shell(cmd):
    subprocess.call(cmd, shell=True)


def dynamic_import(module_name):
    module = __import__(module_name)
    return module


user_cmd = "print('hello')"
run_user_input(user_cmd)

code = "x = 1 + 2"
execute_code(code)

run_command("echo hello")
run_shell("dir")
