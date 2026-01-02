import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Shield,
    Eye,
    Briefcase,
    Palette,
    Stethoscope,
    RefreshCw,
    Lightbulb
} from 'lucide-react';
import { METADATA_EXAMPLES, getRandomExample } from '@/utils/educationalExamples';

export function EducationalExamples() {
    const [example, setExample] = useState(METADATA_EXAMPLES[0]);
    const [isAnimating, setIsAnimating] = useState(false);

    const nextExample = () => {
        setIsAnimating(true);
        setTimeout(() => {
            let next = getRandomExample();
            // Ensure we get a different example
            while (next.title === example.title) {
                next = getRandomExample();
            }
            setExample(next);
            setIsAnimating(false);
        }, 300);
    };

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'forensic': return <Shield className="w-4 h-4" />;
            case 'privacy': return <Eye className="w-4 h-4" />;
            case 'professional': return <Briefcase className="w-4 h-4" />;
            case 'creative': return <Palette className="w-4 h-4" />;
            case 'medical': return <Stethoscope className="w-4 h-4" />;
            default: return <Lightbulb className="w-4 h-4" />;
        }
    };

    const getCategoryColor = (category: string) => {
        switch (category) {
            case 'forensic': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
            case 'privacy': return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
            case 'professional': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
            case 'creative': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300';
            case 'medical': return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300';
            default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-4 animate-in fade-in zoom-in duration-500">
            <div className="text-center mb-8 space-y-2">
                <div className="inline-flex items-center justify-center p-3 bg-secondary/30 rounded-full mb-2">
                    <Lightbulb className="w-8 h-8 text-yellow-500" />
                </div>
                <h2 className="text-2xl font-bold tracking-tight">Discover the Power of Metadata</h2>
                <p className="text-muted-foreground">
                    Select a file to begin, or learn how metadata solves real-world mysteries below.
                </p>
            </div>

            <Card className={`transition-opacity duration-300 ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
                <CardHeader>
                    <div className="flex items-center justify-between mb-2">
                        <Badge
                            variant="secondary"
                            className={`flex items-center gap-1.5 px-3 py-1 ${getCategoryColor(example.category)}`}
                        >
                            {getCategoryIcon(example.category)}
                            <span className="capitalize">{example.category} Use Case</span>
                        </Badge>
                    </div>
                    <CardTitle className="text-xl">{example.title}</CardTitle>
                    <CardDescription className="text-base mt-2">
                        {example.description}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-3">
                        <h4 className="text-sm font-semibold flex items-center gap-2 text-primary">
                            <Eye className="w-4 h-4" />
                            What Metadata Revealed
                        </h4>
                        <ul className="space-y-2">
                            {example.revealed.map((item, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-muted-foreground">
                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary/50 flex-shrink-0" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="p-4 bg-muted/50 rounded-lg border">
                        <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                            <Shield className="w-4 h-4 text-green-600 dark:text-green-400" />
                            Real World Impact
                        </h4>
                        <p className="text-sm italic text-muted-foreground">
                            "{example.impact}"
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        {example.fields.map((field) => (
                            <Badge key={field} variant="outline" className="text-xs font-mono">
                                {field}
                            </Badge>
                        ))}
                    </div>
                </CardContent>
                <CardFooter className="flex justify-between border-t bg-muted/10 p-4">
                    <span className="text-xs text-muted-foreground">
                        Example from public records & news
                    </span>
                    <Button variant="ghost" size="sm" onClick={nextExample} className="gap-2">
                        <RefreshCw className="w-3 h-3" />
                        View Another Example
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
