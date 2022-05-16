# LISTA ELABORATI

> Sviluppare un client per il broker con le seguenti caratteristiche:
> - il client deve collegarsi automaticamente al broker
> - il client deve implementare un'interfaccia a riga di comando per
>   - collegarsi a un canale del broker
>   - inviare un messaggio su un determinato canale
>   - bufferizzare e fornire su richiesta all'utente la lista dei canali a cui si è collegati e dei messaggi in esso comunicati.

> Sviluppare un'interfaccia REST-API per il collegamento al broker con le seguenti caratteristiche:
> - l'interfaccia deve mediare su più utenti identificati mediante un meccanismo di password e token
> - l'interfaccia deve bufferizzare le risposte del broker per ogni utente collegato rendendole disponibili su richiesta

> Estendere il broker per permetterne un utilizzo distribuito. In particolare:
> - la connessione tra i broker componenti deve essere a rete completa
> - la struttura è completamente trasparente al generico client che può connettersi a uno qualsiasi dei broker componenti
> - si lascia completa libertà sulla gestione dinamica dei broker in ingresso e uscita

> Estendere il broker per permetterne un utilizzo distribuito. In particolare:
> - la connessione tra i broker componenti deve essere ad albero
> - la struttura è completamente trasparente al generico client che può connettersi a uno qualsiasi dei broker componenti
> - si lascia completa libertà sulla gestione dinamica dei broker in ingresso e uscita

> Implementare un nodo di generazione dati (ad esempio di lettura di dati diagnostici da pc) con pubblicazione su un canale del broker
> Implementare un sistema di lettura su canale e presentazione dei risultati.
> Il sistema deve essere robusto alla caduta del generatore o dei sistemi di lettura
