import { Metadata } from 'next';
import WholesaleClient from './WholesaleClient';

export const metadata: Metadata = {
  title: 'Wholesale & Retails | PURE Health Supps',
  description: 'Partner with PURE. Competitive margins, marketing support, and fast logistics for retail partners, gym owners, and distributors across India.',
};

export default function WholesalePage() {
  return <WholesaleClient />;
}
