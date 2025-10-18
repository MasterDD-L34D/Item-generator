import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { APP_TITLE } from "@/const";

export default function Home() {
  const { data: healthData, isLoading: healthLoading, error: healthError } = trpc.health.check.useQuery();
  const { data: dataStats, isLoading: dataLoading, error: dataError } = trpc.data.stats.useQuery();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">{APP_TITLE}</CardTitle>
          <CardDescription>Sistema di Test - Fase 1</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Health Check */}
          <div className="space-y-2">
            <h3 className="font-semibold text-sm text-muted-foreground">Server Status</h3>
            {healthLoading && (
              <div className="text-center text-muted-foreground">Caricamento...</div>
            )}
            {healthError && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                Errore: {healthError.message}
              </div>
            )}
            {healthData && (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                <span className="font-semibold">Status: {healthData.status}</span>
              </div>
            )}
          </div>

          {/* Data Access Test */}
          <div className="space-y-2">
            <h3 className="font-semibold text-sm text-muted-foreground">Accesso ai Dati</h3>
            {dataLoading && (
              <div className="text-center text-muted-foreground">Caricamento dati...</div>
            )}
            {dataError && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                Errore: {dataError.message}
              </div>
            )}
            {dataStats && (
              <div className="space-y-3">
                {dataStats.success ? (
                  <>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full" />
                      <span className="font-semibold">File caricato con successo</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="p-2 bg-muted rounded">
                        <p className="text-muted-foreground text-xs">Oggetti Totali</p>
                        <p className="font-bold text-lg">{dataStats.totalCount}</p>
                      </div>
                      <div className="p-2 bg-muted rounded">
                        <p className="text-muted-foreground text-xs">Tipi Unici</p>
                        <p className="font-bold text-lg">{dataStats.types.length}</p>
                      </div>
                    </div>
                    {dataStats.sampleItem && (
                      <div className="p-2 bg-muted/50 rounded text-xs">
                        <p className="font-semibold">Esempio:</p>
                        <p className="truncate">{dataStats.sampleItem.name}</p>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                    <p className="font-semibold">Errore nel caricamento:</p>
                    <p>{dataStats.error}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
