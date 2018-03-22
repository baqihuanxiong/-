import threading
import subprocess
import sys


def run(nf):
    for nt in range(100, 200, 100):
        for nr in range(3, 11):
            for i in range(20):
                sub = subprocess.Popen(r'python C:\Users\lw390\OneDrive\Documents\物流自动化技术\穿梭式货架叉车配比.py --task={} --fork={} --rack={}'.format(nt, nf, nr), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmd_out = sub.stdout.read()
                sub.stdout.close()
                cmd_error = sub.stderr.read()
                sub.stderr.close()
                sys.stdout.write(cmd_out.decode())
                sys.stdout.write(cmd_error.decode())


ts = [threading.Thread(target=run, args=(i,)) for i in range(2, 6)]
for t in ts:
    t.start()
for t in ts:
    t.join()
