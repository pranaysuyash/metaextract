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
