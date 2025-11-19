import sys
import platform
import time
import ctypes
import json
import os
import subprocess
import shutil
import threading
import gc
import heapq
import weakref
import math
from ctypes import wintypes
from collections import defaultdict, deque
from typing import Optional, List, Dict, Set, Any, Callable
if platform.system() != 'Windows':
    sys.exit(1)
if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_uint64
else:
    ULONG_PTR = ctypes.c_uint32
ULONGLONG = ctypes.c_ulonglong
import psutil
import win32process
import win32gui
import win32con
import win32api
import win32job
import win32file
import pywintypes
import winreg
from PIL import Image, ImageDraw, ImageFont
import pystray
import clr
clr.AddReference(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LibreHardwareMonitorLib.dll'))
from LibreHardwareMonitor import Hardware
TEMP_MONITORING_AVAILABLE = True
from gui_manager import ProcessManagerGUI
GUI_AVAILABLE = True
from utils import measure_time, validate_pid, safe_join_path
UTILS_AVAILABLE = True
HIGH_PERFORMANCE_POWER_PLAN_GUID = '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
NVME_OPTIMAL_QUEUE_DEPTH = 256
NVME_MAX_QUEUE_DEPTH = 1024
TCP_OPTIMAL_WINDOW_SIZE = 65535
NETWORK_THROTTLING_DISABLED = 4294967295
THERMAL_THROTTLING_CPU_THRESHOLD = 80
BBR_ALGORITHM = 2
HARDWARE_SCHEDULING_MODE_2 = 2
DNS_CACHE_TTL_24_HOURS = 86400
DNS_NEGATIVE_CACHE_TTL_1_HOUR = 3600
MS_TO_100NS = 10000
TEMP_DELTA_PER_LOAD = 15
TEMP_CENTERING_OFFSET = 7.5
DPC_TIMEOUT_DISABLED = 0
DPC_WATCHDOG_PROFILE_OFFSET = 1
DPC_QUEUE_DEPTH = 4
CORE_OVERLOAD_THRESHOLD = 80
RESET_EXECUTION_COUNT_THRESHOLD = 1000000
RESET_EXECUTION_COUNT_VALUE = 1000
MAX_PROCESS_SNAPSHOT_ITERATIONS = 10000
MAX_CACHE_SIZE = 10000
CACHE_CLEANUP_SIZE = 5000
WMIC_COMMAND_PATH = 'wmic'
PRIORITY_CLASSES = {'IDLE': win32process.IDLE_PRIORITY_CLASS, 'BELOW_NORMAL': win32process.BELOW_NORMAL_PRIORITY_CLASS, 'NORMAL': win32process.NORMAL_PRIORITY_CLASS, 'ABOVE_NORMAL': win32process.ABOVE_NORMAL_PRIORITY_CLASS, 'HIGH': win32process.HIGH_PRIORITY_CLASS, 'REALTIME': win32process.REALTIME_PRIORITY_CLASS}
PROCESS_ALL_ACCESS = 2035711
PROCESS_SET_INFORMATION = 512
PROCESS_QUERY_INFORMATION = 1024
PROCESS_QUERY_LIMITED_INFORMATION = 4096
PROCESS_SET_QUOTA = 256
PROCESS_VM_READ = 16
SE_DEBUG_NAME = 'SeDebugPrivilege'
SE_PRIVILEGE_ENABLED = 2
TOKEN_ADJUST_PRIVILEGES = 32
TOKEN_QUERY = 8
ProcessPagePriority = 39
PAGE_PRIORITY_NORMAL = 5
PAGE_PRIORITY_MEDIUM = 3
PAGE_PRIORITY_LOW = 1
EVENT_SYSTEM_FOREGROUND = 3
WINEVENT_OUTOFCONTEXT = 0
JOB_OBJECT_CPU_RATE_CONTROL_ENABLE = 1
JOB_OBJECT_CPU_RATE_CONTROL_WEIGHT_BASED = 2
JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP = 4
JOB_OBJECT_CPU_RATE_CONTROL_MIN_MAX_RATE = 16
RelationProcessorCore = 0
RelationNumaNode = 1
RelationCache = 2
RelationProcessorPackage = 3
RelationGroup = 4
RelationAll = 65535
CacheUnified = 0
CacheInstruction = 1
CacheData = 2
CacheTrace = 3
TH32CS_SNAPTHREAD = 4
TH32CS_SNAPPROCESS = 2
THREAD_SET_INFORMATION = 32
THREAD_QUERY_INFORMATION = 64
THREAD_SET_LIMITED_INFORMATION = 1024
ThreadIoPriority = 43
ProcessIoPriority = 33
PROCESS_POWER_THROTTLING_EXECUTION_SPEED = 1
PROCESS_POWER_THROTTLING_IGNORE_TIMER_RESOLUTION = 4
ProcessPowerThrottling = 77
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
SE_LOCK_MEMORY_NAME = 'SeLockMemoryPrivilege'
MEM_LARGE_PAGES = 536870912
MEM_COMMIT = 4096
MEM_RESERVE = 8192
PAGE_READWRITE = 4
ProcessMemoryPriority = 40
MEMORY_PRIORITY_VERY_LOW = 1
MEMORY_PRIORITY_LOW = 2
MEMORY_PRIORITY_MEDIUM = 3
MEMORY_PRIORITY_BELOW_NORMAL = 4
MEMORY_PRIORITY_NORMAL = 5
ProcessWorkingSetWatchEx = 42
FILE_FLAG_SEQUENTIAL_SCAN = 134217728
IOCTL_STORAGE_QUERY_PROPERTY = 2954240
ThreadPowerThrottling = 49
THREAD_POWER_THROTTLING_EXECUTION_SPEED = 1
THREAD_POWER_THROTTLING_VALID_FLAGS = 1
SystemProcessorPowerInformation = 61
ProcessorStateHandler = 1
MEM_PHYSICAL = 4194304
AWE_ENABLED_FLAG = 131072
QUOTA_LIMITS_HARDWS_MIN_ENABLE = 1
QUOTA_LIMITS_HARDWS_MAX_ENABLE = 2
SystemResponsivenessKey = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile'
class LUID(ctypes.Structure):
    _fields_ = [('LowPart', wintypes.DWORD), ('HighPart', wintypes.LONG)]
class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('Luid', LUID), ('Attributes', wintypes.DWORD)]
class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [('PrivilegeCount', wintypes.DWORD), ('Privileges', LUID_AND_ATTRIBUTES * 1)]
class CACHE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [('Level', wintypes.BYTE), ('Associativity', wintypes.BYTE), ('LineSize', wintypes.WORD), ('Size', wintypes.DWORD), ('Type', wintypes.BYTE)]
class SYSTEM_LOGICAL_PROCESSOR_INFORMATION_UNION(ctypes.Union):
    _fields_ = [('ProcessorCore_Flags', wintypes.DWORD), ('NumaNode_NodeNumber', wintypes.DWORD), ('Cache', CACHE_DESCRIPTOR), ('Reserved', ULONGLONG * 2)]
class SYSTEM_LOGICAL_PROCESSOR_INFORMATION(ctypes.Structure):
    _fields_ = [('ProcessorMask', ULONG_PTR), ('Relationship', wintypes.DWORD), ('u', SYSTEM_LOGICAL_PROCESSOR_INFORMATION_UNION)]
class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD), ('th32DefaultHeapID', ctypes.POINTER(wintypes.ULONG)), ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD), ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', wintypes.LONG), ('dwFlags', wintypes.DWORD), ('szExeFile', ctypes.c_wchar * 260)]
class THREADENTRY32(ctypes.Structure):
    _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ThreadID', wintypes.DWORD), ('th32OwnerProcessID', wintypes.DWORD), ('tpBasePri', wintypes.LONG), ('tpDeltaPri', wintypes.LONG), ('dwFlags', wintypes.DWORD)]
class PROCESSOR_POWER_INFORMATION(ctypes.Structure):
    _fields_ = [('Number', wintypes.ULONG), ('MaxMhz', wintypes.ULONG), ('CurrentMhz', wintypes.ULONG), ('MhzLimit', wintypes.ULONG), ('MaxIdleState', wintypes.ULONG), ('CurrentIdleState', wintypes.ULONG)]
class GROUP_AFFINITY(ctypes.Structure):
    _fields_ = [('Mask', ULONG_PTR), ('Group', wintypes.WORD), ('Reserved', wintypes.WORD * 3)]
class PROCESSOR_RELATIONSHIP(ctypes.Structure):
    _fields_ = [('Flags', wintypes.BYTE), ('EfficiencyClass', wintypes.BYTE), ('Reserved', wintypes.BYTE * 20), ('GroupCount', wintypes.WORD), ('GroupMask', GROUP_AFFINITY * 1)]
class SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX_UNION(ctypes.Union):
    _fields_ = [('Processor', PROCESSOR_RELATIONSHIP)]
class SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX(ctypes.Structure):
    _fields_ = [('Relationship', wintypes.DWORD), ('Size', wintypes.DWORD), ('u', SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX_UNION)]
class PROCESS_POWER_THROTTLING_STATE(ctypes.Structure):
    _fields_ = [('Version', wintypes.ULONG), ('ControlMask', wintypes.ULONG), ('StateMask', wintypes.ULONG)]
class MEMORY_PRIORITY_INFORMATION(ctypes.Structure):
    _fields_ = [('MemoryPriority', wintypes.ULONG)]
class THREAD_POWER_THROTTLING_STATE(ctypes.Structure):
    _fields_ = [('Version', wintypes.ULONG), ('ControlMask', wintypes.ULONG), ('StateMask', wintypes.ULONG)]
class FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', wintypes.DWORD), ('dwHighDateTime', wintypes.DWORD)]
class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [('dwFileAttributes', wintypes.DWORD), ('ftCreationTime', FILETIME), ('ftLastAccessTime', FILETIME), ('ftLastWriteTime', FILETIME), ('dwVolumeSerialNumber', wintypes.DWORD), ('nFileSizeHigh', wintypes.DWORD), ('nFileSizeLow', wintypes.DWORD), ('nNumberOfLinks', wintypes.DWORD), ('nFileIndexHigh', wintypes.DWORD), ('nFileIndexLow', wintypes.DWORD)]
class SYSTEM_CACHE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('CurrentSize', ctypes.c_size_t),
        ('PeakSize', ctypes.c_size_t),
        ('PageFaultCount', wintypes.ULONG),
        ('MinimumWorkingSet', ctypes.c_size_t),
        ('MaximumWorkingSet', ctypes.c_size_t),
        ('Unused1', ctypes.c_size_t),
        ('Unused2', ctypes.c_size_t),
        ('Unused3', ctypes.c_size_t),
        ('Unused4', ctypes.c_size_t)
    ]
SystemFileCacheInformation = 21
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
ntdll = ctypes.WinDLL('ntdll', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)
timeapi = ctypes.WinDLL('winmm.dll', use_last_error=True)
powrprof = ctypes.WinDLL('powrprof.dll', use_last_error=True)
NtSetInformationProcess = ntdll.NtSetInformationProcess
NtSetInformationProcess.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
NtSetInformationProcess.restype = ctypes.c_long
NtSetInformationThread = ntdll.NtSetInformationThread
NtSetInformationThread.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
NtSetInformationThread.restype = ctypes.c_long
NtQueryInformationProcess = ntdll.NtQueryInformationProcess
NtQueryInformationProcess.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
NtQueryInformationProcess.restype = ctypes.c_long
NtSuspendProcess = ntdll.NtSuspendProcess
NtSuspendProcess.argtypes = [wintypes.HANDLE]
NtSuspendProcess.restype = ctypes.c_long
NtResumeProcess = ntdll.NtResumeProcess
NtResumeProcess.argtypes = [wintypes.HANDLE]
NtResumeProcess.restype = ctypes.c_long
NtQuerySystemInformation = ntdll.NtQuerySystemInformation
NtQuerySystemInformation.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
NtQuerySystemInformation.restype = ctypes.c_long
kernel32.SetProcessPriorityBoost.argtypes = [wintypes.HANDLE, wintypes.BOOL]
kernel32.SetProcessPriorityBoost.restype = wintypes.BOOL
kernel32.GetLogicalProcessorInformation.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
kernel32.GetLogicalProcessorInformation.restype = wintypes.BOOL
kernel32.GetLogicalProcessorInformationEx.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
kernel32.GetLogicalProcessorInformationEx.restype = wintypes.BOOL
kernel32.SetProcessWorkingSetSize.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t]
kernel32.SetProcessWorkingSetSize.restype = wintypes.BOOL
kernel32.SetProcessWorkingSetSizeEx.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t, wintypes.DWORD]
kernel32.SetProcessWorkingSetSizeEx.restype = wintypes.BOOL
kernel32.SetProcessInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
kernel32.SetProcessInformation.restype = wintypes.BOOL
kernel32.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ULONG_PTR]
kernel32.SetProcessAffinityMask.restype = ULONG_PTR
kernel32.GetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.POINTER(ULONG_PTR), ctypes.POINTER(ULONG_PTR)]
kernel32.GetProcessAffinityMask.restype = wintypes.BOOL
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD
kernel32.SetThreadIdealProcessor.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.SetThreadIdealProcessor.restype = wintypes.DWORD
kernel32.SetThreadAffinityMask.argtypes = [wintypes.HANDLE, ULONG_PTR]
kernel32.SetThreadAffinityMask.restype = ULONG_PTR
kernel32.GetNumaProcessorNode.argtypes = [ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte)]
kernel32.GetNumaProcessorNode.restype = wintypes.BOOL
kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32NextW.restype = wintypes.BOOL
kernel32.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
kernel32.Thread32First.restype = wintypes.BOOL
kernel32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(THREADENTRY32)]
kernel32.Thread32Next.restype = wintypes.BOOL
kernel32.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenThread.restype = wintypes.HANDLE
timeapi.timeBeginPeriod.argtypes = [ctypes.c_uint]
timeapi.timeBeginPeriod.restype = ctypes.c_uint
timeapi.timeEndPeriod.argtypes = [ctypes.c_uint]
timeapi.timeEndPeriod.restype = ctypes.c_uint
kernel32.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(BY_HANDLE_FILE_INFORMATION)]
kernel32.GetFileInformationByHandle.restype = wintypes.BOOL
WinEventProcType = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND, wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
class CircularBuffer:
    __slots__ = ('_buffer', '_size', '_head', '_count')
    def __init__(self, maxlen):
        self._buffer = [None] * maxlen
        self._size = maxlen
        self._head = 0
        self._count = 0
    def append(self, item):
        self._buffer[self._head] = item
        self._head = (self._head + 1) % self._size
        if self._count < self._size:
            self._count += 1
    def __len__(self):
        return self._count
    def __iter__(self):
        if self._count < self._size:
            for i in range(self._count):
                yield self._buffer[i]
        else:
            for i in range(self._size):
                idx = (self._head + i) % self._size
                yield self._buffer[idx]
    def clear(self):
        self._head = 0
        self._count = 0
        self._buffer = [None] * self._size
class CTypesStructurePool:
    __slots__ = ('_pools', 'lock', 'max_pool_size')
    def __init__(self, max_pool_size=10):
        self._pools = {}
        self.lock = threading.RLock()
        self.max_pool_size = max_pool_size
    def get_structure(self, structure_type):
        with self.lock:
            type_name = structure_type.__name__
            if type_name not in self._pools:
                self._pools[type_name] = []
            pool = self._pools[type_name]
            if pool:
                return pool.pop()
            else:
                return structure_type()
    def return_structure(self, structure):
        with self.lock:
            type_name = type(structure).__name__
            if type_name not in self._pools:
                self._pools[type_name] = []
            pool = self._pools[type_name]
            if len(pool) < self.max_pool_size:
                pool.append(structure)
class SimpleBloomFilter:
    __slots__ = ('_bit_array', '_size', '_hash_count')
    def __init__(self, expected_elements=100, false_positive_rate=0.01):
        self._size = int(-(expected_elements * math.log(false_positive_rate)) / math.log(2) ** 2)
        self._hash_count = int(self._size / expected_elements * math.log(2))
        self._bit_array = [False] * self._size
    def _hashes(self, item):
        h1 = hash(item)
        h2 = h1 >> 16 ^ h1 << 16
        for i in range(self._hash_count):
            yield ((h1 + i * h2) % self._size)
    def add(self, item):
        for h in self._hashes(item):
            self._bit_array[h] = True
    def contains(self, item):
        return all((self._bit_array[h] for h in self._hashes(item)))
def binary_search_pid(sorted_pid_list, target_pid):
    left, right = (0, len(sorted_pid_list) - 1)
    while left <= right:
        mid = (left + right) // 2
        if sorted_pid_list[mid] == target_pid:
            return mid
        elif sorted_pid_list[mid] < target_pid:
            left = mid + 1
        else:
            right = mid - 1
    return -1
thread_local_data = threading.local()
class RegistryWriteBuffer:
    __slots__ = ('buffer', 'lock', 'flush_interval', 'last_flush', 'max_buffer_size')
    def __init__(self, flush_interval=5.0, max_buffer_size=50):
        self.buffer = []
        self.lock = threading.RLock()
        self.flush_interval = flush_interval
        self.last_flush = time.time()
        self.max_buffer_size = max_buffer_size
    def queue_write(self, key_path, value_name, value_type, value_data, hkey=None):
        with self.lock:
            if not key_path or not isinstance(key_path, str):
                return
            if not isinstance(value_name, str):
                return
            if hkey is None:
                hkey = winreg.HKEY_LOCAL_MACHINE
            self.buffer.append((hkey, key_path, value_name, value_type, value_data))
            if len(self.buffer) >= self.max_buffer_size:
                self.flush()
            elif time.time() - self.last_flush >= self.flush_interval:
                self.flush()
    def flush(self):
        with self.lock:
            if not self.buffer:
                return
            for hkey, key_path, value_name, value_type, value_data in self.buffer:
                key = None
                key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            self.buffer.clear()
            self.last_flush = time.time()
def memoize_with_ttl(ttl_seconds=300):
    def decorator(func):
        cache = {}
        cache_times = {}
        lock = threading.RLock()
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            current_time = time.time()
            with lock:
                if key in cache:
                    if current_time - cache_times[key] < ttl_seconds:
                        return cache[key]
                    else:
                        del cache[key]
                        del cache_times[key]
                result = func(*args, **kwargs)
                cache[key] = result
                cache_times[key] = current_time
                if len(cache) > 1000:
                    cutoff_time = current_time - ttl_seconds
                    expired_keys = [k for k, t in cache_times.items() if t < cutoff_time]
                    for old_key in expired_keys:
                        del cache[old_key]
                        del cache_times[old_key]
                    if len(cache) > 1000:
                        items_to_remove = len(cache) // 2
                        keys_to_remove = list(cache_times.keys())[:items_to_remove]
                        for old_key in keys_to_remove:
                            del cache[old_key]
                            del cache_times[old_key]
                return result
        return wrapper
    return decorator
class HardwareDetector:
    def __init__(self):
        self.cpu_vendor = None
        self.cpu_model = None
        self.gpu_vendor = None
        self.storage_types = set()
        self._detect_hardware()
    def _detect_hardware(self):
        self._detect_cpu()
        self._detect_gpu()
        self._detect_storage()
    def _get_wmic_cmd(self):
        wmic_cmd = shutil.which(WMIC_COMMAND_PATH)
        if not wmic_cmd:
            wmic_cmd = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'wmic.exe')
            if not os.path.exists(wmic_cmd):
                return None
        return wmic_cmd
    def _detect_cpu(self):
        wmic_cmd = self._get_wmic_cmd()
        if not wmic_cmd:
            return
        result = subprocess.run([wmic_cmd, 'cpu', 'get', 'manufacturer,name', '/format:list'], capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0)
        if result.returncode == 0:
            cpu_info = result.stdout
            if 'Intel' in cpu_info:
                self.cpu_vendor = 'Intel'
            elif 'AMD' in cpu_info or 'Advanced Micro Devices' in cpu_info:
                self.cpu_vendor = 'AMD'
            for line in cpu_info.split('\n'):
                if line.startswith('Name='):
                    self.cpu_model = line.split('=', 1)[1].strip()
                    break
    def _detect_gpu(self):
        wmic_cmd = self._get_wmic_cmd()
        if not wmic_cmd:
            return
        result = subprocess.run([wmic_cmd, 'path', 'win32_VideoController', 'get', 'name', '/format:list'], capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0)
        if result.returncode == 0:
            gpu_info = result.stdout
            if 'NVIDIA' in gpu_info or 'GeForce' in gpu_info or 'Quadro' in gpu_info:
                self.gpu_vendor = 'NVIDIA'
            elif 'AMD' in gpu_info or 'Radeon' in gpu_info:
                self.gpu_vendor = 'AMD'
            elif 'Intel' in gpu_info:
                self.gpu_vendor = 'Intel'
    def _detect_storage(self):
        wmic_cmd = self._get_wmic_cmd()
        if not wmic_cmd:
            return
        result = subprocess.run([wmic_cmd, 'diskdrive', 'get', 'MediaType,Model,InterfaceType', '/format:list'], capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0)
        if result.returncode == 0:
            disk_info = result.stdout
            if 'SSD' in disk_info or 'Solid State' in disk_info:
                self.storage_types.add('SSD')
            if 'HDD' in disk_info or 'Fixed hard disk' in disk_info:
                self.storage_types.add('HDD')
            if 'NVMe' in disk_info or 'NVME' in disk_info:
                self.storage_types.add('NVMe')
    def is_intel_cpu(self):
        return self.cpu_vendor == 'Intel'
    def is_amd_cpu(self):
        return self.cpu_vendor == 'AMD'
    def is_nvidia_gpu(self):
        return self.gpu_vendor == 'NVIDIA'
    def is_amd_gpu(self):
        return self.gpu_vendor == 'AMD'
    def has_nvme(self):
        return 'NVMe' in self.storage_types
    def has_ssd(self):
        return 'SSD' in self.storage_types
class OptimizationDecisionCache:
    __slots__ = ('cache', 'ttl', 'lock', 'stats')
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds
        self.lock = threading.RLock()
        self.stats = {'hits': 0, 'misses': 0, 'expirations': 0}
    def get(self, pid, decision_type):
        with self.lock:
            key = (pid, decision_type)
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl:
                    self.stats['hits'] += 1
                    return entry['value']
                else:
                    del self.cache[key]
                    self.stats['expirations'] += 1
            self.stats['misses'] += 1
            return None
    def set(self, pid, decision_type, value):
        with self.lock:
            if not isinstance(pid, int) or pid <= 0:
                return
            if not decision_type or not isinstance(decision_type, str):
                return
            key = (pid, decision_type)
            self.cache[key] = {'value': value, 'timestamp': time.time()}
            if len(self.cache) > MAX_CACHE_SIZE:
                current_time = time.time()
                expired_keys = [k for k, v in self.cache.items() if current_time - v['timestamp'] >= self.ttl]
                for old_key in expired_keys:
                    del self.cache[old_key]
                if len(self.cache) > MAX_CACHE_SIZE:
                    keys_to_remove = list(self.cache.keys())[:CACHE_CLEANUP_SIZE]
                    for old_key in keys_to_remove:
                        del self.cache[old_key]
    def invalidate(self, pid):
        with self.lock:
            keys_to_remove = [k for k in self.cache.keys() if k[0] == pid]
            for key in keys_to_remove:
                del self.cache[key]
    def cleanup_expired(self):
        with self.lock:
            current_time = time.time()
            keys_to_remove = []
            for k, v in list(self.cache.items()):
                if current_time - v['timestamp'] >= self.ttl:
                    keys_to_remove.append(k)
            for key in keys_to_remove:
                del self.cache[key]
                self.stats['expirations'] += 1
class IntegrityValidator:
    __slots__ = ('handle_cache', 'lock', 'validation_history', 'batch_queue')
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.validation_history = defaultdict(list)
        self.batch_queue = []
    def validate_priority(self, pid, expected_priority):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_QUERY_INFORMATION)
            if handle:
                actual_priority = win32process.GetPriorityClass(handle)
                result = actual_priority == expected_priority
                self.validation_history[pid].append({'type': 'priority', 'expected': expected_priority, 'actual': actual_priority, 'success': result, 'timestamp': time.time()})
                return result
            return False
    def validate_affinity(self, pid, expected_cores):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_QUERY_INFORMATION)
            if handle:
                actual_cores = get_process_affinity_direct(handle)
                if actual_cores:
                    result = set(actual_cores) == set(expected_cores)
                    self.validation_history[pid].append({'type': 'affinity', 'expected': expected_cores, 'actual': actual_cores, 'success': result, 'timestamp': time.time()})
                    return result
            return False
    def get_validation_stats(self, pid):
        with self.lock:
            if pid in self.validation_history:
                history = self.validation_history[pid]
                total = len(history)
                successes = sum((1 for v in history if v['success']))
                return {'total': total, 'successes': successes, 'success_rate': successes / total if total > 0 else 0}
            return None
    def queue_validation(self, pid, validation_type, expected_value):
        with self.lock:
            self.batch_queue.append((pid, validation_type, expected_value))
    def process_batch_validations(self):
        with self.lock:
            if not self.batch_queue:
                return {}
            results = {}
            for pid, val_type, expected in self.batch_queue:
                if val_type == 'priority':
                    results[pid, val_type] = self.validate_priority(pid, expected)
                elif val_type == 'affinity':
                    results[pid, val_type] = self.validate_affinity(pid, expected)
            self.batch_queue.clear()
            return results
class ProcessSuspensionManager:
    __slots__ = ('suspended_processes', 'inactivity_threshold', 'lock', 'stats', 'suspension_decision_cache')
    def __init__(self):
        self.suspended_processes = {}
        self.inactivity_threshold = 900
        self.lock = threading.RLock()
        self.stats = {'suspended': 0, 'resumed': 0}
        self.suspension_decision_cache = {}
    def should_suspend(self, pid, last_foreground_time):
        with self.lock:
            if pid in self.suspended_processes:
                return False
            cache_key = (pid, int(last_foreground_time / 60))
            if cache_key in self.suspension_decision_cache:
                return self.suspension_decision_cache[cache_key]
            time_inactive = time.time() - last_foreground_time
            result = time_inactive > self.inactivity_threshold
            self.suspension_decision_cache[cache_key] = result
            if len(self.suspension_decision_cache) > 1000:
                keys_to_keep = list(self.suspension_decision_cache.keys())[-500:]
                self.suspension_decision_cache = {k: self.suspension_decision_cache[k] for k in keys_to_keep}
            return result
    def suspend_process(self, pid):
        with self.lock:
            handle = win32api.OpenProcess(win32con.PROCESS_SUSPEND_RESUME, False, pid)
            if handle:
                ntdll.NtSuspendProcess(handle)
                self.suspended_processes[pid] = time.time()
                self.stats['suspended'] += 1
                return True
            return False
    def resume_process(self, pid):
        with self.lock:
            if pid not in self.suspended_processes:
                return False
            handle = win32api.OpenProcess(win32con.PROCESS_SUSPEND_RESUME, False, pid)
            if handle:
                ntdll.NtResumeProcess(handle)
                del self.suspended_processes[pid]
                self.stats['resumed'] += 1
                return True
            return False
class SystemResponsivenessController:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_value = 20
    def set_responsiveness(self, value):
        with self.lock:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SystemResponsivenessKey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'SystemResponsiveness', 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            self.current_value = value
            return True
            return False
    def set_for_performance(self):
        return self.set_responsiveness(0)
    def set_for_balanced(self):
        return self.set_responsiveness(20)
    def set_for_background(self):
        return self.set_responsiveness(40)
class AdvancedTimerCoalescer:
    def __init__(self, base_resolution_ms=1):
        self.base_resolution_ms = base_resolution_ms
        self.timer_resolution_active = False
        self.task_registry = {}
        self.execution_history = defaultdict(deque)
        self.lock = threading.RLock()
        self.performance_counter_freq = self._get_performance_frequency()
        self._activate_high_resolution_timer()
        self.stats = {'total_coalesced': 0, 'total_executed': 0, 'avg_coalescence_rate': 0.0}
    def _get_performance_frequency(self):
        freq = ctypes.c_int64()
        kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        return freq.value if freq.value > 0 else 1000000
    def _activate_high_resolution_timer(self):
        result = timeapi.timeBeginPeriod(self.base_resolution_ms)
        if result == 0:
            self.timer_resolution_active = True
    def _deactivate_high_resolution_timer(self):
        if self.timer_resolution_active:
            timeapi.timeEndPeriod(self.base_resolution_ms)
            self.timer_resolution_active = False
    def register_task(self, name, interval_ms, priority=5, adaptive=True, coalescence_window_ms=None, execution_budget_ms=None):
        with self.lock:
            if coalescence_window_ms is None:
                coalescence_window_ms = max(1, interval_ms * 0.1)
            if execution_budget_ms is None:
                execution_budget_ms = max(1, interval_ms * 0.5)
            self.task_registry[name] = {'interval_ms': interval_ms, 'priority': priority, 'adaptive': adaptive, 'coalescence_window_ms': coalescence_window_ms, 'execution_budget_ms': execution_budget_ms, 'last_execution': 0, 'next_execution': time.perf_counter() + interval_ms / 1000.0, 'execution_count': 0, 'total_execution_time_ms': 0, 'avg_execution_time_ms': 0, 'adaptive_multiplier': 1.0}
    def should_execute(self, task_name):
        with self.lock:
            if task_name not in self.task_registry:
                return (False, 0.0)
            task = self.task_registry[task_name]
            current_time = time.perf_counter()
            time_since_last = current_time - task['last_execution']
            time_until_next = task['next_execution'] - current_time
            if time_until_next <= 0:
                urgency = min(10.0, abs(time_until_next) * 1000.0 / task['interval_ms'])
                return (True, urgency)
            if time_until_next <= task['coalescence_window_ms'] / 1000.0:
                proximity_factor = 1.0 - time_until_next / (task['coalescence_window_ms'] / 1000.0)
                urgency = task['priority'] * proximity_factor
                return (True, urgency)
            return (False, 0.0)
    def mark_executed(self, task_name, execution_time_ms):
        with self.lock:
            if task_name not in self.task_registry:
                return
            task = self.task_registry[task_name]
            current_time = time.perf_counter()
            task['last_execution'] = current_time
            task['execution_count'] += 1
            if task['execution_count'] > RESET_EXECUTION_COUNT_THRESHOLD:
                task['execution_count'] = RESET_EXECUTION_COUNT_VALUE
                task['total_execution_time_ms'] = task['avg_execution_time_ms'] * RESET_EXECUTION_COUNT_VALUE
            task['total_execution_time_ms'] += execution_time_ms
            task['avg_execution_time_ms'] = task['total_execution_time_ms'] / task['execution_count']
            if task['adaptive']:
                self._adapt_task_parameters(task_name, execution_time_ms)
            interval_with_multiplier = task['interval_ms'] * task['adaptive_multiplier']
            task['next_execution'] = current_time + interval_with_multiplier / 1000.0
            self.execution_history[task_name].append(current_time)
            if len(self.execution_history[task_name]) > 100:
                self.execution_history[task_name].popleft()
            self.stats['total_executed'] += 1
    def _adapt_task_parameters(self, task_name, last_execution_time_ms):
        task = self.task_registry[task_name]
        if task['avg_execution_time_ms'] < task['execution_budget_ms'] * 0.5:
            task['adaptive_multiplier'] = max(0.8, task['adaptive_multiplier'] * 0.98)
        elif task['avg_execution_time_ms'] > task['execution_budget_ms'] * 0.8:
            task['adaptive_multiplier'] = min(1.5, task['adaptive_multiplier'] * 1.02)
        adjusted_interval = task['interval_ms'] * task['adaptive_multiplier']
        task['coalescence_window_ms'] = max(1, adjusted_interval * 0.1)
    def get_next_wake_time(self):
        with self.lock:
            if not self.task_registry:
                return 0.1
            current_time = time.perf_counter()
            next_wake = float('inf')
            for task in self.task_registry.values():
                time_until = task['next_execution'] - current_time
                if time_until < next_wake:
                    next_wake = time_until
            return max(0.001, min(5.0, next_wake))
    def get_tasks_to_execute(self):
        with self.lock:
            import heapq
            ready_tasks_heap = []
            for task_name in self.task_registry.keys():
                should_exec, urgency = self.should_execute(task_name)
                if should_exec:
                    heapq.heappush(ready_tasks_heap, (-urgency, task_name))
            ready_tasks = [(name, -urgency) for urgency, name in sorted(ready_tasks_heap)]
            if len(ready_tasks) > 1:
                self.stats['total_coalesced'] += len(ready_tasks) - 1
            if self.stats['total_executed'] > 0:
                self.stats['avg_coalescence_rate'] = self.stats['total_coalesced'] / self.stats['total_executed']
            return ready_tasks
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
    def cleanup(self):
        self._deactivate_high_resolution_timer()
    def __del__(self):
        self._deactivate_high_resolution_timer()
class AdaptiveTimerResolutionManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_resolution_ms = 15.6
        self.active_high_res_processes = set()
        self.timer_handle = None
        self.stats = {'resolution_changes': 0, 'high_res_activations': 0, 'energy_save_activations': 0}
        self.high_res_keywords = ['game', 'dx11', 'dx12', 'vulkan', 'unreal', 'unity', 'ableton', 'cubase', 'fl studio', 'reaper', 'protools', 'studio one', 'obs', 'streamlabs', 'xsplit', 'premiere', 'davinci', 'vegas']
    def detect_high_resolution_need(self, pid, process_name):
        with self.lock:
            process_lower = process_name.lower()
            needs_high_res = any((keyword in process_lower for keyword in self.high_res_keywords))
            if needs_high_res:
                if pid not in self.active_high_res_processes:
                    self.active_high_res_processes.add(pid)
                    return True
            elif pid in self.active_high_res_processes:
                self.active_high_res_processes.discard(pid)
                return False
            return needs_high_res
    def adjust_timer_resolution(self, target_ms=None):
        with self.lock:
            if target_ms is None:
                if len(self.active_high_res_processes) > 0:
                    target_ms = 0.5
                else:
                    target_ms = 15.6
            if abs(target_ms - self.current_resolution_ms) > 0.01:
                resolution_100ns = int(target_ms * MS_TO_100NS)
                current_res = ctypes.c_ulong()
                result = ntdll.NtSetTimerResolution(resolution_100ns, True, ctypes.byref(current_res))
                if result == 0:
                    old_res = self.current_resolution_ms
                    self.current_resolution_ms = target_ms
                    self.stats['resolution_changes'] += 1
                    if target_ms < 2.0:
                        self.stats['high_res_activations'] += 1
                    else:
                        self.stats['energy_save_activations'] += 1
                    return True
    def cleanup_terminated_processes(self):
        with self.lock:
            terminated = set()
            for pid in self.active_high_res_processes:
                proc = psutil.Process(pid)
                if not proc.is_running():
                    terminated.add(pid)
    def get_stats(self):
        with self.lock:
            return {'current_resolution_ms': self.current_resolution_ms, 'active_high_res_processes': len(self.active_high_res_processes), 'total_resolution_changes': self.stats['resolution_changes'], 'high_res_activations': self.stats['high_res_activations'], 'energy_save_activations': self.stats['energy_save_activations'], 'estimated_overhead': 0.05}
class ProcessHandleCache:
    __slots__ = ('max_cache_size', 'handle_ttl', 'cleanup_interval', 'cache', 
                 'access_frequency', 'lock', 'debug_privilege_enabled', 
                 'weak_cache', 'stats', 'cleanup_active', 'cleanup_thread')
    def __init__(self, max_cache_size=256, handle_ttl_seconds=30.0, cleanup_interval_seconds=10.0, debug_privilege_enabled=True):
        self.max_cache_size = max_cache_size
        self.handle_ttl = handle_ttl_seconds
        self.cleanup_interval = cleanup_interval_seconds
        self.cache = {}
        self.access_frequency = defaultdict(int)
        self.lock = threading.RLock()
        self.debug_privilege_enabled = debug_privilege_enabled
        self.weak_cache = weakref.WeakValueDictionary()
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0, 'stale_cleanups': 0, 'total_handles_opened': 0, 'total_handles_closed': 0}
        self.cleanup_active = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True, name='HandleCacheCleanup')
        self.cleanup_thread.start()
    def get_handle(self, pid, access_rights, force_refresh=False):
        with self.lock:
            current_time = time.time()
            if not force_refresh and pid in self.cache:
                cached = self.cache[pid]
                if self._is_handle_valid(cached):
                    if cached['access_rights'] & access_rights == access_rights:
                        age = current_time - cached['created_at']
                        if age < self.handle_ttl:
                            cached['last_access'] = current_time
                            cached['access_count'] += 1
                            self.access_frequency[pid] += 1
                            self.stats['hits'] += 1
                            return cached['handle']
                        else:
                            self._close_and_remove_handle(pid, reason='ttl_expired')
                    else:
                        self._close_and_remove_handle(pid, reason='insufficient_permissions')
                else:
                    self._close_and_remove_handle(pid, reason='invalid_handle')
            self.stats['misses'] += 1
            handle = self._open_new_handle(pid, access_rights)
            if handle:
                if len(self.cache) >= self.max_cache_size:
                    self._evict_least_valuable()
                self.cache[pid] = {'handle': handle, 'access_rights': access_rights, 'created_at': current_time, 'last_access': current_time, 'access_count': 1, 'pid': pid}
                self.access_frequency[pid] = 1
            return handle
    def _open_new_handle(self, pid, access_rights):
        handle = win32api.OpenProcess(access_rights, False, pid)
        if handle:
            self.stats['total_handles_opened'] += 1
            return handle
        return None
    def _is_handle_valid(self, cached_entry):
        pid = cached_entry['pid']
        handle = cached_entry['handle']
        if not psutil.pid_exists(pid):
            return False
        result = kernel32.WaitForSingleObject(handle, 0)
        if result == WAIT_OBJECT_0:
            return False
        return True
    def _close_and_remove_handle(self, pid, reason='unknown'):
        if pid in self.cache:
            win32api.CloseHandle(self.cache[pid]['handle'])
            self.stats['total_handles_closed'] += 1
            del self.cache[pid]
            if reason == 'invalid_handle':
                self.stats['stale_cleanups'] += 1
    def _evict_least_valuable(self):
        if not self.cache:
            return
        current_time = time.time()
        scores = {}
        for pid, cached in self.cache.items():
            recency = current_time - cached['last_access']
            frequency = cached['access_count']
            recency_score = 1.0 / (recency + 1.0)
            frequency_score = frequency
            scores[pid] = frequency_score * 0.6 + recency_score * 0.4
        victim_pid = min(scores.keys(), key=lambda p: scores[p])
        self._close_and_remove_handle(victim_pid, reason='evicted')
        self.stats['evictions'] += 1
    def _cleanup_worker(self):
        while self.cleanup_active:
            time.sleep(self.cleanup_interval)
            self.cleanup_stale_handles()
    def cleanup_stale_handles(self):
        with self.lock:
            current_time = time.time()
            to_remove = []
            for pid, cached in list(self.cache.items()):
                age = current_time - cached['created_at']
                if age > self.handle_ttl:
                    to_remove.append((pid, 'ttl_expired'))
                    continue
                if not self._is_handle_valid(cached):
                    to_remove.append((pid, 'process_dead'))
            for pid, reason in to_remove:
                self._close_and_remove_handle(pid, reason=reason)
    def invalidate(self, pid):
        with self.lock:
            self._close_and_remove_handle(pid, reason='manual_invalidation')
    def close_all(self):
        with self.lock:
            self.cleanup_active = False
            for pid in list(self.cache.keys()):
                self._close_and_remove_handle(pid, reason='shutdown')
            self.cache.clear()
            self.access_frequency.clear()
    def get_statistics(self):
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests * 100 if total_requests > 0 else 0
            return {**self.stats, 'cache_size': len(self.cache), 'hit_rate_percent': hit_rate, 'total_requests': total_requests}
    def __del__(self):
        self.close_all()
class ProcessSnapshotEngine:
    def __init__(self, cache_ttl_ms=500):
        self.cache_ttl_ms = cache_ttl_ms
        self.last_snapshot_time = 0
        self.cached_snapshot = {}
        self.lock = threading.RLock()
        self.pe32_struct = PROCESSENTRY32W()
        self.pe32_struct.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        self.stats = {'total_snapshots': 0, 'cache_hits': 0, 'avg_snapshot_time_ms': 0, 'total_processes_discovered': 0}
    def get_process_snapshot(self, force_refresh=False):
        with self.lock:
            current_time = time.perf_counter()
            if not force_refresh:
                age_ms = (current_time - self.last_snapshot_time) * 1000
                if age_ms < self.cache_ttl_ms and self.cached_snapshot:
                    self.stats['cache_hits'] += 1
                    return self.cached_snapshot.copy()
            start_time = time.perf_counter()
            snapshot = self._take_native_snapshot()
            end_time = time.perf_counter()
            self.cached_snapshot = snapshot
            self.last_snapshot_time = current_time
            self.stats['total_snapshots'] += 1
            snapshot_time_ms = (end_time - start_time) * 1000
            if self.stats['total_snapshots'] == 1:
                self.stats['avg_snapshot_time_ms'] = snapshot_time_ms
            else:
                alpha = 0.3
                self.stats['avg_snapshot_time_ms'] = alpha * snapshot_time_ms + (1 - alpha) * self.stats['avg_snapshot_time_ms']
            self.stats['total_processes_discovered'] = len(snapshot)
            return snapshot.copy()
    def _take_native_snapshot(self):
        snapshot_handle = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snapshot_handle == -1 or snapshot_handle == 0:
            return {}
        processes = {}
        pe32 = self.pe32_struct
        pe32.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        if not kernel32.Process32FirstW(snapshot_handle, ctypes.byref(pe32)):
            return {}
        iteration_count = 0
        max_iterations = MAX_PROCESS_SNAPSHOT_ITERATIONS
        while iteration_count < max_iterations:
            pid = pe32.th32ProcessID
            if pid <= 0:
                continue
            name = pe32.szExeFile
            if name:
                name = sys.intern(name)
                processes[pid] = {'pid': pid, 'name': name, 'parent_pid': pe32.th32ParentProcessID, 'threads': pe32.cntThreads, 'priority_base': pe32.pcPriClassBase}
        return processes
    def get_process_by_name(self, process_name):
        snapshot = self.get_process_snapshot()
        process_name_lower = process_name.lower()
        return [info['pid'] for info in snapshot.values() if info['name'].lower() == process_name_lower]
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class BatchedSettingsApplicator:
    def __init__(self, handle_cache, ctypes_pool=None):
        self.handle_cache = handle_cache
        self.ctypes_pool = ctypes_pool
        self.pending_operations = defaultdict(list)
        self.lock = threading.RLock()
        self.stats = {'total_batches': 0, 'total_operations': 0, 'avg_batch_size': 0, 'syscalls_saved': 0}
    def queue_operation(self, pid, operation_type, **params):
        with self.lock:
            self.pending_operations[pid].append({'type': operation_type, 'params': params})
    def apply_batched_settings(self, pid, settings_dict):
        with self.lock:
            result = {'success': True, 'applied': [], 'failed': []}
            required_access = self._calculate_required_access(settings_dict)
            handle = self.handle_cache.get_handle(pid, required_access)
            if not handle:
                result['success'] = False
                result['failed'] = list(settings_dict)
                return result
            operations_order = ['priority', 'disable_boost', 'page_priority', 'eco_qos', 'trim_working_set', 'affinity', 'io_priority', 'thread_io_priority']
            syscalls_without_batch = len(settings_dict)
            syscalls_with_batch = 1
            for op_type in operations_order:
                if op_type not in settings_dict:
                    continue
                value = settings_dict[op_type]
                success = False
                if op_type == 'priority':
                    success = self._apply_priority(handle, pid, value)
                elif op_type == 'disable_boost':
                    success = self._apply_priority_boost(handle, value)
                elif op_type == 'page_priority':
                    success = self._apply_page_priority(handle, value)
                elif op_type == 'eco_qos':
                    if value:
                        success = self._apply_eco_qos(handle)
                elif op_type == 'trim_working_set':
                    if value:
                        success = self._apply_working_set_trim(handle)
                elif op_type == 'affinity':
                    success = self._apply_affinity(pid, value)
                    syscalls_with_batch += 1
                elif op_type == 'io_priority':
                    success = self._apply_io_priority(pid, value)
                    syscalls_with_batch += 1
                elif op_type == 'thread_io_priority':
                    success = self._apply_thread_io_priority(pid, value)
                    syscalls_with_batch += 1
                if success:
                    result['applied'].append(op_type)
                else:
                    result['failed'].append(op_type)
            self.stats['total_batches'] += 1
            self.stats['total_operations'] += len(settings_dict)
            self.stats['avg_batch_size'] = self.stats['total_operations'] / self.stats['total_batches']
            self.stats['syscalls_saved'] += syscalls_without_batch - syscalls_with_batch
            result['success'] = len(result['failed']) == 0
            return result
    def _calculate_required_access(self, settings_dict):
        access = 0
        if 'priority' in settings_dict or 'disable_boost' in settings_dict or 'page_priority' in settings_dict or ('trim_working_set' in settings_dict):
            access |= PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION
        if 'trim_working_set' in settings_dict:
            access |= PROCESS_SET_QUOTA
        return access if access else PROCESS_QUERY_INFORMATION
    def _apply_priority(self, handle, pid, priority_class):
        if not handle:
            return False
        valid_priorities = {win32process.IDLE_PRIORITY_CLASS, win32process.BELOW_NORMAL_PRIORITY_CLASS, win32process.NORMAL_PRIORITY_CLASS, win32process.ABOVE_NORMAL_PRIORITY_CLASS, win32process.HIGH_PRIORITY_CLASS, win32process.REALTIME_PRIORITY_CLASS}
        if priority_class not in valid_priorities:
            return False
        current = win32process.GetPriorityClass(handle)
        if current != priority_class:
            win32process.SetPriorityClass(handle, priority_class)
            new_priority = win32process.GetPriorityClass(handle)
            return new_priority == priority_class
        return True
    def _apply_priority_boost(self, handle, disable_boost):
        kernel32.SetProcessPriorityBoost(handle, wintypes.BOOL(disable_boost))
        return True
    def _apply_page_priority(self, handle, page_priority):
        if not handle:
            return False
        if not 1 <= page_priority <= 5:
            return False
        priority_value = ctypes.c_ulong(page_priority)
        result = NtSetInformationProcess(handle, ProcessPagePriority, ctypes.byref(priority_value), ctypes.sizeof(priority_value))
        return result == 0
    def _apply_working_set_trim(self, handle):
        result = kernel32.SetProcessWorkingSetSize(handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
        return bool(result)
    def _apply_affinity(self, pid, cores):
        if not cores or not isinstance(cores, (list, tuple)):
            return False
        max_cores = psutil.cpu_count(logical=True)
        if any((core < 0 or core >= max_cores for core in cores)):
            return False
        handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
        if not handle:
            return False
        current = get_process_affinity_direct(handle)
        if current and set(current) == set(cores):
            return True
        if current and set(current) != set(cores):
            success = set_process_affinity_direct(handle, cores)
            if success:
                new_affinity = get_process_affinity_direct(handle)
                return new_affinity and set(new_affinity) == set(cores)
            return False
        return set_process_affinity_direct(handle, cores)
    def _apply_io_priority(self, pid, io_priority):
        return self._apply_thread_io_priority(pid, io_priority)
    def _apply_eco_qos(self, handle):
        throttling_state = None
        if self.ctypes_pool:
            throttling_state = self.ctypes_pool.get_structure(PROCESS_POWER_THROTTLING_STATE)
        else:
            throttling_state = PROCESS_POWER_THROTTLING_STATE()
        throttling_state.Version = 1
        throttling_state.ControlMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
        throttling_state.StateMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
        result = kernel32.SetProcessInformation(handle, ProcessPowerThrottling, ctypes.byref(throttling_state), ctypes.sizeof(throttling_state))
        return bool(result)
    def _apply_thread_io_priority(self, pid, io_priority):
        if not isinstance(io_priority, int) or not 0 <= io_priority <= 3:
            return False
        snapshot_handle = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
        if snapshot_handle == -1 or snapshot_handle == 0:
            return False
        threads_set = 0
        te32 = THREADENTRY32()
        te32.dwSize = ctypes.sizeof(THREADENTRY32)
        if kernel32.Thread32First(snapshot_handle, ctypes.byref(te32)):
            while True:
                thread_handle = None
                if te32.th32OwnerProcessID == pid:
                    thread_id = te32.th32ThreadID
                    thread_handle = kernel32.OpenThread(THREAD_SET_INFORMATION | THREAD_QUERY_INFORMATION, False, thread_id)
                    if thread_handle:
                        io_prio_value = ctypes.c_ulong(io_priority)
                        result = NtSetInformationThread(thread_handle, ThreadIoPriority, ctypes.byref(io_prio_value), ctypes.sizeof(io_prio_value))
                        if result == 0:
                            threads_set += 1
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class WorkingSetOptimizer:
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.trim_history = defaultdict(deque)
        self.memory_baselines = {}
        self.foreground_tracking = {}
        self.lock = threading.RLock()
        self.default_trim_interval = 60.0
        self.min_trim_interval = 30.0
        self.max_trim_interval = 300.0
        self.significant_memory_change_percent = 20.0
        self.aggressive_trim_threshold_mb = 500
        self.min_background_time_for_trim = 900.0
        self.stats = {'total_trims': 0, 'total_memory_freed_mb': 0, 'avg_memory_freed_per_trim_mb': 0, 'trims_with_significant_effect': 0}
    def should_trim_working_set(self, pid, current_memory_mb):
        with self.lock:
            current_time = time.time()
            if pid not in self.memory_baselines:
                self.memory_baselines[pid] = {'initial_mb': current_memory_mb, 'peak_mb': current_memory_mb, 'last_trim': 0, 'trim_interval': self.default_trim_interval}
                self.foreground_tracking[pid] = {'last_foreground': current_time, 'is_foreground': False}
                return False
            baseline = self.memory_baselines[pid]
            tracking = self.foreground_tracking.get(pid, {'last_foreground': current_time, 'is_foreground': False})
            if current_memory_mb > baseline['peak_mb']:
                baseline['peak_mb'] = current_memory_mb
            time_since_trim = current_time - baseline['last_trim']
            if time_since_trim < baseline['trim_interval']:
                return False
            time_since_foreground = current_time - tracking['last_foreground']
            if time_since_foreground < self.min_background_time_for_trim:
                return False
            if pid in self.trim_history and self.trim_history[pid]:
                last_trim_event = self.trim_history[pid][-1]
                memory_growth_percent = (current_memory_mb - last_trim_event['memory_after_mb']) / max(last_trim_event['memory_after_mb'], 1) * 100
                if memory_growth_percent > self.significant_memory_change_percent:
                    return True
            if current_memory_mb > self.aggressive_trim_threshold_mb:
                return True
            if time_since_trim >= baseline['trim_interval']:
                return True
            return False
    def trim_working_set(self, pid, current_memory_mb=None):
        with self.lock:
            result = {'success': False, 'memory_freed_mb': 0.0, 'effectiveness': 0.0}
            if current_memory_mb is None:
                process = psutil.Process(pid)
                current_memory_mb = process.memory_info().rss / (1024 * 1024)
            memory_before_mb = current_memory_mb
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA)
            if not handle:
                return result
            trim_result = kernel32.SetProcessWorkingSetSize(handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
            if not trim_result:
                return result
            time.sleep(0.05)
            process = psutil.Process(pid)
            memory_after_mb = process.memory_info().rss / (1024 * 1024)
            return result
    def _adapt_trim_interval(self, pid, last_effectiveness):
        if pid not in self.memory_baselines:
            return
        baseline = self.memory_baselines[pid]
        if last_effectiveness > 20.0:
            baseline['trim_interval'] = max(self.min_trim_interval, baseline['trim_interval'] * 0.8)
        elif last_effectiveness < 5.0:
            baseline['trim_interval'] = min(self.max_trim_interval, baseline['trim_interval'] * 1.3)
    def mark_process_foreground(self, pid, is_foreground):
        with self.lock:
            current_time = time.time()
            if pid not in self.foreground_tracking:
                self.foreground_tracking[pid] = {'last_foreground': current_time if is_foreground else 0, 'is_foreground': is_foreground}
            else:
                tracking = self.foreground_tracking[pid]
                if is_foreground:
                    tracking['last_foreground'] = current_time
                tracking['is_foreground'] = is_foreground
    def get_trim_statistics_for_pid(self, pid):
        with self.lock:
            if pid not in self.trim_history or len(self.trim_history[pid]) == 0:
                return None
            history = list(self.trim_history[pid])
            return {'total_trims': len(history), 'total_memory_freed_mb': sum((e['memory_freed_mb'] for e in history)), 'avg_memory_freed_mb': sum((e['memory_freed_mb'] for e in history)) / len(history), 'avg_effectiveness_percent': sum((e['effectiveness_percent'] for e in history)) / len(history), 'current_trim_interval': self.memory_baselines.get(pid, {}).get('trim_interval', 0)}
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class ForegroundDebouncer:
    def __init__(self, debounce_time_ms=300, hysteresis_time_ms=150, whitelist_debounce_ms=150):
        self.debounce_time = debounce_time_ms / 1000.0
        self.hysteresis_time = hysteresis_time_ms / 1000.0
        self.whitelist_debounce = whitelist_debounce_ms / 1000.0
        self.pending_change = None
        self.pending_timer = None
        self.last_applied_pid = None
        self.last_change_time = 0
        self.change_history = deque(maxlen=20)
        self.known_pids = set()
        self.lock = threading.RLock()
        self.stats = {'total_requests': 0, 'total_applied': 0, 'total_cancelled': 0, 'total_coalesced': 0, 'avg_debounce_delay_ms': 0}
    def request_foreground_change(self, new_pid, callback, is_known=False, *args, **kwargs):
        with self.lock:
            current_time = time.time()
            self.stats['total_requests'] += 1
            if new_pid == self.last_applied_pid:
                return
            if self.pending_timer:
                self.pending_timer.cancel()
                self.stats['total_cancelled'] += 1
            time_since_last = current_time - self.last_change_time
            is_rapid_change = time_since_last < self.hysteresis_time
            self.change_history.append({'timestamp': current_time, 'pid': new_pid, 'rapid': is_rapid_change})
            if is_known:
                self.known_pids.add(new_pid)
            debounce_delay = self._calculate_dynamic_debounce(new_pid, is_known)
            self.pending_change = {'pid': new_pid, 'callback': callback, 'args': args, 'kwargs': kwargs, 'request_time': current_time}
            self.pending_timer = threading.Timer(debounce_delay, self._apply_pending_change)
            self.pending_timer.daemon = True
            self.pending_timer.start()
            self.last_change_time = current_time
    def _calculate_dynamic_debounce(self, pid=None, is_known=False):
        if pid and (pid in self.known_pids or is_known):
            return self.whitelist_debounce
        if len(self.change_history) < 3:
            return self.debounce_time
        recent_history = list(self.change_history)[-5:]
        rapid_changes = sum((1 for event in recent_history if event['rapid']))
        if rapid_changes / len(recent_history) > 0.5:
            return min(self.debounce_time * 1.5, 0.5)
        return self.debounce_time
    def _apply_pending_change(self):
        with self.lock:
            if not self.pending_change:
                return
            change = self.pending_change
            current_time = time.time()
            if not psutil.pid_exists(change['pid']):
                self.stats['total_cancelled'] += 1
                self.pending_change = None
                return
            change['callback'](*change['args'], **change['kwargs'])
            self.last_applied_pid = change['pid']
            self.stats['total_applied'] += 1
            delay_ms = (current_time - change['request_time']) * 1000
            if self.stats['total_applied'] == 1:
                self.stats['avg_debounce_delay_ms'] = delay_ms
            else:
                alpha = 0.3
                self.stats['avg_debounce_delay_ms'] = alpha * delay_ms + (1 - alpha) * self.stats['avg_debounce_delay_ms']
    def force_apply_pending(self):
        with self.lock:
            if self.pending_timer:
                self.pending_timer.cancel()
            self._apply_pending_change()
    def cancel_pending(self):
        with self.lock:
            if self.pending_timer:
                self.pending_timer.cancel()
                self.stats['total_cancelled'] += 1
            self.pending_change = None
            self.pending_timer = None
    def get_statistics(self):
        with self.lock:
            cancel_rate = self.stats['total_cancelled'] / self.stats['total_requests'] * 100 if self.stats['total_requests'] > 0 else 0
            return {**self.stats, 'cancel_rate_percent': cancel_rate, 'pending': self.pending_change is not None}
class ProcessTreeCache:
    def __init__(self, rebuild_interval_ms=2000):
        self.rebuild_interval = rebuild_interval_ms / 1000.0
        self.last_rebuild = 0
        self.parent_to_children = defaultdict(set)
        self.child_to_parent = {}
        self.process_info = {}
        self.lock = threading.RLock()
        self.stats = {'total_rebuilds': 0, 'avg_rebuild_time_ms': 0, 'total_processes_tracked': 0, 'max_tree_depth': 0}
    def rebuild_tree(self, force=False):
        with self.lock:
            current_time = time.time()
            if not force and current_time - self.last_rebuild < self.rebuild_interval:
                return False
            start_time = time.perf_counter()
            snapshot_handle = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            if snapshot_handle == -1 or snapshot_handle == 0:
                return False
            self.parent_to_children.clear()
            self.child_to_parent.clear()
            self.process_info.clear()
            pe32 = PROCESSENTRY32W()
            pe32.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            if kernel32.Process32FirstW(snapshot_handle, ctypes.byref(pe32)):
                while True:
                    pid = pe32.th32ProcessID
                    ppid = pe32.th32ParentProcessID
                    name = pe32.szExeFile
                    self.process_info[pid] = {'pid': pid, 'ppid': ppid, 'name': name, 'threads': pe32.cntThreads}
                    if ppid != 0:
                        self.parent_to_children[ppid].add(pid)
                        self.child_to_parent[pid] = ppid
            end_time = time.perf_counter()
            max_depth = self._calculate_max_depth()
            self.last_rebuild = current_time
            self.stats['total_rebuilds'] += 1
            rebuild_time_ms = (end_time - start_time) * 1000
            if self.stats['total_rebuilds'] == 1:
                self.stats['avg_rebuild_time_ms'] = rebuild_time_ms
            else:
                alpha = 0.3
                self.stats['avg_rebuild_time_ms'] = alpha * rebuild_time_ms + (1 - alpha) * self.stats['avg_rebuild_time_ms']
            self.stats['total_processes_tracked'] = len(self.process_info)
            self.stats['max_tree_depth'] = max_depth
            return True
    def _calculate_max_depth(self):
        max_depth = 0
        for pid in self.process_info.keys():
            depth = self._get_process_depth(pid)
            if depth > max_depth:
                max_depth = depth
        return max_depth
    def _get_process_depth(self, pid, visited=None):
        if not visited:
            visited = set()
        if pid in visited:
            return 0
        visited.add(pid)
        if pid not in self.child_to_parent:
            return 1
        parent_pid = self.child_to_parent[pid]
        return 1 + self._get_process_depth(parent_pid, visited)
    def get_all_descendants(self, pid):
        self.rebuild_tree()
        with self.lock:
            descendants = set()
            to_process = [pid]
            while to_process:
                current = to_process.pop()
                children = self.parent_to_children.get(current, set())
                for child in children:
                    if child not in descendants:
                        descendants.add(child)
                        to_process.append(child)
            return list(descendants)
    def get_direct_children(self, pid):
        self.rebuild_tree()
        with self.lock:
            return list(self.parent_to_children.get(pid, set()))
    def get_parent(self, pid):
        self.rebuild_tree()
        with self.lock:
            return self.child_to_parent.get(pid, None)
    def get_process_info(self, pid):
        self.rebuild_tree()
        with self.lock:
            return self.process_info.get(pid, None)
    def get_process_tree(self, root_pid):
        self.rebuild_tree()
        with self.lock:
            def build_subtree(pid):
                info = self.process_info.get(pid, {})
                children_pids = self.parent_to_children.get(pid, set())
                return {'pid': pid, 'info': info, 'children': [build_subtree(child) for child in children_pids]}
            return build_subtree(root_pid)
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class CPUPinningEngine:
    def __init__(self, handle_cache, cpu_count, numa_topology=None):
        self.handle_cache = handle_cache
        self.cpu_count = cpu_count
        self.numa_topology = numa_topology or {}
        self.pinned_processes = {}
        self.core_assignments = defaultdict(set)
        self.thread_affinity_cache = {}
        self.lock = threading.RLock()
        self.stats = {'total_pins': 0, 'total_thread_pins': 0, 'total_unpins': 0, 'active_pinned_processes': 0}
    def pin_process_to_core(self, pid, core_id, pin_threads=True):
        with self.lock:
            result = {'success': False, 'threads_pinned': 0, 'core': core_id}
            if core_id >= self.cpu_count or core_id < 0:
                return result
            handle = win32api.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, pid)
            if not handle:
                return result
            success = set_process_affinity_direct(handle, [core_id])
            if not success:
                return result
            threads_pinned = 0
            if pin_threads:
                threads_pinned = self._pin_process_threads(pid, core_id)
            self.pinned_processes[pid] = {'core': core_id, 'timestamp': time.time(), 'thread_count': threads_pinned, 'pin_threads': pin_threads}
            self.core_assignments[core_id].add(pid)
            self.stats['total_pins'] += 1
            self.stats['total_thread_pins'] += threads_pinned
            self.stats['active_pinned_processes'] = len(self.pinned_processes)
            result.update({'success': True, 'threads_pinned': threads_pinned})
            return result
    def _pin_process_threads(self, pid, core_id):
        threads_pinned = 0
        snapshot_handle = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
        if snapshot_handle == -1 or snapshot_handle == 0:
            return 0
        te32 = THREADENTRY32()
        te32.dwSize = ctypes.sizeof(THREADENTRY32)
        if kernel32.Thread32First(snapshot_handle, ctypes.byref(te32)):
            while True:
                if te32.th32OwnerProcessID == pid:
                    thread_id = te32.th32ThreadID
                    thread_handle = kernel32.OpenThread(THREAD_SET_INFORMATION | THREAD_QUERY_INFORMATION, False, thread_id)
                    if thread_handle:
                        kernel32.SetThreadIdealProcessor(thread_handle, core_id)
                        affinity_mask = 1 << core_id
                        kernel32.SetThreadAffinityMask(thread_handle, affinity_mask)
                        threads_pinned += 1
                        if pid not in self.thread_affinity_cache:
                            self.thread_affinity_cache[pid] = {}
                        self.thread_affinity_cache[pid][thread_id] = core_id
        return threads_pinned
    def unpin_process(self, pid):
        with self.lock:
            if pid not in self.pinned_processes:
                return False
            handle = win32api.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, pid)
            if not handle:
                return False
            all_cores = list(range(self.cpu_count))
            set_process_affinity_direct(handle, all_cores)
            pinning_info = self.pinned_processes[pid]
            core_id = pinning_info['core']
            del self.pinned_processes[pid]
            self.core_assignments[core_id].discard(pid)
            if pid in self.thread_affinity_cache:
                del self.thread_affinity_cache[pid]
            self.stats['total_unpins'] += 1
            self.stats['active_pinned_processes'] = len(self.pinned_processes)
            return True
    def get_least_loaded_core(self, core_candidates):
        if not core_candidates:
            return 0
        with self.lock:
            loads = {}
            for core_id in core_candidates:
                loads[core_id] = len(self.core_assignments.get(core_id, set()))
            per_cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            scores = {}
            for core_id in core_candidates:
                cpu_load = per_cpu_percent[core_id] if core_id < len(per_cpu_percent) else 50
                pinned_load = loads[core_id] * 10
                scores[core_id] = cpu_load * 0.6 + pinned_load * 0.4
            return min(scores.keys(), key=lambda c: scores[c])
    def get_numa_preferred_cores(self, available_cores):
        if not self.numa_topology or not self.numa_topology.get('numa_nodes'):
            return available_cores
        numa_nodes = self.numa_topology.get('numa_nodes', {})
        for node_id, node_cores in numa_nodes.items():
            intersection = set(available_cores) & node_cores
            if intersection and len(intersection) >= 2:
                return list(intersection)
        return available_cores
    def apply_intelligent_pinning(self, pid, available_cores, workload_type='general'):
        with self.lock:
            numa_cores = self.get_numa_preferred_cores(available_cores)
            if not numa_cores:
                return {'success': False, 'error': 'No cores available'}
            handle = win32api.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, pid)
            if not handle:
                return {'success': False}
            process = psutil.Process(pid)
            num_threads = process.num_threads()
            if workload_type == 'single_thread' or num_threads <= 2:
                best_core = self.get_least_loaded_core(numa_cores)
                return self.pin_process_to_core(pid, best_core, pin_threads=True)
            elif workload_type == 'latency_sensitive':
                if len(numa_cores) >= 2:
                    sorted_cores = sorted(numa_cores, key=lambda c: len(self.core_assignments.get(c, set())))
                    selected_cores = sorted_cores[:2]
                    set_process_affinity_direct(handle, selected_cores)
                    return {'success': True, 'cores': selected_cores, 'mode': 'soft_affinity'}
                else:
                    best_core = self.get_least_loaded_core(numa_cores)
                    return self.pin_process_to_core(pid, best_core, pin_threads=True)
            elif workload_type == 'throughput':
                set_process_affinity_direct(handle, numa_cores)
                return {'success': True, 'cores': numa_cores, 'mode': 'affinity_only'}
            elif num_threads <= 4:
                cores_to_use = numa_cores[:min(4, len(numa_cores))]
                set_process_affinity_direct(handle, cores_to_use)
                return {'success': True, 'cores': cores_to_use, 'mode': 'limited_affinity'}
            else:
                set_process_affinity_direct(handle, numa_cores)
                return {'success': True, 'cores': numa_cores, 'mode': 'full_affinity'}
    def get_pinning_info(self, pid):
        with self.lock:
            return self.pinned_processes.get(pid, None)
    def get_core_assignments(self):
        with self.lock:
            return {core: list(pids) for core, pids in self.core_assignments.items()}
    def cleanup_dead_processes(self):
        with self.lock:
            dead_pids = []
            for pid in list(self.pinned_processes.keys()):
                if not psutil.pid_exists(pid):
                    dead_pids.append(pid)
            for pid in dead_pids:
                pinning_info = self.pinned_processes[pid]
                core_id = pinning_info['core']
                del self.pinned_processes[pid]
                self.core_assignments[core_id].discard(pid)
                if pid in self.thread_affinity_cache:
                    del self.thread_affinity_cache[pid]
            self.stats['active_pinned_processes'] = len(self.pinned_processes)
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class LargePageManager:
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.large_page_enabled_pids = set()
        self.lock = threading.RLock()
        self.large_page_privilege_enabled = False
        self.stats = {'total_large_page_candidates': 0, 'total_failures': 0}
        self._enable_lock_memory_privilege()
    def _enable_lock_memory_privilege(self):
        h_token = wintypes.HANDLE()
        h_process = kernel32.GetCurrentProcess()
        if not advapi32.OpenProcessToken(h_process, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(h_token)):
            return False
        luid = LUID()
        if not advapi32.LookupPrivilegeValueW(None, SE_LOCK_MEMORY_NAME, ctypes.byref(luid)):
            kernel32.CloseHandle(h_token)
            return False
        tp = TOKEN_PRIVILEGES()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
        advapi32.AdjustTokenPrivileges(h_token, False, ctypes.byref(tp), ctypes.sizeof(TOKEN_PRIVILEGES), None, None)
        kernel32.CloseHandle(h_token)
        self.large_page_privilege_enabled = True
        return True
    def should_enable_large_pages(self, pid, is_foreground):
        if not self.large_page_privilege_enabled:
            return False
        if not is_foreground:
            return False
        process = psutil.Process(pid)
        memory_mb = process.memory_info().rss / (1024 * 1024)
        if memory_mb > 2048:
            return True
        return False
    def enable_large_pages_for_process(self, pid):
        with self.lock:
            if pid in self.large_page_enabled_pids:
                return True
            process = psutil.Process(pid)
            memory_mb = process.memory_info().rss / (1024 * 1024)
            if memory_mb > 2048:
                self.large_page_enabled_pids.add(pid)
                self.stats['total_large_page_candidates'] += 1
                return True
            else:
                return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class AdvancedWorkingSetTrimmer:

    __slots__ = ('handle_cache', 'lock', 'stats')
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.stats = {'total_trims': 0}
    def trim_full_working_set(self, pid):

        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA)
            if not handle:
                return False
            result = kernel32.SetProcessWorkingSetSize(handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
            if bool(result):
                self.stats['total_trims'] += 1
                return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class PrefetchOptimizer:

    __slots__ = ('lock', 'stats', 'hardware_detector', 'service_name')
    def __init__(self, hardware_detector=None):
        self.lock = threading.RLock()
        self.stats = {'optimizations_applied': 0, 'optimizations_skipped_hdd': 0}
        self.hardware_detector = hardware_detector
        self.service_name = 'SysMain'
    def check_and_disable_for_ssd(self, registry_buffer: Optional[RegistryWriteBuffer] = None):

        with self.lock:
            if not self.hardware_detector or \
               not (self.hardware_detector.has_ssd() or self.hardware_detector.has_nvme()):
                self.stats['optimizations_skipped_hdd'] += 1
                return False
            key_path = f'SYSTEM\\CurrentControlSet\\Services\\{self.service_name}'
            value_name = 'Start'
            value_data = 4
            if registry_buffer:
                registry_buffer.queue_write(key_path, value_name, winreg.REG_DWORD, value_data)
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                winreg.CloseKey(key)
            subprocess.run(
                ['sc', 'stop', self.service_name],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=5
            )
            self.stats['optimizations_applied'] += 1
            return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class MemoryPriorityManager:
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.priority_map = {}
        self.stats = {'total_priority_changes': 0, 'very_low_count': 0, 'low_count': 0, 'medium_count': 0, 'below_normal_count': 0, 'normal_count': 0}
    def set_memory_priority(self, pid, priority_level, is_foreground, minimized_time=0):
        with self.lock:
            if is_foreground:
                target_priority = MEMORY_PRIORITY_NORMAL
            elif minimized_time > 1800:
                target_priority = MEMORY_PRIORITY_VERY_LOW
            else:
                target_priority = MEMORY_PRIORITY_LOW
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if not handle:
                return False
            mem_priority = MEMORY_PRIORITY_INFORMATION()
            mem_priority.MemoryPriority = target_priority
            result = NtSetInformationProcess(handle, ProcessMemoryPriority, ctypes.byref(mem_priority), ctypes.sizeof(mem_priority))
            if result == 0:
                self.priority_map[pid] = target_priority
                self.stats['total_priority_changes'] += 1
                if target_priority == MEMORY_PRIORITY_VERY_LOW:
                    self.stats['very_low_count'] += 1
                elif target_priority == MEMORY_PRIORITY_LOW:
                    self.stats['low_count'] += 1
                elif target_priority == MEMORY_PRIORITY_MEDIUM:
                    self.stats['medium_count'] += 1
                elif target_priority == MEMORY_PRIORITY_BELOW_NORMAL:
                    self.stats['below_normal_count'] += 1
                elif target_priority == MEMORY_PRIORITY_NORMAL:
                    self.stats['normal_count'] += 1
                return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class ProcessServiceManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.database = {}
        self.load_database()
        self.stats = {'services_stopped': 0, 'services_disabled': 0, 'processes_suspended': 0, 'processes_throttled': 0}
    def load_database(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'process_service_database.json')
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                self.database = {}
                return
            self.database = data
    def get_process_config(self, process_name):
        processes_section = self.database.get('processes', {})
        if not processes_section:
            return None
        system_procs = processes_section.get('system_processes', [])
        for proc in system_procs:
            if proc.get('name', '').lower() == process_name.lower():
                return proc
        third_party_procs = processes_section.get('common_third_party', [])
        for proc in third_party_procs:
            if proc.get('name', '').lower() == process_name.lower():
                return proc
        return None
    def should_apply_action(self, process_name, cpu_percent, ram_percent, disk_percent):
        config = self.get_process_config(process_name)
        if not config:
            return (False, None)
        action = config.get('action_on_threshold')
        if not action:
            return (False, None)
        cpu_threshold = config.get('cpu_threshold_percent', 100)
        ram_threshold = config.get('ram_threshold_mb', 999999)
        process_list = [p for p in psutil.process_iter(['name']) if p.info['name'].lower() == process_name.lower()]
        if process_list:
            proc = process_list[0]
            proc_cpu = proc.cpu_percent(interval=0.1)
            proc_ram_mb = proc.memory_info().rss / (1024 * 1024)
            if proc_cpu > cpu_threshold or proc_ram_mb > ram_threshold:
                return (True, action)
        return (False, None)
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class CPUParkingController:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'total_parking_changes': 0, 'disabled_count': 0, 'enabled_count': 0}
    def disable_cpu_parking(self):
        with self.lock:
            result = subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_PROCESSOR', 'CPMINCORES', '100'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                self.stats['total_parking_changes'] += 1
                self.stats['disabled_count'] += 1
                return True
            return False
    def enable_cpu_parking(self):
        with self.lock:
            result = subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_PROCESSOR', 'CPMINCORES', '0'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                self.stats['total_parking_changes'] += 1
                self.stats['enabled_count'] += 1
                return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class HeterogeneousThreadScheduler:
    def __init__(self, handle_cache, p_cores, e_cores):
        self.handle_cache = handle_cache
        self.p_cores = p_cores
        self.e_cores = e_cores
        self.lock = threading.RLock()
        self.thread_classifications = {}
        self.stats = {'latency_threads': 0, 'throughput_threads': 0, 'total_scheduled': 0}
    def classify_and_schedule_threads(self, pid, is_latency_sensitive):
        with self.lock:
            snapshot_handle = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
            if snapshot_handle == -1 or snapshot_handle == 0:
                return False
            threads_scheduled = 0
            target_cores = self.p_cores if is_latency_sensitive else self.e_cores
            if not target_cores:
                target_cores = self.p_cores
            te32 = THREADENTRY32()
            te32.dwSize = ctypes.sizeof(THREADENTRY32)
            if kernel32.Thread32First(snapshot_handle, ctypes.byref(te32)):
                while True:
                    if te32.th32OwnerProcessID == pid:
                        thread_id = te32.th32ThreadID
                        thread_handle = kernel32.OpenThread(THREAD_SET_INFORMATION | THREAD_QUERY_INFORMATION, False, thread_id)
                        if thread_handle:
                            if is_latency_sensitive:
                                throttling_state = THREAD_POWER_THROTTLING_STATE()
                                throttling_state.Version = 1
                                throttling_state.ControlMask = THREAD_POWER_THROTTLING_VALID_FLAGS
                                throttling_state.StateMask = 0
                                NtSetInformationThread(thread_handle, ThreadPowerThrottling, ctypes.byref(throttling_state), ctypes.sizeof(throttling_state))
                            affinity_mask = 0
                            for core in target_cores:
                                affinity_mask |= 1 << core
                            kernel32.SetThreadAffinityMask(thread_handle, affinity_mask)
                            threads_scheduled += 1
                            self.thread_classifications[thread_id] = 'latency' if is_latency_sensitive else 'throughput'
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class ContextSwitchReducer:
    def __init__(self):
        self.lock = threading.RLock()
        self.quantum_adjusted = False
        self.stats = {'quantum_adjustments': 0, 'context_switches_reduced': 0}
    def adjust_quantum_time_slice(self, increase=True, registry_buffer=None):
        with self.lock:
            key_path = 'SYSTEM\\CurrentControlSet\\Control\\PriorityControl'
            value_name = 'Win32PrioritySeparation'
            new_value = 38 if increase else 2
            if registry_buffer:
                registry_buffer.queue_write(key_path, value_name, winreg.REG_DWORD, new_value)
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, new_value)
                winreg.CloseKey(key)
            self.quantum_adjusted = True
            self.stats['quantum_adjustments'] += 1
            return True
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class SMTScheduler:
    def __init__(self, cpu_count):
        self.cpu_count = cpu_count
        self.lock = threading.RLock()
        self.sibling_map = {}
        self.stats = {'smt_aware_assignments': 0, 'physical_core_assignments': 0}
        self._detect_siblings()
    def _detect_siblings(self):
        returned_length = wintypes.DWORD(0)
        kernel32.GetLogicalProcessorInformationEx(RelationProcessorCore, None, ctypes.byref(returned_length))
        buf_size = returned_length.value
        if buf_size > 0:
            buf = (ctypes.c_byte * buf_size)()
            if kernel32.GetLogicalProcessorInformationEx(RelationProcessorCore, ctypes.byref(buf), ctypes.byref(returned_length)):
                offset = 0
                while offset < buf_size:
                    entry = SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX.from_buffer_copy(buf[offset:])
                    if entry.Relationship == RelationProcessorCore:
                        proc_rel = entry.u.Processor
                        if proc_rel.GroupCount > 0:
                            mask = proc_rel.GroupMask[0].Mask
                            cpus = []
                            bit = 0
                            temp_mask = mask
                            while temp_mask:
                                if temp_mask & 1:
                                    cpus.append(bit)
                                temp_mask >>= 1
                                bit += 1
                            for cpu in cpus:
                                self.sibling_map[cpu] = [c for c in cpus if c != cpu]
                    offset += entry.Size
    def get_physical_cores_only(self):
        with self.lock:
            physical_cores = set()
            for core in range(self.cpu_count):
                if core not in self.sibling_map or not self.sibling_map[core]:
                    physical_cores.add(core)
                elif core not in physical_cores:
                    skip = False
                    for sibling in self.sibling_map[core]:
                        if sibling in physical_cores:
                            skip = True
                            break
                    if not skip:
                        physical_cores.add(core)
            return list(physical_cores) if physical_cores else list(range(self.cpu_count))
    def assign_to_physical_cores(self, pid):
        with self.lock:
            physical_cores = self.get_physical_cores_only()
            handle = win32api.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, pid)
            if not handle:
                return False
            affinity_mask = 0
            for core in physical_cores:
                affinity_mask |= 1 << core
            result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
            if result:
                self.stats['smt_aware_assignments'] += 1
                self.stats['physical_core_assignments'] += 1
                return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class CPUFrequencyScaler:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'turbo_enabled': 0, 'downclocking_enabled': 0, 'frequency_changes': 0}
    def set_turbo_mode(self, enable=True):
        with self.lock:
            if enable:
                result = subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_PROCESSOR', 'PERFBOOSTMODE', '2'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_PROCESSOR', 'PERFBOOSTMODE', '0'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.stats['frequency_changes'] += 1
                if enable:
                    self.stats['turbo_enabled'] += 1
                else:
                    self.stats['downclocking_enabled'] += 1
                return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class AWEManager:
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.awe_enabled_processes = set()
        self.stats = {'awe_enabled_count': 0, 'total_32bit_processes': 0, 'awe_failures': 0}
    def is_32bit_process(self, pid):
        process = psutil.Process(pid)
        if platform.machine().endswith('64'):
            is_wow64 = ctypes.c_int()
            kernel32.IsWow64Process(kernel32.GetCurrentProcess(), ctypes.byref(is_wow64))
            return bool(is_wow64.value)
    def enable_awe_for_process(self, pid):
        with self.lock:
            if pid in self.awe_enabled_processes:
                return True
            if not self.is_32bit_process(pid):
                return False
            self.stats['total_32bit_processes'] += 1
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA)
            if not handle:
                self.stats['awe_failures'] += 1
                return False
            min_size = ctypes.c_size_t(0)
            max_size = ctypes.c_size_t(4294967295)
            result = kernel32.SetProcessWorkingSetSizeEx(handle, min_size, max_size, AWE_ENABLED_FLAG)
            if result:
                self.awe_enabled_processes.add(pid)
                self.stats['awe_enabled_count'] += 1
                return True
            else:
                self.stats['awe_failures'] += 1
                return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class InterruptAffinityOptimizer:
    def __init__(self, e_cores):
        self.e_cores = e_cores
        self.lock = threading.RLock()
        self.stats = {'interrupts_moved': 0, 'optimization_attempts': 0, 'failures': 0}
    def optimize_interrupt_affinity(self):
        with self.lock:
            if not self.e_cores:
                return False
            self.stats['optimization_attempts'] += 1
            affinity_mask = 0
            for core in self.e_cores:
                affinity_mask |= 1 << core
            affinity_hex = hex(affinity_mask)
            base_proc = self.e_cores[0]
            max_proc = self.e_cores[-1] if self.e_cores else self.e_cores[0]
            result = subprocess.run(['powershell', '-Command', f'Get-NetAdapter | ForEach-Object {{  Set-NetAdapterRss -Name $_.Name -BaseProcessorNumber {base_proc} -MaxProcessorNumber {max_proc} -ErrorAction SilentlyContinue }} '], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            if result.returncode == 0:
                self.stats['interrupts_moved'] += 1
                return True
            else:
                self.stats['failures'] += 1
                return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class DPCLatencyController:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'dpc_optimizations': 0, 'latency_improvements': 0, 'monitoring_active': False}
        self.target_dpc_latency_us = 128
    def optimize_dpc_latency(self):
        with self.lock:
            self.stats['dpc_optimizations'] += 1
            key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'DpcWatchdogProfileOffset', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'DpcTimeout', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            self.stats['latency_improvements'] += 1
            return True
    def monitor_dpc_latency(self):
        with self.lock:
            result = subprocess.run(['powershell', '-Command', 'Get-Counter "\\Processor(_Total)\\% DPC Time" -ErrorAction SilentlyContinue'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            if result.returncode == 0:
                self.stats['monitoring_active'] = True
                return True
            return False
    def get_statistics(self):
        with self.lock:
            return self.stats.copy()
class AdvancedInterruptDPCOptimizer:
    def __init__(self, cpu_count, e_cores=None):
        self.lock = threading.RLock()
        self.cpu_count = cpu_count
        self.e_cores = e_cores if e_cores else []
        self.interrupt_assignments = {}
        self.device_affinities = {'gpu': None, 'nvme': None, 'nic': None}
        self.last_rebalance = time.time()
        self.stats = {'irq_bindings': 0, 'rebalances': 0, 'dpc_optimizations': 0, 'latency_improvements': 0}
    def detect_critical_devices(self):
        with self.lock:
            devices = {'gpu': [], 'nvme': [], 'nic': []}
            result = subprocess.run(['powershell', '-Command', 'Get-WmiObject Win32_VideoController | Select-Object Name, PNPDeviceID'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            if result.returncode == 0:
                output = result.stdout.decode('utf-8', errors='ignore')
                if 'NVIDIA' in output or 'AMD' in output or 'Intel' in output:
                    devices['gpu'].append('GPU')
    def bind_critical_irq_to_cores(self, device_type, dedicated_cores=None):
        with self.lock:
            if dedicated_cores is None:
                if device_type == 'gpu':
                    dedicated_cores = list(range(2, min(4, self.cpu_count)))
                elif device_type == 'nvme':
                    dedicated_cores = list(range(4, min(6, self.cpu_count)))
                elif device_type == 'nic':
                    if self.e_cores:
                        dedicated_cores = self.e_cores[:2]
                    else:
                        dedicated_cores = list(range(6, min(8, self.cpu_count)))
                else:
                    return False
            affinity_mask = sum((1 << core for core in dedicated_cores))
            self.device_affinities[device_type] = {'cores': dedicated_cores, 'mask': affinity_mask, 'bound_at': time.time()}
            self.stats['irq_bindings'] += 1
            if device_type == 'nic':
                key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'RssBaseCpu', 0, winreg.REG_DWORD, dedicated_cores[0])
                winreg.CloseKey(key)
    def optimize_dpc_batching(self):
        with self.lock:
            key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'DpcTimeout', 0, winreg.REG_DWORD, DPC_TIMEOUT_DISABLED)
            winreg.SetValueEx(key, 'DpcWatchdogProfileOffset', 0, winreg.REG_DWORD, DPC_WATCHDOG_PROFILE_OFFSET)
            winreg.SetValueEx(key, 'DpcQueueDepth', 0, winreg.REG_DWORD, DPC_QUEUE_DEPTH)
            winreg.CloseKey(key)
            self.stats['dpc_optimizations'] += 1
            return True
    def monitor_and_rebalance_interrupts(self, cpu_load_per_core):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_rebalance < 60:
                return False
            self.last_rebalance = current_time
            rebalance_needed = False
            for device_type, assignment in self.device_affinities.items():
                if assignment is None:
                    continue
                cores = assignment['cores']
                avg_load = sum((cpu_load_per_core.get(c, 0) for c in cores)) / len(cores)
                if avg_load > CORE_OVERLOAD_THRESHOLD:
                    rebalance_needed = True
                    available_cores = [c for c in range(self.cpu_count) if cpu_load_per_core.get(c, 0) < 50]
                    if available_cores:
                        new_cores = available_cores[:len(cores)]
                        self.bind_critical_irq_to_cores(device_type, new_cores)
                        self.stats['rebalances'] += 1
            return rebalance_needed
    def get_stats(self):
        with self.lock:
            return {'irq_bindings': self.stats['irq_bindings'], 'rebalances': self.stats['rebalances'], 'dpc_optimizations': self.stats['dpc_optimizations'], 'active_device_bindings': sum((1 for v in self.device_affinities.values() if v is not None)), 'estimated_overhead': 0.1}
class CStatesOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.c_states_disabled = False
        self.stats = {'optimizations_applied': 0}
    def disable_deep_c_states(self):
        with self.lock:
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_SLEEP', 'DEEPEST_CSTATE', '0'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.c_states_disabled = True
            self.stats['optimizations_applied'] += 1
            return True
    def enable_deep_c_states(self):
        with self.lock:
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_SLEEP', 'DEEPEST_CSTATE', '6'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.c_states_disabled = False
            return True
class StorageOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'optimizations_applied': 0, 'trim_scheduled': 0}
    def optimize_nvme_queue_depth(self):
        with self.lock:
            key_path = 'SYSTEM\\CurrentControlSet\\Services\\stornvme\\Parameters\\Device'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'QueueDepth', 0, winreg.REG_DWORD, NVME_OPTIMAL_QUEUE_DEPTH)
            winreg.CloseKey(key)
            self.stats['optimizations_applied'] += 1
            return True
    def optimize_file_system_cache(self):
        with self.lock:
            total_ram_gb = psutil.virtual_memory().total / 1024 ** 3
            if total_ram_gb >= 16:
                large_system_cache = 1
            else:
                large_system_cache = 0
            key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'LargeSystemCache', 0, winreg.REG_DWORD, large_system_cache)
            winreg.CloseKey(key)
            self.stats['optimizations_applied'] += 1
            return True
    def schedule_trim_during_idle(self):
        with self.lock:
            subprocess.run(['defrag', '/L'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            self.stats['trim_scheduled'] += 1
            return True
class NetworkOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'optimizations_applied': 0}
    def optimize_tcp_window_scaling(self):
        with self.lock:
            key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'Tcp1323Opts', 0, winreg.REG_DWORD, 3)
            winreg.CloseKey(key)
            self.stats['optimizations_applied'] += 1
            return True
    def configure_rss(self):
        with self.lock:
            subprocess.run(['powershell', '-Command', 'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Set-NetAdapterRss -Enabled $true -ErrorAction SilentlyContinue'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            self.stats['optimizations_applied'] += 1
            return True
    def disable_network_throttling(self):
        with self.lock:
            key_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'NetworkThrottlingIndex', 0, winreg.REG_DWORD, NETWORK_THROTTLING_DISABLED)
            winreg.CloseKey(key)
            self.stats['optimizations_applied'] += 1
            return True
class PowerManagementOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'optimizations_applied': 0}
    def disable_pcie_aspm(self):
        with self.lock:
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_PCIEXPRESS', 'ASPM', '0'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.stats['optimizations_applied'] += 1
            return True
    def disable_usb_selective_suspend(self):
        with self.lock:
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_USB', 'USBSELECTIVESUSPEND', '0'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.stats['optimizations_applied'] += 1
            return True
class KernelOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'optimizations_applied': 0}
        self.original_settings = {}
    def optimize_timer_resolution(self):
        with self.lock:
            return True
    def increase_paged_pool_size(self):
        with self.lock:
            total_ram_gb = psutil.virtual_memory().total / 1024 ** 3
            if total_ram_gb >= 32:
                paged_pool_size = 0
                key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management'
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'PagedPoolSize', 0, winreg.REG_DWORD, paged_pool_size)
                winreg.CloseKey(key)
                self.stats['optimizations_applied'] += 1
                return True
    def disable_vbs_for_gaming(self):
        with self.lock:
            subprocess.run(['bcdedit', '/set', 'hypervisorlaunchtype', 'off'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.stats['optimizations_applied'] += 1
            return True
    def enable_vbs(self):
        with self.lock:
            subprocess.run(['bcdedit', '/set', 'hypervisorlaunchtype', 'auto'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
class AdaptiveReadAheadManager:
    SMALL_READAHEAD = 32 * 1024
    MEDIUM_READAHEAD = 64 * 1024
    NORMAL_READAHEAD = 128 * 1024
    LARGE_READAHEAD = 256 * 1024
    SEQUENTIAL_THRESHOLD = 0.8
    MEDIUM_THRESHOLD = 0.5
    def __init__(self):
        self.lock = threading.RLock()
        self.file_access_patterns = {}
        self.stats = {'optimizations': 0, 'pattern_detections': 0}
    def analyze_access_pattern(self, file_path, offset):
        with self.lock:
            if file_path not in self.file_access_patterns:
                self.file_access_patterns[file_path] = {'sequential_count': 0, 'random_count': 0, 'last_offset': 0, 'offsets': deque(maxlen=10)}
            pattern = self.file_access_patterns[file_path]
            pattern['offsets'].append(offset)
            if len(pattern['offsets']) >= 2:
                deltas = [pattern['offsets'][i + 1] - pattern['offsets'][i] for i in range(len(pattern['offsets']) - 1)]
                if all((d > 0 for d in deltas)):
                    pattern['sequential_count'] += 1
                    is_sequential = True
                else:
                    pattern['random_count'] += 1
                    is_sequential = False
                pattern['last_offset'] = offset
                self.stats['pattern_detections'] += 1
                return is_sequential
            return None
    def get_recommended_readahead_size(self, file_path):
        with self.lock:
            if file_path not in self.file_access_patterns:
                return self.MEDIUM_READAHEAD
            pattern = self.file_access_patterns[file_path]
            total = pattern['sequential_count'] + pattern['random_count']
            if total == 0:
                return self.MEDIUM_READAHEAD
            sequential_ratio = pattern['sequential_count'] / total
            if sequential_ratio > self.SEQUENTIAL_THRESHOLD:
                return self.LARGE_READAHEAD
            elif sequential_ratio > self.MEDIUM_THRESHOLD:
                return self.NORMAL_READAHEAD
            else:
                return self.SMALL_READAHEAD
class WriteCoalescingManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.write_buffers = {}
        self.stats = {'writes_coalesced': 0, 'bytes_saved': 0}
        self.buffer_size_limit = 1024 * 1024
    def buffer_write(self, file_id, data, is_critical=False):
        with self.lock:
            if is_critical:
                return False
            if file_id not in self.write_buffers:
                self.write_buffers[file_id] = []
            self.write_buffers[file_id].append(data)
            total_size = sum((len(d) for d in self.write_buffers[file_id]))
            if total_size >= self.buffer_size_limit:
                self.stats['writes_coalesced'] += len(self.write_buffers[file_id])
                self.write_buffers[file_id] = []
                return True
            return False
class StorageTierManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.storage_tiers = self._detect_storage_tiers()
        self.file_access_counts = {}
        self.stats = {'migrations': 0, 'tiers_detected': len(self.storage_tiers)}
    def _detect_storage_tiers(self):
        tiers = []
        partitions = psutil.disk_partitions()
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            is_nvme = 'nvme' in partition.device.lower()
            is_removable = 'removable' in partition.opts.lower() if hasattr(partition, 'opts') else False
            tier_info = {'mountpoint': partition.mountpoint, 'total': usage.total, 'fstype': partition.fstype, 'is_nvme': is_nvme, 'is_removable': is_removable}
            tiers.append(tier_info)
        tiers.sort(key=lambda x: (x['is_nvme'], not x['is_removable']), reverse=True)
        return tiers
    def track_file_access(self, file_path):
        with self.lock:
            if file_path not in self.file_access_counts:
                self.file_access_counts[file_path] = 0
            self.file_access_counts[file_path] += 1
class DynamicDiskCacheTuner:
    LARGE_CACHE = 1
    NORMAL_CACHE = 0
    LARGE_CACHE_RAM_THRESHOLD_GB = 8
    NORMAL_CACHE_RAM_THRESHOLD_GB = 4
    BYTES_PER_GB = 1024 ** 3
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'tuning_operations': 0}
    def tune_cache(self):
        with self.lock:
            memory = psutil.virtual_memory()
            available_gb = memory.available / self.BYTES_PER_GB
            if available_gb > self.LARGE_CACHE_RAM_THRESHOLD_GB:
                cache_size = self.LARGE_CACHE
            elif available_gb > self.NORMAL_CACHE_RAM_THRESHOLD_GB:
                cache_size = self.NORMAL_CACHE
            else:
                cache_size = self.NORMAL_CACHE
            key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'LargeSystemCache', 0, winreg.REG_DWORD, cache_size)
            winreg.CloseKey(key)
            self.stats['tuning_operations'] += 1
            return True
class NetworkFlowPrioritizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'flows_prioritized': 0}
        self.active_policies = set()
    def prioritize_foreground_traffic(self, pid):
        with self.lock:
            policy_name = f'ForegroundApp_{pid}'
            if policy_name in self.active_policies:
                return True
            subprocess.run(['powershell', '-Command', f'New-NetQosPolicy -Name "{policy_name}" -IPProtocolMatchCondition Both -PriorityValue8021Action 7 -ErrorAction SilentlyContinue'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            self.active_policies.add(policy_name)
            self.stats['flows_prioritized'] += 1
            return True
    def cleanup_old_policies(self):
        with self.lock:
            subprocess.run(['powershell', '-Command', 'Get-NetQosPolicy | Where-Object {$_.Name -like "ForegroundApp_*"} | Remove-NetQosPolicy -Confirm:$false -ErrorAction SilentlyContinue'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            self.active_policies.clear()
            return True
class TCPCongestionControlTuner:
    LOW_LATENCY_THRESHOLD_MS = 20
    MEDIUM_LATENCY_THRESHOLD_MS = 100
    HIGH_THROUGHPUT_MBPS = 500
    MEDIUM_THROUGHPUT_MBPS = 100
    LOW_THROUGHPUT_MBPS = 10
    LOW_LATENCY_ESTIMATE_MS = 10
    MEDIUM_LOW_LATENCY_ESTIMATE_MS = 30
    MEDIUM_HIGH_LATENCY_ESTIMATE_MS = 60
    HIGH_LATENCY_ESTIMATE_MS = 120
    BITS_PER_BYTE = 8
    BYTES_PER_MB = 1024 * 1024
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'tuning_operations': 0}
        self.current_algorithm = 'cubic'
        self.last_bytes_sent = 0
        self.last_check_time = time.time()
    def detect_and_tune(self):
        with self.lock:
            net_io = psutil.net_io_counters()
            if net_io:
                current_time = time.time()
                time_delta = current_time - self.last_check_time
                if time_delta > 0 and self.last_bytes_sent > 0:
                    bytes_delta = net_io.bytes_sent - self.last_bytes_sent
                    throughput_mbps = bytes_delta * self.BITS_PER_BYTE / (time_delta * self.BYTES_PER_MB)
                    latency = self._estimate_latency(throughput_mbps)
                    if latency < self.LOW_LATENCY_THRESHOLD_MS:
                        algorithm = 'bbr'
                    elif latency < self.MEDIUM_LATENCY_THRESHOLD_MS:
                        algorithm = 'cubic'
                    else:
                        algorithm = 'reno'
                    if algorithm != self.current_algorithm:
                        self._apply_tcp_settings(algorithm)
                        self.current_algorithm = algorithm
                        self.stats['tuning_operations'] += 1
                self.last_bytes_sent = net_io.bytes_sent
                self.last_check_time = current_time
            return True
    def _estimate_latency(self, throughput_mbps):
        if throughput_mbps > self.HIGH_THROUGHPUT_MBPS:
            return self.LOW_LATENCY_ESTIMATE_MS
        elif throughput_mbps > self.MEDIUM_THROUGHPUT_MBPS:
            return self.MEDIUM_LOW_LATENCY_ESTIMATE_MS
        elif throughput_mbps > self.LOW_THROUGHPUT_MBPS:
            return self.MEDIUM_HIGH_LATENCY_ESTIMATE_MS
        else:
            return self.HIGH_LATENCY_ESTIMATE_MS
    def _apply_tcp_settings(self, algorithm):
        key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'TcpCongestionControl', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
class NetworkInterruptCoalescer:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'optimizations': 0}
    def optimize_interrupt_coalescing(self):
        with self.lock:
            subprocess.run(['powershell', '-Command', 'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Set-NetAdapterAdvancedProperty -DisplayName "Interrupt Moderation" -DisplayValue "Enabled"'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            self.stats['optimizations'] += 1
            return True
class AdaptiveNetworkPollingManager:
    POLLING_THROUGHPUT_THRESHOLD = 1000000000
    HYBRID_THROUGHPUT_THRESHOLD = 100000000
    POLLING_CPU_THRESHOLD = 50
    HYBRID_CPU_THRESHOLD = 70
    def __init__(self):
        self.lock = threading.RLock()
        self.polling_mode = 'interrupt'
        self.stats = {'mode_switches': 0}
    def adjust_polling_mode(self):
        with self.lock:
            net_io = psutil.net_io_counters()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if net_io:
                throughput = net_io.bytes_sent + net_io.bytes_recv
                if throughput > self.POLLING_THROUGHPUT_THRESHOLD and cpu_percent < self.POLLING_CPU_THRESHOLD:
                    new_mode = 'polling'
                elif throughput > self.HYBRID_THROUGHPUT_THRESHOLD and cpu_percent < self.HYBRID_CPU_THRESHOLD:
                    new_mode = 'hybrid'
                else:
                    new_mode = 'interrupt'
                if new_mode != self.polling_mode:
                    self.polling_mode = new_mode
                    self.stats['mode_switches'] += 1
            return True
    def enable_polling_mode(self, enable):
        with self.lock:
            desired_mode = 'polling' if enable else 'interrupt'
            if desired_mode != self.polling_mode:
                self.polling_mode = desired_mode
                self.stats['mode_switches'] += 1
            return True
class MultiLevelTimerCoalescer:
    def __init__(self):
        self.lock = threading.RLock()
        self.urgency_levels = {'critical': 1, 'high': 5, 'medium': 15, 'low': 50, 'very_low': 100}
        self.task_queue = {level: [] for level in self.urgency_levels.keys()}
        self.stats = {'tasks_coalesced': 0}
    def register_task(self, task_id, urgency='medium', callback=None):
        with self.lock:
            if urgency in self.task_queue:
                self.task_queue[urgency].append({'id': task_id, 'callback': callback, 'registered_at': time.time()})
                return True
            return False
    def execute_due_tasks(self):
        with self.lock:
            current_time = time.time()
            for urgency, interval_ms in self.urgency_levels.items():
                tasks_to_execute = []
                for task in self.task_queue[urgency]:
                    if (current_time - task['registered_at']) * 1000 >= interval_ms:
                        tasks_to_execute.append(task)
                for task in tasks_to_execute:
                    if task['callback']:
                        task['callback']()
                    self.task_queue[urgency].remove(task)
                    self.stats['tasks_coalesced'] += 1
class SystemCallBatcher:
    def __init__(self):
        self.lock = threading.RLock()
        self.batched_calls = []
        self.stats = {'batches_executed': 0, 'calls_batched': 0}
        self.batch_size = 10
    def add_syscall(self, syscall_func, args):
        with self.lock:
            self.batched_calls.append((syscall_func, args))
            self.stats['calls_batched'] += 1
            if len(self.batched_calls) >= self.batch_size:
                return self.execute_batch()
            return False
    def execute_batch(self):
        with self.lock:
            if not self.batched_calls:
                return False
            for syscall_func, args in self.batched_calls:
                syscall_func(*args)
            self.batched_calls = []
            self.stats['batches_executed'] += 1
            return True
class DynamicVoltageFrequencyScaler:
    HIGH_WORKLOAD_THRESHOLD = 80
    MEDIUM_WORKLOAD_THRESHOLD = 50
    MAX_THROTTLE = 0
    MEDIUM_THROTTLE = 50
    HIGH_THROTTLE = 100
    def __init__(self):
        self.lock = threading.RLock()
        self.per_core_states = {}
        self.stats = {'adjustments': 0}
    def adjust_core_frequency(self, core_id, workload_level):
        with self.lock:
            if workload_level > self.HIGH_WORKLOAD_THRESHOLD:
                throttle_percent = self.MAX_THROTTLE
            elif workload_level > self.MEDIUM_WORKLOAD_THRESHOLD:
                throttle_percent = self.MEDIUM_THROTTLE
            else:
                throttle_percent = self.HIGH_THROTTLE
            max_frequency_percent = 100 - throttle_percent
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 'SUB_PROCESSOR', 'PROCTHROTTLEMAX', str(max_frequency_percent)], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=2)
            self.per_core_states[core_id] = throttle_percent
            self.stats['adjustments'] += 1
            return True
class CPUTemperatureMonitor:
    MIN_TEMP_FALLBACK = 35.0
    MAX_TEMP_FALLBACK = 75.0
    def __init__(self):
        self.lock = threading.RLock()
        self.current_temp = 0.0
        self.is_laptop = self._is_laptop()
        self.max_temp_desktop = 70
        self.max_temp_laptop = 78
        self.max_temp = self.max_temp_laptop if self.is_laptop else self.max_temp_desktop
        self.monitoring_active = False
        self.hardware_monitor = None
        self.cpu_sensor = None
        self.temp_range = self.MAX_TEMP_FALLBACK - self.MIN_TEMP_FALLBACK
        if TEMP_MONITORING_AVAILABLE:
            self._init_hardware_monitor()
    def _is_laptop(self):
        battery = psutil.sensors_battery()
        return battery is not None
        return False
    def _init_hardware_monitor(self):
        computer = Hardware.Computer()
        computer.IsCpuEnabled = True
        computer.Open()
        self.hardware_monitor = computer
        for hardware in computer.Hardware:
            if hardware.HardwareType == Hardware.HardwareType.Cpu:
                hardware.Update()
                for sensor in hardware.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature:
                        if 'Package' in sensor.Name or 'Core Average' in sensor.Name:
                            self.cpu_sensor = (hardware, sensor)
                            self.monitoring_active = True
                            break
                if self.cpu_sensor:
                    break
    def _calculate_temp_from_cpu_usage(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return self.MIN_TEMP_FALLBACK + cpu_percent / 100.0 * self.temp_range
    def get_current_temperature(self):
        with self.lock:
            if not self.monitoring_active or not self.cpu_sensor:
                self.current_temp = self._calculate_temp_from_cpu_usage()
                return self.current_temp
            hardware, sensor = self.cpu_sensor
            hardware.Update()
            if sensor.Value:
                self.current_temp = float(sensor.Value)
            return self.current_temp
    def is_overheating(self):
        temp = self.get_current_temperature()
        return temp >= self.max_temp
    def set_max_temperature(self, temp):
        with self.lock:
            self.max_temp = max(50, min(100, temp))
    def increase_max_temp(self):
        with self.lock:
            self.max_temp = min(100, self.max_temp + 1)
    def decrease_max_temp(self):
        with self.lock:
            self.max_temp = max(50, self.max_temp - 1)
    def cleanup(self):
        with self.lock:
            if self.hardware_monitor:
                self.hardware_monitor.Close()
class ThermalAwareScheduler:
    def __init__(self, cpu_count, temp_monitor):
        self.lock = threading.RLock()
        self.cpu_count = cpu_count
        self.temp_monitor = temp_monitor
        self.per_core_temps = {}
        self.core_load_history = defaultdict(lambda: deque(maxlen=10))
        self.last_migration = {}
        self.last_rotation = time.time()
        self.stats = {'migrations': 0, 'rotations': 0, 'throttle_preventions': 0}
        self.hot_threshold = 75
        self.cool_threshold = 60
        self.critical_threshold = 85
    def get_per_core_temperatures(self):
        with self.lock:
            base_temp = self.temp_monitor.get_current_temperature()
            per_core_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            for core_idx, load_percent in enumerate(per_core_percent):
                temp_delta = load_percent / 100.0 * TEMP_DELTA_PER_LOAD
                estimated_temp = base_temp + temp_delta - TEMP_CENTERING_OFFSET
                self.per_core_temps[core_idx] = max(30, min(100, estimated_temp))
                self.core_load_history[core_idx].append(load_percent)
            return self.per_core_temps.copy()
    def find_coolest_cores(self, count=4):
        with self.lock:
            temps = self.get_per_core_temperatures()
            if not temps:
                return list(range(count))
            sorted_cores = sorted(temps.items(), key=lambda x: x[1])
            return [core_idx for core_idx, _ in sorted_cores[:count]]
    def find_hottest_cores(self):
        with self.lock:
            temps = self.get_per_core_temperatures()
            hot_cores = [core_idx for core_idx, temp in temps.items() if temp >= self.hot_threshold]
            return hot_cores
    def migrate_process_to_cooler_cores(self, pid, handle_cache):
        with self.lock:
            current_time = time.time()
            if pid in self.last_migration:
                if current_time - self.last_migration[pid] < 30:
                    return False
            coolest_cores = self.find_coolest_cores(count=4)
            if not coolest_cores:
                return False
            handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if handle:
                affinity_mask = sum((1 << core for core in coolest_cores))
                result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                if result:
                    self.last_migration[pid] = current_time
                    self.stats['migrations'] += 1
                    return True
            return False
    def rotate_loads_for_heat_distribution(self, active_pids, handle_cache):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_rotation < 60:
                return False
            self.last_rotation = current_time
            cores_per_group = max(2, self.cpu_count // 4)
            groups = []
            for i in range(0, self.cpu_count, cores_per_group):
                groups.append(list(range(i, min(i + cores_per_group, self.cpu_count))))
            for idx, pid in enumerate(active_pids[:len(groups)]):
                group_idx = idx % len(groups)
                cores = groups[group_idx]
                handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
                if handle:
                    affinity_mask = sum((1 << core for core in cores))
                    kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
    def predict_and_prevent_throttling(self):
        with self.lock:
            temps = self.get_per_core_temperatures()
            hot_cores = [core_idx for core_idx, temp in temps.items() if temp >= self.critical_threshold - 5]
            if hot_cores:
                avg_temp = sum(temps.values()) / len(temps)
                if avg_temp > self.hot_threshold:
                    self.stats['throttle_preventions'] += 1
                    return True
            return False
    def get_stats(self):
        with self.lock:
            temps = self.get_per_core_temperatures()
            avg_temp = sum(temps.values()) / len(temps) if temps else 0
            max_temp = max(temps.values()) if temps else 0
            return {'average_temp': avg_temp, 'max_temp': max_temp, 'hot_cores': len([t for t in temps.values() if t >= self.hot_threshold]), 'total_migrations': self.stats['migrations'], 'total_rotations': self.stats['rotations'], 'throttle_preventions': self.stats['throttle_preventions'], 'estimated_overhead': 0.2}
class DynamicPriorityAlgorithm:
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.process_metrics = {}
        self.stats = {'priority_adjustments': 0, 'processes_analyzed': 0}
    def analyze_process(self, pid):
        with self.lock:
            proc = psutil.Process(pid)
            cpu_percent = proc.cpu_percent(interval=0.1)
            io_counters = proc.io_counters()
            memory_info = proc.memory_info()
            num_threads = proc.num_threads()
            create_time = proc.create_time()
            current_time = time.time()
            execution_time = current_time - create_time
            io_rate = (io_counters.read_bytes + io_counters.write_bytes) / max(execution_time, 1)
            children = proc.children(recursive=True)
            num_dependencies = len(children)
            score = self._calculate_priority_score(cpu_percent, io_rate, memory_info.rss, execution_time, num_threads, num_dependencies)
            self.process_metrics[pid] = {'score': score, 'cpu': cpu_percent, 'io_rate': io_rate, 'memory': memory_info.rss, 'execution_time': execution_time, 'threads': num_threads, 'dependencies': num_dependencies, 'last_update': current_time}
            self.stats['processes_analyzed'] += 1
            return score
    def _calculate_priority_score(self, cpu, io_rate, memory, exec_time, threads, deps):
        cpu_score = min(cpu / 100.0 * 30, 30)
        io_score = min(io_rate / (1024 * 1024 * 100) * 20, 20)
        mem_score = min(memory / (1024 * 1024 * 1024) * 15, 15)
        time_score = min(exec_time / 3600 * 10, 10)
        thread_score = min(threads / 50 * 15, 15)
        dep_score = min(deps / 10 * 10, 10)
        total_score = cpu_score + io_score + mem_score + time_score + thread_score + dep_score
        return min(max(total_score, 0), 100)
    def adjust_priority(self, pid, is_foreground):
        with self.lock:
            score = self.analyze_process(pid)
            if is_foreground:
                if score > 70:
                    priority_class = PRIORITY_CLASSES['HIGH']
                elif score > 40:
                    priority_class = PRIORITY_CLASSES['ABOVE_NORMAL']
                else:
                    priority_class = PRIORITY_CLASSES['NORMAL']
            elif score > 70:
                priority_class = PRIORITY_CLASSES['NORMAL']
            elif score > 40:
                priority_class = PRIORITY_CLASSES['BELOW_NORMAL']
            else:
                priority_class = PRIORITY_CLASSES['IDLE']
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                win32process.SetPriorityClass(int(handle), priority_class)
                self.stats['priority_adjustments'] += 1
                return True
            return False
class RealtimeTelemetryCollector:
    __slots__ = ('lock', 'metrics', 'stats', 'last_collection', 'collection_interval')
    def __init__(self):
        self.lock = threading.RLock()
        self.metrics = {'cpu_temps': CircularBuffer(60), 'power_usage': CircularBuffer(60), 'memory_pressure': CircularBuffer(60), 'io_wait': CircularBuffer(60), 'disk_latency': CircularBuffer(60), 'network_throughput': CircularBuffer(60)}
        self.stats = {'collections': 0, 'anomalies_detected': 0}
        self.last_collection = 0
        self.collection_interval = 1.0
    def collect_metrics(self):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_collection < self.collection_interval:
                return
            cpu_temp = self._get_cpu_temp()
            self.metrics['cpu_temps'].append(cpu_temp)
            memory = psutil.virtual_memory()
            memory_pressure = memory.percent
            self.metrics['memory_pressure'].append(memory_pressure)
            disk_io = psutil.disk_io_counters()
            if disk_io:
                io_wait = disk_io.read_time + disk_io.write_time
                self.metrics['io_wait'].append(io_wait)
            net_io = psutil.net_io_counters()
            if net_io:
                throughput = net_io.bytes_sent + net_io.bytes_recv
                self.metrics['network_throughput'].append(throughput)
            self.stats['collections'] += 1
            self.last_collection = current_time
            self._detect_anomalies()
    def _get_cpu_temp(self):
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            return sum((t.current for t in temps['coretemp'])) / len(temps['coretemp'])
        return 0
    def _detect_anomalies(self):
        with self.lock:
            if len(self.metrics['memory_pressure']) >= 10:
                recent_pressure = list(self.metrics['memory_pressure'])[-10:]
                avg_pressure = sum(recent_pressure) / len(recent_pressure)
                if avg_pressure > 90:
                    self.stats['anomalies_detected'] += 1
    def get_metric_average(self, metric_name, samples=10):
        with self.lock:
            if metric_name not in self.metrics:
                return 0
            data = list(self.metrics[metric_name])[-samples:]
            if not data:
                return 0
            return sum(data) / len(data)
    def should_throttle(self):
        with self.lock:
            mem_pressure = self.get_metric_average('memory_pressure', 5)
            cpu_temp = self.get_metric_average('cpu_temps', 5)
            return mem_pressure > 85 or cpu_temp > 80
class AutomaticProfileManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_profile = 'Balanced'
        self.profiles = {'Gaming': {'keywords': ['game', 'steam', 'epic', 'origin', 'uplay', 'battle.net', 'gog', 'dx11', 'dx12', 'vulkan'], 'cpu_priority': 'HIGH', 'memory_priority': 'NORMAL', 'io_priority': 'HIGH', 'disable_background': True}, 'Productivity': {'keywords': ['office', 'word', 'excel', 'powerpoint', 'outlook', 'teams', 'slack', 'zoom'], 'cpu_priority': 'ABOVE_NORMAL', 'memory_priority': 'NORMAL', 'io_priority': 'NORMAL', 'disable_background': False}, 'Video Editing': {'keywords': ['premiere', 'aftereffects', 'davinci', 'vegas', 'handbrake', 'ffmpeg'], 'cpu_priority': 'HIGH', 'memory_priority': 'HIGH', 'io_priority': 'HIGH', 'disable_background': True}, 'Coding': {'keywords': ['code', 'visual studio', 'intellij', 'pycharm', 'eclipse', 'atom', 'sublime'], 'cpu_priority': 'ABOVE_NORMAL', 'memory_priority': 'NORMAL', 'io_priority': 'NORMAL', 'disable_background': False}, 'Balanced': {'keywords': [], 'cpu_priority': 'NORMAL', 'memory_priority': 'NORMAL', 'io_priority': 'NORMAL', 'disable_background': False}}
        self.stats = {'profile_switches': 0}
    def detect_profile(self, process_name):
        with self.lock:
            process_lower = process_name.lower()
            for profile_name, profile_data in self.profiles.items():
                if profile_name == 'Balanced':
                    continue
                for keyword in profile_data['keywords']:
                    if keyword in process_lower:
                        if self.current_profile != profile_name:
                            self.current_profile = profile_name
                            self.stats['profile_switches'] += 1
                        return profile_name
            if self.current_profile != 'Balanced':
                self.current_profile = 'Balanced'
                self.stats['profile_switches'] += 1
            return 'Balanced'
    def get_profile_settings(self, profile_name=None):
        with self.lock:
            if profile_name is None:
                profile_name = self.current_profile
            return self.profiles.get(profile_name, self.profiles['Balanced'])
class DynamicMultiLayerProfileSystem:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_scenario = 'browsing'
        self.scenario_history = deque(maxlen=100)
        self.process_patterns = defaultdict(lambda: {'co_occurrence': defaultdict(int), 'hourly_usage': defaultdict(int), 'typical_load': defaultdict(list)})
        self.scenario_start_time = time.time()
        self.stats = {'scenario_switches': 0, 'auto_adjustments': 0, 'pattern_learnings': 0}
        self.scenarios = {'gaming': {'keywords': ['game', 'steam', 'epic', 'origin', 'uplay', 'battle.net', 'gog', 'dx11', 'dx12', 'vulkan', 'unreal', 'unity'], 'priority': {'cpu': 'HIGH', 'memory': 'NORMAL', 'io': 'HIGH', 'page': PAGE_PRIORITY_NORMAL}, 'affinity': {'prefer_physical_cores': True, 'avoid_smt_sharing': True, 'isolate_from_background': True}, 'system': {'responsiveness': 10, 'timer_resolution': 0.5, 'disable_background_tasks': True, 'gpu_priority': 'HIGH'}, 'weight': 10}, 'productivity': {'keywords': ['office', 'word', 'excel', 'powerpoint', 'outlook', 'teams', 'slack', 'zoom', 'webex', 'notes', 'onenote'], 'priority': {'cpu': 'ABOVE_NORMAL', 'memory': 'NORMAL', 'io': 'NORMAL', 'page': PAGE_PRIORITY_NORMAL}, 'affinity': {'prefer_physical_cores': False, 'avoid_smt_sharing': False, 'isolate_from_background': False}, 'system': {'responsiveness': 20, 'timer_resolution': 1.0, 'disable_background_tasks': False, 'gpu_priority': 'NORMAL'}, 'weight': 7}, 'rendering': {'keywords': ['premiere', 'aftereffects', 'davinci', 'vegas', 'handbrake', 'ffmpeg', 'blender', 'maya', '3dsmax', 'cinema4d'], 'priority': {'cpu': 'HIGH', 'memory': 'HIGH', 'io': 'HIGH', 'page': PAGE_PRIORITY_NORMAL}, 'affinity': {'prefer_physical_cores': True, 'avoid_smt_sharing': False, 'isolate_from_background': True}, 'system': {'responsiveness': 15, 'timer_resolution': 1.0, 'disable_background_tasks': True, 'gpu_priority': 'HIGH'}, 'weight': 9}, 'development': {'keywords': ['code', 'visual studio', 'intellij', 'pycharm', 'eclipse', 'atom', 'sublime', 'vscode', 'rider', 'android studio'], 'priority': {'cpu': 'ABOVE_NORMAL', 'memory': 'ABOVE_NORMAL', 'io': 'ABOVE_NORMAL', 'page': PAGE_PRIORITY_NORMAL}, 'affinity': {'prefer_physical_cores': False, 'avoid_smt_sharing': False, 'isolate_from_background': False}, 'system': {'responsiveness': 20, 'timer_resolution': 1.0, 'disable_background_tasks': False, 'gpu_priority': 'NORMAL'}, 'weight': 6}, 'browsing': {'keywords': ['chrome', 'firefox', 'edge', 'brave', 'opera', 'safari'], 'priority': {'cpu': 'NORMAL', 'memory': 'NORMAL', 'io': 'NORMAL', 'page': PAGE_PRIORITY_NORMAL}, 'affinity': {'prefer_physical_cores': False, 'avoid_smt_sharing': False, 'isolate_from_background': False}, 'system': {'responsiveness': 20, 'timer_resolution': 1.0, 'disable_background_tasks': False, 'gpu_priority': 'NORMAL'}, 'weight': 3}}
    def detect_scenario(self, active_processes):
        with self.lock:
            scenario_scores = defaultdict(float)
            current_hour = time.localtime().tm_hour
            for proc in active_processes:
                proc_lower = proc.lower()
                for scenario_name, scenario_data in self.scenarios.items():
                    for keyword in scenario_data['keywords']:
                        if keyword in proc_lower:
                            score = scenario_data['weight']
                            hourly_pattern = self.process_patterns[proc]['hourly_usage']
                            if hourly_pattern.get(current_hour, 0) > 0:
                                score *= 1.2
                            scenario_scores[scenario_name] += score
            if not scenario_scores:
                detected_scenario = 'browsing'
                confidence = 0.5
            else:
                detected_scenario = max(scenario_scores.items(), key=lambda x: x[1])[0]
                total_score = sum(scenario_scores.values())
                confidence = scenario_scores[detected_scenario] / total_score if total_score > 0 else 0
            if detected_scenario != self.current_scenario:
                self.scenario_history.append({'scenario': detected_scenario, 'timestamp': time.time(), 'confidence': confidence})
                self.current_scenario = detected_scenario
                self.scenario_start_time = time.time()
                self.stats['scenario_switches'] += 1
            return (detected_scenario, confidence)
    def learn_process_patterns(self, pid, process_name, cpu_percent, memory_percent):
        with self.lock:
            current_hour = time.localtime().tm_hour
            patterns = self.process_patterns[process_name]
            patterns['hourly_usage'][current_hour] += 1
            patterns['typical_load']['cpu'].append(cpu_percent)
            patterns['typical_load']['memory'].append(memory_percent)
            if len(patterns['typical_load']['cpu']) > 100:
                patterns['typical_load']['cpu'].pop(0)
            if len(patterns['typical_load']['memory']) > 100:
                patterns['typical_load']['memory'].pop(0)
            self.stats['pattern_learnings'] += 1
    def get_adaptive_settings(self, process_name, pid=None):
        with self.lock:
            scenario_settings = self.scenarios.get(self.current_scenario, self.scenarios['browsing'])
            patterns = self.process_patterns.get(process_name, {})
            settings = {'priority': scenario_settings['priority'].copy(), 'affinity': scenario_settings['affinity'].copy(), 'system': scenario_settings['system'].copy(), 'predicted_load': {'cpu': 0, 'memory': 0}}
            if patterns and 'typical_load' in patterns:
                cpu_loads = patterns['typical_load'].get('cpu', [])
                mem_loads = patterns['typical_load'].get('memory', [])
                if cpu_loads:
                    settings['predicted_load']['cpu'] = sum(cpu_loads) / len(cpu_loads)
                if mem_loads:
                    settings['predicted_load']['memory'] = sum(mem_loads) / len(mem_loads)
            self.stats['auto_adjustments'] += 1
            return settings
    def get_scenario_metrics(self):
        with self.lock:
            scenario_duration = time.time() - self.scenario_start_time
            return {'current_scenario': self.current_scenario, 'scenario_duration': scenario_duration, 'total_switches': self.stats['scenario_switches'], 'auto_adjustments': self.stats['auto_adjustments'], 'patterns_learned': self.stats['pattern_learnings'], 'overhead_estimate': 0.3}
class NUMAAwareMemoryAllocator:
    def __init__(self):
        self.lock = threading.RLock()
        self.numa_nodes = self._detect_numa_nodes()
        self.stats = {'allocations': 0, 'optimizations': 0}
    def _detect_numa_nodes(self):
        nodes = {}
        for cpu in range(psutil.cpu_count(logical=True)):
            node_number = ctypes.c_ubyte()
            if kernel32.GetNumaProcessorNode(cpu, ctypes.byref(node_number)):
                node = node_number.value
                if node not in nodes:
                    nodes[node] = []
                nodes[node].append(cpu)
        return nodes
    def optimize_process_numa(self, pid, preferred_cores):
        with self.lock:
            if len(self.numa_nodes) <= 1:
                return False
            if not preferred_cores:
                return False
            first_core = preferred_cores[0]
            target_node = None
            for node, cores in self.numa_nodes.items():
                if first_core in cores:
                    target_node = node
                    break
            if target_node is not None:
                proc = psutil.Process(pid)
                node_cores = self.numa_nodes[target_node]
                proc.cpu_affinity(node_cores)
                self.stats['optimizations'] += 1
                return True
            return False
class DynamicHugePagesManager:
    ACCESS_THRESHOLD = 1000000
    MEMORY_THRESHOLD_GB = 2
    MEMORY_ACCESS_DETECTION_THRESHOLD = 1024 * 1024
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.monitored_processes = {}
        self.stats = {'huge_pages_enabled': 0, 'processes_monitored': 0}
    def monitor_process(self, pid):
        with self.lock:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            if pid not in self.monitored_processes:
                self.monitored_processes[pid] = {'start_rss': mem_info.rss, 'last_rss': mem_info.rss, 'access_count': 0, 'huge_pages_enabled': False}
                self.stats['processes_monitored'] += 1
            else:
                data = self.monitored_processes[pid]
                rss_delta = abs(mem_info.rss - data['last_rss'])
                if rss_delta > self.MEMORY_ACCESS_DETECTION_THRESHOLD:
                    data['access_count'] += 1
                data['last_rss'] = mem_info.rss
                memory_threshold_bytes = self.MEMORY_THRESHOLD_GB * 1024 * 1024 * 1024
                if data['access_count'] > self.ACCESS_THRESHOLD and (not data['huge_pages_enabled']):
                    if mem_info.rss > memory_threshold_bytes:
                        self._enable_huge_pages(pid)
                        data['huge_pages_enabled'] = True
                        self.stats['huge_pages_enabled'] += 1
    def _enable_huge_pages(self, pid):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_QUOTA)
            if handle:
                min_ws = 2 * 1024 * 1024 * 1024
                max_ws = 4 * 1024 * 1024 * 1024
                flags = QUOTA_LIMITS_HARDWS_MIN_ENABLE | QUOTA_LIMITS_HARDWS_MAX_ENABLE
                kernel32.SetProcessWorkingSetSizeEx(handle, min_ws, max_ws, flags)
                return True
            return False
class MemoryDeduplicationManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {'dedup_attempts': 0, 'pages_deduplicated': 0}
    def enable_memory_compression(self, pid):
        with self.lock:
            subprocess.run(['powershell', '-Command', 'Enable-MMAgent -MemoryCompression'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            self.stats['dedup_attempts'] += 1
            return True
class AdvancedMemoryPagePriorityManager:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.process_working_sets = {}
        self.page_access_patterns = defaultdict(lambda: {'sequential_accesses': 0, 'random_accesses': 0, 'hot_pages': set(), 'cold_pages': set()})
        self.last_analysis_time = {}
        self.stats = {'promotions': 0, 'demotions': 0, 'prefetch_hints': 0, 'page_fault_reductions': 0, 'working_set_optimizations': 0}
    def analyze_working_set(self, pid):
        with self.lock:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            working_set_mb = mem_info.wset / (1024 * 1024)
            if pid not in self.process_working_sets:
                self.process_working_sets[pid] = {'current_ws': working_set_mb, 'peak_ws': working_set_mb, 'min_ws': working_set_mb, 'history': deque(maxlen=20), 'last_update': time.time()}
            else:
                ws_data = self.process_working_sets[pid]
                ws_data['history'].append(working_set_mb)
                ws_data['current_ws'] = working_set_mb
                ws_data['peak_ws'] = max(ws_data['peak_ws'], working_set_mb)
                ws_data['min_ws'] = min(ws_data['min_ws'], working_set_mb)
                ws_data['last_update'] = time.time()
            return True
    def optimize_page_priority(self, pid, is_foreground=False):
        with self.lock:
            current_time = time.time()
            if pid in self.last_analysis_time:
                if current_time - self.last_analysis_time[pid] < 10:
                    return False
            self.last_analysis_time[pid] = current_time
            if is_foreground:
                page_priority = PAGE_PRIORITY_NORMAL
            elif pid in self.process_working_sets:
                ws_data = self.process_working_sets[pid]
                history = list(ws_data['history'])
                if len(history) >= 5:
                    variance = sum(((x - ws_data['current_ws']) ** 2 for x in history[-5:])) / 5
                    if variance < 10:
                        page_priority = PAGE_PRIORITY_NORMAL
                    else:
                        page_priority = PAGE_PRIORITY_MEDIUM
                else:
                    page_priority = PAGE_PRIORITY_MEDIUM
            else:
                page_priority = PAGE_PRIORITY_LOW
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                page_priority_info = MEMORY_PRIORITY_INFORMATION()
                page_priority_info.MemoryPriority = page_priority
                result = ntdll.NtSetInformationProcess(int(handle), ProcessMemoryPriority, ctypes.byref(page_priority_info), ctypes.sizeof(page_priority_info))
                if result == 0:
                    if page_priority == PAGE_PRIORITY_NORMAL:
                        self.stats['promotions'] += 1
                    else:
                        self.stats['demotions'] += 1
                    return True
            return False
    def detect_sequential_access_pattern(self, pid):
        with self.lock:
            if pid not in self.process_working_sets:
                return False
            ws_data = self.process_working_sets[pid]
            history = list(ws_data['history'])
            if len(history) < 5:
                return False
            sequential = True
            for i in range(1, min(5, len(history))):
                if history[-i] < history[-(i + 1)]:
                    sequential = False
                    break
            if sequential:
                patterns = self.page_access_patterns[pid]
                patterns['sequential_accesses'] += 1
                if patterns['sequential_accesses'] > 3:
                    self.stats['prefetch_hints'] += 1
                    return True
            else:
                patterns = self.page_access_patterns[pid]
                patterns['random_accesses'] += 1
            return False
    def optimize_working_set_size(self, pid, target_mb=None):
        with self.lock:
            if pid not in self.process_working_sets:
                return False
            ws_data = self.process_working_sets[pid]
            if target_mb is None:
                history = list(ws_data['history'])
                if history:
                    avg_ws = sum(history) / len(history)
                    min_ws_mb = avg_ws * 0.8
                    max_ws_mb = avg_ws * 1.5
                else:
                    min_ws_mb = ws_data['current_ws'] * 0.8
                    max_ws_mb = ws_data['current_ws'] * 1.5
            else:
                min_ws_mb = target_mb * 0.8
                max_ws_mb = target_mb * 1.5
            min_ws_bytes = int(min_ws_mb * 1024 * 1024)
            max_ws_bytes = int(max_ws_mb * 1024 * 1024)
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_QUOTA)
            if handle:
                result = kernel32.SetProcessWorkingSetSize(int(handle), ctypes.c_size_t(min_ws_bytes), ctypes.c_size_t(max_ws_bytes))
                if result:
                    self.stats['working_set_optimizations'] += 1
                    return True
            return False
    def get_stats(self):
        with self.lock:
            return {'total_promotions': self.stats['promotions'], 'total_demotions': self.stats['demotions'], 'prefetch_hints': self.stats['prefetch_hints'], 'working_set_optimizations': self.stats['working_set_optimizations'], 'tracked_processes': len(self.process_working_sets), 'estimated_overhead': 0.2}
class RealtimePriorityManager:
    GLITCH_DETECTION_THRESHOLD = 0.001
    GLITCH_COUNT_THRESHOLD = 3
    def __init__(self, handle_cache):
        self.handle_cache = handle_cache
        self.lock = threading.RLock()
        self.monitored_processes = {}
        self.stats = {'adjustments': 0, 'glitches_detected': 0}
    def monitor_realtime_process(self, pid, process_name):
        with self.lock:
            process_name_lower = process_name.lower()
            is_audio = any((x in process_name_lower for x in ['audio', 'sound', 'music', 'spotify', 'discord']))
            is_video = any((x in process_name_lower for x in ['video', 'stream', 'obs', 'zoom', 'teams']))
            is_game = any((x in process_name_lower for x in ['game', 'dx11', 'dx12', 'vulkan']))
            if is_audio or is_video or is_game:
                proc = psutil.Process(pid)
                cpu_times = proc.cpu_times()
                if pid not in self.monitored_processes:
                    self.monitored_processes[pid] = {'last_cpu_time': cpu_times.user + cpu_times.system, 'glitch_count': 0, 'type': 'audio' if is_audio else 'video' if is_video else 'game'}
                else:
                    data = self.monitored_processes[pid]
                    current_cpu_time = cpu_times.user + cpu_times.system
                    cpu_delta = current_cpu_time - data['last_cpu_time']
                    if cpu_delta < self.GLITCH_DETECTION_THRESHOLD and data['type'] in ['audio', 'video']:
                        data['glitch_count'] += 1
                        self.stats['glitches_detected'] += 1
                        if data['glitch_count'] > self.GLITCH_COUNT_THRESHOLD:
                            self._boost_priority(pid)
                    else:
                        data['glitch_count'] = max(0, data['glitch_count'] - 1)
                    data['last_cpu_time'] = current_cpu_time
    def _boost_priority(self, pid):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                win32process.SetPriorityClass(int(handle), PRIORITY_CLASSES['HIGH'])
                self.stats['adjustments'] += 1
                return True
            return False
class SystemTrayManager:
    def __init__(self, manager_instance, temp_monitor):
        self.manager = manager_instance
        self.temp_monitor = temp_monitor
        self.icon = None
        self.temp_icon = None
        self.show_temp_icon = True
        self.game_mode = False
        self.running = False
        self.original_settings = {}
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.is_autostart_enabled = self._check_autostart_status()
        self.gui = None
    def load_icon_from_file(self, icon_path):
        if Image is None:
            return None
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        return None
    def create_icon_image(self, text='OP', size=64, bg_color=(0, 120, 215), text_color=(255, 255, 255)):
        if Image is None:
            return None
        image = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('arial.ttf', int(size * 0.5))
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) / 2
        y = (size - text_height) / 2
        draw.text((x, y), text, fill=text_color, font=font)
        return image
    def create_temp_icon_image(self, temp):
        if Image is None:
            return None
        size = 64
        if temp >= self.temp_monitor.max_temp:
            text_color = (220, 20, 60, 255)
        elif temp >= self.temp_monitor.max_temp - 5:
            text_color = (255, 140, 0, 255)
        else:
            text_color = (0, 128, 0, 255)
        temp_text = f'{int(temp)}°'
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('arial.ttf', int(size * 0.875))
        bbox = draw.textbbox((0, 0), temp_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) / 2
        y = (size - text_height) / 2
        draw.text((x, y), temp_text, fill=text_color, font=font)
        return image
    def update_temp_icon(self):
        if self.temp_icon and self.show_temp_icon:
            temp = self.temp_monitor.get_current_temperature()
            new_image = self.create_temp_icon_image(temp)
            if new_image:
                self.temp_icon.icon = new_image
                self.temp_icon.title = f'CPU: {int(temp)}°C'
    def toggle_temp_display(self, icon, item):
        self.show_temp_icon = not self.show_temp_icon
        if self.show_temp_icon and self.temp_icon is None and pystray:
            self._create_temp_icon()
        elif not self.show_temp_icon and self.temp_icon:
            self.temp_icon.stop()
            self.temp_icon = None
    def toggle_game_mode(self, icon, item):
        self.game_mode = not self.game_mode
        if self.game_mode:
            self._activate_game_mode()
        else:
            self._deactivate_game_mode()
    def _activate_game_mode(self):
        if not self.manager:
            return
        self.manager.cpu_frequency_scaler.set_turbo_mode(enable=True)
        self.manager.cpu_parking_controller.disable_cpu_parking()
        subprocess.run(['powercfg', '/setactive', HIGH_PERFORMANCE_POWER_PLAN_GUID], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
    def _deactivate_game_mode(self):
        if not self.manager:
            return
        services_to_restore = ['WSearch', 'SysMain']
        for service_name in services_to_restore:
            subprocess.run(['net', 'start', service_name], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
    def increase_temp_threshold(self, icon, item):
        self.temp_monitor.increase_max_temp()
    def decrease_temp_threshold(self, icon, item):
        self.temp_monitor.decrease_max_temp()
    def _check_autostart_status(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, 'GEMINAZO')
        winreg.CloseKey(key)
        return True
    def toggle_autostart(self, icon, item):
        if self.is_autostart_enabled:
            self._disable_autostart()
        else:
            self._enable_autostart()
        self.is_autostart_enabled = not self.is_autostart_enabled
    def _enable_autostart(self):
        exe_path = sys.executable
        script_path = os.path.abspath(__file__)
        if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
            startup_command = f'"{exe_path}"'
        else:
            startup_command = f'"{exe_path}" "{script_path}"'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'GEMINAZO', 0, winreg.REG_SZ, startup_command)
        winreg.CloseKey(key)
    def _disable_autostart(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, 'GEMINAZO')
    def exit_application(self, icon, item):
        if self.manager and hasattr(self.manager, 'registry_buffer'):
            self.manager.registry_buffer.flush()
        self._revert_all_settings()
        self.running = False
        if self.temp_icon:
            self.temp_icon.stop()
        icon.stop()
        import sys
        sys.exit(0)
    def _revert_all_settings(self):
        if self.game_mode:
            self._deactivate_game_mode()
        if self.manager:
            self.manager.context_switch_reducer.adjust_quantum_time_slice(increase=False, registry_buffer=self.manager.registry_buffer)
    def open_gui(self, icon, item):
        if not GUI_AVAILABLE or ProcessManagerGUI is None:
            return
        if not self.gui:
            self.gui = self._create_gui_instance()
        if self.gui and hasattr(self.gui, 'show'):
            gui_thread = threading.Thread(target=self.gui.show, daemon=False, name='GemGUIThread')
            gui_thread.start()
    def _create_gui_instance(self):
        if ProcessManagerGUI is None:
            return None
        constructors = ((self.manager, self.temp_monitor, self), (self.manager,), tuple())
        for args in constructors:
            return ProcessManagerGUI(*args)
        return None
    def create_menu(self):
        if pystray is None:
            return None
        menu_items = [pystray.MenuItem('Abrir Administrador de Procesos', self.open_gui, enabled=GUI_AVAILABLE), pystray.Menu.SEPARATOR, pystray.MenuItem('Modo Juego', self.toggle_game_mode, checked=lambda item: self.game_mode), pystray.Menu.SEPARATOR, pystray.MenuItem('Salir', self.exit_application)]
        return pystray.Menu(*menu_items)
    def _create_temp_icon(self):
        if pystray is None or Image is None:
            return
        temp = self.temp_monitor.get_current_temperature()
        icon_image = self.create_temp_icon_image(temp)
        if icon_image:
            self.temp_icon = pystray.Icon('GEMINAZO_Temp', icon_image, f'CPU: {int(temp)}°C')
            def run_temp_icon():
                self.temp_icon.run()
    def run(self):
        if pystray is None or Image is None:
            self.running = True
            while self.running:
                time.sleep(5)
            return
        icon_path = os.path.join(self.script_dir, '1.ico')
        icon_image = self.load_icon_from_file(icon_path)
        if icon_image is None:
            icon_image = self.create_icon_image('OP')
        if icon_image is None:
            self.running = True
            while self.running:
                time.sleep(5)
            return
        self.icon = pystray.Icon('GEMINAZO', icon_image, 'GEMINAZO Optimizer', menu=self.create_menu())
        if self.show_temp_icon:
            self._create_temp_icon()
        self.running = True
        def update_loop():
            while self.running:
                time.sleep(3)
                self.update_temp_icon()
                if self.icon:
                    self.icon.menu = self.create_menu()
def is_user_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())
def find_nsudo_executable() -> Optional[str]:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for candidate in ('NSudo.exe', 'NSudoLG.exe'):
        candidate_path = os.path.join(script_dir, candidate)
        if os.path.isfile(candidate_path):
            return candidate_path
    return None
def attempt_nsudo_elevation() -> bool:
    nsudo_path = find_nsudo_executable()
    if not nsudo_path:
        return False
    script_path = os.path.abspath(__file__)
    argument_parts = ['-P:E', '-UseCurrentConsole', '-Wait', f'"{sys.executable}"', f'"{script_path}"']
    if len(sys.argv) > 1:
        extra = ' '.join((f'"{arg}"' for arg in sys.argv[1:]))
        argument_parts.append(extra)
    arguments = ' '.join(argument_parts)
    shell32 = ctypes.windll.shell32
    result = shell32.ShellExecuteW(None, 'runas', nsudo_path, arguments, os.path.dirname(nsudo_path), 1)
    if result <= 32:
        return False
    return True
def relaunch_with_elevation() -> Optional[str]:
    if is_user_admin():
        return None
    if attempt_nsudo_elevation():
        return 'nsudo'
    shell32 = ctypes.windll.shell32
    script_path = os.path.abspath(__file__)
    arg_list = [script_path] + sys.argv[1:]
    params = ' '.join((f'"{arg}"' for arg in arg_list))
    result = shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
    if result <= 32:
        return None
    return 'runas'
def enable_debug_privilege():
    h_token = None
    h_token = wintypes.HANDLE()
    h_process = kernel32.GetCurrentProcess()
    if not advapi32.OpenProcessToken(h_process, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(h_token)):
        return False
    luid = LUID()
    if not advapi32.LookupPrivilegeValueW(None, SE_DEBUG_NAME, ctypes.byref(luid)):
        return False
    tp = TOKEN_PRIVILEGES()
    tp.PrivilegeCount = 1
    tp.Privileges[0].Luid = luid
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
    kernel32.SetLastError(0)
    result = advapi32.AdjustTokenPrivileges(h_token, False, ctypes.byref(tp), ctypes.sizeof(TOKEN_PRIVILEGES), None, None)
    error = kernel32.GetLastError()
    if result != 0 and error == 0:
        return True
    return False
def set_process_affinity_direct(handle, core_list):
    if not handle or not core_list:
        return False
    max_cores = psutil.cpu_count(logical=True)
    if any((core < 0 or core >= max_cores for core in core_list)):
        return False
    affinity_mask = sum((1 << core for core in core_list))
    result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
    if result != 0:
        return True
    else:
        error_code = kernel32.GetLastError()
        return False
def get_process_affinity_direct(handle):
    if not handle:
        return None
    process_mask = ULONG_PTR()
    system_mask = ULONG_PTR()
    if kernel32.GetProcessAffinityMask(handle, ctypes.byref(process_mask), ctypes.byref(system_mask)):
        cores = []
        mask = process_mask.value
        core_idx = 0
        max_cores = psutil.cpu_count(logical=True)
        while mask and core_idx < max_cores:
            if mask & 1:
                cores.append(core_idx)
            mask >>= 1
            core_idx += 1
        return cores if cores else None
    error_code = kernel32.GetLastError()
    return None
def set_page_priority_for_pid(pid, page_priority):
    h_process = None
    if not isinstance(pid, int) or pid <= 0:
        return False
    if not isinstance(page_priority, int) or not 1 <= page_priority <= 5:
        return False
    h_process = kernel32.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, pid)
    if not h_process:
        error_code = kernel32.GetLastError()
        return False
    priority_value = ctypes.c_ulong(page_priority)
    result = NtSetInformationProcess(h_process, ProcessPagePriority, ctypes.byref(priority_value), ctypes.sizeof(priority_value))
    if result == 0:
        return True
    else:
        return False
def set_priority_boost(pid, disable_boost):
    h_process = None
    if not isinstance(pid, int) or pid <= 0:
        return False
    if not isinstance(disable_boost, bool):
        return False
    h_process = win32api.OpenProcess(win32con.PROCESS_SET_INFORMATION | win32con.PROCESS_QUERY_INFORMATION, False, pid)
    if not h_process:
        return False
    result = kernel32.SetProcessPriorityBoost(int(h_process), wintypes.BOOL(disable_boost))
    if result:
        return True
    else:
        return False
def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    if not os.path.exists(config_path):
        return {'whitelist': [], 'lista_juegos': [], 'lista_blanca': []}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
class L3CacheOptimizer:
    def __init__(self, topology):
        self.lock = threading.RLock()
        self.topology = topology
        self.cache_groups = self._detect_l3_cache_groups()
        self.process_assignments = {}
        self.stats = {'optimizations': 0, 'cache_hits': 0}
    def _detect_l3_cache_groups(self):
        cache_groups = defaultdict(set)
        returned_length = wintypes.DWORD(0)
        kernel32.GetLogicalProcessorInformation(None, ctypes.byref(returned_length))
        if returned_length.value > 0:
            buf = (ctypes.c_byte * returned_length.value)()
            if not kernel32.GetLogicalProcessorInformation(ctypes.byref(buf), ctypes.byref(returned_length)):
                return cache_groups
            entry_size = ctypes.sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
            entry_count = returned_length.value // entry_size
            for i in range(entry_count):
                offset = i * entry_size
                entry = SYSTEM_LOGICAL_PROCESSOR_INFORMATION.from_buffer_copy(buf[offset:offset + entry_size])
                if entry.Relationship == RelationCache:
                    cache_desc = entry.u.Cache
                    if cache_desc.Level == 3:
                        mask = entry.ProcessorMask
                        cores = []
                        core_idx = 0
                        while mask:
                            if mask & 1:
                                cores.append(core_idx)
                            mask >>= 1
                            core_idx += 1
                        cache_id = i
                        cache_groups[cache_id].update(cores)
        return cache_groups
    def optimize_process_cache_locality(self, pid, is_critical=False, handle_cache=None):
        with self.lock:
            if not self.cache_groups:
                return False
            if is_critical and handle_cache:
                best_cache_group = None
                min_processes = float('inf')
                for cache_id, cores in self.cache_groups.items():
                    process_count = sum((1 for p_cores in self.process_assignments.values() if any((c in cores for c in p_cores))))
                    if process_count < min_processes:
                        min_processes = process_count
                        best_cache_group = cores
                if best_cache_group:
                    handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
                    if handle:
                        affinity_mask = sum((1 << core for core in best_cache_group))
                        result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                        if result:
                            self.process_assignments[pid] = list(best_cache_group)
                            self.stats['optimizations'] += 1
                            return True
            return False
    def detect_cache_contention(self, pid_list):
        with self.lock:
            for cache_id, cores in self.cache_groups.items():
                processes_in_group = [pid for pid, assigned_cores in self.process_assignments.items() if pid in pid_list and any((c in cores for c in assigned_cores))]
                if len(processes_in_group) > len(cores) / 2:
                    return (True, cache_id, processes_in_group)
            return (False, None, [])
class EnhancedCacheTopologyOptimizer:
    def __init__(self, topology):
        self.lock = threading.RLock()
        self.topology = topology
        self.l2_cache_groups = self._detect_l2_cache_groups()
        self.l3_cache_groups = self._detect_l3_cache_groups()
        self.process_cache_assignments = {}
        self.cache_contention_scores = defaultdict(float)
        self.last_rebalance = time.time()
        self.stats = {'optimizations': 0, 'rebalances': 0, 'cache_hits': 0, 'contention_detected': 0}
    def _detect_l2_cache_groups(self):
        cache_groups = defaultdict(set)
        returned_length = wintypes.DWORD(0)
        kernel32.GetLogicalProcessorInformation(None, ctypes.byref(returned_length))
        if returned_length.value > 0:
            buf = (ctypes.c_byte * returned_length.value)()
            if not kernel32.GetLogicalProcessorInformation(ctypes.byref(buf), ctypes.byref(returned_length)):
                return cache_groups
            entry_size = ctypes.sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
            entry_count = returned_length.value // entry_size
            for i in range(entry_count):
                offset = i * entry_size
                entry = SYSTEM_LOGICAL_PROCESSOR_INFORMATION.from_buffer_copy(buf[offset:offset + entry_size])
                if entry.Relationship == RelationCache:
                    cache_desc = entry.u.Cache
                    if cache_desc.Level == 2:
                        mask = entry.ProcessorMask
                        cores = self._mask_to_cores(mask)
                        cache_id = f'L2_{i}'
                        cache_groups[cache_id].update(cores)
        return cache_groups
    def _detect_l3_cache_groups(self):
        cache_groups = defaultdict(set)
        returned_length = wintypes.DWORD(0)
        kernel32.GetLogicalProcessorInformation(None, ctypes.byref(returned_length))
        if returned_length.value > 0:
            buf = (ctypes.c_byte * returned_length.value)()
            if not kernel32.GetLogicalProcessorInformation(ctypes.byref(buf), ctypes.byref(returned_length)):
                return cache_groups
            entry_size = ctypes.sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
            entry_count = returned_length.value // entry_size
            for i in range(entry_count):
                offset = i * entry_size
                entry = SYSTEM_LOGICAL_PROCESSOR_INFORMATION.from_buffer_copy(buf[offset:offset + entry_size])
                if entry.Relationship == RelationCache:
                    cache_desc = entry.u.Cache
                    if cache_desc.Level == 3:
                        mask = entry.ProcessorMask
                        cores = self._mask_to_cores(mask)
                        cache_id = f'L3_{i}'
                        cache_groups[cache_id].update(cores)
        return cache_groups
    def _mask_to_cores(self, mask):
        cores = []
        core_idx = 0
        while mask:
            if mask & 1:
                cores.append(core_idx)
            mask >>= 1
            core_idx += 1
        return cores
    def assign_process_to_cache_group(self, pid, process_name, related_pids=None, handle_cache=None):
        with self.lock:
            if not self.l3_cache_groups and (not self.l2_cache_groups):
                return False
            target_cache_group = None
            if related_pids:
                for cache_id, cores in self.l3_cache_groups.items():
                    related_count = sum((1 for rel_pid in related_pids if self.process_cache_assignments.get(rel_pid, {}).get('cache_group') == cache_id))
                    if related_count > 0:
                        target_cache_group = cache_id
                        break
            if not target_cache_group:
                min_contention = float('inf')
                for cache_id in self.l3_cache_groups.keys():
                    contention = self.cache_contention_scores.get(cache_id, 0)
                    if contention < min_contention:
                        min_contention = contention
                        target_cache_group = cache_id
            if target_cache_group and handle_cache:
                cores = self.l3_cache_groups[target_cache_group]
                handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
                if handle:
                    affinity_mask = sum((1 << core for core in cores))
                    result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                    if result:
                        self.process_cache_assignments[pid] = {'cache_group': target_cache_group, 'cores': list(cores), 'assigned_at': time.time()}
                        self.stats['optimizations'] += 1
                        return True
            return False
    def detect_and_rebalance_contention(self, active_pids, handle_cache=None):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_rebalance < 30:
                return False
            self.last_rebalance = current_time
            for cache_id, cores in self.l3_cache_groups.items():
                processes_in_group = [pid for pid in active_pids if self.process_cache_assignments.get(pid, {}).get('cache_group') == cache_id]
                contention = len(processes_in_group) / max(len(cores), 1)
                self.cache_contention_scores[cache_id] = contention
                if contention > 2.0:
                    self.stats['contention_detected'] += 1
            high_contention_groups = [cache_id for cache_id, score in self.cache_contention_scores.items() if score > 2.0]
            if high_contention_groups and handle_cache:
                self._rebalance_processes(active_pids, high_contention_groups, handle_cache)
                return True
            return False
    def _rebalance_processes(self, active_pids, high_contention_groups, handle_cache):
        low_contention_groups = [cache_id for cache_id, score in self.cache_contention_scores.items() if score < 1.0 and cache_id not in high_contention_groups]
        if not low_contention_groups:
            return
        for high_cache_id in high_contention_groups:
            processes_to_move = [pid for pid in active_pids if self.process_cache_assignments.get(pid, {}).get('cache_group') == high_cache_id]
            move_count = min(len(processes_to_move) // 2, len(low_contention_groups))
            for i, pid in enumerate(processes_to_move[:move_count]):
                target_cache_id = low_contention_groups[i % len(low_contention_groups)]
                cores = self.l3_cache_groups[target_cache_id]
                handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
                if handle:
                    affinity_mask = sum((1 << core for core in cores))
                    result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                    if result:
                        self.process_cache_assignments[pid] = {'cache_group': target_cache_id, 'cores': list(cores), 'assigned_at': time.time()}
                        self.stats['rebalances'] += 1
    def get_stats(self):
        with self.lock:
            return {'l2_groups': len(self.l2_cache_groups), 'l3_groups': len(self.l3_cache_groups), 'total_optimizations': self.stats['optimizations'], 'total_rebalances': self.stats['rebalances'], 'contention_events': self.stats['contention_detected'], 'assigned_processes': len(self.process_cache_assignments)}
class AVXInstructionOptimizer:
    def __init__(self, handle_cache, cpu_count):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.cpu_count = cpu_count
        self.avx_processes = {}
        self.avx_capable_cores = self._detect_avx_cores()
        self.stats = {'avx_detected': 0, 'optimizations': 0}
    def _detect_avx_cores(self):
        import platform
        result = subprocess.run(
            ['powershell', '-Command', 
             '(Get-WmiObject Win32_Processor).Description; ' +
             '(gwmi Win32_Processor).Name'],
            capture_output=True, 
            creationflags=subprocess.CREATE_NO_WINDOW, 
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            output = result.stdout.lower()
            has_avx = any([
                'intel' in output and any(x in output for x in ['core i', 'xeon', 'core(tm) i']),
                'amd' in output and any(x in output for x in ['ryzen', 'threadripper', 'epyc']),
            ])
            if has_avx:
                return list(range(self.cpu_count))
            else:
                return list(range(self.cpu_count))
        return list(range(self.cpu_count))
    def detect_avx_usage(self, pid, process_name):
        with self.lock:
            process_lower = process_name.lower()
            avx_indicators = ['render', 'encode', 'decode', 'video', 'blender', 'maya', 'handbrake', 'ffmpeg', 'premiere', 'davinci', 'x264', 'x265', 'scientific', 'matlab', 'mathematica', 'numpy']
            is_avx_process = any((indicator in process_lower for indicator in avx_indicators))
            if is_avx_process:
                self.avx_processes[pid] = {'name': process_name, 'detected_at': time.time(), 'optimized': False}
                self.stats['avx_detected'] += 1
                return True
            return False
    def optimize_avx_process(self, pid):
        with self.lock:
            if pid not in self.avx_processes or self.avx_processes[pid]['optimized']:
                return False
            if self.avx_capable_cores:
                handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
                if handle:
                    cores_to_use = max(len(self.avx_capable_cores) // 2, min(4, len(self.avx_capable_cores)))
                    affinity_mask = sum((1 << core for core in self.avx_capable_cores[:cores_to_use]))
                    result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                    if result:
                        self.avx_processes[pid]['optimized'] = True
                        self.stats['optimizations'] += 1
                        win32process.SetPriorityClass(handle, win32process.ABOVE_NORMAL_PRIORITY_CLASS)
            return False
class EnhancedSMTOptimizer:
    def __init__(self, topology, cpu_count):
        self.lock = threading.RLock()
        self.topology = topology
        self.cpu_count = cpu_count
        self.physical_cores = self._detect_physical_cores()
        self.smt_pairs = self._detect_smt_pairs()
        self.process_smt_config = {}
        self.stats = {'smt_disabled': 0, 'smt_enabled': 0}
    def _detect_physical_cores(self):
        return list(range(psutil.cpu_count(logical=False)))
    def _detect_smt_pairs(self):
        pairs = {}
        logical_count = psutil.cpu_count(logical=True)
        physical_count = psutil.cpu_count(logical=False)
        if logical_count == physical_count * 2:
            for i in range(physical_count):
                pairs[i] = [i, i + physical_count]
        return pairs
    def optimize_for_latency(self, pid, handle_cache):
        with self.lock:
            if not self.physical_cores:
                return False
            handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if handle:
                affinity_mask = sum((1 << core for core in self.physical_cores))
                result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                if result:
                    self.process_smt_config[pid] = 'latency'
                    self.stats['smt_disabled'] += 1
                    return True
            return False
    def optimize_for_throughput(self, pid, handle_cache):
        with self.lock:
            handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if handle:
                affinity_mask = (1 << self.cpu_count) - 1
                result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                if result:
                    self.process_smt_config[pid] = 'throughput'
                    self.stats['smt_enabled'] += 1
                    return True
            return False
class CPUPipelineOptimizer:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.stats = {'optimizations': 0}
    def optimize_instruction_ordering(self, pid, is_critical=False):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if not handle:
                return False
            if is_critical:
                kernel32.SetProcessPriorityBoost(handle, wintypes.BOOL(False))
                win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
            return False
class TSCSynchronizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.tsc_synced = False
        self.stats = {'sync_attempts': 0, 'sync_success': 0}
    def synchronize_tsc(self):
        with self.lock:
            self.stats['sync_attempts'] += 1
            result = subprocess.run(['powershell', '-Command', '(Get-WmiObject Win32_Processor).Caption'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            if result.returncode == 0:
                self.tsc_synced = True
                self.stats['sync_success'] += 1
                return True
            return False
class TLBOptimizer:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.large_page_processes = set()
        self.stats = {'large_pages_enabled': 0, 'optimizations': 0}
    def enable_large_pages(self, pid):
        with self.lock:
            if pid in self.large_page_processes:
                return True
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION)
            if handle:
                min_ws = 1024 * 1024 * 1024
                max_ws = 4 * 1024 * 1024 * 1024
                flags = QUOTA_LIMITS_HARDWS_MIN_ENABLE | QUOTA_LIMITS_HARDWS_MAX_ENABLE
                result = kernel32.SetProcessWorkingSetSizeEx(handle, min_ws, max_ws, flags)
                if result:
                    self.large_page_processes.add(pid)
                    self.stats['large_pages_enabled'] += 1
                    self.stats['optimizations'] += 1
                    return True
            return False
    def optimize_memory_layout(self, pid):
        with self.lock:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            if mem_info.rss > 512 * 1024 * 1024:
                return self.enable_large_pages(pid)
            return False
class AdvancedNUMAOptimizer:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.numa_nodes = self._detect_numa_topology()
        self.process_numa_assignments = {}
        self.stats = {'migrations': 0, 'optimizations': 0}
    def _detect_numa_topology(self):
        nodes = defaultdict(list)
        for cpu in range(psutil.cpu_count(logical=True)):
            node_number = ctypes.c_ubyte()
            if kernel32.GetNumaProcessorNode(cpu, ctypes.byref(node_number)):
                nodes[node_number.value].append(cpu)
        return nodes.copy()
    def optimize_numa_placement(self, pid):
        with self.lock:
            if len(self.numa_nodes) <= 1:
                return False
            best_node = min(self.numa_nodes.keys(), key=lambda n: len([p for p in self.process_numa_assignments.values() if p == n]))
            node_cores = self.numa_nodes[best_node]
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if handle:
                affinity_mask = sum((1 << core for core in node_cores))
                result = kernel32.SetProcessAffinityMask(handle, ULONG_PTR(affinity_mask))
                if result:
                    self.process_numa_assignments[pid] = best_node
                    self.stats['optimizations'] += 1
                    return True
            return False
    def migrate_memory_between_nodes(self, pid, target_node):
        with self.lock:
            if target_node not in self.numa_nodes:
                return False
            if pid in self.process_numa_assignments and self.process_numa_assignments[pid] != target_node:
                if self.optimize_numa_placement(pid):
                    self.stats['migrations'] += 1
                    return True
            return False
class MemoryScrubbingOptimizer:
    IDLE_CPU_THRESHOLD = 20
    SCRUB_INTERVAL = 3600
    def __init__(self):
        self.lock = threading.RLock()
        self.enabled = False
        self.scrubbing_scheduled = False
        self.last_scrub_time = 0
        self.scrubbing_interval = 60
        self.scrubbing_thread = None
        self.memory_regions = []
        self.stats = {'scrubbing_optimizations': 0, 'regions_scrubbed': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
            self._initialize_memory_regions()
    def disable(self):
        with self.lock:
            self.enabled = False
    def _initialize_memory_regions(self):
        mem = psutil.virtual_memory()
        self.memory_regions = self._partition_memory(mem.total)
    def _partition_memory(self, total_memory):
        regions = []
        region_size = 1024 * 1024 * 1024
        num_regions = max(1, total_memory // region_size)
        for i in range(min(num_regions, 16)):
            regions.append({'id': i, 'size': region_size, 'last_scrub': 0})
        return regions
    def set_scrubbing_interval(self, interval_seconds):
        with self.lock:
            self.scrubbing_interval = interval_seconds
    def start_background_scrubbing(self):
        with self.lock:
            if not self.enabled or self.scrubbing_thread is not None:
                return
            def scrub_memory():
                while self.enabled:
                    for region in self.memory_regions:
                        if not self.enabled:
                            break
                        self._scrub_region(region)
                    time.sleep(self.scrubbing_interval)
            self.scrubbing_thread = threading.Thread(target=scrub_memory, daemon=True, name='MemoryScrubber')
            self.scrubbing_thread.start()
    def stop_background_scrubbing(self):
        with self.lock:
            self.enabled = False
            self.scrubbing_thread = None
    def _scrub_region(self, region):
        current_time = time.time()
        if current_time - region.get('last_scrub', 0) >= self.scrubbing_interval:
            gc.collect(generation=2)
            region['last_scrub'] = current_time
            self.stats['regions_scrubbed'] += 1
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'scrubbing_optimizations': self.stats.get('scrubbing_optimizations', 0),
                'regions_scrubbed': self.stats.get('regions_scrubbed', 0),
                'memory_regions': len(self.memory_regions)
            }
    def schedule_scrubbing_low_load(self):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_scrub_time < self.SCRUB_INTERVAL:
                return False
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < self.IDLE_CPU_THRESHOLD:
                subprocess.run(['mdsched.exe'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=2)
                self.scrubbing_scheduled = True
                self.last_scrub_time = current_time
                self.stats['scrubbing_optimizations'] += 1
                return True
            return False
class CacheCoherencyOptimizer:
    CACHE_LINE_SIZE = 64
    FALSE_SHARING_THRESHOLD = 10 * 1024 * 1024
    DETECTION_COUNT_THRESHOLD = 5
    def __init__(self):
        self.lock = threading.RLock()
        self.enabled = False
        self.cache_line_size = self.CACHE_LINE_SIZE
        self.coherency_protocol = None
        self.cache_lines = {}
        self.process_memory_patterns = {}
        self.stats = {'optimizations': 0, 'false_sharing_detected': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
    def disable(self):
        with self.lock:
            self.enabled = False
    def set_coherency_protocol(self, protocol):
        with self.lock:
            self.coherency_protocol = protocol
    def initialize_cache_lines(self):
        with self.lock:
            if self.coherency_protocol == "MESI":
                self._init_mesi_protocol()
            elif self.coherency_protocol == "MOESI":
                self._init_moesi_protocol()
    def _init_mesi_protocol(self):
        self.cache_lines = {
            'modified': [],
            'exclusive': [],
            'shared': [],
            'invalid': []
        }
    def _init_moesi_protocol(self):
        self.cache_lines = {
            'modified': [],
            'owned': [],
            'exclusive': [],
            'shared': [],
            'invalid': []
        }
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'protocol': self.coherency_protocol,
                'optimizations': self.stats.get('optimizations', 0),
                'false_sharing_detected': self.stats.get('false_sharing_detected', 0)
            }
    def detect_false_sharing(self, pid):
        with self.lock:
            proc = psutil.Process(pid)
            num_threads = proc.num_threads()
            if num_threads > 4:
                mem_info = proc.memory_info()
                if pid not in self.process_memory_patterns:
                    self.process_memory_patterns[pid] = {'last_rss': mem_info.rss, 'access_count': 0, 'timestamp': time.time()}
                    return False
                pattern = self.process_memory_patterns[pid]
                rss_delta = abs(mem_info.rss - pattern['last_rss'])
                time_delta = time.time() - pattern['timestamp']
                if time_delta > 0:
                    access_rate = rss_delta / time_delta
                    if access_rate > self.FALSE_SHARING_THRESHOLD:
                        pattern['access_count'] += 1
                        if pattern['access_count'] > self.DETECTION_COUNT_THRESHOLD:
                            pattern['last_rss'] = mem_info.rss
                            pattern['timestamp'] = time.time()
                            self.stats['false_sharing_detected'] += 1
                            return True
                pattern['last_rss'] = mem_info.rss
                pattern['timestamp'] = time.time()
            return False
    def optimize_thread_placement(self, pid, handle_cache):
        with self.lock:
            if self.detect_false_sharing(pid):
                handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
                if handle:
                    kernel32.SetProcessPriorityBoost(handle, wintypes.BOOL(False))
                    proc = psutil.Process(pid)
                    threads = proc.threads()
                    physical_cores = psutil.cpu_count(logical=False)
                    snapshot_handle = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
                    if snapshot_handle != -1:
                        te32 = THREADENTRY32()
                        te32.dwSize = ctypes.sizeof(THREADENTRY32)
                        if kernel32.Thread32First(snapshot_handle, ctypes.byref(te32)):
                            thread_index = 0
                            while True:
                                if te32.th32OwnerProcessID == pid:
                                    core = thread_index % physical_cores
                                    affinity_mask = 1 << core
                                    thread_handle = kernel32.OpenThread(
                                        THREAD_SET_INFORMATION | THREAD_QUERY_INFORMATION,
                                        False,
                                        te32.th32ThreadID
                                    )
                                    if thread_handle:
                                        kernel32.SetThreadAffinityMask(thread_handle, ULONG_PTR(affinity_mask))
                                        kernel32.CloseHandle(thread_handle)
                                    thread_index += 1
                                if not kernel32.Thread32Next(snapshot_handle, ctypes.byref(te32)):
                                    break
                        kernel32.CloseHandle(snapshot_handle)
            return False
class MemoryBandwidthManager:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.enabled = False
        self.handle_cache = handle_cache
        self.foreground_processes = set()
        self.background_processes = set()
        self.bandwidth_limit = 100
        self.qos_policies = {}
        self.current_usage = 0
        self.monitoring_thread = None
        self.stats = {'priority_adjustments': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
            self._start_bandwidth_monitoring()
    def disable(self):
        with self.lock:
            self.enabled = False
            self.monitoring_thread = None
    def set_bandwidth_limit(self, limit_percent):
        with self.lock:
            self.bandwidth_limit = min(100, max(0, limit_percent))
    def configure_qos_policies(self):
        with self.lock:
            self.qos_policies = {
                'high_priority': {'limit': 50, 'guaranteed': 30},
                'normal_priority': {'limit': 30, 'guaranteed': 15},
                'low_priority': {'limit': 20, 'guaranteed': 5}
            }
    def _start_bandwidth_monitoring(self):
        if self.monitoring_thread is not None:
            return
        def monitor_bandwidth():
            last_read = 0
            last_write = 0
            last_time = time.time()
            while self.enabled:
                current_time = time.time()
                time_delta = current_time - last_time
                if time_delta > 0:
                    total_read = 0
                    total_write = 0
                    for proc in psutil.process_iter(['io_counters']):
                        io = proc.info.get('io_counters')
                        if io:
                            total_read += io.read_bytes
                            total_write += io.write_bytes
        self.monitoring_thread = threading.Thread(target=monitor_bandwidth, daemon=True, name='BandwidthMonitor')
        self.monitoring_thread.start()
    def get_current_usage(self):
        with self.lock:
            return self.current_usage
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'bandwidth_limit': self.bandwidth_limit,
                'current_usage': self.current_usage,
                'priority_adjustments': self.stats.get('priority_adjustments', 0),
                'foreground_processes': len(self.foreground_processes),
                'background_processes': len(self.background_processes)
            }
    def prioritize_foreground_memory_access(self, pid):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if handle:
                mem_priority = MEMORY_PRIORITY_INFORMATION()
                mem_priority.MemoryPriority = MEMORY_PRIORITY_NORMAL
                result = NtSetInformationProcess(handle, ProcessMemoryPriority, ctypes.byref(mem_priority), ctypes.sizeof(mem_priority))
                if result == 0:
                    self.foreground_processes.add(pid)
                    self.background_processes.discard(pid)
                    self.stats['priority_adjustments'] += 1
                    return True
            return False
    def limit_background_bandwidth(self, pid):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
            if handle:
                mem_priority = MEMORY_PRIORITY_INFORMATION()
                mem_priority.MemoryPriority = MEMORY_PRIORITY_LOW
                result = NtSetInformationProcess(handle, ProcessMemoryPriority, ctypes.byref(mem_priority), ctypes.sizeof(mem_priority))
                if result == 0:
                    self.background_processes.add(pid)
                    self.foreground_processes.discard(pid)
                    self.stats['priority_adjustments'] += 1
                    return True
            return False
class IntelligentTRIMScheduler:
    def __init__(self):
        self.lock = threading.RLock()
        self.last_trim = 0
        self.trim_interval = 3600
        self.gaming_mode = False
        self.system_idle = False
    def should_execute_trim(self):
        with self.lock:
            if self.gaming_mode:
                return False
            current_time = time.time()
            if current_time - self.last_trim < self.trim_interval:
                return False
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 10:
                self.system_idle = True
                return True
            return False
    def execute_trim(self):
        if self.should_execute_trim():
            import string
            from ctypes import windll
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drive_path = f'{letter}:\\'
                    drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                    if drive_type == 3:
                        drives.append(f'{letter}:')
                bitmask >>= 1
            for drive in drives:
                subprocess.run(
                    ['defrag', '/L', drive],
                    capture_output=True,
                    timeout=300,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
    def set_gaming_mode(self, enabled):
        with self.lock:
            self.gaming_mode = enabled
class AggressiveWriteCache:
    def __init__(self):
        self.lock = threading.RLock()
        self.enabled = False
        self.cache_size = 0
        self.write_policy = None
        self.cache_data = {}
        self.flush_daemon = None
        self.write_buffer_size = 512 * 1024 * 1024
        self.stats = {'cache_hits': 0, 'cache_misses': 0, 'flushes': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
    def disable(self):
        with self.lock:
            self.enabled = False
    def set_cache_size(self, size_bytes):
        with self.lock:
            self.cache_size = size_bytes
            self.write_buffer_size = size_bytes
    def set_write_policy(self, policy):
        with self.lock:
            if policy in ['write-back', 'write-through']:
                self.write_policy = policy
    def start_cache_flush_daemon(self):
        with self.lock:
            if not self.enabled or self.flush_daemon is not None:
                return
            def flush_periodically():
                while self.enabled:
                    self._flush_dirty_pages()
                    time.sleep(5)
            self.flush_daemon = threading.Thread(target=flush_periodically, daemon=True, name='CacheFlusher')
            self.flush_daemon.start()
    def flush_and_disable(self):
        with self.lock:
            self._flush_dirty_pages()
            self.enabled = False
            self.flush_daemon = None
    def _flush_dirty_pages(self):
        if self.cache_data:
            self.cache_data.clear()
            self.stats['flushes'] += 1
    def get_hit_ratio(self):
        with self.lock:
            total = self.stats.get('cache_hits', 0) + self.stats.get('cache_misses', 0)
            if total == 0:
                return 0.0
            return self.stats.get('cache_hits', 0) / total
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'cache_size': self.cache_size,
                'write_policy': self.write_policy,
                'hit_ratio': self.get_hit_ratio(),
                'flushes': self.stats.get('flushes', 0)
            }
    def optimize_write_cache_for_gaming(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'IoPageLockLimit', 0, winreg.REG_DWORD, self.write_buffer_size)
        winreg.CloseKey(key)
class CustomIOScheduler:
    def __init__(self):
        self.lock = threading.RLock()
        self.enabled = False
        self.scheduling_algorithm = None
        self.queue_depth = 128
        self.io_queue = []
        self.scheduler_thread = None
        self.read_priority = 2
        self.write_priority = 1
        self.stats = {'io_requests': 0, 'io_processed': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
    def disable(self):
        with self.lock:
            self.enabled = False
    def set_scheduling_algorithm(self, algorithm):
        with self.lock:
            if algorithm in ['deadline', 'cfq', 'noop', 'bfq']:
                self.scheduling_algorithm = algorithm
    def set_queue_depth(self, depth):
        with self.lock:
            self.queue_depth = max(1, min(depth, 1024))
    def start_scheduling(self):
        with self.lock:
            if not self.enabled or self.scheduler_thread is not None:
                return
            def schedule_io():
                while self.enabled:
                    if self.io_queue:
                        request = self.io_queue.pop(0)
                        self._process_io_request(request)
                    time.sleep(0.001)
            self.scheduler_thread = threading.Thread(target=schedule_io, daemon=True, name='IOScheduler')
            self.scheduler_thread.start()
    def stop_scheduling(self):
        with self.lock:
            self.enabled = False
            self.scheduler_thread = None
    def add_syscall(self, syscall_func, args):
        with self.lock:
            self.io_queue.append((syscall_func, args))
            self.stats['io_requests'] += 1
    def _process_io_request(self, request):
        request_type = request.get('type', 'unknown')
        priority = request.get('priority', 1)
        if self.scheduling_algorithm == 'deadline':
            deadline = request.get('deadline', time.time() + 1.0)
        elif self.scheduling_algorithm == 'cfq':
            process_id = request.get('pid', 0)
        elif self.scheduling_algorithm == 'bfq':
            bandwidth = request.get('bandwidth', 1)
        self.stats['io_processed'] += 1
    def get_queue_status(self):
        with self.lock:
            return {
                'queue_length': len(self.io_queue),
                'queue_depth': self.queue_depth
            }
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'algorithm': self.scheduling_algorithm,
                'queue_depth': self.queue_depth,
                'io_requests': self.stats.get('io_requests', 0),
                'io_processed': self.stats.get('io_processed', 0)
            }
    def prioritize_reads_for_gaming(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Services\\Disk'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'TimeOutValue', 0, winreg.REG_DWORD, 10)
        winreg.CloseKey(key)
class NCQOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.queue_depth_gaming = 32
        self.queue_depth_transfer = 256
        self.current_mode = 'normal'
    def set_queue_depth_for_gaming(self, gaming_mode):
        with self.lock:
            depth = self.queue_depth_gaming if gaming_mode else self.queue_depth_transfer
            self.current_mode = 'gaming' if gaming_mode else 'transfer'
            key_path = 'SYSTEM\\CurrentControlSet\\Services\\storahci\\Parameters\\Device'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'QueueDepth', 0, winreg.REG_DWORD, depth)
            winreg.CloseKey(key)
class AdvancedFileSystemCache:
    def __init__(self):
        self.lock = threading.RLock()
    def optimize_cache_for_gaming(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'DisablePagingExecutive', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'LargeSystemCache', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
class IOPriorityInheritance:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.enabled = False
        self.handle_cache = handle_cache
        self.io_priorities = {}
        self.priority_levels = 3
        self.priority_boosting = False
        self.inheritance_chain = []
        self.stats = {'inversions': 0, 'boosts': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
    def disable(self):
        with self.lock:
            self.enabled = False
    def set_priority_levels(self, levels):
        with self.lock:
            self.priority_levels = max(3, min(levels, 10))
    def enable_priority_boosting(self):
        with self.lock:
            self.priority_boosting = True
    def configure_inheritance_chain(self):
        with self.lock:
            self.inheritance_chain = self._build_inheritance_tree()
    def _build_inheritance_tree(self):
        tree = []
        for level in range(self.priority_levels):
            tree.append({
                'level': level,
                'processes': [],
                'parent_level': max(0, level - 1)
            })
        return tree
    def get_inversion_count(self):
        with self.lock:
            return self.stats.get('inversions', 0)
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'priority_levels': self.priority_levels,
                'priority_boosting': self.priority_boosting,
                'inversions': self.stats.get('inversions', 0),
                'boosts': self.stats.get('boosts', 0)
            }
    def inherit_io_priority(self, pid, priority):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                self.io_priorities[pid] = priority
                return True
            return False
    def throttle_background_io(self, pid):
        with self.lock:
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                throttle = PROCESS_POWER_THROTTLING_STATE()
                throttle.Version = 1
                throttle.ControlMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
                throttle.StateMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
                NtSetInformationProcess(handle, ProcessPowerThrottling, ctypes.byref(throttle), ctypes.sizeof(throttle))
                return True
            return False
class AdaptiveIOScheduler:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.process_io_patterns = defaultdict(lambda: {'sequential_reads': 0, 'random_reads': 0, 'sequential_writes': 0, 'random_writes': 0, 'total_operations': 0, 'last_pattern': None, 'last_update': time.time()})
        self.nvme_queue_depth = 256
        self.io_priorities = {}
        self.last_adjustment = time.time()
        self.stats = {'pattern_detections': 0, 'queue_adjustments': 0, 'priority_changes': 0, 'coalescing_events': 0}
    def detect_io_pattern(self, pid):
        with self.lock:
            proc = psutil.Process(pid)
            io_counters = proc.io_counters()
            pattern_data = self.process_io_patterns[pid]
            current_time = time.time()
            if pattern_data['total_operations'] > 0:
                time_delta = current_time - pattern_data['last_update']
                if time_delta > 0:
                    read_rate = io_counters.read_count / max(time_delta, 1)
                    write_rate = io_counters.write_count / max(time_delta, 1)
                    if read_rate > write_rate * 2:
                        if read_rate > 1000:
                            pattern = 'sequential_read'
                            pattern_data['sequential_reads'] += 1
                        else:
                            pattern = 'random_read'
                            pattern_data['random_reads'] += 1
                    elif write_rate > read_rate * 2:
                        if write_rate > 1000:
                            pattern = 'sequential_write'
                            pattern_data['sequential_writes'] += 1
                        else:
                            pattern = 'random_write'
                            pattern_data['random_writes'] += 1
                    else:
                        pattern = pattern_data['last_pattern']
                    pattern_data['last_pattern'] = pattern
                    pattern_data['total_operations'] += 1
                    pattern_data['last_update'] = current_time
                    self.stats['pattern_detections'] += 1
                    return pattern
            else:
                pattern_data['total_operations'] = 1
                pattern_data['last_update'] = current_time
            return None
    def adjust_nvme_queue_depth(self, system_load):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_adjustment < 30:
                return False
            self.last_adjustment = current_time
            total_io_ops = sum((data['total_operations'] for data in self.process_io_patterns.values()))
            if system_load < 0.3:
                new_queue_depth = 32
            elif system_load < 0.6:
                new_queue_depth = 128
            elif system_load < 0.8:
                new_queue_depth = 512
            else:
                new_queue_depth = 1024
            if total_io_ops > 10000:
                new_queue_depth = min(new_queue_depth * 2, NVME_MAX_QUEUE_DEPTH)
            if new_queue_depth != self.nvme_queue_depth:
                self.nvme_queue_depth = new_queue_depth
                self.stats['queue_adjustments'] += 1
                key_path = 'SYSTEM\\CurrentControlSet\\Services\\stornvme\\Parameters\\Device'
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'QueueDepth', 0, winreg.REG_DWORD, new_queue_depth)
                winreg.CloseKey(key)
            return False
    def prioritize_io(self, pid, is_interactive=False, is_foreground=False):
        with self.lock:
            if is_foreground:
                io_priority = 2
            elif is_interactive:
                io_priority = 1
            else:
                io_priority = 0
            handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                proc = psutil.Process(pid)
                for thread in proc.threads():
                    thread_handle = kernel32.OpenThread(THREAD_SET_INFORMATION, False, thread.id)
                    if thread_handle:
                        ntdll.NtSetInformationThread(thread_handle, ThreadIoPriority, ctypes.byref(ctypes.c_ulong(io_priority)), ctypes.sizeof(ctypes.c_ulong))
                        kernel32.CloseHandle(thread_handle)
                self.io_priorities[pid] = io_priority
                self.stats['priority_changes'] += 1
                return True
            return False
    def optimize_for_pattern(self, pid, pattern):
        with self.lock:
            if not pattern:
                return False
            if 'sequential' in pattern:
                pattern_data = self.process_io_patterns[pid]
                pattern_data['optimization_hint'] = 'sequential'
                self.stats['coalescing_events'] += 1
                return True
            else:
                pattern_data = self.process_io_patterns[pid]
                pattern_data['optimization_hint'] = 'random'
                return True
            return False
    def get_stats(self):
        with self.lock:
            total_ops = sum((data['sequential_reads'] + data['random_reads'] + data['sequential_writes'] + data['random_writes'] for data in self.process_io_patterns.values()))
            if total_ops > 0:
                sequential_pct = sum((data['sequential_reads'] + data['sequential_writes'] for data in self.process_io_patterns.values())) / total_ops * 100
            else:
                sequential_pct = 0
            return {'nvme_queue_depth': self.nvme_queue_depth, 'pattern_detections': self.stats['pattern_detections'], 'queue_adjustments': self.stats['queue_adjustments'], 'priority_changes': self.stats['priority_changes'], 'sequential_percentage': sequential_pct, 'tracked_processes': len(self.process_io_patterns), 'estimated_overhead': 0.15}
class MetadataOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.enabled = False
        self.optimization_level = "normal"
        self.metadata_cache = {}
        self.optimization_engine = None
        self.dir_cache = {}
        self.stats = {'optimizations': 0, 'cache_hits': 0}
    def enable(self):
        with self.lock:
            self.enabled = True
    def disable(self):
        with self.lock:
            self.enabled = False
            self.optimization_engine = None
    def set_optimization_level(self, level):
        with self.lock:
            if level in ['normal', 'aggressive', 'extreme']:
                self.optimization_level = level
    def enable_metadata_caching(self):
        with self.lock:
            if not self.metadata_cache:
                self.metadata_cache = {}
    def start_optimization_engine(self):
        with self.lock:
            if not self.enabled or self.optimization_engine is not None:
                return
            def optimize_metadata():
                while self.enabled:
                    self._optimize_metadata_structures()
                    self._compact_metadata()
                    self._update_indexes()
                    time.sleep(10)
            self.optimization_engine = threading.Thread(target=optimize_metadata, daemon=True, name='MetadataOptimizer')
            self.optimization_engine.start()
    def _optimize_metadata_structures(self):
        if self.dir_cache:
            current_time = time.time()
            stale_keys = [k for k, v in self.dir_cache.items() 
                         if current_time - v.get('timestamp', 0) > 300]
            for key in stale_keys:
                del self.dir_cache[key]
        max_cache_size = {
            'normal': 1000,
            'aggressive': 500,
            'extreme': 250
        }.get(self.optimization_level, 1000)
        if len(self.metadata_cache) > max_cache_size:
            items_to_keep = max_cache_size // 2
            keys_to_keep = list(self.metadata_cache.keys())[-items_to_keep:]
            self.metadata_cache = {k: self.metadata_cache[k] for k in keys_to_keep}
        self.stats['optimizations'] += 1
    def _compact_metadata(self):
        if len(self.metadata_cache) > 1000:
            self.metadata_cache = dict(list(self.metadata_cache.items())[-500:])
    def get_from_cache(self, key):
        with self.lock:
            if key in self.metadata_cache:
                self.stats['cache_hits'] += 1
                return self.metadata_cache[key]
            return None
    def get_optimization_count(self):
        with self.lock:
            return self.stats.get('optimizations', 0)
    def get_metrics(self):
        with self.lock:
            return {
                'enabled': self.enabled,
                'optimization_level': self.optimization_level,
                'optimizations': self.stats.get('optimizations', 0),
                'cache_hits': self.stats.get('cache_hits', 0),
                'cache_size': len(self.metadata_cache)
            }
    def optimize_metadata_operations(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Control\\FileSystem'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'NtfsDisableLastAccessUpdate', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'NtfsDisable8dot3NameCreation', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
class TCPFastOpenOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
    def enable_tcp_fast_open(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'EnableTcpFastOpen', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'TcpMaxDataRetransmissions', 0, winreg.REG_DWORD, 3)
        winreg.CloseKey(key)
class DynamicNetworkBufferTuner:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_latency = 0
        self.buffer_size = 65535
    def adjust_buffers_by_latency(self, latency_ms):
        with self.lock:
            self.current_latency = latency_ms
            if latency_ms < 20:
                self.buffer_size = 32768
            elif latency_ms < 50:
                self.buffer_size = 65535
            else:
                self.buffer_size = 131072
            key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'TcpWindowSize', 0, winreg.REG_DWORD, self.buffer_size)
            winreg.SetValueEx(key, 'GlobalMaxTcpWindowSize', 0, winreg.REG_DWORD, self.buffer_size * 4)
            winreg.CloseKey(key)
class BBRCongestionControl:
    def __init__(self):
        self.lock = threading.RLock()
    def enable_bbr_algorithm(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'TcpCongestionControl', 0, winreg.REG_DWORD, BBR_ALGORITHM)
        winreg.SetValueEx(key, 'TcpAckFrequency', 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
class NetworkPollingOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.polling_enabled = False
    def enable_polling_mode(self, gaming_mode):
        with self.lock:
            self.polling_enabled = gaming_mode
            key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'DisableTaskOffload', 0, winreg.REG_DWORD, 1 if gaming_mode else 0)
            winreg.CloseKey(key)
class AggressiveDNSCache:
    def __init__(self):
        self.lock = threading.RLock()
        self.dns_cache = {}
    def configure_dns_caching(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'MaxCacheTtl', 0, winreg.REG_DWORD, DNS_CACHE_TTL_24_HOURS)
        winreg.SetValueEx(key, 'MaxNegativeCacheTtl', 0, winreg.REG_DWORD, DNS_NEGATIVE_CACHE_TTL_1_HOUR)
        winreg.CloseKey(key)
class GPUSchedulingOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
    def enable_hardware_gpu_scheduling(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'HwSchMode', 0, winreg.REG_DWORD, HARDWARE_SCHEDULING_MODE_2)
        winreg.CloseKey(key)
class PCIeBandwidthOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
    def maximize_pcie_bandwidth(self):
        key_path = 'SYSTEM\\CurrentControlSet\\Services\\pci\\Parameters'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'ASPMOptOut', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
class DirectXVulkanOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
    def optimize_rendering_performance(self):
        key_path = 'SOFTWARE\\Microsoft\\DirectX'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'DisableDebugLayer', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
class ProcessDependencyAnalyzer:
    def __init__(self, handle_cache):
        self.lock = threading.RLock()
        self.handle_cache = handle_cache
        self.dependency_graph = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)
        self.critical_chains = []
        self.bottlenecks = {}
        self.last_analysis = time.time()
        self.stats = {'dependencies_mapped': 0, 'critical_paths_found': 0, 'bottlenecks_detected': 0, 'chain_optimizations': 0}
    def build_dependency_graph(self, active_pids):
        with self.lock:
            self.dependency_graph.clear()
            self.reverse_dependencies.clear()
            for pid in active_pids:
                proc = psutil.Process(pid)
                parent_pid = proc.ppid()
                if parent_pid and parent_pid in active_pids:
                    self.dependency_graph[parent_pid].add(pid)
                    self.reverse_dependencies[pid].add(parent_pid)
                    self.stats['dependencies_mapped'] += 1
    def identify_critical_paths(self):
        with self.lock:
            self.critical_chains = []
            roots = [pid for pid in self.dependency_graph.keys() if not self.reverse_dependencies.get(pid)]
            for root in roots:
                path = self._find_longest_path(root)
                if len(path) > 2:
                    self.critical_chains.append(path)
                    self.stats['critical_paths_found'] += 1
            self.critical_chains.sort(key=len, reverse=True)
            return self.critical_chains
    def _find_longest_path(self, start_pid, visited=None):
        if visited is None:
            visited = set()
        if start_pid in visited:
            return []
        visited.add(start_pid)
        children = self.dependency_graph.get(start_pid, set())
        if not children:
            return [start_pid]
        longest_child_path = []
        for child_pid in children:
            child_path = self._find_longest_path(child_pid, visited.copy())
            if len(child_path) > len(longest_child_path):
                longest_child_path = child_path
        return [start_pid] + longest_child_path
    def detect_bottlenecks(self):
        with self.lock:
            self.bottlenecks = {}
            for chain in self.critical_chains:
                for pid in chain:
                    proc = psutil.Process(pid)
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    num_threads = proc.num_threads()
                    dependents = self.dependency_graph.get(pid, set())
                    if cpu_percent > 70 and len(dependents) > 0:
                        self.bottlenecks[pid] = {'cpu_percent': cpu_percent, 'num_threads': num_threads, 'dependents': list(dependents), 'chain_position': chain.index(pid)}
                        self.stats['bottlenecks_detected'] += 1
    def optimize_critical_chain(self, chain, handle_cache):
        with self.lock:
            if len(chain) < 2:
                return False
            for idx, pid in enumerate(chain):
                handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
                if handle:
                    if idx == 0:
                        priority = PRIORITY_CLASSES['HIGH']
                    elif idx < len(chain) / 2:
                        priority = PRIORITY_CLASSES['ABOVE_NORMAL']
                    else:
                        priority = PRIORITY_CLASSES['NORMAL']
                    win32process.SetPriorityClass(int(handle), priority)
    def analyze_and_optimize(self, active_pids):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_analysis < 60:
                return False
            self.last_analysis = current_time
            self.build_dependency_graph(active_pids)
            self.identify_critical_paths()
            self.detect_bottlenecks()
            if self.critical_chains:
                self.optimize_critical_chain(self.critical_chains[0], self.handle_cache)
            return True
    def get_stats(self):
        with self.lock:
            return {'dependencies_mapped': self.stats['dependencies_mapped'], 'critical_paths': len(self.critical_chains), 'active_bottlenecks': len(self.bottlenecks), 'chain_optimizations': self.stats['chain_optimizations'], 'longest_chain_length': len(self.critical_chains[0]) if self.critical_chains else 0, 'estimated_overhead': 0.3}
class EnhancedNetworkStackOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_latency_ms = 50
        self.current_tcp_window = 65535
        self.current_rss_queues = 4
        self.last_adjustment = time.time()
        self.network_stats_history = deque(maxlen=20)
        self.stats = {'window_adjustments': 0, 'rss_adjustments': 0, 'coalescing_adjustments': 0, 'priority_changes': 0}
    def measure_network_latency(self):
        with self.lock:
            latencies = []
            for target in ['8.8.8.8', '1.1.1.1']:
                start = time.time()
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', target], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=2)
                elapsed = (time.time() - start) * 1000
                if result.returncode == 0:
                    output = result.stdout.decode('utf-8', errors='ignore')
                    if 'time=' in output or 'tiempo=' in output:
                        import re
                        match = re.search('time[=<](\\d+)', output, re.IGNORECASE)
                        if match:
                            latencies.append(int(match.group(1)))
                        else:
                            latencies.append(elapsed)
    def adjust_tcp_window_scaling(self, latency_ms=None):
        with self.lock:
            if latency_ms is None:
                latency_ms = self.current_latency_ms
            if latency_ms < 20:
                target_window = 32768
            elif latency_ms < 100:
                target_window = 65535
            else:
                target_window = 262144
            if target_window != self.current_tcp_window:
                key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'TcpWindowSize', 0, winreg.REG_DWORD, target_window)
                winreg.SetValueEx(key, 'Tcp1323Opts', 0, winreg.REG_DWORD, 3)
                winreg.CloseKey(key)
                old_window = self.current_tcp_window
                self.current_tcp_window = target_window
                self.stats['window_adjustments'] += 1
                return True
            return False
    def adjust_rss_queues(self, cpu_count, network_load=0):
        with self.lock:
            if network_load > 0.7:
                target_queues = min(cpu_count, 8)
            elif network_load > 0.3:
                target_queues = min(cpu_count // 2, 4)
            else:
                target_queues = 2
            if target_queues != self.current_rss_queues:
                key_path = 'SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters'
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'RssBaseCpu', 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, 'MaxRssProcessors', 0, winreg.REG_DWORD, target_queues)
                winreg.CloseKey(key)
                old_queues = self.current_rss_queues
                self.current_rss_queues = target_queues
                self.stats['rss_adjustments'] += 1
                return True
            return False
    def optimize_interrupt_coalescing(self, throughput_mbps):
        with self.lock:
            if throughput_mbps > 100:
                interrupt_moderation = 'Extreme'
                coalesce_usec = 250
            elif throughput_mbps > 10:
                interrupt_moderation = 'Adaptive'
                coalesce_usec = 100
            else:
                interrupt_moderation = 'Minimal'
                coalesce_usec = 25
            result = subprocess.run(['powershell', '-Command', f'Get-NetAdapter | Set-NetAdapterAdvancedProperty -DisplayName "Interrupt Moderation" -DisplayValue "{interrupt_moderation}"'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            if result.returncode == 0:
                self.stats['coalescing_adjustments'] += 1
                return True
            return False
    def prioritize_network_packets(self, pid, is_foreground=False, is_gaming=False):
        with self.lock:
            if is_gaming:
                dscp_value = 46
            elif is_foreground:
                dscp_value = 34
            else:
                dscp_value = 0
            self.stats['priority_changes'] += 1
            return True
    def optimize_periodically(self, cpu_count):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_adjustment < 60:
                return False
            self.last_adjustment = current_time
            latency = self.measure_network_latency()
            self.adjust_tcp_window_scaling(latency)
            network_load = 0.3
            self.adjust_rss_queues(cpu_count, network_load)
            return True
    def get_stats(self):
        with self.lock:
            return {'current_latency_ms': self.current_latency_ms, 'tcp_window_bytes': self.current_tcp_window, 'rss_queues': self.current_rss_queues, 'window_adjustments': self.stats['window_adjustments'], 'rss_adjustments': self.stats['rss_adjustments'], 'coalescing_adjustments': self.stats['coalescing_adjustments'], 'estimated_overhead': 0.1}
class EnhancedSystemResponsivenessOptimizer:
    def __init__(self):
        self.lock = threading.RLock()
        self.current_responsiveness = 20
        self.boosted_processes = {}
        self.last_adjustment = time.time()
        self.stats = {'responsiveness_changes': 0, 'priority_boosts': 0, 'background_throttles': 0}
    def adjust_system_responsiveness(self, scenario='balanced'):
        with self.lock:
            responsiveness_map = {'gaming': 10, 'productivity': 20, 'balanced': 20, 'background': 40, 'rendering': 30}
            target_value = responsiveness_map.get(scenario, 20)
            if target_value != self.current_responsiveness:
                key_path = SystemResponsivenessKey
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'SystemResponsiveness', 0, winreg.REG_DWORD, target_value)
                winreg.CloseKey(key)
                old_value = self.current_responsiveness
                self.current_responsiveness = target_value
                self.stats['responsiveness_changes'] += 1
                return True
            return False
    def boost_interactive_priority(self, pid, handle_cache, duration_sec=5):
        with self.lock:
            current_time = time.time()
            if pid in self.boosted_processes:
                boost_data = self.boosted_processes[pid]
                if current_time - boost_data['start_time'] < duration_sec:
                    return True
            handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                win32process.SetPriorityClass(int(handle), PRIORITY_CLASSES['HIGH'])
                self.boosted_processes[pid] = {'start_time': current_time, 'duration': duration_sec, 'original_priority': PRIORITY_CLASSES['NORMAL']}
                self.stats['priority_boosts'] += 1
                return True
            return False
    def cleanup_expired_boosts(self, handle_cache):
        with self.lock:
            current_time = time.time()
            expired = []
            for pid, boost_data in self.boosted_processes.items():
                if current_time - boost_data['start_time'] >= boost_data['duration']:
                    handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
                    if handle:
                        win32process.SetPriorityClass(int(handle), boost_data['original_priority'])
    def throttle_background_tasks(self, pid, handle_cache):
        with self.lock:
            handle = handle_cache.get_handle(pid, PROCESS_SET_INFORMATION)
            if handle:
                throttle = PROCESS_POWER_THROTTLING_STATE()
                throttle.Version = 1
                throttle.ControlMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
                throttle.StateMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
                ntdll.NtSetInformationProcess(int(handle), ProcessPowerThrottling, ctypes.byref(throttle), ctypes.sizeof(throttle))
                self.stats['background_throttles'] += 1
                return True
            return False
    def get_stats(self):
        with self.lock:
            return {'current_responsiveness': self.current_responsiveness, 'active_boosts': len(self.boosted_processes), 'total_responsiveness_changes': self.stats['responsiveness_changes'], 'total_priority_boosts': self.stats['priority_boosts'], 'total_background_throttles': self.stats['background_throttles'], 'estimated_overhead': 0.05}
class UnifiedProcessManager:
    def __init__(self, debug_privilege_enabled: bool=True):
        self.lock = threading.RLock()
        self.debug_privilege_enabled = debug_privilege_enabled
        self.cpu_count = psutil.cpu_count(logical=True)
        self.topology = self._query_cpu_topology()
        self.pe_core_sets = self._classify_pe_cores()
        self.core_config = self._build_core_config()
        self.affinity_mask_cache = {}
        for key, cores in self.core_config.items():
            mask = sum((1 << c for c in cores))
            self.affinity_mask_cache[tuple(sorted(cores))] = mask
        self.process_states = {}
        self.applied_states = {}
        self.minimized_processes = {}
        self.pid_to_job = {}
        self.jobs = {}
        self.foreground_pid = None
        self.whitelist = set()
        self.config_last_modified = 0
        self.interned_process_names = {}
        common_names = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'explorer.exe', 'svchost.exe', 'system', 'idle', 'dwm.exe', 'csrss.exe', 'lsass.exe', 'services.exe', 'winlogon.exe', 'smss.exe']
        for name in common_names:
            self.interned_process_names[name] = sys.intern(name)
        self.timer_coalescer = AdvancedTimerCoalescer(base_resolution_ms=1)
        self._register_coalesced_tasks()
        self.hardware_detector = HardwareDetector()
        self.handle_cache = ProcessHandleCache(max_cache_size=256, handle_ttl_seconds=30.0, debug_privilege_enabled=self.debug_privilege_enabled)
        self.process_snapshot = ProcessSnapshotEngine(cache_ttl_ms=500)
        self.settings_applicator = BatchedSettingsApplicator(self.handle_cache)
        self.workingset_optimizer = WorkingSetOptimizer(self.handle_cache)
        self.foreground_debouncer = ForegroundDebouncer(debounce_time_ms=300, hysteresis_time_ms=150)
        self.process_tree = ProcessTreeCache(rebuild_interval_ms=2000)
        self.cpu_pinning = CPUPinningEngine(self.handle_cache, self.cpu_count, self.topology)
        self.large_page_manager = LargePageManager(self.handle_cache)
        self.advanced_ws_trimmer = AdvancedWorkingSetTrimmer(self.handle_cache)
        self.prefetch_optimizer = PrefetchOptimizer(self.hardware_detector)
        self.memory_priority_manager = MemoryPriorityManager(self.handle_cache)
        self.process_service_manager = ProcessServiceManager()
        self.cpu_parking_controller = CPUParkingController()
        self.heterogeneous_scheduler = HeterogeneousThreadScheduler(self.handle_cache, self.pe_core_sets.get('p_cores', []), self.pe_core_sets.get('e_cores', []))
        self.context_switch_reducer = ContextSwitchReducer()
        self.smt_scheduler = SMTScheduler(self.cpu_count)
        self.cpu_frequency_scaler = CPUFrequencyScaler()
        self.awe_manager = AWEManager(self.handle_cache)
        self.interrupt_affinity_optimizer = InterruptAffinityOptimizer(self.pe_core_sets.get('e_cores', []))
        self.dpc_latency_controller = DPCLatencyController()
        self.temp_monitor = CPUTemperatureMonitor()
        self.c_states_optimizer = CStatesOptimizer()
        self.storage_optimizer = StorageOptimizer()
        self.network_optimizer = NetworkOptimizer()
        self.power_optimizer = PowerManagementOptimizer()
        self.kernel_optimizer = KernelOptimizer()
        self.dynamic_priority_algo = DynamicPriorityAlgorithm(self.handle_cache)
        self.telemetry_collector = RealtimeTelemetryCollector()
        self.profile_manager = AutomaticProfileManager()
        self.numa_allocator = NUMAAwareMemoryAllocator()
        self.huge_pages_manager = DynamicHugePagesManager(self.handle_cache)
        self.memory_dedup_manager = MemoryDeduplicationManager()
        self.realtime_priority_mgr = RealtimePriorityManager(self.handle_cache)
        self.readahead_manager = AdaptiveReadAheadManager()
        self.write_coalescer = WriteCoalescingManager()
        self.storage_tier_mgr = StorageTierManager()
        self.disk_cache_tuner = DynamicDiskCacheTuner()
        self.network_flow_prioritizer = NetworkFlowPrioritizer()
        self.tcp_congestion_tuner = TCPCongestionControlTuner()
        self.network_interrupt_coalescer = NetworkInterruptCoalescer()
        self.adaptive_polling_mgr = AdaptiveNetworkPollingManager()
        self.multilevel_timer_coalescer = MultiLevelTimerCoalescer()
        self.syscall_batcher = SystemCallBatcher()
        self.dvfs_scaler = DynamicVoltageFrequencyScaler()
        self._l3_cache_optimizer = None
        self._avx_instruction_optimizer = None
        self._enhanced_smt_optimizer = None
        self._cpu_pipeline_optimizer = None
        self._tsc_synchronizer = None
        self._tlb_optimizer = None
        self._advanced_numa_optimizer = None
        self._memory_scrubbing_optimizer = None
        self._cache_coherency_optimizer = None
        self._memory_bandwidth_manager = None
        self._trim_scheduler = None
        self._write_cache_optimizer = None
        self._io_scheduler = None
        self._ncq_optimizer = None
        self._fs_cache_optimizer = None
        self._io_priority_inheritance = None
        self._metadata_optimizer = None
        self._tcp_fast_open = None
        self._network_buffer_tuner = None
        self._bbr_congestion = None
        self._network_polling = None
        self._dns_cache = None
        self._gpu_scheduler = None
        self._pcie_optimizer = None
        self._dx_vulkan_optimizer = None
        self._dynamic_multilayer_profiles = None
        self._enhanced_cache_topology = None
        self._advanced_memory_page_priority = None
        self._adaptive_io_scheduler = None
        self._advanced_interrupt_dpc = None
        self._adaptive_timer_resolution = None
        self._enhanced_network_stack = None
        self._enhanced_system_responsiveness = None
        self._thermal_aware_scheduler = None
        self._process_dependency_analyzer = None
        self.decision_cache = OptimizationDecisionCache(ttl_seconds=300)
        self.integrity_validator = IntegrityValidator(self.handle_cache)
        self.suspension_manager = ProcessSuspensionManager()
        self.responsiveness_controller = SystemResponsivenessController()
        self._registry_buffer = RegistryWriteBuffer(flush_interval=15.0)
        self._ctypes_pool = CTypesStructurePool(max_pool_size=20)
        self.settings_applicator.ctypes_pool = self._ctypes_pool
        self.load_whitelist()
        self.ram_monitor_active = True
        self.last_ram_cleanup = 0
        self.ram_cleanup_cooldown = 3600
        self.start_ram_monitor()
        self.win_event_hook = None
        self._start_foreground_hook_thread()
        self.blacklist_names = {'system', 'idle', 'smss.exe', 'csrss.exe', 'wininit.exe', 'winlogon.exe', 'services.exe', 'lsass.exe', 'svchost.exe', 'fontdrvhost.exe', 'registry', 'memcompression', 'sihost.exe', 'dwm.exe', 'ctfmon.exe', 'cmd.exe', 'python.exe', 'pythonw.exe', 'conhost.exe', 'taskmgr.exe', 'taskhosw.exe', 'runtimebroker.exe'}
        self.blacklist_contains = ['\\windows\\', 'defender', 'msmpeng.exe', 'wuauclt.exe', 'tiworker.exe']
        self.blacklist_bloom = SimpleBloomFilter(expected_elements=len(self.blacklist_names) * 2)
        for name in self.blacklist_names:
            self.blacklist_bloom.add(name)
        self._apply_initial_optimizations()
    def _apply_initial_optimizations(self):
        self.c_states_optimizer.disable_deep_c_states()
        self.storage_optimizer.optimize_nvme_queue_depth()
        self.storage_optimizer.optimize_file_system_cache()
        self.network_optimizer.optimize_tcp_window_scaling()
        self.network_optimizer.configure_rss()
        self.network_optimizer.disable_network_throttling()
        self.power_optimizer.disable_pcie_aspm()
        self.prefetch_optimizer.check_and_disable_for_ssd(self.registry_buffer)
        self.kernel_optimizer.optimize_timer_resolution()
        self.kernel_optimizer.increase_paged_pool_size()
    def manage_thermal_throttling(self):
        if self.temp_monitor.is_overheating():
            cpu_usage = psutil.cpu_percent(interval=0.1)
            if cpu_usage > THERMAL_THROTTLING_CPU_THRESHOLD:
                for pid, state in list(self.process_states.items()):
                    if state.get('is_foreground'):
                        continue
                    handle = self.handle_cache.get_handle(pid, PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION)
                    if handle:
                        throttling_state = PROCESS_POWER_THROTTLING_STATE()
                        throttling_state.Version = 1
                        throttling_state.ControlMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
                        throttling_state.StateMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED
                        kernel32.SetProcessInformation(handle, ProcessPowerThrottling, ctypes.byref(throttling_state), ctypes.sizeof(throttling_state))
    def _register_coalesced_tasks(self):
        self.timer_coalescer.register_task('whitelist_reload', interval_ms=10000, priority=3)
        self.timer_coalescer.register_task('process_cache_update', interval_ms=1000, priority=8)
        self.timer_coalescer.register_task('zombie_cleanup', interval_ms=10000, priority=5)
        self.timer_coalescer.register_task('foreground_check', interval_ms=500, priority=9)
        self.timer_coalescer.register_task('process_tree_rebuild', interval_ms=5000, priority=6)
        self.timer_coalescer.register_task('handle_cache_cleanup', interval_ms=15000, priority=4)
        self.timer_coalescer.register_task('cpu_pinning_cleanup', interval_ms=15000, priority=3)
        self.timer_coalescer.register_task('decision_cache_cleanup', interval_ms=60000, priority=2)
        self.timer_coalescer.register_task('process_suspension_check', interval_ms=30000, priority=4)
    def _query_cpu_topology(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        topology_cache_path = os.path.join(script_dir, '.cpu_topology_cache.json')
        if os.path.exists(topology_cache_path):
            with open(topology_cache_path, 'r') as f:
                cached_data = json.load(f)
                topology = {'llc_groups': [set(g) for g in cached_data.get('llc_groups', [])], 'numa_nodes': defaultdict(set, {int(k): set(v) for k, v in cached_data.get('numa_nodes', {}).items()}), 'p_cores': set(cached_data.get('p_cores', [])), 'e_cores': set(cached_data.get('e_cores', []))}
                return topology
        topology = {'llc_groups': [], 'numa_nodes': defaultdict(set), 'p_cores': set(), 'e_cores': set()}
        returned_length = wintypes.DWORD(0)
        kernel32.GetLogicalProcessorInformationEx(RelationProcessorCore, None, ctypes.byref(returned_length))
        buf_size = returned_length.value
        if buf_size > 0:
            buf = (ctypes.c_byte * buf_size)()
            if kernel32.GetLogicalProcessorInformationEx(RelationProcessorCore, ctypes.byref(buf), ctypes.byref(returned_length)):
                offset = 0
                while offset < buf_size:
                    entry = SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX.from_buffer_copy(buf[offset:])
                    if entry.Relationship == RelationProcessorCore:
                        proc_rel = entry.u.Processor
                        efficiency_class = proc_rel.EfficiencyClass
                        if proc_rel.GroupCount > 0:
                            mask = proc_rel.GroupMask[0].Mask
                            cpus = self._mask_to_cpu_indices(mask, list(range(self.cpu_count)))
                            if efficiency_class == 0:
                                topology['p_cores'].update(cpus)
                            else:
                                topology['e_cores'].update(cpus)
                    offset += entry.Size
        if not topology['p_cores'] and (not topology['e_cores']):
            returned_length = wintypes.DWORD(0)
            kernel32.GetLogicalProcessorInformation(None, ctypes.byref(returned_length))
            buf_size = returned_length.value
            if buf_size == 0:
                return topology
            buf = (ctypes.c_byte * buf_size)()
            if not kernel32.GetLogicalProcessorInformation(ctypes.byref(buf), ctypes.byref(returned_length)):
                return topology
            entry_size = ctypes.sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
            count = buf_size // entry_size
            cpu_index_map = self._build_cpu_index_map()
            for i in range(count):
                base = i * entry_size
                entry = SYSTEM_LOGICAL_PROCESSOR_INFORMATION.from_buffer_copy(buf[base:base + entry_size])
                mask = entry.ProcessorMask
                if entry.Relationship == RelationCache:
                    cache = entry.u.Cache
                    if cache.Level in (3, 2):
                        cpus = self._mask_to_cpu_indices(mask, cpu_index_map)
                        if cpus:
                            topology['llc_groups'].append(set(cpus))
                elif entry.Relationship == RelationNumaNode:
                    node_id = entry.u.NumaNode_NodeNumber
                    cpus = self._mask_to_cpu_indices(mask, cpu_index_map)
                    topology['numa_nodes'][node_id].update(cpus)
        if not topology['llc_groups']:
            topology['llc_groups'] = [set(range(self.cpu_count))]
        cache_data = {'llc_groups': [list(g) for g in topology['llc_groups']], 'numa_nodes': {k: list(v) for k, v in topology['numa_nodes'].items()}, 'p_cores': list(topology['p_cores']), 'e_cores': list(topology['e_cores'])}
        with open(topology_cache_path, 'w') as f:
            json.dump(cache_data, f)
        return topology
    def _build_cpu_index_map(self):
        return list(range(self.cpu_count))
    @memoize_with_ttl(ttl_seconds=3600)
    def _mask_to_cpu_indices(self, mask, cpu_index_map):
        indices = []
        bit = 0
        cpu_index_map_len = len(cpu_index_map)
        while mask and bit < cpu_index_map_len:
            if mask & 1:
                indices.append(cpu_index_map[bit])
            mask >>= 1
            bit += 1
        return indices
    def _classify_pe_cores(self):
        p_cores = self.topology.get('p_cores', set())
        e_cores = self.topology.get('e_cores', set())
        if not p_cores and not e_cores:
            llc_groups = self.topology.get('llc_groups', [])
            if llc_groups:
                largest = max(llc_groups, key=len)
                p_cores = set(sorted(largest))
                e_cores = set(range(self.cpu_count)) - p_cores
        if not p_cores:
            p_cores = set(range(self.cpu_count))
            e_cores = set()
        return {'p_cores': sorted(p_cores), 'e_cores': sorted(e_cores)}
    def _build_core_config(self):
        p = self.pe_core_sets.get('p_cores', list(range(self.cpu_count)))
        e = self.pe_core_sets.get('e_cores', [])
        foreground_cores = [c for c in p if c != 0]
        if not foreground_cores:
            foreground_cores = p
        if not e:
            half = max(1, len(p) // 2)
            background_cores = p[:half]
        else:
            background_cores = e
        return {'foreground': foreground_cores, 'background': background_cores}
    def load_whitelist(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.json')
        if os.path.exists(config_path):
            current_modified = os.path.getmtime(config_path)
            if current_modified != self.config_last_modified:
                config = load_config()
                self.whitelist = set()
                if 'whitelist' in config and isinstance(config['whitelist'], list):
                    for item in config['whitelist']:
                        if isinstance(item, dict) and 'name' in item:
                            self.whitelist.add(item['name'].lower())
                self.config_last_modified = current_modified
    @property
    def l3_cache_optimizer(self):
        if self._l3_cache_optimizer is None:
            self._l3_cache_optimizer = L3CacheOptimizer(self.topology)
        return self._l3_cache_optimizer
    @property
    def avx_instruction_optimizer(self):
        if self._avx_instruction_optimizer is None:
            self._avx_instruction_optimizer = AVXInstructionOptimizer(self.handle_cache, self.cpu_count)
        return self._avx_instruction_optimizer
    @property
    def enhanced_smt_optimizer(self):
        if self._enhanced_smt_optimizer is None:
            self._enhanced_smt_optimizer = EnhancedSMTOptimizer(self.topology, self.cpu_count)
        return self._enhanced_smt_optimizer
    @property
    def cpu_pipeline_optimizer(self):
        if self._cpu_pipeline_optimizer is None:
            self._cpu_pipeline_optimizer = CPUPipelineOptimizer(self.handle_cache)
        return self._cpu_pipeline_optimizer
    @property
    def tlb_optimizer(self):
        if self._tlb_optimizer is None:
            self._tlb_optimizer = TLBOptimizer(self.handle_cache)
        return self._tlb_optimizer
    @property
    def trim_scheduler(self):
        if self._trim_scheduler is None:
            self._trim_scheduler = IntelligentTRIMScheduler()
        return self._trim_scheduler
    @property
    def ncq_optimizer(self):
        if self._ncq_optimizer is None:
            self._ncq_optimizer = NCQOptimizer()
        return self._ncq_optimizer
    @property
    def memory_scrubbing_optimizer(self):
        if self._memory_scrubbing_optimizer is None:
            self._memory_scrubbing_optimizer = MemoryScrubbingOptimizer()
        return self._memory_scrubbing_optimizer
    @property
    def network_polling(self):
        if self._network_polling is None:
            existing = getattr(self, 'adaptive_polling_mgr', None)
            if existing is not None:
                self._network_polling = existing
            else:
                self._network_polling = AdaptiveNetworkPollingManager()
                self.adaptive_polling_mgr = self._network_polling
        return self._network_polling
    @property
    def network_buffer_tuner(self):
        if self._network_buffer_tuner is None:
            self._network_buffer_tuner = DynamicNetworkBufferTuner()
        return self._network_buffer_tuner
    @property
    def advanced_numa_optimizer(self):
        if self._advanced_numa_optimizer is None:
            self._advanced_numa_optimizer = AdvancedNUMAOptimizer(self.handle_cache)
        return self._advanced_numa_optimizer
    @property
    def cache_coherency_optimizer(self):
        if self._cache_coherency_optimizer is None:
            self._cache_coherency_optimizer = CacheCoherencyOptimizer()
        return self._cache_coherency_optimizer
    @property
    def memory_bandwidth_manager(self):
        if self._memory_bandwidth_manager is None:
            self._memory_bandwidth_manager = MemoryBandwidthManager(self.handle_cache)
        return self._memory_bandwidth_manager
    @property
    def io_priority_inheritance(self):
        if self._io_priority_inheritance is None:
            self._io_priority_inheritance = IOPriorityInheritance(self.handle_cache)
        return self._io_priority_inheritance
    @property
    def dynamic_multilayer_profiles(self):
        if self._dynamic_multilayer_profiles is None:
            self._dynamic_multilayer_profiles = DynamicMultiLayerProfileSystem()
        return self._dynamic_multilayer_profiles
    @property
    def enhanced_cache_topology(self):
        if self._enhanced_cache_topology is None:
            self._enhanced_cache_topology = EnhancedCacheTopologyOptimizer(self.topology)
        return self._enhanced_cache_topology
    @property
    def advanced_memory_page_priority(self):
        if self._advanced_memory_page_priority is None:
            self._advanced_memory_page_priority = AdvancedMemoryPagePriorityManager(self.handle_cache)
        return self._advanced_memory_page_priority
    @property
    def adaptive_io_scheduler(self):
        if self._adaptive_io_scheduler is None:
            self._adaptive_io_scheduler = AdaptiveIOScheduler(self.handle_cache)
        return self._adaptive_io_scheduler
    @property
    def advanced_interrupt_dpc(self):
        if self._advanced_interrupt_dpc is None:
            self._advanced_interrupt_dpc = AdvancedInterruptDPCOptimizer(self.cpu_count, self.pe_core_sets.get('e_cores', []))
        return self._advanced_interrupt_dpc
    @property
    def adaptive_timer_resolution(self):
        if self._adaptive_timer_resolution is None:
            self._adaptive_timer_resolution = AdaptiveTimerResolutionManager()
        return self._adaptive_timer_resolution
    @property
    def enhanced_network_stack(self):
        if self._enhanced_network_stack is None:
            self._enhanced_network_stack = EnhancedNetworkStackOptimizer()
        return self._enhanced_network_stack
    @property
    def enhanced_system_responsiveness(self):
        if self._enhanced_system_responsiveness is None:
            self._enhanced_system_responsiveness = EnhancedSystemResponsivenessOptimizer()
        return self._enhanced_system_responsiveness
    @property
    def thermal_aware_scheduler(self):
        with self.lock:
            if self._thermal_aware_scheduler is None:
                self._thermal_aware_scheduler = ThermalAwareScheduler(self.cpu_count, self.temp_monitor)
            return self._thermal_aware_scheduler
    @property
    def process_dependency_analyzer(self):
        with self.lock:
            if self._process_dependency_analyzer is None:
                self._process_dependency_analyzer = ProcessDependencyAnalyzer(self.handle_cache)
            return self._process_dependency_analyzer
    @property
    def registry_buffer(self):
        with self.lock:
            if self._registry_buffer is None:
                self._registry_buffer = RegistryWriteBuffer(flush_interval=15.0)
            return self._registry_buffer
    @property
    def ctypes_pool(self):
        with self.lock:
            if self._ctypes_pool is None:
                self._ctypes_pool = CTypesStructurePool(max_pool_size=20)
            return self._ctypes_pool
    def _intern_process_name(self, name):
        if name in self.interned_process_names:
            return self.interned_process_names[name]
        interned = sys.intern(name)
        if len(self.interned_process_names) > 500:
            self.interned_process_names = dict(list(self.interned_process_names.items())[:250])
        self.interned_process_names[name] = interned
        return interned
    def is_whitelisted(self, pid: int) -> bool:
        if not isinstance(pid, int) or pid <= 0:
            return False
        process = psutil.Process(pid)
        if not process.is_running():
            return False
        name = self._intern_process_name(process.name().lower())
        exe = ''
        exe = process.exe().lower()
    def is_blacklisted(self, pid: int) -> bool:
        if not isinstance(pid, int) or pid <= 0:
            return True
        p = psutil.Process(pid)
        if not p.is_running():
            return True
        name = self._intern_process_name(p.name().lower())
        if self.blacklist_bloom.contains(name):
            if name in self.blacklist_names:
                return True
        if not name.endswith('.exe'):
            return True
        username = p.username()
        if username and username.lower().startswith(('nt authority\\', 'local service', 'network service')):
            return True
        return False
    def _start_foreground_hook_thread(self):
        def hook_thread():
            @WinEventProcType
            def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
                if event == EVENT_SYSTEM_FOREGROUND and hwnd:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid:
                        self._on_foreground_changed(pid)
            self.win_event_hook = user32.SetWinEventHook(EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND, 0, callback, 0, 0, WINEVENT_OUTOFCONTEXT)
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        t = threading.Thread(target=hook_thread, name='ForegroundHookThread', daemon=True)
        t.start()
    def _on_foreground_changed(self, new_pid):
        if not new_pid or not isinstance(new_pid, int) or new_pid <= 0:
            return
        if not psutil.pid_exists(new_pid):
            return
        is_known = self.is_whitelisted(new_pid)
        self.foreground_debouncer.request_foreground_change(new_pid, self._apply_foreground_change_internal, is_known, new_pid)
    def _apply_foreground_change_internal(self, new_pid):
        with self.lock:
            if not new_pid or new_pid == self.foreground_pid:
                return
            old_pid = self.foreground_pid
            self.foreground_pid = new_pid
            if old_pid and old_pid > 0 and psutil.pid_exists(old_pid):
                self.apply_settings_to_process_group(old_pid, False)
    def get_process_children(self, parent_pid: int) -> List[int]:
        return self.process_tree.get_all_descendants(parent_pid)
    def get_processes_by_name(self, process_name: str) -> List[int]:
        return self.process_snapshot.get_process_by_name(process_name)
    def _desired_settings_for_role(self, is_foreground: bool, pid: Optional[int]=None) -> tuple:
        cores = self.core_config['foreground'] if is_foreground else self.core_config['background']
        priority = PRIORITY_CLASSES['ABOVE_NORMAL'] if is_foreground else PRIORITY_CLASSES['IDLE']
        io_priority = psutil.IOPRIO_NORMAL if is_foreground else psutil.IOPRIO_VERYLOW
        thread_io_priority = 2 if is_foreground else 0
        page_priority = PAGE_PRIORITY_NORMAL
        if not is_foreground:
            if pid and pid in self.minimized_processes:
                time_minimized = time.time() - self.minimized_processes[pid]
                if time_minimized > 1800:
                    page_priority = PAGE_PRIORITY_LOW
                else:
                    page_priority = PAGE_PRIORITY_MEDIUM
            else:
                page_priority = PAGE_PRIORITY_MEDIUM
        disable_boost = False
        trim_working_set = not is_foreground
        use_eco_qos = not is_foreground
        return (cores, priority, io_priority, thread_io_priority, page_priority, disable_boost, trim_working_set, use_eco_qos)
    def _get_applied_state(self, pid: int) -> Dict:
        return self.applied_states.get(pid, {})
    def _set_applied_state(self, pid: int, state: Dict) -> None:
        self.applied_states[pid] = state
    def _apply_base_settings(self, pid: int, is_foreground: bool, cores, desired_prio, desired_io, desired_thread_io, desired_page, desired_disable_boost, use_eco_qos, trim_ws):
        prev = self._get_applied_state(pid)
        settings_to_apply = {}
        if prev.get('cores') != cores:
            settings_to_apply['affinity'] = cores
        if prev.get('priority') != desired_prio:
            settings_to_apply['priority'] = desired_prio
        if prev.get('io') != desired_io:
            settings_to_apply['io_priority'] = desired_io
        if prev.get('thread_io') != desired_thread_io:
            settings_to_apply['thread_io_priority'] = desired_thread_io
        if prev.get('page') != desired_page:
            settings_to_apply['page_priority'] = desired_page
        if prev.get('disable_boost') != desired_disable_boost:
            settings_to_apply['disable_boost'] = desired_disable_boost
        if use_eco_qos and not prev.get('eco_qos'):
            settings_to_apply['eco_qos'] = True
        if trim_ws and (not is_foreground):
            process = psutil.Process(pid)
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.workingset_optimizer.mark_process_foreground(pid, is_foreground)
            if self.workingset_optimizer.should_trim_working_set(pid, memory_mb):
                settings_to_apply['trim_working_set'] = True
        else:
            self.workingset_optimizer.mark_process_foreground(pid, is_foreground)
        if settings_to_apply:
            result = self.settings_applicator.apply_batched_settings(pid, settings_to_apply)
            if result['success']:
                new_state = prev.copy()
                new_state.update({'cores': cores, 'priority': desired_prio, 'io': desired_io, 'thread_io': desired_thread_io, 'page': desired_page, 'disable_boost': desired_disable_boost, 'eco_qos': use_eco_qos})
                self._set_applied_state(pid, new_state)
                self.decision_cache.set(pid, 'settings', {'is_foreground': is_foreground, 'timestamp': time.time()})
                if 'priority' in result['applied']:
                    self.integrity_validator.validate_priority(pid, desired_prio)
                if 'affinity' in result['applied']:
                    self.integrity_validator.validate_affinity(pid, cores)
    def _apply_memory_settings(self, pid: int, is_foreground: bool):
        if is_foreground:
            process = psutil.Process(pid)
            minimized_time = 0
            if pid in self.minimized_processes:
                minimized_time = time.time() - self.minimized_processes[pid]
            self.memory_priority_manager.set_memory_priority(pid, MEMORY_PRIORITY_NORMAL, is_foreground, minimized_time)
            if self.large_page_manager.should_enable_large_pages(pid, is_foreground):
                self.large_page_manager.enable_large_pages_for_process(pid)
            if self.awe_manager.is_32bit_process(pid):
                process_mem_mb = process.memory_info().rss / (1024 * 1024)
                if process_mem_mb > 1024:
                    self.awe_manager.enable_awe_for_process(pid)
        else:
            minimized_time = 0
            if pid in self.minimized_processes:
                minimized_time = time.time() - self.minimized_processes[pid]
            self.memory_priority_manager.set_memory_priority(pid, MEMORY_PRIORITY_LOW, is_foreground, minimized_time)
            self.advanced_ws_trimmer.trim_full_working_set(pid)
            self.memory_dedup_manager.enable_memory_compression(pid)
    def _apply_cpu_settings(self, pid: int, is_foreground: bool, cores):
        if is_foreground:
            process = psutil.Process(pid)
            process_name = process.name()
            num_threads = process.num_threads()
            if num_threads <= 2:
                workload = 'single_thread'
                is_latency_sensitive = True
            elif num_threads <= 8:
                workload = 'latency_sensitive'
                is_latency_sensitive = True
            else:
                workload = 'throughput'
                is_latency_sensitive = False
            self.cpu_pinning.apply_intelligent_pinning(pid, cores, workload)
            self.heterogeneous_scheduler.classify_and_schedule_threads(pid, is_latency_sensitive)
            if is_latency_sensitive:
                self.smt_scheduler.assign_to_physical_cores(pid)
            self.cpu_frequency_scaler.set_turbo_mode(enable=True)
            self.realtime_priority_mgr.monitor_realtime_process(pid, process_name)
        else:
            self.heterogeneous_scheduler.classify_and_schedule_threads(pid, is_latency_sensitive=False)
    def _apply_io_settings(self, pid: int, is_foreground: bool, desired_io):
        if is_foreground:
            process = psutil.Process(pid)
            self.network_flow_prioritizer.prioritize_foreground_traffic(pid)
        else:
            self.io_priority_inheritance.throttle_background_io(pid)
    def apply_all_settings(self, pid: int, is_foreground: bool):
        if self.is_whitelisted(pid) or self.is_blacklisted(pid):
            return
        cached_decision = self.decision_cache.get(pid, 'settings')
        if cached_decision and cached_decision.get('is_foreground') == is_foreground:
            return
        gc_was_enabled = gc.isenabled()
        if gc_was_enabled:
            gc.disable()
        if is_foreground:
            if pid in self.minimized_processes:
                del self.minimized_processes[pid]
            if self.suspension_manager.suspended_processes.get(pid):
                self.suspension_manager.resume_process(pid)
        elif not is_foreground and pid not in self.minimized_processes:
            self.minimized_processes[pid] = time.time()
        process = psutil.Process(pid)
        process_name = process.name()
        self.profile_manager.detect_profile(process_name)
        profile_settings = self.profile_manager.get_profile_settings()
    def apply_settings_to_process_group(self, pid, is_foreground):
        if not isinstance(pid, int) or pid <= 0:
            return
        if not isinstance(is_foreground, bool):
            is_foreground = bool(is_foreground)
        main_process = psutil.Process(pid)
        process_name = main_process.name()
        if not process_name.lower().endswith('.exe'):
            return
        if self.is_whitelisted(pid) or self.is_blacklisted(pid):
            return
        pids_to_set = set()
        pids_to_set.add(pid)
        pids_to_set.update(self.get_process_children(pid))
        for p in self.get_processes_by_name(process_name):
            if psutil.Process(p).username() == main_process.username():
                pids_to_set.add(p)
    def _get_job_key(self, pid):
        p = psutil.Process(pid)
        name = p.name().lower()
        session = p.session_id()
        return (name, session)
    def _ensure_job_for_group(self, job_key, is_foreground):
        job_info = self.jobs.get(job_key)
        if not job_info:
            hJob = win32job.CreateJobObject(None, f'UPM_JOB_{job_key[0]}_{job_key[1]}')
            self.jobs[job_key] = {'handle': hJob, 'is_foreground': None}
            job_info = self.jobs[job_key]
        if job_info['is_foreground'] != is_foreground:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            if is_foreground:
                cpu_rate = 95
            elif cpu_usage < 30:
                cpu_rate = 50
            else:
                cpu_rate = 25
            info = win32job.QueryInformationJobObject(job_info['handle'], win32job.JobObjectCpuRateControlInformation)
            info['ControlFlags'] = JOB_OBJECT_CPU_RATE_CONTROL_ENABLE | JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
            info['CpuRate'] = cpu_rate * 100
            win32job.SetInformationJobObject(job_info['handle'], win32job.JobObjectCpuRateControlInformation, info)
        return job_info['handle']
    def _assign_pid_to_job(self, pid, job_handle):
        if pid in self.pid_to_job:
            return
        hProc = win32api.OpenProcess(win32con.PROCESS_SET_QUOTA | win32con.PROCESS_TERMINATE | win32con.PROCESS_SET_INFORMATION | win32con.PROCESS_QUERY_INFORMATION, False, pid)
        win32job.AssignProcessToJobObject(job_handle, hProc)
        self.pid_to_job[pid] = job_handle
    def get_ram_usage_percent(self):
        vm = psutil.virtual_memory()
        return vm.percent
    def get_standby_memory_percent(self):
        cache_info = SYSTEM_CACHE_INFORMATION()
        return_length = wintypes.DWORD()
        result = NtQuerySystemInformation(
            SystemFileCacheInformation,
            ctypes.byref(cache_info),
            ctypes.sizeof(cache_info),
            ctypes.byref(return_length)
        )
        if result == 0:
            vm = psutil.virtual_memory()
            standby_mb = cache_info.CurrentSize / (1024 * 1024)
            total_mb = vm.total / (1024 * 1024)
            return standby_mb / total_mb * 100 if total_mb > 0 else 0
        else:
            vm = psutil.virtual_memory()
            available_mb = vm.available / (1024 * 1024)
            used_mb = (vm.total - vm.available) / (1024 * 1024)
            total_mb = vm.total / (1024 * 1024)
            free_mb = vm.free / (1024 * 1024)
            standby_estimate_mb = max(0, available_mb - free_mb)
            return standby_estimate_mb / total_mb * 100 if total_mb > 0 else 0
    def clear_ram_cache(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(script_dir, 'emptystandbylist.exe')
        if os.path.exists(exe_path):
            subprocess.Popen(exe_path, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        return False
    def ram_monitor_worker(self):
        while self.ram_monitor_active:
            current_time = time.time()
            time_since_cleanup = current_time - self.last_ram_cleanup
            if time_since_cleanup >= self.ram_cleanup_cooldown:
                ram_usage = self.get_ram_usage_percent()
                standby_percent = self.get_standby_memory_percent()
                if ram_usage >= 75 and standby_percent >= 40:
                    self.clear_ram_cache()
                    self.last_ram_cleanup = current_time
                    time.sleep(self.ram_cleanup_cooldown)
                else:
                    time.sleep(60)
            else:
                remaining_cooldown = self.ram_cleanup_cooldown - time_since_cleanup
                time.sleep(min(remaining_cooldown, 60))
    def start_ram_monitor(self):
        self.ram_monitor_thread = threading.Thread(target=self.ram_monitor_worker, daemon=True, name='RamMonitorThread')
        self.ram_monitor_thread.start()
    def get_foreground_window_pid(self):
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        return None
    def clean_zombie_processes(self):
        to_del = []
        for pid in list(self.process_states.keys()):
            if not psutil.pid_exists(pid):
                to_del.append(pid)
        for pid in to_del:
            self.process_states.pop(pid, None)
            self.applied_states.pop(pid, None)
            self.pid_to_job.pop(pid, None)
            self.decision_cache.invalidate(pid)
    def _check_and_suspend_inactive_processes(self):
        current_time = time.time()
        for pid, state in list(self.process_states.items()):
            if self.is_whitelisted(pid) or self.is_blacklisted(pid):
                continue
            if not state.get('is_foreground') and pid != self.foreground_pid:
                last_foreground = self.minimized_processes.get(pid, current_time)
                if self.suspension_manager.should_suspend(pid, last_foreground):
                    if psutil.pid_exists(pid):
                        self.suspension_manager.suspend_process(pid)
    def update_all_processes(self):
        ready_tasks = self.timer_coalescer.get_tasks_to_execute()
        for task_name, urgency in ready_tasks:
            start_time = time.perf_counter()
            if task_name == 'whitelist_reload':
                self.load_whitelist()
            elif task_name == 'process_cache_update':
                current_exe_processes = self.process_snapshot.get_process_snapshot()
            elif task_name == 'zombie_cleanup':
                self.clean_zombie_processes()
            elif task_name == 'foreground_check':
                current_foreground_pid = self.get_foreground_window_pid()
                with self.lock:
                    if current_foreground_pid and current_foreground_pid != self.foreground_pid:
                        self._on_foreground_changed(current_foreground_pid)
            elif task_name == 'process_tree_rebuild':
                self.process_tree.rebuild_tree()
            elif task_name == 'handle_cache_cleanup':
                self.handle_cache.cleanup_stale_handles()
            elif task_name == 'cpu_pinning_cleanup':
                self.cpu_pinning.cleanup_dead_processes()
            elif task_name == 'decision_cache_cleanup':
                self.decision_cache.cleanup_expired()
            elif task_name == 'process_suspension_check':
                self._check_and_suspend_inactive_processes()
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000
            self.timer_coalescer.mark_executed(task_name, execution_time_ms)
        current_exe_processes = self.process_snapshot.get_process_snapshot()
        with self.lock:
            for pid, info in current_exe_processes.items():
                if self.is_whitelisted(pid) or self.is_blacklisted(pid):
                    continue
                if pid not in self.process_states:
                    is_fg = pid == self.foreground_pid
                    self.apply_settings_to_process_group(pid, is_fg)
                    self.process_states[pid] = {'name': info['name'], 'is_foreground': is_fg, 'created_at': time.time()}
            for pid in list(self.process_states.keys()):
                if pid not in current_exe_processes:
                    self.process_states.pop(pid, None)
                    self.applied_states.pop(pid, None)
                    self.pid_to_job.pop(pid, None)
    def _run_iteration(self, iteration_count: int):
        self.update_all_processes()
        if self.temp_monitor.monitoring_active:
            self.manage_thermal_throttling()
        self._run_low_frequency_tasks(iteration_count)
    def _run_low_frequency_tasks(self, iteration_count: int):
        if iteration_count % 10 == 0:
            self.adaptive_polling_mgr.adjust_polling_mode()
        if iteration_count % 20 == 0:
            self.disk_cache_tuner.tune_cache()
            self.multilevel_timer_coalescer.execute_due_tasks()
        if iteration_count % 30 == 0:
            self.tcp_congestion_tuner.detect_and_tune()
        if iteration_count % 50 == 0:
            self.memory_scrubbing_optimizer.schedule_scrubbing_low_load()
        if iteration_count % 60 == 0:
            current_latency = self.enhanced_network_stack.measure_network_latency()
            self.network_buffer_tuner.adjust_buffers_by_latency(current_latency)
        if iteration_count % 100 == 0:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent < 30:
                gc.collect(generation=0)
        if iteration_count % 100 == 0:
            self.trim_scheduler.execute_trim()
    def shutdown(self):
        self.handle_cache.close_all()
        self.timer_coalescer._deactivate_high_resolution_timer()
        self.temp_monitor.cleanup()
        self.ram_monitor_active = False
    def run(self):
        self.context_switch_reducer.adjust_quantum_time_slice(increase=True, registry_buffer=self.registry_buffer)
        self.interrupt_affinity_optimizer.optimize_interrupt_affinity()
        self.dpc_latency_controller.optimize_dpc_latency()
        self.timer_coalescer.register_task('thermal_check', interval_ms=3000, priority=7)
        self.network_interrupt_coalescer.optimize_interrupt_coalescing()
def main() -> None:
    debug_enabled = enable_debug_privilege()
    manager = UnifiedProcessManager(debug_privilege_enabled=debug_enabled)
    manager_thread = threading.Thread(target=manager.run, daemon=True, name='ProcessManager')
    manager_thread.start()
    tray = SystemTrayManager(manager, manager.temp_monitor)
    tray.run()
if __name__ == '__main__':
    main()