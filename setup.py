from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rental_ms/__init__.py
from rental_ms import __version__ as version

setup(
	name="rental_ms",
	version=version,
	description="Booking of Rental Service",
	author="Mohamed Abdulsalam Alqadasi",
	author_email="moha2016it@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
