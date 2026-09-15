# Fixes applied — ros2-humanoid-robot audit follow-up

All six real inconsistencies from the audit are fixed below. The two
"informational" items (packaging, detector heuristic) are intentionally
left alone — see the note at the end.

## 1. Deleted `urdf/robot.urdf`
It was a stale, hand-written duplicate of the xacro output — no
`ros2_control`, no sensors, and inertia values that didn't match the
`properties.xacro` formulas. Nothing referenced it, so removal is the
safe fix. `setup.py`'s `glob('urdf/*')` will simply stop picking it up.

## 2. Wired up `config/stand_pose.yaml` instead of leaving it orphaned
Three coordinated changes:
- **`config/stand_pose.yaml`**: rewritten so its top-level key is
  `stand_pose_publisher` (the node's actual runtime name — it was
  wrongly `humanoid_trajectory_controller` before, which is why it could
  never have worked even if loaded), and extended to cover all 18 joints
  instead of just 6 leg joints.
- **`robot_description/stand_pose.py`**: now declares each joint's target
  as a `stand_positions.<joint_name>` parameter (seeded with the old
  hardcoded values as defaults) and builds the trajectory from
  `get_parameter(...)` instead of a hardcoded list. Retuning the pose is
  now a YAML edit, not a code edit.
- **`launch/gazebo.launch.py`**: passes `config/stand_pose.yaml` to the
  `stand_pose` node via `parameters=[...]`.

## 3. Added `use_sim_time` to `robot_state_publisher` in `gazebo.launch.py`
It was missing while `navigation.launch.py`'s nodes already set it. Left
on the wall clock, `robot_state_publisher`'s TF stamps drift out of sync
with Gazebo's simulated `/clock`, which is a common source of TF
extrapolation warnings once Nav2/MoveIt are also running.

## 4. Rewrote `config/nav2_params.yaml` with the plugin definitions Nav2 needs
The costmaps referenced `obstacle_layer`/`inflation_layer` by name without
ever defining what those plugins *are*, and `controller_server` /
`planner_server` had no `*_plugins` entries or per-plugin parameter
blocks — Nav2 Humble would fail to bring these servers up as the file
stood. Rewritten with:
- `controller_server`: `FollowPath` → `RegulatedPurePursuitController`
  (fewer required parameters than DWB, reasonable default for a small
  indoor base once one exists), plus `progress_checker`/`goal_checker`.
- `planner_server`: `GridBased` → `NavfnPlanner`.
- `behavior_server` (Humble's name; `recoveries_server` was renamed in
  the Galactic→Humble migration) with `spin`/`backup`/`wait` plugins.
- Both costmaps: proper `plugin:` keys for `ObstacleLayer` and
  `InflationLayer`, plus an `observation_sources: scan` block pointing at
  the lidar's `/scan` topic.

This makes the config *loadable*; it does not make the humanoid drive
itself. The README/ROADMAP's scope note — that Nav2 still needs a real
gait controller publishing odometry and consuming velocity commands —
still applies and is now restated at the top of the file itself.

## 5. Fixed the MoveIt SRDF end-effector mismatch
`<end_effector parent_link="left_forearm" .../>` skipped a link relative
to its own group's chain (`tip_link="left_hand"`). Changed `parent_link`
to `left_hand` on both sides so the end-effector tag is internally
consistent with the chain it belongs to.

## Not changed (informational items, no action needed)
- **`build/`/`install/`/`log/` in the zip**: your `.gitignore` already
  excludes these correctly — the zip was just made from the raw working
  directory instead of a git export. Nothing to fix in the repo; just
  zip from a clean `git archive` or after `rm -rf build install log`
  next time, since some of those files are symlinks to your local
  `/home/rony/Downloads/...` path and won't resolve on another machine.
- **`object_detector.py`'s red-channel brightness check**: already
  documented in its own docstring as a deliberately simple baseline. No
  change made.

## 7. Fixed `xacro: error: expected exactly one input file` (path-with-spaces bug)
Root cause: your workspace lives under a directory containing a space
(`ROS2 PROJECTS`). `launch.substitutions.Command([...])` builds one
shell-style string and tokenizes it with `shlex`, so an unquoted path
with a space splits into two arguments — `xacro` then sees more than
one filename and refuses to run.

Two things fix this:
- **Immediate workaround (do this regardless):** rename the folder to
  remove the space, e.g. `mv "/home/rony/ROS2 PROJECTS" /home/rony/ros2_projects`.
  Spaces in ROS 2 workspace paths cause the same class of problem in
  colcon, catkin, and plenty of other tooling, so this is worth doing
  even after the code fix below.
- **Code fix (defense in depth):** every `Command([...])` that builds a
  path in `display.launch.py`, `gazebo.launch.py`, and `moveit.launch.py`
  now wraps each path in literal quote characters before concatenation
  (e.g. `Command(['xacro ', '"', urdf, '"'])`), so `shlex.split()`
  treats the whole quoted path as a single token no matter what
  characters are in it. Verified with a `shlex` simulation using the
  exact failing path from the error log — resolves to exactly the
  arguments `xacro` expects.

## 8. Fixed the robot free-falling and vanishing from view in Gazebo
Root cause: `gazebo.launch.py` let physics run from the moment the world
started. All 18 joints are unactuated until `joint_state_broadcaster`
(3s) and `humanoid_trajectory_controller` (5s) finish loading, so the
robot free-fell/ragdolled under gravity for several seconds first. When
the trajectory controller then activated, it tried to snap every joint
from wherever the robot had fallen into the standing pose in 3 seconds —
a large, sudden correction that's a classic trigger for Gazebo Classic's
ODE solver to diverge and fling the model far outside the camera view
(it isn't deleted — check the Gazebo GUI's World panel; `my_robot` is
still listed, just off-screen at extreme coordinates).

Fix: the world now starts paused (`extra_gazebo_args: '--pause'` on the
included `gazebo_ros` launch), so nothing moves while the controllers
load. `stand_pose` now fires at 6s (before the 8s unpause) so its one
trajectory command is already queued on `humanoid_trajectory_controller`
before physics ever runs. The first simulated step the robot experiences
is already under active control heading toward the standing pose,
instead of free-falling first and correcting after the fact. Physics is
unpaused via `ros2 service call /unpause_physics std_srvs/srv/Empty {}`
at 8s.

If the robot still topples once unpaused, that's a separate, expected
limitation the README already calls out: a single open-loop trajectory
command has no balance feedback, so on real ground contact it can still
tip over — that needs an actual gait/balance controller, not a launch
timing fix. What this change specifically fixes is the "flew off into
space" failure mode caused by the fall-then-snap sequence.
