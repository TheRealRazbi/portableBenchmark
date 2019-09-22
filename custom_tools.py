import win32gui
import win32com.client
import re
import psutil
import time
import GPUtil
import os
from datetime import datetime
from playsound import playsound
import statistics
import pyautogui


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(self._handle)

    def activate_e_hunt(self, after_delay=0.0):
        self.find_window_wildcard("The Equinox Hunt")
        self.set_foreground()
        time.sleep(after_delay)


def find_e_hunt_pid():
    """Returns the Equinox Hunt's PID"""
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo["name"] == "The Equinox Hunt.exe":
                return pinfo['pid']
    raise EnvironmentError("Equinox Hunt not found!")


def initialize_gpu_monitor():
    res = {}
    for gpu in GPUtil.getGPUs():
        pass
        res["GPU_NAME"] = gpu.name
        res["GPU_ID"] = gpu.id
        res["GPU_TOTAL_MEMORY"] = gpu.memoryTotal
        res["GPU_DRIVER_VERSION"] = gpu.driver
        return res


def sample_gpu():
    res = {}
    for gpu in GPUtil.getGPUs():
        pass
        res["GPU_LOAD"] = round(gpu.load*100, 4)
        res["GPU_MEMORY_USED"] = gpu.memoryUtil
        return res


class Benchmark:
    def __init__(self, cpu_brand, samples_to_take=10):
        if not os.path.exists("_lib") or not os.path.isfile("_lib/skypord.mp3"):
            raise FileNotFoundError("'_lib' not found or corrupted, aborting...")
        if not os.path.isfile("_lib/config.txt"):
            with open("_lib/config.txt", "w") as f:
                f.write("samples=10\nscreenshot_after_benchmark=False")
        else:
            if samples_to_take == 10:
                with open("_lib/config.txt", "r") as f:
                    samples_to_take = int(f.readline()[8:])
                    if samples_to_take < 1:
                        raise ValueError(f"Samples amount {samples_to_take} is invalid.")
            with open("_lib/config.txt", "r") as f:
                f.readline()
                line = f.readline()[27:].lower()
                if line == 'false':
                    self.allowed_screenshot = False
                elif line == 'true':
                    self.allowed_screenshot = True
                else:
                    print(f'No clue what {line} means. It must be either "false" or "true" caps insensitive')
                    print('Program will continue only after a restart if the problem was solved')
                    time.sleep(99999999)

        self.samples_to_take = samples_to_take


        self.cpu_brand = cpu_brand
        self.window_manager = WindowMgr()
        if not os.path.exists("benchmarks"):
            os.mkdir("benchmarks")
        now = datetime.now()
        self.now_str = now.strftime("%m-%d-%Y %H_%M_%S")
        self.simplified_path = os.path.join(f"benchmarks/{self.now_str}", "simplified")
        self.full_info_path = os.path.join(f"benchmarks/{self.now_str}", "full-info")
        self.simplified_txt_path = os.path.join(self.simplified_path, "basic_results.txt")
        self.full_info_txt_path = os.path.join(self.full_info_path, "advanced_results.txt")
        self.path_to_sound_effect = "_lib/Skypord.mp3"

        self.e_hunt = psutil.Process(find_e_hunt_pid())

        os.mkdir(os.path.join("benchmarks/", self.now_str))

        os.mkdir(self.simplified_path)

        with open(self.simplified_txt_path, "w"):
            pass

        os.mkdir(self.full_info_path)

        self.cpu_stats = {}
        self.gpu_stats = {}
        self.memory_stats = {}
        self.miscellaneous = {}

    @property
    def bench_results(self):
        return [self.cpu_stats, self.gpu_stats, self.memory_stats, self.miscellaneous]

    def clear_stats(self):
        self.cpu_stats = {}
        self.gpu_stats = {}
        self.memory_stats = {}
        self.miscellaneous = {}

    def get_samples(self, time_before=3):
        print("Starting Benchmark")
        true_now = time.time()
        self.window_manager.activate_e_hunt(time_before)
        for sample in range(self.samples_to_take):
            who_knows_now = time.time()
            self.cpu_stats[f'sample{sample}'] = self.sample_CPU()
            self.gpu_stats[f'sample{sample}'] = self.sample_GPU()
            self.memory_stats[f'sample{sample}'] = self.sample_RAM()
            print(f"Sample{sample} took {round(time.time()-who_knows_now, 2)} seconds to complete")

        cpu_usage_list = [i['CPU_USAGE'] for i in self.cpu_stats.values()]
        gpu_usage_list = [i['GPU_LOAD'] for i in self.gpu_stats.values()]
        ram_usage_list = [i['RAM_Dump_E_HUNT'].rss/1_048_576 for i in self.memory_stats.values()]
        average_cpu_usage = round(statistics.median(cpu_usage_list), 2)
        min_cpu_usage = round(min(cpu_usage_list), 2)
        max_cpu_usage = round(max(cpu_usage_list), 2)
        average_gpu_usage = int(statistics.median(gpu_usage_list))
        min_gpu_usage = int(min(gpu_usage_list))
        max_gpu_usage = int(max(gpu_usage_list))
        average_ram_usage = int(statistics.median(ram_usage_list))
        min_ram_usage = int(min(ram_usage_list))
        max_ram_usage = int(max(ram_usage_list))

        total_system_ram = round(psutil.virtual_memory().total/1_073_741_824, 2)

        self.screenshot_save()

        playsound(self.path_to_sound_effect)

        self.dump_everything()

        self.simplified_dump([f'{datetime.now().strftime("%m-%d-%Y %H:%M:%S")} | User : {self.e_hunt.username()}',
                              f'SAMPLES TAKEN : {self.samples_to_take}',
                              f'SCREENSHOT : {self.allowed_screenshot}',
                              f'\nCPU NAME : {self.cpu_brand}',
                              f'CPU MIN : {min_cpu_usage}%',
                              f'CPU MAX : {max_cpu_usage}%',
                              f'CPU AVG : {average_cpu_usage}%\n',
                              f'GPU NAME : {self.get_GPU_info()["GPU_NAME"]}',
                              f'GPU MIN : {min_gpu_usage}%',
                              f'GPU MAX : {max_gpu_usage}%',
                              f'GPU AVG : {average_gpu_usage}%\n',
                              f'TOTAL AVAILABLE SYSTEM RAM : {total_system_ram}GB',
                              f'RAM MIN : {min_ram_usage}MB',
                              f'RAM MAX : {max_ram_usage}MB',
                              f'RAM AVG : {average_ram_usage}MB'
                              ])

        self.finish()
        print(f"Benchmark took {round(time.time()-true_now, 2)} seconds to complete")

    def sample_CPU(self):
        return {"CPU_USAGE": round(self.e_hunt.cpu_percent(interval=0.75) / psutil.cpu_count(), 4),
                "IO_counters": self.e_hunt.io_counters(),
                "num_threads": self.e_hunt.num_threads(),
                "num_handles": self.e_hunt.num_handles()}

    @staticmethod
    def sample_GPU():
        return sample_gpu()

    def sample_RAM(self):
        return {"OVERALL_SYSTEM_RAM_USAGE": psutil.virtual_memory(),
                "RAM_Dump_E_HUNT": self.e_hunt.memory_info()}

    def dump_everything(self):
        data = [f'{datetime.now().strftime("%m-%d-%Y %H:%M:%S")} | User : {self.e_hunt.username()}\n\nFirst sample is : \n',
               [self.cpu_stats['sample0'],
                self.gpu_stats['sample0'],
                f'{self.memory_stats["sample0"]}'],
                "\n\nRest of samples [including first sample] : \n\n",
                ]

        with open(self.full_info_txt_path, "a") as f:
            for item in data:
                f.write(f"{item}")

            for sample_count in range(self.samples_to_take):
                data_to_write = self.cpu_stats[f"sample{sample_count}"]
                f.write(f"Sample {sample_count} : {data_to_write}")
                data_to_write = self.gpu_stats[f"sample{sample_count}"]
                f.write(f"{data_to_write}")
                data_to_write = self.memory_stats[f"sample{sample_count}"]
                f.write(f"{data_to_write}\n\n")

    def simplified_dump(self, data):
        with open(self.simplified_txt_path, "a") as f:
            for item in data:
                f.write(f"{item}\n")

    @staticmethod
    def get_GPU_info():
        return initialize_gpu_monitor()

    def finish(self):
        os.rename(os.path.join("benchmarks", self.now_str), os.path.join("benchmarks", f"{self.now_str} FINISHED"))

    def screenshot_save(self):
        if self.allowed_screenshot:
            pyautogui.screenshot(os.path.join("benchmarks", f'{self.now_str}/screenshot.png'))


if __name__ == '__main__':
    pass
    import cpuinfo
    from multiprocessing import freeze_support

    freeze_support()

    b = Benchmark(cpuinfo.get_cpu_info()["brand"])
    b.get_samples()
    print("BENCHMARK DONE")
    # e_hunt = psutil.Process(find_e_hunt_pid())
    # WindowMgr().activate_e_hunt(1.5)
    # bnk = Benchmark()
    # bnk.get_samples()




