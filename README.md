# Humanoid Robot — ROS 2 Simulation

A custom 18-DOF humanoid robot modeled in URDF/xacro and simulated in Gazebo Classic on ROS 2 Humble. Built as a hands-on project to learn ROS 2 and robotics simulation by building and debugging a real robot stack, rather than following tutorials end-to-end.

## Current status

- [x] Custom humanoid URDF, refactored into reusable xacro macros — pelvis, torso, head, bilateral arms, bilateral legs (22 links, 21 joints, 18 revolute DOF)
- [x] Gazebo Classic simulation launch (`gazebo.launch.py`), starting paused and unpausing only once the standing-pose command is already queued
- [x] RViz visualization launch (`display.launch.py`)
- [x] `ros2_control` integration — `joint_state_broadcaster` + `humanoid_trajectory_controller`, driven by `config/controllers.yaml`
- [x] Standing-pose publisher (`stand_pose.py`), configurable via `config/stand_pose.yaml`
- [x] Simulated camera sensor + baseline object detector (coarse brightness heuristic, `object_detector.py`)
- [x] MoveIt 2 configuration for upper-body planning (`left_arm` / `right_arm` / `upper_body` groups)
- [x] Nav2 configuration scaffolding (`config/nav2_params.yaml`, `navigation.launch.py`) — **not yet functional**, see Known limitations
- [ ] IMU / lidar sensors
- [ ] Gait / balance controller (needed for the robot to actually stand or walk under its own control)

See `CHANGELOG_fixes.md` for a detailed log of bugs found and fixed during a full-repo review (stale URDF, orphaned config, Nav2 plugin definitions, launch-timing/physics issues, etc.).

## Package structure

```
src/
└── robot_description/            # ament_python package
    ├── urdf/
    │   ├── robot.urdf.xacro       # top-level assembly
    │   ├── arm.xacro              # arm macro (left/right)
    │   ├── leg.xacro              # leg macro (left/right)
    │   └── properties.xacro       # shared inertia/geometry macros
    ├── config/
    │   ├── controllers.yaml       # ros2_control controller definitions
    │   ├── stand_pose.yaml        # standing-pose joint targets
    │   ├── ekf.yaml               # robot_localization EKF config
    │   └── nav2_params.yaml       # Nav2 costmap/controller/planner/behavior config
    ├── moveit/
    │   ├── humanoid.srdf
    │   ├── kinematics.yaml
    │   ├── joint_limits.yaml
    │   └── moveit_controllers.yaml
    ├── launch/
    │   ├── gazebo.launch.py       # spawns robot in Gazebo, brings up ros2_control
    │   ├── display.launch.py      # RViz only, no Gazebo
    │   ├── moveit.launch.py       # MoveIt 2 move_group + RViz
    │   ├── navigation.launch.py   # Nav2 bringup + EKF
    │   └── perception.launch.py   # camera + object_detector
    ├── robot_description/         # Python nodes
    │   ├── stand_pose.py
    │   └── object_detector.py
    ├── rviz/
    │   └── urdf.rviz
    └── test/                      # ament_copyright / flake8 / pep257
```

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic (`gazebo_ros`, `gazebo_ros2_control`)
- `ros2_control`, `controller_manager`, `joint_state_broadcaster`, `joint_trajectory_controller`
- `robot_localization` and `nav2_bringup` (for `navigation.launch.py`)
- `moveit_ros_move_group`, `moveit_ros_visualization` (for `moveit.launch.py`)
- `xacro`

Quickest way to pull all of these in one go, from the workspace root:
```bash
rosdep install --from-paths src --ignore-src -r -y
```

## Build

```bash
cd ~/ros2_ws        # workspace root, i.e. the directory containing src/
colcon build --packages-select robot_description
source install/setup.bash
```

## Run

**View the robot in RViz, no physics (quick sanity check on the model/TF tree):**
```bash
ros2 launch robot_description display.launch.py
```

**Spawn and simulate in Gazebo, with `ros2_control` and the standing pose:**
```bash
ros2 launch robot_description gazebo.launch.py
```

**Upper-body motion planning (run after `gazebo.launch.py` is already up):**
```bash
ros2 launch robot_description moveit.launch.py
```

**Camera + baseline object detector (run after `gazebo.launch.py`):**
```bash
ros2 launch robot_description perception.launch.py
```

**Nav2 + EKF (run after `gazebo.launch.py`) — scaffolding only, see below:**
```bash
ros2 launch robot_description navigation.launch.py
```

## Known limitations

- **No gait/balance controller yet.** `stand_pose.py` sends one open-loop trajectory command; it has no feedback, so the robot can still topple once it makes ground contact.
- **Nav2 is scaffolding, not a working stack.** The costmap/controller/planner/behavior plugins are all correctly defined and the servers will load, but there's no real base/gait controller consuming `/cmd_vel` or publishing odometry yet, so nothing will actually drive the robot.
- **Object detector is a deliberately simple placeholder** — a red-channel brightness threshold over the whole frame, not real vision.

## Notes from building this

`CHANGELOG_fixes.md` documents specific bugs found and fixed during a full audit of this repo: a stale/inconsistent hand-written URDF, an orphaned YAML config that no node was actually reading, missing Nav2 plugin definitions, `xacro` paths breaking on workspace directories with spaces, `use_sim_time` inconsistencies, and a physics-timing issue that caused the robot to free-fall and get violently corrected before its controllers had activated.

## Roadmap

Remaining: IMU/lidar sensors, and — the big one — an actual gait/balance controller, without which Nav2 and the standing pose remain open-loop scaffolding rather than a robot that can stand or walk on its own.

## License

MIT — see [LICENSE](LICENSE)
