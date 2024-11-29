# Forum
Det här projektet är ett diskussionsforum
* användare kan registrera och skapa ett eget konto
* Endast inloggade användare kan lägga till ett inlägg 
* inloggade användare kan också kommentera på inlägget 
* I kommentarerna på inlägget så kan man svara på andras meddelanden så att man ser texten från kommentaren man svarar på, så att det är tydligt vem man svarar på.
* Det finns information om inlägg som t.ex. hur många svar det har och när den lagts upp. 
* På sidan kan man också söka på inlägg eller sortera dem med namn eller med hur många svar de har. 
* Användare kan också meddela varandra privat om de vill. Admin användare har möjligheten att ta bort tillägg och kommentarer.

För att använda programmet kan man först starta ett virtual env om man vill.  
Allt som behövs finns i requirements.txt och sql schema finns i schema.sql  
`(venv) $ pip install -r requirements.txt`  
`(venv) $ psql < schema.sql`  
I programmet finns det behörigheter som man måste för tillfället manuellt lägga till i databasen genom att öppna psql och skriva  
`INSERT INTO Permissions (permission_name) VALUES ('view'), ('send'), ('post'), ('comment')`  
När man gjort det här så kan man starta programmet genom att köra  
`(venv) $ flask run`  
Detta kommer att starta programmet på localhost:5000  
Designen på huvudsidan är inte ännu färdig, men en del av funktionaliteten finns där. I mitten av skärmen kan man se alla inlägg och   på inläggen kan man lämna kommentarer för tillfället finns det ingen knapp att komma till inlägget, men man kan komma dit genom att   skriva in url manuellt. Den är i formen `/post/<post_id>`.  

Ett konto skapar man förstås genom att registrera sig eller logga in. Man måste vara inloggad för att kunna lägga till ett inlägg   eller kommentera på inlägg eller skicka meddelanden åt andra användare.   

Användare har behörigheter, det finns globala behörigheter som gäller då man vill lägga ut inlägg och det finns behörigheter som är   för specifika rum som användaren är medlem i. Om man t.ex. inte har rätt behörighet så slipper man inte ens in på sidan, som om man   inte har behörigheten 'view' för ett rum slipper man inte in på sidan för det rummet.   

För att starta en ny chat med en annan användare måste man vara inloggad och skriva in manuellt url `/start-chat/<int:user_id>` där   user_id är id:n på den användaren man vill starta en chat med. För att testa det här behöver man registrera åtminstone två användare,   det räcker att en av användarna startar chatten med den andra användaren.  

Efter att man startat en chat så borde den synas på sidan av webbsidan, där syns alla chattar som man har öppnat och därifrån kan man   öppna chatten. Om man vill testa chatten så måste man logga in andra användaren på en incognito flik eftersom annars får användarna   samma access_token på grund av att de delar cookies. Efter att man öppnat chatten från två flikar så kan man testa skicka meddelanden   mellan dem och se att meddelanden uppdateras dynamiskt på sidan.  

Måste ännu fixa finare design till webbsidan och lägga till admin permissioner som ger åtgång till allt, samt möjligheten ta bort   inlägg, kommentarer och meddelanden. Måste ännu fixa upp små saker med koden och lägga till sökfunktion till sidan.  
