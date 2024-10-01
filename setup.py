from setuptools import setup, find_packages

setup(
    name='django_discord_logger',  # Replace with your app's name
    version='0.1.0',  # Initial release version
    description='Monitor your Django app with Discord webhooks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='IndagoDev',
    author_email='support@indago-dev.com',
    url='https://github.com/yourusername/your-app-name',  # Replace with your repo URL
    license='MIT',  # Choose an appropriate license
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',  # Specify Django version or other dependencies
        'requests>=2.28.2',
        # Add other dependencies if needed
    ],
    classifiers=[
        'Development Status :: 4 - Beta',  # Adjust as appropriate
        'Framework :: Django',
        'Framework :: Django :: 3.2',  # Adjust to your Django version
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        # Add more classifiers from https://pypi.org/classifiers/
    ],
)
