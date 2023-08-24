# airport-api-service
API allows users to create profiles and book flights
### Features

* JWT Authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing orders and tickets for the flights
* Displaying available and taken places on the flight
* Filtering airports, routs and flights
* Create airports, routs, flights with administrator rights
* Email confirmation

## Run with docker
Docker should be installed
+ git clone https://github.com/kleotan901/airport-api-service.git
+ cd airport-api-service
+ docker-compose up --build

## Getting access

+ create new user via /api/user/register/
+ get access token via /api/user/token/

### You can use the following test credentials:

##### Test superuser:
- Email: admin@admin.com
- Password: qay12345


##### Test user:
- Email: user@email.com
- Password: qay12345
## Configuration
The project uses environment variables for configuration. Please follow these steps to set up the required configuration files.

The .env file is used to store sensitive information and configuration variables that are necessary for the project to function properly.

The .env.sample file serves as a template or example for the .env file. It includes the necessary variables and their expected format, but with placeholder values.
 
 To configure the project:

- Locate the .env.sample file in the project's root directory.
- Duplicate the .env.sample file and rename the duplicated file to .env.
- Open the .env file and replace the placeholder values with the actual configuration values specific to your setup.

Remember to keep the .env file secure and avoid sharing it publicly or committing it to version control systems.
