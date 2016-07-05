# rcportal migration
For migrating across rcallocation request data from NeCTAR rcportal database over to CRAMS database.

## Pre-Setup
- Git clone this project.
- This setup assumes you are migrating from MySQL to MySQL database and the target MySQL database has been setup.

## Setup
intall pip:

		sudo apt-get install python3-pip

install tox:

		sudo pip3 install tox

install mysql lib:

		sudo apt-get install mysql-server
		sudo apt-get install python3.5-dev
		sudo apt-get install libmysqlclient-dev

Export mysql_config path if on mac os:

		export PATH=$PATH:/usr/local/mysql/bin

## Setup Virtual Environment
From the project root directory, create the virtual environment by running the tox command:

		tox -e py35
This will create ".tox/" directory, to activate the virtualenv run: 

		source .tox/bin/activate

## To run migration:
Setup the source and target database in:

		rcportal_migration/settings.py

1. Create the database schema of your target db by running: 

		python manage.py migrate --database='crams_db'

2. Run django command to find the missing keystone users from source database

		python manage.py findmissinguser
	- It will generate a file called user_not_found_requests.csv under missing_keystone_users directory

	- Go through all user emails and find the current user in keystone based on the created_by id

	- Update missing_keystone_users.json

3. Start the django command to migrate the rcportal data into crams database

		python manage.py rcportalmigrate
	- any problems issues will be logged in the migration.log file

4. Validate the migration data - this will do a diff check on the db source and db target.

		python manage.py migrationvalidate
