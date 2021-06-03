from setuptools import setup

package_name = 'nodl_to_policy'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Abrar Rahman Protyasha',
    maintainer_email='abrar@openrobotics.org',
    description='Tool to generate a ROS 2 Access Control Policy from the NoDL description of a ROS system',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
