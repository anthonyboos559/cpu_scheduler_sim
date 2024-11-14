import os
import sys
import heapq
import random

from enum import Enum
from collections import deque

class EventType(Enum):
    NEW_PROCESS = 0
    PROCESS_READY = 1
    PROCESS_RUNNING = 2
    PROCESS_BLOCKED = 3
    PROCESS_TERMINATED = 4
    PROCESS_PREEMPTED = 5

class Process:
    ID = 5
    def __init__(self, arrival, bursts, io) -> None:
        self.arrival = arrival
        self.bursts = bursts
        self.io = io
        self.current_burst = 0
        self.current_io = 0
        self.burst_remain = self.bursts[self.current_burst]
        self.io_remain = self.io[self.current_io] if io else None
        self.pid = Process.ID
        Process.ID += random.randint(1,50)
    
    def is_last_cpu(self):
        return len(self.bursts) - 1 == self.current_burst
    
    def is_last_io(self):
        return len(self.io) == self.current_io
    
    def next_burst(self):
        self.current_burst += 1
        if not self.is_last_cpu():
            self.burst_remain = self.bursts[self.current_burst]
        else:
            self.burst_remain = 0

    def next_io(self):
        self.current_io += 1
        if not self.is_last_io():
            self.io_remain = self.io[self.current_io]
        else:
            self.io_remain = 0

class Event:
    def __init__(self, type, time, process):
        self.type = type
        self.time = time
        self.process = process
    
    def __lt__(self, other):
        return self.time < other.time

def main(input, quantum):
    events = []
    with open(input, "r") as file:
        for line in file:
            line = line.strip()
            vals = line.split(" ")
            arrival = int(vals.pop(0))
            n_bursts = int(vals.pop(0))
            bursts = []
            io = []
            for i in range(len(vals)):
                if i % 2 == 0:
                    bursts.append(int(vals[i]))
                else:
                    io.append(int(vals[i]))
            heapq.heappush(events, (arrival, Event(EventType.NEW_PROCESS, arrival, Process(arrival, bursts, io))))

    ready_queue = deque()
    in_cpu = None
    cpu_idle = 0
    cpu_empty_at = 0
    tat = []
    wt = []
    while True:
        time, ev = heapq.heappop(events)
        if ev.type == EventType.NEW_PROCESS:
            print(f"Time: {time} - New process ID: {ev.process.pid} created")
            ready_queue.appendleft(ev.process)

        elif ev.type == EventType.PROCESS_READY:
            print(f"Time: {time} - Process ID: {ev.process.pid} ready")
            ready_queue.appendleft(ev.process)
            ev.process.next_io()

        elif ev.type == EventType.PROCESS_RUNNING:
            print(f"Time: {time} - Process ID: {ev.process.pid} running")
            if not cpu_empty_at == time:
                cpu_idle += time - cpu_empty_at
            in_cpu = ev.process
            burst = ev.process.burst_remain
            if burst > quantum:
                heapq.heappush(events, (time + quantum, Event(EventType.PROCESS_PREEMPTED, time + quantum, ev.process)))
            elif ev.process.is_last_cpu():
                heapq.heappush(events, (time + burst, Event(EventType.PROCESS_TERMINATED, time + burst, ev.process)))
            else:
                heapq.heappush(events, (time + burst, Event(EventType.PROCESS_BLOCKED, time + burst, ev.process)))

        elif ev.type == EventType.PROCESS_BLOCKED:
            print(f"Time: {time} - Process ID: {ev.process.pid} blocked")
            print(f"Time: {time} - Process ID: {ev.process.pid} io starting")
            ev.process.next_burst()
            heapq.heappush(events, (time + ev.process.io_remain, Event(EventType.PROCESS_READY, time + ev.process.io_remain, ev.process)))
            in_cpu = None
            cpu_empty_at = time
            
        elif ev.type == EventType.PROCESS_TERMINATED:
            print(f"Time: {time} - Process ID: {ev.process.pid} terminated")
            turnaround = time - ev.process.arrival
            wait = turnaround - sum(ev.process.bursts)
            tat.append(turnaround)
            wt.append(wait)
            print(f"Time: {time} - Turn-Around-Time: {turnaround} Wait time: {wait}")
            in_cpu = None
            cpu_empty_at = time
        
        elif ev.type == EventType.PROCESS_PREEMPTED:
            print(f"Time: {time} - Process ID: {ev.process.pid} preempted")
            ev.process.burst_remain -= quantum
            ready_queue.appendleft(ev.process)
            in_cpu = None
            cpu_empty_at = time

        else:
            print("ERROR ERROR ERROR!!!!!! INVALID EVENT FOUND???!?!?!?!?")

        if in_cpu is None and len(ready_queue) > 0:
            heapq.heappush(events, (ev.time, Event(EventType.PROCESS_RUNNING, ev.time, ready_queue.pop())))
        
        if len(events) == 0:
            break

    cpu_use = (time - cpu_idle) / time
    avg_tat = sum(tat) / len(tat) if len(tat) > 0 else 0
    avg_wt = sum(wt) / len(wt) if len(wt) > 0 else 0
    print(f"Time: {time} - Avg CPU utilization: {cpu_use:.2f}% - Avg TAT: {avg_tat:.2f} - Avg WT: {avg_wt:.2f}")

if __name__ == '__main__':
    input = sys.argv[1]
    quantum = int(sys.argv[2])
    main(input, quantum)