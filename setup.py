from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

from smart_stock import __version__ as version

setup(
	name="smart_stock",
	version=version,
	description="Modern, easy-to-use stock management with visual controls, barcode support, and low stock alerts",
	author="Your Company",
	author_email="your-email@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
