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
    ],

    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='evolve06',
    maintainer_email='evolve06@todo.todo',

    description='Robot description package with URDF and launch files',
    license='Apache-2.0',

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [],
    },
)
