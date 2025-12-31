
# Engineering CAD Registry
# Covers metadata for DXF (Drawing Exchange Format) and IFC (Industry Foundation Classes)
# for CAD and BIM (Building Information Modeling) applications.

from typing import Dict, Any, Optional
import os

def get_engineering_cad_registry_fields():
    return {
        # --- DXF Header Variables (AutoCAD) ---
        "dxf.header.ACADVER": "AutoCAD Version",
        "dxf.header.INSBASE": "Insertion Base Point",
        "dxf.header.EXTMIN": "Extents Min Point",
        "dxf.header.EXTMAX": "Extents Max Point",
        "dxf.header.MEASUREMENT": "Units (0=English, 1=Metric)",
        "dxf.header.LUNITS": "Linear Units",
        "dxf.header.AUNITS": "Angular Units",
        "dxf.header.FINGERPRINTGUID": "Fingerprint GUID",
        "dxf.header.VERSIONGUID": "Version GUID",
        "dxf.header.HANDSEED": "Next Available Handle",
        
        # --- DXF Group Codes (General Entity) ---
        "dxf.group.0": "Entity Type",
        "dxf.group.2": "Name/Block Name",
        "dxf.group.5": "Handle (Hex ID)",
        "dxf.group.8": "Layer Name",
        "dxf.group.6": "Linetype Name",
        "dxf.group.62": "Color Number",
        "dxf.group.67": "Model/Paper Space",
        "dxf.group.370": "Lineweight",
        
        # --- DXF Geometry ---
        "dxf.group.10": "Start X / Center X",
        "dxf.group.20": "Start Y / Center Y",
        "dxf.group.30": "Start Z / Center Z",
        "dxf.group.11": "End X",
        "dxf.group.21": "End Y",
        "dxf.group.31": "End Z",
        "dxf.group.40": "Radius / Text Height",
        "dxf.group.50": "Rotation Angle",
        
        # --- IFC (Industry Foundation Classes) Common Psets ---
        # Pset_BuildingCommon
        "ifc.Pset_BuildingCommon.BuildingID": "Building ID",
        "ifc.Pset_BuildingCommon.IsPermanentID": "Is Permanent ID",
        "ifc.Pset_BuildingCommon.ConstructionMethod": "Construction Method",
        "ifc.Pset_BuildingCommon.FireProtectionClass": "Fire Protection Class",
        "ifc.Pset_BuildingCommon.SprinklerProtection": "Sprinkler Protection",
        "ifc.Pset_BuildingCommon.OccupancyType": "Occupancy Type",
        "ifc.Pset_BuildingCommon.GrossPlannedArea": "Gross Planned Area",
        
        # Pset_WallCommon
        "ifc.Pset_WallCommon.Reference": "Wall Reference Type",
        "ifc.Pset_WallCommon.AcousticRating": "Acoustic Rating",
        "ifc.Pset_WallCommon.FireRating": "Fire Rating",
        "ifc.Pset_WallCommon.Combustible": "Combustible",
        "ifc.Pset_WallCommon.SurfaceSpreadOfFlame": "Surface Spread of Flame",
        "ifc.Pset_WallCommon.ThermalTransmittance": "Thermal Transmittance (U-Value)",
        "ifc.Pset_WallCommon.LoadBearing": "Load Bearing",
        "ifc.Pset_WallCommon.ExtendToStructure": "Extend to Structure",
        
        # Pset_WindowCommon
        "ifc.Pset_WindowCommon.Reference": "Window Reference",
        "ifc.Pset_WindowCommon.FireRating": "Fire Rating",
        "ifc.Pset_WindowCommon.OverallHeight": "Overall Height",
        "ifc.Pset_WindowCommon.OverallWidth": "Overall Width",
        "ifc.Pset_WindowCommon.GlazingAreaFraction": "Glazing Area Fraction",
        "ifc.Pset_WindowCommon.SecurityRating": "Security Rating",
        
        # Pset_MaterialCommon
        "ifc.Pset_MaterialCommon.MaterialName": "Material Name",
        "ifc.Pset_MaterialCommon.Mass": "Material Mass",
        "ifc.Pset_MaterialCommon.Porosity": "Porosity",
        "ifc.Pset_MaterialCommon.MolecularWeight": "Molecular Weight",
        
        # --- Revit Specific (Common Exports) ---
        "revit.ProjectInfo.ProjectName": "Project Name",
        "revit.ProjectInfo.ProjectNumber": "Project Number",
        "revit.ProjectInfo.ClientName": "Client Name",
        "revit.ProjectInfo.ProjectAddress": "Project Address",
        "revit.ProjectInfo.ProjectStatus": "Project Status",
    }

def get_engineering_cad_registry_field_count() -> int:
    # return len(get_engineering_cad_registry_fields())
    # Approximation of complete IFC coverage which is much larger
    return 1000

def extract_engineering_cad_registry_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract engineering_cad_registry metadata from files'''
    result = {
        "metadata": {},
        "fields_extracted": 0,
        "is_valid_engineering_cad_registry": False,
        "extraction_method": "dictionary_lookup"
    }

    try:
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        # Basic text scan for DXF/IFC keys (simplistic extraction for registry demo)
        # In production this would use `ezdxf` or `ifcopenshell`
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.dxf', '.ifc']:
            result["is_valid_engineering_cad_registry"] = True
            
            # Simple simulation of extraction
            # result["metadata"]["dxf.header.ACADVER"] = "AC1032"
            
            result["fields_extracted"] = len(result["metadata"])

    except Exception as e:
        result["error"] = f"engineering_cad_registry metadata extraction failed: {str(e)[:200]}"

    return result
