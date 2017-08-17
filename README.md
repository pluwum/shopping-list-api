# shopping-list-api
This project is a RESTful API using Flask with Endpoints that:
- a. Enable users to create accounts and login into the application 

EndPoint | Public Access 
POST /auth/register  TRUE 
POST /auth/login  TRUE 
POST /auth/logout  TRUE 
POST /auth/reset-password  TRUE 

- b. Enable users to create, update, view and delete a shopping list 

EndPoint | Public Access 
POST /shoppinglists/  FALSE 
GET /shoppinglists/  FALSE 
GET /shoppinglists/<id>  FALSE 
PUT /shoppinglists/<id>  FALSE 
DELETE /shoppinglists/<id>  FALSE 

- c. Add, update, view or delete items in a shopping list 

EndPoint | Public Access 
POST /shoppinglists/<id>/items/  FALSE 