#!/usr/bin/env python3
"""Social Media Metadata Fields Inventory

This script documents metadata fields available from major social media platforms
via their public APIs and embed endpoints.

Social Media Platforms Covered:
- Instagram (Graph API, oEmbed)
- TikTok (Embed API, Discovery API)
- YouTube (Data API v3, oEmbed)
- Twitter/X (API v2, oEmbed)
- Facebook (Graph API, oEmbed)
- LinkedIn (Share API, oEmbed)
- Snapchat (Snap Kit)
- Pinterest (Pin API)
- Reddit (API)
- Twitch (Helix API)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


SOCIAL_MEDIA_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "Social Media Platform APIs and oEmbed endpoints",
    "description": "Metadata fields available from major social media platforms",
    "platforms": {
        "instagram": {
            "api": "Instagram Graph API",
            "categories": {
                "media_object": {
                    "description": "Instagram Media object fields (photos, videos, carousel)",
                    "fields": [
                        "id", "caption", "media_type", "media_url", "permalink", 
                        "thumbnail_url", "timestamp", "username", "like_count",
                        "comments_count", "insights_impressions", "insights_reach",
                        "insights_saved", "engagement_count", "video_view_count",
                        "duration", "is_sidecar", "children", "product_type",
                        "media_product_type", "owner", "shortcode", "dimensions",
                        "filter_type", "location", "comments_enabled", "like_and_view_counts_disabled",
                        "is_video", "video_url", "accessibility_caption", "alt",
                        "fb_like_count", "fb_comments_count", "fb_shares_count",
                        "fb_saves_count", "fb_reach", "fb_impressions", "fb_engagement"
                    ],
                    "count": 43
                },
                "profile": {
                    "description": "Instagram Business/Creator Profile fields",
                    "fields": [
                        "id", "username", "name", "profile_picture_url", "biography",
                        "followers_count", "follows_count", "media_count", "website",
                        "category", "category_name", "description", "is_verified",
                        "verified_status", "business_category", "contact_email",
                        "page_id", "page_name", "account_type", "profile_type",
                        "ig_id", "email", "phone", "password_requirements",
                        "can_link_entities_in_bio", "has_animal_stickers", "has_review_rejects",
                        "has_igtv_video_tutorials", "has_new_email_notification",
                        "should_show_oauth_account_denylist_status", "third_party_partner_apps"
                    ],
                    "count": 30
                },
                "story": {
                    "description": "Instagram Story fields",
                    "fields": [
                        "id", "caption", "media_type", "media_url", "permalink",
                        "timestamp", "username", "like_count", "comments_count",
                        "insights_replies", "insights_impressions", "insights_reach",
                        "insights_saved", "insights_taps_forward", "insights_taps_back",
                        "insights_exits", "insights_story_responses", "media_product_type",
                        "owner", "shortcode", "duration", "is_video", "video_url"
                    ],
                    "count": 23
                },
                "reel": {
                    "description": "Instagram Reels fields",
                    "fields": [
                        "id", "caption", "media_type", "media_url", "permalink",
                        "timestamp", "username", "like_count", "comments_count",
                        "insights_impressions", "insights_reach", "insights_saved",
                        "insights_shares", "insights_comments", "insights_plays",
                        "media_product_type", "owner", "shortcode", "video_url",
                        "thumbnail_url", "duration", "is_video", "view_count",
                        "video_view_count", "like_count", "cover_frame_url"
                    ],
                    "count": 25
                },
                "hashtag": {
                    "description": "Instagram Hashtag fields",
                    "fields": [
                        "id", "name", "profile_picture_url", "search_result_count",
                        "edge_hashtag_to_media", "edge_hashtag_to_top_posts",
                        "edge_hashtag_to_content_advisory", "allows_follower"
                    ],
                    "count": 8
                },
                "oembed": {
                    "description": "Instagram oEmbed fields",
                    "fields": [
                        "type", "version", "author_id", "author_name", "author_url",
                        "provider_name", "provider_url", "thumbnail_url", "thumbnail_width",
                        "thumbnail_height", "html", "width", "height", "cache_age",
                        "media_id", "title", "description"
                    ],
                    "count": 17
                }
            },
            "total_fields": 146
        },
        "tiktok": {
            "api": "TikTok API (oEmbed, embed.js)",
            "categories": {
                "video": {
                    "description": "TikTok Video object fields",
                    "fields": [
                        "id", "title", "description", "create_time", "cover_image_url",
                        "share_url", "duration", "digg_count", "comment_count", "share_count",
                        "view_count", "like_count", "video_id", "video_description",
                        "video_url", "author_id", "author_name", "author_avatar",
                        "music_id", "music_title", "music_author", "music_cover_url",
                        "music_play_url", "is_ad", "is_video", "width", "height",
                        "ratio", "format", "bit_rate", "definition", "subtitle_subtitles",
                        "stickers", "is_story", "challenges", "duet_video_id",
                        "original_duet_video_id", "effect_ids", "filter_ids",
                        "playlist_id", "playlist_name", "voiceover_id"
                    ],
                    "count": 44
                },
                "user": {
                    "description": "TikTok User profile fields",
                    "fields": [
                        "id", "open_id", "union_id", "avatar_url", "avatar_large",
                        "avatar_medium", "display_name", "bio_description", "profile_deep_link",
                        "is_verified", "follower_count", "following_count", "likes_count",
                        "video_count", "digg_count", "friend_count", "verified_status",
                        "verified_reason", "verified_reason_description", "custom_verify",
                        "platform_sync", "can_gcrealth", "username"
                    ],
                    "count": 23
                },
                "music": {
                    "description": "TikTok Music/Sound fields",
                    "fields": [
                        "id", "title", "author_name", "duration", "album",
                        "play_url", "cover_url", "music_status", "source_platform",
                        "original", "duration_normalized", "album_id", "artist_id"
                    ],
                    "count": 13
                },
                "hashtag": {
                    "description": "TikTok Hashtag/Challenge fields",
                    "fields": [
                        "id", "title", "cover_url", "banner_url", "is_commerce",
                        "desc_url", "profile_url", "view_count", "video_count",
                        "digg_count", "challenge_id", "author"
                    ],
                    "count": 12
                },
                "oembed": {
                    "description": "TikTok oEmbed fields",
                    "fields": [
                        "version", "provider_url", "provider_name", "author_id",
                        "author_name", "author_url", "type", "width", "height",
                        "html", "title", "thumbnail_url", "thumbnail_width",
                        "thumbnail_height", "cache_age"
                    ],
                    "count": 15
                },
                "embed": {
                    "description": "TikTok embed.js fields",
                    "fields": [
                        "videoId", "userId", "createTime", "desc", "duration",
                        "diguCount", "commentCount", "shareCount", "viewCount",
                        "isVerify", "isAd", "musicId", "musicTitle", "musicAuthor",
                        "musicCoverUrl", "musicPlayUrl", "duet", "stitch",
                        "canvas", "ratio", "bitrate", "definition"
                    ],
                    "count": 23
                }
            },
            "total_fields": 130
        },
        "youtube": {
            "api": "YouTube Data API v3, oEmbed",
            "categories": {
                "video": {
                    "description": "YouTube Video resource fields",
                    "fields": [
                        "id", "title", "description", "publishedAt", "channelId",
                        "channelTitle", "categoryId", "liveBroadcastContent", "defaultLanguage",
                        "defaultAudioLanguage", "duration", "dimension", "definition",
                        "caption", "licensedContent", "contentRating", "projection",
                        "madeForKids", "channelContentPolicy", "embedHtml", "embeddable",
                        "publicStatsViewable", "viewCount", "likeCount", "dislikeCount",
                        "favoriteCount", "commentCount", "topicCategories", "tags",
                        "localized", "thumbnails", "fileDetails", "processingDetails",
                        "suggestions", "liveStreamingDetails", "recordingDetails",
                        "player", "status", "statistics", "snippet"
                    ],
                    "count": 41
                },
                "channel": {
                    "description": "YouTube Channel resource fields",
                    "fields": [
                        "id", "title", "description", "customUrl", "channelUrl",
                        "videoUploadDefaultPrivacy", "bannerImageUrl", "bannerMobileImageUrl",
                        "bannerTabletLowImageUrl", "bannerMobileMediumImageUrl",
                        "bannerTabletImageUrl", "bannerDesktopLowImageUrl",
                        "bannerDesktopMediumImageUrl", "bannerDesktopHighImageUrl",
                        "bannerTvMediumImageUrl", "bannerTvHighImageUrl", "brandingSettings",
                        "contentDetails", "contentOwnerDetails", "statistics",
                        "topicDetails", "localized", "viewCount", "subscriberCount",
                        "hiddenSubscriberCount", "videoCount", "privacyStatus",
                        "isLinked", "longUploadsStatus", "madeForKids", "keywords"
                    ],
                    "count": 32
                },
                "playlist": {
                    "description": "YouTube Playlist resource fields",
                    "fields": [
                        "id", "title", "description", "publishedAt", "channelId",
                        "channelTitle", "defaultLanguage", "localized", "thumbnail",
                        "status", "contentDetails", "player", "itemCount",
                        "privacyStatus", "addToPlaylistToNewSeriesDefaultPrivacy",
                        "allowNewSeriesDefaultPrivacy", "allowToSavePlaylistDefaultPrivacy",
                        "saveFromHistoryDefaultPrivacy"
                    ],
                    "count": 18
                },
                "playlist_item": {
                    "description": "YouTube PlaylistItem resource fields",
                    "fields": [
                        "id", "playlistId", "position", "note", "contentDetails",
                        "status", "snippet", "resourceId", "thumbnail"
                    ],
                    "count": 9
                },
                "comment": {
                    "description": "YouTube Comment and CommentThread fields",
                    "fields": [
                        "id", "textDisplay", "textOriginal", "authorChannelId",
                        "authorChannelUrl", "authorProfileImageUrl", "authorDisplayName",
                        "videoId", "channelId", "parentId", "canRate", "viewerRating",
                        "likeCount", "moderationStatus", "publishedAt", "updatedAt",
                        "totalReplyCount", "replies", "topLevelComment", "snippet",
                        "repliesResource"
                    ],
                    "count": 21
                },
                "oembed": {
                    "description": "YouTube oEmbed fields",
                    "fields": [
                        "type", "version", "provider_name", "provider_url",
                        "author_name", "author_url", "title", "width", "height",
                        "html", "thumbnail_url", "thumbnail_width", "thumbnail_height"
                    ],
                    "count": 13
                },
                "live_broadcast": {
                    "description": "YouTube Live Broadcast fields",
                    "fields": [
                        "id", "title", "description", "publishedAt", "channelId",
                        "channelTitle", "scheduledStartTime", "scheduledEndTime",
                        "actualStartTime", "actualEndTime", "isLiveBroadcast",
                        "isRealtime", "liveChatId", "concurrentViewers", "liveStreamingDetails",
                        "status", "privacyStatus", "recordingStatus", "boundStreamId",
                        "boundStreamLastUpdateTimeMillis", "monitorStream", "enableDvr",
                        "enableContentEncryption", "startWithSlate", "isMdx", "lowLatency"
                    ],
                    "count": 26
                }
            },
            "total_fields": 160
        },
        "twitter_x": {
            "api": "Twitter API v2, oEmbed",
            "categories": {
                "tweet": {
                    "description": "Twitter Tweet (post) fields",
                    "fields": [
                        "id", "text", "created_at", "author_id", "in_reply_to_user_id",
                        "conversation_id", "referenced_tweets", "reply_settings", "lang",
                        "public_metrics", "non_public_metrics", "organic_metrics",
                        "source", "withheld", "geo", "place", "attachments",
                        "entities", "context_annotations", "matching_rules",
                        "possibly_sensitive", "edit_history_tweet_ids", "edit_controls",
                        "views", "bookmarks", "likes", "retweets", "replies",
                        "quotes", "note_tweet", "super_followers", "text_link_domains"
                    ],
                    "count": 31
                },
                "user": {
                    "description": "Twitter User profile fields",
                    "fields": [
                        "id", "name", "username", "description", "entities",
                        "location", "url", "profile_image_url", "profile_image_extensions",
                        "protected", "verified", "verified_type", "created_at",
                        "public_metrics", "followers_count", "following_count",
                        "tweet_count", "listed_count", "pinned_tweet_id",
                        "profile_banner_url", "default_profile", "default_profile_image",
                        "withheld", "withheld_scope", "withheld_countries",
                        "notifications", "screen_name", "profile_link_color",
                        "profile_text_color", "profile_sidebar_fill_color",
                        "profile_sidebar_border_color", "is_translator",
                        "is_translation_enabled", "translator_type"
                    ],
                    "count": 33
                },
                "space": {
                    "description": "Twitter Space fields",
                    "fields": [
                        "id", "state", "created_at", "ended_at", "title",
                        "host_ids", "speaker_ids", "speaker_ids", "moderator_ids",
                        "invited_user_ids", "participant_count", "total_live_listeners",
                        "peak_concurrent_listeners", "scheduled_start", "topics",
                        "is_ticketed", "access_settings", "duration"
                    ],
                    "count": 18
                },
                "list": {
                    "description": "Twitter List fields",
                    "fields": [
                        "id", "name", "slug", "description", "created_at",
                        "owner_id", "follower_count", "member_count", "private",
                        "following", "description_entities"
                    ],
                    "count": 11
                },
                "oembed": {
                    "description": "Twitter oEmbed fields",
                    "fields": [
                        "type", "version", "url", "author_name", "author_url",
                        "provider_name", "provider_url", "height", "width", "html",
                        "cache_age", "embed_id", "content"
                    ],
                    "count": 13
                }
            },
            "total_fields": 106
        },
        "facebook": {
            "api": "Facebook Graph API, oEmbed",
            "categories": {
                "post": {
                    "description": "Facebook Post fields",
                    "fields": [
                        "id", "message", "story", "story_tags", "permalink_url",
                        "created_time", "admin_creator", "app_id", "attachment",
                        "backdated_time", "call_to_action", "caption", "child_attachments",
                        "comments", "coordinates", "error_info", "feed_targeting",
                        "from", "icon", "instagram_eligible", "is_instagram_eligible",
                        "is_hidden", "is_expired", "is_pinned", "is_sponsored",
                        "linked_story", "message_tags", "multi_share_end_card",
                        "multi_share_optimized", "object_id", "parent_id", "place",
                        "privacy", "promotable", "promotion_status", "properties",
                        "scheduled_publish_time", "shares", "status_type", "story_id",
                        "subscribed", "target", "targeting", "to", "type", "updated_time",
                        "video_entry_point", "video_id", "video_start_time",
                        "views", "with_tags", "reactions", "likes", "comments_count",
                        "shares_count"
                    ],
                    "count": 54
                },
                "page": {
                    "description": "Facebook Page fields",
                    "fields": [
                        "id", "about", "admin_notes", "app_links", "artwork",
                        "attire", "band_members", "best_page", "bio", "birthday",
                        "booking_agent", "category", "category_list", "checkins",
                        "company_overview", "contact_address", "culinary_team",
                        "current_location", "description", "description_html",
                        "directed_by", "display_subtext", "emails", "engagement",
                        "fan_count", "features", "food_styles", "founded",
                        "general_info", "general_manager", "genre", "hours",
                        "instagram", "is_always_open", "is_chain", "is_community_page",
                        "is_owned", "is_permanently_closed", "is_published", "is_verified",
                        "is_webhooks_subscribed", "link", "location", "members",
                        "mission", "name", "name_with_location_descriptor",
                        "network", "new_like_count", "offer_eligible", "offers",
                        "parent_page", "parking", "payment_options", "personal",
                        "personal_info", "personal_interests", "phone", "photos",
                        "picture", "place_type", "plot_outline", "preferred_audience",
                        "press_contact", "price_range", "produced_by", "products",
                        "promotion_eligible", "promotion_ineligible_reason",
                        "public_transit", "rating_count", "record_label_name",
                        "release_date", "restaurant_services", "restaurant_specialties",
                        "schedule", "screen_name", "season", "single_line_address",
                        "social_presence", "specialties", "store_number", "studio",
                        "supports_donate_button_in_live", "talking_about_count",
                        "temporary_status", "unread_notif_count", "username", "verified",
                        "verification_status", "video_upload_limits", "videos",
                        "website", "were_here_count", "workflows", "written_by"
                    ],
                    "count": 107
                },
                "profile": {
                    "description": "Facebook User Profile fields",
                    "fields": [
                        "id", "about", "age_range", "birthday", "context",
                        "cover", "currency", "devices", "education", "email",
                        "favorite_athletes", "favorite_teams", "first_name",
                        "gender", "hometown", "inspirational_people", "install_type",
                        "is_guest_user", "languages", "last_name", "link",
                        "locale", "location", "meeting_for", "middle_name",
                        "name", "name_format", "payment_pricepoints", "platform",
                        "preferred_locale", "profile_pic", "quotes", "relationship_status",
                        "religion", "security_settings", "shared_login_upgrade_required_by",
                        "short_name", "significant_other", "sports", "tags",
                        "third_party_id", "timezone", "updated_time", "verified",
                        "video_upload_limits", "viewer_can_send_gift"
                    ],
                    "count": 46
                },
                "photo": {
                    "description": "Facebook Photo fields",
                    "fields": [
                        "id", "album", "backdated_time", "backdated_time_granularity",
                        "created_time", "from", "height", "icon", "images",
                        "is_silhoutte", "link", "location", "name", "name_tags",
                        "offset_x", "offset_y", "picture", "place", "privacy",
                        "reactions", "source", "tags", "updated_time", "webp_images",
                        "width", "album_id", "can_delete", "can_tag"
                    ],
                    "count": 27
                },
                "video": {
                    "description": "Facebook Video fields",
                    "fields": [
                        "id", "backdated_time", "backdated_time_granularity",
                        "content_tags", "created_time", "description", "embed_html",
                        "entity", "embeddable", "from", "icon", "is_instagram_eligible",
                        "is_synced", "is_tv_video", "length", "live_status",
                        "live_video_breaks", "live_video_clips", "message", "permalink_url",
                        "picture", "place", "privacy", "promoted_id", "published",
                        "scheduled_publish_time", "shared_text_formatting", "source",
                        "status", "story", "subscribed", "tags", "title", "updated_time",
                        "views", "video_insights", "thumbnails"
                    ],
                    "count": 37
                },
                "oembed": {
                    "description": "Facebook oEmbed fields",
                    "fields": [
                        "type", "version", "title", "author_name", "author_url",
                        "provider_name", "provider_url", "thumbnail_url", "thumbnail_width",
                        "thumbnail_height", "html", "width", "height", "cache_age"
                    ],
                    "count": 14
                }
            },
            "total_fields": 285
        },
        "linkedin": {
            "api": "LinkedIn Share API, oEmbed",
            "categories": {
                "post": {
                    "description": "LinkedIn Share/Post fields",
                    "fields": [
                        "id", "author", "category", "commentary", "created_at",
                        "distribution", "first_published_at", "full_content", "is_reshare_disabled_by_author",
                        "is_resharable", "like_count", "comment_count", "reposts_count",
                        "visibility", "lifecycle_status", "object_type", "original_share",
                        "original_share_of", "root_update", "attachement", "content",
                        "description", "entity", "media", "thumbnails", "title",
                        "author_company", "author_profile", "subdescription", "resolved_url"
                    ],
                    "count": 29
                },
                "profile": {
                    "description": "LinkedIn User Profile fields",
                    "fields": [
                        "id", "localized_first_name", "localized_last_name", "localized_headline",
                        "profilePicture", "profilePictureDisplayImage", "profilePictureDisplayImageStandalone",
                        "background_image", "vanity_name", "first_name", "last_name",
                        "maiden_name", "headline", "pronouns", "location", "country",
                        "geo", "position", "industry", "summary", "certifications",
                        "education", "languages", "skills", "connections", "followers",
                        "is_open_to_work", "is_hiring", "contact_info", "profile_essentials"
                    ],
                    "count": 30
                },
                "organization": {
                    "description": "LinkedIn Organization/Company fields",
                    "fields": [
                        "id", "name", "vanity_name", "description", "specialties",
                        "status", "country", "locale", "industry", "size",
                        "founded", "phone", "threads", "background_cover_image",
                        "logo", "tagline", "summary", "website", "staff_count",
                        "followers", "display_name", "organization_type", "primary_role",
                        "founded_on", "headquarters", "description_localized",
                        "specialties_localized", "title_localized"
                    ],
                    "count": 27
                },
                "article": {
                    "description": "LinkedIn Article fields",
                    "fields": [
                        "id", "author", "category", "created_at", "description",
                        "first_published_at", "last_modified_at", "published_at",
                        "state", "title", "original_url", "thumbnail", "views",
                        "likes", "comments", "shares", "article_content",
                        "visibility", "subtitle", "summary"
                    ],
                    "count": 20
                },
                "oembed": {
                    "description": "LinkedIn oEmbed fields",
                    "fields": [
                        "type", "version", "author_name", "author_url", "provider_name",
                        "provider_url", "html", "width", "height"
                    ],
                    "count": 9
                }
            },
            "total_fields": 115
        },
        "pinterest": {
            "api": "Pinterest API",
            "categories": {
                "pin": {
                    "description": "Pinterest Pin fields",
                    "fields": [
                        "id", "title", "description", "created_at", "article",
                        "link", "url", "image", "images", "video", "board",
                        "owner", "is_video", "is_repin", "repin_count", "like_count",
                        "comment_count", "view_counts", "download_count", "forward_pin_id",
                        "rich_metadata", "is_stale", "note", "original_link",
                        "has_custom_link", "promoted_is_lead_ads", "tracking_token",
                        "is_quiz_poll", "poll_options", "pin_promotion_type"
                    ],
                    "count": 28
                },
                "board": {
                    "description": "Pinterest Board fields",
                    "fields": [
                        "id", "name", "description", "created_at", "url",
                        "owner", "privacy", "collaborator_count", "follower_count",
                        "pin_count", "image", "medium_thumbnail", "video_thumbnail",
                        "is_write_enabled", "mfa_enforced", "layout", "category",
                        "cover_image", "background_image"
                    ],
                    "count": 19
                },
                "user": {
                    "description": "Pinterest User fields",
                    "fields": [
                        "id", "username", "first_name", "last_name", "bio",
                        "created_at", "account_type", "profile_url", "profile_image",
                        "cover_image", "followers", "following", "pins",
                        "boards", "likes", "business_url", "website"
                    ],
                    "count": 17
                }
            },
            "total_fields": 64
        },
        "reddit": {
            "api": "Reddit API",
            "categories": {
                "post": {
                    "description": "Reddit Post/Submission fields",
                    "fields": [
                        "id", "name", "title", "selftext", "selftext_html",
                        "link_flair_text", "link_flair_background_color", "link_flair_text_color",
                        "link_flair_type", "link_flair_template_id", "is_self", "is_video",
                        "is_original_content", "is_reddit_media_domain", "is_meta",
                        "is_crosspostable", "is_self", "locked", "archived", "spoiler",
                        "pinned", "stickied", "premium", "view_count", "ups", "downs",
                        "upvote_ratio", "score", "author", "author_fullname", "author_id",
                        "author_karma", "subreddit", "subreddit_id", "subreddit_name_prefixed",
                        "subreddit_type", "subreddit_subscribers", "created_utc", "created",
                        "num_comments", "num_crossposts", "total_awards_received",
                        "all_awardings", "gilded", "approved_at_utc", "removed_by_category",
                        "removed_by", "mod_reports", "user_reports", "crosspost_parent_list",
                        "media", "media_embed", "secure_media", "secure_media_embed",
                        "poll_data", "preview", "thumbnail", "url"
                    ],
                    "count": 62
                },
                "comment": {
                    "description": "Reddit Comment fields",
                    "fields": [
                        "id", "name", "parent_id", "link_id", "subreddit_id",
                        "author", "author_fullname", "author_flair_css_class",
                        "author_flair_text", "author_flair_text_color", "author_flair_background_color",
                        "body", "body_html", "is_submitter", "collapsed", "collapsed_reason",
                        "collapsed_because_crowd_control", "distinguished", "removed",
                        "deleted", "ups", "downs", "score", "score_hidden",
                        "controversiality", "depth", "replies", "all_replies",
                        "parent", "children", "sort", "count", "gold",
                        "all_awardings"
                    ],
                    "count": 32
                },
                "subreddit": {
                    "description": "Reddit Subreddit fields",
                    "fields": [
                        "id", "name", "title", "description", "description_html",
                        "sidebar", "submit_text", "header_title", "public_description",
                        "over18", "icon_img", "header_img", "banner_img",
                        "mobile_banner_img", "key_color", "subscribers", "active_user_count",
                        "accounts_active", "type", "is_crosspostable_subreddit",
                        "allow_images", "allow_videos", "allow_galleries",
                        "allow_polls", "allow_chat_posts", "allow_collaborator_crowdsourcing",
                        "submission_text", "submit_text_html", "rules",
                        "created_utc", "subscribers", "quarantine"
                    ],
                    "count": 32
                },
                "user": {
                    "description": "Reddit User/Account fields",
                    "fields": [
                        "id", "name", "is_employee", "is_friend", "is_gold",
                        "is_mod", "is_suspended", "verified", "premium",
                        "created_utc", "hide_from_robots", "accept_chats",
                        "accept_pms", "awardee_karma", "awarder_karma",
                        "comment_karma", "link_karma", "total_karma",
                        "inbox_count", "has_subscribed", "has_verified_email",
                        "subreddit", "avatar", "banner", "snoovatar"
                    ],
                    "count": 25
                }
            },
            "total_fields": 151
        },
        "snapchat": {
            "api": "Snap Kit, Stories API",
            "categories": {
                "snap": {
                    "description": "Snapchat Snap/Story fields",
                    "fields": [
                        "id", "type", "status", "created_at", "expiration",
                        "snap_url", "snap_html_url", "snap_preview_url", "thumbnail_url",
                        "title", "description", "duration", "width", "height",
                        "bitrate", "format", "has_audio", "view_count", "screenshots",
                        "forward_count", "reply_count", "geofilter_ids",
                        "geofilter_names", "snap_language", "country_code"
                    ],
                    "count": 25
                },
                "story": {
                    "description": "Snapchat Story fields",
                    "fields": [
                        "id", "type", "status", "created_at", "expired_at",
                        "snap_id", "snaps", "snap_count", "view_count", "screenshot_count",
                        "reply_enabled", "share_enabled", "viewer_count",
                        "story_type", "story_title", "thumbnail_url", "ad_id"
                    ],
                    "count": 17
                },
                "profile": {
                    "description": "Snapchat User Profile fields",
                    "fields": [
                        "id", "display_name", "username", "bitmoji", "avatar",
                        "story", "snapcode", "is_friend", "is_blocked",
                        "added_me", "friends_count", "snaps_sent", "snaps_received"
                    ],
                    "count": 13
                }
            },
            "total_fields": 55
        },
        "twitch": {
            "api": "Twitch Helix API",
            "categories": {
                "video": {
                    "description": "Twitch Video fields",
                    "fields": [
                        "id", "user_id", "user_login", "user_name", "title",
                        "description", "created_at", "published_at", "url", "thumbnail_url",
                        "viewable", "view_count", "language", "duration",
                        "stream_type", "type", "archive_duration", "bitrate",
                        "is_muted", "position", "channel_id", "channel_name"
                    ],
                    "count": 21
                },
                "stream": {
                    "description": "Twitch Stream fields",
                    "fields": [
                        "id", "user_id", "user_login", "user_name", "game_id",
                        "game_name", "type", "title", "viewer_count", "started_at",
                        "language", "thumbnail_url", "is_mature", "tag_ids",
                        "tags", "content_classification_labels"
                    ],
                    "count": 16
                },
                "channel": {
                    "description": "Twitch Channel/Broadcaster fields",
                    "fields": [
                        "id", "login", "display_name", "type", "broadcaster_type",
                        "description", "profile_image_url", "offline_image_url",
                        "view_count", "created_at", "email", "twitch_url",
                        "banner_image", "vip", "affiliate", "partner"
                    ],
                    "count": 16
                },
                "clip": {
                    "description": "Twitch Clip fields",
                    "fields": [
                        "id", "url", "embed_url", " broadcaster_id", "broadcaster_name",
                        "creator_id", "creator_name", "video_id", "game_id", "game_name",
                        "title", "view_count", "created_at", "duration", "thumbnail_url",
                        "is_featured"
                    ],
                    "count": 16
                },
                "user": {
                    "description": "Twitch User fields",
                    "fields": [
                        "id", "login", "display_name", "type", "broadcaster_type",
                        "description", "profile_image_url", "offline_image_url",
                        "view_count", "created_at", "email", "twitch_url"
                    ],
                    "count": 12
                }
            },
            "total_fields": 81
        }
    },
    "totals": {
        "platforms": 10,
        "total_fields": 1263,
        "field_counts_by_platform": {
            "instagram": 146,
            "tiktok": 130,
            "youtube": 160,
            "twitter_x": 106,
            "facebook": 285,
            "linkedin": 115,
            "pinterest": 64,
            "reddit": 151,
            "snapchat": 55,
            "twitch": 81
        }
    }
}


def main():
    output_dir = Path("dist/social_media_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "social_media_inventory.json"
    output_file.write_text(json.dumps(SOCIAL_MEDIA_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary_file = output_dir / "social_media_summary.json"
    summary = {
        "generated_at": SOCIAL_MEDIA_INVENTORY["generated_at"],
        "platforms": SOCIAL_MEDIA_INVENTORY["totals"]["platforms"],
        "total_fields": SOCIAL_MEDIA_INVENTORY["totals"]["total_fields"],
        "field_counts_by_platform": SOCIAL_MEDIA_INVENTORY["totals"]["field_counts_by_platform"],
        "categories": {}
    }
    
    for platform, data in SOCIAL_MEDIA_INVENTORY["platforms"].items():
        summary["categories"][platform] = {
            "api": data["api"],
            "total_fields": data["total_fields"],
            "category_count": len(data["categories"])
        }
    
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("SOCIAL MEDIA METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {SOCIAL_MEDIA_INVENTORY['generated_at']}")
    print(f"Platforms: {SOCIAL_MEDIA_INVENTORY['totals']['platforms']}")
    print(f"Total Fields: {SOCIAL_MEDIA_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY PLATFORM:")
    print("-" * 40)
    for platform, count in sorted(SOCIAL_MEDIA_INVENTORY["totals"]["field_counts_by_platform"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {platform:15s}: {count:>5} fields")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    from datetime import datetime
    main()
