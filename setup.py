from setuptools import setup, find_packages

setup(
    name="election_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    author="MinoHealth AI Labs",
    author_email="your.email@minohealth.ai",
    description="A short description of election_analysis",
    python_requires=">=3.9",
)