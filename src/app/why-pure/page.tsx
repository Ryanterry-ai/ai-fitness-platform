import { Metadata } from 'next';
import WhyPureClient from './WhyPureClient';

export const metadata: Metadata = {
  title: 'Why PURE — Transparent Pre-Workout | PURE HEALTH SUPPS',
  description: 'Learn why PURE HEALTH SUPPS is different. Full transparency, clinical doses, zero proprietary blends. Every ingredient on the label.',
};

export default function WhyPurePage() {
  return <WhyPureClient />;
}
