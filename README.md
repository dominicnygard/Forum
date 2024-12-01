# Forum
Det här projektet är ett diskussionsforum
* användare kan registrera och skapa ett eget konto
* Endast inloggade användare kan lägga till ett inlägg
* Användare kan kommentera på inlägg 
* inloggade användare kan också kommentera på inlägget 
* Det finns information om inlägg som t.ex. hur många svar det har och när den lagts upp. 
* På sidan kan man också söka på inlägg eller sortera dem med namn eller med hur många svar de har. 
* Användare kan också meddela varandra privat om de vill. Admin användare har möjligheten att ta bort tillägg och kommentarer.

För att använda programmet kan man först starta ett virtual env om man vill.  
Allt som behövs finns i requirements.txt och sql schema finns i schema.sql  
`(venv) $ pip install -r requirements.txt`  
`(venv) $ psql < schema.sql`  
När man gjort det här så kan man starta programmet genom att köra  
`(venv) $ flask run`  
Detta kommer att starta programmet på localhost:5000  
Designen på huvudsidan är inte ännu färdig, men funktionaliteten finns där. I mitten av skärmen kan man se alla inlägg och  på inläggen kan man lämna kommentarer. Flera inlägg laddas in automatiskt om man skrollar neråt, om det finns inlägg, samma sak finns för kommentarer samt meddelanden i privata samtal.   

Ett konto skapar man förstås genom att registrera sig eller logga in. Man måste vara inloggad för att kunna lägga till ett inlägg   eller kommentera på inlägg eller skicka meddelanden åt andra användare.   

Användare har behörigheter, det finns globala behörigheter som gäller då man vill lägga ut inlägg och det finns behörigheter som är   för specifika rum som användaren är medlem i. Om man t.ex. inte har rätt behörighet så slipper man inte ens in på sidan, som om man   inte har behörigheten 'view' för ett rum slipper man inte in på sidan för det rummet.   

För att starta en ny chat med en annan användare måste man vara inloggad och skriva in manuellt url `/start-chat/<int:user_id>` där   user_id är id:n på den användaren man vill starta en chat med. För att testa det här behöver man registrera åtminstone två användare,   det räcker att en av användarna startar chatten med den andra användaren.  

Efter att man startat en chat så borde den synas på sidan av webbsidan, där syns alla chattar som man har öppnat och därifrån kan man   öppna chatten. Om man vill testa chatten så måste man logga in andra användaren på en incognito flik eftersom annars får användarna   samma access_token på grund av att de delar cookies. Efter att man öppnat chatten från två flikar så kan man testa skicka meddelanden   mellan dem och se att meddelanden uppdateras dynamiskt på sidan.  

Måste ännu fixa finare design till webbsidan och lägga till admin permissioner som ger åtgång till allt, samt möjligheten ta bort   inlägg, kommentarer och meddelanden. Måste ännu fixa upp små saker med koden och lägga till sökfunktion till sidan. I stort sett fungerar alla funktionalitet som det ska, det är mest bara designen kvar på webbsidan.  
