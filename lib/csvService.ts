import { FraudEntry, PhoneEntries, CustomerIdToPhone } from '@/types';

const CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1l2CD7aX4_5qHwkQRRHD3ntTyOTOSfB-1jAsBP9J_TdSkyQGdc8qCjO1-GOgXysUdvkG6HQ4LuCov/pub?gid=0&single=true&output=csv";

export class CSVService {
  private fraudList: FraudEntry[] = [];
  private phoneEntries: PhoneEntries = {};
  private customerIdToPhone: CustomerIdToPhone = {};
  private lastFetch: number = 0;
  private readonly CACHE_DURATION = 10 * 60 * 1000; // 10 minutes

  constructor() {
    this.initializeService();
  }

  private normalizePhone(phone: string): string {
    phone = phone.trim();
    if (phone.startsWith('0') && phone.length === 11) {
      return phone.slice(1);
    }
    return phone;
  }

  private parseCustomerIds(cell: string): string[] {
    return cell
      .trim()
      .replace(/[\[\]\n]/g, ' ')
      .replace(/,/g, ' ')
      .split(' ')
      .filter(cid => cid.length > 0);
  }

  async fetchAndParseCSV(): Promise<void> {
    const now = Date.now();
    if (now - this.lastFetch < this.CACHE_DURATION) {
      return;
    }

    try {
      const response = await fetch(CSV_URL);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const csvText = await response.text();
      const lines = csvText.split('\n');
      const headers = lines[0].split(',');
      
      const tempFraudList: FraudEntry[] = [];
      const tempPhoneEntries: PhoneEntries = {};
      const tempCustomerIdToPhone: CustomerIdToPhone = {};

      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const values = this.parseCSVLine(line);
        const row: any = {};
        headers.forEach((header, index) => {
          row[header.trim()] = values[index]?.trim() || '';
        });

        const phone = row['Phone'];
        const ids = this.parseCustomerIds(row['customer_ids'] || '');
        
        const entry: FraudEntry = {
          phone,
          state: row['State'],
          city: row['City'],
          zone: row['Zone'],
          distinct_customers: row['distinct_customers'],
          customer_ids: ids
        };

        tempFraudList.push(entry);
        
        if (!tempPhoneEntries[phone]) {
          tempPhoneEntries[phone] = [];
        }
        tempPhoneEntries[phone].push(entry);

        ids.forEach(cid => {
          tempCustomerIdToPhone[cid] = phone;
        });
      }

      this.fraudList = tempFraudList;
      this.phoneEntries = tempPhoneEntries;
      this.customerIdToPhone = tempCustomerIdToPhone;
      this.lastFetch = now;
      
      console.log("CSV refreshed successfully");
    } catch (error) {
      console.error("CSV fetch error:", error);
      throw error;
    }
  }

  private parseCSVLine(line: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current);
    return result;
  }

  async search(query: string): Promise<SearchResult> {
    await this.fetchAndParseCSV();
    
    const displayPhone = query;
    let phone: string | undefined;
    const normQuery = this.normalizePhone(query);

    if (this.phoneEntries[normQuery]) {
      phone = normQuery;
    } else if (this.customerIdToPhone[query]) {
      phone = this.customerIdToPhone[query];
    }

    if (phone && this.phoneEntries[phone]) {
      const entries = this.phoneEntries[phone];
      const locations = entries.map(entry => ({
        state: entry.state,
        city: entry.city,
        zone: entry.zone,
        distinct_customers: entry.distinct_customers,
        customer_ids: entry.customer_ids,
      }));

      let search_display = displayPhone;
      if (phone.length === 10) {
        search_display = '0' + phone;
      }

      return {
        status: "fraud",
        phone: search_display,
        locations,
        search_value: search_display,
      };
    } else {
      let search_display = displayPhone;
      if (query.length === 10) {
        search_display = '0' + query;
      }

      return {
        status: "notfraud",
        phone: search_display,
        locations: [],
        search_value: search_display,
      };
    }
  }

  getStats() {
    return {
      totalEntries: this.fraudList.length,
      uniquePhones: Object.keys(this.phoneEntries).length,
      lastFetch: this.lastFetch,
    };
  }
}

// Singleton instance
export const csvService = new CSVService();