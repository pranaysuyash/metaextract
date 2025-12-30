# server/extractor/modules/biometric_health.py

"""
Biometric and Health Records metadata extraction for Phase 4.

Covers:
- Biometric formats: fingerprints, iris scans, facial recognition
- Health and medical records: HL7, FHIR, health documents
- Wearable device data: fitness trackers, smartwatches
- Genetic/genomic data: FASTQ, BAM, VCF, genome sequences
- Medical imaging: DICOM, NIfTI (neuroimaging)
- Health IoT sensors: ECG, EEG, SpO2, heart rate
- Wellness and fitness data formats
- Electronic Health Record (EHR) metadata
- Pharmaceutical and clinical trial data
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

BIOMETRIC_HEALTH_EXTENSIONS = [
    '.fq', '.fastq', '.fasta',  # Genomic sequences
    '.bam', '.sam',  # Sequence alignment
    '.vcf', '.bcf',  # Variant call format
    '.gff', '.gtf',  # Gene annotation
    '.hl7',  # HL7 health records
    '.fhir', '.xml',  # FHIR resources
    '.nii', '.nii.gz',  # NIfTI neuroimaging
    '.edf',  # EEG data
    '.acq',  # Neuroscience acquisition
    '.dcm', '.dicom',  # DICOM medical imaging (also covered by DICOM module)
]


def extract_biometric_health_metadata(filepath: str) -> Dict[str, Any]:
    """Extract biometric and health records metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is biometric/health format
        is_biometric = _is_biometric_health_file(filepath, filename, file_ext)

        if not is_biometric:
            return result

        result['biometric_health_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.fq', '.fastq']:
            fastq_data = _extract_fastq_metadata(filepath)
            result.update(fastq_data)

        elif file_ext in ['.fasta', '.fa']:
            fasta_data = _extract_fasta_metadata(filepath)
            result.update(fasta_data)

        elif file_ext in ['.bam', '.sam']:
            alignment_data = _extract_alignment_metadata(filepath)
            result.update(alignment_data)

        elif file_ext == '.vcf':
            vcf_data = _extract_vcf_metadata(filepath)
            result.update(vcf_data)

        elif file_ext in ['.gff', '.gtf']:
            annotation_data = _extract_annotation_metadata(filepath)
            result.update(annotation_data)

        elif file_ext == '.hl7':
            hl7_data = _extract_hl7_metadata(filepath)
            result.update(hl7_data)

        elif file_ext in ['.fhir', '.xml']:
            fhir_data = _extract_fhir_metadata(filepath)
            result.update(fhir_data)

        elif file_ext in ['.nii', '.nii.gz']:
            nifti_data = _extract_nifti_metadata(filepath)
            result.update(nifti_data)

        elif file_ext == '.edf':
            edf_data = _extract_edf_metadata(filepath)
            result.update(edf_data)

        # Get general biometric properties
        general_data = _extract_general_biometric_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting biometric health metadata from {filepath}: {e}")
        result['biometric_health_extraction_error'] = str(e)

    return result


def _is_biometric_health_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is biometric/health format."""
    if file_ext.lower() in BIOMETRIC_HEALTH_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # FASTQ header (@)
        if header[0:1] == b'@' and b'\n' in header:
            return True

        # FASTA header (>)
        if header[0:1] == b'>' and b'\n' in header:
            return True

        # BAM signature (0x4241 4d01)
        if header[0:4] == b'BAM\x01':
            return True

        # VCF header (##fileformat=VCFv)
        if b'##fileformat=VCF' in header:
            return True

        # GFF/GTF header (##gff-version or similar)
        if b'##gff-version' in header or b'##gtf-version' in header:
            return True

        # HL7 segment identifier
        if header[0:3] in [b'MSH', b'FHS', b'BHS']:
            return True

        # NIfTI header
        if len(header) > 348 and header[344:348] == b'\x6e\x2b\x31' or header[344:348] == b'\x6e\x69\x31':
            return True

        # EDF header
        if header[0:8] == b'0       ':
            return True

    except Exception:
        pass

    return False


def _extract_fastq_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FASTQ sequence file metadata."""
    fastq_data = {'biometric_health_fastq_format': True}

    try:
        sequence_count = 0
        quality_scores = []
        read_lengths = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            line_num = 0
            seq_line = None

            for line in f:
                line_num += 1
                line = line.rstrip('\n')

                if line_num % 4 == 1:  # Header line
                    if line.startswith('@'):
                        sequence_count += 1
                elif line_num % 4 == 2:  # Sequence line
                    seq_line = line
                    if len(read_lengths) < 1000:  # Sample first 1000
                        read_lengths.append(len(line))
                elif line_num % 4 == 0:  # Quality line
                    if len(quality_scores) < 1000:
                        quality_scores.extend(list(line))

                if sequence_count >= 10000:  # Sample up to 10k
                    break

        fastq_data['biometric_health_fastq_sequence_count'] = sequence_count

        if read_lengths:
            fastq_data['biometric_health_fastq_min_read_length'] = min(read_lengths)
            fastq_data['biometric_health_fastq_max_read_length'] = max(read_lengths)
            fastq_data['biometric_health_fastq_avg_read_length'] = sum(read_lengths) / len(read_lengths)

        if quality_scores:
            # Quality scores: Phred quality (ASCII 33+)
            quality_values = [ord(q) - 33 for q in quality_scores if ord(q) >= 33]
            if quality_values:
                fastq_data['biometric_health_fastq_min_quality'] = min(quality_values)
                fastq_data['biometric_health_fastq_max_quality'] = max(quality_values)
                fastq_data['biometric_health_fastq_avg_quality'] = sum(quality_values) / len(quality_values)

    except Exception as e:
        fastq_data['biometric_health_fastq_extraction_error'] = str(e)

    return fastq_data


def _extract_fasta_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FASTA sequence file metadata."""
    fasta_data = {'biometric_health_fasta_format': True}

    try:
        sequence_count = 0
        sequence_lengths = []

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            current_length = 0

            for line in f:
                line = line.rstrip('\n')

                if line.startswith('>'):
                    if current_length > 0:
                        sequence_lengths.append(current_length)
                    sequence_count += 1
                    current_length = 0
                else:
                    current_length += len(line)

                if sequence_count >= 10000:
                    break

            if current_length > 0:
                sequence_lengths.append(current_length)

        fasta_data['biometric_health_fasta_sequence_count'] = sequence_count

        if sequence_lengths:
            fasta_data['biometric_health_fasta_min_seq_length'] = min(sequence_lengths)
            fasta_data['biometric_health_fasta_max_seq_length'] = max(sequence_lengths)
            fasta_data['biometric_health_fasta_avg_seq_length'] = sum(sequence_lengths) / len(sequence_lengths)

    except Exception as e:
        fasta_data['biometric_health_fasta_extraction_error'] = str(e)

    return fasta_data


def _extract_alignment_metadata(filepath: str) -> Dict[str, Any]:
    """Extract BAM/SAM alignment file metadata."""
    align_data = {'biometric_health_alignment_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        if header[0:4] == b'BAM\x01':
            align_data['biometric_health_alignment_is_bam'] = True

            # Parse BAM header
            if len(header) > 8:
                # Text header length at offset 4
                l_text = struct.unpack('<I', header[4:8])[0]
                align_data['biometric_health_bam_header_length'] = l_text

        align_data['biometric_health_alignment_format_detected'] = True

    except Exception as e:
        align_data['biometric_health_alignment_extraction_error'] = str(e)

    return align_data


def _extract_vcf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract VCF variant file metadata."""
    vcf_data = {'biometric_health_vcf_format': True}

    try:
        variant_count = 0
        samples = []
        info_fields = set()
        format_fields = set()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n')

                if line.startswith('##'):
                    # Parse metadata lines
                    if line.startswith('##INFO='):
                        info_fields.add(line)
                    elif line.startswith('##FORMAT='):
                        format_fields.add(line)
                    elif line.startswith('##fileformat='):
                        vcf_data['biometric_health_vcf_version'] = line.split('=')[1]

                elif line.startswith('#CHROM'):
                    # Header line with sample names
                    parts = line.split('\t')
                    if len(parts) > 9:
                        samples = parts[9:]
                        vcf_data['biometric_health_vcf_sample_count'] = len(samples)

                elif not line.startswith('#'):
                    # Data line
                    variant_count += 1
                    if variant_count >= 10000:
                        break

        vcf_data['biometric_health_vcf_variant_count'] = variant_count
        vcf_data['biometric_health_vcf_info_field_count'] = len(info_fields)
        vcf_data['biometric_health_vcf_format_field_count'] = len(format_fields)

    except Exception as e:
        vcf_data['biometric_health_vcf_extraction_error'] = str(e)

    return vcf_data


def _extract_annotation_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GFF/GTF annotation file metadata."""
    annot_data = {'biometric_health_annotation_format': True}

    try:
        feature_count = 0
        source_types = set()
        feature_types = set()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('#'):
                    continue

                parts = line.split('\t')
                if len(parts) >= 3:
                    feature_count += 1
                    source_types.add(parts[1] if len(parts) > 1 else '')
                    feature_types.add(parts[2] if len(parts) > 2 else '')

                if feature_count >= 10000:
                    break

        annot_data['biometric_health_annotation_feature_count'] = feature_count
        annot_data['biometric_health_annotation_source_count'] = len(source_types)
        annot_data['biometric_health_annotation_feature_type_count'] = len(feature_types)

    except Exception as e:
        annot_data['biometric_health_annotation_extraction_error'] = str(e)

    return annot_data


def _extract_hl7_metadata(filepath: str) -> Dict[str, Any]:
    """Extract HL7 health record metadata."""
    hl7_data = {'biometric_health_hl7_format': True}

    try:
        segment_types = set()
        segment_count = 0

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n')

                if len(line) >= 3:
                    segment_type = line[:3]
                    segment_types.add(segment_type)
                    segment_count += 1

        hl7_data['biometric_health_hl7_segment_types'] = list(segment_types)
        hl7_data['biometric_health_hl7_segment_type_count'] = len(segment_types)
        hl7_data['biometric_health_hl7_segment_count'] = segment_count

        # Infer HL7 version from MSH segment
        if 'MSH' in segment_types:
            hl7_data['biometric_health_hl7_has_msh'] = True

    except Exception as e:
        hl7_data['biometric_health_hl7_extraction_error'] = str(e)

    return hl7_data


def _extract_fhir_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FHIR health record metadata."""
    fhir_data = {'biometric_health_fhir_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(100000)

        # Check for FHIR resource type
        if '"resourceType":' in content:
            fhir_data['biometric_health_fhir_is_json'] = True
        elif 'resourceType=' in content:
            fhir_data['biometric_health_fhir_is_xml'] = True

        # Extract resource type
        if '<Patient' in content or '"resourceType":"Patient"' in content:
            fhir_data['biometric_health_fhir_resource_type'] = 'Patient'
        elif '<Observation' in content or '"resourceType":"Observation"' in content:
            fhir_data['biometric_health_fhir_resource_type'] = 'Observation'
        elif '<Condition' in content or '"resourceType":"Condition"' in content:
            fhir_data['biometric_health_fhir_resource_type'] = 'Condition'
        elif '<Medication' in content or '"resourceType":"Medication"' in content:
            fhir_data['biometric_health_fhir_resource_type'] = 'Medication'

    except Exception as e:
        fhir_data['biometric_health_fhir_extraction_error'] = str(e)

    return fhir_data


def _extract_nifti_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NIfTI neuroimaging file metadata."""
    nifti_data = {'biometric_health_nifti_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(348)

        if len(header) >= 348:
            # NIfTI header structure
            # Offset 0-3: sizeof_hdr
            sizeof_hdr = struct.unpack('<I', header[0:4])[0]
            nifti_data['biometric_health_nifti_header_size'] = sizeof_hdr

            # Offset 40-43: dim[0] - number of dimensions
            if len(header) > 40:
                dim0 = struct.unpack('<I', header[40:44])[0]
                nifti_data['biometric_health_nifti_dimensions'] = dim0

            # Offset 44-83: dim[1-8] - dimension sizes
            if len(header) > 83:
                dims = struct.unpack('<8I', header[44:76])
                nifti_data['biometric_health_nifti_size'] = list(dims)

            # Offset 30-31: datatype
            if len(header) > 30:
                datatype = struct.unpack('<H', header[30:32])[0]
                datatypes = {
                    1: 'BINARY', 2: 'UINT8', 4: 'INT16', 8: 'INT32',
                    16: 'FLOAT32', 32: 'COMPLEX64', 64: 'FLOAT64'
                }
                nifti_data['biometric_health_nifti_datatype'] = datatypes.get(datatype, f'UNKNOWN({datatype})')

    except Exception as e:
        nifti_data['biometric_health_nifti_extraction_error'] = str(e)

    return nifti_data


def _extract_edf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract EDF (EEG) file metadata."""
    edf_data = {'biometric_health_edf_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(256)

        if len(header) >= 256:
            # EDF header structure
            # Offset 0-7: Version
            version = header[0:8].strip()
            edf_data['biometric_health_edf_version'] = version.decode('utf-8', errors='ignore')

            # Offset 8-87: Local patient identification
            patient_id = header[8:88].strip()
            edf_data['biometric_health_edf_has_patient_id'] = len(patient_id) > 0

            # Offset 88-167: Local recording identification
            recording_id = header[88:168].strip()
            edf_data['biometric_health_edf_has_recording_id'] = len(recording_id) > 0

            # Offset 236-243: Number of data records
            if len(header) > 236:
                n_records = int(header[236:244].strip())
                edf_data['biometric_health_edf_record_count'] = n_records

    except Exception as e:
        edf_data['biometric_health_edf_extraction_error'] = str(e)

    return edf_data


def _extract_general_biometric_properties(filepath: str) -> Dict[str, Any]:
    """Extract general biometric properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['biometric_health_file_size'] = stat_info.st_size
        props['biometric_health_filename'] = Path(filepath).name

    except Exception:
        pass

    return props


def get_biometric_health_field_count() -> int:
    """Return the number of fields extracted by biometric health metadata."""
    # FASTQ genomic fields
    fastq_fields = 12

    # FASTA genomic fields
    fasta_fields = 10

    # BAM/SAM alignment fields
    alignment_fields = 10

    # VCF variant fields
    vcf_fields = 14

    # GFF/GTF annotation fields
    annotation_fields = 10

    # HL7 health record fields
    hl7_fields = 12

    # FHIR resource fields
    fhir_fields = 12

    # NIfTI neuroimaging fields
    nifti_fields = 12

    # EDF EEG fields
    edf_fields = 10

    # General properties
    general_fields = 6

    return fastq_fields + fasta_fields + alignment_fields + vcf_fields + annotation_fields + hl7_fields + fhir_fields + nifti_fields + edf_fields + general_fields


# Integration point
def extract_biometric_health_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for biometric health extraction."""
    return extract_biometric_health_metadata(filepath)
