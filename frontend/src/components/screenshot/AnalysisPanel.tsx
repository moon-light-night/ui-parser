import { Sparkles, LayoutDashboard, Layers, Bug, Lightbulb, ListChecks, Loader2 } from 'lucide-react';
import type { Analysis } from '@/proto/generated/screenshot';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { severityVariant, severityLabel, priorityVariant, priorityLabel } from '@/components/screenshot/analysisHelpers';

function AnalysisSkeleton() {
  return (
    <div className="space-y-4">
      {[80, 60, 100].map((w, i) => (
        <Card key={i} className="p-4 space-y-3">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton style={{ width: `${w}%` }} className="h-3" />
          <Skeleton className="h-3 w-3/4" />
        </Card>
      ))}
    </div>
  );
}

function Panel({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 px-4 py-3 space-y-0 border-b border-border">
        <span className="text-muted-foreground [&>svg]:w-4 [&>svg]:h-4">{icon}</span>
        <h2 className="text-sm font-semibold text-foreground">{title}</h2>
      </CardHeader>
      <CardContent className="p-4">{children}</CardContent>
    </Card>
  );
}

interface AnalysisPanelProps {
  analysis: Analysis | null;
  loading: boolean;
  isAnalyzing: boolean;
}

export function AnalysisPanel({ analysis, loading, isAnalyzing }: AnalysisPanelProps) {
  return (
    <div className="space-y-4">
      {loading && <AnalysisSkeleton />}

      {!loading && isAnalyzing && (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <Loader2 className="w-8 h-8 text-muted-foreground animate-spin" />
          <p className="text-sm text-muted-foreground">Анализ выполняется…</p>
        </div>
      )}

      {!loading && !isAnalyzing && !analysis && (
        <Card className="p-8 flex flex-col items-center text-center gap-3">
          <div className="w-12 h-12 bg-muted rounded-xl flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-muted-foreground" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">Анализ не выполнялся</p>
          </div>
        </Card>
      )}

      {!loading && !isAnalyzing && analysis && (
        <>
          <Panel icon={<LayoutDashboard />} title="Summary">
            <p className="text-sm text-muted-foreground leading-relaxed">
              {analysis.summary || 'Описание недоступно'}
            </p>
            <div className="flex items-center gap-2 mt-3">
              {analysis.screenType && (
                <Badge variant="purple">{analysis.screenType.replace('_', ' ')}</Badge>
              )}
              {analysis.modelName && (
                <span className="text-xs text-muted-foreground">{analysis.modelName}</span>
              )}
            </div>
          </Panel>

          {analysis.sections?.length > 0 && (
            <Panel icon={<Layers />} title={`Sections (${analysis.sections.length})`}>
              <ul className="space-y-2">
                {analysis.sections.map((s, i) => (
                  <li key={i} className="text-sm">
                    <span className="font-medium text-foreground">{s.name}</span>
                    {s.description && (
                      <span className="text-muted-foreground"> — {s.description}</span>
                    )}
                  </li>
                ))}
              </ul>
            </Panel>
          )}

          {analysis.uiIssues?.length > 0 && (
            <Panel icon={<Bug />} title={`UI Issues (${analysis.uiIssues.length})`}>
              <ul className="space-y-3">
                {analysis.uiIssues.map((issue, i) => (
                  <li key={i} className="border border-border rounded-lg p-3 space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground flex-1">{issue.title}</span>
                      <Badge variant={severityVariant(issue.severity)}>
                        {severityLabel(issue.severity)}
                      </Badge>
                    </div>
                    {issue.description && (
                      <p className="text-xs text-muted-foreground">{issue.description}</p>
                    )}
                    {issue.evidence && (
                      <p className="text-xs text-gray-400 italic">"{issue.evidence}"</p>
                    )}
                    {issue.recommendation && (
                      <p className="text-xs text-blue-600 font-medium">→ {issue.recommendation}</p>
                    )}
                  </li>
                ))}
              </ul>
            </Panel>
          )}

          {analysis.uxSuggestions?.length > 0 && (
            <Panel icon={<Lightbulb />} title={`UX Suggestions (${analysis.uxSuggestions.length})`}>
              <ul className="space-y-3">
                {analysis.uxSuggestions.map((s, i) => (
                  <li key={i} className="text-sm">
                    <p className="font-medium text-foreground">{s.title}</p>
                    {s.description && (
                      <p className="text-xs text-muted-foreground mt-0.5">{s.description}</p>
                    )}
                  </li>
                ))}
              </ul>
            </Panel>
          )}

          {analysis.implementationTasks?.length > 0 && (
            <Panel icon={<ListChecks />} title={`Tasks (${analysis.implementationTasks.length})`}>
              <ul className="space-y-3">
                {analysis.implementationTasks.map((t, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm">
                    <Badge variant={priorityVariant(t.priority)} className="mt-0.5 shrink-0">
                      {priorityLabel(t.priority)}
                    </Badge>
                    <div>
                      <p className="font-medium text-foreground">{t.title}</p>
                      {t.description && (
                        <p className="text-xs text-muted-foreground mt-0.5">{t.description}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </Panel>
          )}
        </>
      )}
    </div>
  );
}
