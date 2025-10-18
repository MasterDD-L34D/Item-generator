import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Sparkles, Search, Dice6, Loader2, Scroll, Coins } from "lucide-react";
import { APP_TITLE } from "@/const";

// Mappa emoji per slot
const SLOT_EMOJI: Record<string, string> = {
  Head: "🎩",
  Headband: "👑",
  Eyes: "👁️",
  Shoulders: "🧥",
  Neck: "📿",
  Chest: "🛡️",
  Body: "👕",
  Belt: "🔗",
  Wrists: "⌚",
  Hands: "🧤",
  Ring: "💍",
  Feet: "👢",
  "—": "✨",
};

// Mappa emoji per categoria
const CATEGORY_EMOJI: Record<string, string> = {
  "Wondrous Item": "✨",
  Weapon: "⚔️",
  Armor: "🛡️",
  Ring: "💍",
  Rod: "🪄",
  Staff: "🏹",
  Scroll: "📜",
  Potion: "🧪",
  Wand: "🪄",
};

export default function Generator() {
  const [generatePrompt, setGeneratePrompt] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [generatedItem, setGeneratedItem] = useState<any>(null);

  const generateMutation = trpc.items.generate.useMutation();
  const { data: searchResults, refetch: searchRefetch, isLoading: searchLoading } = trpc.items.search.useQuery(
    { query: searchQuery, limit: 5 },
    { enabled: false }
  );
  const { data: randomItems, refetch: randomRefetch } = trpc.items.random.useQuery({ count: 3 });

  const handleGenerate = async () => {
    if (!generatePrompt.trim()) return;
    try {
      console.log('🔄 Avvio generazione...');
      const result = await generateMutation.mutateAsync({ prompt: generatePrompt });
      console.log('✅ Risposta ricevuta:', result);
      if (result.success && result.item) {
        setGeneratedItem(result.item);
      } else {
        console.error('❌ Generazione fallita:', result);
        alert('Errore nella generazione: ' + (result.error || 'Errore sconosciuto'));
      }
    } catch (error) {
      console.error('❌ Errore durante la generazione:', error);
      alert('Errore durante la generazione: ' + (error instanceof Error ? error.message : 'Errore sconosciuto'));
    }
  };

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    searchRefetch();
  };

  // Componente per visualizzare un oggetto in Formato Torneo
  const TournamentItemCard = ({ item }: { item: any }) => {
    const slotEmoji = SLOT_EMOJI[item.slot] || "✨";
    const categoryEmoji = CATEGORY_EMOJI[item.category] || "✨";

    return (
      <Card className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 border-purple-400/30">
        <CardHeader className="pb-3">
          {/* Titolo con emoji */}
          <CardTitle className="text-white text-xl flex items-center gap-2">
            {slotEmoji} {item.name}
          </CardTitle>
          
          {/* Metadati */}
          <div className="text-sm text-purple-200 space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span>📦 {item.slot}</span>
              <span>•</span>
              <span>LI {item.casterLevel}°</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Coins className="w-3 h-3" />
                {item.price.toLocaleString()} gp
              </span>
              <span>•</span>
              <span>Peso {item.weight}</span>
              <span>•</span>
              <Badge variant="outline" className="text-purple-300 border-purple-400">
                {item.rarity}
              </Badge>
              <span>{categoryEmoji}</span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-3 text-white/90">
          {/* Aura/Scuola */}
          <p className="text-sm">
            <strong className="text-purple-300">Aura/Scuola:</strong> {item.auraIntensity}, {item.school}
          </p>

          {/* Descrizione (flavour) */}
          <p className="text-sm italic text-white/80 border-l-2 border-purple-400/50 pl-3">
            {item.description}
          </p>

          <Separator className="bg-white/10" />

          {/* Uso/Attivazione */}
          <div className="text-sm space-y-1">
            <p>
              <strong className="text-purple-300">Uso/Attivazione:</strong> Azione <strong>{item.activationAction}</strong>
              {item.usesPerDay && ` • Usi: ${item.usesPerDay}`}
            </p>
            <p>
              <strong className="text-purple-300">Durata:</strong> {item.duration}
              {" • "}
              <strong className="text-purple-300">TS:</strong> {item.savingThrow}
              {" • "}
              <strong className="text-purple-300">SR:</strong> {item.spellResistance}
              {item.referencedSpell && ` (come ${item.referencedSpell})`}
            </p>
          </div>

          {/* Effetto */}
          <p className="text-sm">
            <strong className="text-purple-300">Effetto:</strong> {item.effect}
          </p>

          {/* Dettaglio */}
          {item.details && item.details.length > 0 && (
            <div className="text-sm">
              <strong className="text-purple-300">Dettaglio:</strong>
              <ul className="list-disc list-inside space-y-1 mt-1 ml-2">
                {item.details.map((detail: string, idx: number) => (
                  <li key={idx} className="text-white/80">{detail}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Interazioni */}
          <p className="text-sm">
            <strong className="text-purple-300">Interazioni:</strong> {item.stacking}
            {item.bonusType && ` (Tipo bonus: ${item.bonusType})`}
            {" "}
            <Badge variant="outline" className="text-xs text-purple-300 border-purple-400 ml-1">
              {item.rawTag}
            </Badge>
          </p>

          <Separator className="bg-white/10" />

          {/* Costruzione */}
          <div className="text-sm space-y-1">
            <p>
              <strong className="text-purple-300">Costruzione:</strong> {item.craftingRequirements}
            </p>
            <p>
              <strong className="text-purple-300">Costo:</strong> {item.craftingCost.toLocaleString()} gp
            </p>
          </div>

          {/* Nota Playtest */}
          <div className="bg-yellow-900/20 border border-yellow-600/30 rounded p-2 text-xs">
            <strong className="text-yellow-400">⚠️ Nota Playtest:</strong> {item.playtestNote}
          </div>

          {/* Spunto narrativo (opzionale) */}
          {item.narrativeHook && (
            <p className="text-xs italic text-purple-300 border-t border-white/10 pt-2">
              <Scroll className="w-3 h-3 inline mr-1" />
              {item.narrativeHook}
            </p>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-400" />
            {APP_TITLE}
          </h1>
          <p className="text-sm text-purple-200 mt-1">Genera e cerca oggetti magici per Pathfinder 1E • Formato Torneo</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="generate" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-3 mb-8">
            <TabsTrigger value="generate">
              <Sparkles className="w-4 h-4 mr-2" />
              Genera
            </TabsTrigger>
            <TabsTrigger value="search">
              <Search className="w-4 h-4 mr-2" />
              Cerca
            </TabsTrigger>
            <TabsTrigger value="random">
              <Dice6 className="w-4 h-4 mr-2" />
              Casuale
            </TabsTrigger>
          </TabsList>

          {/* Generate Tab */}
          <TabsContent value="generate" className="space-y-6">
            <Card className="max-w-2xl mx-auto bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Genera Nuovo Oggetto</CardTitle>
                <CardDescription className="text-purple-200">
                  Descrivi l'oggetto magico che vuoi creare (conforme a Pathfinder 1E RAW)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Es: Una spada fiammeggiante che aumenta la forza del portatore..."
                  value={generatePrompt}
                  onChange={(e) => setGeneratePrompt(e.target.value)}
                  className="min-h-[100px] bg-white/5 border-white/20 text-white placeholder:text-white/40"
                />
                <Button
                  onClick={handleGenerate}
                  disabled={generateMutation.isPending || !generatePrompt.trim()}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {generateMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generazione in corso...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Genera Oggetto
                    </>
                  )}
                </Button>

                {/* Generated Item Display */}
                {generatedItem && (
                  <div className="mt-6">
                    <TournamentItemCard item={generatedItem} />
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Search Tab */}
          <TabsContent value="search" className="space-y-6">
            <Card className="max-w-2xl mx-auto bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Cerca Oggetti</CardTitle>
                <CardDescription className="text-purple-200">
                  Cerca oggetti magici esistenti nel database
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Es: spada di fuoco, anello di protezione..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                  <Button
                    onClick={handleSearch}
                    disabled={searchLoading || !searchQuery.trim()}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {searchLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </Button>
                </div>

                {/* Search Results */}
                {searchResults && searchResults.success && searchResults.items.length > 0 && (
                  <div className="space-y-3 mt-6">
                    {searchResults.items.map((item: any, idx: number) => (
                      <Card key={idx} className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-white text-lg">{item.name}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-white/80 text-sm line-clamp-2">{item.description}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {searchResults && searchResults.success && searchResults.items.length === 0 && (
                  <p className="text-center text-white/60 py-8">Nessun risultato trovato</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Random Tab */}
          <TabsContent value="random" className="space-y-6">
            <Card className="max-w-2xl mx-auto bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Oggetti Casuali</CardTitle>
                <CardDescription className="text-purple-200">
                  Lasciati ispirare da oggetti casuali dal database
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={() => randomRefetch()}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  <Dice6 className="w-4 h-4 mr-2" />
                  Genera Nuovi Oggetti Casuali
                </Button>

                {randomItems && randomItems.success && (
                  <div className="space-y-3 mt-6">
                    {randomItems.items.map((item: any, idx: number) => (
                      <Card key={idx} className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-purple-400/20">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-white text-lg">{item.name}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-white/80 text-sm">{item.description}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

