from setuptools import setup, find_packages

setup(
    name='inference-gateway',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.26.0',
    ],
    tests_require=[
        'unittest',
        'mock',
    ],
    author='Eden Reich',
    author_email='eden.reich@gmail.com',
    description='A Python SDK for Inference Gateway',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/edenreich/inference-gateway-python-sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
