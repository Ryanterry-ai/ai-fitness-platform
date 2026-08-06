import { Metadata } from 'next';
import JournalClient from './JournalClient';

export const metadata: Metadata = {
  title: 'Journal — Training Tips & Nutrition Science | PURE HEALTH SUPPS',
  description: 'Training tips, nutrition science, and athlete stories from PURE HEALTH SUPPS. Learn from the experts who built PRIME X.',
};

export default function JournalPage() {
  return <JournalClient />;
}
