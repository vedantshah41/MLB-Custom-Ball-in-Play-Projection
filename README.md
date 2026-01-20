# MLB Hitter vs Stadium Comparison Project

A comprehensive Python project that analyzes how every MLB hitter's balls in play characteristics match up against every Major League Baseball stadium.

## Features

- **Complete MLB Hitter Database**: Fetches data for all MLB hitters with configurable minimum plate appearance requirements
- **All 30 MLB Stadiums**: Includes dimensions, park factors, and other relevant stadium characteristics
- **Balls in Play Analysis**: Analyzes exit velocity, launch angle, hard-hit rate, and other key metrics
- **Match Scoring System**: Calculates how well each hitter's profile matches each stadium
- **Comprehensive Comparisons**: Generates detailed comparisons between all hitters and all stadiums
- **Interactive Tool**: Ask for a player, select a stadium by number, view expected stats and xBA heatmap
- **Visual Heatmaps**: Beautiful visualizations showing all balls in play colored by expected batting average (xBA)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd MLBPlayerProjection
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode (Recommended)

Run the interactive tool to select a player and stadium, then view expected stats and heatmap:
```bash
python interactive.py
```

This will:
1. Ask you to enter a player name
2. Show a numbered list of all 30 MLB stadiums
3. Let you select a stadium by number
4. Display expected statistics for that player-stadium combination
5. Generate a heatmap visualization showing all balls in play colored by xBA (expected batting average)

### Batch Analysis Mode

Run a full comparison of all hitters against all stadiums:
```bash
python main.py --year 2024 --min-pa 100
```

### Command Line Options

- `--year`: Year to analyze (default: 2024)
- `--min-pa`: Minimum plate appearances required (default: 100)
- `--top-n`: Only analyze top N hitters by plate appearances
- `--output`: Output CSV file name (default: comparisons.csv)
- `--hitter`: Analyze specific hitter by name
- `--list-stadiums`: List all stadiums and exit
- `--list-hitters`: List all hitters and exit

### Examples

**Compare all hitters from 2023:**
```bash
python main.py --year 2023 --min-pa 150
```

**Analyze only top 50 hitters:**
```bash
python main.py --year 2024 --top-n 50
```

**Find best stadium matches for a specific hitter:**
```bash
python main.py --year 2024 --hitter "Mike Trout"
```

**List all available stadiums:**
```bash
python main.py --list-stadiums
```

**List all hitters:**
```bash
python main.py --list-hitters
```

## Project Structure

```
MLBPlayerProjection/
├── src/
│   ├── __init__.py
│   ├── hitter_data.py      # Functions to fetch and process hitter data
│   ├── stadiums.py          # Stadium data and information
│   ├── comparison.py        # Comparison and analysis functions
│   └── visualization.py    # Heatmap and visualization functions
├── main.py                  # Batch analysis script
├── interactive.py           # Interactive player-stadium comparison tool
├── example.py               # Example usage scripts
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Data Sources

- **Hitter Data**: Uses `pybaseball` library to fetch MLB statistics from FanGraphs and Statcast
- **Stadium Data**: Includes manually curated stadium dimensions and park factors

## Output

### Interactive Mode Output

When using `interactive.py`, you'll get:
- **Expected Statistics**: Park-adjusted batting average, slugging percentage, OPS, and HR rate
- **Stadium Match Analysis**: Overall match score and detailed breakdown
- **Heatmap Visualization**: PNG image showing all balls in play on a baseball field, colored by xBA (expected batting average)
  - Red circles = low xBA
  - Green circles = high xBA
  - Stadium fence overlay showing dimensions

### Batch Mode Output

The batch analysis generates a CSV file with the following information for each hitter-stadium combination:

- Player information (name, ID)
- Stadium information (name, team, dimensions, park factor)
- Match scores (exit velocity score, hard-hit score, distance score, overall match score)
- Expected performance metrics

## Analysis Metrics

The comparison uses several key metrics:

1. **Exit Velocity Score**: How hitter's exit velocity interacts with park factors
2. **Hard-Hit Rate**: Percentage of balls hit at 95+ mph
3. **Distance Score**: Expected home run potential based on average distance
4. **Park Factor**: Calculated value, based off the stadium's historical tendency to favor hitters or pitchers
5. **Overall Match Score**: Weighted combination of all factors

## Notes

- Data fetching may take some time depending on the number of hitters analyzed
- The script includes rate limiting to avoid overwhelming data sources
- Some hitters may not have complete Statcast data available
- Park factors are approximate and based on historical data

## Requirements

- Python 3.8+
- See `requirements.txt` for full list of dependencies

## License

