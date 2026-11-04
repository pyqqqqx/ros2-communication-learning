from setuptools import find_packages, setup

package_name = 'data_subscriber'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pyqqqx',
    maintainer_email='pyqqqx@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'calc1_node = data_subscriber.calc1_node:main',
            'calc2_node = data_subscriber.calc2_node:main',
            'final_node = data_subscriber.final_node:main',
        ],
    },
)
