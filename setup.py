from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

project_slug = "ops-downloader"
module_name = project_slug.replace("-", "")

setup(
    name=project_slug,
    use_scm_version=True,
    url=f"https://github.com/Senth/{project_slug}",
    license="MIT",
    author="Matteus Magnusson",
    author_email="senth.wallace@gmail.com",
    description="Downloads objective personality episodes in a plex-friendly format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={"console_scripts": [f"{project_slug}={module_name}.__main__:main"]},
    include_package_data=True,
    data_files=[("config", [f"config/{project_slug}-example.cfg"])],
    install_requires=[
        "tealprint==0.3.0",
        "blulib",
        "selenium",
        "chromedriver-autoinstaller",
        "yt-dlp",
        "ffmpeg-python",
        "dataclasses",
        "autosub",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
