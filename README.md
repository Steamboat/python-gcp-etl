python-gcp-etl
==============================

Code, framework, and tools for ETL prototyping.


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



<!-- ABOUT THE PROJECT -->
## About The Project

I'm not sure the best way to architect ETL patterns so this project will serve as a living document of what 
I've found that works and doesn't for serverless message brokering, loggregation, and data management.

### Built With
This app is built on a few key frameworks:
* [Flask](http://flask.pocoo.org/)
* [Google Cloud](https://cloud.google.com/)



<!-- GETTING STARTED -->
## Getting Started

Spin up some Cloud Functions and get started!

etl_to_lake.py - Migrate data from a SQL DB into a Data Lake in bulk.
Read from any SQL db with pandas and push the data into BigQuery tables.
Requires a list of tables and their ID columns for deduplication.

request_to_pubsub.py - Consume a request with a JSON payload.
Unpack the payload, inspect for a few values, and repack for a PUB/SUB topic.

http_subscriber -  Pub/Sub will keep trying until an HTTP route returns a 200.
This means that poorly-formed messages can ricochet through the system causing errors to be
over-represented. This function consumes 400 (Bad Request / validation failed json) and
 500 (server error) responses and notifies an admin, rather than retrying. Erroneous messages
are dropped in a dead-letter queue for a later pull subscriber.

<!-- LICENSE -->
## License

This project is covered under the [Do What The F*ck You Want To Public License](http://www.wtfpl.net/). So act accordingly.


<!-- CONTACT -->
## Contact

Steven Sutton - admin@theeverydayfuture.com

Project Link: [https://github.com/Steamboat/python-gcp-etl](https://github.com/Steamboat/python-gcp-etl)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Best-README-Template](https://raw.githubusercontent.com/othneildrew/Best-README-Template/)
