import { NextRequest, NextResponse } from 'next/server';
import { csvService } from '@/lib/csvService';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const query = formData.get('query') as string;

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    const result = await csvService.search(query.trim());
    return NextResponse.json(result);
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST.' },
    { status: 405 }
  );
}