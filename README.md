# 🖥️ Operating System Simulator

An interactive **Operating System Simulator** built with **Python** and **PyQt6** that demonstrates fundamental Operating System concepts including **CPU Scheduling**, **Virtual Memory Management**, **Page Replacement Algorithms**, and **Process Management** through a graphical user interface.

## 📌 Features

### ✅ CPU Scheduling Algorithms
- Round Robin (RR)
- First Come First Serve (FCFS)
- Shortest Job First (SJF)
- Priority Scheduling

### ✅ Virtual Memory Management
- Page Frame Simulation
- FIFO Page Replacement
- LRU (Least Recently Used) Page Replacement
- Page Fault Tracking

### ✅ Process Management
- Create multiple processes
- Configure:
  - Burst Time
  - Arrival Time
  - Number of Memory Pages
  - Priority
- Monitor process states:
  - Ready
  - Running
  - Terminated

### ✅ Visualization
- Dynamic CPU Gantt Chart
- Color-coded Process Execution
- Memory Frame Usage Display
- Page Fault Counter
- Process Status Table

### ✅ Simulation Controls
- Start Simulation
- Pause / Resume
- Reset Simulation
- Clear All Processes
- Export Simulation Logs

# 🛠️ Technologies Used

- Python 3.x
- PyQt6
- Matplotlib
- Collections (deque, OrderedDict)
- Object-Oriented Programming (OOP)

# 📂 Project Structure

```
OSProjectFinal.py
README.md
```

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/os-simulator.git
```

Move into the project folder.

```bash
cd os-simulator
```

## 2. Install Dependencies

```bash
pip install PyQt6 matplotlib
```

## 3. Run the Project

```bash
python OSProjectFinal.py
```

# 🚀 How to Use

1. Launch the application.
2. Add one or more processes.
3. Enter:
   - Burst Time
   - Arrival Time
   - Memory Pages
   - Priority
4. Select a CPU Scheduling Algorithm.
5. Choose a Page Replacement Algorithm.
6. Press **Start**.
7. Observe:
   - CPU execution
   - Gantt Chart
   - Process Table
   - Memory Frames
   - Page Faults
8. Export logs if required.

# 🧠 Scheduling Algorithms

## Round Robin (RR)

- Uses Time Quantum
- Fair CPU allocation
- Suitable for Time Sharing Systems

## First Come First Serve (FCFS)

- Executes processes in order of arrival.

## Shortest Job First (SJF)

- Executes the process with the smallest burst time first.

## Priority Scheduling

- Executes processes according to priority.
- Lower priority number means higher priority.

# 💾 Page Replacement Algorithms

## FIFO

Removes the page that entered memory first.

## LRU

Removes the page that has not been used for the longest period.

# 📊 Simulation Outputs

The simulator provides:

- Live CPU Execution
- Interactive Gantt Chart
- Process Table
- Process State Updates
- Memory Frame Status
- Page Fault Counter
- Simulation Logs

# 🎯 Learning Objectives

This project helps understand:

- CPU Scheduling
- Process Scheduling
- Process States
- Time Sharing
- Virtual Memory
- Page Replacement
- Page Fault Handling
- Memory Management
- Operating System Fundamentals

# 📚 Future Improvements

- Multilevel Queue Scheduling
- Multilevel Feedback Queue
- Preemptive Priority Scheduling
- Disk Scheduling Algorithms
- Deadlock Detection
- Banker’s Algorithm
- Memory Allocation Algorithms
- Multi-threading Simulation
- Performance Statistics Dashboard
- Dark Mode UI

## ⭐ If you like this project

Give this repository a ⭐ on GitHub to support the project!
