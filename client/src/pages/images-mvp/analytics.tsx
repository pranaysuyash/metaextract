import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  Download,
  FileJson,
  FileText,
  RefreshCw,
  Target,
  Timer,
  Upload,
  Users,
} from "lucide-react";
import { PublicLayout as Layout } from "@/components/public-layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

type CountMap = Record<string, number>;

interface AnalyticsReport {
  period: {
    range: string;
    since: string | null;
    until: string;
    limit: number;
  };
  totals: {
    events: number;
    sessions: number;
    users: number;
    firstEventAt: string | null;
    lastEventAt: string | null;
  };
  funnel: {
    landing_viewed: number;
    upload_selected: number;
    upload_rejected: number;
    analysis_started: number;
    analysis_completed: number;
    analysis_success: number;
    analysis_failed: number;
    results_viewed: number;
    paywall_viewed: number;
    paywall_previewed: number;
    paywall_clicked: number;
    purchase_completed: number;
    export_summary_downloaded: number;
    export_json_downloaded: number;
    export_full_txt_downloaded: number;
  };
  events: CountMap;
  purposes: {
    selected: CountMap;
    prompt_shown: number;
    prompt_opened: number;
    skipped: number;
  };
  tabs: CountMap;
  density: CountMap;
  formats: {
    hints: CountMap;
    results: CountMap;
  };
  exports: {
    json: number;
    summary: number;
    full_txt: number;
    summary_copied: number;
  };
  analysis: {
    completed: number;
    success: number;
    failed: number;
    average_processing_ms: number | null;
  };
  paywall: {
    previewed: number;
    cta_clicked: number;
  };
}

const PERIODS = [
  { label: "24h", value: "24h" },
  { label: "7d", value: "7d" },
  { label: "30d", value: "30d" },
  { label: "All", value: "all" },
];

const formatNumber = (value?: number | null) =>
  typeof value === "number" ? value.toLocaleString() : "—";

const formatPercent = (numerator: number, denominator: number) => {
  if (!denominator) return "—";
  return `${Math.round((numerator / denominator) * 100)}%`;
};

const sortedEntries = (entries: CountMap): Array<[string, number]> =>
  Object.entries(entries).sort((a, b) => b[1] - a[1]);

export default function ImagesMvpAnalytics() {
  const [period, setPeriod] = useState("7d");
  const [report, setReport] = useState<AnalyticsReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async (nextPeriod: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/images_mvp/analytics/report?period=${nextPeriod}`
      );
      if (!response.ok) {
        throw new Error("Failed to load analytics report");
      }
      const data = (await response.json()) as AnalyticsReport;
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(period);
  }, [period]);

  useEffect(() => {
    document.title = "MetaExtract | Analytics";
  }, []);

  const overviewCards = useMemo(() => {
    if (!report) return [];
    return [
      {
        title: "Events",
        value: formatNumber(report.totals.events),
        icon: <BarChart3 className="h-4 w-4 text-primary" />,
      },
      {
        title: "Sessions",
        value: formatNumber(report.totals.sessions),
        icon: <Users className="h-4 w-4 text-emerald-400" />,
      },
      {
        title: "Analyses",
        value: formatNumber(report.funnel.analysis_completed),
        icon: <Upload className="h-4 w-4 text-blue-400" />,
      },
      {
        title: "Purchases",
        value: formatNumber(report.funnel.purchase_completed),
        icon: <Target className="h-4 w-4 text-amber-400" />,
      },
    ];
  }, [report]);

  const purposeEntries = useMemo(
    () => (report ? sortedEntries(report.purposes.selected) : []),
    [report]
  );

  const formatEntries = useMemo(
    () => (report ? sortedEntries(report.formats.results) : []),
    [report]
  );

  const eventEntries = useMemo(
    () => (report ? sortedEntries(report.events) : []),
    [report]
  );

  const tabEntries = useMemo(
    () => (report ? sortedEntries(report.tabs) : []),
    [report]
  );

  const densityEntries = useMemo(
    () => (report ? sortedEntries(report.density) : []),
    [report]
  );

  return (
    <Layout showHeader={true} showFooter={true}>
      <div className="min-h-screen bg-[#0B0C10] text-white pt-20">
        <div className="container mx-auto px-4 py-10 space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="inline-flex items-center gap-2 text-xs text-primary font-mono uppercase">
                <BarChart3 className="h-4 w-4" />
                Images MVP Analytics
              </div>
              <h1 className="text-3xl font-bold mt-2">Launch Signal Dashboard</h1>
              <p className="text-sm text-slate-300 mt-2">
                A lightweight pulse plus full event detail for Images MVP.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <ToggleGroup
                type="single"
                value={period}
                onValueChange={(value) => value && setPeriod(value)}
              >
                {PERIODS.map((item) => (
                  <ToggleGroupItem
                    key={item.value}
                    value={item.value}
                    className="text-xs"
                  >
                    {item.label}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
              <Button
                variant="outline"
                className="border-white/10 hover:bg-white/5"
                onClick={() => fetchReport(period)}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>

          {loading && (
            <Card className="border-white/10 bg-white/5">
              <CardContent className="py-10 text-center text-sm text-slate-300">
                Loading analytics…
              </CardContent>
            </Card>
          )}

          {error && (
            <Card className="border-red-500/20 bg-red-500/5">
              <CardContent className="py-8 text-center text-sm text-red-200">
                {error}
              </CardContent>
            </Card>
          )}

          {!loading && report && (
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="bg-[#121217] border border-white/5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="funnel">Funnel</TabsTrigger>
                <TabsTrigger value="full">Full</TabsTrigger>
                <TabsTrigger value="raw">Raw</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-6 space-y-6">
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {overviewCards.map((card) => (
                    <Card key={card.title} className="border-white/10 bg-white/5">
                      <CardContent className="flex items-center justify-between py-6">
                        <div>
                          <div className="text-xs text-slate-300 uppercase font-mono">
                            {card.title}
                          </div>
                          <div className="text-2xl font-semibold mt-2">
                            {card.value}
                          </div>
                        </div>
                        <div className="h-9 w-9 rounded-full border border-white/10 flex items-center justify-center">
                          {card.icon}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
                  <Card className="border-white/10 bg-white/5">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-300">
                        Conversion Signals
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Landing → Upload</span>
                        <Badge variant="outline">
                          {formatPercent(
                            report.funnel.upload_selected,
                            report.funnel.landing_viewed
                          )}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Upload → Analysis</span>
                        <Badge variant="outline">
                          {formatPercent(
                            report.funnel.analysis_completed,
                            report.funnel.upload_selected
                          )}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Analysis → Results</span>
                        <Badge variant="outline">
                          {formatPercent(
                            report.funnel.results_viewed,
                            report.funnel.analysis_completed
                          )}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Paywall → Purchase</span>
                        <Badge variant="outline">
                          {formatPercent(
                            report.funnel.purchase_completed,
                            report.funnel.paywall_clicked
                          )}
                        </Badge>
                      </div>
                      <Separator className="bg-white/5" />
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">
                          Avg processing time
                        </span>
                        <span className="text-white font-mono text-xs">
                          {report.analysis.average_processing_ms !== null
                            ? `${report.analysis.average_processing_ms} ms`
                            : "—"}
                        </span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-white/10 bg-white/5">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-300">
                        Purpose Mix
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm">
                      {purposeEntries.length === 0 && (
                        <div className="text-xs text-slate-500">
                          No purpose selections yet.
                        </div>
                      )}
                      {purposeEntries.map(([label, count]) => (
                        <div
                          key={label}
                          className="flex items-center justify-between"
                        >
                          <span className="text-slate-300 capitalize">
                            {label}
                          </span>
                          <span className="text-white font-mono text-xs">
                            {formatNumber(count)}
                          </span>
                        </div>
                      ))}
                      <Separator className="bg-white/5" />
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Prompt shown</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.purposes.prompt_shown)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Skipped</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.purposes.skipped)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card className="border-white/10 bg-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-300">
                      Format Mix
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    {formatEntries.length === 0 && (
                      <div className="text-xs text-slate-500">
                        No format data yet.
                      </div>
                    )}
                    {formatEntries.map(([label, count]) => (
                      <div
                        key={label}
                        className="flex items-center justify-between"
                      >
                        <span className="text-slate-300">{label}</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(count)}
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="funnel" className="mt-6 space-y-6">
                <Card className="border-white/10 bg-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-300">
                      Funnel Detail
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="grid gap-4 md:grid-cols-2 text-sm">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Landing viewed</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.landing_viewed)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Upload selected</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.upload_selected)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Upload rejected</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.upload_rejected)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Analysis started</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.analysis_started)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Analysis completed</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.analysis_completed)}
                        </span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Results viewed</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.results_viewed)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Paywall previewed</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.paywall_previewed)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Paywall clicked</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.paywall_clicked)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Purchases</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.purchase_completed)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Summary exports</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.export_summary_downloaded)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">JSON exports</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.export_json_downloaded)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Full report exports</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.export_full_txt_downloaded)}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="full" className="mt-6 space-y-6">
                <Card className="border-white/10 bg-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-300">
                      Events by Name
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Event</TableHead>
                          <TableHead className="text-right">Count</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {eventEntries.map(([name, count]) => (
                          <TableRow key={name}>
                            <TableCell className="text-slate-200">
                              {name}
                            </TableCell>
                            <TableCell className="text-right text-slate-300 font-mono text-xs">
                              {formatNumber(count)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>

                <div className="grid gap-6 md:grid-cols-2">
                  <Card className="border-white/10 bg-white/5">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-300">
                        Tabs
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      {tabEntries.map(([name, count]) => (
                        <div
                          key={name}
                          className="flex items-center justify-between"
                        >
                          <span className="text-slate-300 capitalize">
                            {name}
                          </span>
                          <span className="text-white font-mono text-xs">
                            {formatNumber(count)}
                          </span>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  <Card className="border-white/10 bg-white/5">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-300">
                        Density Mode
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      {densityEntries.map(([name, count]) => (
                        <div
                          key={name}
                          className="flex items-center justify-between"
                        >
                          <span className="text-slate-300 capitalize">
                            {name}
                          </span>
                          <span className="text-white font-mono text-xs">
                            {formatNumber(count)}
                          </span>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <Card className="border-white/10 bg-white/5">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-300">
                        Exports
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-2">
                          <Download className="h-4 w-4 text-slate-500" />
                          Summary downloads
                        </span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.exports.summary)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-2">
                          <FileJson className="h-4 w-4 text-slate-500" />
                          JSON downloads
                        </span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.exports.json)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-2">
                          <FileText className="h-4 w-4 text-slate-500" />
                          Full report downloads
                        </span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.exports.full_txt)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-2">
                          <Timer className="h-4 w-4 text-slate-500" />
                          Summary copied
                        </span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.exports.summary_copied)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-white/10 bg-white/5">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-300">
                        Paywall
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Previewed</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.paywall.previewed)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">CTA clicked</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.paywall.cta_clicked)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300">Paywall viewed</span>
                        <span className="text-white font-mono text-xs">
                          {formatNumber(report.funnel.paywall_viewed)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="raw" className="mt-6">
                <Card className="border-white/10 bg-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-300">
                      Raw JSON
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[420px] rounded-md border border-white/5 bg-black/50 p-4">
                      <pre className="text-xs text-slate-200 whitespace-pre-wrap">
                        {JSON.stringify(report, null, 2)}
                      </pre>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}

          {!loading && report && (
            <div className="text-xs text-slate-500">
              Updated {new Date(report.period.until).toLocaleString()} • period{" "}
              {report.period.range}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
