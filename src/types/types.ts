export interface Condominio {
  id: string;
  nome: string;
  indirizzo: string;
  numStazioni: number;
  energiaMese: number;
}

export interface ChargingStation {
  id: string;
  condominioId: string;
  posizione: string;
  potenza: number;
  postoAuto: string;
  assegnataA: string | null;
  consumoTrimestre: number;
  valoreTrimestre: number;
  stato: "In uso" | "Libero";
  storicoTrimestrale: StoricoTrimestrale[];
}

export interface StoricoTrimestrale {
  trimestre: string;
  consumo: number;
  valore: number;
  reportUrl: string;
}

export interface Wallbox {
  id: string;
  stazioneId: string;
  potenzaMax: number;
  posteggio: string;
  assegnataA: string | null;
  consumoMese: number;
  valore: number;
  stato: "In uso ora" | "Libera" | "Sospesa";
}

export interface Utente {
  id: string;
  condominioId: string;
  nome: string;
  interno: string;
  email: string;
  auto: string;
  targa: string;
  consumoMese: number;
  costoMese: number;
  statoFattura: "Da fatturare" | "Fatturato" | "Pagato";
}

export interface StoricoMensile {
  mese: string;
  consumo: number;
  costo: number;
  stato: "Pagato" | "Da pagare";
}
