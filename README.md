# integrating-sap-graph-and-essential-dissertation

The project is to connect with SAP Graph and using the returned metadata to capture data and visualize in Essential Architecture. 

### Project Structure
1. web - Automation for browser based application to connect to SAP Graph, visualize the entities and EA for capture and views
2. cli - Currently in progress but provides the command-line tool to automate the process
3. domain - The common business logic contains in this folder
4. data - The extracted data are put into this folder, since fetching all the entities from SAP Graph is slow

### Features
#### Web
1. Using SAP Graph we can sync all the entities to our data/ folder
2. Using SAP Graph we can push the entities data into Neo4J databases for later queries and visualization
3. Using SAP Graph we can provide the name of the Entity and it will return the relatship with it
4. Using Essential Architecture API we can login to the EA
5. Using Essential Architecture API we can capture data for Information layer - It will publish data to EA
6. TODO Using Essential Architecture API we want to push data into Data Object and Data Object Attribute for automation
#### Cli
TODO

### Getting Started
To run the application we need to install Python and the required dependency `django`
1. If running first time need to run migrate script (for session management) `python manage.py web/migrate`
2. Running the server `python manage.py runserver`
3. Go to browser and enter http://localhost:8000

### Screenshots

When click on the SAP Graph and Login to your SAP Graph. Search for Entity for their relationship or Click on "Load Graph Network". This will display the entities with relationships on the Graph

![Alt text](screenshots/sap-graph-entities.png?raw=true "Relationship")

