import { NextResponse } from "next/server";

let cart: any[] = [];

export async function GET() {
  return NextResponse.json(cart);
}

export async function POST(request: Request) {
  const body = await request.json();
  const { productId, quantity, flavor } = body;
  
  const existingItem = cart.find(item => item.productId === productId && item.flavor === flavor);
  
  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    cart.push({ productId, quantity, flavor });
  }
  
  return NextResponse.json(cart);
}

export async function DELETE(request: Request) {
  const body = await request.json();
  const { productId } = body;
  cart = cart.filter(item => item.productId !== productId);
  return NextResponse.json(cart);
}
