# 🏆 Vincitore Hackathon 🏆
## NeoData Hackatania 2.0
### 18 novembre 2024
Questo progetto è stato realizzato da Giuseppe Bellamacina e Salvatore Iurato.

[![NeoData Hackatania 2.0](https://badgen.net/badge/🏆/Vincitore/orange)](https://devpost.com/software/guardian-p2g0df)

# Guardian

**Guardian** è un avanzato **ChatBot** con supporto **MultiModale** progettato per aiutare le **Forze dell'Ordine**, fornendo informazioni critiche e tempestive riguardanti individui e veicoli fermati durante un posto di blocco o per un'indagine. Grazie all'integrazione con **LangChain**, **LangGraph** e **Neo4j**, è in grado di accedere a dati sensibili e fornirli in tempo reale, rendendo il processo di identificazione e verifica più rapido ed efficiente.

### Deployment
[![Guardian Deployment](https://badgen.net/badge/Guardian/Streamlit%20App/green)](https://guardianbot.streamlit.app)

### Demo
[![Guarda il video su YouTube](https://img.youtube.com/vi/0PmxTnOJM-M/0.jpg)](https://www.youtube.com/watch?v=0PmxTnOJM-M)

## Funzionalità principali

1. **Precedenti penali**  
   Accesso immediato a informazioni sui precedenti penali di un individuo, inclusa la presenza di condanne o reati pregressi.

2. **Dati anagrafici**  
   Recupero di informazioni personali, come nome, cognome, data di nascita e residenza.

3. **Dati veicolo**  
   Accesso a informazioni sul veicolo, come modello, targa, proprietario, RCA e scadenza della revisione. Inoltre, il sistema è in grado di ottenere i dati di un veicolo direttamente dalle immagini, utilizzando tecnologie avanzate di riconoscimento.

4. **Navigazione contestualizzata dei dati**  
   Grazie a **GraphRAG**, Guardian sfrutta un approccio di *Retrieval-Augmented Generation* (RAG) basato su grafi, che consente di navigare in modo efficiente attraverso grandi moli di dati, fornendo risposte contestualizzate e precise. È possibile accedere rapidamente a informazioni su individui, veicoli, scuole o posti di lavoro associati a un determinato soggetto, offrendo un quadro completo e dettagliato della situazione.

5. **Calcolo del coefficiente di rischio**  
   Il sistema include un tool dedicato per calcolare uno pseudo coefficiente di rischio. Questo valore è determinato sulla base del livello di gravità dei reati di una persona, includendo un'analisi dei reati commessi dai suoi familiari o colleghi. Tale funzionalità consente di ottenere una visione complessiva del potenziale livello di pericolosità di un individuo.
