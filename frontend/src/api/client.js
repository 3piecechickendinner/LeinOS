// Use environment variable for API base URL in production, fallback to proxy path for development
const API_BASE = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api';

// Default tenant for development (matches Firestore data)
const DEFAULT_TENANT = 'demo-user';

// Toggle for demo mode with mock data
// Set to false to use real API even in development
// Note: Notifications and Deadlines have mock fallbacks regardless of this setting
const USE_MOCK_DATA = true;

// Mock data for demos and screenshots
const mockData = {
  portfolioStats: {
    total_value: 87500,
    total_interest_earned: 14230,
    active_liens: 12,
    average_return_rate: 16.2,
    upcoming_deadlines: 3,
  },

  liens: [
    {
      id: 'lien-001',
      certificate_number: 'MD-2024-0847',
      property_address: '123 Main St, Miami, FL 33130',
      parcel_id: '01-3245-067-0890',
      county: 'Miami-Dade',
      state: 'FL',
      purchase_amount: 8500,
      interest_rate: 18,
      premium: 250,
      purchase_date: '2024-05-15',
      redemption_deadline: '2026-05-15',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-002',
      certificate_number: 'BR-2024-1234',
      property_address: '456 Oak Ave, Fort Lauderdale, FL 33301',
      parcel_id: '50-42-04-12-0010',
      county: 'Broward',
      state: 'FL',
      purchase_amount: 12000,
      interest_rate: 18,
      premium: 500,
      purchase_date: '2024-03-22',
      redemption_deadline: '2026-03-22',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-003',
      certificate_number: 'PB-2024-0567',
      property_address: '789 Palm Dr, West Palm Beach, FL 33401',
      parcel_id: '74-43-44-21-05-000',
      county: 'Palm Beach',
      state: 'FL',
      purchase_amount: 5200,
      interest_rate: 18,
      premium: 100,
      purchase_date: '2024-06-10',
      redemption_deadline: '2026-06-10',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-004',
      certificate_number: 'MD-2024-0923',
      property_address: '321 Coral Way, Miami, FL 33145',
      parcel_id: '01-4156-023-0450',
      county: 'Miami-Dade',
      state: 'FL',
      purchase_amount: 15000,
      interest_rate: 18,
      premium: 750,
      purchase_date: '2024-04-08',
      redemption_deadline: '2026-04-08',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-005',
      certificate_number: 'BR-2023-4521',
      property_address: '567 Sunrise Blvd, Plantation, FL 33317',
      parcel_id: '50-41-17-01-0230',
      county: 'Broward',
      state: 'FL',
      purchase_amount: 7800,
      interest_rate: 18,
      premium: 200,
      purchase_date: '2023-11-20',
      redemption_deadline: '2025-11-20',
      tax_year: 2022,
      status: 'redeemed',
    },
    {
      id: 'lien-006',
      certificate_number: 'PB-2024-0789',
      property_address: '890 Ocean Blvd, Boca Raton, FL 33432',
      parcel_id: '06-43-47-27-01-000',
      county: 'Palm Beach',
      state: 'FL',
      purchase_amount: 9500,
      interest_rate: 18,
      premium: 300,
      purchase_date: '2024-02-14',
      redemption_deadline: '2026-02-14',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-007',
      certificate_number: 'MD-2024-1156',
      property_address: '234 Biscayne Dr, Miami Beach, FL 33139',
      parcel_id: '02-3241-008-0120',
      county: 'Miami-Dade',
      state: 'FL',
      purchase_amount: 4200,
      interest_rate: 18,
      premium: 50,
      purchase_date: '2024-07-03',
      redemption_deadline: '2026-07-03',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-008',
      certificate_number: 'BR-2024-2345',
      property_address: '678 Flamingo Rd, Pembroke Pines, FL 33028',
      parcel_id: '51-40-04-02-0560',
      county: 'Broward',
      state: 'FL',
      purchase_amount: 6300,
      interest_rate: 18,
      premium: 150,
      purchase_date: '2024-01-25',
      redemption_deadline: '2026-01-25',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-009',
      certificate_number: 'PB-2023-3456',
      property_address: '901 Royal Palm Way, Palm Beach, FL 33480',
      parcel_id: '50-43-43-02-00-000',
      county: 'Palm Beach',
      state: 'FL',
      purchase_amount: 3500,
      interest_rate: 18,
      premium: 75,
      purchase_date: '2023-09-18',
      redemption_deadline: '2025-09-18',
      tax_year: 2022,
      status: 'redeemed',
    },
    {
      id: 'lien-010',
      certificate_number: 'MD-2024-0234',
      property_address: '445 Collins Ave, Miami Beach, FL 33140',
      parcel_id: '02-3242-015-0780',
      county: 'Miami-Dade',
      state: 'FL',
      purchase_amount: 2800,
      interest_rate: 18,
      premium: 25,
      purchase_date: '2024-08-12',
      redemption_deadline: '2026-08-12',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-011',
      certificate_number: 'BR-2024-5678',
      property_address: '112 Las Olas Blvd, Fort Lauderdale, FL 33301',
      parcel_id: '50-42-06-08-0340',
      county: 'Broward',
      state: 'FL',
      purchase_amount: 11200,
      interest_rate: 18,
      premium: 450,
      purchase_date: '2024-04-30',
      redemption_deadline: '2026-04-30',
      tax_year: 2023,
      status: 'active',
    },
    {
      id: 'lien-012',
      certificate_number: 'PB-2024-6789',
      property_address: '333 Clematis St, West Palm Beach, FL 33401',
      parcel_id: '74-43-43-18-14-001',
      county: 'Palm Beach',
      state: 'FL',
      purchase_amount: 2500,
      interest_rate: 18,
      premium: 50,
      purchase_date: '2024-06-28',
      redemption_deadline: '2026-06-28',
      tax_year: 2023,
      status: 'active',
    },
  ],

  chartData: [
    { month: 'Dec 2023', revenue: 0, interest: 0 },
    { month: 'Jan 2024', revenue: 5200, interest: 420 },
    { month: 'Feb 2024', revenue: 14700, interest: 1180 },
    { month: 'Mar 2024', revenue: 26700, interest: 2650 },
    { month: 'Apr 2024', revenue: 53900, interest: 4320 },
    { month: 'May 2024', revenue: 62400, interest: 5890 },
    { month: 'Jun 2024', revenue: 70100, interest: 7450 },
    { month: 'Jul 2024', revenue: 74300, interest: 8920 },
    { month: 'Aug 2024', revenue: 77100, interest: 10280 },
    { month: 'Sep 2024', revenue: 77100, interest: 11540 },
    { month: 'Oct 2024', revenue: 87500, interest: 12890 },
    { month: 'Nov 2024', revenue: 87500, interest: 14230 },
  ],

  payments: {
    'lien-005': [
      { date: '2024-08-15', amount: 8760, type: 'Redemption' },
    ],
    'lien-009': [
      { date: '2024-06-22', amount: 4025, type: 'Redemption' },
    ],
  },
};

class ApiClient {
  constructor() {
    this.tenantId = DEFAULT_TENANT;
  }

  setTenantId(tenantId) {
    this.tenantId = tenantId;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-Tenant-ID': this.tenantId,
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Liens
  async getLiens(params = {}) {
    if (USE_MOCK_DATA) {
      let liens = [...mockData.liens];
      if (params.status && params.status !== 'all') {
        liens = liens.filter(l => l.status === params.status);
      }
      if (params.limit) {
        liens = liens.slice(0, parseInt(params.limit));
      }
      return liens;
    }
    const queryString = new URLSearchParams(params).toString();
    const response = await this.request(`/liens${queryString ? `?${queryString}` : ''}`);

    // Handle API response format: {liens: [...], count: number, ...}
    // Return just the liens array for consistency with mock data
    if (response && typeof response === 'object') {
      if (Array.isArray(response)) {
        return response; // Already an array
      }
      if (Array.isArray(response.liens)) {
        return response.liens; // Extract liens array
      }
      if (Array.isArray(response.data?.liens)) {
        return response.data.liens; // Handle wrapped response
      }
    }

    // Fallback: return empty array on unexpected format
    console.error('Unexpected API response format for getLiens:', response);
    return [];
  }

  async getLien(lienId) {
    if (USE_MOCK_DATA) {
      const lien = mockData.liens.find(l => l.id === lienId);
      if (!lien) throw new Error('Lien not found');
      return lien;
    }
    return this.request(`/liens/${lienId}`);
  }

  async createLien(data) {
    if (USE_MOCK_DATA) {
      const newLien = { id: `lien-${Date.now()}`, ...data };
      mockData.liens.push(newLien);
      return newLien;
    }
    return this.request('/liens', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateLien(lienId, data) {
    if (USE_MOCK_DATA) {
      const index = mockData.liens.findIndex(l => l.id === lienId);
      if (index === -1) throw new Error('Lien not found');
      mockData.liens[index] = { ...mockData.liens[index], ...data };
      return mockData.liens[index];
    }
    return this.request(`/liens/${lienId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteLien(lienId) {
    if (USE_MOCK_DATA) {
      const index = mockData.liens.findIndex(l => l.id === lienId);
      if (index === -1) throw new Error('Lien not found');
      mockData.liens.splice(index, 1);
      return { success: true };
    }
    return this.request(`/liens/${lienId}`, {
      method: 'DELETE',
    });
  }

  // Interest calculation
  async calculateInterest(lienId) {
    if (USE_MOCK_DATA) {
      const lien = mockData.liens.find(l => l.id === lienId);
      if (!lien) throw new Error('Lien not found');

      const purchaseDate = new Date(lien.purchase_date);
      const today = new Date();
      const daysHeld = Math.floor((today - purchaseDate) / (1000 * 60 * 60 * 24));
      const dailyRate = lien.interest_rate / 100 / 365;
      const accruedInterest = lien.purchase_amount * dailyRate * daysHeld;

      return {
        lien_id: lienId,
        days_held: daysHeld,
        accrued_interest: accruedInterest,
        total_value: lien.purchase_amount + accruedInterest,
        calculation_date: today.toISOString(),
      };
    }
    return this.request(`/liens/${lienId}/interest`);
  }

  // Payments
  async getPayments(lienId) {
    if (USE_MOCK_DATA) {
      return mockData.payments[lienId] || [];
    }
    return this.request(`/liens/${lienId}/payments`);
  }

  async recordPayment(lienId, data) {
    if (USE_MOCK_DATA) {
      if (!mockData.payments[lienId]) {
        mockData.payments[lienId] = [];
      }
      mockData.payments[lienId].push(data);
      return data;
    }
    return this.request(`/liens/${lienId}/payments`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Deadlines
  async getDeadlines(params = {}) {
    if (USE_MOCK_DATA) {
      return mockData.liens
        .filter(l => l.status === 'active')
        .map(l => ({
          id: `deadline-${l.id}`,
          lien_id: l.id,
          type: 'redemption',
          due_date: l.redemption_deadline,
          description: `Redemption deadline for ${l.certificate_number}`,
        }))
        .slice(0, 5);
    }
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/deadlines${queryString ? `?${queryString}` : ''}`);
  }

  async getUpcomingDeadlines(days = 90) {
    if (USE_MOCK_DATA) {
      const now = new Date();
      const futureDate = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);

      return mockData.liens
        .filter(l => {
          if (l.status !== 'active') return false;
          const deadline = new Date(l.redemption_deadline);
          return deadline >= now && deadline <= futureDate;
        })
        .map(l => {
          const deadline = new Date(l.redemption_deadline);
          const daysRemaining = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));

          return {
            deadline_id: `deadline-${l.id}`,
            lien_id: l.id,
            certificate_number: l.certificate_number,
            property_address: l.property_address,
            deadline_type: 'redemption',
            deadline_date: l.redemption_deadline,
            days_remaining: daysRemaining,
            description: `Redemption period ends`,
            status: 'pending',
            created_at: l.purchase_date,
          };
        })
        .sort((a, b) => a.days_remaining - b.days_remaining);
    }

    const response = await this.request(`/deadlines/upcoming?days=${days}`);

    // Handle wrapped response
    if (response?.data) {
      return response.data;
    }
    return response;
  }

  async createDeadline(data) {
    if (USE_MOCK_DATA) {
      return { id: `deadline-${Date.now()}`, ...data };
    }
    return this.request('/deadlines', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async markDeadlineCompleted(deadlineId) {
    if (USE_MOCK_DATA) {
      return { success: true };
    }
    return this.request(`/deadlines/${deadlineId}/complete`, {
      method: 'PUT',
    });
  }

  // Portfolio
  async getPortfolioSummary() {
    if (USE_MOCK_DATA) {
      return mockData.portfolioStats;
    }
    const response = await this.request('/portfolio/summary');

    // Handle API response format: return data directly or extract from wrapper
    if (response && typeof response === 'object') {
      // If wrapped in {success: true, data: {...}}, extract data
      if (response.data && typeof response.data === 'object') {
        return response.data;
      }
      // Otherwise return as-is
      return response;
    }

    // Fallback
    console.error('Unexpected API response format for getPortfolioSummary:', response);
    return null;
  }

  async getPortfolioAnalytics() {
    if (USE_MOCK_DATA) {
      return {
        chart_data: mockData.chartData,
        liens_by_county: {
          'Miami-Dade': 4,
          'Broward': 4,
          'Palm Beach': 4,
        },
        liens_by_status: {
          active: 10,
          redeemed: 2,
        },
      };
    }
    return this.request('/portfolio/analytics');
  }

  // Notifications
  async getNotifications(params = {}) {
    if (USE_MOCK_DATA) {
      return {
        notifications: [
          {
            notification_id: 'notif-001',
            notification_type: 'deadline_approaching',
            title: 'Deadline Approaching',
            message: 'Redemption deadline approaching for MD-2024-0847 in 5 days',
            lien_id: 'lien-001',
            priority: 'high',
            created_at: new Date().toISOString(),
            read: false,
          },
          {
            notification_id: 'notif-002',
            notification_type: 'payment_received',
            title: 'Payment Received',
            message: 'Payment received for BR-2023-4521',
            lien_id: 'lien-005',
            priority: 'normal',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            read: true,
          },
          {
            notification_id: 'notif-003',
            notification_type: 'lien_created',
            title: 'New Lien Created',
            message: 'Successfully created lien for 890 Ocean Blvd',
            lien_id: 'lien-006',
            priority: 'normal',
            created_at: new Date(Date.now() - 172800000).toISOString(),
            read: false,
          },
        ],
        count: 3,
        unread_count: 2,
      };
    }
    const queryString = new URLSearchParams(params).toString();
    const response = await this.request(`/notifications${queryString ? `?${queryString}` : ''}`);

    // Handle wrapped response
    if (response?.data) {
      return response.data;
    }
    return response;
  }

  async markNotificationRead(notificationId) {
    if (USE_MOCK_DATA) {
      return { success: true };
    }
    return this.request(`/notifications/${notificationId}/read`, {
      method: 'PUT',
    });
  }

  async getUnreadNotificationCount() {
    if (USE_MOCK_DATA) {
      return { count: 2 };
    }
    const response = await this.getNotifications({ unread_only: true });
    return { count: response?.unread_count || response?.notifications?.length || 0 };
  }

  // Documents
  async generateDocument(type, data) {
    if (USE_MOCK_DATA) {
      return {
        id: `doc-${Date.now()}`,
        type,
        content: '<html><body>Mock document content</body></html>',
        created_at: new Date().toISOString(),
      };
    }
    return this.request('/documents/generate', {
      method: 'POST',
      body: JSON.stringify({ type, ...data }),
    });
  }

  async getDocuments(lienId) {
    if (USE_MOCK_DATA) {
      return [];
    }
    return this.request(`/liens/${lienId}/documents`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
