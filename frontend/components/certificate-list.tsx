"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Download, FileText, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface Certificate {
  domain: string
  file: string
}

export function CertificateList() {
  const [certificates, setCertificates] = useState<Certificate[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  const fetchCertificates = async () => {
    try {
      const response = await fetch("/api/cert")
      if (!response.ok) {
        throw new Error("인증서 목록을 불러오는데 실패했습니다.")
      }
      const data = await response.json()
      setCertificates(data.certificates || [])
    } catch (error) {
      toast({
        title: "오류",
        description: error instanceof Error ? error.message : "인증서 목록을 불러오는데 실패했습니다.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCertificates()

    const handleCertCreated = () => {
      fetchCertificates()
    }
    window.addEventListener("certificateCreated", handleCertCreated)
    return () => window.removeEventListener("certificateCreated", handleCertCreated)
  }, [])

  const downloadCertificate = (domain: string) => {
    const element = document.createElement("a")
    element.href = `/api/cert/${domain}`
    element.download = `${domain}.zip`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)

    toast({
      title: "다운로드 시작",
      description: `${domain}.zip 파일을 다운로드합니다.`,
    })
  }

  if (isLoading) {
    return (
      <Card className="flex items-center justify-center p-12">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </Card>
    )
  }

  return (
    <>
      {certificates.length === 0 ? (
        <Card className="p-12 text-center">
          <FileText className="mx-auto mb-3 size-12 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">{"발급된 인증서가 없습니다."}</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {certificates.map((cert) => (
            <Card key={cert.domain} className="p-4">
              <div className="flex items-center justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="truncate font-mono text-sm font-medium text-foreground">{cert.domain}</p>
                  <p className="text-xs text-muted-foreground">{cert.file}</p>
                </div>
                <Button size="sm" variant="outline" onClick={() => downloadCertificate(cert.domain)}>
                  <Download className="mr-2 size-4" />
                  {"다운로드"}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </>
  )
}
