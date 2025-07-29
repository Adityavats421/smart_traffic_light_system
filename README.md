# AI Traffic Light System

An intelligent traffic light simulation system with emergency vehicle priority and adaptive signal timing.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-traffic-light-system.git
cd ai-traffic-light-system
```

### 2. Install Dependencies
```bash
python setup.py
```
Or manually:
```bash
pip install -r requirements.txt
```

### 3. Run the Simulation
```bash
python run.py
```
Or directly:
```bash
python ai_traffic_simulation.py
```

## 🎮 What You'll See

- **4-way intersection** with traffic lights
- **Multiple vehicle types**: cars, buses, trucks, rickshaws, bikes, emergency vehicles
- **Real-time vehicle count** display
- **Signal timers** showing countdown
- **Emergency vehicle priority** system
- **Adaptive timing** based on traffic density

## ✨ Features

- **Real-time Traffic Simulation**: 4-way intersection with multiple vehicle types
- **Emergency Vehicle Priority**: Automatic signal switching for emergency vehicles (prioritizes earliest arrival)
- **Adaptive Signal Timing**: Dynamic green time calculation based on vehicle count
- **Multiple Vehicle Types**: Cars, buses, trucks, rickshaws, bikes, and emergency vehicles
- **Visual Simulation**: Pygame-based graphical interface
- **Performance Metrics**: Tracks waiting times and throughput

## 🚗 Vehicle Types

- **Car**: Standard passenger vehicle
- **Bus**: Large passenger vehicle
- **Truck**: Heavy goods vehicle  
- **Rickshaw**: Three-wheeled vehicle
- **Bike**: Two-wheeled vehicle
- **Emergency**: Priority vehicle (ambulance, fire truck, etc.)

## 🎯 Key Features

- **Emergency Priority**: Emergency vehicles automatically get green light based on arrival time
- **Smart Timing**: Green time adapts to number of waiting vehicles using formula: `8 + 1.0 * (waiting_count ^ 0.85)`
- **Visual Feedback**: Real-time display of vehicle counts and timers
- **Performance Tracking**: Metrics saved to `output/emerg_results.json`

## ⚙️ How It Works

### Signal Control Algorithm
The system uses a priority-based algorithm that considers:
- Number of waiting vehicles
- Waiting time for each lane
- Emergency vehicle presence (prioritizes earliest arrival)
- Vehicle type distribution

### Emergency Vehicle Priority
- Emergency vehicles get automatic priority
- Signals switch immediately when emergency vehicles are detected
- **NEW**: Prioritizes the earliest arriving emergency vehicle, not just count
- Multiple emergency vehicles are handled by arrival time priority

### Adaptive Timing
- Green time is calculated using the formula: `8 + 1.0 * (waiting_count ^ 0.85)`
- Minimum green time: 10 seconds
- Maximum green time: 60 seconds

## 🚦 Controls

- **Close Window**: Click X to exit
- **Simulation**: Runs automatically for the set duration (default: 300 seconds)

## 📊 Output

The simulation generates:
- Real-time vehicle count display
- Signal timer display
- Performance metrics in `output/emerg_results.json`

After simulation ends, check `output/emerg_results.json` for:
- Total vehicles passed
- Average waiting time
- Lane-wise statistics
- Performance metrics

## ⚙️ Configuration

Key parameters can be modified in `ai_traffic_simulation.py`:
- `SIM_TIME`: Total simulation duration (default: 300 seconds)
- `DEFAULT_RED/YELLOW/GREEN`: Default signal timings
- `speeds`: Vehicle movement speeds
- `gap`: Vehicle spacing

## 📁 Project Structure

```
ai-traffic-light-system/
├── ai_traffic_simulation.py  # Main simulation file
├── run.py                   # Quick run script
├── setup.py                 # Installation helper
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
├── images/                 # Graphics assets
│   ├── mod_int.png        # Intersection background
│   ├── signals/           # Traffic signal images
│   └── [direction]/       # Vehicle images by direction
└── output/                # Generated results
```

## 🐛 Troubleshooting

**Pygame not found:**
```bash
pip install pygame
```

**Permission errors:**
```bash
chmod +x run.py setup.py
```

**Image loading errors:**
Make sure all image files are in the correct directories under `images/`

**Common Issues:**
1. Check that all dependencies are installed
2. Verify image files are in place
3. Ensure Python 3.7+ is being used
4. Check the console for error messages

## 📋 Requirements

- Python 3.7+
- Pygame
- See `requirements.txt` for complete list

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Pygame for the graphics engine
- Open source community for inspiration

---

**Enjoy the AI Traffic Light Simulation! 🚦**
