import { NextResponse } from "next/server"

const API_BASE_URL = process.env.CERT_API_URL || "http://localhost:8000"

// GET /api/cert - List all certificates
export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/cert`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      throw new Error("Failed to fetch certificates")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching certificates:", error)
    const errorMessage =
      error instanceof Error
        ? error.message.includes("aborted")
          ? "Backend API timeout"
          : error.message
        : "Failed to fetch certificates"
    return NextResponse.json({ detail: errorMessage, certificates: [] }, { status: 500 })
  }
}

// POST /api/cert - Create new certificate
export async function POST(request: Request) {
  const body = await request.json()

  try {
    const response = await fetch(`${API_BASE_URL}/cert`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data, { status: 201 })
  } catch (error) {
    console.error("Error creating certificate:", error)
    const errorMessage =
      error instanceof Error
        ? error.message.includes("aborted")
          ? "Backend API timeout"
          : error.message
        : "Failed to create certificate"
    return NextResponse.json({ detail: errorMessage }, { status: 500 })
  }
}
