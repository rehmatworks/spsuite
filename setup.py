from setuptools import setup
import os
import subprocess
from spsuite.tools import parsetpl, runcmd
from setuptools.command.install import install

class SetupSslRenewCron(install):
	def run(self):
		crondir = '/etc/cron.weekly'
		cronfile = os.path.join(crondir, 'spsuite-sslrenewals')
		if not os.path.exists(crondir):
			os.makedirs(crondir)

		certbotpath = subprocess.check_output(['which', 'certbot']).strip().decode('utf8')
		cronfiledata = parsetpl('cron.tpl', data={'certbotpath': certbotpath})
		with open(cronfile, 'w') as cf:
			cf.write(cronfiledata)
		runcmd("chmod +x {}".format(cronfile))
		install.run(self)

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
		'Jinja2',
		'pymysql',
		'certbot'
	],
	package_data={'spsuite':['templates/*.tpl']},
	cmdclass={
		'install': SetupSslRenewCron
	}
)
