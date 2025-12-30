# server/extractor/modules/biotechnology_metadata.py

"""
Biotechnology metadata extraction for Phase 4.

Extracts metadata from:
- Genomic data files (FASTA, FASTQ, BAM, VCF)
- Protein structure files (PDB, mmCIF)
- Lab equipment configurations
- Experimental protocols
- Bioinformatics pipelines
- Drug discovery data
- CRISPR/Cas9 designs
"""

import logging
import json
import re
import struct
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import gzip

logger = logging.getLogger(__name__)

# Biotechnology file extensions and formats
BIOTECHNOLOGY_EXTENSIONS = [
    '.fasta', '.fastq', '.fa', '.fq', '.bam', '.sam', '.vcf', '.bcf',
    '.pdb', '.cif', '.mmcif', '.sdf', '.mol', '.mol2', '.pdbqt',
    '.gb', '.gbk', '.gff', '.gtf', '.bed', '.wig', '.bigwig',
    '.json', '.yaml', '.yml', '.xml', '.csv', '.tsv', '.txt'
]

# Biotechnology-specific keywords
BIOTECHNOLOGY_KEYWORDS = [
    'genome', 'dna', 'rna', 'protein', 'sequence', 'gene',
    'chromosome', 'transcript', 'exon', 'intron', 'promoter',
    'orf', 'cds', 'utr', 'snp', 'mutation', 'variant',
    'alignment', 'blast', 'primer', 'probe', 'oligo',
    'pcr', 'sequencing', 'ngs', 'mass_spec', 'crispr',
    'cas9', 'talen', 'zfn', 'sirna', 'microrna',
    'antibody', 'antigen', 'enzyme', 'receptor', 'ligand',
    'pathway', 'metabolism', 'biosynthesis', 'biodegradation',
    'fermentation', 'bioreactor', 'cell_culture', 'tissue',
    'organoid', 'stem_cell', 'differentiation', 'transfection',
    'transduction', 'electroporation', 'lipofection'
]


def extract_biotechnology_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract biotechnology metadata from genomic, proteomic, and experimental files.

    Supports various bioinformatics and biotechnology formats.
    """
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is biotechnology-related
        is_biotech_file = _is_biotechnology_related_file(filepath, filename)

        if not is_biotech_file:
            return result

        result['biotechnology_file_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.fasta', '.fa']:
            fasta_data = _extract_fasta_metadata(filepath)
            result.update(fasta_data)

        elif file_ext in ['.fastq', '.fq']:
            fastq_data = _extract_fastq_metadata(filepath)
            result.update(fastq_data)

        elif file_ext in ['.bam', '.sam']:
            alignment_data = _extract_alignment_metadata(filepath)
            result.update(alignment_data)

        elif file_ext in ['.vcf', '.bcf']:
            variant_data = _extract_variant_metadata(filepath)
            result.update(variant_data)

        elif file_ext in ['.pdb', '.cif', '.mmcif']:
            structure_data = _extract_structure_metadata(filepath)
            result.update(structure_data)

        elif file_ext in ['.sdf', '.mol', '.mol2', '.pdbqt']:
            molecule_data = _extract_molecule_metadata(filepath)
            result.update(molecule_data)

        elif file_ext in ['.gb', '.gbk']:
            genbank_data = _extract_genbank_metadata(filepath)
            result.update(genbank_data)

        elif file_ext in ['.gff', '.gtf']:
            annotation_data = _extract_annotation_metadata(filepath)
            result.update(annotation_data)

        elif file_ext in ['.json', '.yaml', '.yml']:
            biotech_config_data = _extract_biotech_config_metadata(filepath)
            result.update(biotech_config_data)

        elif file_ext in ['.csv', '.tsv', '.txt']:
            experimental_data = _extract_experimental_metadata(filepath)
            result.update(experimental_data)

        # Extract general biotechnology properties
        general_data = _extract_general_biotechnology_properties(filepath)
        result.update(general_data)

        # Analyze biotechnology components
        biotech_analysis = _analyze_biotechnology_components(filepath)
        result.update(biotech_analysis)

    except Exception as e:
        logger.warning(f"Error extracting biotechnology metadata from {filepath}: {e}")
        result['biotechnology_extraction_error'] = str(e)

    return result


def _is_biotechnology_related_file(filepath: str, filename: str) -> bool:
    """Check if file is biotechnology-related."""
    try:
        # Check filename patterns
        biotech_patterns = [
            'genome', 'dna', 'rna', 'protein', 'sequence', 'gene',
            'transcript', 'chromosome', 'snp', 'variant', 'alignment',
            'primer', 'pcr', 'sequencing', 'crispr', 'antibody'
        ]
        if any(pattern in filename for pattern in biotech_patterns):
            return True

        # Check file content for biotechnology keywords
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)  # Read first 4KB

        content_lower = content.lower()

        # Count biotechnology keywords
        biotech_keyword_count = sum(1 for keyword in BIOTECHNOLOGY_KEYWORDS if keyword in content_lower)

        # Must have multiple biotechnology keywords to be considered biotech-related
        if biotech_keyword_count >= 3:
            return True

        # Check for specific biotechnology patterns
        biotech_patterns = [
            r'^>',  # FASTA header
            r'^@',  # FASTQ header
            r'LOCUS|DEFINITION|ACCESSION',  # GenBank
            r'ATOM|HETATM',  # PDB structure
            r'HEADER|TITLE|COMPND',  # PDB/mmCIF headers
            r'##fileformat=VCF',  # VCF header
            r'@SQ|@HD|@PG',  # SAM header
            r'##gff-version|##gtf',  # GFF/GTF
        ]

        for pattern in biotech_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True

    except Exception:
        pass

    return False


def _extract_fasta_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from FASTA sequence files."""
    fasta_data = {'biotechnology_fasta_format_present': True}

    try:
        sequences = []
        headers = []
        total_length = 0

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            current_seq = []
            current_header = None

            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # Save previous sequence
                    if current_header and current_seq:
                        seq_str = ''.join(current_seq)
                        sequences.append({
                            'header': current_header,
                            'length': len(seq_str),
                            'sequence': seq_str[:100] + '...' if len(seq_str) > 100 else seq_str
                        })
                        total_length += len(seq_str)

                    # Start new sequence
                    current_header = line[1:]  # Remove '>'
                    headers.append(current_header)
                    current_seq = []
                elif line and current_header:
                    current_seq.append(line.upper())

            # Don't forget the last sequence
            if current_header and current_seq:
                seq_str = ''.join(current_seq)
                sequences.append({
                    'header': current_header,
                    'length': len(seq_str),
                    'sequence': seq_str[:100] + '...' if len(seq_str) > 100 else seq_str
                })
                total_length += len(seq_str)

        fasta_data['biotechnology_sequence_count'] = len(sequences)
        fasta_data['biotechnology_total_sequence_length'] = total_length

        if sequences:
            avg_length = total_length / len(sequences)
            fasta_data['biotechnology_average_sequence_length'] = round(avg_length, 2)

        # Analyze sequence types
        sequence_types = {'dna': 0, 'rna': 0, 'protein': 0, 'unknown': 0}

        for seq in sequences:
            seq_type = _classify_sequence(seq['sequence'])
            sequence_types[seq_type] += 1

        if sequence_types['dna'] > 0 or sequence_types['rna'] > 0 or sequence_types['protein'] > 0:
            fasta_data['biotechnology_sequence_types'] = {k: v for k, v in sequence_types.items() if v > 0}

        # Extract species information from headers
        species_info = _extract_species_from_headers(headers)
        if species_info:
            fasta_data['biotechnology_species_info'] = species_info

        # Check for common databases
        database_info = _identify_sequence_database(headers)
        if database_info:
            fasta_data['biotechnology_database_info'] = database_info

    except Exception as e:
        fasta_data['biotechnology_fasta_extraction_error'] = str(e)

    return fasta_data


def _extract_fastq_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from FASTQ sequence files."""
    fastq_data = {'biotechnology_fastq_format_present': True}

    try:
        read_count = 0
        total_length = 0
        quality_scores = []

        # Handle gzipped files
        if filepath.endswith('.gz'):
            import gzip
            opener = gzip.open
            mode = 'rt'
        else:
            opener = open
            mode = 'r'

        with opener(filepath, mode, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Process FASTQ records (4 lines per read)
        for i in range(0, len(lines), 4):
            if i + 3 >= len(lines):
                break

            header = lines[i].strip()
            sequence = lines[i + 1].strip()
            quality = lines[i + 3].strip()

            read_count += 1
            total_length += len(sequence)

            # Collect quality scores (first 100 reads for performance)
            if read_count <= 100 and quality:
                quality_scores.extend(ord(c) - 33 for c in quality)  # Phred+33

        fastq_data['biotechnology_read_count'] = read_count
        fastq_data['biotechnology_total_read_length'] = total_length

        if read_count > 0:
            avg_length = total_length / read_count
            fastq_data['biotechnology_average_read_length'] = round(avg_length, 2)

        # Analyze quality scores
        if quality_scores:
            fastq_data['biotechnology_mean_quality_score'] = round(sum(quality_scores) / len(quality_scores), 2)
            fastq_data['biotechnology_min_quality_score'] = min(quality_scores)
            fastq_data['biotechnology_max_quality_score'] = max(quality_scores)

        # Extract instrument information from headers
        if read_count > 0:
            first_header = lines[0].strip()
            instrument_info = _extract_sequencing_instrument_info(first_header)
            if instrument_info:
                fastq_data['biotechnology_sequencing_instrument'] = instrument_info

        # Estimate sequencing technology
        if read_count > 0:
            tech_info = _estimate_sequencing_technology(avg_length if 'avg_length' in locals() else 0)
            if tech_info:
                fastq_data['biotechnology_sequencing_technology'] = tech_info

    except Exception as e:
        fastq_data['biotechnology_fastq_extraction_error'] = str(e)

    return fastq_data


def _extract_alignment_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from BAM/SAM alignment files."""
    alignment_data = {'biotechnology_alignment_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext == '.sam':
            alignment_data['biotechnology_alignment_format'] = 'SAM'
            # Parse SAM header
            header_info = _parse_sam_header(filepath)
            alignment_data.update(header_info)

        elif file_ext == '.bam':
            alignment_data['biotechnology_alignment_format'] = 'BAM'
            # For BAM files, we can try to get basic info
            alignment_data['biotechnology_bam_format'] = True

        # Get file size for data estimation
        stat_info = Path(filepath).stat()
        file_size = stat_info.st_size

        alignment_data['biotechnology_alignment_file_size'] = file_size

        # Estimate number of alignments (rough estimate)
        if file_ext == '.sam':
            # Count non-header lines
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                alignment_count = sum(1 for line in f if line.strip() and not line.startswith('@'))
            alignment_data['biotechnology_alignment_count'] = alignment_count

        elif file_ext == '.bam':
            # Rough estimate for BAM files (30-40 bytes per alignment)
            estimated_alignments = file_size // 35
            alignment_data['biotechnology_estimated_alignment_count'] = estimated_alignments

    except Exception as e:
        alignment_data['biotechnology_alignment_extraction_error'] = str(e)

    return alignment_data


def _extract_variant_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from VCF variant files."""
    variant_data = {'biotechnology_variant_format_present': True}

    try:
        variant_count = 0
        sample_count = 0
        chromosomes = set()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()

                if line.startswith('##'):
                    # Parse VCF header metadata
                    if line.startswith('##fileformat='):
                        variant_data['biotechnology_vcf_version'] = line.split('=')[1]
                    elif line.startswith('##reference='):
                        variant_data['biotechnology_reference_genome'] = line.split('=')[1]
                    elif line.startswith('##contig='):
                        # Extract contig information
                        contig_match = re.search(r'ID=([^,]+)', line)
                        if contig_match:
                            chromosomes.add(contig_match.group(1))

                elif line.startswith('#CHROM'):
                    # Sample names line
                    parts = line.split('\t')
                    if len(parts) > 9:
                        sample_count = len(parts) - 9
                        variant_data['biotechnology_sample_count'] = sample_count

                elif line and not line.startswith('#'):
                    # Variant line
                    variant_count += 1
                    parts = line.split('\t')
                    if len(parts) >= 1:
                        chromosomes.add(parts[0])

        variant_data['biotechnology_variant_count'] = variant_count

        if chromosomes:
            variant_data['biotechnology_chromosomes'] = sorted(list(chromosomes))

        # Classify variants (if we have some)
        if variant_count > 0:
            variant_types = _classify_variants(filepath)
            if variant_types:
                variant_data['biotechnology_variant_types'] = variant_types

    except Exception as e:
        variant_data['biotechnology_variant_extraction_error'] = str(e)

    return variant_data


def _extract_structure_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from protein structure files (PDB, mmCIF)."""
    structure_data = {'biotechnology_structure_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)  # Read first 10KB

        if file_ext == '.pdb':
            structure_data['biotechnology_structure_format'] = 'PDB'

            # Parse PDB headers
            pdb_info = _parse_pdb_headers(content)
            structure_data.update(pdb_info)

        elif file_ext in ['.cif', '.mmcif']:
            structure_data['biotechnology_structure_format'] = 'mmCIF'

            # Parse mmCIF headers
            cif_info = _parse_cif_headers(content)
            structure_data.update(cif_info)

        # Count atoms and residues
        atom_count = content.count('ATOM') + content.count('HETATM')
        structure_data['biotechnology_atom_count'] = atom_count

        # Extract molecule information
        molecule_info = _extract_molecule_info(content, file_ext)
        if molecule_info:
            structure_data.update(molecule_info)

    except Exception as e:
        structure_data['biotechnology_structure_extraction_error'] = str(e)

    return structure_data


def _extract_molecule_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from molecular structure files (SDF, MOL, MOL2)."""
    molecule_data = {'biotechnology_molecule_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if file_ext == '.sdf':
            molecule_data['biotechnology_molecule_format'] = 'SDF'

            # Parse SDF entries
            sdf_entries = content.split('$$$$')
            molecule_data['biotechnology_molecule_count'] = len(sdf_entries) - 1  # Last split is empty

            if len(sdf_entries) > 1:
                first_molecule = sdf_entries[0]
                mol_info = _parse_sdf_molecule(first_molecule)
                molecule_data.update(mol_info)

        elif file_ext == '.mol':
            molecule_data['biotechnology_molecule_format'] = 'MOL'

            mol_info = _parse_mol_file(content)
            molecule_data.update(mol_info)

        elif file_ext == '.mol2':
            molecule_data['biotechnology_molecule_format'] = 'MOL2'

            mol2_info = _parse_mol2_file(content)
            molecule_data.update(mol2_info)

        # Extract molecular properties
        molecular_props = _calculate_molecular_properties(content, file_ext)
        if molecular_props:
            molecule_data.update(molecular_props)

    except Exception as e:
        molecule_data['biotechnology_molecule_extraction_error'] = str(e)

    return molecule_data


def _extract_genbank_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from GenBank files."""
    genbank_data = {'biotechnology_genbank_format_present': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(50000)  # Read first 50KB

        # Extract LOCUS information
        locus_match = re.search(r'LOCUS\s+(\S+)', content, re.IGNORECASE)
        if locus_match:
            genbank_data['biotechnology_locus'] = locus_match.group(1)

        # Extract sequence length
        length_match = re.search(r'LOCUS\s+\S+\s+(\d+)\s+bp', content, re.IGNORECASE)
        if length_match:
            genbank_data['biotechnology_sequence_length'] = int(length_match.group(1))

        # Extract definition
        definition_match = re.search(r'DEFINITION\s+(.+?)(?:\n[A-Z]|$)', content, re.DOTALL | re.IGNORECASE)
        if definition_match:
            genbank_data['biotechnology_definition'] = definition_match.group(1).strip()

        # Extract accession
        accession_match = re.search(r'ACCESSION\s+(\S+)', content, re.IGNORECASE)
        if accession_match:
            genbank_data['biotechnology_accession'] = accession_match.group(1)

        # Extract organism
        organism_match = re.search(r'ORGANISM\s+(.+?)(?:\n[A-Z]|$)', content, re.DOTALL | re.IGNORECASE)
        if organism_match:
            genbank_data['biotechnology_organism'] = organism_match.group(1).strip()

        # Count features
        feature_count = len(re.findall(r'^\s+\w+\s+', content, re.MULTILINE))
        genbank_data['biotechnology_feature_count'] = feature_count

        # Extract feature types
        feature_types = {}
        feature_matches = re.findall(r'^\s+(\w+)\s+', content, re.MULTILINE)
        for feature_type in feature_matches:
            feature_types[feature_type] = feature_types.get(feature_type, 0) + 1

        if feature_types:
            genbank_data['biotechnology_feature_types'] = feature_types

    except Exception as e:
        genbank_data['biotechnology_genbank_extraction_error'] = str(e)

    return genbank_data


def _extract_annotation_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from GFF/GTF annotation files."""
    annotation_data = {'biotechnology_annotation_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext == '.gff':
            annotation_data['biotechnology_annotation_format'] = 'GFF'
        elif file_ext == '.gtf':
            annotation_data['biotechnology_annotation_format'] = 'GTF'

        feature_count = 0
        sources = set()
        feature_types = {}
        chromosomes = set()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()

                if line.startswith('#'):
                    continue

                parts = line.split('\t')
                if len(parts) >= 9:
                    feature_count += 1

                    # Extract chromosome/contig
                    chromosomes.add(parts[0])

                    # Extract source
                    sources.add(parts[1])

                    # Extract feature type
                    feature_type = parts[2]
                    feature_types[feature_type] = feature_types.get(feature_type, 0) + 1

        annotation_data['biotechnology_annotation_feature_count'] = feature_count

        if sources:
            annotation_data['biotechnology_annotation_sources'] = sorted(list(sources))

        if feature_types:
            annotation_data['biotechnology_annotation_feature_types'] = feature_types

        if chromosomes:
            annotation_data['biotechnology_annotation_chromosomes'] = sorted(list(chromosomes))

    except Exception as e:
        annotation_data['biotechnology_annotation_extraction_error'] = str(e)

    return annotation_data


def _extract_biotech_config_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from biotechnology configuration files."""
    config_data = {'biotechnology_config_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext in ['.yaml', '.yml']:
            import yaml
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = yaml.safe_load(f)
        elif file_ext == '.json':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

        if isinstance(data, dict):
            # Check for bioinformatics pipeline configuration
            if any(key in data for key in ['pipeline', 'workflow', 'steps', 'tools']):
                config_data['biotechnology_pipeline_config'] = True

                # Extract pipeline steps
                if 'steps' in data:
                    steps = data['steps']
                    if isinstance(steps, list):
                        config_data['biotechnology_pipeline_step_count'] = len(steps)

                        step_types = {}
                        for step in steps:
                            if isinstance(step, dict):
                                step_type = step.get('type') or step.get('tool') or step.get('name', '')
                                if step_type:
                                    step_types[step_type] = step_types.get(step_type, 0) + 1

                        if step_types:
                            config_data['biotechnology_pipeline_step_types'] = step_types

            # Check for experimental protocol configuration
            if any(key in data for key in ['protocol', 'experiment', 'assay', 'method']):
                config_data['biotechnology_experiment_config'] = True

            # Check for sequencing configuration
            if any(key in data for key in ['sequencing', 'ngs', 'illumina', 'pacbio']):
                config_data['biotechnology_sequencing_config'] = True

            # Check for analysis parameters
            if any(key in data for key in ['parameters', 'settings', 'config']):
                config_data['biotechnology_analysis_config'] = True

    except Exception as e:
        config_data['biotechnology_config_extraction_error'] = str(e)

    return config_data


def _extract_experimental_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from experimental data files."""
    experimental_data = {'biotechnology_experimental_format_present': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        # Determine delimiter
        if file_ext == '.csv':
            delimiter = ','
        elif file_ext == '.tsv':
            delimiter = '\t'
        else:
            delimiter = None  # Auto-detect

        row_count = 0
        column_count = 0
        headers = []

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                line = line.strip()

                if not line:
                    continue

                if i == 0:
                    # Try to detect delimiter if not set
                    if delimiter is None:
                        if '\t' in line:
                            delimiter = '\t'
                        else:
                            delimiter = ','

                    headers = line.split(delimiter)
                    column_count = len(headers)

                row_count += 1

                # Limit reading for performance
                if i >= 1000:
                    break

        experimental_data['biotechnology_data_row_count'] = row_count
        experimental_data['biotechnology_data_column_count'] = column_count

        if headers:
            experimental_data['biotechnology_data_headers'] = headers[:10]  # First 10 headers

        # Try to identify data type
        data_type = _identify_experimental_data_type(headers)
        if data_type:
            experimental_data['biotechnology_experimental_data_type'] = data_type

    except Exception as e:
        experimental_data['biotechnology_experimental_extraction_error'] = str(e)

    return experimental_data


def _extract_general_biotechnology_properties(filepath: str) -> Dict[str, Any]:
    """Extract general biotechnology file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['biotechnology_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['biotechnology_filename'] = filename

        # Check for biotechnology-specific naming patterns
        biotech_indicators = [
            'genome', 'dna', 'rna', 'protein', 'sequence', 'gene',
            'transcript', 'chromosome', 'snp', 'variant', 'primer'
        ]
        if any(indicator in filename.lower() for indicator in biotech_indicators):
            props['biotechnology_filename_suggests_biotech'] = True

        # Extract version numbers from filename
        version_match = re.search(r'v?(\d+(?:\.\d+)*)', filename)
        if version_match:
            props['biotechnology_file_version_hint'] = version_match.group(1)

    except Exception:
        pass

    return props


def _analyze_biotechnology_components(filepath: str) -> Dict[str, Any]:
    """Analyze biotechnology components and research focus."""
    analysis = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8192)  # Read first 8KB

        # Analyze research domain
        research_domains = {
            'genomics': ['genome', 'dna', 'chromosome', 'sequencing', 'ngs'],
            'transcriptomics': ['rna', 'transcript', 'mrna', 'microrna', 'expression'],
            'proteomics': ['protein', 'peptide', 'mass_spec', 'proteome'],
            'metabolomics': ['metabolite', 'metabolism', 'lcms', 'gcms'],
            'structural_biology': ['structure', 'pdb', 'crystal', 'nmr', 'cryoem'],
            'drug_discovery': ['drug', 'compound', 'screening', 'docking', 'pharmacophore'],
            'gene_editing': ['crispr', 'cas9', 'talen', 'zfn', 'editing'],
            'synthetic_biology': ['synthetic', 'biosynthesis', 'pathway', 'engineering'],
            'microbiome': ['microbiome', 'microbiota', '16s', 'metagenomics'],
            'immunology': ['antibody', 'antigen', 'immune', 'tcell', 'bcell'],
        }

        detected_domains = {}
        for domain, indicators in research_domains.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_domains[domain] = count

        if detected_domains:
            # Find primary research domain
            primary_domain = max(detected_domains.items(), key=lambda x: x[1])[0]
            analysis['biotechnology_primary_research_domain'] = primary_domain

        # Analyze experimental techniques
        techniques = {
            'pcr': ['pcr', 'polymerase', 'amplification'],
            'sequencing': ['sequencing', 'ngs', 'illumina', 'pacbio', 'ont'],
            'mass_spectrometry': ['mass_spec', 'ms', 'lcms', 'gcms', 'proteomics'],
            'crystallography': ['crystal', 'xray', 'diffraction'],
            'nmr': ['nmr', 'nuclear', 'magnetic', 'resonance'],
            'cryo_em': ['cryoem', 'cryo-em', 'electron', 'microscopy'],
            'flow_cytometry': ['flow', 'cytometry', 'facs'],
            'microarray': ['microarray', 'chip', 'array'],
            'rna_seq': ['rna-seq', 'rnaseq', 'transcriptomics'],
            'chip_seq': ['chip-seq', 'chipseq', 'chromatin'],
        }

        detected_techniques = {}
        for technique, indicators in techniques.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_techniques[technique] = count

        if detected_techniques:
            analysis['biotechnology_experimental_techniques'] = detected_techniques

        # Check for bioinformatics tools
        bioinfo_tools = [
            'blast', 'bowtie', 'bwa', 'samtools', 'bedtools', 'picard',
            'gatk', 'freebayes', 'varscan', 'snpeff', 'annovar',
            'trinity', 'cufflinks', 'tophat', 'hisat', 'kallisto',
            'salmon', 'star', 'featurecounts', 'deseq', 'edger'
        ]

        detected_tools = [tool for tool in bioinfo_tools if tool in content.lower()]
        if detected_tools:
            analysis['biotechnology_bioinformatics_tools'] = detected_tools

        # Check for model organisms
        model_organisms = {
            'human': ['homo', 'sapiens', 'hg38', 'grch38'],
            'mouse': ['mus', 'musculus', 'mm10', 'grcm38'],
            'rat': ['rattus', 'norvegicus', 'rn6'],
            'zebrafish': ['danio', 'rerio', 'danrer10'],
            'fruitfly': ['drosophila', 'melanogaster', 'dm6'],
            'yeast': ['saccharomyces', 'cerevisiae', 'saccer3'],
            'ecoli': ['escherichia', 'coli', 'k12'],
            'arabidopsis': ['arabidopsis', 'thaliana', 'tair10'],
        }

        detected_organisms = {}
        for organism, indicators in model_organisms.items():
            count = sum(1 for indicator in indicators if indicator in content.lower())
            if count > 0:
                detected_organisms[organism] = count

        if detected_organisms:
            analysis['biotechnology_model_organisms'] = detected_organisms

    except Exception:
        pass

    return analysis


# Helper functions for biotechnology metadata extraction

def _classify_sequence(sequence: str) -> str:
    """Classify sequence type (DNA, RNA, protein, or unknown)."""
    if not sequence:
        return 'unknown'

    # Count nucleotide bases
    dna_bases = sequence.count('A') + sequence.count('T') + sequence.count('G') + sequence.count('C')
    rna_bases = sequence.count('A') + sequence.count('U') + sequence.count('G') + sequence.count('C')

    # Count amino acids (common ones)
    amino_acids = sum(sequence.count(aa) for aa in 'ACDEFGHIKLMNPQRSTVWY')

    total_chars = len(sequence)

    if dna_bases / total_chars > 0.8:
        return 'dna'
    elif rna_bases / total_chars > 0.8:
        return 'rna'
    elif amino_acids / total_chars > 0.5:
        return 'protein'
    else:
        return 'unknown'


def _extract_species_from_headers(headers: List[str]) -> Optional[Dict[str, Any]]:
    """Extract species information from sequence headers."""
    species_patterns = [
        r'\[([^\]]+)\]',  # [Species name]
        r'([A-Z][a-z]+ [a-z]+)',  # Genus species
        r'sp\.|species|strain',  # Species indicators
    ]

    species_mentions = []
    for header in headers[:10]:  # Check first 10 headers
        for pattern in species_patterns:
            matches = re.findall(pattern, header, re.IGNORECASE)
            species_mentions.extend(matches)

    if species_mentions:
        # Count occurrences
        species_count = {}
        for species in species_mentions:
            species_count[species] = species_count.get(species, 0) + 1

        return {
            'detected_species': list(species_count.keys()),
            'primary_species': max(species_count.items(), key=lambda x: x[1])[0]
        }

    return None


def _identify_sequence_database(headers: List[str]) -> Optional[Dict[str, Any]]:
    """Identify the database source of sequences."""
    database_patterns = {
        'genbank': r'[A-Z]{1,2}\d{5,}',
        'refseq': r'NC_\d+|NM_\d+|NP_\d+|NR_\d+|XM_\d+|XP_\d+|XR_\d+',
        'ensembl': r'ENS[A-Z]+\d+',
        'uniprot': r'[A-Z0-9]{6,10}',
        'pdb': r'\d[A-Z0-9]{3}',
    }

    database_matches = {}
    for header in headers[:5]:  # Check first 5 headers
        for db_name, pattern in database_patterns.items():
            if re.search(pattern, header):
                database_matches[db_name] = database_matches.get(db_name, 0) + 1

    if database_matches:
        primary_db = max(database_matches.items(), key=lambda x: x[1])[0]
        return {
            'detected_databases': list(database_matches.keys()),
            'primary_database': primary_db
        }

    return None


def _extract_sequencing_instrument_info(header: str) -> Optional[str]:
    """Extract sequencing instrument information from FASTQ header."""
    # Illumina format: @<instrument>:<run number>:<flowcell ID>:<lane>:<tile>:<x-pos>:<y-pos> <read>:<is filtered>:<control number>:<sample number>
    instrument_match = re.search(r'@([^:]+):', header)
    if instrument_match:
        return instrument_match.group(1)

    return None


def _estimate_sequencing_technology(avg_read_length: float) -> Optional[str]:
    """Estimate sequencing technology based on read length."""
    if avg_read_length == 0:
        return None

    if avg_read_length < 100:
        return 'short_read'
    elif 100 <= avg_read_length <= 400:
        return 'long_read_pacbio'
    elif avg_read_length > 400:
        return 'long_read_nanopore'
    else:
        return 'unknown'


def _parse_sam_header(filepath: str) -> Dict[str, Any]:
    """Parse SAM file header."""
    header_info = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.startswith('@'):
                    break

                if line.startswith('@HD'):
                    # Header line
                    parts = line.strip().split('\t')
                    for part in parts[1:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            header_info[f'biotechnology_sam_hd_{key.lower()}'] = value

                elif line.startswith('@SQ'):
                    # Sequence dictionary
                    if 'biotechnology_sam_sequences' not in header_info:
                        header_info['biotechnology_sam_sequences'] = []
                    seq_info = {}
                    parts = line.strip().split('\t')
                    for part in parts[1:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            seq_info[key.lower()] = value
                    header_info['biotechnology_sam_sequences'].append(seq_info)

                elif line.startswith('@PG'):
                    # Program record
                    if 'biotechnology_sam_programs' not in header_info:
                        header_info['biotechnology_sam_programs'] = []
                    pg_info = {}
                    parts = line.strip().split('\t')
                    for part in parts[1:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            pg_info[key.lower()] = value
                    header_info['biotechnology_sam_programs'].append(pg_info)

    except Exception:
        pass

    return header_info


def _classify_variants(filepath: str) -> Optional[Dict[str, Any]]:
    """Classify variants in VCF file."""
    variant_types = {'snp': 0, 'indel': 0, 'other': 0}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i > 1000:  # Limit for performance
                    break

                if line.startswith('#'):
                    continue

                parts = line.split('\t')
                if len(parts) >= 5:
                    ref = parts[3]
                    alt = parts[4]

                    if len(ref) == 1 and len(alt) == 1:
                        variant_types['snp'] += 1
                    elif len(ref) != len(alt):
                        variant_types['indel'] += 1
                    else:
                        variant_types['other'] += 1

    except Exception:
        pass

    return variant_types if sum(variant_types.values()) > 0 else None


def _parse_pdb_headers(content: str) -> Dict[str, Any]:
    """Parse PDB file headers."""
    pdb_info = {}

    # Extract HEADER
    header_match = re.search(r'^HEADER\s+(.+?)\s+(\d{2}-\w{3}-\d{2})\s+(\w{4})', content, re.MULTILINE)
    if header_match:
        pdb_info['biotechnology_pdb_classification'] = header_match.group(1).strip()
        pdb_info['biotechnology_pdb_deposition_date'] = header_match.group(2)
        pdb_info['biotechnology_pdb_id'] = header_match.group(3)

    # Extract TITLE
    title_match = re.search(r'^TITLE\s+(.+?)(?=^[^T]|$)', content, re.MULTILINE | re.DOTALL)
    if title_match:
        pdb_info['biotechnology_pdb_title'] = title_match.group(1).strip()

    # Extract COMPND
    compnd_match = re.search(r'^COMPND\s+(.+?)(?=^[A-Z]|$)', content, re.MULTILINE | re.DOTALL)
    if compnd_match:
        pdb_info['biotechnology_pdb_compound'] = compnd_match.group(1).strip()

    # Extract SOURCE
    source_match = re.search(r'^SOURCE\s+(.+?)(?=^[A-Z]|$)', content, re.MULTILINE | re.DOTALL)
    if source_match:
        pdb_info['biotechnology_pdb_source'] = source_match.group(1).strip()

    return pdb_info


def _parse_cif_headers(content: str) -> Dict[str, Any]:
    """Parse mmCIF file headers."""
    cif_info = {}

    # Extract entry ID
    entry_match = re.search(r'_entry\.id\s+(\w+)', content)
    if entry_match:
        cif_info['biotechnology_cif_entry_id'] = entry_match.group(1)

    # Extract title
    title_match = re.search(r'_struct\.title\s+(.+?)(?=_|\n)', content)
    if title_match:
        cif_info['biotechnology_cif_title'] = title_match.group(1).strip()

    return cif_info


def _extract_molecule_info(content: str, file_ext: str) -> Dict[str, Any]:
    """Extract molecule information from structure files."""
    mol_info = {}

    if file_ext == '.pdb':
        # Count residues
        residue_count = len(re.findall(r'^ATOM\s+\d+\s+\w+\s+(\w{3})\s+', content, re.MULTILINE))
        mol_info['biotechnology_residue_count'] = residue_count

        # Count chains
        chains = set()
        chain_matches = re.findall(r'^ATOM\s+\d+\s+\w+\s+\w{3}\s+(\w)\s+', content, re.MULTILINE)
        chains.update(chain_matches)
        mol_info['biotechnology_chain_count'] = len(chains)

    return mol_info


def _parse_sdf_molecule(content: str) -> Dict[str, Any]:
    """Parse SDF molecule information."""
    mol_info = {}

    lines = content.split('\n')

    if len(lines) >= 4:
        # Line 1: Molecule name
        mol_info['biotechnology_molecule_name'] = lines[0].strip()

        # Line 4: Counts line (aaabbblllfffcccsssxxxrrrpppiiimmmvvvvvv)
        if len(lines[3]) >= 6:
            try:
                atom_count = int(lines[3][:3])
                bond_count = int(lines[3][3:6])
                mol_info['biotechnology_atom_count'] = atom_count
                mol_info['biotechnology_bond_count'] = bond_count
            except ValueError:
                pass

    return mol_info


def _parse_mol_file(content: str) -> Dict[str, Any]:
    """Parse MOL file information."""
    mol_info = {'biotechnology_molecule_format': 'MOL'}

    lines = content.split('\n')

    if len(lines) >= 4:
        # Similar to SDF
        try:
            atom_count = int(lines[3][:3])
            bond_count = int(lines[3][3:6])
            mol_info['biotechnology_atom_count'] = atom_count
            mol_info['biotechnology_bond_count'] = bond_count
        except (ValueError, IndexError):
            pass

    return mol_info


def _parse_mol2_file(content: str) -> Dict[str, Any]:
    """Parse MOL2 file information."""
    mol2_info = {'biotechnology_molecule_format': 'MOL2'}

    # Count atoms
    atom_section = re.search(r'@<TRIPOS>ATOM(.+?)@', content, re.DOTALL)
    if atom_section:
        atom_lines = atom_section.group(1).strip().split('\n')
        mol2_info['biotechnology_atom_count'] = len([line for line in atom_lines if line.strip()])

    # Count bonds
    bond_section = re.search(r'@<TRIPOS>BOND(.+?)@', content, re.DOTALL)
    if bond_section:
        bond_lines = bond_section.group(1).strip().split('\n')
        mol2_info['biotechnology_bond_count'] = len([line for line in bond_lines if line.strip()])

    return mol2_info


def _calculate_molecular_properties(content: str, file_ext: str) -> Dict[str, Any]:
    """Calculate basic molecular properties."""
    props = {}

    # This is a simplified calculation - real molecular weight calculation
    # would require parsing atom types and their masses

    if file_ext == '.sdf':
        # Try to extract molecular weight from SDF properties
        mw_match = re.search(r'> <MW>[\r\n]+(\d+\.?\d*)', content)
        if mw_match:
            props['biotechnology_molecular_weight'] = float(mw_match.group(1))

    return props


def _identify_experimental_data_type(headers: List[str]) -> Optional[str]:
    """Identify the type of experimental data."""
    header_str = ' '.join(headers).lower()

    data_types = {
        'gene_expression': ['expression', 'fpkm', 'tpm', 'rpkm', 'counts'],
        'proteomics': ['peptide', 'protein', 'intensity', 'abundance'],
        'metabolomics': ['metabolite', 'mz', 'rt', 'intensity'],
        'genotyping': ['snp', 'allele', 'genotype', 'variant'],
        'methylation': ['methylation', 'beta', 'm_value'],
        'chip_seq': ['chip', 'peak', 'enrichment', 'binding'],
        'microarray': ['probe', 'bead', 'intensity'],
        'flow_cytometry': ['fsc', 'ssc', 'fl1', 'fl2', 'compensation'],
    }

    for data_type, indicators in data_types.items():
        if any(indicator in header_str for indicator in indicators):
            return data_type

    return None


def get_biotechnology_field_count() -> int:
    """Return the number of fields extracted by biotechnology metadata."""
    # Format detection (5)
    detection_fields = 5

    # FASTA specific (15)
    fasta_fields = 15

    # FASTQ specific (12)
    fastq_fields = 12

    # Alignment specific (10)
    alignment_fields = 10

    # Variant specific (10)
    variant_fields = 10

    # Structure specific (12)
    structure_fields = 12

    # Molecule specific (10)
    molecule_fields = 10

    # GenBank specific (12)
    genbank_fields = 12

    # Annotation specific (10)
    annotation_fields = 10

    # Config specific (8)
    config_fields = 8

    # Experimental specific (8)
    experimental_fields = 8

    # General properties (6)
    general_fields = 6

    # Biotechnology analysis (12)
    analysis_fields = 12

    return detection_fields + fasta_fields + fastq_fields + alignment_fields + variant_fields + structure_fields + molecule_fields + genbank_fields + annotation_fields + config_fields + experimental_fields + general_fields + analysis_fields


# Integration point for metadata_engine.py
def extract_biotechnology_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for biotechnology metadata extraction."""
    return extract_biotechnology_metadata(filepath)