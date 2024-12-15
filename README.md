# Forum
Det här projektet är ett diskussionsforum
* användare kan registrera och skapa ett eget konto
* Endast inloggade användare kan lägga till ett inlägg
* Användare kan kommentera på inlägg 
* inloggade användare kan också kommentera på inlägget 
* Det finns information om inlägg som t.ex. hur många svar det har och när den lagts upp. 
* På sidan kan man också söka på inlägg.   
* Användare kan också meddela varandra privat om de vill.  

För att använda programmet kan man först starta ett virtual env om man vill.  
Allt som behövs finns i requirements.txt och sql schema finns i schema.sql  
`(venv) $ pip install -r requirements.txt`  
`(venv) $ psql < schema.sql`  
Efter att man gjort det här måste man också skapa en .env fil där man måste skriva tre variabler  
`SECRET_KEY='secret key'`
`JWT_SECRET_KEY='jwt secret key'`
`DATABASE_URI='din databas URI'`
Efter det så är det bara att köra  
`(venv) $ flask run`  
Detta kommer att starta programmet på localhost:5000  

