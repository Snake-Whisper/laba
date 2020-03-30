import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="laba-server",
    version="0.0.1",
    author="snake-whipser",
    author_email="snake-whisper@web-utils.eu",
    description="lightweight open source chat server with media support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/snake-whisper/laba",
    install_requieres=["pymysql", "redis", "Flask", "Flask-SocketIO", "validate-email", "eventlet"],
    install_requieres=True,
    packages=['laba-server']
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
