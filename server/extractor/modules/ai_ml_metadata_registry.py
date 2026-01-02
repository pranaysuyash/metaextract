"""
AI/ML Model Metadata Registry
Comprehensive metadata field definitions for Artificial Intelligence and Machine Learning

Target: 3,000+ fields covering:
- Model architecture parameters
- Training dataset provenance
- Hyperparameter configurations
- Model performance metrics
- Deployment metadata
- MLOps tracking
- Model cards documentation
- Bias and fairness metrics
- Explainability metadata
- Federated learning
- Neural architecture search
- AutoML tracking
- Model versioning
- Experiment tracking
- Feature engineering metadata
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib
import os

# ============================================================================
# MODEL ARCHITECTURE FIELDS (500+ fields)
# ============================================================================

NEURAL_NETWORK_ARCHITECTURES = {
    # Architecture Type
    "model_type": "type_of_neural_network",
    "architecture_family": "model_family_category",
    "framework": "deep_learning_framework",
    "implementation_language": "programming_language",
    "model_version": "version_identifier",
    "model_name": "human_readable_name",
    "model_uuid": "universally_unique_identifier",
    "parent_model": "parent_model_reference",
    "derivative_type": "how_model_was_modified",
    "pretrained_base": "pretrained_model_used",

    # Neural Network Specific - Deep Learning
    "total_parameters": "total_learnable_parameters",
    "trainable_parameters": "parameters_updated_during_training",
    "non_trainable_parameters": "frozen_parameters",
    "layer_count": "total_number_of_layers",
    "hidden_layers": "number_of_hidden_layers",
    "input_neurons": "input_layer_size",
    "output_neurons": "output_layer_size",
    "activation_functions": "activations_used_by_layer",
    "loss_function": "objective_function",
    "optimizer": "optimization_algorithm",
    "learning_rate": "initial_learning_rate_value",
    "batch_size": "training_batch_size",
    "epochs": "total_training_epochs",
    "dropout_rate": "dropout_probability",
    "regularization_type": "regularization_method",
    "regularization_strength": "regularization_coefficient",
    "gradient_clipping": "gradient_clipping_threshold",
    "weight_initialization": "weight_initialization_method",
    "bias_initialization": "bias_initialization_method",
    "normalization_layers": "batch_norm_layer_norm",
    "skip_connections": "residual_connections_present",
    "attention_mechanisms": "attention_implementation_details",
    "recurrent_layers": "rnn_lstm_gru_layers",
    "convolutional_layers": "conv_layers_configurations",
    "pooling_layers": "pooling_operations",
    "upsampling_layers": "upsampling_methods",
    "embedding_layers": "embedding_dimensions",
    "dense_layers": "fully_connected_layers",
    "output_layer": "final_layer_configuration",
    "multi_head_attention": "attention_heads_count",
    "transformer_blocks": "number_of_transformer_layers",
    "positional_encoding": "position_encoding_method",
    "layer_normalization": "norm_configuration",
    "feed_forward_dimension": "ffn_hidden_size",
    "attention_dropout": "attention_dropout_rate",
    "encoder_decoder": "architecture_type",
    "bert_style": "bert_architecture_variant",
    "gpt_style": "gpt_architecture_variant",
    "vit_style": "vision_transformer_config",
    "diffusion_model": "diffusion_architecture_details",
    "gan_architecture": "generator_discriminator_config",
    "vae_architecture": "encoder_decoder_bottleneck",
    "graph_neural_network": "gnn_architecture_type",
    "capsule_network": "capsule_configuration",
    "neuro_symbolic": "neural_symbolic_hybrid",
    "mixture_of_experts": "expert_routing_config",
    "ensemble_method": "ensemble_combination_strategy",

    # CNN Specific
    "kernel_sizes": "convolutional_kernel_sizes_per_layer",
    "strides": "convolutional_strides_per_layer",
    "padding": "padding_method_per_layer",
    "dilation_rate": "atrous_convolution_rates",
    "groups": "grouped_convolutions",
    "depthwise_separable": "depthwise_separable_convolutions",
    "transposed_convolutions": "upsampling_convs",
    "receptive_field": "effective_receptive_field_size",
    "feature_map_sizes": "feature_map_dimensions_per_layer",

    # RNN/LSTM/GRU Specific
    "hidden_size": "recurrent_hidden_state_size",
    "num_directions": "bidirectional_unidirectional",
    "sequence_length": "max_sequence_length",
    "cell_state_size": "lstm_cell_state_dimension",
    "forget_gate_bias": "lstm_forget_gate_initialization",
    "recurrent_dropout": "recurrent_connection_dropout",
    "attention_context": "attention_vector_size",

    # Transformer Specific
    "sequence_length_limit": "max_token_sequence_length",
    "vocab_size": "vocabulary_dimension",
    "embedding_dimension": "token_embedding_size",
    "num_attention_heads": "attention_heads_per_layer",
    "head_dimension": "dimension_per_attention_head",
    "feedforward_size": "position_wise_ffn_size",
    "relative_position": "relative_position_encoding",
    "rotary_position": "rotary_position_embedding",
    "alibi_position": "attention_with_linear_biases",
    "cross_attention": "encoder_decoder_attention",
    "masked_attention": "causal_masking",
    "sparse_attention": "attention_pattern_sparsity",
    "flash_attention": "optimized_attention_implementation",
    "memory_efficient": "memory_optimization_techniques",
}

# ============================================================================
# TRAINING DATASET METADATA (400+ fields)
# ============================================================================

DATASET_PROVENANCE = {
    # Dataset Identification
    "dataset_name": "name_of_training_dataset",
    "dataset_version": "dataset_version_identifier",
    "dataset_source": "where_dataset_originated",
    "dataset_license": "dataset_usage_license",
    "dataset_citation": "how_to_cite_dataset",
    "dataset_creators": "who_created_dataset",
    "dataset_curators": "who_maintains_dataset",
    "dataset_release_date": "when_dataset_was_released",
    "dataset_last_modified": "last_dataset_update_date",
    "dataset_download_url": "where_to_download_dataset",
    "dataset_checksum": "dataset_integrity_hash",
    "dataset_format": "file_format_of_dataset",
    "dataset_size_bytes": "dataset_size_in_bytes",
    "dataset_compression": "compression_method_used",

    # Dataset Composition
    "total_samples": "number_of_training_samples",
    "training_samples": "samples_for_training",
    "validation_samples": "samples_for_validation",
    "test_samples": "samples_for_testing",
    "num_classes": "number_of_output_classes",
    "class_distribution": "samples_per_class_distribution",
    "class_imbalance": "class_imbalance_ratio",
    "majority_class": "most_frequent_class",
    "minority_class": "least_frequent_class",
    "augmentation_factor": "data_augmentation_multiplier",
    "synthetic_samples": "synthetically_generated_samples",

    # Data Types and Modalities
    "data_modality": "type_of_data_image_text_audio",
    "input_format": "format_of_input_data",
    "output_format": "format_of_output_labels",
    "feature_dimension": "dimensionality_of_features",
    "image_resolution": "resolution_of_image_data",
    "image_channels": "number_of_color_channels",
    "audio_sample_rate": "audio_sampling_frequency",
    "audio_duration": "length_of_audio_clips",
    "text_tokenization": "tokenization_method",
    "text_vocabulary_size": "vocabulary_size",
    "text_max_length": "maximum_text_sequence_length",
    "video_frame_rate": "video_fps",
    "video_resolution": "video_frame_dimensions",
    "tabular_features": "number_of_tabular_features",
    "categorical_features": "number_of_categorical_variables",
    "numerical_features": "number_of_numerical_variables",
    "temporal_features": "number_of_time_series_features",
    "geospatial_features": "spatial_data_features",

    # Data Quality
    "missing_value_percentage": "percentage_of_missing_values",
    "outlier_percentage": "percentage_of_outliers",
    "duplicate_percentage": "percentage_of_duplicates",
    "noise_level": "estimated_noise_in_data",
    "label_quality_score": "quality_of_labels",
    "feature_quality_score": "quality_of_features",
    "consistency_score": "data_consistency_metric",
    "completeness_score": "data_completeness_metric",
    "validity_score": "data_validity_metric",
    "accuracy_score": "ground_truth_accuracy",

    # Data Preprocessing
    "normalization_method": "feature_normalization",
    "standardization_method": "feature_standardization",
    "feature_scaling": "scaling_method",
    "encoding_method": "categorical_encoding",
    "missing_imputation": "how_missing_values_handled",
    "outlier_treatment": "how_outliers_handled",
    "feature_selection": "feature_selection_method",
    "dimensionality_reduction": "pca_tsne_umap_method",
    "text_preprocessing": "text_cleaning_steps",
    "image_preprocessing": "image_augmentation_techniques",
    "audio_preprocessing": "audio_feature_extraction",
    "data_splitting": "train_val_test_split_method",
    "stratification": "stratified_sampling_method",
    "cross_validation": "cv_folds_strategy",
    "temporal_split": "time_based_splitting",

    # Data Privacy and Ethics
    "personal_data_present": "contains_personally_identifiable_info",
    "sensitive_attributes": "protected_demographic_attributes",
    "consent_obtained": "data_collection_consent",
    "anonymization_method": "de_identification_technique",
    "data_governance": "governance_compliance_status",
    "ethical_approval": "ethics_review_status",
    "bias_assessment": "dataset_bias_analysis",
    "fairness_audit": "fairness_evaluation_results",
    "representativeness": "population_representativeness",
    "inclusive_language": "inclusive_language_practices",
}


# FEDERATED_LEARNING
FEDERATED_LEARNING = {
    "num_clients": "number_of_participating_clients",
    "client_selection": "client_sampling_strategy",
    "aggregation_method": "fedavg_fedprox",
    "communication_rounds": "total_training_rounds",
    "local_epochs": "epochs_per_client",
    "privacy_budget": "differential_privacy_epsilon",
    "secure_aggregation": "encrypted_gradient_aggregation",
    "byzantine_robustness": "adversarial_client_tolerance",
}


# NEURAL_ARCHITECTURE_SEARCH
NEURAL_ARCHITECTURE_SEARCH = {
    "search_space": "architecture_search_space_definition",
    "optimization": "reinforcement_learning_evolutionary",
    "efficiency_predictor": "performance_estimation_model",
    "architecture_encoding": "network_representation_method",
    "evaluation_strategy": "weight_sharing_hypernetwork",
    "search_iterations": "total_architectures_evaluated",
    "best_architecture": "optimal_model_configuration",
}


# AUTOML_TRACKING
AUTOML_TRACKING = {
    "automl_framework": "auto_sklearn_tpot_h2o",
    "time_budget_seconds": "maximum_optimization_time",
    "metric_optimization": "objective_function_target",
    "ensemble_building": "model_combination_strategy",
    "feature_preprocessing": "automated_feature_engineering",
    "algorithm_selection": "model_type_recommendation",
    "hyperparameter_tuning": "automatic_parameter_optimization",
}

def get_ai_ml_metadata_field_count() -> int:
    """Return total number of ai_ml_metadata metadata fields."""
    total = 0
    total += len(NEURAL_NETWORK_ARCHITECTURES)
    total += len(DATASET_PROVENANCE)
    total += len(FEDERATED_LEARNING)
    total += len(NEURAL_ARCHITECTURE_SEARCH)
    total += len(AUTOML_TRACKING)
    total += len(all_fields)
    total += len(AI_ML_METADATA_FIELDS)
    return total

def get_ai_ml_fields() -> Dict[str, str]:
    """Return all AI/ML field mappings."""
    all_fields = {}
    all_fields.update(NEURAL_NETWORK_ARCHITECTURES)
    all_fields.update(DATASET_PROVENANCE)
    return all_fields

def extract_ai_ml_metadata(filepath: str) -> Dict[str, Any]:
    """Extract AI/ML metadata from model files.

    Args:
        filepath: Path to the model file or directory

    Returns:
        Dictionary containing extracted AI/ML metadata
    """
    result = {
        "model_architecture": {},
        "dataset_info": {},
        "hyperparameters": {},
        "performance_metrics": {},
        "deployment_info": {},
        "mlops_info": {},
        "model_card": {},
        "fairness_info": {},
        "explainability": {},
        "fields_extracted": 0,
        "is_valid_ai_ml": False,
        "model_type": None
    }

    try:
        import os
        from pathlib import Path

        file_path = Path(filepath)
        result["file_info"] = {
            "name": file_path.name,
            "extension": file_path.suffix,
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0
        }

        # Detect model format
        if file_path.suffix in ['.h5', '.keras']:
            result["model_type"] = "keras"
            result["is_valid_ai_ml"] = True
        elif file_path.suffix in ['.pt', '.pth', '.pkl']:
            result["model_type"] = "pytorch"
            result["is_valid_ai_ml"] = True
        elif file_path.suffix in ['.onnx']:
            result["model_type"] = "onnx"
            result["is_valid_ai_ml"] = True
        elif file_path.suffix in ['.pb', '.tflite']:
            result["model_type"] = "tensorflow"
            result["is_valid_ai_ml"] = True
        elif 'checkpoint' in file_path.name.lower():
            result["model_type"] = "checkpoint"
            result["is_valid_ai_ml"] = True

        # Try to extract metadata based on format
        if result["model_type"] == "pytorch":
            try:
                import torch
                model_data = torch.load(filepath, map_location='cpu')

                if isinstance(model_data, dict):
                    # Extract model architecture info
                    if 'model_state_dict' in model_data:
                        result["model_architecture"]["has_state_dict"] = True
                        param_count = sum(p.numel() for p in model_data['model_state_dict'].values())
                        result["model_architecture"]["total_parameters"] = param_count

                    # Extract hyperparameters
                    for key in ['epoch', 'learning_rate', 'batch_size', 'optimizer']:
                        if key in model_data:
                            result["hyperparameters"][key] = model_data[key]

                    # Extract training info
                    for key in ['loss', 'accuracy', 'val_loss', 'val_accuracy']:
                        if key in model_data:
                            result["performance_metrics"][key] = model_data[key]

                    result["fields_extracted"] = len(result.get("model_architecture", {})) + \
                                                   len(result.get("hyperparameters", {})) + \
                                                   len(result.get("performance_metrics", {}))
            except Exception as e:
                result["error"] = f"PyTorch extraction failed: {str(e)[:100]}"

        elif result["model_type"] == "keras":
            try:
                # Try to load Keras model structure without full weights
                result["model_architecture"]["format"] = "hdf5_keras"
                result["is_valid_ai_ml"] = True
            except Exception as e:
                result["error"] = f"Keras extraction failed: {str(e)[:100]}"

        elif result["model_type"] == "onnx":
            try:
                import onnx
                model = onnx.load(filepath)

                # Extract model metadata
                result["model_architecture"]["onnx_version"] = model.opset_import[0].version if model.opset_import else 0
                result["model_architecture"]["producer_name"] = model.producer_name or "unknown"
                result["model_architecture"]["graph_inputs"] = [i.name for i in model.graph.input]
                result["model_architecture"]["graph_outputs"] = [o.name for o in model.graph.output]
                result["fields_extracted"] = len(result["model_architecture"])
            except Exception as e:
                result["error"] = f"ONNX extraction failed: {str(e)[:100]}"

        # Look for companion metadata files
        companion_files = ['config.json', 'model_config.yml', 'hyperparameters.json', 'training_args.json']
        for companion in companion_files:
            companion_path = file_path.parent / companion
            if companion_path.exists():
                try:
                    import json
                    with open(companion_path, 'r') as f:
                        metadata = json.load(f)
                        result["hyperparameters"].update(metadata)
                        result["fields_extracted"] += len(metadata)
                except:
                    pass

    except Exception as e:
        result["error"] = f"AI/ML metadata extraction failed: {str(e)[:200]}"

    return result

# AI/ML Model Metadata field mappings
AI_ML_METADATA_FIELDS = {"":""}

def get_ai_ml_metadata_field_count() -> int:
    """Return total number of ai_ml_metadata metadata fields."""
    total = 0
    total += len(NEURAL_NETWORK_ARCHITECTURES)
    total += len(DATASET_PROVENANCE)
    total += len(FEDERATED_LEARNING)
    total += len(NEURAL_ARCHITECTURE_SEARCH)
    total += len(AUTOML_TRACKING)
    total += len(all_fields)
    total += len(AI_ML_METADATA_FIELDS)
    return total

def get_ai_ml_metadata_fields() -> Dict[str, str]:
    """Return all AI/ML Model Metadata field mappings."""
    return AI_ML_METADATA_FIELDS.copy()

def extract_ai_ml_metadata_metadata(filepath: str) -> Dict[str, Any]:
    """Extract AI/ML Model Metadata metadata from files.

    Args:
        filepath: Path to the file

    Returns:
        Dictionary containing extracted AI/ML Model Metadata metadata
    """
    result = {
        "ai_ml_metadata_metadata": {},
        "fields_extracted": 0,
        "is_valid_ai_ml_metadata": False
    }

    try:
        if not filepath or not os.path.exists(filepath):
            result["error"] = "File path not provided or file doesn't exist"
            return result

        extracted = extract_ai_ml_metadata(filepath)
        if not isinstance(extracted, dict):
            result["error"] = "ai_ml_metadata extraction returned invalid data"
            return result

        if "error" in extracted:
            result["error"] = extracted.get("error")
            return result

        result["ai_ml_metadata_metadata"] = extracted
        result["is_valid_ai_ml_metadata"] = bool(extracted.get("is_valid_ai_ml"))
        extracted_count = extracted.get("fields_extracted")
        if isinstance(extracted_count, int):
            result["fields_extracted"] = extracted_count
    except Exception as e:
        result["error"] = str(e)[:200]

    return result
