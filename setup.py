from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='tokeks',
    version='0.1',
    description='',
    url='https://github.com/ckarageorgkaneen/tokeks',
    packages=['tokeks'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    project_urls={
        'Tracker': 'https://github.com/ckarageorgkaneen/tokeks/issues',
        'Source': 'https://github.com/ckarageorgkaneen/tokeks',
    },
    license='MIT',
    python_requires='>=3.5',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
    ]
)
