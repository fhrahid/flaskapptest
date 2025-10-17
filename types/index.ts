export interface FraudEntry {
  phone: string;
  state: string;
  city: string;
  zone: string;
  distinct_customers: string;
  customer_ids: string[];
}

export interface Location {
  state: string;
  city: string;
  zone: string;
  distinct_customers: string;
  customer_ids: string[];
}

export interface SearchResult {
  status: 'fraud' | 'notfraud';
  phone: string;
  locations: Location[];
  search_value?: string;
}

export interface PhoneEntries {
  [key: string]: FraudEntry[];
}

export interface CustomerIdToPhone {
  [key: string]: string;
}