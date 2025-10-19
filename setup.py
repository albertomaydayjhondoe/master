from setuptools import setup, find_packages

setup(
    name="tiktok-viral-ml",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    extras_require={
        "ml": [
            line.strip()
            for line in open("requirements-ml.txt")
            if line.strip() and not line.startswith("#")
        ],
        "dev": [
            line.strip()
            for line in open("requirements-dev.txt")
            if line.strip() and not line.startswith("#")
        ],
    },
    python_requires=">=3.11",
)