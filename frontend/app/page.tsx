import { CertificateList } from "@/components/certificate-list"
import { CertificateForm } from "@/components/certificate-form"
import { Shield } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-primary">
              <Shield className="size-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-balance text-2xl font-semibold tracking-tight text-foreground">
                Private CA Certificate Manager
              </h1>
              <p className="text-sm text-muted-foreground">Kawaii Beer Networks</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Certificate Form */}
          <div className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-balance text-xl font-semibold tracking-tight text-foreground">인증서 발급</h2>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Root CA로 서명된 새로운 도메인 인증서를 발급합니다.
              </p>
            </div>
            <CertificateForm />
          </div>

          {/* Certificate List */}
          <div className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-balance text-xl font-semibold tracking-tight text-foreground">인증서 목록</h2>
              <p className="text-sm leading-relaxed text-muted-foreground">발급된 모든 인증서를 조회하고 관리합니다.</p>
            </div>
            <CertificateList />
          </div>
        </div>
      </main>
    </div>
  )
}
