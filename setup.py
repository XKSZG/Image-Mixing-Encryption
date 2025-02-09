from setuptools import setup, find_packages

setup(
    name='Image Mixing Encryption',
    version='1.0',
    packages=find_packages(),
    description='将图片拆解混合进行加密',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='XK',
    author_email='xk1xk2xk3xk@126.com',
    url='None',
    install_requires=[
        # 你的项目依赖的库
        "Pillow"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)