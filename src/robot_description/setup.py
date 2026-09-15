from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_description'

setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[
        # ROS 2 package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # package.xml install
        ('share/' + package_name, ['package.xml']),

        # URDF files
        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*')),

        # Launch files (.launch.py only)
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),

        # RViz configs
        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')),

        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),

        (os.path.join('share', package_name, 'moveit'),
            glob('moveit/*')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='rony',
    maintainer_email='199137478+ronyrajan-p@users.noreply.github.com',

    description='ROS 2 simulation and autonomy stack for a custom humanoid robot',
    license='MIT',

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'stand_pose = robot_description.stand_pose:main',
            'object_detector = robot_description.object_detector:main',
        ],
    },
)
