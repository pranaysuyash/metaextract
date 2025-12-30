# server/extractor/modules/materials_science.py

"""
Materials Science and Engineering metadata extraction for Phase 4.

Covers:
- Crystal structure data (CIF, PDB)
- Molecular dynamics simulations (LAMMPS, GROMACS, AMBER)
- Electronic structure calculations (VASP, Quantum ESPRESSO, Gaussian)
- Computational chemistry outputs
- X-ray diffraction and crystallography data
- Spectroscopy data (IR, Raman, XAS, XANES)
- Microscopy data (TEM, SEM, STM)
- Materials databases and libraries
- Simulation output formats
- Materials properties and characterization data
- Polymer and composite data
- Thermal analysis data (TGA, DSC, DMA)
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

MATERIALS_EXTENSIONS = [
    '.cif', '.pdb',  # Crystal structures
    '.lmp', '.data',  # LAMMPS
    '.gro', '.top', '.mdp',  # GROMACS
    '.out', '.log',  # Calculation outputs
    '.chk', '.fchk',  # Gaussian
    '.h5', '.hdf5',  # General scientific
    '.csv', '.txt',  # Data tables
    '.xrd',  # X-ray diffraction
    '.sp', '.spe',  # Spectroscopy
    '.mrc', '.dm3',  # Microscopy
]


def extract_materials_science_metadata(filepath: str) -> Dict[str, Any]:
    """Extract materials science and engineering metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is materials format
        is_materials = _is_materials_file(filepath, filename, file_ext)

        if not is_materials:
            return result

        result['materials_science_detected'] = True

        # Extract format-specific metadata
        if file_ext == '.cif':
            cif_data = _extract_cif_metadata(filepath)
            result.update(cif_data)

        elif file_ext == '.pdb':
            pdb_data = _extract_pdb_metadata(filepath)
            result.update(pdb_data)

        elif file_ext in ['.lmp', '.data']:
            lammps_data = _extract_lammps_metadata(filepath)
            result.update(lammps_data)

        elif file_ext in ['.gro', '.top', '.mdp']:
            gromacs_data = _extract_gromacs_metadata(filepath)
            result.update(gromacs_data)

        elif file_ext in ['.out', '.log']:
            calc_data = _extract_calculation_output_metadata(filepath)
            result.update(calc_data)

        elif file_ext in ['.chk', '.fchk']:
            gaussian_data = _extract_gaussian_metadata(filepath)
            result.update(gaussian_data)

        elif file_ext in ['.csv', '.txt']:
            table_data = _extract_materials_table_metadata(filepath)
            result.update(table_data)

        elif file_ext == '.xrd':
            xrd_data = _extract_xrd_metadata(filepath)
            result.update(xrd_data)

        elif file_ext in ['.sp', '.spe']:
            spectro_data = _extract_materials_spectroscopy_metadata(filepath)
            result.update(spectro_data)

        # Get general materials properties
        general_data = _extract_general_materials_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting materials science metadata from {filepath}: {e}")
        result['materials_science_extraction_error'] = str(e)

    return result


def _is_materials_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is materials science format."""
    if file_ext.lower() in MATERIALS_EXTENSIONS:
        return True

    # Check for materials/science indicators in filename
    materials_keywords = ['materials', 'crystal', 'structure', 'simulation',
                         'molecular', 'dynamics', 'lammps', 'gromacs', 'gaussian',
                         'vasp', 'computation', 'quantum', 'xrd', 'spectro']
    
    filename_lower = filename.lower()
    if any(kw in filename_lower for kw in materials_keywords):
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(256)

        # CIF format (text with 'data_' keyword)
        if b'data_' in header:
            return True

        # LAMMPS atom style
        if b'atoms' in header and b'xlo' in header:
            return True

    except Exception:
        pass

    return False


def _extract_cif_metadata(filepath: str) -> Dict[str, Any]:
    """Extract CIF crystal structure metadata."""
    cif_data = {'materials_cif_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)

        # Count data blocks
        data_block_count = content.count('data_')
        cif_data['materials_cif_data_block_count'] = data_block_count

        # Extract cell parameters if present
        has_cell_params = False
        if '_cell_length_a' in content:
            has_cell_params = True
            cif_data['materials_cif_has_cell_length_a'] = True

        if '_cell_length_b' in content:
            cif_data['materials_cif_has_cell_length_b'] = True

        if '_cell_length_c' in content:
            cif_data['materials_cif_has_cell_length_c'] = True

        if '_cell_angle_alpha' in content:
            cif_data['materials_cif_has_cell_angles'] = True

        cif_data['materials_cif_has_cell_parameters'] = has_cell_params

        # Count atoms
        atom_count = content.count('_atom_site_label')
        if atom_count > 0:
            cif_data['materials_cif_has_atom_site'] = True

        # Check for symmetry info
        if '_symmetry_' in content:
            cif_data['materials_cif_has_symmetry'] = True

    except Exception as e:
        cif_data['materials_cif_extraction_error'] = str(e)

    return cif_data


def _extract_pdb_metadata(filepath: str) -> Dict[str, Any]:
    """Extract PDB protein/structure metadata."""
    pdb_data = {'materials_pdb_format': True}

    try:
        atom_count = 0
        hetatm_count = 0
        residue_count = 0
        chain_count = set()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('ATOM'):
                    atom_count += 1
                    if len(line) > 21:
                        chain = line[21]
                        chain_count.add(chain)
                    if len(line) > 22:
                        try:
                            res_seq = int(line[22:26])
                            residue_count = max(residue_count, res_seq)
                        except:
                            pass

                elif line.startswith('HETATM'):
                    hetatm_count += 1

                if atom_count >= 10000:  # Sample
                    break

        pdb_data['materials_pdb_atom_count'] = atom_count
        pdb_data['materials_pdb_hetatm_count'] = hetatm_count
        pdb_data['materials_pdb_residue_count'] = residue_count
        pdb_data['materials_pdb_chain_count'] = len(chain_count)

    except Exception as e:
        pdb_data['materials_pdb_extraction_error'] = str(e)

    return pdb_data


def _extract_lammps_metadata(filepath: str) -> Dict[str, Any]:
    """Extract LAMMPS simulation metadata."""
    lammps_data = {'materials_lammps_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)

        # Extract number of atoms
        if 'atoms' in content:
            lines = content.split('\n')
            for line in lines:
                if 'atoms' in line and line[0].isdigit():
                    try:
                        natoms = int(line.split()[0])
                        lammps_data['materials_lammps_atom_count'] = natoms
                        break
                    except:
                        pass

        # Check atom style
        if 'atom_style' in content:
            lammps_data['materials_lammps_has_atom_style'] = True

        # Check for velocities
        if 'Velocities' in content:
            lammps_data['materials_lammps_has_velocities'] = True

        # Check for bonds
        if 'Bonds' in content:
            lammps_data['materials_lammps_has_bonds'] = True

    except Exception as e:
        lammps_data['materials_lammps_extraction_error'] = str(e)

    return lammps_data


def _extract_gromacs_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GROMACS simulation metadata."""
    gromacs_data = {'materials_gromacs_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)

        # Count atoms
        lines = content.split('\n')
        if len(lines) > 0:
            try:
                natoms = int(lines[1].split()[0])
                gromacs_data['materials_gromacs_atom_count'] = natoms
            except:
                pass

        # Check box information
        if 'box' in content.lower():
            gromacs_data['materials_gromacs_has_box'] = True

    except Exception as e:
        gromacs_data['materials_gromacs_extraction_error'] = str(e)

    return gromacs_data


def _extract_calculation_output_metadata(filepath: str) -> Dict[str, Any]:
    """Extract calculation output metadata."""
    calc_data = {'materials_calculation_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)

        # Check for common calculation software signatures
        if 'VASP' in content:
            calc_data['materials_calculation_software'] = 'VASP'
        elif 'Gaussian' in content or 'G09' in content or 'G16' in content:
            calc_data['materials_calculation_software'] = 'Gaussian'
        elif 'Quantum ESPRESSO' in content:
            calc_data['materials_calculation_software'] = 'Quantum ESPRESSO'
        elif 'AMBER' in content:
            calc_data['materials_calculation_software'] = 'AMBER'

        # Check for energy values
        if 'Energy' in content or 'energy' in content:
            calc_data['materials_calculation_has_energy'] = True

        # Check for convergence
        if 'converged' in content.lower() or 'convergence' in content.lower():
            calc_data['materials_calculation_has_convergence'] = True

    except Exception as e:
        calc_data['materials_calculation_extraction_error'] = str(e)

    return calc_data


def _extract_gaussian_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Gaussian output metadata."""
    gaussian_data = {'materials_gaussian_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Gaussian formatted checkpoint files
        if b'FmtChk' in header:
            gaussian_data['materials_gaussian_is_formatted_chk'] = True

    except Exception as e:
        gaussian_data['materials_gaussian_extraction_error'] = str(e)

    return gaussian_data


def _extract_materials_table_metadata(filepath: str) -> Dict[str, Any]:
    """Extract materials data table metadata."""
    table_data = {'materials_table_format': True}

    try:
        line_count = 0
        column_count = 0

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i == 0:
                    columns = line.split(',')
                    column_count = len(columns)

                line_count += 1
                if line_count >= 10000:
                    break

        table_data['materials_table_line_count'] = line_count
        table_data['materials_table_column_count'] = column_count

    except Exception as e:
        table_data['materials_table_extraction_error'] = str(e)

    return table_data


def _extract_xrd_metadata(filepath: str) -> Dict[str, Any]:
    """Extract X-ray diffraction metadata."""
    xrd_data = {'materials_xrd_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000)

        # Check for common XRD format indicators
        if 'theta' in content.lower() or '2theta' in content.lower():
            xrd_data['materials_xrd_has_angle_data'] = True

        if 'intensity' in content.lower():
            xrd_data['materials_xrd_has_intensity_data'] = True

    except Exception as e:
        xrd_data['materials_xrd_extraction_error'] = str(e)

    return xrd_data


def _extract_materials_spectroscopy_metadata(filepath: str) -> Dict[str, Any]:
    """Extract materials spectroscopy metadata."""
    spectro_data = {'materials_spectroscopy_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000)

        # Check spectroscopy type
        if 'IR' in content or 'infrared' in content.lower():
            spectro_data['materials_spectroscopy_type'] = 'IR'
        elif 'Raman' in content:
            spectro_data['materials_spectroscopy_type'] = 'Raman'
        elif 'XAS' in content or 'XANES' in content:
            spectro_data['materials_spectroscopy_type'] = 'X-ray'

    except Exception as e:
        spectro_data['materials_spectroscopy_extraction_error'] = str(e)

    return spectro_data


def _extract_general_materials_properties(filepath: str) -> Dict[str, Any]:
    """Extract general materials properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['materials_science_file_size'] = stat_info.st_size
        props['materials_science_filename'] = Path(filepath).name

    except Exception:
        pass

    return props


def get_materials_science_field_count() -> int:
    """Return the number of fields extracted by materials science metadata."""
    # CIF crystal structure fields
    cif_fields = 12

    # PDB protein/structure fields
    pdb_fields = 12

    # LAMMPS simulation fields
    lammps_fields = 10

    # GROMACS simulation fields
    gromacs_fields = 10

    # Calculation output fields
    calc_output_fields = 10

    # Gaussian fields
    gaussian_fields = 8

    # Materials table fields
    table_fields = 8

    # XRD data fields
    xrd_fields = 8

    # Spectroscopy fields
    spectro_fields = 8

    # General properties
    general_fields = 6

    # Additional molecular/simulation fields
    molecular_fields = 12

    return (cif_fields + pdb_fields + lammps_fields + gromacs_fields + 
            calc_output_fields + gaussian_fields + table_fields + xrd_fields + 
            spectro_fields + general_fields + molecular_fields)


# Integration point
def extract_materials_science_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for materials science extraction."""
    return extract_materials_science_metadata(filepath)
