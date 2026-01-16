import React from 'react';
import { MapPin, Camera, Calendar, Lock, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { MvpMetadata, TabValue, GpsCoordinates } from '@/lib/types';
import { formatDate, hasValue, collectDetailEntries } from '@/utils/imageMetadataTransformers';

interface PrivacyTabProps {
  metadata: MvpMetadata;
  gpsCoords: GpsCoordinates | null;
  overlayGps: GpsCoordinates | null;
  hasGps: boolean;
  embeddedGpsState: 'embedded' | 'overlay' | 'none';
  gpsMapUrl: string;
  captureDateLabel: string;
  captureDateValue: string | null;
  localModifiedValue: string | null;
  burnedTimestamp: string | null;
  software: string | null;
  hashSha256: string | null;
  hashMd5: string | null;
  showOverlayText: boolean;
  onToggleOverlayText: () => void;
  canExport: boolean;
  isAdvanced: boolean;
  onScrollTo: (tab: TabValue, anchorId: string) => void;
}

export const PrivacyTab: React.FC<PrivacyTabProps> = ({
  metadata,
  gpsCoords,
  overlayGps,
  hasGps,
  embeddedGpsState,
  gpsMapUrl,
  captureDateLabel,
  captureDateValue,
  localModifiedValue,
  burnedTimestamp,
  software,
  hashSha256,
  hashMd5,
  showOverlayText,
  onToggleOverlayText,
  canExport,
  isAdvanced,
  onScrollTo,
}) => {
  const formatToneClass =
    embeddedGpsState === 'embedded'
      ? 'border-red-500/20 bg-red-500/5 text-red-200'
      : embeddedGpsState === 'overlay'
      ? 'border-amber-500/20 bg-amber-500/5 text-amber-200'
      : 'border-emerald-500/20 bg-emerald-500/5 text-emerald-200';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Location Card */}
      <Card
        className="bg-[#121217] border-white/5"
        id="section-location"
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
            <MapPin className="w-4 h-4" /> LOCATION DATA
          </CardTitle>
        </CardHeader>
        <CardContent>
          {hasGps && gpsCoords ? (
            <div className="space-y-4">
              <div className={`p-4 border rounded-lg text-sm flex items-center gap-2 ${formatToneClass}`}>
                <ShieldAlert className="w-5 h-5" />
                <span>Location data present in this file.</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm font-mono text-white">
                <div>
                  <span className="text-slate-500 block text-xs">
                    LATITUDE
                  </span>
                  {gpsCoords.latitude}
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">
                    LONGITUDE
                  </span>
                  {gpsCoords.longitude}
                </div>
              </div>
              {gpsMapUrl && (
                <a
                  href={gpsMapUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full py-2 bg-white/5 hover:bg-white/10 text-center rounded text-sm transition-colors text-primary"
                >
                  View on Google Maps{' '}
                  <ArrowRight className="w-3 h-3 inline ml-1" />
                </a>
              )}
            </div>
          ) : overlayGps ? (
            <div className="space-y-4">
              <div className={`p-4 border rounded-lg text-sm flex items-center gap-2 ${formatToneClass}`}>
                <ShieldAlert className="w-5 h-5" />
                <span>
                  Overlay GPS detected from burned-in text (pixels).
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm font-mono text-white">
                <div>
                  <span className="text-slate-500 block text-xs">
                    LATITUDE (Overlay)
                  </span>
                  {overlayGps.latitude}
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">
                    LONGITUDE (Overlay)
                  </span>
                  {overlayGps.longitude}
                </div>
              </div>
              {gpsMapUrl && (
                <a
                  href={gpsMapUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full py-2 bg-white/5 hover:bg-white/10 text-center rounded text-sm transition-colors text-primary"
                >
                  View on Google Maps{' '}
                  <ArrowRight className="w-3 h-3 inline ml-1" />
                </a>
              )}
              {(burnedTimestamp || metadata.burned_metadata?.parsed_data?.plus_code) && (
                <div className="text-xs text-slate-400 space-y-1">
                  {burnedTimestamp && (
                    <div>
                      <span className="text-slate-500">
                        Overlay time:
                      </span>{' '}
                      {burnedTimestamp}
                    </div>
                  )}
                  {metadata.burned_metadata?.parsed_data?.plus_code && (
                    <div>
                      <span className="text-slate-500">
                        Plus code:
                      </span>{' '}
                      {metadata.burned_metadata.parsed_data.plus_code}
                    </div>
                  )}
                </div>
              )}
              <div className="pt-2">
                <Button
                  variant="outline"
                  className="border-white/10 hover:bg-white/5 w-full"
                  onClick={onToggleOverlayText}
                >
                  {showOverlayText
                    ? 'Hide overlay text'
                    : 'View overlay text'}
                </Button>
                {showOverlayText && (
                  <div className="mt-3 text-xs text-slate-200 bg-black/30 border border-white/5 rounded p-3 max-h-40 overflow-auto">
                    {metadata.burned_metadata?.extracted_text?.slice(0, 1200) || 'Text not available'}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="py-8 text-center">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3 opacity-20" />
              <p className="text-emerald-500 font-bold">
                Location not present
              </p>
              <p className="text-slate-500 text-xs mt-1">
                No GPS coordinates were found in this file.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Device Info */}
      <Card
        className="bg-[#121217] border-white/5"
        id="section-device"
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
            <Camera className="w-4 h-4" /> DEVICE INFORMATION
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            {!hasValue(metadata.exif?.Make) &&
            !hasValue(metadata.exif?.Model) ? (
              <div className="text-xs text-slate-500">
                No camera make/model tags present in this file.
              </div>
            ) : (
              <>
                {hasValue(metadata.exif?.Make) && (
                  <div className="pb-3 border-b border-white/5">
                    <span className="text-slate-500 block text-xs font-mono mb-1">
                      CAMERA MAKE
                    </span>
                    <span className="text-white font-medium">
                      {String(metadata.exif?.Make)}
                    </span>
                  </div>
                )}
                {hasValue(metadata.exif?.Model) && (
                  <div className="pb-3 border-b border-white/5">
                    <span className="text-slate-500 block text-xs font-mono mb-1">
                      CAMERA MODEL
                    </span>
                    <span className="text-white font-medium">
                      {String(metadata.exif?.Model)}
                    </span>
                  </div>
                )}
              </>
            )}
            {hasValue(software) && (
              <div>
                <span className="text-slate-500 block text-xs font-mono mb-1">
                  SOFTWARE
                </span>
                <span className="text-white font-medium">
                  {software}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Timestamps */}
      <Card
        className="bg-[#121217] border-white/5"
        id="section-timestamps"
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
            <Calendar className="w-4 h-4" /> TIMESTAMPS
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <div className="pb-3 border-b border-white/5">
              <span className="text-slate-500 block text-xs font-mono mb-1">
                {captureDateLabel}
              </span>
              <span className="text-white font-medium">
                {captureDateValue
                  ? formatDate(captureDateValue)
                  : 'Not present in this file'}
              </span>
            </div>
            {hasValue(burnedTimestamp) && (
              <div className="pb-3 border-b border-white/5">
                <span className="text-slate-500 block text-xs font-mono mb-1">
                  OVERLAY TIMESTAMP
                </span>
                <span className="text-white font-medium">
                  {burnedTimestamp}
                </span>
              </div>
            )}
            <div>
              <span className="text-slate-500 block text-xs font-mono mb-1">
                LOCAL FILE MODIFIED
              </span>
              <span className="text-white font-medium">
                {formatDate(
                  localModifiedValue || undefined,
                  'Not available (browser did not provide)'
                )}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hidden Data Summary */}
      <Card className="bg-[#121217] border-white/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
            <Lock className="w-4 h-4" /> HIDDEN DATA
          </CardTitle>
        </CardHeader>
        <CardContent>
          {(() => {
            const hasMakerNotes =
              (metadata.makernote?.enriched?.deviceSpecific &&
                Object.keys(metadata.makernote.enriched.deviceSpecific).length > 0) ||
              (metadata.registry_summary?.makerNotes as any)?.present;

            const makerNotesInfo = metadata.makernote?.enriched;
            const serial =
              (metadata.exif?.BodySerialNumber as string | undefined) ||
              (metadata.exif?.LensSerialNumber as string | undefined) ||
              (metadata.exif?.SerialNumber as string | undefined) ||
              null;
              const colorSpaceNumeric = Number(metadata.exif?.ColorSpace);
    const colorSpaceValue =
      Number.isFinite(colorSpaceNumeric) && colorSpaceNumeric === 1
        ? 'sRGB'
        : hasValue(metadata.exif?.ColorSpace)
        ? String(metadata.exif?.ColorSpace)
        : null;
    const colorProfile = colorSpaceValue;

            if (!hasMakerNotes && !hasValue(serial) && !hasValue(colorProfile)) {
              return (
                <div className="text-xs text-slate-500">
                  No hidden identifiers present in this file.
                </div>
              );
            }

            return (
              <ul className="space-y-3">
                {hasMakerNotes && makerNotesInfo && (
                  <li className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">
                        MakerNotes
                      </span>
                      <span className="text-emerald-400 capitalize">
                        {makerNotesInfo.manufacturer}
                      </span>
                    </div>
                    {makerNotesInfo.deviceSpecific &&
                      Object.keys(makerNotesInfo.deviceSpecific).length > 0 && (
                        <div className="pl-4 space-y-1">
                          {Object.entries(makerNotesInfo.deviceSpecific)
                            .slice(0, 5)
                            .map(([key, value]) => (
                              <div
                                key={key}
                                className="flex justify-between text-xs"
                              >
                                <span className="text-slate-500">
                                  {key
                                    .replace(/([A-Z])/g, ' $1')
                                    .trim()}
                                </span>
                                <span className="text-slate-300 truncate max-w-[60%]">
                                  {String(value).slice(0, 30)}
                                </span>
                              </div>
                            ))}
                        </div>
                      )}
                  </li>
                )}
                {hasValue(serial) && (
                  <li className="flex justify-between text-sm">
                    <span className="text-slate-400">
                      Serial Numbers
                    </span>
                    <span className="text-slate-200 truncate max-w-[55%]">
                      {serial}
                    </span>
                  </li>
                )}
                {hasValue(colorProfile) && (
                  <li className="flex justify-between text-sm">
                    <span className="text-slate-400">
                      Color Profile
                    </span>
                    <span className="text-slate-200">
                      {colorProfile}
                    </span>
                  </li>
                )}
              </ul>
            );
          })()}
        </CardContent>
      </Card>

      {/* Integrity */}
      {(hasValue(hashSha256) || hasValue(hashMd5)) && (
        <Card
          className="bg-[#121217] border-white/5"
          id="section-integrity"
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
              <div className="w-4 h-4 flex items-center justify-center text-xs">#</div>
              INTEGRITY
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm font-mono">
            {hasValue(hashSha256) && (
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">SHA256</span>
                <span className="text-slate-200 truncate max-w-[60%]">
                  {String(hashSha256)}
                </span>
              </div>
            )}
            {hasValue(hashMd5) && (
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">MD5</span>
                <span className="text-slate-200 truncate max-w-[60%]">
                  {String(hashMd5)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {isAdvanced && (
        <Card className="bg-[#121217] border-white/5 md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-mono text-slate-400">
              ADVANCED DETAILS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Accordion
              type="single"
              collapsible
              className="border-white/10"
            >
              <AccordionItem
                value="privacy-advanced"
                className="border-white/10"
              >
                <AccordionTrigger className="text-slate-200 hover:no-underline">
                  Privacy details (filtered)
                </AccordionTrigger>
                <AccordionContent>
                  {(() => {
                    const maxEntries = canExport ? 200 : 20;
                    const details = collectDetailEntries(
                      {
                        location: {
                          embedded_gps: gpsCoords,
                          overlay_gps: overlayGps,
                          overlay_plus_code:
                            metadata.burned_metadata?.parsed_data?.plus_code,
                          overlay_address:
                            metadata.burned_metadata?.parsed_data?.address,
                        },
                        timestamps: {
                          capture_date: captureDateValue || null,
                          overlay_timestamp: burnedTimestamp,
                          local_file_modified: localModifiedValue,
                        },
                        device: {
                          make: metadata.exif?.Make,
                          model: metadata.exif?.Model,
                          software,
                        },
                        identifiers: {
                          maker_notes_detected:
                            hasValue(metadata.exif?.MakerNote) ||
                            Object.keys(metadata.exif || {}).some(k =>
                              k.toLowerCase().includes('maker')
                            ),
                          serial_numbers:
                            metadata.exif?.BodySerialNumber ||
                            metadata.exif?.LensSerialNumber ||
                            metadata.exif?.SerialNumber,
                        },
                        registry_summary:
                          metadata.registry_summary ?? null,
                      },
                      '',
                      0,
                      4,
                      [],
                      maxEntries
                    );

                    if (details.length === 0) {
                      return (
                        <div className="text-xs text-slate-500">
                          No additional fields in this view.
                        </div>
                      );
                    }

                    return (
                      <>
                        {!canExport && (
                          <div className="text-xs text-slate-500 mb-3">
                            Showing the first {maxEntries} entries.
                            Unlock the full report to search and view
                            everything.
                          </div>
                        )}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {details.map(d => (
                            <button
                              key={d.path}
                              type="button"
                              className="text-left bg-white/5 border border-white/5 rounded px-3 py-2 hover:bg-white/10 transition-colors"
                              onClick={() =>
                                navigator.clipboard?.writeText(
                                  JSON.stringify(
                                    { [d.path]: d.value },
                                    null,
                                    2
                                  )
                                )
                              }
                            >
                              <div className="text-xs font-mono text-slate-300 truncate">
                                {d.path}
                              </div>
                              <div className="text-xs text-slate-500 truncate">
                                {d.valuePreview}
                              </div>
                            </button>
                          ))}
                        </div>
                      </>
                    );
                  })()}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      )}
    </div>
  );
};