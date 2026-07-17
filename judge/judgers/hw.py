import os, shutil, subprocess
from isolate_runner import isolate_run
from checkers import token


def judge(executable, exec_path, config, box_id=0):
    ... 