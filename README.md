# Humanoid Robot — ROS 2 Simulation

A custom 18-DOF humanoid robot modeled in URDF and simulated in Gazebo Classic on ROS 2 Humble. Built as a hands-on project to learn ROS 2 and robotics simulation by building and debugging a real robot stack, rather than following tutorials end-to-end.

## Current status

- [x] Custom humanoid URDF — pelvis, torso, head, bilateral arms, bilateral legs
- [x] Gazebo Classic simulation launch (`gazebo.launch.py`)
- [x] RViz visualization launch with joint sliders (`display.launch.py`)
- [ ] `ros2_control` integration for joint control
- [ ] Simulated sensors (IMU, camera, lidar)
- [ ] Navigation (Nav2)
- [ ] Manipulation (MoveIt2)
- [ ] Perception pipeline

## Package structure

```
robot_ws/
└── src/
    └── robot_description/       # ament_python package
        ├── urdf/
        │   └── robot.urdf       # humanoid robot model
        ├── launch/
        │   ├── gazebo.launch.py     # spawns robot in Gazebo Classic
        │   └── display.launch.py    # RViz + joint_state_publisher_gui
        └── robot_description/       # Python package (currently empty, reserved for future nodes)
```

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic (`gazebo_ros` packages)
- `joint_state_publisher_gui` (for the RViz display launch)

## Build

```bash
cd ~/robot_ws
colcon build --packages-select robot_description
source install/setup.bash
```

## Run

**View the robot in RViz with manual joint control:**
```bash
ros2 launch robot_description display.launch.py
```

**Spawn the robot in Gazebo:**
```bash
ros2 launch robot_description gazebo.launch.py
```

## Notes from building this

Details on specific bugs encountered and how they were resolved will be added here as the project grows — e.g. resolving `robot_state_publisher`'s handling of the URDF kinematic tree, and the `ament_python` `data_files` requirements for installing non-Python assets like URDF and launch files.

## Roadmap

See the checklist above. Next planned step: adding `ros2_control` and simulated sensors (IMU, camera, 2D lidar) to the URDF.

## License

MIT — see [LICENSE](LICENSE)
