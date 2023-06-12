# SABD_Progetto1
Primo progetto per il corso di Sistemi e Architetture per Big Data del corso di Ingegneria Informatica Magistrale dell'università di Roma - Tor Vergata
## Obbiettivo
L'obbiettivo del progetto é quello di riuscire a rispondere a 3 query su un dataset assegnato e trovabile al seguente link: http://www.ce.uniroma2.it/courses/sabd2223/project/out500_combined+header.csv<br>
Inoltre le specifiche del progetto asseriscono una serie di vincoli che devono essere rispettati:
- Il dataset deve essere inserito all'interno dell'HDFS
- Il risultato delle query va inserito all'interno di un Database NoSQL
- Le query devono essere processate con la tecnica del Batch Processing
- Bisogna processare i dati utilizzando il framework Apache Spark
- Fornire una rappresentazione grafica dei risultati delle query utilizzando un framework di visualizzazione
## Framework utilizzati
- Apache Spark: per elaborazione delle Query
- Apache Hadoop Distributed File System (HDFS): Database distribuito che abbiamo utilizzato per il salvataggio del dataset e per il salvataggio dei risultati
- Apache NIFI: Framework per l'ingestion e per il pre-processing del dataset 
- MongoDB: Database NoSQL per caricare il risultato delle Query
- Grafana: Framework per la visulizzazione dei risultati delle Query
## Dataset
il dataset é composto di dati finanziari fornito dall’azienda fintech Infront Financial Technology. In particolare il dataset riguarda lo scambio di strumenti finanziari su tre principali borse europee nel corso di una settimana. I dati si basano su eventi reali acquisiti da Infront Financial Technology per la settimana dall’8 al 14 novembre 2021 (cinque giorni lavorativi seguiti da sabato e domenica). Il dataset ridotto contiene circa 4 milioni di eventi (a fronte dei 289 milioni del dataset originario) che coprono 500 azioni (equities) e indici (indices) sulle borse europee: Parigi (FR), Amsterdam (NL) e Francoforte/Xetra (ETR). Gli eventi sono registrati cos`ı come sono stati acquisiti; alcuni eventi sembrano essere privi di payload.
## Requisiti di Sistema
Il sistema per essere avviato ha bisogno dell'installazione di Docker e Docker compose poichè sistema utilizzato è stato utilizzato in maniera contenerizzata.
## Avvio Sistema
Il sistema può essere avviato tramite lo script avvio_Sistema.sh che si trova sulla directory principale del repository<br>
Per avviare il sistema basta eseguire il seguente comando:
```
sh avvioSistema.sh -x <Numero di Nodi Worker spark>
```
N.B. -x é un flag opzionale può per tanto essere omesso in caso di omissione viene avviato il sistema con un unico nodo Worker per spark<br>
Per continuare l'avvio del sistema bisognerà connettersi a nifi tramite la Web Interface che potrà essere trovatà su http://localhost:8443/nifi e da qui caricare importare il teampleate ./TempleateNIFI/InsertDataToHDFS.xml e avviare l'esecuzione del templeate.<br>
Dopo che l'elaborazione di NIFI sia finita si dovra eseguire il secondo script avvio_elaborazione.sh con il comando
```
sh avvio_elaborazione.sh
```
che permetterà l'elaborazione delle 3 query e il caricamento del Risultato nella cartella Results della directory principale.<br>
Infine per caricare su mongoDB i risultati bisognerà riandare sulla Web Interface di NIFI 
