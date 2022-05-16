# OBIETTIVI

Costruzione di un modello di comunicazione a ring con gestione a oracolo dell'infrastruttura di comunicazione.

## ORACOLO

L'oracolo ha il compito di

* gestire l'ingresso di nuovi nodi all'interno del ring
* gestire l'uscita di nodi dal ring
* aggiornare la configurazione dei nodi a valle di un ingresso o di una uscita

## PROTOCOLLO DI INGRESSO E USCITA

* un nodo che voglia entrare nel ring comunica all'oracolo il suo ingresso e ne riceve la configurazione di comunicazione
* un nodo che voglia uscira dal ring comunica all'oracolo la sua decisione e attende di essere autorizzato all'uscita
* L'oracolo gestisce ingressi e uscite in modo sequenziale

## STEP DI SVILUPPO

* ORACOLO: costruzione della parte di gestione delle richieste di ingresso e uscita.
* ORACOLO/NODI: costruzione dei meccanismi di configurazione dei nodi.
* NODI: costruzione dei meccanismi di comunicazione.
