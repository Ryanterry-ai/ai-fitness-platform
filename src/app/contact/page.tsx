import { Metadata } from 'next';
import ContactClient from './ContactClient';

export const metadata: Metadata = {
  title: 'Contact Us — PURE HEALTH SUPPS',
  description: 'Get in touch with PURE HEALTH SUPPS. Questions about PRIME X? Wholesale enquiries? We are here to help.',
};

export default function ContactPage() {
  return <ContactClient />;
}
