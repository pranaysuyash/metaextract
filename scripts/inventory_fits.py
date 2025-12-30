#!/usr/bin/env python3
"""FITS (Flexible Image Transport System) keyword inventory.

This script generates an inventory of FITS standard keywords and
extended headers used in astronomical imaging.

FITS is the standard data format used in astronomy and contains
keywords for:
- Header parameters (SIMPLE, BITPIX, NAXIS, etc.)
- World Coordinate System (WCS)
- Observation metadata
- Telescope/instrument parameters
- Calibration data
"""

import json
from pathlib import Path
from typing import Dict, List


# FITS standard keywords (from FITS 4.0 specification)
FITS_STANDARD_KEYWORDS = [
    # Mandatory keywords
    "SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "NAXIS3", "EXTEND",

    # Data structure
    "GROUPS", "PCOUNT", "GCOUNT", "EXTNAME", "EXTVER", "EXTLEVEL",
    "DATAMAX", "DATAMIN", "BSCALE", "BZERO", "BUNIT", "BLANK",

    # Observation metadata
    "OBJECT", "TELESCOP", "INSTRUME", "OBSERVER", "DATE-OBS", "DATE",
    "MJD-OBS", "MJD-OBS", "EXPTIME", "EXPOSURE", "FILTER", "OBSERVAT",
    "OBS-LAT", "OBS-LONG", "OBS-ELEV", "EQUINOX", "RADECSYS",

    # Time
    "TIME-OBS", "TIME-SEG", "MJD-OBS", "JD-OBS", "DJD-OBS", "LST-OBS",
    "HA-START", "HA-END", "UTC", "UTCTYPE", "UTCDATE", "TIMESYS",

    # Coordinate system
    "CTYPE1", "CTYPE2", "CTYPE3", "CRVAL1", "CRVAL2", "CRVAL3",
    "CRPIX1", "CRPIX2", "CRPIX3", "CDELT1", "CDELT2", "CDELT3",
    "CD1_1", "CD1_2", "CD1_3", "CD2_1", "CD2_2", "CD2_3",
    "CROTA1", "CROTA2", "CUNIT1", "CUNIT2", "CUNIT3",
    "LONPOLE", "LATPOLE", "RADESYS",

    # Image properties
    "IMAGETYP", "IMAGETYPE", "OBSMODE", "READMODE", "BINNING",
    "CCDSIZE", "CCDSUM", "GAIN", "RDNOISE", "SATURATE", "DARKCUR",
    "OFFSET", "OSCANMEAN", "OSCANMED",

    # Telescope
    "TELFOCUS", "TELPA", "TELALT", "TELAZ", "SECPIX", "SEEING",
    "FWHM", "AIRMASS", "ZENITH", "PARANGLE", "ELLIPTIC",

    # Weather
    "TEMPERAT", "PRESSURE", "HUMIDITY", "WINDDIR", "WINDSP",
    "DEWPOINT", "AMB_TEMP", "DEW_POINT", "AMB_HUMID",

    # Calibration
    "FLATFLD", "BIASFRAM", "DARKFRAM", "SKYFRAM", "CALTHUM",
    "FLAT-TYP", "FLAT-ID", "DOMEFLAT", "SKYFLAT", "TWILIGHT",

    # Mosaic
    "MOSAIC", "MOSAICID", "TILING", "TILES", "TILEID", "TILENAME",
    "OVERLAP", "OVERCOL", "OVERROW", "TOTCOLS", "TOTROWS",

    # Spectroscopy
    "SPECsys", "SPECREF", "WAT0_001", "WAT1_001", "WAT2_001",
    "DISPAXIS", "CGLOS", "CGSEP", "CGANG", "CTYPE1S", "CTYPE2S",
    "CDELT1S", "CDELT2S", "LTM1_1", "LTM2_2", "WCSNAME",
    "DETERIOR", "DETSIZE", "DETSEC", "DETECTOR", "CCDNAME",

    # History
    "HISTORY", "COMMENT", "ORIGIN", "CREATOR", "AUTHOR",
    "REFERENC", "DOCUMENT", "SOFTWARE", "USER", "PROJECT",
    "PROPOSAL", "PROPOSID", "PI-NAME", "PI-INST", "OBSERVER",

    # Quality
    "QUALITY", "QSTATUS", "QFLAGS", "QCOMMENT", "QCFLAGS",
    "BADPIXEL", "COSMICRAY", "SATURPIX", "NONLINE", "MAXCOUNT",

    # Multi-extension
    "XTENSION", "TFIELDS", "TTYPE1", "TTYPE2", "TTYPE3",
    "TFORM1", "TFORM2", "TFORM3", "TUCD1", "TUCD2", "TUCD3",
    "EXTEND", "NEXTEND", "BLOCKED", "SIMPLE",

    # HDU
    "CHECKSUM", "DATASUM", "COMPRESS", "ZIMAGE", "ZTENSION",
    "ZBITPIX", "ZNAXIS", "ZNAXIS1", "ZNAXIS2", "ZPCOUNT",
    "ZGCOUNT", "THEAP", "LHUFF", "LENCOD", "ZHUFF", "ZQUANTIZ",
]

# World Coordinate System (WCS) keywords
WCS_KEYWORDS = [
    "CTYPE1", "CTYPE2", "CTYPE3", "CTYPE4", "CTYPE5", "CTYPE6",
    "CUNIT1", "CUNIT2", "CUNIT3", "CUNIT4", "CUNIT5", "CUNIT6",
    "CDELT1", "CDELT2", "CDELT3", "CDELT4", "CDELT5", "CDELT6",
    "CD1_1", "CD1_2", "CD1_3", "CD1_4", "CD1_5", "CD1_6",
    "CD2_1", "CD2_2", "CD2_3", "CD2_4", "CD2_5", "CD2_6",
    "CD3_1", "CD3_2", "CD3_3", "CD3_4", "CD3_5", "CD3_6",
    "PC1_1", "PC1_2", "PC1_3", "PC1_4", "PC1_5", "PC1_6",
    "PC2_1", "PC2_2", "PC2_3", "PC2_4", "PC2_5", "PC2_6",
    "PC3_1", "PC3_2", "PC3_3", "PC3_4", "PC3_5", "PC3_6",
    "CRPIX1", "CRPIX2", "CRPIX3", "CRPIX4", "CRPIX5", "CRPIX6",
    "CRVAL1", "CRVAL2", "CRVAL3", "CRVAL4", "CRVAL5", "CRVAL6",
    "CROTA1", "CROTA2", "CROTA3", "CROTA4", "CROTA5", "CROTA6",
    "LONPOLE", "LATPOLE", "PV1_1", "PV1_2", "PV1_3", "PV1_4",
    "PV1_5", "PV1_6", "PV1_7", "PV1_8", "PV1_9", "PV1_10",
    "PV2_1", "PV2_2", "PV2_3", "PV2_4", "PV2_5", "PV2_6",
    "PV2_7", "PV2_8", "PV2_9", "PV2_10", "WAT0_001", "WAT1_001",
    "WAT2_001", "WAT3_001", "WAT4_001", "WAT5_001", "WAT6_001",
    "DCTY0_1", "DCTY1_1", "DCTY2_1", "DCTY3_1", "DCTY4_1", "DCTY5_1",
    "DCTY6_1", "DCF1_1", "DCF2_1", "DCF3_1", "DCF4_1", "DCF5_1",
    "DCF6_1", "DCH1_1", "DCH2_1", "DCH3_1", "DCH4_1", "DCH5_1",
    "DCH6_1", "DP1_1", "DP2_1", "DP3_1", "DP4_1", "DP5_1",
    "DP6_1", "AMDX1", "AMDX2", "AMDX3", "AMDX4", "AMDX5",
    "AMDX6", "AMDY1", "AMDY2", "AMDY3", "AMDY4", "AMDY5",
    "AMDY6", "AORDER", "AWIN", "APORDER", "APWIN",
    "DET1", "DET2", "DET3", "DET4", "DET5", "DET6",
    "EXT001", "EXT002", "EXT003", "EXT004", "EXT005", "EXT006",
    "WCSNAME", "WCSNAMEA", "WCSNAMEB", "WCSNAMEC", "WCSNAMED",
    "WCSNAMEP", "WCSNAMES", "RADESYS", "RADESYSA", "RADESYSB",
    "RADESYSC", "RADESYSD", "RADESYSP", "RADESYSS", "EPOCH",
    "EQUINOX", "CGLOS", "CGSEP", "CGANG", "CTYPE1S", "CTYPE2S",
    "CDELT1S", "CDELT2S", "LTM1_1", "LTM2_2", "LTV1", "LTV2",
    "LTM1_2", "LTM2_1", "MJD_OBS", "MJD_AVERAGE", "MJD_START",
    "MJD_STOP", "DATE-OBS", "DATE-AVG", "DATE-BEG", "DATE-END",
    "BJD-OBS", "BJD-AVG", "BJD-BEG", "BJD-END", "HJD-OBS",
    "HJD-AVG", "HJD-BEG", "HJD-END", "VELOCITY", "VELOSYS",
    "VELANGL", "STARTER", "OBSGEO-X", "OBSGEO-Y", "OBSGEO-Z",
    "GEOEXT", "GEOEXTX", "GEOEXTY", "GEOEXTZ", "SB1", "SB2",
    "SIGMA1", "SIGMA2", "NORMARC", "NORMARC1", "NORMARC2",
    "CUNITX", "CUNITY", "CUNITZ", "TCTY0", "TCTY1", "TCTY2",
    "TCUNI0", "TCUNI1", "TCUNI2", "TCRPX0", "TCRPX1", "TCRPX2",
    "TCRVL0", "TCRVL1", "TCRVL2", "TCDLT0", "TCDLT1", "TCDLT2",
    "TCF00", "TCF01", "TCF02", "TCF10", "TCF11", "TCF12",
    "TCF20", "TCF21", "TCF22",
]

# Telescope/instrument keywords
TELESCOPE_KEYWORDS = [
    "TELESCOP", "INSTRUME", "OBSERVER", "PROPOSER", "PI-NAME",
    "PI-INST", "TEL_ID", "TEL_CODE", "SITE_ID", "SITE_NAME",
    "SITE_LAT", "SITE_LON", "SITE_ELEV", "SITE_TIMEZ", "SITE_PHZ",
    "TEL_RA", "TEL_DEC", "TEL_AZ", "TEL_EL", "TEL_PA",
    "TEL_FOCU", "TEL_FOCR", "TEL_MIR", "TEL_SEC", "TEL_ROT",
    "INST_ID", "INST_NAME", "INST_MODE", "INST_PHZ", "INST_FOV",
    "DET_NAME", "DET_TYPE", "DET_DESC", "DET_MANU", "DET_MODEL",
    "DET_SN", "DET_PIXS", "DET_PIXA", "DET_ROT", "DET_DSU",
    "CCD_NAME", "CCD_MANU", "CCD_MODEL", "CCD_SN", "CCD_DATE",
    "CCD_TEMP", "CCD_COOL", "CCD_READ", "CCD_GAIN", "CCD_RON",
    "CCD_BIAS", "CCD_LINE", "CCD_SECT", "CCD_CLOCK", "CCD_SHIFT",
    "FILTER_ID", "FILTER_NAME", "FILTER_TY", "FILTER_SL", "FILTER_BW",
    "FILTER_THR", "FILTER_C1", "FILTER_C2", "FILTER_OFF",
    "FOCUS_POS", "FOCUS_ID", "FOCUS_CHG", "FOCUSER", "FOCUSER_ID",
    "MIRROR_ID", "MIRROR_DI", "MIRROR_CO", "MIRROR_AR", "MIRROR_MA",
    "DOME_ID", "DOME_STA", "DOME_AZ", "DOME_FAN", "DOME_TEM",
    "WEATHER", "WEATHER_", "AMBI_TMP", "AMBI_HUM", "AMBI_DEW",
    "AMBI_WND", "AMBI_BAR", "AMBI_RAIN", "AMBI_FOG", "AMBI_LGT",
    "SKY_BG", "SKY_TEMP", "SKY_HUM", "SKY_WND", "SKY_BAR",
    "SEEING", "SEEING_", "FWHM", "FWHM_GEO", "FWHM_ENC",
    "STREHL", "STREHL_", "WFS_MOD", "WFS_SEE", "WFS_POS",
    "AO_MODE", "AO_NAME", "AO_SN", "AO_CORR", "AO_DEL",
    "AO_BAND", "AO_LSTRT", "AO_LECRT", "AO_RES", "AO_FRQ",
    "HIERARCH ESO DET CHIP NAME",
    "HIERARCH ESO DET CHIP ID",
    "HIERARCH ESO DET CHIP NX",
    "HIERARCH ESO DET CHIP NY",
    "HIERARCH ESO DET PIXSIZE",
    "HIERARCH ESO DET READ SPEED",
    "HIERARCH ESO DET MODE",
    "HIERARCH ESO DET WinstonR",
    "HIERARCH ESO INS PATH",
    "HIERARCH ESO INS MODE",
    "HIERARCH ESO INS OPTI1 NAME",
    "HIERARCH ESO INS OPTI1 ID",
    "HIERARCH ESO INS OPTI2 NAME",
    "HIERARCH ESO INS OPTI2 ID",
    "HIERARCH ESO INS DIL NAME",
    "HIERARCH ESO INS DIL POS",
    "HIERARCH ESO TEL IA",
    "HIERARCH ESO TEL ALT",
    "HIERARCH ESO TEL AZ",
    "HIERARCH ESO TEL OPER",
    "HIERARCH ESO TEL TRAK",
    "HIERARCH ESO OBS PROG ID",
    "HIERARCH ESO OBS PI NAME",
    "HIERARCH ESO OBS PI INSTIT",
    "HIERARCH ESO OBS SCI OB ID",
    "HIERARCH ESO OBS TARG NAME",
    "HIERARCH ESO OBS TARG RA",
    "HIERARCH ESO OBS TARG DEC",
    "HIERARCH ESO OBS TARG EPOCH",
    "HIERARCH ESO OBS EQUINOX",
    "HIERARCH ESO OBS DATE",
    "HIERARCH ESO OBS UTC",
    "HIERARCH ESO OBS LST",
    "HIERARCH ESO AOT DELTAT",
    "HIERARCH ESO AOT TYPE",
    "HIERARCH ESO AOT DISPERSER",
    "HIERARCH ESO AOT GRATING",
    "HIERARCH ESO AOT WAVELENGTH",
    "HIERARCH ESO ATM TYPE",
    "HIERARCH ESO ATM TAU0",
    "HIERARCH ESO ATM SEEING",
    "HIERARCH ESO ATM WINDDIR",
    "HIERARCH ESO ATM WINDSPE",
    "HIERARCH ESO ATM HUMIDITY",
    "HIERARCH ESO ATM PRESSURE",
    "HIERARCH ESO ATM TEMP",
    "HIERARCH ESO AMBI TEMP",
    "HIERARCH ESO AMBI DEW",
    "HIERARCH ESO AMBI WINDSP",
    "HIERARCH ESO AMBI FWHM",
]

# Calibration keywords
CALIBRATION_KEYWORDS = [
    "FLAT_ID", "FLAT_TYPE", "FLAT_COM", "FLAT_DATE", "FLAT_TIME",
    "FLAT_EXP", "FLAT_FIL", "FLAT_LAM", "FLAT_BAND", "FLAT_SLIT",
    "FLAT_POS", "FLAT_OB", "FLAT_N", "FLAT_M", "FLAT_X",
    "BIAS_ID", "BIAS_TYPE", "BIAS_COM", "BIAS_DATE", "BIAS_TIME",
    "BIAS_N", "BIAS_EXP", "BIAS_GAIN", "BIAS_READ", "BIAS_TEMP",
    "DARK_ID", "DARK_TYPE", "DARK_COM", "DARK_DATE", "DARK_TIME",
    "DARK_EXP", "DARK_N", "DARK_TEMP", "DARK_GAIN", "DARK_READ",
    "ARC_ID", "ARC_TYPE", "ARC_COM", "ARC_DATE", "ARC_TIME",
    "ARC_EXP", "ARC_LAM", "ARC_GAS", "ARC_PRES", "ARC_TEMP",
    "STANDARD", "STD_RA", "STD_DEC", "STD_TYPE", "STD_MAG",
    "STD_FLUX", "STD_BAND", "STD_FILTER", "STD_GAIN", "STD_READ",
    "SKY_ID", "SKY_TYPE", "SKY_COM", "SKY_DATE", "SKY_TIME",
    "SKY_EXP", "SKY_FIL", "SKY_FWHM", "SKY_BG", "SKY_ELLIP",
    "DOMEFLAT", "DOMEFLAT_ID", "DOMEFLAT_TYPE", "DOMEFLAT_DATE",
    "TWILIGHT", "TWILIGHT_ID", "TWILIGHT_TYPE", "TWILIGHT_DATE",
    "FRINGE", "FRINGE_ID", "FRINGE_TYPE", "FRINGE_DATE", "FRINGE_N",
    "SUPERBIAS", "SUPERBIAS_ID", "SUPERBIAS_DATE", "SUPERBIAS_N",
    "MASK", "MASK_ID", "MASK_TYPE", "MASK_NAME", "MASK_DATE",
    "SHUTTER", "SHUTTER_ID", "SHUTTER_TYPE", "SHUTTER_DATE",
    "CAL-DB", "CAL-DB_ID", "CAL-DB_TYPE", "CAL-DB_DATE",
    "CAL-TH", "CAL-TH_ID", "CAL-TH_TYPE", "CAL-TH_DATE",
    "CAL-X", "CAL-X_ID", "CAL-X_TYPE", "CAL-X_DATE",
    "CAL-FL", "CAL-FL_ID", "CAL-FL_TYPE", "CAL-FL_DATE",
]

# Proposal/observation keywords
PROPOSAL_KEYWORDS = [
    "PROPOSAL", "PROP_ID", "PROP_PI", "PROP_COPI", "PROP_TITLE",
    "PROP_ABST", "PROP_KEYW", "PROP_TYPE", "PROP_CATG", "PROP_MODE",
    "OBS_ID", "OBS_PI", "OBS_PROG", "OBS_GRP", "OBS_TYPE",
    "OBS_MODE", "OBS_DATE", "OBS_TIME", "OBS_DUR", "OBS_EXPO",
    "OBS_OB", "OBS_OB_ID", "OBS_OB_PR", "OBS_OB_CO", "OBS_OB_N",
    "OBS_ACQ", "OBS_ACQ_ID", "OBS_ACQ_TY", "OBS_ACQ_RA", "OBS_ACQ_DEC",
    "OBS_TARG", "OBS_TARG_ID", "OBS_TARG_NA", "OBS_TARG_RA", "OBS_TARG_DEC",
    "OBS_TARG_EPOCH", "OBS_TARG_PAR", "OBS_TARG_PLX", "OBS_TARG_RV",
    "OBS_TARG_BMAG", "OBS_TARG_VMAG", "OBS_TARG_RMAG", "OBS_TARG_IMAG",
    "OBS_TARG_B-V", "OBS_TARG_SPECT", "OBS_TARG_SA", "OBS_TARG_CN",
    "SCHED", "SCHED_ID", "SCHED_DATE", "SCHED_TIME", "SCHED_DUR",
    "SCHED_SLT", "SCHED_PRS", "SCHED_AIR", "SCHED_MOON",
    "GUIDE", "GUIDE_ID", "GUIDE_STA", "GUIDE_RA", "GUIDE_DEC",
    "GUIDE_OFF", "GUIDE_ERR", "GUIDE_FWHM", "GUIDE_EXC",
]

# Generate complete inventory
def generate_inventory(output_dir: Path) -> None:
    """Generate FITS keyword inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": "",
        "source": "FITS 4.0 Specification + Common Extensions",
        "categories": {},
    }

    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Standard keywords
    inventory["categories"]["Standard_Keywords"] = {
        "description": "FITS standard keywords (mandatory and optional)",
        "keywords": sorted(FITS_STANDARD_KEYWORDS),
        "count": len(FITS_STANDARD_KEYWORDS),
    }

    # WCS keywords
    inventory["categories"]["WCS_Keywords"] = {
        "description": "World Coordinate System keywords",
        "keywords": sorted(WCS_KEYWORDS),
        "count": len(WCS_KEYWORDS),
    }

    # Telescope keywords
    inventory["categories"]["Telescope_Keywords"] = {
        "description": "Telescope and instrument keywords",
        "keywords": sorted(TELESCOPE_KEYWORDS),
        "count": len(TELESCOPE_KEYWORDS),
    }

    # Calibration keywords
    inventory["categories"]["Calibration_Keywords"] = {
        "description": "Calibration frame keywords",
        "keywords": sorted(CALIBRATION_KEYWORDS),
        "count": len(CALIBRATION_KEYWORDS),
    }

    # Proposal keywords
    inventory["categories"]["Proposal_Keywords"] = {
        "description": "Proposal and observation keywords",
        "keywords": sorted(PROPOSAL_KEYWORDS),
        "count": len(PROPOSAL_KEYWORDS),
    }

    # Calculate totals
    total_keywords = (
        len(FITS_STANDARD_KEYWORDS) +
        len(WCS_KEYWORDS) +
        len(TELESCOPE_KEYWORDS) +
        len(CALIBRATION_KEYWORDS) +
        len(PROPOSAL_KEYWORDS)
    )

    # Get unique keywords
    all_keywords = set(FITS_STANDARD_KEYWORDS + WCS_KEYWORDS + TELESCOPE_KEYWORDS + CALIBRATION_KEYWORDS + PROPOSAL_KEYWORDS)
    unique_keywords = len(all_keywords)

    inventory["totals"] = {
        "total_keywords": total_keywords,
        "unique_keywords": unique_keywords,
        "categories": len(inventory["categories"]),
    }

    # Write JSON
    output_path = output_dir / "fits_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print("FITS KEYWORD INVENTORY SUMMARY")
    print("=" * 60)
    print()
    print(f"Total keywords: {total_keywords:,}")
    print(f"Unique keywords: {unique_keywords:,}")
    print(f"Categories: {len(inventory['categories'])}")
    print()

    for cat_name, cat_data in inventory["categories"].items():
        print(f"  {cat_name}: {cat_data['count']:,} keywords")

    print()
    print("=" * 60)
    print("TOTAL FITS KEYWORDS: {:,}".format(total_keywords))
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate FITS keyword inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/fits_inventory"),
        help="Output directory (default: dist/fits_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
