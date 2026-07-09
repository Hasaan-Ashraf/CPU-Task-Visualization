import sys
import random
import datetime
import matplotlib.patches as mpatches
from collections import deque, OrderedDict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QProgressBar, QSpinBox
)
from PyQt6.QtCore import QTimer, Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Process states
STATE_READY = "Ready"
STATE_RUNNING = "Running"
STATE_WAITING = "Waiting"
STATE_TERMINATED = "Terminated"

# Page replacement algorithms
PAGE_REPLACEMENT_ALGORITHMS = ["FIFO", "LRU"]

# Scheduling algorithms
SCHEDULING_ALGORITHMS = ["Round Robin", "FCFS", "SJF", "Priority"]

class Process:
    def __init__(self, pid, burst_time, arrival_time, pages, priority=1):
        self.pid = pid
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.arrival_time = arrival_time
        self.pages = pages
        self.priority = priority
        self.state = STATE_READY
        self.start_time = None
        self.finish_time = None
        # For thread simulation (optional)
        self.threads = []  # List of (thread_id, burst_time, remaining_time)
        self.current_thread = 0

class VirtualMemoryManager:
    def __init__(self, total_frames=10, replacement_algo="FIFO"):
        self.total_frames = total_frames
        self.frames = []  # List of (pid, page_number)
        self.page_table = {}  # pid -> list of pages in frames
        self.replacement_algo = replacement_algo
        self.fifo_queue = deque()
        self.lru_dict = OrderedDict()
        self.page_faults = 0

    def access_page(self, pid, page):
        # Check if page is already in frames
        if (pid, page) in self.frames:
            if self.replacement_algo == "LRU":
                # Move to end to mark recently used
                if (pid, page) in self.lru_dict:
                    self.lru_dict.move_to_end((pid, page))
            return False  # No page fault

        # Page fault occurs
        self.page_faults += 1

        if len(self.frames) < self.total_frames:
            self.frames.append((pid, page))
            if self.replacement_algo == "FIFO":
                self.fifo_queue.append((pid, page))
            elif self.replacement_algo == "LRU":
                self.lru_dict[(pid, page)] = True
        else:
            # Need to replace a page
            if self.replacement_algo == "FIFO":
                to_remove = self.fifo_queue.popleft()
                self.frames.remove(to_remove)
                self.frames.append((pid, page))
                self.fifo_queue.append((pid, page))
            elif self.replacement_algo == "LRU":
                to_remove = next(iter(self.lru_dict))
                self.lru_dict.pop(to_remove)
                self.frames.remove(to_remove)
                self.frames.append((pid, page))
                self.lru_dict[(pid, page)] = True
        return True

    def reset(self):
        self.frames.clear()
        self.page_table.clear()
        self.fifo_queue.clear()
        self.lru_dict.clear()
        self.page_faults = 0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.colors = {}  # Dictionary to store colors assigned to each process

        self.setWindowTitle("OS Simulator - CPU Scheduling + Virtual Memory")
        self.processes = []
        self.time = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.run_simulation_step)
        self.is_running = False
        self.is_paused = False

        # Default configurations
        self.time_quantum = 4
        self.virtual_memory = VirtualMemoryManager(total_frames=10)
        self.scheduling_algorithm = "Round Robin"

        # For scheduling logic
        self.ready_queue = deque()
        self.current_process = None
        self.quantum_counter = 0

        # For logs and UI updates
        self.logs = []

        # Build UI
        self.build_ui()

    def build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left: Inputs and controls
        left_panel = QVBoxLayout()

        # Process inputs
        left_panel.addWidget(QLabel("<b>Add New Process</b>"))

        self.burst_time_input = QSpinBox()
        self.burst_time_input.setRange(1, 1000)
        self.burst_time_input.setValue(5)
        left_panel.addWidget(QLabel("Burst Time:"))
        left_panel.addWidget(self.burst_time_input)

        self.arrival_time_input = QSpinBox()
        self.arrival_time_input.setRange(0, 1000)
        self.arrival_time_input.setValue(0)
        left_panel.addWidget(QLabel("Arrival Time:"))
        left_panel.addWidget(self.arrival_time_input)

        self.pages_input = QSpinBox()
        self.pages_input.setRange(1, 20)
        self.pages_input.setValue(3)
        left_panel.addWidget(QLabel("Memory Pages:"))
        left_panel.addWidget(self.pages_input)

        self.priority_input = QSpinBox()
        self.priority_input.setRange(1, 10)
        self.priority_input.setValue(1)
        left_panel.addWidget(QLabel("Priority (1=highest):"))
        left_panel.addWidget(self.priority_input)

        add_process_btn = QPushButton("Add Process")
        add_process_btn.clicked.connect(self.add_process)
        left_panel.addWidget(add_process_btn)

        # Scheduling Algorithm selection
        left_panel.addWidget(QLabel("<b>Scheduling Algorithm</b>"))
        self.alg_combo = QComboBox()
        self.alg_combo.addItems(SCHEDULING_ALGORITHMS)
        self.alg_combo.currentTextChanged.connect(self.algorithm_changed)
        left_panel.addWidget(self.alg_combo)

        # Time Quantum (only for RR)
        left_panel.addWidget(QLabel("Time Quantum (for Round Robin):"))
        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 100)
        self.quantum_input.setValue(self.time_quantum)
        self.quantum_input.valueChanged.connect(self.quantum_changed)
        left_panel.addWidget(self.quantum_input)

        # Page Replacement Algorithm
        left_panel.addWidget(QLabel("<b>Page Replacement Algorithm</b>"))
        self.page_replacement_combo = QComboBox()
        self.page_replacement_combo.addItems(PAGE_REPLACEMENT_ALGORITHMS)
        self.page_replacement_combo.currentTextChanged.connect(self.page_replacement_changed)
        left_panel.addWidget(self.page_replacement_combo)

        # Memory frames display
        self.memory_label = QLabel("Memory Frames: 0/10 (Page Faults: 0)")
        left_panel.addWidget(self.memory_label)

        # Controls: Start, Pause, Reset, Clear
        controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_simulation)
        controls_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_resume_simulation)
        controls_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_simulation)
        controls_layout.addWidget(self.reset_button)

        self.clear_button = QPushButton("Clear Processes")
        self.clear_button.clicked.connect(self.clear_processes)
        controls_layout.addWidget(self.clear_button)

        left_panel.addLayout(controls_layout)

        # Logs
        left_panel.addWidget(QLabel("<b>Simulation Logs</b>"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        left_panel.addWidget(self.log_text)

        # Export logs
        export_log_btn = QPushButton("Export Logs")
        export_log_btn.clicked.connect(self.export_logs)
        left_panel.addWidget(export_log_btn)

        main_layout.addLayout(left_panel, 3)

        # Right: Gantt chart and process table
        right_panel = QVBoxLayout()

        # Gantt chart
        self.figure = Figure(figsize=(8,4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("CPU Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        self.ax.grid(True)
        self.canvas = FigureCanvas(self.figure)
        right_panel.addWidget(self.canvas, 3)

        # Process Table
        right_panel.addWidget(QLabel("<b>Processes</b>"))
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(7)
        self.process_table.setHorizontalHeaderLabels(
            ["PID", "Burst", "Remaining", "Arrival", "Pages", "Priority", "State"]
        )
        right_panel.addWidget(self.process_table, 2)

        main_layout.addLayout(right_panel, 5)

    def add_process(self):
        try:
            burst_time = int(self.burst_time_input.text())
            arrival_time = int(self.arrival_time_input.text())
            pages = int(self.pages_input.text())
            priority = int(self.priority_input.text())

            pid = len(self.processes) + 1
            new_process = Process(pid, burst_time, arrival_time, pages, priority)
            self.processes.append(new_process)

            # Assign a unique color to the process
            color = f"#{random.randint(0, 0xFFFFFF):06x}"
            self.colors[new_process.pid] = color

            self.log(f"Added Process P{new_process.pid} (Arrival: {arrival_time}, Burst: {burst_time}, Pages: {pages}, Priority: {priority})")
            self.update_process_table()
            self.burst_time_input.clear()
            self.arrival_time_input.clear()
            self.pages_input.clear()
            self.priority_input.clear()
        except ValueError:
            self.log("Invalid input: Please enter integer values.")

    def update_process_table(self):
        self.process_table.setRowCount(len(self.processes))
        for i, p in enumerate(self.processes):
            self.process_table.setItem(i, 0, QTableWidgetItem(f"P{p.pid}"))
            self.process_table.setItem(i, 1, QTableWidgetItem(str(p.burst_time)))
            self.process_table.setItem(i, 2, QTableWidgetItem(str(p.remaining_time)))
            self.process_table.setItem(i, 3, QTableWidgetItem(str(p.arrival_time)))
            self.process_table.setItem(i, 4, QTableWidgetItem(str(p.pages)))
            self.process_table.setItem(i, 5, QTableWidgetItem(str(p.priority)))
            self.process_table.setItem(i, 6, QTableWidgetItem(p.state))

    def algorithm_changed(self, text):
        self.scheduling_algorithm = text
        self.log(f"Scheduling algorithm set to {text}")
        self.quantum_input.setEnabled(text == "Round Robin")

    def quantum_changed(self, val):
        self.time_quantum = val
        self.log(f"Time quantum set to {val}")

    def page_replacement_changed(self, text):
        self.virtual_memory.replacement_algo = text
        self.virtual_memory.reset()
        self.log(f"Page replacement algorithm set to {text}")

    def start_simulation(self):
        if not self.processes:
            QMessageBox.warning(self, "No processes", "Please add at least one process to start.")
            return
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self.time = 0
        self.ready_queue.clear()
        self.current_process = None
        self.quantum_counter = 0
        self.virtual_memory.reset()
        self.logs.clear()
        self.log_text.clear()
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.state = STATE_READY
            p.start_time = None
            p.finish_time = None
        self.update_process_table()
        self.timer.start()
        self.log("Simulation started.")

    def pause_resume_simulation(self):
        if not self.is_running:
            return
        if self.is_paused:
            self.timer.start()
            self.pause_button.setText("Pause")
            self.is_paused = False
            self.log("Simulation resumed.")
        else:
            self.timer.stop()
            self.pause_button.setText("Resume")
            self.is_paused = True
            self.log("Simulation paused.")

    def reset_simulation(self):
        if self.is_running:
            self.timer.stop()
        self.is_running = False
        self.is_paused = False
        self.time = 0
        self.ready_queue.clear()
        self.current_process = None
        self.quantum_counter = 0
        self.virtual_memory.reset()
        self.logs.clear()
        self.log_text.clear()
        self.ax.clear()
        self.ax.set_title("CPU Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        self.ax.grid(True)
        self.canvas.draw()
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.state = STATE_READY
            p.start_time = None
            p.finish_time = None
        self.update_process_table()
        self.pause_button.setText("Pause")
        self.log("Simulation reset.")

    def clear_processes(self):
        self.reset_simulation()
        self.processes.clear()
        self.update_process_table()
        self.log("All processes cleared.")

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        self.log_text.append(log_entry)

    def export_logs(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Logs", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, "w") as f:
                    f.write("\n".join(self.logs))
                QMessageBox.information(self, "Success", f"Logs saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save logs: {e}")

    def update_gantt_chart(self, current_pid):
        if current_pid is None:
            return

        color = self.colors.get(current_pid, "#000000")  # Fallback to black
        bar = self.ax.barh(0, 1, left=self.time, color=color, edgecolor='black', height=0.5)
        
        # Add process name label to the bar
        self.ax.text(self.time + 0.5, 0, f"P{current_pid}", 
                    ha='center', va='center', color='white', fontweight='bold')

        # Update the x-axis range to show the full chart
        self.ax.set_xlim(0, self.time + 5)  # Add padding for visibility

        # Redraw the canvas
        self.canvas.draw()

        # Clear previous legend
        if self.ax.get_legend():
            self.ax.get_legend().remove()

        # Create legend handles
        legend_handles = []
        for pid, color in self.colors.items():
            patch = mpatches.Patch(color=color, label=f"P{pid}")
            legend_handles.append(patch)

        self.ax.legend(handles=legend_handles, title="Processes")
        self.canvas.draw()

    def get_color_for_pid(self, pid):
        random.seed(pid)
        r = random.random()
        g = random.random()
        b = random.random()
        return (r, g, b)

    def run_simulation_step(self):
        self.time += 1
        self.log(f"Time: {self.time}")

        # Add arrived processes to ready queue
        for p in self.processes:
            if p.arrival_time == self.time - 1 and p.state == STATE_READY:
                self.ready_queue.append(p)
                self.log(f"Process P{p.pid} arrived and added to ready queue.")

        if self.current_process is None or self.current_process.state == STATE_TERMINATED:
            # Pick next process based on scheduling algorithm
            self.current_process = self.pick_next_process()
            self.quantum_counter = 0
            if self.current_process:
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.time
                self.current_process.state = STATE_RUNNING
                self.log(f"Process P{self.current_process.pid} started running.")
                self.update_process_table()  # Update table when process starts running

        if self.current_process:
            # Access virtual memory pages for this process
            for page in range(1, self.current_process.pages + 1):
                fault = self.virtual_memory.access_page(self.current_process.pid, page)
                if fault:
                    self.log(f"Page fault for Process P{self.current_process.pid} page {page}")

            # Run one unit of burst time
            self.current_process.remaining_time -= 1
            self.quantum_counter += 1
            self.update_gantt_chart(self.current_process.pid)
            self.memory_label.setText(f"Memory Frames: {len(self.virtual_memory.frames)}/{self.virtual_memory.total_frames} (Page Faults: {self.virtual_memory.page_faults})")

            if self.current_process.remaining_time == 0:
                self.current_process.state = STATE_TERMINATED
                self.current_process.finish_time = self.time
                self.log(f"Process P{self.current_process.pid} terminated at time {self.time}")
                self.update_process_table()  # Update table immediately when process terminates
                self.current_process = None
                self.quantum_counter = 0
            else:
                # Check quantum for RR
                if self.scheduling_algorithm == "Round Robin":
                    if self.quantum_counter >= self.time_quantum:
                        self.current_process.state = STATE_READY
                        self.ready_queue.append(self.current_process)
                        self.log(f"Time quantum expired for Process P{self.current_process.pid}, moved back to ready queue.")
                        self.update_process_table()  # Update table when process moves to ready
                        self.current_process = None
                        self.quantum_counter = 0

        else:
            # CPU idle
            self.log("CPU is idle.")

        # Update process table at the end of each step
        self.update_process_table()

        # If all processes terminated, stop timer
        if all(p.state == STATE_TERMINATED for p in self.processes):
            self.log("All processes completed. Stopping simulation.")
            self.timer.stop()
            self.is_running = False

    def pick_next_process(self):
        # Pick next process based on scheduling algorithm
        if not self.ready_queue:
            return None

        if self.scheduling_algorithm == "FCFS":
            # Pick earliest arrival
            proc = min(self.ready_queue, key=lambda p: p.arrival_time)
            self.ready_queue.remove(proc)
            return proc

        elif self.scheduling_algorithm == "SJF":
            # Pick shortest remaining burst time
            proc = min(self.ready_queue, key=lambda p: p.remaining_time)
            self.ready_queue.remove(proc)
            return proc

        elif self.scheduling_algorithm == "Priority":
            # Pick highest priority (lowest number)
            proc = min(self.ready_queue, key=lambda p: p.priority)
            self.ready_queue.remove(proc)
            return proc

        elif self.scheduling_algorithm == "Round Robin":
            # FIFO queue behavior
            proc = self.ready_queue.popleft()
            return proc

        else:
            # Default FCFS
            proc = self.ready_queue.popleft()
            return proc

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1100, 700)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
