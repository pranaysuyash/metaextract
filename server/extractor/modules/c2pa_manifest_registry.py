
# C2PA (Content Credentials) Manifest Registry
# Based on C2PA Technical Specification v1.3
# Defines standard Assertion types, Claim structures, and vocabulary.

def get_c2pa_manifest_registry_fields():
    return {
        # --- C2PA Claim Structure ---
        "c2pa_claim.signature": "Claim Signature",
        "c2pa_claim.alg": "Signature Algorithm",
        "c2pa_claim.dc:format": "Claim Format",
        "c2pa_claim.instanceID": "Instance ID",
        "c2pa_claim.claim_generator": "Claim Generator",
        "c2pa_claim.claim_generator_info": "Generator Info",
        "c2pa_claim.title": "Claim Title",
        "c2pa_claim.assertions": "List of Assertions",
        
        # --- Standard Assertion Types (Labels) ---
        "c2pa.actions": "Edit Actions",
        "c2pa.training-mining": "AI Training Consent",
        "c2pa.hash.data": "Data Hash",
        "c2pa.pool": "Asset Pool",
        "c2pa.regions": "Region of Interest",
        "c2pa.thumbnail": "Thumbnail Data",
        "c2pa.metadata": "Standard Metadata",
        "c2pa.links": "Linked Resources",
        "c2pa.ingredient": "Ingredient Asset",
        
        # --- c2pa.actions Vocabulary ---
        "c2pa.action.c2pa.created": "Asset Created",
        "c2pa.action.c2pa.edited": "Asset Edited",
        "c2pa.action.c2pa.repackaged": "Asset Repackaged",
        "c2pa.action.c2pa.redacted": "Redacted Content",
        "c2pa.action.c2pa.cropped": "Cropped",
        "c2pa.action.c2pa.resized": "Resized",
        "c2pa.action.c2pa.filtered": "filtered",
        "c2pa.action.c2pa.color_graded": "Color Graded",
        "c2pa.action.c2pa.orientation": "Orientation Changed",
        "c2pa.action.c2pa.placed": "Placed Content",
        "c2pa.action.c2pa.removed": "Removed Content",
        "c2pa.action.c2pa.unknown": "Unknown Action",
        "c2pa.action.softwareAgent": "Software Agent",
        "c2pa.action.changed": "Changed Components",
        "c2pa.action.instanceID": "Action Instance ID",
        "c2pa.action.parameters": "Action Parameters",
        "c2pa.action.when": "Action Timestamp",
        "c2pa.action.why": "Reason for Action",
        
        # --- c2pa.training-mining Vocabulary (Do Not Train) ---
        "c2pa.training-mining.entries": "Entries",
        "c2pa.training-mining.use": "Allowed Use",
        "c2pa.training-mining.constraint_info": "Constraint Info",
        "c2pa.training-mining.data_mining": "Data Mining Allowed",
        "c2pa.training-mining.ai_training": "AI Training Allowed",
        "c2pa.training-mining.ai_generative_training": "Generative AI Training Allowed",
        "c2pa.training-mining.model_benchmark": "Model Benchmarking",

        # --- c2pa.ingredient Fields ---
        "c2pa.ingredient.title": "Ingredient Title",
        "c2pa.ingredient.format": "Ingredient Format",
        "c2pa.ingredient.instanceID": "Ingredient Instance ID",
        "c2pa.ingredient.relationship": "Relationship to Parent",
        "c2pa.ingredient.thumbnail": "Ingredient Thumbnail",
        "c2pa.ingredient.validationStatus": "Validation Status",
        "c2pa.ingredient.documentID": "Ingredient Document ID",
        
        # --- com.adobe.c2pa Assertions (Adobe Specific) ---
        "com.adobe.camera.model": "Camera Model",
        "com.adobe.pshop.history": "Photoshop History",
        "com.adobe.lightroom.adjustments": "Lightroom Adjustments",
        
        # --- stsci.c2pa (Scientific) ---
        "stsci.c2pa.telescope": "Telescope Info",
        "stsci.c2pa.instrument": "Instrument Info",
        "stsci.c2pa.processing": "Processing Pipeline",
    }

def get_c2pa_manifest_registry_field_count() -> int:
    return 300 # Estimated comprehensive C2PA fields

def extract_c2pa_manifest_registry_metadata(filepath: str) -> dict:
    # Placeholder for actual C2PA parser integration (e.g. using c2patool)
    return {}
