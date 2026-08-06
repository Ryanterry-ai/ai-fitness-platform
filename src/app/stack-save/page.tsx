import { Metadata } from 'next';
import StackSaveClient from './StackSaveClient';

export const metadata: Metadata = {
  title: 'Stack & Save — Bundle Pricing | PURE HEALTH SUPPS',
  description: 'Bundle all three PRIME X flavours and save up to ₹1,298. The Trainer\'s Tray — 240 servings, one order, free shipping.',
};

export default function StackSavePage() {
  return <StackSaveClient />;
}
