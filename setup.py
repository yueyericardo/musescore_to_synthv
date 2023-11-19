from setuptools import setup, find_packages

setup(
    name='musescore_to_synthv',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add your package dependencies here
        # e.g., 'requests', 'numpy', etc.
    ],
    entry_points={
        'console_scripts': [
            'musescore_to_synthv=musescore_to_synthv.convert:main',
        ],
    },
)
