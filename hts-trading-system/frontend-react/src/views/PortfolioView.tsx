import React from 'react';

interface Props {
  priceData: Map<string, any>;
}

const PortfolioView: React.FC<Props> = ({ priceData }) => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Portfolio Management</h1>
      <p className="text-gray-400">
        Track your positions and monitor performance
      </p>
      {/* Add portfolio components here in Phase 2 */}
    </div>
  );
};

export default PortfolioView;
