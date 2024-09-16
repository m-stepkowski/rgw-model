# Rabbits Grass Weeds Multiagent Model

## Overview

This project implements the Rabbits Grass Weeds multiagent model in Python. It simulates the interaction between rabbits, grass, and weeds in a 2D environment, exploring population dynamics and resource management. The project is based on the paper "Multi-agent model of the interaction between rabbits, grass, and weeds" by Wacław Kowalski and Andrzej Skowron and was prepared as a part of "Mutli-agent modeling" classes at Warsaw School of Economics.

## Model Description

The Rabbits Grass Weeds model simulates an ecosystem with three main components:

1. Rabbits: Mobile agents that consume grass and weeds for energy.
2. Grass: Stationary agents that provide energy to rabbits.
3. Weeds: Stationary agents that provide less energy to rabbits compared to grass.

The simulation takes place on a 2D grid where these agents interact over time.

## Key Features

- Rabbits move, eat, reproduce, and die based on their energy levels.
- Grass and weeds grow randomly with specified probabilities.
- The environment is toroidal (wraps around at the edges).
- Configurable parameters for initial conditions and agent behaviors.

## Implementation Details

### Classes

1. `Rabbit`: Represents rabbit agents with methods for movement, eating, reproduction, and death.
2. `Agent`: Represents stationary agents (grass and weeds) with a method for reproduction.
3. `City`: Manages the overall simulation environment and agent interactions.

### Simulation Process

1. Initialize the environment with rabbits, grass, and weeds.
2. For each time step:
   - Rabbits move and attempt to eat.
   - Rabbits may reproduce if they have sufficient energy.
   - Grass and weeds may grow in empty spaces.
   - Rabbits die if their energy depletes.
3. The simulation runs for a specified number of iterations.

### Parameters

The model includes various configurable parameters:

- Map dimensions
- Initial densities of grass and weeds
- Rabbit energy levels and reproduction thresholds
- Probabilities for grass and weed growth
- Energy gained from consuming grass or weeds

## Usage

To run the simulation:

1. Ensure you have the required dependencies installed (SimPy, Pandas, Matplotlib, NumPy).
2. Adjust the parameters in the script as needed.
3. Run the script to execute the simulation.
4. The results will be saved in a CSV file for further analysis.
5. An example [R script](rabbit.R) is provided for analysis.

## Visualization

The script includes functionality to visualize the initial and final states of the simulation using Matplotlib.

## Data Analysis

The simulation generates data on rabbit population dynamics under various environmental conditions. This data can be analyzed to understand the relationships between resource availability, rabbit energy levels, and population growth.

## Future Enhancements

- Implement more sophisticated movement and decision-making algorithms for rabbits.
- Add seasonal variations in grass and weed growth.
- Introduce predators or other environmental factors.
- Develop a user interface for easier parameter adjustment and real-time visualization.

## Dependencies

- Python 3.12+
- SimPy
- Pandas
- Matplotlib
- NumPy

## Example usage

```bash
poetry shell
poetry install
python rabbit.py
```

## License

MIT

## Contributors

Maciej Stepkowski [@m-stepkowski](https://github.com/m-stepkowski)