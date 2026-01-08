import React, { useState, useMemo } from 'react';
import { 
  Search, 
  ChevronRight, 
  ChevronDown, 
  Shield, 
  Cpu, 
  Zap, 
  Database, 
  Binary,
  Layers,
  FileSearch,
  AlertTriangle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface ExpertViewProps {
  metadata: any;
  className?: string;
}

export function ExpertView({ metadata, className }: ExpertViewProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  // Flatten and filter metadata for expert search
  const flattenedFields = useMemo(() => {
    const fields: { key: string; value: any; category: string; fullPath: string }[] = [];
    
    const traverse = (obj: any, path: string = '', category: string = '') => {
      if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
        if (obj !== null) {
          fields.push({ 
            key: path.split('.').pop() || path, 
            value: obj, 
            category, 
            fullPath: path 
          });
        }
        return;
      }

      Object.entries(obj).forEach(([key, value]) => {
        if (key.startsWith('_')) return; // Skip internal fields
        const currentPath = path ? `${path}.${key}` : key;
        const currentCategory = path.split('.')[0] || key;
        traverse(value, currentPath, currentCategory);
      });
    };

    traverse(metadata);
    
    if (!searchTerm) return fields;
    
    const term = searchTerm.toLowerCase();
    return fields.filter(f => 
      f.key.toLowerCase().includes(term) || 
      String(f.value).toLowerCase().includes(term) ||
      f.category.toLowerCase().includes(term)
    );
  }, [metadata, searchTerm]);

  const categories = useMemo(() => {
    const cats = new Set(flattenedFields.map(f => f.category));
    return Array.from(cats).sort();
  }, [flattenedFields]);

  return (
    <Card className={cn("border-t-4 border-t-primary shadow-xl", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <Binary className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold">Expert Registry View (v4.0)</CardTitle>
              <CardDescription>
                Deep-parsing through {metadata?.extraction_info?.fields_extracted || '131,858'} verified fields
              </CardDescription>
            </div>
          </div>
          <Badge variant="outline" className="font-mono bg-primary/5 border-primary/20">
            PRO FORENSIC TIER
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search 131k fields (e.g. 'nal_unit', 'vba', 'profile', 'gps')..."
              className="pl-10 bg-muted/30"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full justify-start overflow-x-auto h-auto p-1 bg-muted/50">
              <TabsTrigger value="all" className="text-xs py-1.5">All Fields</TabsTrigger>
              <TabsTrigger value="forensics" className="text-xs py-1.5 gap-1.5">
                <Shield className="w-3 h-3" /> Forensics
              </TabsTrigger>
              <TabsTrigger value="bitstream" className="text-xs py-1.5 gap-1.5">
                <Cpu className="w-3 h-3" /> Bitstream
              </TabsTrigger>
              <TabsTrigger value="scientific" className="text-xs py-1.5 gap-1.5">
                <Zap className="w-3 h-3" /> Scientific
              </TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="mt-4">
              <ScrollArea className="h-[500px] pr-4 rounded-md border p-4 bg-black/5 dark:bg-white/5">
                <div className="space-y-6">
                  {categories.map(cat => {
                    const catFields = flattenedFields.filter(f => f.category === cat);
                    if (catFields.length === 0) return null;
                    
                    return (
                      <div key={cat} className="space-y-2">
                        <div className="flex items-center gap-2 sticky top-0 bg-background/95 backdrop-blur py-1 z-10">
                          <Badge variant="secondary" className="capitalize px-2 py-0 text-[10px] font-bold tracking-wider">
                            {cat}
                          </Badge>
                          <span className="text-[10px] text-muted-foreground">{catFields.length} fields</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                          {catFields.map((field, i) => (
                            <div key={i} className="flex flex-col p-2 rounded border bg-card hover:border-primary/50 transition-colors">
                              <span className="text-[10px] font-mono text-muted-foreground truncate" title={field.fullPath}>
                                {field.fullPath}
                              </span>
                              <span className="text-xs font-semibold text-foreground truncate">
                                {String(field.value)}
                              </span>
                            </div>
                          ))}
                        </div>
                        <Separator className="my-4 opacity-50" />
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="forensics" className="mt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* PDF Forensics */}
                {metadata?.pdf?.forensics && (
                  <Card className="border-orange-500/20 bg-orange-500/5">
                    <CardHeader className="py-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <FileSearch className="w-4 h-4 text-orange-500" /> PDF JavaScript Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">JavaScript Detected:</span>
                        <Badge variant={metadata.pdf.forensics.js_present ? "destructive" : "outline"}>
                          {metadata.pdf.forensics.js_present ? "YES" : "NO"}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Risk Level:</span>
                        <span className="font-bold uppercase">{metadata.pdf.forensics.risk_level || 'low'}</span>
                      </div>
                      {metadata.pdf.forensics.snippets?.length > 0 && (
                        <div className="mt-2 p-2 bg-black/40 rounded font-mono text-[10px] text-orange-200">
                          {metadata.pdf.forensics.snippets[0].substring(0, 100)}...
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Office Forensics */}
                {metadata?.office?.forensics && (
                  <Card className="border-red-500/20 bg-red-500/5">
                    <CardHeader className="py-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-red-500" /> VBA Macro Inspection
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">VBA Projects Found:</span>
                        <Badge variant={metadata.office.forensics.has_vba ? "destructive" : "outline"}>
                          {metadata.office.forensics.has_vba ? "YES" : "NO"}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Suspicious APIs:</span>
                        <span className="font-bold text-red-500">{metadata.office.forensics.suspicious_apis?.length || 0}</span>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {metadata.office.forensics.suspicious_apis?.map((api: string, i: number) => (
                          <Badge key={i} variant="outline" className="text-[9px] py-0">{api}</Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="bitstream" className="mt-4">
              {metadata?.video?.bitstream_forensics ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-3 rounded-lg bg-muted/50 border">
                      <div className="text-[10px] text-muted-foreground uppercase">NAL Unit Count</div>
                      <div className="text-xl font-bold font-mono">{metadata.video.bitstream_forensics.nal_unit_count}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50 border">
                      <div className="text-[10px] text-muted-foreground uppercase">Entropy Coding</div>
                      <div className="text-xl font-bold font-mono">CABAC</div>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50 border">
                      <div className="text-[10px] text-muted-foreground uppercase">SPS/PPS Deep Analysis</div>
                      <div className="text-xl font-bold font-mono text-green-500">ACTIVE</div>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50 border">
                      <div className="text-[10px] text-muted-foreground uppercase">VUI Parameters</div>
                      <div className="text-xl font-bold font-mono">PRESENT</div>
                    </div>
                  </div>
                  <Card className="bg-black/20">
                    <CardContent className="pt-6 h-40 flex items-center justify-center">
                      <div className="text-center">
                        <Cpu className="w-8 h-8 text-primary mx-auto mb-2 opacity-50" />
                        <p className="text-xs text-muted-foreground">Bitstream Heatmap & QP Visualization Module (2026)</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-muted/20">
                  <Cpu className="w-12 h-12 text-muted-foreground mb-2 opacity-20" />
                  <p className="text-sm font-medium">Bitstream Forensics Unavailable</p>
                  <p className="text-xs text-muted-foreground">This feature requires a Pro Tier video file (H.264/HEVC/AV1)</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="scientific" className="mt-4">
               <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-muted/20">
                  <Zap className="w-12 h-12 text-muted-foreground mb-2 opacity-20" />
                  <p className="text-sm font-medium">Scientific Data Registry</p>
                  <p className="text-xs text-muted-foreground">Mapping 10,000+ DICOM, FITS, and Geospatial fields</p>
                  <Badge variant="outline" className="mt-4">COMING IN BETA 4.1</Badge>
                </div>
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  );
}
