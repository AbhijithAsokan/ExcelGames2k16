Dalalbull is a part of Excel 2016 online Games.
So to make easier to manage all the games, different games were separated and made as different Django App within the same project.
This repository has Only Dalalbull.

NOTE: The Market Opens at: 09:15 hours and Closes at: 15:30 hours.
So running this setup during the above time period is preferred.

-------------------------------------------------------
			Setting UP
-------------------------------------------------------

1. Install [Python Virtual Environment](https://github.com/pypa/virtualenv):
    	pip install virtualenv
	
2. Navigate to the folder where you want to setup the project. Start and switch to new virtual environment :
	virtualenv venv_name
	source venv_name/bin/activate

3. Clone this repository to virtual environment folder,then go inside that folder, then execute the following commands:

	pip install -r requirements.txt
	
4. Run initial setup
	You can either run the shell script after granting permission:
		chmod +x first_run.sh
		./first_run.sh
	OR copy paste the instructions in terminal if you don't want to grant permissions. 

5. Runing the project:
	We need 2 terminals to run project, one for running celery task and another for running server.
	In first terminal:
		navigate to ExcelGames2k16 (folder where readme.md resides)
		Then run the following commands:
			chmod +x run_dalalbull.sh
			./run_dalalbull.sh
	In second terminal:
		navigate to ExcelGames2k16 (folder where readme.md resides)
		Then run the following commands:
			chmod +x run_dalalbull_celery.sh
			./run_dalalbull_celery.sh
			

### EDITS TO DO

Change Database name, username and password

<code>
 
    @ExcelGames2k16/ExcelGames/ExcelGames/settings.py


    DATABASES = {

        'default': {

            'ENGINE': 'django.db.backends.mysql',

            'NAME': 'excel2k16',

            'USER': 'USER',

            'PASSWORD': 'PASSWORD',

            'HOST': '',

            'PORT': '',

        }

    }

</code>





    

