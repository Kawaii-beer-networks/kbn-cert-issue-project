import { NextResponse } from "next/server"

const API_BASE_URL = process.env.CERT_API_URL || "http://localhost:8000"

// GET /api/cert/[domain] - Get certificate content
export async function GET(request: Request, { params }: { params: Promise<{ domain: string }> }) {
  const { domain } = await params

  try {
    const response = await fetch(`${API_BASE_URL}/cert/${domain}`, {
      method: "GET",
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json({ detail: "Certificate not found" }, { status: 404 })
      }
      throw new Error("Failed to fetch certificate")
    }

    const content = await response.text()
    return new NextResponse(content, {
      headers: {
        "Content-Type": "text/plain",
      },
    })
  } catch (error) {
    console.error("Error fetching certificate:", error)
    const errorMessage =
      error instanceof Error
        ? error.message.includes("aborted")
          ? "Backend API timeout"
          : error.message
        : "Failed to fetch certificate"
    return NextResponse.json({ detail: errorMessage }, { status: 500 })
  }
}
