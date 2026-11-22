

data starbucks_data;
    infile "/home/u64492455/Proiect/starbucks_date_complete.csv"
        dsd dlm=',' firstobs=2;

    length Country_Code $2
           Ownership_Type $30
           City $50;

    input Country_Code $
          Ownership_Type $
          Latitude
          Longitude
          City $
          Sales
          Costs
          Satisfaction
          Store_size;
run;
/*Afisarea datelor ințiale de la Starbucks*/
title "Datele inițiale din fisierul Starbucks";
proc print data=starbucks_data;
run;
/*Descrierea setului de date*/
proc contents data=starbucks_data;
run;

libname starb '/home/u64492455/Proiect';
data starb.starbucks_data;
    infile "/home/u64492455/Proiect/starbucks_date_complete.csv" dsd dlm=',' firstobs=2;
    input 
        Country_Code : $2.
        Ownership_Type : $30.
        Latitude 
        Longitude 
        City : $50.
        Sales
        Costs
        Satisfaction 
        Store_size;
run;
/*Crearea unui set de date permanent ce contine numele intreg al tarilor*/
data starb.starbucks_nume_tari;
    set starb.starbucks_data;
    length Tara $30;
    if Country_Code = 'FR' then Tara = 'Franța';
    else if Country_Code = 'DE' then Tara = 'Germania';
    else if Country_Code = 'IT' then Tara = 'Italia';
    else if Country_Code = 'ES' then Tara = 'Spania';
    else if Country_Code in ('UK', 'GB') then Tara = 'Regatul Unit';
    else if Country_Code = 'NL' then Tara = 'Olanda';
    else if Country_Code = 'BE' then Tara = 'Belgia';
    else if Country_Code = 'PL' then Tara = 'Polonia';
    else if Country_Code = 'RO' then Tara = 'România';
    else if Country_Code = 'RU' then Tara = 'Rusia';
    else if Country_Code = 'CH' then Tara = 'Elveția';
    else if Country_Code = 'SE' then Tara = 'Suedia';
    else if Country_Code = 'NO' then Tara = 'Norvegia';
    else if Country_Code = 'FI' then Tara = 'Finlanda';
    else if Country_Code = 'AT' then Tara = 'Austria';
    else if Country_Code = 'PT' then Tara = 'Portugalia';
    else if Country_Code = 'IE' then Tara = 'Irlanda';
    else if Country_Code = 'CZ' then Tara = 'Cehia';
    else if Country_Code = 'HU' then Tara = 'Ungaria';
    else if Country_Code = 'SK' then Tara = 'Slovacia';
    else if Country_Code = 'BG' then Tara = 'Bulgaria';
    else if Country_Code = 'GR' then Tara = 'Grecia';
    else Tara = 'Altele';
run; 
title "Date Starbucks cu denumiri complete pentru țări";
proc print data=starb.starbucks_nume_tari;
run;



proc sort data=starb.starbucks_nume_tari 
          out=starb.starbucks_nume_tari; 
    by Tara;
run; 

/* Extragem observațiile care au costurile operationale <50, dar recenziile clientilor >8 într-un fișier temporar din setul permanent */
data locatii_preferate;
    set starb.starbucks_nume_tari;
    if Satisfaction > 8 and Costs < 50;
run;

/* Afișarea */
title "Locații preferate";
proc print data=locatii_preferate;
    var Tara Ownership_Type Satisfaction Costs;
run;

/*Sortati crescator dupa costuri aceste locatii */
proc sort data=locatii_preferate out=locatii_preferate_sortate;
    by Costs;
run;

title "Locațiile preferate sortate crescător după costuri";
proc print data=locatii_preferate_sortate;
	var Tara Ownership_Type Satisfaction Costs;
run;
/*Analiza profitului in aceste locatii*/
data locatii_preferate_profit;
    set locatii_preferate_sortate;
    /* Eliminăm valorile lipsă cu ajutorul ne . */
    if Sales ne . and Costs ne . and Satisfaction ne . then do;
        Profit = Sales - Costs;
        output;
    end;
run;

title "Locații preferate cu profit lunar calculat";
proc print data=locatii_preferate_profit;
    var Tara City Sales Costs Satisfaction Profit;
run;

title "Media profitului și satisfacției pe țări";
proc means data=locatii_preferate_profit mean;
    class Tara;
    var Profit Satisfaction;
run;

proc means data=locatii_preferate_profit noprint;
    class Tara;
    var Profit;
    output out=profit_pe_tara (drop=_TYPE_ _FREQ_) mean=MedieProfit;
run;

/* Sortăm descrescător după profit mediu */
proc sort data=profit_pe_tara out=profit_pe_tara_sortat;
    by descending MedieProfit;
run;

data top3_tari;
    set profit_pe_tara_sortat;
    if _N_ <= 3;
run;
/* Afișăm rezultatul */
title "Top 3 țări cu cel mai mare profit mediu";
proc print data=top3_tari noobs;
run;

data locatii_profit;
    set starb.starbucks_nume_tari;
    if Sales ne . and Costs ne . then do;
        Profit = Sales - Costs;
        output;
    end;
run;

proc print data=locatii_profit;



proc means data=locatii_profit;
    class Tara;
    var Profit;
    output out=medii_profit_pe_tara (drop=_TYPE_ _FREQ_) mean=Profit_Mediu;
run;

data medii_profit_pe_tara;
    set medii_profit_pe_tara;
    if Tara ne '';
run;


proc print data=medii_profit_pe_tara;

proc format;
    value profit_level
        low - <50 = 'Mic'
        50 - <55 = 'Mediu'
        55 - high = 'Mare';
run;

data medii_profit_cu_categorie;
    set medii_profit_pe_tara;
    format Categorie_Profit $8.;
    Categorie_Profit = put(Profit_Mediu, profit_level.);
run;

title "Media profitului și categoria de profit pe țări";
proc print data=medii_profit_cu_categorie;
    var Tara Profit_Mediu Categorie_Profit;
run;
 



data tari_cu_profit_mic;
    set medii_profit_cu_categorie;
    if Categorie_Profit = 'Mic';
run;

title "Țări cu profit mic – Se vor aplica strategii de îmbunătățire";
proc print data=tari_cu_profit_mic;
    var Tara Profit_Mediu Categorie_Profit;
run;

proc sql;
    create table tari_statistici as
    select
        Country_Code as Tara,
        count(*) as Numar_Magazine,
        mean(Satisfaction) as Media_Satisfactie format=6.2
    from starbucks_data
    group by Country_Code;
quit;
title "Numarul de magazine Starbucks si media satisfactiei pe tara";
proc print data=tari_statistici;
run;

proc format;
    value categ_satisfactie
        low -< 8 = 'Scazuta'
        8 -< 9 = 'Rezonabila'
        9 - high = 'Ridicata';
run;

data tari_statistici_clasificate;
    set tari_statistici;
    format Nivel_Satisfactie $10.;
    Nivel_Satisfactie = put(Media_Satisfactie, categ_satisfactie.);
run;

title "Clasificarea țărilor în funcție de satisfacția medie a clienților";
proc print data=tari_statistici_clasificate;
    var Tara Numar_Magazine Media_Satisfactie Nivel_Satisfactie;
run;

/*Gruparea datelor pe regiuni*/
data starbucks_regiuni;
    set locatii_profit;
    length Regiune $10;
    select (Country_Code);
        when ('AT','BE','DE','FR','NL','IE','GB') Regiune = 'Vest';
        when ('BG','CZ','HU','PL','RO','RU','SK') Regiune = 'Est';
        when ('ES','GR','PT') Regiune = 'Sud';
        otherwise Regiune = 'Alta';
    end;
run;

proc means data=starbucks_regiuni noprint;
    class Regiune;
    var Profit Satisfaction;
    output out=analiza_regiuni mean=Medie_Profit Medie_Satisfactie;
run;

data analiza_regiuni;
    set analiza_regiuni;
    if Regiune ne '';
run;

proc print data=analiza_regiuni;
    title "Profitul și satisfacția medie pe regiuni europene";
run;

/*Lucru cu masive*/
data analiza_masive;
    set analiza_regiuni;
    array valori(2) Medie_Profit Medie_Satisfactie;
    do i = 1 to dim(valori);
        put "Valoare " i ": " valori(i);
    end;
run;

/*Grafice*/
title "Profitul Mediu al magazinelor preferate Starbucks pe tari din Europa";
proc sgplot data=profit_pe_tara_sortat;
    vbar Tara / response=MedieProfit datalabel
        datalabelattrs=(color=black size=10 weight=bold)
        fillattrs=(color=green)
        outlineattrs=(color=black thickness=0.5);

    xaxis display=(nolabel) label="Tara";
    yaxis label="Profit Mediu" grid;
run;

title "Număr total de magazine Starbucks pe țară";

proc sql;
    create table magazine_pe_tari as
    select Tara, count(*) as Nr_Magazine
    from starb.starbucks_nume_tari
    group by Tara;
quit;

proc sgplot data=magazine_pe_tari;
    vbar Tara / response=Nr_Magazine datalabel 
        fillattrs=(color=lightblue) 
        datalabelattrs=(size=10 weight=bold);
    yaxis label="Număr Magazine";
run;

proc sql;
    create table nr_magazine_regiuni as
    select Regiune, count(*) as Numar_Magazine
    from starbucks_regiuni
    where Regiune ne ''
    group by Regiune;
quit;

title "Numar total de magazine Starbucks pe regiuni europene";
proc sgplot data=nr_magazine_regiuni;
    vbar Regiune / response=Numar_Magazine datalabel
        fillattrs=(color=lightblue)
        datalabelattrs=(size=10 weight=bold);
    yaxis label="Număr Magazine";
    xaxis label="Regiune";
run;
















