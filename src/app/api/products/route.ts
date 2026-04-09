import { NextResponse } from "next/server";
import { products } from "@/lib/data";

export async function GET() {
  return NextResponse.json(products);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newProduct = {
    id: products.length + 1,
    ...body,
  };
  products.push(newProduct);
  return NextResponse.json(newProduct, { status: 201 });
}
