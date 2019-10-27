# SP Suite (for ServerPilot)
SP Suite is a Python library written to interact with ServerPilot-managed servers over CLI. If you want to manage your ServerPilot server over command line, this utility is for you.

## Getting Started
Recommended way to install SP Suite is via PIP:

```bash
pip3 install spsuite
```

If PIP isn't installed on your system, you need to install it first:

```bash
sudo apt-get install python3-pip
```

The alternate way to install SP Suite is cloning the repository:

```bash
git clone https://github.com/rehmatworks/spsuite && cd spsuite && python3 setup.py install
```

## Available Commands
Once SP Suite is installed, a command `spsuite` will become available in your terminal. You will have access to the following sub-commands in order to manage your server.

```bash
listsysusers        Show all SSH users existing on this server.
createsysuser       Create a new SSH user.
listapps            Show all existing apps.
createapp           Create a new app.
updatedomains       Update an apps' domains and recreate vhost files.
changephp           Change PHP version of an app.
changephpall        Change PHP version for all apps.
deleteapp           Delete an app permanently.
delallapps          Delete all apps permanently.
listdbusers         Show all existing database users.
createsqluser       Create a new MySQL user.
updatesqlpassword   Update any MySQL user's password.
dropuser            Drop a MySQL user.
dropallsqlusers     Drop all MySQL users except system users (root, sp-
                    admin, debian-sys-maint, mysql.session, mysql.sys).
listdbs             Show all existing databases.
createdb            Create a new MySQL database.
dropdb              Drop a MySQL database.
dropalldbs          Drop all databases except system databases
                    (information_schema, mysql, performance_schema, sys).
getcert             Get letsencrypt cert for an app.
getcerts            Get letsencrypt certs for all apps.
removecert          Uninstall SSL cert from an app.
removecerts         Uninstall SSL certs for all apps.
forcessl            Force SSL certificate for an app.
unforcessl          Unforce SSL certificate for an app.
forceall            Force HTTPs for all apps.
unforceall          Unforce HTTPs for all apps.
denyunknown         Deny requests from unknown domains.
allowunknown        Allow requests from unknown domains.
```
