#!/usr/bin/env python3
"""
Genomic/Biological Data Extractor for MetaExtract.
Extracts metadata from FASTA, FASTQ, VCF, BAM, and other bioinformatics formats.
"""

import os
import sys
import json
import gzip
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

BIOPYTHON_AVAILABLE = True
try:
    from Bio import SeqIO
    from Bio.Seq import Seq
    from Bio.Alphabet import generic_alphabet
except ImportError:
    BIOPYTHON_AVAILABLE = False
    logger.warning("Biopython not available - genomic extraction limited")


class GenomicFormat(Enum):
    FASTA = "fasta"
    FASTQ = "fastq"
    VCF = "vcf"
    BAM = "bam"
    SAM = "sam"
    GFF = "gff"
    GTF = "gtf"
    BED = "bed"
    BCF = "bcf"
    UNKNOWN = "unknown"


@dataclass
class FastaRecord:
    id: str = ""
    description: str = ""
    length: int = 0
    alphabet: str = ""
    gc_content: Optional[float] = None


@dataclass
class FastqRecord:
    id: str = ""
    sequence: str = ""
    quality: str = ""
    length: int = 0
    gc_content: Optional[float] = None
    quality_mean: Optional[float] = None


@dataclass
class VcfMetadata:
    format_version: Optional[str] = None
    file_date: Optional[str] = None
    source: Optional[str] = None
    reference: Optional[str] = None
    contigs: List[str] = field(default_factory=list)
    samples: List[str] = field(default_factory=list)
    filters: Dict[str, str] = field(default_factory=dict)
    info_fields: Dict[str, str] = field(default_factory=dict)
    format_fields: List[str] = field(default_factory=list)


class GenomicExtractor:
    """Extract genomic/biological data metadata."""

    def __init__(self):
        pass

    def detect_format(self, filepath: str) -> GenomicFormat:
        """Detect genomic file format."""
        ext = Path(filepath).suffix.lower()

        if ext in ['.fa', '.fna', '.faa', '.fasta']:
            return GenomicFormat.FASTA
        elif ext in ['.fq', '.fastq']:
            return GenomicFormat.FASTQ
        elif ext in ['.vcf', '.vcf.gz']:
            return GenomicFormat.VCF
        elif ext in ['.bam']:
            return GenomicFormat.BAM
        elif ext in ['.sam']:
            return GenomicFormat.SAM
        elif ext in ['.gff', '.gff3', '.gtf']:
            return GenomicFormat.GFF
        elif ext in ['.bed']:
            return GenomicFormat.BED
        elif ext in ['.bcf']:
            return GenomicFormat.BCF

        with open(filepath, 'rb') as f:
            header = f.read(4)
            if header == b'BAM\x01':
                return GenomicFormat.BAM
            elif header[:3] in [b'VCF', b'##f']:
                return GenomicFormat.VCF

        return GenomicFormat.UNKNOWN

    def extract_fasta_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract FASTA file metadata."""
        if not BIOPYTHON_AVAILABLE:
            return self._extract_fasta_basic(filepath)

        try:
            records = []
            total_length = 0
            gc_total = 0

            for record in SeqIO.parse(filepath, "fasta"):
                rec = FastaRecord(
                    id=record.id,
                    description=record.description,
                    length=len(record.seq),
                    alphabet=str(record.seq.alphabet) if hasattr(record.seq, 'alphabet') else 'unknown',
                )

                seq_str = str(record.seq).upper()
                gc = seq_str.count('G') + seq_str.count('C')
                if len(seq_str) > 0:
                    rec.gc_content = round(gc / len(seq_str) * 100, 2)
                    gc_total += gc

                total_length += len(seq_str)
                records.append(rec)

            if total_length > 0:
                total_gc_content = round(gc_total / total_length * 100, 2)
            else:
                total_gc_content = None

            return {
                "format": "fasta",
                "record_count": len(records),
                "total_length": total_length,
                "total_gc_content": total_gc_content,
                "records": [
                    {
                        "id": r.id,
                        "length": r.length,
                        "gc_content": r.gc_content,
                    }
                    for r in records[:100]
                ],
            }

        except Exception as e:
            logger.error(f"Error parsing FASTA: {e}")
            return self._extract_fasta_basic(filepath)

    def _extract_fasta_basic(self, filepath: str) -> Dict[str, Any]:
        """Basic FASTA extraction without Biopython."""
        try:
            records = []
            total_length = 0
            gc_total = 0
            current_id = None
            current_seq = []

            open_func = gzip.open if filepath.endswith('.gz') else open
            with open_func(filepath, 'rt') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('>'):
                        if current_id:
                            seq = ''.join(current_seq)
                            records.append({
                                "id": current_id,
                                "length": len(seq),
                            })
                            gc = seq.upper().count('G') + seq.upper().count('C')
                            if len(seq) > 0:
                                gc_content = round(gc / len(seq) * 100, 2)
                                gc_total += gc
                            total_length += len(seq)
                        current_id = line[1:].split()[0] if ' ' in line[1:] else line[1:]
                        current_seq = []
                    elif current_id:
                        current_seq.append(line.upper())

            if current_id:
                seq = ''.join(current_seq)
                records.append({
                    "id": current_id,
                    "length": len(seq),
                })
                gc = seq.upper().count('G') + seq.upper().count('C')
                if len(seq) > 0:
                    gc_content = round(gc / len(seq) * 100, 2)
                    gc_total += gc
                total_length += len(seq)

            total_gc = None
            if total_length > 0:
                total_gc = round(gc_total / total_length * 100, 2)

            return {
                "format": "fasta",
                "record_count": len(records),
                "total_length": total_length,
                "total_gc_content": total_gc,
                "records": records,
            }

        except Exception as e:
            return {"error": str(e)}

    def extract_fastq_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract FASTQ file metadata."""
        if not BIOPYTHON_AVAILABLE:
            return self._extract_fastq_basic(filepath)

        try:
            records = []
            total_length = 0
            quality_scores = []
            gc_total = 0

            for record in SeqIO.parse(filepath, "fastq"):
                rec = FastqRecord(
                    id=record.id,
                    sequence=str(record.seq),
                    quality=record.letter_annotations.get('phred_quality', []),
                    length=len(record.seq),
                )

                seq_str = str(record.seq).upper()
                gc = seq_str.count('G') + seq_str.count('C')
                if len(seq_str) > 0:
                    rec.gc_content = round(gc / len(seq_str) * 100, 2)
                    gc_total += gc

                if rec.quality:
                    rec.quality_mean = sum(rec.quality) / len(rec.quality)

                total_length += len(seq_str)
                quality_scores.extend(rec.quality)
                records.append(rec)

            avg_quality = None
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)

            return {
                "format": "fastq",
                "record_count": len(records),
                "total_bases": total_length,
                "avg_gc_content": round(gc_total / total_length * 100, 2) if total_length > 0 else None,
                "avg_quality_score": round(avg_quality, 2) if avg_quality else None,
                "records_sample": [
                    {
                        "id": r.id,
                        "length": r.length,
                        "gc_content": r.gc_content,
                        "quality_mean": r.quality_mean,
                    }
                    for r in records[:50]
                ],
            }

        except Exception as e:
            logger.error(f"Error parsing FASTQ: {e}")
            return self._extract_fastq_basic(filepath)

    def _extract_fastq_basic(self, filepath: str) -> Dict[str, Any]:
        """Basic FASTQ extraction without Biopython."""
        try:
            records = []
            total_length = 0
            quality_scores = []
            gc_total = 0

            open_func = gzip.open if filepath.endswith('.gz') else open
            with open_func(filepath, 'rt') as f:
                i = 0
                lines = f.readlines()
                while i < len(lines):
                    if lines[i].startswith('@'):
                        rec_id = lines[i][1:].strip()
                        i += 1
                        seq = lines[i].strip().upper()
                        i += 2
                        qual = lines[i].strip()
                        i += 1

                        rec = {
                            "id": rec_id,
                            "length": len(seq),
                        }
                        gc = seq.count('G') + seq.count('C')
                        if len(seq) > 0:
                            rec["gc_content"] = round(gc / len(seq) * 100, 2)
                            gc_total += gc
                        total_length += len(seq)

                        for q in qual:
                            try:
                                quality_scores.append(ord(q) - 33)
                            except:
                                pass

                        records.append(rec)

            avg_quality = None
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)

            return {
                "format": "fastq",
                "record_count": len(records),
                "total_bases": total_length,
                "avg_gc_content": round(gc_total / total_length * 100, 2) if total_length > 0 else None,
                "avg_quality_score": round(avg_quality, 2) if avg_quality else None,
            }

        except Exception as e:
            return {"error": str(e)}

    def extract_vcf_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract VCF file metadata."""
        try:
            metadata = VcfMetadata()
            info_fields = {}
            format_fields = []
            samples = []

            open_func = gzip.open if filepath.endswith('.gz') else open
            with open_func(filepath, 'rt') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('##'):
                        if 'fileformat=' in line:
                            metadata.format_version = line.split('=')[1].strip()
                        elif 'source=' in line:
                            metadata.source = line.split('=')[1].strip()
                        elif 'reference=' in line:
                            metadata.reference = line.split('=')[1].strip()
                        elif 'INFO' in line:
                            parts = line.split('=')[1].split(',')
                            if len(parts) >= 2:
                                info_fields[parts[0]] = parts[1] if len(parts) > 1 else ""
                        elif 'FORMAT' in line:
                            parts = line.split('=')[1].split(',')
                            if parts[0]:
                                format_fields.append(parts[0])
                        elif 'FILTER' in line:
                            parts = line.split('=')[1].split(',')
                            if len(parts) >= 2:
                                metadata.filters[parts[0]] = parts[1]
                    elif line.startswith('#CHROM'):
                        parts = line.split('\t')
                        if len(parts) > 9:
                            samples = parts[9:]

            result = {
                "format": "vcf",
                "format_version": metadata.format_version,
                "source": metadata.source,
                "reference": metadata.reference,
                "info_field_count": len(info_fields),
                "format_field_count": len(format_fields),
                "sample_count": len(samples),
                "sample_names": samples,
                "filter_count": len(metadata.filters),
            }

            return result

        except Exception as e:
            logger.error(f"Error parsing VCF: {e}")
            return {"error": str(e)}

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract genomic metadata from a file."""
        result = {
            "source": "metaextract_genomic_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "genomic_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        format_type = self.detect_format(filepath)
        result["format_detected"] = format_type.value

        if format_type == GenomicFormat.FASTA:
            result["genomic_metadata"] = self.extract_fasta_metadata(filepath)
            result["extraction_success"] = "error" not in result["genomic_metadata"]

        elif format_type == GenomicFormat.FASTQ:
            result["genomic_metadata"] = self.extract_fastq_metadata(filepath)
            result["extraction_success"] = "error" not in result["genomic_metadata"]

        elif format_type == GenomicFormat.VCF:
            result["genomic_metadata"] = self.extract_vcf_metadata(filepath)
            result["extraction_success"] = "error" not in result["genomic_metadata"]

        else:
            result["genomic_metadata"] = {"message": "Unsupported genomic format"}
            result["extraction_success"] = False

        return result


def extract_genomic_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract genomic metadata."""
    extractor = GenomicExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python genomic_extractor.py <file.fasta>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_genomic_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))

def get_genomic_extractor_field_count() -> int:
    """
    Return the number of genomic metadata fields extracted.
    
    Returns:
        Total field count (6 fields)
    """
    return 6  # source, filepath, format_detected, extraction_success, genomic_metadata, error

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python genomic_extractor.py <file.fasta|fastq|vcf>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_genomic_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
