"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Plus, X, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export function CertificateForm() {
  const [domain, setDomain] = useState("")
  const [altNames, setAltNames] = useState<string[]>([])
  const [currentAlt, setCurrentAlt] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const addAltName = () => {
    if (currentAlt.trim() && !altNames.includes(currentAlt.trim())) {
      setAltNames([...altNames, currentAlt.trim()])
      setCurrentAlt("")
    }
  }

  const removeAltName = (name: string) => {
    setAltNames(altNames.filter((n) => n !== name))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!domain.trim()) {
      toast({
        title: "오류",
        description: "도메인을 입력해주세요.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch("/api/cert", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          domain: domain.trim(),
          alt_names: altNames,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        if (error.detail?.includes("ECONNREFUSED") || error.detail?.includes("fetch failed")) {
          throw new Error("백엔드 API에 연결할 수 없습니다. Python 서버가 실행 중인지 확인하세요.")
        }
        throw new Error(error.detail || "인증서 생성에 실패했습니다.")
      }

      const data = await response.json()

      toast({
        title: "성공",
        description: `${data.domain} 인증서가 생성되었습니다.`,
      })

      // Reset form
      setDomain("")
      setAltNames([])
      setCurrentAlt("")

      // Trigger refresh of certificate list
      window.dispatchEvent(new Event("certificateCreated"))
    } catch (error) {
      toast({
        title: "오류",
        description: error instanceof Error ? error.message : "인증서 생성에 실패했습니다.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="domain" className="text-foreground">
            {"도메인 *"}
          </Label>
          <Input
            id="domain"
            type="text"
            placeholder="example.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            disabled={isLoading}
            className="bg-background"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="altName" className="text-foreground">
            {"추가 도메인 (SAN)"}
          </Label>
          <div className="flex gap-2">
            <Input
              id="altName"
              type="text"
              placeholder="*.example.com"
              value={currentAlt}
              onChange={(e) => setCurrentAlt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  addAltName()
                }
              }}
              disabled={isLoading}
              className="bg-background"
            />
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={addAltName}
              disabled={isLoading || !currentAlt.trim()}
            >
              <Plus className="size-4" />
            </Button>
          </div>

          {altNames.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {altNames.map((name) => (
                <div
                  key={name}
                  className="flex items-center gap-1 rounded-md bg-secondary px-3 py-1 text-sm text-secondary-foreground"
                >
                  {name}
                  <button
                    type="button"
                    onClick={() => removeAltName(name)}
                    disabled={isLoading}
                    className="ml-1 hover:text-foreground"
                  >
                    <X className="size-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 size-4 animate-spin" />}
          {"인증서 발급"}
        </Button>
      </form>
    </Card>
  )
}
