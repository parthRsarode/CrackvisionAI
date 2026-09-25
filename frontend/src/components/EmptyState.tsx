import { Upload, TrendingUp } from 'lucide-react';

interface EmptyStateProps {
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({ className = '' }) => {
  return (
    <div className={`text-center py-12 ${className}`}>
      <Upload className="h-12 w-12 mx-auto mb-6 text-muted" />
      <h3 className="text-xl font-bold text-text mb-4">No analyses yet</h3>
      <p className="text-muted max-w-md mx-auto">
        Upload and analyze an image to see your crack detection history here.
      </p>
    </div>
  );
};

export default EmptyState;
