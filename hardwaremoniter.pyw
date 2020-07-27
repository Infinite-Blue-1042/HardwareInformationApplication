from tkinter import *
import tkinter.font as font
import psutil
import clr
import os
import win32api
import threading
import time

#List for hardware types and sensor types that our DLL can open
OHM_hwtypes = [ 'Mainboard', 'SuperIO', 'CPU', 'RAM', 'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'SSD' ]
OHM_sensortypes = [
 'Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level', 'Factor', 'Power', 'Data', 'SmallData'
]


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def init_OHM() :
    clr.AddReference('C:/Users/ketha/Downloads/PyTherm-master/OpenHardwareMonitorLib.dll')
    from OpenHardwareMonitor import Hardware
    hw = Hardware.Computer()
    hw.MainboardEnabled, hw.CPUEnabled, hw.RAMEnabled, hw.GPUEnabled, hw.HDDEnabled = True, True, True, True, True
    hw.Open()
    return hw


def fetch_data( handle ) :
    out = []
    for i in handle.Hardware :
        i.Update()
        for sensor in i.Sensors :
            thing = parse_sensor( sensor )
            if thing is not None :
                out.append( thing )
        for j in i.SubHardware :
            j.Update()
            for subsensor in j.Sensors :
                thing = parse_sensor( subsensor )
                out.append( thing )
    return out


def parse_sensor( snsr ) :
    if snsr.Value is not None :
        if snsr.SensorType == OHM_sensortypes.index( 'Temperature' ) :
            HwType = OHM_hwtypes[ snsr.Hardware.HardwareType ]
            return { "Type" : HwType, "Name" : snsr.Hardware.Name, "Sensor" : snsr.Name, "Reading" : u'%s\xb0C' % snsr.Value }


names = {}
temps = {}
nvidia = False


data = fetch_data(init_OHM())
for each in data:
    if each['Type'] == 'CPU':
        names['CPU Name'] = each['Name']
        temps['CPU'] = {}
    elif 'Gpu' in each['Type']:
        names['GPU Name'] = each['Name']
        temps['Gpu'] = {}
    elif each['Type'] == 'SSD':
        names['SSD Name'] = each['Name']
        temps['SSD'] = {}
for each in data:
    if each['Type'] == 'CPU':
        temps['CPU'][each['Sensor']] = each['Reading']
    elif 'Gpu' in each['Type']:
        if each['Type'] == 'GpuNvidia':
            nvidia = True
        else:
            temps['Gpu'][each['Sensor']] = each['Reading']
    elif each['Type'] == 'SSD':
        temps['SSD'][each['Sensor']] = each['Reading']

def refresh_tmps():
    global temps
    data = fetch_data(init_OHM())
    for each in data:
        if each['Type'] == 'CPU':
            temps['CPU'][each['Sensor']] = each['Reading']
        elif 'Gpu' in each['Type']:
            if each['Type'] != 'GpuNvidia':
                temps['Gpu'][each['Sensor']] = each['Reading']
        elif each['Type'] == 'SSD':
            temps['SSD'][each['Sensor']] = each['Reading']

class Ram:
    
    mem = psutil.virtual_memory()
    
    @staticmethod
    def total_mem(acc):
        return round(Ram.mem.total/1000000000, acc)
    
    @staticmethod
    def used_mem(acc):
        return round(Ram.mem.used/1000000000, acc)
    
    @staticmethod
    def free_mem(acc):
        return round(Ram.mem.available/1000000000, acc)
    
    @staticmethod
    def refresh():
        Ram.mem = psutil.virtual_memory()
        
        
def GetIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = None
    finally:
        s.close()
    return IP


master = Tk()
master.title("Hardware Moniter")

myFont = font.Font(family='Comfortaa', size=15)


for name, value in names.items():
    globals()[f'{name}L'] = Label(master, text=f'{name}: {value}', font=myFont)
    globals()[f'{name}L'].pack()


if nvidia:


    things = [i for i in list(os.popen('nvidia-smi').readlines())[8].split(' ') if i != '' and i != '|' and i != '/' and i != '!\n']

    nvidia_usage = StringVar()
    nvidia_usage.set(f'GPU Usage: {things[7]}')
    nvidia_usageL = Label(master, textvariable=nvidia_usage, font=myFont)
    nvidia_usageL.pack()

    nvidia_temp = StringVar()
    nvidia_temp.set(f'GPU Temp: {things[1].strip("C")}°C')
    nvidia_tempL = Label(master, textvariable=nvidia_temp, font=myFont)
    nvidia_tempL.pack()

    nvidia_memL = Label(master, text=f'GPU Mem: {things[6]}', font=myFont)
    nvidia_memL.pack()



for name, tmps in temps.items():
    for temp in tmps:
        globals()[temp] = StringVar()
        globals()[temp].set(f'{temp}: {tmps[temp]}')
        globals()[f'{name}L'] = Label(master, textvariable=globals()[temp], font=myFont)
        globals()[f'{name}L'].pack()


coresL = Label(master, text=f'Physical CPU Cores: {psutil.cpu_count(logical=False)}', font=myFont)
coresL.pack()

cores_HL = Label(master, text=f'Logical CPU Cores: {psutil.cpu_count()}', font=myFont)
cores_HL.pack()

cpu_usage = StringVar()
cpu_usageL = Label(master, textvariable=cpu_usage, font=myFont)
cpu_usageL.pack()

cpu_freq = StringVar()
cpu_freqL = Label(master, textvariable=cpu_freq, font=myFont)
cpu_freqL.pack()

total_ram = StringVar()
total_ram.set(f'Total Ram: {Ram.total_mem(2)}')
total_ramL = Label(master, textvariable=total_ram, font=myFont)
total_ramL.pack()

free_ram = StringVar()
free_ramL = Label(master, textvariable=free_ram, font=myFont)
free_ramL.pack()

used_ram = StringVar()
used_ramL = Label(master, textvariable=used_ram, font=myFont)
used_ramL.pack()

get_ip = StringVar()
get_ip.set(f'IP: {GetIP()}')
get_ipL = Label(master, textvariable=get_ip, font=myFont)
get_ipL.pack()

device = win32api.EnumDisplayDevices()
settings = win32api.EnumDisplaySettings(device.DeviceName, -1)
for varName in ['DisplayFrequency']:
    refresh_rateL = Label(master, text=f'Screen Refresh Rate: {getattr(settings, varName)} hertz', font=myFont)
    refresh_rateL.pack()
        

def command_nvidia_smi():

    global nvidia
    global nvidia_temp
    global nvidia_usage
    global to_set_nvidia_temp
    global to_set_nvidia_usage

    to_set_nvidia_temp = 0
    to_set_nvidia_usage = 0

    while True:
        if nvidia:
            things = [i for i in list(os.popen('nvidia-smi').readlines())[8].split(' ') if i != '' and i != '|' and i != '/' and i != '!\n']
            to_set_nvidia_temp = f'GPU Temp: {things[1].strip("C")}°C'
            to_set_nvidia_usage = f'GPU Usage: {things[7]}'
        refresh_tmps()
        Ram.refresh()
        time.sleep(0.4)        


def background_cpu_temp():
    global background_cpu_temp_value
    background_cpu_temp_value = f'CPU Usage: 0%'
    while True:
        background_cpu_temp_value = f'CPU Usage: {psutil.cpu_percent(1)}%'

t1 = threading.Thread(target=command_nvidia_smi, daemon=True)
t2 = threading.Thread(target=background_cpu_temp, daemon=True)

t1.start()
t2.start()


while True:

    cpu_usage.set(background_cpu_temp_value)
    free_ram.set(f'Free Ram: {Ram.free_mem(2)}')
    used_ram.set(f'Used Ram: {Ram.used_mem(2)}')
    
    try:
        master.update()
    except:
        break

    cpu_freq.set(f"CPU Frequency: {psutil.cpu_freq().current/1000:.2f}Ghz")

    for name, tmps in temps.items():
        for temp in tmps:
            globals()[temp].set(f'{temp}: {tmps[temp]}')

    nvidia_temp.set(to_set_nvidia_temp)
    nvidia_usage.set(to_set_nvidia_usage)
    
    time.sleep(0.2)
