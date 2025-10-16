import React from 'react';

interface Props {
  selectedSymbol: string;
  priceData: Map<string, any>;
}

const ChartView: React.FC<Props> = ({ selectedSymbol, priceData }) => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Advanced Charts</h1>
      <p className="text-gray-400">
        Select a cryptocurrency to view detailed price charts and analysis
      </p>
      {/* Add detailed chart components here in Phase 2 */}
    </div>
  );
};

export default ChartView;
