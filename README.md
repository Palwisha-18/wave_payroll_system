# Payroll System 

## Project Description

Imagine that this is the early days of Wave's history, and that we are prototyping a new payroll system API. A front end (that hasn't been developed yet, but will likely be a single page application) is going to use our API to achieve two goals:

1. Upload a CSV file containing data on the number of hours worked per day per employee
1. Retrieve a report detailing how much each employee should be paid in each _pay period_

All employees are paid by the hour (there are no salaried employees.) Employees belong to one of two _job groups_ which determine their wages; job group A is paid $20/hr, and job group B is paid $30/hr. Each employee is identified by a string called an "employee id" that is globally unique in our system.

Hours are tracked per employee, per day in comma-separated value files (CSV).
Each individual CSV file is known as a "time report", and will contain:

1. A header, denoting the columns in the sheet (`date`, `hours worked`,
   `employee id`, `job group`)
1. 0 or more data rows

In addition, the file name should be of the format `time-report-x.csv`,
where `x` is the ID of the time report represented as an integer. For example, `time-report-42.csv` would represent a report with an ID of `42`.

A sample input file named `time-report-42.csv` is included in this repo.

### What our API does:

Django REST framework is used to build API with the following endpoints to serve HTTP requests:

1. An endpoint for uploading a file.

   - This file conforms to the CSV specifications outlined in the previous section.
   - Upon upload, the timekeeping information within the file is stored to a database for archival purposes.
   - If an attempt is made to upload a file with the same report ID as a previously uploaded file, this upload fails with an error message indicating that this is not allowed.

2. An endpoint for retrieving a payroll report structured in the following way:
   - Returns a JSON object `payrollReport`.
   - `payrollReport` has a single field, `employeeReports`, containing a list of objects with fields `employeeId`, `payPeriod`, and `amountPaid`.
   - The `payPeriod` field is an object containing a date interval that is roughly biweekly. Each month has two pay periods; the _first half_ is from the 1st to the 15th inclusive, and the _second half_ is from the 16th to the end of the month, inclusive. `payPeriod` will have two fields to represent this interval: `startDate` and `endDate`.
   - Each employee has a single object in `employeeReports` for each pay period that they have recorded hours worked. The `amountPaid` field contains the sum of the hours worked in that pay period multiplied by the hourly rate for their job group.
   - If an employee is not paid in a specific pay period, there is not be an object in `employeeReports` for that employee + pay period combination.
   - The report is sorted in some sensical order (e.g. sorted by employee id and then pay period start.)
   - The report is based on all _of the data_ across _all of the uploaded time reports_, for all time.

As an example, given the upload of a sample file with the following data:

   | date       | hours worked | employee id | job group |
   | ---------- | ------------ | ----------- | --------- |
   | 4/1/2023   | 10           | 1           | A         |
   | 14/1/2023  | 5            | 1           | A         |
   | 20/1/2023  | 3            | 2           | B         |
   | 20/1/2023  | 4            | 1           | A         |

A request to the report endpoint returns the following JSON response:

   ```json
   {
     "payrollReport": {
       "employeeReports": [
         {
           "employeeId": "1",
           "payPeriod": {
             "startDate": "2023-01-01",
             "endDate": "2023-01-15"
           },
           "amountPaid": "$300.00"
         },
         {
           "employeeId": "1",
           "payPeriod": {
             "startDate": "2023-01-16",
             "endDate": "2023-01-31"
           },
           "amountPaid": "$80.00"
         },
         {
           "employeeId": "2",
           "payPeriod": {
             "startDate": "2023-01-16",
             "endDate": "2023-01-31"
           },
           "amountPaid": "$90.00"
         }
       ]
     }
   }
   ```
## Project Setup 
1. Follow the instructions on https://docs.docker.com/install/ to install docker
2. Follow the instructions on https://docs.docker.com/compose/install/ to install docker compose
3. Create a `.env` file under *payroll* directory and copy the contents from `.env.sample` in it. Contact the developer for credentials.
4. From the project root, `cd payroll` and run the following command to start the application server: 
        `sudo docker-compose up --build`
5. docker-compose will run entrypoint.sh that handles model migrations.
6. The app will run locally at http://127.0.0.1:8001

### Interacting with API endpoints
Django REST's web browsable API can be used to test endpoints
#### Uploading CSV 
POST `http://127.0.0.1:8001/api/upload-csv/` with csv file

It will return a success message incase the csv is parsed and loaded into databse without any errors. On the other hand it will return 400 HTTP status with an error message if an attempt is made to upload a file with the same report ID as a previously uploaded file.

#### Retrieve Payroll
GET `http://127.0.0.1:8001/api/retrieve-payroll/`

It should return the same `payrollReport` as mentioned in the project description section.

### Running Unittests
Unittests are added to test the functionality of both endpoints. While the docker container is running, in a new terminal try the following:

* `docker exec -it payroll-backend /bin/sh`
* `python manage.py test api.tests`

## Notes 
1. Following features are implemented/used in the current version of the project:
- Uses docker and docker-compose for building and running the application
- Uses Python 3.8 and Django REST framework for creating API endpoints
- A bash script file has been added that does `makemigrations` and `migrate`. This script is called everytime django service starts and automatically runs database migrations.
- Logger has been added in django settings to allow logging messages through the project
- PostgreSQL has been integrated as it works well with Django ORM
- Local, staging and production configurations has been added
- Unittests have been added to test endpoints

2. Answers to the following questions:
   - How did you test that your implementation was correct? 
     - First using DRF's browsable web API, manually tested both endpoints and then added unittests as well
   - If this application was destined for a production environment, what would you add or change?
     - Enable user authentication for accessing the endpoints (such as JWT authentication)
     - Enable caching `payrollReport` such that if no new csv has been uploaded, then instead of processing payroll at runtime everytime, we can retrieve it from cache
     - Support CI/CD
     - Add unittests for Django Models
   - What compromises did you have to make as a result of the time constraints of this challenge?
     - Was unable to unittests for all scenarios (for example, uploading csv with the same report ID as a previously uploaded file).
     - More comprehensive error handling could be implemented
