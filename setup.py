from setuptools import setup

setup(
	name='nauta',
	version='2.1',
	py_modules=['nauta'],
	install_requires=[
		'httpx==0.27.0'
	],
	entry_points={
		'console_scripts': [
			'nauta=nauta:main'
		]
	}
)