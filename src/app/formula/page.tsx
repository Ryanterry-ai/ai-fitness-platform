import { Metadata } from 'next';
import FormulaClient from './FormulaClient';

export const metadata: Metadata = {
  title: 'The Formula — Ingredient Science | PURE HEALTH SUPPS',
  description: 'Explore the science behind PRIME X. 8 clinically dosed ingredients, full transparency, zero proprietary blends.',
};

export default function FormulaPage() {
  return <FormulaClient />;
}
