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
Designen på huvudsidan är inte ännu färidg, men en del av funktionaliteten finns där.
