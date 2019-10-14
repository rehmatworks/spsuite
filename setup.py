from setuptools import setup

setup(name='spsuite',
	version='1.0.0',
	description='Command line utilities to manage ServerPilot provisioned servers.',
	author="Rehmat Alam",
	author_email="contact@rehmat.works",
	url="https://github.com/rehmatworks/spsuite",
	license="MIT",
	entry_points={
		'console_scripts': [
			'spsuite = spsuite.spsuite:main'
			],
	},
	packages=[
		'spsuite'
	],
	install_requires=[
		'python-nginx',
		'validators',
		'termcolor',
		'tabulate',
		'Jinja2'
	],
	package_data={'spsuite':['templates/*.tpl']},
)
