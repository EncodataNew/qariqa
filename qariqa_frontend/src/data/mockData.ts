import { Condominio, ChargingStation, Wallbox, Utente, StoricoMensile, StoricoTrimestrale } from "@/types/types";

const COSTO_KWH = 0.36;

export const condomini: Condominio[] = [
  {
    id: "c1",
    nome: "Condominio Via Verdi 12",
    indirizzo: "Via Verdi 12, Milano",
    numStazioni: 2,
    energiaMese: 427,
  },
  {
    id: "c2",
    nome: "Residence Porta Nuova",
    indirizzo: "Corso Como 8, Milano",
    numStazioni: 3,
    energiaMese: 612,
  },
  {
    id: "c3",
    nome: "Condominio Sempione",
    indirizzo: "Viale Certosa 45, Milano",
    numStazioni: 2,
    energiaMese: 389,
  },
  {
    id: "c4",
    nome: "Palazzo Brera",
    indirizzo: "Via Brera 28, Milano",
    numStazioni: 4,
    energiaMese: 821,
  },
  {
    id: "c5",
    nome: "Condominio Navigli",
    indirizzo: "Alzaia Naviglio Grande 18, Milano",
    numStazioni: 3,
    energiaMese: 691,
  },
];

export const chargingStations: ChargingStation[] = [
  {
    id: "CP-01",
    condominioId: "c1",
    posizione: "Garage - Piano -1",
    potenza: 22,
    postoAuto: "Posto 12",
    assegnataA: "Marco Bianchi",
    consumoTrimestre: 247.2,
    valoreTrimestre: 247.2 * COSTO_KWH,
    stato: "In uso",
    storicoTrimestrale: [
      { trimestre: "Q4 2024", consumo: 238.5, valore: 238.5 * COSTO_KWH, reportUrl: "/reports/cp01-q4-2024.pdf" },
      { trimestre: "Q3 2024", consumo: 215.8, valore: 215.8 * COSTO_KWH, reportUrl: "/reports/cp01-q3-2024.pdf" },
      { trimestre: "Q2 2024", consumo: 251.3, valore: 251.3 * COSTO_KWH, reportUrl: "/reports/cp01-q2-2024.pdf" },
    ],
  },
  {
    id: "CP-02",
    condominioId: "c1",
    posizione: "Garage - Piano -2",
    potenza: 22,
    postoAuto: "Posto 28",
    assegnataA: null,
    consumoTrimestre: 118.9,
    valoreTrimestre: 42.80,
    stato: "Libero",
    storicoTrimestrale: [
      { trimestre: "Q4 2024", consumo: 115.2, valore: 41.47, reportUrl: "/reports/cp02-q4-2024.pdf" },
      { trimestre: "Q3 2024", consumo: 122.8, valore: 44.21, reportUrl: "/reports/cp02-q3-2024.pdf" },
      { trimestre: "Q2 2024", consumo: 118.5, valore: 42.66, reportUrl: "/reports/cp02-q2-2024.pdf" },
    ],
  },
  {
    id: "CP-03",
    condominioId: "c2",
    posizione: "Piano Interrato A, Zona Est",
    potenza: 44,
    postoAuto: "Posto 5",
    assegnataA: "Laura Conti",
    consumoTrimestre: 153.3,
    valoreTrimestre: 153.3 * COSTO_KWH,
    stato: "In uso",
    storicoTrimestrale: [
      { trimestre: "Q4 2024", consumo: 148.2, valore: 148.2 * COSTO_KWH, reportUrl: "/reports/cp03-q4-2024.pdf" },
      { trimestre: "Q3 2024", consumo: 162.7, valore: 162.7 * COSTO_KWH, reportUrl: "/reports/cp03-q3-2024.pdf" },
      { trimestre: "Q2 2024", consumo: 139.4, valore: 139.4 * COSTO_KWH, reportUrl: "/reports/cp03-q2-2024.pdf" },
    ],
  },
  {
    id: "CP-04",
    condominioId: "c2",
    posizione: "Piano Interrato B, Zona Ovest",
    potenza: 22,
    postoAuto: "Posto 18",
    assegnataA: "Luca Ferri",
    consumoTrimestre: 401.4,
    valoreTrimestre: 401.4 * COSTO_KWH,
    stato: "In uso",
    storicoTrimestrale: [
      { trimestre: "Q4 2024", consumo: 389.6, valore: 389.6 * COSTO_KWH, reportUrl: "/reports/cp04-q4-2024.pdf" },
      { trimestre: "Q3 2024", consumo: 425.1, valore: 425.1 * COSTO_KWH, reportUrl: "/reports/cp04-q3-2024.pdf" },
      { trimestre: "Q2 2024", consumo: 378.9, valore: 378.9 * COSTO_KWH, reportUrl: "/reports/cp04-q2-2024.pdf" },
    ],
  },
  {
    id: "CP-05",
    condominioId: "c2",
    posizione: "Piano Terra - Posti Esterni",
    potenza: 22,
    postoAuto: "Posto 32",
    assegnataA: "Giulia Martini",
    consumoTrimestre: 285.6,
    valoreTrimestre: 285.6 * COSTO_KWH,
    stato: "Libero",
    storicoTrimestrale: [
      { trimestre: "Q4 2024", consumo: 268.4, valore: 268.4 * COSTO_KWH, reportUrl: "/reports/cp05-q4-2024.pdf" },
      { trimestre: "Q3 2024", consumo: 291.7, valore: 291.7 * COSTO_KWH, reportUrl: "/reports/cp05-q3-2024.pdf" },
      { trimestre: "Q2 2024", consumo: 257.2, valore: 257.2 * COSTO_KWH, reportUrl: "/reports/cp05-q2-2024.pdf" },
    ],
  },
];

export const wallboxes: Wallbox[] = [
  {
    id: "WB-01",
    stazioneId: "ST-01",
    potenzaMax: 7.4,
    posteggio: "Posto 12",
    assegnataA: "Marco Bianchi",
    consumoMese: 82.4,
    valore: 82.4 * COSTO_KWH,
    stato: "In uso ora",
  },
  {
    id: "WB-02",
    stazioneId: "ST-01",
    potenzaMax: 11,
    posteggio: "Posto 15",
    assegnataA: null,
    consumoMese: 0,
    valore: 0,
    stato: "Libera",
  },
  {
    id: "WB-03",
    stazioneId: "ST-02",
    potenzaMax: 7.4,
    posteggio: "Posto 24",
    assegnataA: "Laura Conti",
    consumoMese: 51.1,
    valore: 51.1 * COSTO_KWH,
    stato: "Libera",
  },
  {
    id: "WB-04",
    stazioneId: "ST-02",
    potenzaMax: 7.4,
    posteggio: "Posto 26",
    assegnataA: "Luca Ferri",
    consumoMese: 133.8,
    valore: 133.8 * COSTO_KWH,
    stato: "In uso ora",
  },
  {
    id: "WB-05",
    stazioneId: "ST-02",
    potenzaMax: 11,
    posteggio: "Posto 28",
    assegnataA: "Giulia Martini",
    consumoMese: 95.2,
    valore: 95.2 * COSTO_KWH,
    stato: "Libera",
  },
];

export const utenti: Utente[] = [
  {
    id: "u1",
    condominioId: "c1",
    nome: "Marco Bianchi",
    interno: "4B",
    email: "m.bianchi@email.it",
    auto: "Tesla Model 3",
    targa: "EV 123 XY",
    consumoMese: 82.4,
    costoMese: 82.4 * COSTO_KWH,
    statoFattura: "Da fatturare",
  },
  {
    id: "u2",
    condominioId: "c1",
    nome: "Laura Conti",
    interno: "2A",
    email: "l.conti@email.it",
    auto: "Renault Zoe",
    targa: "EV 456 AB",
    consumoMese: 51.1,
    costoMese: 51.1 * COSTO_KWH,
    statoFattura: "Fatturato",
  },
  {
    id: "u3",
    condominioId: "c1",
    nome: "Luca Ferri",
    interno: "7C",
    email: "l.ferri@email.it",
    auto: "BMW i4",
    targa: "EV 789 CD",
    consumoMese: 133.8,
    costoMese: 133.8 * COSTO_KWH,
    statoFattura: "Pagato",
  },
  {
    id: "u4",
    condominioId: "c1",
    nome: "Giulia Martini",
    interno: "1D",
    email: "g.martini@email.it",
    auto: "Volkswagen ID.4",
    targa: "EV 321 EF",
    consumoMese: 95.2,
    costoMese: 95.2 * COSTO_KWH,
    statoFattura: "Da fatturare",
  },
  {
    id: "u5",
    condominioId: "c1",
    nome: "Andrea Russo",
    interno: "5A",
    email: "a.russo@email.it",
    auto: "Audi e-tron",
    targa: "EV 654 GH",
    consumoMese: 64.5,
    costoMese: 64.5 * COSTO_KWH,
    statoFattura: "Fatturato",
  },
];

export const storicoMensile: Record<string, StoricoMensile[]> = {
  u1: [
    { mese: "Settembre 2025", consumo: 74.2, costo: 74.2 * COSTO_KWH, stato: "Pagato" },
    { mese: "Agosto 2025", consumo: 69.8, costo: 69.8 * COSTO_KWH, stato: "Pagato" },
    { mese: "Luglio 2025", consumo: 91.5, costo: 91.5 * COSTO_KWH, stato: "Pagato" },
    { mese: "Giugno 2025", consumo: 58.3, costo: 58.3 * COSTO_KWH, stato: "Pagato" },
  ],
  u2: [
    { mese: "Settembre 2025", consumo: 48.9, costo: 48.9 * COSTO_KWH, stato: "Pagato" },
    { mese: "Agosto 2025", consumo: 52.4, costo: 52.4 * COSTO_KWH, stato: "Pagato" },
    { mese: "Luglio 2025", consumo: 61.2, costo: 61.2 * COSTO_KWH, stato: "Pagato" },
  ],
  u3: [
    { mese: "Settembre 2025", consumo: 128.5, costo: 128.5 * COSTO_KWH, stato: "Pagato" },
    { mese: "Agosto 2025", consumo: 142.1, costo: 142.1 * COSTO_KWH, stato: "Pagato" },
    { mese: "Luglio 2025", consumo: 119.7, costo: 119.7 * COSTO_KWH, stato: "Pagato" },
  ],
};

export const getCondominioById = (id: string) => condomini.find((c) => c.id === id);
export const getStazioniByCondominio = (condominioId: string) =>
  chargingStations.filter((s) => s.condominioId === condominioId);
export const getUtentiByCondominio = (condominioId: string) => utenti.filter((u) => u.condominioId === condominioId);
export const getWallboxByStazione = (stazioneId: string) => wallboxes.filter((w) => w.stazioneId === stazioneId);
export const getUtenteById = (id: string) => utenti.find((u) => u.id === id);
export const getStazioneById = (id: string) => chargingStations.find((s) => s.id === id);
export const getStoricoByUtente = (utenteId: string) => storicoMensile[utenteId] || [];
