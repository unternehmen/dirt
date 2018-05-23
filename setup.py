from setuptools import setup, find_packages

setup(
    name='dirt',
    description='A first-person, turn-based adventure game',
    version='0.1.0',
    license='GPLv3',
    packages=find_packages(),
    install_requires=['pygame==1.9.3', 'appdirs==1.4.3'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dirt = dirt:main'
        ]
    },
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment :: Role-Playing'
    ]
)
