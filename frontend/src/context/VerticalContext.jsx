import React, { createContext, useContext, useState } from 'react';

const VerticalContext = createContext();

export function VerticalProvider({ children }) {
  // Default to 'tax_lien'
  const [currentVertical, setCurrentVertical] = useState('tax_lien');

  const value = {
    currentVertical,
    setCurrentVertical,
    // Helper to get readable names
    getVerticalName: () => {
      const names = {
        tax_lien: 'Tax Liens',
        civil_judgment: 'Civil Judgments',
        probate: 'Probate',
        mineral_rights: 'Mineral Rights',
        surplus_funds: 'Surplus Funds'
      };
      return names[currentVertical] || 'Assets';
    }
  };

  return (
    <VerticalContext.Provider value={value}>
      {children}
    </VerticalContext.Provider>
  );
}

export function useVertical() {
  return useContext(VerticalContext);
}