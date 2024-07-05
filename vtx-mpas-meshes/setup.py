import setuptools

dependencies = [
    'xarray',
    'mpas-tools',
    'jigsaw',
]

setuptools.setup(
    name="vtxmpasmeshes",
    version="0.0.1",
    author="Marta Gil Bardaji, Gerard Cavero Siscart et al.",
    author_email="marta.gil@vortexfdc.com",
    description="MPAS and WRF for python",
    packages=setuptools.find_packages(include=['vtxmpasmeshes']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=dependencies,
    maintainer='Marta Gil Bardaji',
    maintainer_email='marta.gil@vortexfdc.com',
)