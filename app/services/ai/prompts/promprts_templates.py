ATTRIBUTE_MAPPING_PROMPT = """
ZADATAK:
Mapiraj isključivo postojeće External (WooCommerce) atribute i njihove opcije na Internal (Mungos) sistemske ključeve.

PODACI:
1. External: {external_data}
2. Internal: {internal_data}

STROGA PRAVILA ZA MAPIRANJE (ZABRANE):
1. ZABRANJENO JE izmišljati vrijednosti. Mapiraj SAMO "name" i "options" koji se nalaze u External setu podataka.
2. Ako u External setu ne postoji jasan par za neki Internal ključ, taj Internal ključ POTPUNO IGNORIŠI.
3. Nemoj dodavati opise kategorija ili "opšta mjesta" ako se oni ne nalaze u listi dostavljenih atributa.
4. "External_Value" mora biti identičan tekstu iz WooCommerce podataka.

PRAVILA ZA STRUKTURU I REDOSLIJED (KRITIČNO):
1. Output MORA biti organizovan po grupama: jedan Atribut, pa odmah njegove Opcije.
2. Redoslijed: 
   - Red sa "TypeFrom": "CategoryAttribute"
   - Redovi sa "TypeTo": "OptionForMultioptionAttribute" koji pripadaju isključivo tom atributu iznad.
3. STROGO JE ZABRANJENO grupisati sve atribute na vrh, a sve opcije na dno.

TEHNIČKA PRAVILA:
- Tipovi za atribute: "CategoryAttribute"
- Tipovi za opcije: "OptionForMultioptionAttribute"
- Mapiraj External "name" -> Internal "code" (za atribute).
- Mapiraj External "options" -> Internal "optionsForMultioptionAttribute.code" (za opcije).

OUTPUT FORMAT:
Vrati isključivo validan JSON (lista objekata). Svaki objekat mora imati tačno ove ključeve:
"TypeFrom", "ExternalKey", "TypeTo", "InternalKey".

PRIMJER ISPRAVNOG REDOSLIJEDA:
[
  {{"TypeFrom": "CategoryAttribute", "ExternalKey": "Širina", "TypeTo": "CategoryAttribute", "InternalKey": "TireWidth"}},
  {{"TypeFrom": "OptionForMultioptionAttribute", "ExternalKey": "155", "TypeTo": "OptionForMultioptionAttribute", "InternalKey": "Vehicles_Tires_TireWidth_155"}},
  {{"TypeFrom": "CategoryAttribute", "ExternalKey": "Visina", "TypeTo": "CategoryAttribute", "InternalKey": "TireHeight"}}
]
"""

CATEGORY_MAPPING_PROMPT = """
ZADATAK:
Ti si ekspert za e-commerce taksonomiju. Poveži svaku stavku iz "EKSTERNE LISTE" 
sa najsličnijom, logički odgovarajućom kategorijom iz "INTERNE LISTE".

PODACI:
1. EKSTERNA LISTA (Kategorije koje treba mapirati - mogu biti pojedinačna imena ili putanje razdvojene sa ';', '>', '/' ili ','):
{external_categories}

2. INTERNA LISTA (Dozvoljene ciljne kategorije u Mungos sistemu):
{internal_categories}

STROGA PRAVILA ZA MAPIRANJE:
1. Svaka stavka dostavljena u EKSTERNOJ LISTI mora imati svoj par u rezultatu.
2. "ExternalKey" MORA biti identičan tekstu iz Eksterne liste. 
   - Ako je ulaz "Parfemi", ExternalKey je "Parfemi".
   - Ako je ulaz "TV & SAT > Antene", ExternalKey je "TV & SAT > Antene". 
   - Ne mijenjaj separatore, ne skraćuj i ne prevodi ExternalKey.
3. "InternalKey" mora biti TAČAN naziv (kod) kategorije iz Interne liste.
4. LOGIKA UPARIVANJA:
   - Primarno koristi semantičku sličnost (npr. "Radijska oprema" -> "Radio_Oprema").
   - Ako je eksterna kategorija putanja (npr. "Aparati > Kuhinja > Mikseri"), fokusiraj se na zadnji element (Mikseri) pri traženju para u Internoj listi.
   - Ako ne postoji specifično poklapanje, mapiraj na najlogičniju nadređenu (roditeljsku) kategoriju koja postoji u Internoj listi.
5. Ako je kategorija potpuno neprepoznatljiva, mapiraj je na najopštiju srodnu kategoriju (npr. "Ostalo" ili "Razno" ako postoje u Internoj listi).

TEHNIČKA PRAVILA:
- "TypeFrom" je uvijek "Category".
- "TypeTo" je uvijek "Category".
- Vrati isključivo validan JSON (lista objekata) bez ikakvog dodatnog teksta, uvoda ili objašnjenja.

OUTPUT FORMAT:
[
  {{"TypeFrom": "Category", "ExternalKey": "Originalni_Ulaz", "TypeTo": "Category", "InternalKey": "Mungos_Kod"}}
]
"""