import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
    User,
    Monitor,
    Settings,
    Calendar,
    Layers,
    HeartPulse,
} from 'lucide-react';

interface MedicalAvailable {
    available: boolean;
    patient_info?: any;
    study_info?: any;
    series_info?: any;
    equipment_info?: any;
    image_info?: any;
    acquisition_params?: any;
    private_tags?: any;
}

interface MedicalAnalysisResultProps {
    data: MedicalAvailable;
    isUnlocked: boolean;
}

export function MedicalAnalysisResult({
    data,
    isUnlocked,
}: MedicalAnalysisResultProps) {
    if (!data || !data.available) return null;

    const DetailRow = ({ label, value, unit = '' }: { label: string; value: any; unit?: string }) => {
        if (value === undefined || value === null || value === '') return null;
        return (
            <div className="flex justify-between py-1 border-b border-gray-100 last:border-0">
                <span className="text-sm text-gray-500">{label}</span>
                <span className="text-sm font-medium text-gray-900 text-right">
                    {String(value)}
                    {unit ? ` ${unit}` : ''}
                </span>
            </div>
        );
    };

    const Section = ({
        title,
        icon: Icon,
        children,
        color,
    }: {
        title: string;
        icon: any;
        children: React.ReactNode;
        color: string;
    }) => (
        <Card className={`border-${color}-200 bg-${color}-50/30 overflow-hidden`}>
            <CardHeader className={`bg-${color}-50/50 pb-3 border-b border-${color}-100`}>
                <CardTitle className={`text-base flex items-center gap-2 text-${color}-900`}>
                    <Icon className={`h-5 w-5 text-${color}-600`} />
                    {title}
                </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-1 bg-white/50">{children}</CardContent>
        </Card>
    );

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-blue-100 rounded-lg">
                    <HeartPulse className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Medical Imaging Analysis</h2>
                    <p className="text-gray-500">DICOM Metadata Extraction</p>
                </div>
                {data.series_info?.modality && (
                    <Badge className="ml-auto text-lg px-3 py-1 bg-blue-600">
                        {data.series_info.modality}
                    </Badge>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Patient Information - SENSITIVE */}
                {data.patient_info && (
                    <Section title="Patient Information" icon={User} color="rose">
                        <DetailRow label="ID" value={data.patient_info.id} />
                        <DetailRow label="Sex" value={data.patient_info.sex} />
                        <DetailRow label="Age" value={data.patient_info.age} />
                        <DetailRow label="Weight" value={data.patient_info.weight} unit="kg" />
                        <DetailRow label="Height" value={data.patient_info.height} unit="m" />
                        <DetailRow label="Birth Date" value={data.patient_info.birth_date} />
                        {isUnlocked ? (
                            <DetailRow label="Name" value={data.patient_info.name} />
                        ) : (
                            <div className="flex justify-between py-1 border-b border-gray-100 last:border-0 opacity-50">
                                <span className="text-sm text-gray-500">Name</span>
                                <span className="text-sm font-medium text-gray-900 text-right blur-sm select-none">John Doe</span>
                            </div>
                        )}
                    </Section>
                )}

                {/* Study Information */}
                {data.study_info && (
                    <Section title="Study Details" icon={Calendar} color="blue">
                        <DetailRow label="Description" value={data.study_info.description} />
                        <DetailRow label="Date" value={data.study_info.date} />
                        <DetailRow label="Time" value={data.study_info.time} />
                        <DetailRow label="Study ID" value={data.study_info.id} />
                        <DetailRow label="Accession Number" value={data.study_info.accession_number} />
                        <DetailRow
                            label="Referring Physician"
                            value={data.study_info.referring_physician}
                        />
                    </Section>
                )}

                {/* Series & Image Info */}
                <Section title="Image Parameters" icon={Layers} color="indigo">
                    {data.series_info && (
                        <>
                            <DetailRow label="Series # " value={data.series_info.number} />
                            <DetailRow label="Description" value={data.series_info.description} />
                            <DetailRow label="Body Part" value={data.series_info.body_part} />
                            <DetailRow label="Position" value={data.series_info.patient_position} />
                        </>
                    )}
                    {data.image_info && (
                        <>
                            <div className="my-2 border-t border-gray-100"></div>
                            <DetailRow
                                label="Dimensions"
                                value={`${data.image_info.width} x ${data.image_info.height}`}
                                unit="px"
                            />
                            <DetailRow
                                label="Resolution"
                                value={data.image_info.pixel_spacing}
                                unit="mm"
                            />
                            <DetailRow
                                label="Slice Thickness"
                                value={data.image_info.slice_thickness}
                                unit="mm"
                            />
                            <DetailRow label="Photometric" value={data.image_info.photometric_interpretation} />
                        </>
                    )}
                </Section>

                {/* Equipment Details */}
                {data.equipment_info && (
                    <Section title="Equipment" icon={Monitor} color="slate">
                        <DetailRow label="Manufacturer" value={data.equipment_info.manufacturer} />
                        <DetailRow label="Model" value={data.equipment_info.model} />
                        <DetailRow
                            label="Software Version"
                            value={data.equipment_info.software_version}
                        />
                        <DetailRow label="Station" value={data.equipment_info.station_name} />
                        <DetailRow label="Institution" value={data.equipment_info.institution} />
                    </Section>
                )}

                {/* Acquisition Params */}
                {data.acquisition_params && (
                    <Section title="Acquisition Settings" icon={Settings} color="amber">
                        <DetailRow label="KVP" value={data.acquisition_params.kvp} unit="kV" />
                        <DetailRow label="Tube Current" value={data.acquisition_params.tube_current} unit="mA" />
                        <DetailRow label="Exposure Time" value={data.acquisition_params.exposure_time} unit="ms" />
                        <DetailRow label="Filter" value={data.acquisition_params.filter_type} />
                        <DetailRow label="Kernel" value={data.acquisition_params.kernel} />
                        <DetailRow label="Gantry Tilt" value={data.acquisition_params.gantry_tilt} />
                    </Section>
                )}
            </div>
        </div>
    );
}
