"""
Social Media Metadata Extraction
Instagram, Facebook, Twitter/X, TikTok, YouTube, and other platforms
"""

from typing import Dict, Any, Optional, List


# Instagram Metadata
INSTAGRAM_TAGS = {
    "Instagram_ImageType": "instagram_image_type",
    "Instagram_FilterType": "instagram_filter_type",
    "Instagram_CreationTimestamp": "instagram_creation_timestamp",
    "Instagram_VideoDuration": "instagram_video_duration",
    "Instagram_LikeCount": "instagram_like_count",
    "Instagram_CommentCount": "instagram_comment_count",
    "Instagram_ViewCount": "instagram_view_count",
    "Instagram_IsVideo": "instagram_is_video",
    "Instagram_HasLocation": "instagram_has_location",
    "Instagram_IsSponsored": "instagram_is_sponsored",
    "Instagram_StoryMedia": "instagram_story_media",
    "Instagram_ReelsSource": "instagram_reels_source",
    "Instagram_MediaType": "instagram_media_type",
    "Instagram_ProductType": "instagram_product_type",
    "Instagram_IGTV": "instagram_igtv",
    "Instagram_Shopping": "instagram_shopping",
    "Instagram_Collaboration": "instagram_collaboration",
    "Instagram_OriginalMedia": "instagram_original_media",
}

# Facebook Metadata
FACEBOOK_TAGS = {
    "Facebook_ImageType": "facebook_image_type",
    "Facebook_CreationDate": "facebook_creation_date",
    "Facebook_LikeCount": "facebook_like_count",
    "Facebook_CommentCount": "facebook_comment_count",
    "Facebook_ShareCount": "facebook_share_count",
    "Facebook_ViewCount": "facebook_view_count",
    "Facebook_IsVideo": "facebook_is_video",
    "Facebook_VideoDuration": "facebook_video_duration",
    "Facebook_HasLocation": "facebook_has_location",
    "Facebook_IsSponsored": "facebook_is_sponsored",
    "Facebook_PostID": "facebook_post_id",
    "Facebook_PageID": "facebook_page_id",
    "Facebook_Permalink": "facebook_permalink",
    "Facebook_ReactionCount": "facebook_reaction_count",
    "Facebook_CarouselCount": "facebook_carousel_count",
    "Facebook_Stories": "facebook_stories",
    "Facebook_Reels": "facebook_reels",
}

# Twitter/X Metadata
TWITTER_TAGS = {
    "Twitter_ImageType": "twitter_image_type",
    "Twitter_CreationDate": "twitter_creation_date",
    "Twitter_LikeCount": "twitter_like_count",
    "Twitter_RetweetCount": "twitter_retweet_count",
    "Twitter_ReplyCount": "twitter_reply_count",
    "Twitter_QuoteCount": "twitter_quote_count",
    "Twitter_ViewCount": "twitter_view_count",
    "Twitter_IsReply": "twitter_is_reply",
    "Twitter_IsRetweet": "twitter_is_retweet",
    "Twitter_ReplyTo": "twitter_reply_to",
    "Twitter_QuoteOf": "twitter_quote_of",
    "Twitter_MediaType": "twitter_media_type",
    "Twitter_PollOptions": "twitter_poll_options",
    "Twitter_ThreadID": "twitter_thread_id",
    "Twitter_ConversationID": "twitter_conversation_id",
    "Twitter_Language": "twitter_language",
    "Twitter_Source": "twitter_source",
}

# TikTok Metadata
TIKTOK_TAGS = {
    "TikTok_ImageType": "tiktok_image_type",
    "TikTok_CreationDate": "tiktok_creation_date",
    "TikTok_LikeCount": "tiktok_like_count",
    "TikTok_CommentCount": "tiktok_comment_count",
    "TikTok_ShareCount": "tiktok_share_count",
    "TikTok_ViewCount": "tiktok_view_count",
    "TikTok_Duration": "tiktok_duration",
    "TikTok_VideoID": "tiktok_video_id",
    "TikTok_DeviceID": "tiktok_device_id",
    "TikTok_AuthorID": "tiktok_author_id",
    "TikTok_Challenge": "tiktok_challenge",
    "TikTok_SoundID": "tiktok_sound_id",
    "TikTok_EffectID": "tiktok_effect_id",
    "TikTok_Str": "tiktok_str",
    "TikTok_VideoFormat": "tiktok_video_format",
    "TikTok_Hashtag": "tiktok_hashtag",
    "TikTok_Duets": "tiktok_duets",
    "TikTok_Stitches": "tiktok_stitches",
    "TikTok_IsOriginal": "tiktok_is_original",
}

# YouTube Metadata
YOUTUBE_TAGS = {
    "YouTube_ImageType": "youtube_image_type",
    "YouTube_VideoID": "youtube_video_id",
    "YouTube_Title": "youtube_title",
    "YouTube_Description": "youtube_description",
    "YouTube_ChannelID": "youtube_channel_id",
    "YouTube_ChannelTitle": "youtube_channel_title",
    "YouTube_PublishedAt": "youtube_published_at",
    "YouTube_ViewCount": "youtube_view_count",
    "YouTube_LikeCount": "youtube_like_count",
    "YouTube_DislikeCount": "youtube_dislike_count",
    "YouTube_CommentCount": "youtube_comment_count",
    "YouTube_FavoriteCount": "youtube_favorite_count",
    "YouTube_CategoryID": "youtube_category_id",
    "YouTube_LiveBroadcastContent": "youtube_live_content",
    "YouTube_KeyWords": "youtube_keywords",
    "YouTube_PrivacyStatus": "youtube_privacy_status",
    "YouTube_License": "youtube_license",
    "YouTube_Embeddable": "youtube_embeddable",
    "YouTube_PublicStatsViewable": "youtube_public_stats",
    "YouTube_ViewCountRatio": "youtube_view_count_ratio",
}

# General Social Media Tags
GENERAL_SOCIAL_TAGS = {
    "Social_Platform": "social_platform",
    "Social_PostID": "social_post_id",
    "Social_AuthorUsername": "social_author_username",
    "Social_AuthorDisplayName": "social_author_display_name",
    "Social_AuthorProfileURL": "social_author_profile_url",
    "Social_PostURL": "social_post_url",
    "Social_PostDate": "social_post_date",
    "Social_Caption": "social_caption",
    "Social_Hashtags": "social_hashtags",
    "Social_Mentions": "social_mentions",
    "Social_LikeCount": "social_like_count",
    "Social_CommentCount": "social_comment_count",
    "Social_ShareCount": "social_share_count",
    "Social_ViewCount": "social_view_count",
    "Social_IsSponsored": "social_is_sponsored",
    "Social_FilterUsed": "social_filter_used",
    "Social_EngagementRate": "social_engagement_rate",
    "Social_Reach": "social_reach",
    "Social_Impressions": "social_impressions",
    "Social_ClickCount": "social_click_count",
}


def extract_social_media_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract social media metadata from files.
    
    Args:
        filepath: Path to file
    
    Returns:
        Dictionary with social media metadata
    """
    result = {
        "social_media": {
            "instagram": {},
            "facebook": {},
            "twitter": {},
            "tiktok": {},
            "youtube": {},
            "general": {}
        },
        "detection": {
            "platforms_detected": [],
            "confidence": 0.0
        },
        "engagement_metrics": {},
        "fields_extracted": 0
    }
    
    try:
        from .exif import extract_exif_metadata
        from .iptc_xmp import extract_iptc_xmp_metadata
        
        all_tags = {}
        
        exif_data = extract_exif_metadata(filepath)
        if exif_data and "error" not in exif_data:
            for category in ["image", "photo", "gps", "interoperability"]:
                if category in exif_data and isinstance(exif_data[category], dict):
                    all_tags.update(exif_data[category])
        
        iptc_data = extract_iptc_xmp_metadata(filepath)
        if iptc_data and "error" not in iptc_data and isinstance(iptc_data, dict):
            for section in iptc_data.values():
                if isinstance(section, dict):
                    all_tags.update(section)
        
        detected_any = False
        
        for tag, value in all_tags.items():
            tag_str = str(tag)
            
            if tag_str in INSTAGRAM_TAGS:
                result["social_media"]["instagram"][INSTAGRAM_TAGS[tag_str]] = str(value)
                detected_any = True
            
            elif tag_str in FACEBOOK_TAGS:
                result["social_media"]["facebook"][FACEBOOK_TAGS[tag_str]] = str(value)
                detected_any = True
            
            elif tag_str in TWITTER_TAGS:
                result["social_media"]["twitter"][TWITTER_TAGS[tag_str]] = str(value)
                detected_any = True
            
            elif tag_str in TIKTOK_TAGS:
                result["social_media"]["tiktok"][TIKTOK_TAGS[tag_str]] = str(value)
                detected_any = True
            
            elif tag_str in YOUTUBE_TAGS:
                result["social_media"]["youtube"][YOUTUBE_TAGS[tag_str]] = str(value)
                detected_any = True
            
            elif tag_str in GENERAL_SOCIAL_TAGS:
                result["social_media"]["general"][GENERAL_SOCIAL_TAGS[tag_str]] = str(value)
                detected_any = True
        
        if detected_any:
            platforms = []
            for platform in ["instagram", "facebook", "twitter", "tiktok", "youtube"]:
                if result["social_media"][platform]:
                    platforms.append(platform)
            result["detection"]["platforms_detected"] = platforms
            result["detection"]["confidence"] = min(1.0, len(platforms) * 0.25)
            
            total_engagement = 0
            engagement_fields = ["like_count", "comment_count", "share_count", "view_count"]
            
            for platform_data in result["social_media"].values():
                for field in engagement_fields:
                    if field in platform_data:
                        try:
                            total_engagement += int(platform_data[field])
                        except (ValueError, TypeError):
                            pass
            
            if total_engagement > 0:
                result["engagement_metrics"]["total_engagement"] = total_engagement
        
        total_fields = sum(len(v) for v in result["social_media"].values())
        result["fields_extracted"] = total_fields
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to extract social media metadata: {str(e)}"}


def get_social_media_field_count() -> int:
    """Return approximate number of social media fields."""
    return 60
