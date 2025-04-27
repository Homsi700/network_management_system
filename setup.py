import os
from setuptools import setup, find_packages

setup(
    name="network_management_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'fastapi==0.68.1',
        'uvicorn[standard]==0.15.0',
        'h11>=0.12.0',  # بديل عن httptools للتوافق مع Windows
        'sqlalchemy==1.4.23',
        'websockets==10.0',
        'python-dotenv==0.19.0',
        'paramiko==2.8.1',
        'routeros-api==0.17.0',
        'requests==2.26.0',
        'pydantic==1.10.13',  # Updated version
        'python-multipart==0.0.5',
        'aiofiles==0.7.0',
        'python-jose[cryptography]',
        'passlib[bcrypt]',
        'jinja2',
        'watchdog',
        'psutil',
        'apscheduler',
        'email-validator==2.1.0.post1'  # Added for email validation
    ],
    author="Network Management System Team",
    author_email="admin@networkmanager.com",
    description="نظام إدارة شبكة الإنترنت المحلية",
    long_description=open('README.md').read() if os.path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'network-manager=backend.main:start_server',
        ],
    },
)