# This Python file uses the following encoding: utf-8
from custom_tools import WindowMgr, find_e_hunt_pid, Benchmark
from getkeys import key_check
import time

BENCHMARKS = 1


def create_benchmark():
    try:
        global BENCHMARKS
        bnk = Benchmark(CPU_NAME)
        bnk.get_samples()
        del bnk
        print(f"BENCHMARK DONE | SO FAR : {BENCHMARKS} COMPLETED")
        BENCHMARKS += 1
    except Exception as e:
        print(f'The Error : {e} stopped the benchmark , but you can still start new benchmarks')

# def listen_process(key):
#     pass
#     if key == KeyCode(12):
#         create_benchmark()


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    import cpuinfo
    CPU_NAME = cpuinfo.get_cpu_info()["brand"]

    while True:
        keys = key_check()
        if 'P' in keys:
            create_benchmark()
            keys = []
        # elif 'O' in keys:
        #     raise KeyboardInterrupt("The Exit key 'O' was pressed")
        time.sleep(0.15)
    # b = Benchmark(CPU_NAME, samples_to_take=3)
    # b.get_samples()
    # print("BENCHMARK DONE")



