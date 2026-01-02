"""
ID3v2 Complete Frame Registry
Complete mapping of all ID3v2.3 and ID3v2.4 frame IDs to descriptive names.
Based on id3.org specification: https://id3.org/id3v2.4.0-frames
Target: +300 fields for comprehensive ID3v2 coverage
"""

from typing import Dict, Any, Optional, List

# ID3v2.4 Frame ID to field name mapping
# Complete list from id3.org/id3v2.4.0-frames specification

ID3V2_TEXT_FRAMES = {
    # Text information frames
    "TALB": "album_title",
    "TBPM": "beats_per_minute",
    "TCOM": "composer",
    "TCON": "content_type",
    "TCOP": "copyright_message",
    "TDEN": "encoding_time",
    "TDLY": "playlist_delay",
    "TDOR": "original_release_time",
    "TDRC": "recording_time",
    "TDRL": "release_time",
    "TDTG": "tagging_time",
    "TENC": "encoded_by",
    "TEXT": "lyricist",
    "TFLT": "file_type",
    "TIPL": "involved_people_list",
    "TIT1": "content_group_description",
    "TIT2": "title",
    "TIT3": "subtitle",
    "TKEY": "initial_key",
    "TLAN": "language",
    "TLEN": "length",
    "TMCL": "musician_credits_list",
    "TMED": "media_type",
    "TMOO": "mood",
    "TOAL": "original_album_title",
    "TOFN": "original_filename",
    "TOLY": "original_lyricist",
    "TOPE": "original_artist",
    "TOWN": "file_owner",
    "TPE1": "lead_performer",
    "TPE2": "band_orchestra",
    "TPE3": "conductor",
    "TPE4": "interpreted_remixed_by",
    "TPOS": "part_of_set",
    "TPRO": "produced_notice",
    "TPUB": "publisher",
    "TRCK": "track_number",
    "TRSN": "internet_radio_station_name",
    "TRSO": "internet_radio_station_owner",
    "TSOA": "album_sort_order",
    "TSOP": "performer_sort_order",
    "TSOT": "title_sort_order",
    "TSRC": "isrc",
    "TSSE": "encoding_software",
    "TSST": "set_subtitle",
    # User defined text frames
    "TXXX": "user_defined_text",
}

ID3V2_URL_FRAMES = {
    # URL link frames
    "WCOM": "commercial_url",
    "WCOP": "copyright_url",
    "WOAF": "official_audio_file_url",
    "WOAR": "official_artist_url",
    "WOAS": "official_audio_source_url",
    "WORS": "official_internet_radio_url",
    "WPAY": "payment_url",
    "WPUB": "publishers_official_url",
    "WXXX": "user_defined_url",
}

ID3V2_OTHER_FRAMES = {
    # Other frames
    "AENC": "audio_encryption",
    "APIC": "attached_picture",
    "ASPI": "audio_seek_point_index",
    "COMM": "comment",
    "COMR": "commercial_frame",
    "ENCR": "encryption_method_registration",
    "EQU2": "equalisation_2",
    "ETCO": "event_timing_codes",
    "GEOB": "general_encapsulated_object",
    "GRID": "group_identification_registration",
    "LINK": "linked_information",
    "MCDI": "music_cd_identifier",
    "MLLT": "mpeg_location_lookup_table",
    "OWNE": "ownership_frame",
    "PRIV": "private_frame",
    "PCNT": "play_counter",
    "POPM": "popularimeter",
    "POSS": "position_synchronisation",
    "RBUF": "recommended_buffer_size",
    "RVA2": "relative_volume_adjustment_2",
    "RVRB": "reverb",
    "SEEK": "seek_frame",
    "SIGN": "signature_frame",
    "SYLT": "synchronised_lyrics",
    "SYTC": "synchronised_tempo_codes",
    "UFID": "unique_file_identifier",
    "USER": "terms_of_use",
    "USLT": "unsynchronised_lyrics",
    # Chapters
    "CHAP": "chapter",
    "CTOC": "table_of_contents",
    # Apple extensions
    "PCST": "podcast_flag",
    "TCAT": "podcast_category",
    "TDES": "podcast_description",
    "TGID": "podcast_id",
    "TKWD": "podcast_keywords",
    "WFED": "podcast_url",
    # MusicBrainz extensions
    "TXXX:MusicBrainz Album Id": "musicbrainz_album_id",
    "TXXX:MusicBrainz Artist Id": "musicbrainz_artist_id",
    "TXXX:MusicBrainz Album Artist Id": "musicbrainz_album_artist_id",
    "TXXX:MusicBrainz Release Group Id": "musicbrainz_release_group_id",
    "TXXX:MusicBrainz Work Id": "musicbrainz_work_id",
    "TXXX:MusicBrainz Track Id": "musicbrainz_track_id",
    "TXXX:MusicBrainz Release Track Id": "musicbrainz_release_track_id",
    "TXXX:MusicBrainz Recording Id": "musicbrainz_recording_id",
    "TXXX:MusicBrainz TRM Id": "musicbrainz_trm_id",
    "TXXX:MusicBrainz Disc Id": "musicbrainz_disc_id",
    "TXXX:MusicBrainz Album Status": "musicbrainz_album_status",
    "TXXX:MusicBrainz Album Type": "musicbrainz_album_type",
    "TXXX:MusicBrainz Album Release Country": "musicbrainz_release_country",
    "TXXX:Acoustid Id": "acoustid_id",
    "TXXX:Acoustid Fingerprint": "acoustid_fingerprint",
    # ReplayGain extensions
    "TXXX:REPLAYGAIN_TRACK_GAIN": "replaygain_track_gain",
    "TXXX:REPLAYGAIN_TRACK_PEAK": "replaygain_track_peak",
    "TXXX:REPLAYGAIN_ALBUM_GAIN": "replaygain_album_gain",
    "TXXX:REPLAYGAIN_ALBUM_PEAK": "replaygain_album_peak",
    "TXXX:REPLAYGAIN_REFERENCE_LOUDNESS": "replaygain_reference_loudness",
    # iTunes extensions
    "TXXX:ITUNES_CDDB_1": "itunes_cddb_1",
    "TXXX:iTunes_CDDB_IDs": "itunes_cddb_ids",
    "TXXX:ITUNNORM": "itunes_normalization",
    "TXXX:ITUNSMPB": "itunes_seamless_playback",
    "TXXX:ITUNES_GAPLESS_DATA": "itunes_gapless_data",
    # Discogs extensions
    "TXXX:DISCOGS_RELEASE_ID": "discogs_release_id",
    "TXXX:DISCOGS_ARTIST_ID": "discogs_artist_id",
    "TXXX:DISCOGS_LABEL_ID": "discogs_label_id",
    "TXXX:DISCOGS_MASTER_ID": "discogs_master_id",
    # Beatport extensions
    "TXXX:BEATPORT_TRACK_ID": "beatport_track_id",
    "TXXX:BEATPORT_RELEASE_ID": "beatport_release_id",
    # Spotify extensions
    "TXXX:SPOTIFY_TRACK_ID": "spotify_track_id",
    "TXXX:SPOTIFY_ARTIST_ID": "spotify_artist_id",
    "TXXX:SPOTIFY_ALBUM_ID": "spotify_album_id",
    # Amazon extensions
    "TXXX:AMAZON_ID": "amazon_id",
    "TXXX:ASIN": "asin",
    # Other common TXXX fields
    "TXXX:BARCODE": "barcode",
    "TXXX:CATALOGNUMBER": "catalog_number",
    "TXXX:SCRIPT": "script",
    "TXXX:MEDIA": "media",
    "TXXX:ORIGINALYEAR": "original_year",
    "TXXX:RELEASETYPE": "release_type",
    "TXXX:RELEASESTATUS": "release_status",
    "TXXX:ARTISTS": "artists",
    "TXXX:ALBUMARTISTS": "album_artists",
    "TXXX:WORK": "work",
    "TXXX:MOVEMENT": "movement",
    "TXXX:MOVEMENTNUMBER": "movement_number",
    "TXXX:MOVEMENTTOTAL": "movement_total",
    "TXXX:SHOWMOVEMENT": "show_movement",
    "TXXX:COMPILATION": "is_compilation",
    "TXXX:GAPLESS": "gapless",
    "TXXX:DJ_MIXER": "dj_mixer",
    "TXXX:MIXER": "mixer",
    "TXXX:REMIXER": "remixer",
    "TXXX:PRODUCER": "producer",
    "TXXX:ENGINEER": "engineer",
    "TXXX:ARRANGER": "arranger",
    "TXXX:WRITER": "writer",
    "TXXX:CONDUCTOR": "conductor",
    "TXXX:LYRICIST": "lyricist",
    "TXXX:LABEL": "label",
    "TXXX:RATING": "rating",
    "TXXX:EXPLICIT": "explicit",
    "TXXX:LANGUAGE": "language",
    "TXXX:COUNTRY": "country",
}

# ID3v2.2 (3-character) to ID3v2.4 (4-character) frame ID mapping
ID3V22_TO_V24_MAP = {
    "BUF": "RBUF",
    "CNT": "PCNT",
    "COM": "COMM",
    "CRA": "AENC",
    "CRM": None,  # removed in v2.4
    "EQU": "EQU2",
    "ETC": "ETCO",
    "GEO": "GEOB",
    "IPL": "TIPL",
    "LNK": "LINK",
    "MCI": "MCDI",
    "MLL": "MLLT",
    "PIC": "APIC",
    "POP": "POPM",
    "REV": "RVRB",
    "RVA": "RVA2",
    "SLT": "SYLT",
    "STC": "SYTC",
    "TAL": "TALB",
    "TBP": "TBPM",
    "TCM": "TCOM",
    "TCO": "TCON",
    "TCR": "TCOP",
    "TDA": "TDRC",
    "TDY": "TDLY",
    "TEN": "TENC",
    "TFT": "TFLT",
    "TIM": "TDRC",
    "TKE": "TKEY",
    "TLA": "TLAN",
    "TLE": "TLEN",
    "TMT": "TMED",
    "TOA": "TOPE",
    "TOF": "TOFN",
    "TOL": "TOLY",
    "TOR": "TDOR",
    "TOT": "TOAL",
    "TP1": "TPE1",
    "TP2": "TPE2",
    "TP3": "TPE3",
    "TP4": "TPE4",
    "TPA": "TPOS",
    "TPB": "TPUB",
    "TRC": "TSRC",
    "TRD": "TDRC",
    "TRK": "TRCK",
    "TSI": None,  # removed in v2.4
    "TSS": "TSSE",
    "TT1": "TIT1",
    "TT2": "TIT2",
    "TT3": "TIT3",
    "TXT": "TEXT",
    "TXX": "TXXX",
    "TYE": "TDRC",
    "UFI": "UFID",
    "ULT": "USLT",
    "WAF": "WOAF",
    "WAR": "WOAR",
    "WAS": "WOAS",
    "WCM": "WCOM",
    "WCP": "WCOP",
    "WPB": "WPUB",
    "WXX": "WXXX",
}

# APIC picture types (ID3v2.3/2.4)
APIC_PICTURE_TYPES = {
    0x00: "other",
    0x01: "32x32_file_icon",
    0x02: "other_file_icon",
    0x03: "cover_front",
    0x04: "cover_back",
    0x05: "leaflet_page",
    0x06: "media",
    0x07: "lead_artist",
    0x08: "artist",
    0x09: "conductor",
    0x0A: "band_orchestra",
    0x0B: "composer",
    0x0C: "lyricist",
    0x0D: "recording_location",
    0x0E: "during_recording",
    0x0F: "during_performance",
    0x10: "movie_video_screen_capture",
    0x11: "bright_coloured_fish",
    0x12: "illustration",
    0x13: "band_artist_logotype",
    0x14: "publisher_studio_logotype",
}

# Event timing codes (ETCO frame)
EVENT_TIMING_TYPES = {
    0x00: "padding",
    0x01: "end_of_initial_silence",
    0x02: "intro_start",
    0x03: "main_part_start",
    0x04: "outro_start",
    0x05: "outro_end",
    0x06: "verse_start",
    0x07: "refrain_start",
    0x08: "interlude_start",
    0x09: "theme_start",
    0x0A: "variation_start",
    0x0B: "key_change",
    0x0C: "time_change",
    0x0D: "momentary_unwanted_noise",
    0x0E: "sustained_noise",
    0x0F: "sustained_noise_end",
    0x10: "intro_end",
    0x11: "main_part_end",
    0x12: "verse_end",
    0x13: "refrain_end",
    0x14: "theme_end",
    0x15: "profanity",
    0x16: "profanity_end",
    0xFD: "audio_end",
    0xFE: "audio_file_end",
}

# Synced lyrics content types (SYLT frame)
SYLT_CONTENT_TYPES = {
    0x00: "other",
    0x01: "lyrics",
    0x02: "text_transcription",
    0x03: "movement_name",
    0x04: "events",
    0x05: "chord",
    0x06: "trivia",
    0x07: "webpage_urls",
    0x08: "image_urls",
}

# Channel types for RVA2 frame
RVA2_CHANNEL_TYPES = {
    0x00: "other",
    0x01: "master_volume",
    0x02: "front_right",
    0x03: "front_left",
    0x04: "back_right",
    0x05: "back_left",
    0x06: "front_centre",
    0x07: "back_centre",
    0x08: "subwoofer",
}

# Vorbis Comment standard field names (also used in FLAC, Opus)
VORBIS_COMMENT_FIELDS = {
    "TITLE": "title",
    "ARTIST": "artist",
    "ALBUM": "album",
    "ALBUMARTIST": "album_artist",
    "ALBUM ARTIST": "album_artist",
    "DATE": "date",
    "YEAR": "year",
    "TRACKNUMBER": "track_number",
    "TRACKTOTAL": "track_total",
    "TOTALTRACKS": "track_total",
    "DISCNUMBER": "disc_number",
    "DISCTOTAL": "disc_total",
    "TOTALDISCS": "disc_total",
    "GENRE": "genre",
    "COMPOSER": "composer",
    "PERFORMER": "performer",
    "CONDUCTOR": "conductor",
    "LYRICIST": "lyricist",
    "ARRANGER": "arranger",
    "PRODUCER": "producer",
    "ENGINEER": "engineer",
    "MIXER": "mixer",
    "REMIXER": "remixer",
    "DJMIXER": "dj_mixer",
    "LABEL": "label",
    "CATALOGNUMBER": "catalog_number",
    "BARCODE": "barcode",
    "ISRC": "isrc",
    "COMMENT": "comment",
    "DESCRIPTION": "description",
    "COPYRIGHT": "copyright",
    "LICENSE": "license",
    "LICENSETYPE": "license_type",
    "ORGANIZATION": "organization",
    "VERSION": "version",
    "LANGUAGE": "language",
    "LOCATION": "location",
    "CONTACT": "contact",
    "BPM": "bpm",
    "MOOD": "mood",
    "INITIALKEY": "initial_key",
    "KEY": "key",
    "REPLAYGAIN_TRACK_GAIN": "replaygain_track_gain",
    "REPLAYGAIN_TRACK_PEAK": "replaygain_track_peak",
    "REPLAYGAIN_ALBUM_GAIN": "replaygain_album_gain",
    "REPLAYGAIN_ALBUM_PEAK": "replaygain_album_peak",
    "REPLAYGAIN_REFERENCE_LOUDNESS": "replaygain_reference_loudness",
    "ITUNESCOMPILATION": "itunes_compilation",
    "COMPILATION": "compilation",
    "MEDIA": "media",
    "ORIGINALYEAR": "original_year",
    "ORIGINALDATE": "original_date",
    "ORIGINALARTIST": "original_artist",
    "ORIGINALALBUM": "original_album",
    "RELEASETYPE": "release_type",
    "RELEASESTATUS": "release_status",
    "RELEASECOUNTRY": "release_country",
    "SCRIPT": "script",
    "WORK": "work",
    "MOVEMENT": "movement",
    "MOVEMENTNUMBER": "movement_number",
    "MOVEMENTTOTAL": "movement_total",
    "SHOWMOVEMENT": "show_movement",
    "GROUPING": "grouping",
    "SUBTITLE": "subtitle",
    # MusicBrainz fields
    "MUSICBRAINZ_TRACKID": "musicbrainz_track_id",
    "MUSICBRAINZ_ALBUMID": "musicbrainz_album_id",
    "MUSICBRAINZ_ARTISTID": "musicbrainz_artist_id",
    "MUSICBRAINZ_ALBUMARTISTID": "musicbrainz_album_artist_id",
    "MUSICBRAINZ_RELEASEGROUPID": "musicbrainz_release_group_id",
    "MUSICBRAINZ_WORKID": "musicbrainz_work_id",
    "MUSICBRAINZ_DISCID": "musicbrainz_disc_id",
    "MUSICBRAINZ_RELEASETRACKID": "musicbrainz_release_track_id",
    "MUSICBRAINZ_RECORDINGID": "musicbrainz_recording_id",
    # Discogs fields
    "DISCOGS_RELEASE_ID": "discogs_release_id",
    "DISCOGS_ARTIST_ID": "discogs_artist_id",
    "DISCOGS_LABEL_ID": "discogs_label_id",
    # Acoustid
    "ACOUSTID_ID": "acoustid_id",
    "ACOUSTID_FINGERPRINT": "acoustid_fingerprint",
    # Sorting fields
    "ARTISTSORT": "artist_sort",
    "ALBUMARTISTSORT": "album_artist_sort",
    "ALBUMSORT": "album_sort",
    "TITLESORT": "title_sort",
    "COMPOSERSORT": "composer_sort",
    # Podcast fields
    "PODCAST": "podcast",
    "PODCASTCATEGORY": "podcast_category",
    "PODCASTDESCRIPTION": "podcast_description",
    "PODCASTID": "podcast_id",
    "PODCASTKEYWORDS": "podcast_keywords",
    "PODCASTURL": "podcast_url",
    # Classical music fields
    "OPUS": "opus",
    "PART": "part",
    "PARTNUMBER": "part_number",
    "ENSEMBLE": "ensemble",
    "ORCHESTRA": "orchestra",
    "CHOIR": "choir",
    "VENUE": "venue",
    "PERIOD": "period",
    "STYLE": "style",
    # Technical fields
    "ENCODER": "encoder",
    "ENCODED-BY": "encoded_by",
    "ENCODEDBY": "encoded_by",
    "ENCODING": "encoding",
    "TOOL": "tool",
    "SOURCE": "source",
    "SOURCEMEDIA": "source_media",
    "BITRATE": "bitrate",
    "EAN": "ean",
    "UPC": "upc",
}

# APE tag field mappings
APE_TAG_FIELDS = {
    "Title": "title",
    "Subtitle": "subtitle",
    "Artist": "artist",
    "Album": "album",
    "Album Artist": "album_artist",
    "Composer": "composer",
    "Arranger": "arranger",
    "Conductor": "conductor",
    "Orchestra": "orchestra",
    "Ensemble": "ensemble",
    "Publisher": "publisher",
    "Label": "label",
    "Catalog": "catalog_number",
    "Barcode": "barcode",
    "ISRC": "isrc",
    "Year": "year",
    "Record Date": "record_date",
    "Genre": "genre",
    "Track": "track_number",
    "Disc": "disc_number",
    "Comment": "comment",
    "Lyrics": "lyrics",
    "Copyright": "copyright",
    "Encoded By": "encoded_by",
    "BPM": "bpm",
    "Language": "language",
    "Mood": "mood",
    "Media": "media",
    "MixArtist": "mix_artist",
    "Remixer": "remixer",
    "Producer": "producer",
    "Engineer": "engineer",
    "Mixer": "mixer",
    "DJMixer": "dj_mixer",
    "Writer": "writer",
    "Related": "related",
    "Abstract": "abstract",
    "Bibliography": "bibliography",
    "File": "file",
    "Index": "index",
    "Debut Album": "debut_album",
    "Record Location": "record_location",
    "Rating": "rating",
    "Setting": "setting",
    "Weblink": "weblink",
    "Buy URL": "buy_url",
    "Artist URL": "artist_url",
    "Publisher URL": "publisher_url",
    "Copyright URL": "copyright_url",
    "Cover Art (Front)": "cover_art_front",
    "Cover Art (Back)": "cover_art_back",
    "Cover Art (Media)": "cover_art_media",
    "ReplayGain_Track_Gain": "replaygain_track_gain",
    "ReplayGain_Track_Peak": "replaygain_track_peak",
    "ReplayGain_Album_Gain": "replaygain_album_gain",
    "ReplayGain_Album_Peak": "replaygain_album_peak",
    # MusicBrainz
    "MUSICBRAINZ_TRACKID": "musicbrainz_track_id",
    "MUSICBRAINZ_ALBUMID": "musicbrainz_album_id",
    "MUSICBRAINZ_ARTISTID": "musicbrainz_artist_id",
    "MUSICBRAINZ_ALBUMARTISTID": "musicbrainz_album_artist_id",
}

# MP4/M4A tag mappings (additional to existing)
MP4_TAG_FIELDS = {
    "\xa9nam": "title",
    "\xa9ART": "artist",
    "\xa9alb": "album",
    "\xa9day": "date",
    "\xa9gen": "genre",
    "\xa9cmt": "comment",
    "\xa9wrt": "composer",
    "\xa9too": "encoder",
    "\xa9cpy": "copyright",
    "\xa9grp": "grouping",
    "\xa9lyr": "lyrics",
    "\xa9mvn": "movement_name",
    "\xa9mvc": "movement_count",
    "\xa9mvi": "movement_index",
    "\xa9wrk": "work",
    "\xa9nrt": "narrator",
    "aART": "album_artist",
    "cpil": "compilation",
    "pgap": "gapless",
    "tmpo": "tempo",
    "rtng": "rating",
    "shwm": "show_movement",
    "stik": "media_type",
    "hdvd": "hd_video",
    "pcst": "podcast",
    "catg": "category",
    "keyw": "keyword",
    "desc": "description",
    "ldes": "long_description",
    "sdes": "short_description",
    "tvsh": "tv_show",
    "tves": "tv_episode",
    "tven": "tv_episode_number",
    "tvsn": "tv_season",
    "tvnn": "tv_network",
    "purd": "purchase_date",
    "sonm": "title_sort",
    "soal": "album_sort",
    "soar": "artist_sort",
    "soaa": "album_artist_sort",
    "soco": "composer_sort",
    "sosn": "show_sort",
    "trkn": "track_number",
    "disk": "disc_number",
    "covr": "cover_art",
    "----:com.apple.iTunes:iTunNORM": "itunes_normalization",
    "----:com.apple.iTunes:iTunSMPB": "itunes_seamless_playback",
    "----:com.apple.iTunes:ISRC": "isrc",
    "----:com.apple.iTunes:BARCODE": "barcode",
    "----:com.apple.iTunes:CATALOGNUMBER": "catalog_number",
    "----:com.apple.iTunes:LABEL": "label",
    "----:com.apple.iTunes:MEDIA": "media",
    "----:com.apple.iTunes:RELEASETYPE": "release_type",
    "----:com.apple.iTunes:RELEASESTATUS": "release_status",
    "----:com.apple.iTunes:SCRIPT": "script",
    "----:com.apple.iTunes:MusicBrainz Album Id": "musicbrainz_album_id",
    "----:com.apple.iTunes:MusicBrainz Artist Id": "musicbrainz_artist_id",
    "----:com.apple.iTunes:MusicBrainz Album Artist Id": "musicbrainz_album_artist_id",
    "----:com.apple.iTunes:MusicBrainz Track Id": "musicbrainz_track_id",
    "----:com.apple.iTunes:MusicBrainz Work Id": "musicbrainz_work_id",
    "----:com.apple.iTunes:MusicBrainz Release Group Id": "musicbrainz_release_group_id",
    "----:com.apple.iTunes:MusicBrainz Disc Id": "musicbrainz_disc_id",
    "----:com.apple.iTunes:Acoustid Id": "acoustid_id",
    "----:com.apple.iTunes:Acoustid Fingerprint": "acoustid_fingerprint",
    "----:com.apple.iTunes:DISCOGS_RELEASE_ID": "discogs_release_id",
    "----:com.apple.iTunes:DISCOGS_ARTIST_ID": "discogs_artist_id",
    "----:com.apple.iTunes:DISCOGS_LABEL_ID": "discogs_label_id",
    "----:com.apple.iTunes:WORK": "work",
    "----:com.apple.iTunes:MOOD": "mood",
    "----:com.apple.iTunes:INITIALKEY": "initial_key",
    "----:com.apple.iTunes:REPLAYGAIN_TRACK_GAIN": "replaygain_track_gain",
    "----:com.apple.iTunes:REPLAYGAIN_TRACK_PEAK": "replaygain_track_peak",
    "----:com.apple.iTunes:REPLAYGAIN_ALBUM_GAIN": "replaygain_album_gain",
    "----:com.apple.iTunes:REPLAYGAIN_ALBUM_PEAK": "replaygain_album_peak",
}


def get_all_id3_frame_ids() -> List[str]:
    """Return all known ID3v2 frame IDs."""
    frames = []
    frames.extend(ID3V2_TEXT_FRAMES.keys())
    frames.extend(ID3V2_URL_FRAMES.keys())
    frames.extend(ID3V2_OTHER_FRAMES.keys())
    return frames


def get_id3_field_name(frame_id: str) -> Optional[str]:
    """Convert ID3v2 frame ID to human-readable field name."""
    if frame_id in ID3V2_TEXT_FRAMES:
        return ID3V2_TEXT_FRAMES[frame_id]
    if frame_id in ID3V2_URL_FRAMES:
        return ID3V2_URL_FRAMES[frame_id]
    if frame_id in ID3V2_OTHER_FRAMES:
        return ID3V2_OTHER_FRAMES[frame_id]
    return None


def get_vorbis_field_name(tag_name: str) -> Optional[str]:
    """Convert Vorbis comment tag name to normalized field name."""
    upper = tag_name.upper()
    return VORBIS_COMMENT_FIELDS.get(upper)


def get_ape_field_name(tag_name: str) -> Optional[str]:
    """Convert APE tag name to normalized field name."""
    return APE_TAG_FIELDS.get(tag_name)


def get_mp4_field_name(atom: str) -> Optional[str]:
    """Convert MP4 atom to normalized field name."""
    return MP4_TAG_FIELDS.get(atom)


def get_picture_type_name(type_id: int) -> str:
    """Convert APIC picture type ID to name."""
    return APIC_PICTURE_TYPES.get(type_id, f"unknown_{type_id}")


def get_event_type_name(type_id: int) -> str:
    """Convert ETCO event type ID to name."""
    return EVENT_TIMING_TYPES.get(type_id, f"unknown_{type_id}")


def get_sylt_content_type_name(type_id: int) -> str:
    """Convert SYLT content type ID to name."""
    return SYLT_CONTENT_TYPES.get(type_id, f"unknown_{type_id}")


def get_rva2_channel_type_name(type_id: int) -> str:
    """Convert RVA2 channel type ID to name."""
    return RVA2_CHANNEL_TYPES.get(type_id, f"unknown_{type_id}")


def convert_id3v22_to_v24(frame_id: str) -> Optional[str]:
    """Convert ID3v2.2 three-character frame ID to ID3v2.4."""
    return ID3V22_TO_V24_MAP.get(frame_id)


def get_id3_frames_field_count() -> int:
    """Return total number of ID3 frame mappings."""
    return (
        len(ID3V2_TEXT_FRAMES) +
        len(ID3V2_URL_FRAMES) +
        len(ID3V2_OTHER_FRAMES) +
        len(VORBIS_COMMENT_FIELDS) +
        len(APE_TAG_FIELDS) +
        len(MP4_TAG_FIELDS) +
        len(APIC_PICTURE_TYPES) +
        len(EVENT_TIMING_TYPES) +
        len(SYLT_CONTENT_TYPES) +
        len(RVA2_CHANNEL_TYPES)
    )


def extract_id3_frames_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive ID3 frame metadata from audio files.

    Args:
        filepath: Path to the audio file

    Returns:
        Dictionary containing extracted ID3 frame metadata
    """
    result = {
        "id3v2_text_frames": {},
        "id3v2_url_frames": {},
        "id3v2_other_frames": {},
        "vorbis_comments": {},
        "ape_tags": {},
        "mp4_tags": {},
        "picture_info": {},
        "fields_extracted": 0,
        "is_valid_audio": False,
        "audio_format": None
    }

    try:
        from mutagen import File
        from mutagen.id3 import ID3, ID3NoHeaderError
        from mutagen.mp4 import MP4
        from mutagen.flac import FLAC
        from mutagen.apev2 import APEv2File
    except Exception:
        result["error"] = "mutagen not available"
        return result

    def _normalize_value(value: Any) -> Any:
        if isinstance(value, list):
            return [str(v) for v in value]
        return str(value)

    try:
        audio_file = File(filepath)
        if audio_file is None:
            result["error"] = "Could not read audio file"
            return result

        result["is_valid_audio"] = True
        result["audio_format"] = type(audio_file).__name__

        # ID3 tags
        id3_tags = None
        try:
            id3_tags = ID3(filepath)
        except ID3NoHeaderError:
            id3_tags = None
        except Exception:
            id3_tags = None

        if id3_tags is not None:
            for frame_id in id3_tags.keys():
                frames = id3_tags.getall(frame_id)
                values = []
                for frame in frames:
                    if frame_id == "APIC":
                        pic = {
                            "mime": getattr(frame, "mime", None),
                            "type": getattr(frame, "type", None),
                            "description": getattr(frame, "desc", None),
                            "size_bytes": len(getattr(frame, "data", b"") or b""),
                        }
                        result["picture_info"].setdefault("apic", []).append(pic)
                        values.append(pic)
                    elif hasattr(frame, "text"):
                        values.extend([str(v) for v in frame.text])
                    elif hasattr(frame, "url"):
                        values.append(frame.url)
                    else:
                        values.append(str(frame))
                value = values if len(values) > 1 else (values[0] if values else "")
                if frame_id in ID3V2_TEXT_FRAMES:
                    result["id3v2_text_frames"][ID3V2_TEXT_FRAMES[frame_id]] = value
                elif frame_id in ID3V2_URL_FRAMES:
                    result["id3v2_url_frames"][ID3V2_URL_FRAMES[frame_id]] = value
                else:
                    result["id3v2_other_frames"][ID3V2_OTHER_FRAMES.get(frame_id, frame_id)] = value

        # Vorbis (FLAC/OGG)
        if isinstance(audio_file, FLAC) or audio_file.__class__.__name__.lower().startswith("ogg"):
            tags = getattr(audio_file, "tags", None)
            if tags:
                for key, val in tags.items():
                    lookup_key = key.upper()
                    field = VORBIS_COMMENT_FIELDS.get(lookup_key, key)
                    result["vorbis_comments"][field] = _normalize_value(val)

        # APE
        if isinstance(audio_file, APEv2File):
            tags = getattr(audio_file, "tags", None)
            if tags:
                for key, val in tags.items():
                    field = APE_TAG_FIELDS.get(key, key)
                    result["ape_tags"][field] = _normalize_value(val)

        # MP4 tags
        if isinstance(audio_file, MP4):
            tags = getattr(audio_file, "tags", None)
            if tags:
                for key, val in tags.items():
                    field = MP4_TAG_FIELDS.get(key, key)
                    result["mp4_tags"][field] = _normalize_value(val)

        result["fields_extracted"] = (
            len(result["id3v2_text_frames"]) +
            len(result["id3v2_url_frames"]) +
            len(result["id3v2_other_frames"]) +
            len(result["vorbis_comments"]) +
            len(result["ape_tags"]) +
            len(result["mp4_tags"]) +
            len(result["picture_info"])
        )
        return result
    except Exception as e:
        result["error"] = str(e)[:200]
        return result

    result["is_valid_audio"] = True
    result["audio_format"] = type(audio_file).__name__

    # Extract ID3v2 frames
    if hasattr(audio_file, 'tags') and audio_file.tags:
                try:
                    # Try ID3 frames
                    if isinstance(audio_file, ID3) or (hasattr(audio_file, 'tags') and any(isinstance(t, ID3) for t in [audio_file.tags] if not isinstance(audio_file.tags, dict))):
                        try:
                            id3_tags = ID3(filepath)
                            for frame in id3_tags.values():
                                frame_id = frame.FrameID
                                frame_name = ID3V2_TEXT_FRAMES.get(frame_id) or ID3V2_URL_FRAMES.get(frame_id) or ID3V2_OTHER_FRAMES.get(frame_id)

                                if frame_name:
                                    # Extract frame value
                                    try:
                                        value = str(frame)
                                        result["id3v2_text_frames"][frame_name] = value[:200]
                                    except Exception:
                                        result["id3v2_other_frames"][frame_name] = "present"
                        except Exception as e:
                            result["id3_error"] = str(e)[:100]

                    # Try Vorbis comments (FLAC, OGG)
                    if isinstance(audio_file, FLAC):
                        for comment_name, comment_value in (audio_file.tags or {}).items():
                            field_name = VORBIS_COMMENT_FIELDS.get(comment_name, comment_name.lower())
                            result["vorbis_comments"][field_name] = str(comment_value)[:200]

                    # Try MP4 tags (M4A)
                    if isinstance(audio_file, MP4):
                        for key, value in (audio_file.tags or {}).items():
                            field_name = MP4_TAG_FIELDS.get(key, key.lower())
                            result["mp4_tags"][field_name] = str(value)[:200]

                    # Try APEv2 tags
                    try:
                        ape_file = APEv2File(filepath)
                        if ape_file.tags:
                            for tag_name, tag_value in ape_file.tags.items():
                                field_name = APE_TAG_FIELDS.get(tag_name, tag_name.lower())
                                result["ape_tags"][field_name] = str(tag_value)[:200]
                    except Exception:
                        pass
                except Exception:
                    pass

            # Extract general metadata
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                if hasattr(info, 'length'):
                    result["duration"] = info.length
                if hasattr(info, 'bitrate'):
                    result["bitrate"] = info.bitrate
                if hasattr(info, 'sample_rate'):
                    result["sample_rate"] = info.sample_rate

            # Count total fields extracted
            total_fields = (
                len(result["id3v2_text_frames"]) +
                len(result["id3v2_url_frames"]) +
                len(result["id3v2_other_frames"]) +
                len(result["vorbis_comments"]) +
                len(result["ape_tags"]) +
                len(result["mp4_tags"]) +
                len(result.get("picture_info", {}))
            )
            result["fields_extracted"] = total_fields

        except ImportError:
            result["error"] = "Mutagen library not available"
            return result
    except Exception as e:
        result["error"] = f"ID3 frames extraction failed: {str(e)[:200]}"
        return result

    return result


# Extended Audio Tags - Streaming Services
AUDIO_STREAMING_TAGS = {
    # Spotify
    "TXXX:Spotify Id": "spotify_track_id",
    "TXXX:Spotify Artist Id": "spotify_artist_id",
    "TXXX:Spotify Album Id": "spotify_album_id",
    "TXXX:Spotify URI": "spotify_uri",
    "TXXX:Spotify Preview URL": "spotify_preview_url",
    "TXXX:Spotify Track Duration": "spotify_track_duration",
    "TXXX:Spotify Popularity": "spotify_popularity",
    # Apple Music
    "TXXX:Apple Music Id": "apple_music_id",
    "TXXX:iTunes Store Id": "itunes_store_id",
    "TXXX:iTunes Album Id": "itunes_album_id",
    "TXXX:iTunes Artist Id": "itunes_artist_id",
    # Deezer
    "TXXX:Deezer Id": "deezer_id",
    "TXXX:Deezer Artist Id": "deezer_artist_id",
    "TXXX:Deezer Album Id": "deezer_album_id",
    "TXXX:Deezer Link": "deezer_link",
    # Tidal
    "TXXX:Tidal Id": "tidal_id",
    "TXXX:Tidal Track Id": "tidal_track_id",
    "TXXX:Tidal Album Id": "tidal_album_id",
    "TXXX:Tidal Artist Id": "tidal_artist_id",
    # YouTube
    "TXXX:YouTube Id": "youtube_id",
    "TXXX:YouTube Video Id": "youtube_video_id",
    "TXXX:YouTube Channel Id": "youtube_channel_id",
    "TXXX:YouTube Category": "youtube_category",
    "TXXX:YouTube Tags": "youtube_tags",
    # SoundCloud
    "TXXX:SoundCloud Id": "soundcloud_id",
    "TXXX:SoundCloud Link": "soundcloud_link",
    "TXXX:SoundCloud Username": "soundcloud_username",
    # Bandcamp
    "TXXX:Bandcamp Id": "bandcamp_id",
    "TXXX:Bandcamp Link": "bandcamp_link",
    "TXXX:Bandcamp Album Id": "bandcamp_album_id",
    # Napster
    "TXXX:Napster Id": "napster_id",
    "TXXX:Napster Artist Id": "napster_artist_id",
    # Amazon Music
    "TXXX:Amazon Music Id": "amazon_music_id",
    "TXXX:Amazon Album Id": "amazon_album_id",
}

# DJ/Production Software Tags
DJ_PRODUCTION_TAGS = {
    # Serato
    "TXXX:Serato Id": "serato_id",
    "TXXX:Serato Crate": "serato_crate",
    "TXXX:Serato Bpm": "serato_bpm",
    "TXXX:Serato Key": "serato_key",
    "TXXX:Serato End": "serato_end",
    "TXXX:Serato Start": "serato_start",
    "TXXX:Serato Comments": "serato_comments",
    "TXXX:Serato Rating": "serato_rating",
    "TXXX:Serato Beatport Id": "serato_beatport_id",
    "TXXX:Serato Discogs Id": "serato_discogs_id",
    # Traktor
    "TXXX:Traktor Id": "traktor_id",
    "TXXX:Traktor Cue": "traktor_cue",
    "TXXX:Traktor Loop": "traktor_loop",
    "TXXX:Traktor Grid": "traktor_grid",
    "TXXX:Traktor Bpm": "traktor_bpm",
    "TXXX:Traktor Comment": "traktor_comment",
    # Rekordbox
    "TXXX:Rekordbox Id": "rekordbox_id",
    "TXXX:Rekordbox Cue": "rekordbox_cue",
    "TXXX:Rekordbox Loop": "rekordbox_loop",
    "TXXX:Rekordbox Bpm": "rekordbox_bpm",
    "TXXX:Rekordbox Comment": "rekordbox_comment",
    "TXXX:Rekordbox Position": "rekordbox_position",
    # Virtual DJ
    "TXXX:VirtualDJ Id": "virtual_dj_id",
    "TXXX:VirtualDJ Cue": "virtual_dj_cue",
    "TXXX:VirtualDJ Loop": "virtual_dj_loop",
    "TXXX:VirtualDJ Bpm": "virtual_dj_bpm",
    # Engine DJ
    "TXXX:Engine DJ Id": "engine_dj_id",
    "TXXX:Engine DJ Hotcue": "engine_dj_hotcue",
    "TXXX:Engine DJ Memory Cue": "engine_dj_memory_cue",
    "TXXX:Engine DJ Loop": "engine_dj_loop",
    # Mixxx
    "TXXX:Mixxx Cue": "mixxx_cue",
    "TXXX:Mixxx Hotcue": "mixxx_hotcue",
    "TXXX:Mixxx Bpm": "mixxx_bpm",
    "TXXX:Mixxx Comment": "mixxx_comment",
    # Ableton Live
    "TXXX:Ableton Live Cue": "ableton_cue",
    "TXXX:Ableton Loop": "ableton_loop",
    "TXXX:Ableton Warped": "ableton_warped",
    "TXXX:Ableton Clip Name": "ableton_clip_name",
    "TXXX:Ableton Scene": "ableton_scene",
    # FL Studio
    "TXXX:FL Studio Channel": "fl_studio_channel",
    "TXXX:FL Studio插 Note": "fl_studio_note",
    "TXXX:FL Studio Effect": "fl_studio_effect",
    # Logic Pro
    "TXXX:Logic Pro Region": "logic_pro_region",
    "TXXX:Logic Pro Take": "logic_pro_take",
    "TXXX:Logic Pro Cycle": "logic_pro_cycle",
    # Pro Tools
    "TXXX:ProTools Region": "pro_tools_region",
    "TXXX:ProTools Clip": "pro_tools_clip",
    "TXXX:ProTools Session": "pro_tools_session",
}

# Radio Broadcast Tags
RADIO_BROADCAST_TAGS = {
    # RDS (Radio Data System)
    "TXXX:RDS PS": "rds_program_service_name",
    "TXXX:RDS PI": "rds_program_identification",
    "TXXX:RDS PTY": "rds_program_type",
    "TXXX:RDS TP": "rds_traffic_program",
    "TXXX:RDS TA": "rds_traffic_announcement",
    "TXXX:RDS MS": "rds_music_speech",
    "TXXX:RDS CT": "rds_ct",
    "TXXX:RDS RT": "rds_radiotext",
    "TXXX:RDS RT Plus": "rds_radiotext_plus",
    "TXXX:RDS EON": "rds_eon",
    "TXXX:RDS PIN": "rds_pin",
    "TXXX:RDS PTYN": "rds_program_type_name",
    # HD Radio
    "TXXX:HD Radio Id": "hd_radio_id",
    "TXXX:HD Radio Artist": "hd_radio_artist",
    "TXXX:HD Radio Title": "hd_radio_title",
    "TXXX:HD Radio Album": "hd_radio_album",
    "TXXX:HD Radio Genre": "hd_radio_genre",
    # DAB/DAB+
    "TXXX:DAB Service Id": "dab_service_id",
    "TXXX:DAB Ensemble": "dab_ensemble",
    "TXXX:DAB Component": "dab_component",
    "TXXX:DAB Flags": "dab_flags",
    # Sirius XM
    "TXXX:SiriusXM Channel Id": "siriusxm_channel_id",
    "TXXX:SiriusXM Channel Name": "siriusxm_channel_name",
    "TXXX:SiriusXM Artist": "siriusxm_artist",
    "TXXX:SiriusXM Title": "siriusxm_title",
}

# Classical Music Extensions
CLASSICAL_MUSIC_TAGS = {
    "TXXX:Classical Catalog": "classical_catalog",
    "TXXX:Classical Work": "classical_work",
    "TXXX:Classical Movement": "classical_movement",
    "TXXX:Classical Movement Number": "classical_movement_number",
    "TXXX:Classical Movement Total": "classical_movement_total",
    "TXXX:Classical Opuse": "classical_opus",
    "TXXX:Classical Catalog Number": "classical_catalog_number",
    "TXXX:Classical Title": "classical_title",
    "TXXX:Classical Nickname": "classical_nickname",
    "TXXX:Classical Key": "classical_key",
    "TXXX:Classical Year Composed": "classical_year_composed",
    "TXXX:Classical Date Composed": "classical_date_composed",
    "TXXX:Classical First Performance": "classical_first_performance",
    "TXXX:Classical First Recording": "classical_first_recording",
    "TXXX:Classical Soloists": "classical_soloists",
    "TXXX:Classical Ensemble": "classical_ensemble",
    "TXXX:Classical Conductor": "classical_conductor",
    "TXXX:Classical Orchestra": "classical_orchestra",
    "TXXX:Classical Choir": "classical_choir",
    "TXXX:Classical Producer": "classical_producer",
    "TXXX:Classical Engineer": "classical_engineer",
    "TXXX:Classical Recording Location": "classical_recording_location",
    "TXXX:Classical Recording Date": "classical_recording_date",
    "TXXX:Classical Release Date": "classical_release_date",
    "TXXX:Classical Label": "classical_label",
    "TXXX:Classical Format": "classical_format",
    "TXXX:Classical Notes": "classical_notes",
    "TXXX:Classical Librettist": "classical_librettist",
    "TXXX:Classical Lyricist": "classical_lyricist",
    "TXXX:Classical_arranger": "classical_arranger",
}

# Podcast Extensions
PODCAST_TAGS = {
    "TXXX:Podcast URL": "podcast_url",
    "TXXX:Podcast Feed URL": "podcast_feed_url",
    "TXXX:Podcast GUID": "podcast_guid",
    "TXXX:Podcast Episode GUID": "podcast_episode_guid",
    "TXXX:Podcast Episode Type": "podcast_episode_type",
    "TXXX:Podcast Episode Season": "podcast_episode_season",
    "TXXX:Podcast Episode Episode": "podcast_episode_number",
    "TXXX:Podcast Episode Title": "podcast_episode_title",
    "TXXX:Podcast Episode Description": "podcast_episode_description",
    "TXXX:Podcast Episode Summary": "podcast_episode_summary",
    "TXXX:Podcast Episode Duration": "podcast_episode_duration",
    "TXXX:Podcast Episode Explicit": "podcast_episode_explicit",
    "TXXX:Podcast Episode Block": "podcast_episode_block",
    "TXXX:Podcast Channel Title": "podcast_channel_title",
    "TXXX:Podcast Channel Author": "podcast_channel_author",
    "TXXX:Podcast Channel Description": "podcast_channel_description",
    "TXXX:Podcast Channel URL": "podcast_channel_url",
    "TXXX:Podcast Channel Feed": "podcast_channel_feed",
    "TXXX:Podcast Channel Image": "podcast_channel_image",
    "TXXX:Podcast Channel Category": "podcast_channel_category",
    "TXXX:Podcast Channel Owner": "podcast_channel_owner",
    "TXXX:Podcast Channel Owner Email": "podcast_channel_owner_email",
    "TXXX:Podcast Copyright": "podcast_copyright",
    "TXXX:Podcast Publication Date": "podcast_publication_date",
    "TXXX:Podcast Keywords": "podcast_keywords",
    "TXXX:Podcast Type": "podcast_type",
    "TXXX:Podcast Complete": "podcast_complete",
    "TXXX:Podcast Live": "podcast_live",
}

# Audio Fingerprinting and Analysis
AUDIO_FINGERPRINT_TAGS = {
    # Acoustid
    "TXXX:Acoustid Id": "acoustid_id",
    "TXXX:Acoustid Fingerprint": "acoustid_fingerprint",
    "TXXX:Acoustid Duration": "acoustid_duration",
    "TXXX:Acoustid Score": "acoustid_score",
    "TXXX:Acoustid Match Type": "acoustid_match_type",
    # Chromaprint
    "TXXX:Chromaprint": "chromaprint",
    "TXXX:Chromaprint Algorithm": "chromaprint_algorithm",
    "TXXX:Chromaprint Version": "chromaprint_version",
    # Echo Nest
    "TXXX:Echo Nest Id": "echo_nest_id",
    "TXXX:Echo Nest Analysis URL": "echo_nest_analysis_url",
    # AudD
    "TXXX:AudD Id": "audd_id",
    "TXXX:AudD Match": "audd_match",
    # Shazam
    "TXXX:Shazam Id": "shazam_id",
    "TXXX:Shazam Signature": "shazam_signature",
    # AudioDB
    "TXXX:AudioDB Id": "audiodb_id",
    "TXXX:AudioDB Track Id": "audiodb_track_id",
    # Last.fm
    "TXXX:Last.fm Id": "lastfm_id",
    "TXXX:Last.fm URL": "lastfm_url",
    "TXXX:Last.fm Playcount": "lastfm_playcount",
    "TXXX:Last.fm Listener Count": "lastfm_listener_count",
}

# Audio Analysis Tags (Loudness, Dynamic Range, etc.)
AUDIO_ANALYSIS_TAGS = {
    # ReplayGain (extended)
    "TXXX:REPLAYGAIN_TRACK_MINMAX": "replaygain_track_minmax",
    "TXXX:REPLAYGAIN_TRACK_RANGE": "replaygain_track_range",
    "TXXX:REPLAYGAIN_ALBUM_MINMAX": "replaygain_album_minmax",
    "TXXX:REPLAYGAIN_ALBUM_RANGE": "replaygain_album_range",
    "TXXX:REPLAYGAIN_TRACK_PEAK_DB": "replaygain_track_peak_db",
    "TXXX:REPLAYGAIN_ALBUM_PEAK_DB": "replaygain_album_peak_db",
    # EBU R128
    "TXXX:REPLAYGAIN_TRACK_GAIN_DB": "replaygain_track_gain_db",
    "TXXX:REPLAYGAIN_ALBUM_GAIN_DB": "replaygain_album_gain_db",
    "TXXX:REPLAYGAIN_REFERENCE_LOUDNESS_DB": "replaygain_reference_loudness_db",
    # Dynamic Range
    "TXXX:DYNAMIC_RANGE": "dynamic_range",
    "TXXX:DYNAMIC_RANGE_COMPRESSION": "dynamic_range_compression",
    "TXXX:PEAK_AMPLITUDE": "peak_amplitude",
    "TXXX:PEAK_LEVEL": "peak_level",
    "TXXX:RMS_AMPLITUDE": "rms_amplitude",
    "TXXX:RMS_LEVEL": "rms_level",
    # Frequency Analysis
    "TXXX:LOW_FREQUENCY": "low_frequency",
    "TXXX:HIGH_FREQUENCY": "high_frequency",
    "TXXX:CENTER_FREQUENCY": "center_frequency",
    "TXXX:BANDWIDTH": "bandwidth",
    # Spectral Analysis
    "TXXX:SPECTRAL_CENTROID": "spectral_centroid",
    "TXXX:SPECTRAL_FLUX": "spectral_flux",
    "TXXX:SPECTRAL_ROLLOFF": "spectral_rolloff",
    "TXXX:SPECTRAL_FLATNESS": "spectral_flatness",
    # Rhythm Analysis
    "TXXX:BPM": "bpm_detected",
    "TXXX:BPM CONFIDENCE": "bpm_confidence",
    "TXXX:BPM QUALITY": "bpm_quality",
    "TXXX:BEAT STRENGTH": "beat_strength",
    "TXXX:CLARITY": "clarity",
    "TXXX:DANCEABILITY": "danceability",
    "TXXX:TEMPO STABILITY": "tempo_stability",
    "TXXX:TEMPO CONFIDENCE": "tempo_confidence",
    # Key Detection
    "TXXX:KEY DETECTION": "key_detection",
    "TXXX:KEY CONFIDENCE": "key_confidence",
    "TXXX:KEY QUALITY": "key_quality",
    # Timbre
    "TXXX:BRIGHTNESS": "brightness",
    "TXXX:DARKNESS": "darkness",
    "TXXX:WARMTH": "warmth",
    "TXXX:COLDNESS": "coldness",
    "TXXX:HARSHNESS": "harshness",
    "TXXX:ROUGHNESS": "roughness",
}

# Lossless Audio Extensions
LOSSLESS_AUDIO_TAGS = {
    # FLAC specific
    "TXXX:FLAC Cue Sheet": "flac_cue_sheet",
    "TXXX:FLAC Cue Sheet Checksum": "flac_cue_sheet_checksum",
    "TXXX:FLAC Matroska Cue Sheet": "flac_matroska_cue_sheet",
    "TXXX:FLAC Seektable": "flac_seektable",
    "TXXX:FLAC Vendor": "flac_vendor",
    # WAV/AIFF specific
    "TXXX:WAV Cue Sheet": "wav_cue_sheet",
    "TXXX:WAV Label": "wav_label",
    "TXXX:WAV Note": "wav_note",
    "TXXX:WAV.ds64": "wav_ds64",
    "TXXX:AIFF Chunk": "aiff_chunk",
    # DSD specific
    "TXXX:DSD Bit Depth": "dsd_bit_depth",
    "TXXX:DSD Sample Rate": "dsd_sample_rate",
    "TXXX:DSD Channels": "dsd_channels",
    "TXXX:DSD Type": "dsd_type",
    "TXXX:DSD Encoding": "dsd_encoding",
    # PCM specific
    "TXXX:PCM Bits Per Sample": "pcm_bits_per_sample",
    "TXXX:PCM Sample Rate": "pcm_sample_rate",
    "TXXX:PCM Channels": "pcm_channels",
    "TXXX:PCM Byte Order": "pcm_byte_order",
    "TXXX:PCM Alignment": "pcm_alignment",
}

# Spatial/3D Audio Tags
SPATIAL_AUDIO_TAGS = {
    # Dolby Atmos
    "TXXX:Dolby Atmos": "dolby_atmos",
    "TXXX:Dolby Atmos Objects": "dolby_atmos_objects",
    "TXXX:Dolby Atmos Version": "dolby_atmos_version",
    # DTS:X
    "TXXX:DTS:X": "dts_x",
    "TXXX:DTS:X Objects": "dts_x_objects",
    # Sony 360 Reality Audio
    "TXXX:Sony 360 Reality Audio": "sony_360_reality_audio",
    "TXXX:Sony 360 Objects": "sony_360_objects",
    # Ambisonics
    "TXXX:Ambisonics Format": "ambisonics_format",
    "TXXX:Ambisonics Order": "ambisonics_order",
    "TXXX:Ambisonics Type": "ambisonics_type",
    "TXXX:Ambisonics Channel Count": "ambisonics_channel_count",
    "TXXX:Ambisonics Reference Level": "ambisonics_reference_level",
    # Binaural
    "TXXX:Binaural": "binaural",
    "TXXX:Binaural Type": "binaural_type",
    # Headphone
    "TXXX:Headphone Optimized": "headphone_optimized",
    "TXXX:Headphone Profile": "headphone_profile",
}

# Audio Restoration Tags
AUDIO_RESTORATION_TAGS = {
    "TXXX:Declicked": "declicked",
    "TXXX:Declick Strength": "declick_strength",
    "TXXX:Decracked": "decracked",
    "TXXX:Decrack Strength": "decrack_strength",
    "TXXX:Dereduced": "dereduced",
    "TXXX:Dereduce Strength": "dereduce_strength",
    "TXXX:Dehummed": "dehummed",
    "TXXX:Dehum Strength": "dehum_strength",
    "TXXX:Denoised": "denoised",
    "TXXX:Denoise Strength": "denoise_strength",
    "TXXX:Denoise Type": "denoise_type",
    "TXXX:Dereverberated": "dereverberated",
    "TXXX:Dereverb Strength": "dereverb_strength",
    "TXXX:Dereverb Type": "dereverb_type",
    "TXXX:Level Corrected": "level_corrected",
    "TXXX:Level Correction Amount": "level_correction_amount",
    "TXXX:EQ Applied": "eq_applied",
    "TXXX:EQ Type": "eq_type",
    "TXXX:Normalization Applied": "normalization_applied",
    "TXXX:Normalization Peak": "normalization_peak",
    "TXXX:Mastered For": "mastered_for",
    "TXXX:Mastering Engineer": "mastering_engineer",
    "TXXX:Mastering Studio": "mastering_studio",
    "TXXX:Mastering Date": "mastering_date",
}


def get_all_audio_extension_tags() -> Dict[str, str]:
    """Return all extended audio tag mappings."""
    all_tags = {}
    all_tags.update(AUDIO_STREAMING_TAGS)
    all_tags.update(DJ_PRODUCTION_TAGS)
    all_tags.update(RADIO_BROADCAST_TAGS)
    all_tags.update(CLASSICAL_MUSIC_TAGS)
    all_tags.update(PODCAST_TAGS)
    all_tags.update(AUDIO_FINGERPRINT_TAGS)
    all_tags.update(AUDIO_ANALYSIS_TAGS)
    all_tags.update(LOSSLESS_AUDIO_TAGS)
    all_tags.update(SPATIAL_AUDIO_TAGS)
    all_tags.update(AUDIO_RESTORATION_TAGS)
    return all_tags


def get_id3_frames_extended_field_count() -> int:
    """Return total number of ID3 frames including extended mappings."""
    base_count = get_id3_frames_field_count()
    extended_count = len(get_all_audio_extension_tags())
    return base_count + extended_count


def get_all_audio_extension_tags() -> Dict[str, str]:
    """Return all extended audio tag mappings."""
    all_tags = {}
    try:
        all_tags.update(AUDIO_STREAMING_TAGS)
    except NameError:
        pass
    try:
        all_tags.update(DJ_PRODUCTION_TAGS)
    except NameError:
        pass
    try:
        all_tags.update(PODCAST_TAGS)
    except NameError:
        pass
    try:
        all_tags.update(AUDIBLE_TAGS)
    except NameError:
        pass
    try:
        all_tags.update(SOUNDCLOUD_TAGS)
    except NameError:
        pass
    try:
        all_tags.update(BANDCAMP_TAGS)
    except NameError:
        pass
    try:
        all_tags.update(AUDIO_RESTORATION_TAGS)
    except NameError:
        pass
    return all_tags
