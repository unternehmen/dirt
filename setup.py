from setuptools import setup, find_packages

setup(
    name='dirt',
    description='A first-person, turn-based adventure game',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['pygame==1.9.3'],
    entry_points={
        'console_scripts': [
            'dirt = dirt:main'
        ]
    }
)
