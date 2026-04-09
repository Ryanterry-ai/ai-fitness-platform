import type { Metadata } from "next";
import { Roboto, Oswald } from "next/font/google";
import "./globals.css";
import { CartProvider } from "@/lib/cart-context";

const roboto = Roboto({
  variable: "--font-roboto",
  subsets: ["latin"],
  weight: ["300", "400", "500", "700"],
});

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "NEED® Supplements",
  description: "Premium sports supplements - Proteins, Pre-training, Amino Acids, Vitamins & Minerals",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${roboto.variable} ${oswald.variable} h-full antialiased`}
    >
      <body className={`${roboto.variable} ${oswald.variable} min-h-full flex flex-col font-roboto`}>
        <CartProvider>
          {children}
        </CartProvider>
      </body>
    </html>
  );
}
