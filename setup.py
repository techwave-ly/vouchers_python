from setuptools import setup, find_packages

setup(
    name="vouchers-python",
    version="1.0.0",
    description="Python SDK for Commerce Partner Vouchers API",
    author="TechWave",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # No third-party dependencies! It is completely plug-n-play.
    ],
)
