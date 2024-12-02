from setuptools import find_packages, setup

package_name = 'voice_command'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'speech_recognition',
        'pyttsx3',
        'vosk',
        'pyaudio'
        ],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='jwu7@g.ucla.edu',
    description='Voice Command',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "voice_command_node = voice_command.voice_command_node:main"
        ],
    },
)
