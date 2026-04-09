export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  originalPrice: number | null;
  image: string;
  category: string;
  status: string;
  flavors: string[];
  weight: string;
  proteinPerServing: string;
  servings: string;
}

export const products: Product[] = [
  {
    id: 1,
    name: "NEED PURE WHEY",
    description: "High-quality whey protein isolate for muscle recovery and growth.",
    price: 1.95,
    originalPrice: null,
    image: "/images/products/pure-whey.png",
    category: "proteins",
    status: "sold-out",
    flavors: ["Chocolate", "Vanilla", "Strawberry", "Banana"],
    weight: "1kg",
    proteinPerServing: "24g",
    servings: "33",
  },
  {
    id: 2,
    name: "NEED DIURE·6",
    description: "Advanced diuretic formula for definition and water control.",
    price: 19.50,
    originalPrice: 25.90,
    image: "/images/products/diure6.png",
    category: "weight-loss",
    status: "sold-out",
    flavors: ["Unflavored"],
    weight: "90 capsules",
    proteinPerServing: "N/A",
    servings: "45",
  },
  {
    id: 3,
    name: "NEED PURE ISO",
    description: "Premium isolate protein with zero carbs for lean muscle building.",
    price: 69.90,
    originalPrice: 104.90,
    image: "/images/products/pure-iso.png",
    category: "proteins",
    status: "sale",
    flavors: ["Chocolate", "Capuccino", "Cookies Cream", "Strawberry"],
    weight: "2.27kg (5lbs)",
    proteinPerServing: "25g",
    servings: "74",
  },
  {
    id: 4,
    name: "NEED 0·CARBS",
    description: "Zero carbohydrate protein for cutting and definition phases.",
    price: 24.90,
    originalPrice: 29.90,
    image: "/images/products/0carbs.png",
    category: "proteins",
    status: "sale",
    flavors: ["Chocolate", "Vanilla"],
    weight: "1kg",
    proteinPerServing: "24g",
    servings: "33",
  },
  {
    id: 5,
    name: "NEED POWER CREATINE",
    description: "Pure creatine monohydrate for strength and power enhancement.",
    price: 1.95,
    originalPrice: null,
    image: "/images/products/power-creatine.png",
    category: "muscle-builder",
    status: "",
    flavors: ["Cool Lemon Lime", "Fresh Cola", "Iced Strawberry", "Unflavored"],
    weight: "300g",
    proteinPerServing: "5g",
    servings: "60",
  },
  {
    id: 6,
    name: "NEED BCAAS & GLUTAMINE",
    description: "Branch chain amino acids with glutamine for recovery.",
    price: 1.95,
    originalPrice: null,
    image: "/images/products/bcaas-glutamine.png",
    category: "amino-acids",
    status: "sold-out",
    flavors: ["Watermelon", "Tropical Fruits", "Passion Fruit", "Pina Colada", "Red Grape"],
    weight: "400g",
    proteinPerServing: "10g",
    servings: "40",
  },
  {
    id: 7,
    name: "NEED PURE MASS GAINER",
    description: "High-calorie mass gainer for extreme muscle building.",
    price: 39.90,
    originalPrice: 76.90,
    image: "/images/products/mass-gainer.png",
    category: "muscle-builder",
    status: "sale",
    flavors: ["Chocolate", "Vanilla"],
    weight: "3kg",
    proteinPerServing: "32g",
    servings: "30",
  },
  {
    id: 8,
    name: "NEED TE5TO S7",
    description: "Natural testosterone booster for strength and vitality.",
    price: 24.90,
    originalPrice: 42.90,
    image: "/images/products/testo-s7.png",
    category: "muscle-builder",
    status: "sale",
    flavors: ["Unflavored"],
    weight: "120 capsules",
    proteinPerServing: "N/A",
    servings: "30",
  },
  {
    id: 9,
    name: "NEED PROTEIN MAX",
    description: "Maximum strength protein blend for advanced athletes.",
    price: 57.65,
    originalPrice: null,
    image: "/images/products/protein-max.png",
    category: "proteins",
    status: "sold-out",
    flavors: ["Chocolate", "Capuccino", "Cookies Cream", "Strawberry"],
    weight: "2.27kg (5lbs)",
    proteinPerServing: "30g",
    servings: "74",
  },
  {
    id: 10,
    name: "NEED PRE-WORKOUT EXTREME",
    description: "Maximum energy pre-workout for intense training sessions.",
    price: 29.90,
    originalPrice: 39.90,
    image: "/images/products/pre-workout.png",
    category: "pre-training",
    status: "sale",
    flavors: ["Fruit Punch", "Blue Raz", "Green Apple"],
    weight: "300g",
    proteinPerServing: "N/A",
    servings: "30",
  },
  {
    id: 11,
    name: "NEED CAFFEINE BOOST",
    description: "High caffeine pre-workout for maximum alertness.",
    price: 19.90,
    originalPrice: null,
    image: "/images/products/caffeine.png",
    category: "pre-training",
    status: "",
    flavors: ["Unflavored"],
    weight: "100 capsules",
    proteinPerServing: "200mg",
    servings: "50",
  },
  {
    id: 12,
    name: "NEED PUMP ENHANCER",
    description: "Nitric oxide booster for massive pumps.",
    price: 24.90,
    originalPrice: 34.90,
    image: "/images/products/pump.png",
    category: "pre-training",
    status: "sale",
    flavors: ["Watermelon", "Berry"],
    weight: "180 capsules",
    proteinPerServing: "N/A",
    servings: "30",
  },
  {
    id: 13,
    name: "NEED L-CARNITINE",
    description: "Fat burner and energy booster for weight loss.",
    price: 29.90,
    originalPrice: 39.90,
    image: "/images/products/l-carnitine.png",
    category: "weight-loss",
    status: "sale",
    flavors: ["Strawberry", "Watermelon"],
    weight: "500ml",
    proteinPerServing: "N/A",
    servings: "25",
  },
  {
    id: 14,
    name: "NEED FAT BURNER",
    description: "Advanced thermogenic fat burner.",
    price: 34.90,
    originalPrice: null,
    image: "/images/products/fat-burner.png",
    category: "weight-loss",
    status: "",
    flavors: ["Unflavored"],
    weight: "90 capsules",
    proteinPerServing: "N/A",
    servings: "30",
  },
  {
    id: 15,
    name: "NEED MULTIVITAMIN",
    description: "Complete daily multivitamin for health and vitality.",
    price: 19.90,
    originalPrice: 24.90,
    image: "/images/products/multivitamin.png",
    category: "vitality-and-health",
    status: "sale",
    flavors: ["Unflavored"],
    weight: "90 tablets",
    proteinPerServing: "N/A",
    servings: "30",
  },
  {
    id: 16,
    name: "NEED OMEGA-3",
    description: "Pure fish oil for heart and brain health.",
    price: 14.90,
    originalPrice: null,
    image: "/images/products/omega3.png",
    category: "vitality-and-health",
    status: "",
    flavors: ["Unflavored"],
    weight: "90 softgels",
    proteinPerServing: "N/A",
    servings: "30",
  },
  {
    id: 17,
    name: "NEED VITAMIN D3",
    description: "High potency vitamin D3 for bone health.",
    price: 9.90,
    originalPrice: null,
    image: "/images/products/vitamin-d.png",
    category: "vitality-and-health",
    status: "",
    flavors: ["Unflavored"],
    weight: "60 tablets",
    proteinPerServing: "N/A",
    servings: "60",
  },
];

export const categories = [
  { id: "proteins", name: "Proteins", href: "/collections/proteins" },
  { id: "pre-training", name: "Pre-Training", href: "/collections/pre-training" },
  { id: "muscle-builder", name: "Build Muscle", href: "/collections/muscle-builder" },
  { id: "amino-acids", name: "Amino Acids", href: "/collections/amino-acids" },
  { id: "vitality-and-health", name: "Vitamins & Minerals", href: "/collections/vitality-and-health" },
  { id: "weight-loss", name: "Weight Loss", href: "/collections/weight-loss" },
  { id: "best-sellers", name: "Best Sellers", href: "/collections/best-sellers" },
];

export const cart: any[] = [];

export function getProductsByCategory(category: string) {
  if (category === "best-sellers") {
    return products.slice(0, 8);
  }
  return products.filter(p => p.category === category);
}

export function getProductById(id: number) {
  return products.find(p => p.id === id);
}

export function searchProducts(query: string) {
  const lowerQuery = query.toLowerCase();
  return products.filter(p => 
    p.name.toLowerCase().includes(lowerQuery) ||
    p.description.toLowerCase().includes(lowerQuery)
  );
}

export const bestSellers = products.slice(0, 8);
