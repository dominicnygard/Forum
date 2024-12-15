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

På sidan kan man söka efter inlägg genom att använda sökfältet, man kan skapa nya inlägg genom att klicka på knappen bredvid utloggningen.  
För att kunna skapa inlägg måste man förstås registrera sig eller logga in, men sidan är helt användbar utan att logga in också.  
För att öppna privatmeddelanden med någon måste man klicka på deras användarnamn, för att testa privatmeddelanden lönas det att öppna en  
ny incognito flik där man är inloggad med en annan användare, på så här sätt så ser man att meddelandena uppdateras i realtid utan att  
sidan laddas om.  

Andra funktionaliteter är att det t.ex. går att radera sina inlägg, kommentarer eller privatmeddelanden. Då man raderar privatmeddelanden så  
raderas de i realtid för båda användarna. Om det finns för många inlägg, kommentarer eller privatmeddelanden för att visa på en gång så  
laddas fler in om man använder sin scroll bar.  

