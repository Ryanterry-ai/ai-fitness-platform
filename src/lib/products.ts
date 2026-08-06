export interface NutritionFact {
  name: string;
  amount: string;
  unit: string;
  percentRda?: string;
}

export interface ProductFlavour {
  id: string;
  name: string;
  color: string; // Tailwind color class for accent
  image: string;
}

export interface Product {
  id: string;
  name: string;
  brand: string;
  tagline: string;
  category: string;
  description: string;
  netWeight: string;
  servings: number;
  servingSize: string;
  fssai: string;
  flavours: ProductFlavour[];
  highlights: { label: string; value: string; icon: string }[];
  nutritionFacts: NutritionFact[];
  ingredients: string;
  allergenInfo: string;
  usage: string;
  warnings: string[];
  price: number;
  originalPrice?: number;
  currency: string;
  inStock: boolean;
  badges: string[];
}

export const products: Product[] = [
  {
    id: 'primex-preworkout-orange',
    name: 'PRIME X Pre-Workout',
    brand: 'PURE HEALTH SUPPS',
    tagline: 'High-Intensity Pre-Workout',
    category: 'Pre-Workout',
    description:
      'PRIME X is a high-intensity pre-workout formula designed for serious athletes. Packed with 1.5g Beta-Alanine, 750mg Arginine HCL, and 500mg L-Citrulline to deliver explosive energy, massive pumps, and laser-sharp focus. Each serving fuels your training with clinically dosed ingredients — no filler, no compromise.',
    netWeight: '280g',
    servings: 80,
    servingSize: '3.5g (Half Scoop)',
    fssai: '10824999000028',
    flavours: [
      { id: 'orange', name: 'Orange', color: 'orange-500', image: '/products/prime-x-orange.svg' },
      { id: 'fruit-punch', name: 'Fruit Punch', color: 'red-500', image: '/products/prime-x-fruit-punch.svg' },
      { id: 'rocket-lollipop', name: 'Rocket Lollipop', color: 'purple-500', image: '/products/prime-x-rocket.png' },
    ],
    highlights: [
      { label: 'Beta-Alanine', value: '1.5G', icon: 'zap' },
      { label: 'Arginine HCL', value: '750MG', icon: 'droplets' },
      { label: 'L-Citrulline', value: '500MG', icon: 'flame' },
      { label: 'Focus', value: 'FOCUS', icon: 'target' },
      { label: 'Pump', value: 'PUMP', icon: 'heart-pulse' },
      { label: 'Energy', value: 'ENERGY', icon: 'battery-full' },
    ],
    nutritionFacts: [
      { name: 'Energy', amount: '1.24', unit: 'Kcal', percentRda: '0.062' },
      { name: 'Carbohydrate', amount: '0.28', unit: 'g' },
      { name: 'Total Sugar', amount: '0.11', unit: 'g', percentRda: '0.22' },
      { name: 'Added Sugar', amount: '0', unit: 'g', percentRda: '0' },
      { name: 'Total Fat', amount: '0', unit: 'g' },
      { name: 'Protein', amount: '0', unit: 'g' },
      { name: 'Beta Alanine', amount: '1.5', unit: 'g' },
      { name: 'Arginine HCL', amount: '750', unit: 'mg' },
      { name: 'L-Citrulline', amount: '500', unit: 'mg' },
      { name: 'L-Carnitine', amount: '250', unit: 'mg' },
      { name: 'L-Tyrosine', amount: '125', unit: 'mg' },
      { name: 'Encapsulated Caffeine', amount: '50', unit: 'mg' },
      { name: 'Coffee Bean Extract 45%', amount: '45', unit: 'mg' },
      { name: 'Garcinia Cambogia 20%', amount: '37.5', unit: 'mg' },
      { name: 'Mucuna Pruriens', amount: '30', unit: 'mg' },
      { name: 'Sodium', amount: '20', unit: 'mg', percentRda: '1' },
    ],
    ingredients:
      'Beta Alanine, Arginine HCL, L-Citrulline, L-Carnitine, L-Tyrosine, Encapsulated Caffeine, Coffee Bean Extract (45%), Garcinia Cambogia Extract (20%), Mucuna Pruriens Extract, Acidity Regulator (INS 330), Artificial Sweetener (INS 955), Added Fruit Punch Flavour (Nature-Identical Flavouring Substances), and Permitted Synthetic Food Colours [INS 129, INS 122], including Lake Colours.',
    allergenInfo:
      'Manufactured in a facility that processes milk, soy, nuts, and barley.',
    usage:
      'Take 3.5g (Half Scoop) once daily for adults, or as directed by a healthcare professional.',
    warnings: [
      'NOT FOR MEDICINAL USE',
      'Store in a cool, dry and dark place away from direct sunlight',
      'Serving size 3.5g (Half Scoop) in a day',
      'Do not exceed the recommended serving size',
      'This product is not intended to diagnose, treat, prevent, or cure any disease',
      'Store out of reach of children',
      'Pregnant and lactating women, as well as individuals with any medical condition, should consult a dietitian before consuming this product',
      'Product is not to be used as a substitute for a varied diet',
      'People who are sensitive to caffeine should avoid consuming this product',
    ],
    price: 1299,
    originalPrice: 1599,
    currency: 'INR',
    inStock: true,
    badges: ['Banned Substance Free', 'Contains Caffeine', 'FSSAI Certified'],
  },
];

export function getProductById(id: string): Product | undefined {
  return products.find(p => p.id === id);
}

export function getProductByFlavour(flavourId: string): Product | undefined {
  return products.find(p => p.flavours.some(f => f.id === flavourId));
}

export function formatPrice(price: number, currency: string = 'INR'): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(price);
}
