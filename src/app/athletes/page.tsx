import { Metadata } from 'next';
import AthletesClient from './AthletesClient';

export const metadata: Metadata = {
  title: 'Our Athletes | PURE Health Supps',
  description: 'Meet the athletes who represent PURE. Driven, disciplined, and never finished.',
};

export default function AthletesPage() {
  return <AthletesClient />;
}
