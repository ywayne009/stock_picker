export interface Strategy {
  id: number;
  name: string;
  description: string;
  category: 'technical' | 'quantitative' | 'ml' | 'ai-generated';
  parameters: Record<string, any>;
  createdAt: string;
  creator: 'user' | 'ai';
  performanceMetrics?: PerformanceMetrics;
}

export interface PerformanceMetrics {
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
}
