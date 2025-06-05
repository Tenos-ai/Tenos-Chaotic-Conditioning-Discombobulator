import torch
import numpy as np

class TenosChaoticConditioningDiscombobulator:
    """
    A ComfyUI custom node that applies minimal mathematical alterations to conditioning tensors
    based on numerical input parameters, working directly with the conditioning format.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning": ("CONDITIONING",),
                "scale_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.8,
                    "max": 5,
                    "step": 0.01
                }),
                "shift_value": ("FLOAT", {
                    "default": 0.0,
                    "min": -5,
                    "max": 5,
                    "step": 0.01
                }),
                "noise_amount": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 5,
                    "step": 0.005
                }),
                "affected_dimension_ratio": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,  # Constrain to 0.0-1.0, more intuitive for a ratio
                    "step": 0.05,
                    "description": "Ratio of dimensions to affect (1.0 = all dimensions)"
                }),
                "seed": ("INT", {
                    "default": 0,  # Default seed to 0 (more standard for "no seed")
                    "min": 0,
                    "max": 2**32 - 1, # Max value for a 32-bit unsigned integer
                    "forceInput": True #Forces user to input, so it's more explicit.
                })
            },
        }

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "modify_conditioning"
    CATEGORY = "conditioning/modifiers"

    def modify_conditioning(self, conditioning, scale_factor, shift_value, noise_amount, affected_dimension_ratio, seed):

        # Use a single random number generator for consistency and efficiency
        rng = torch.Generator()
        if seed != 0:
            rng.manual_seed(seed)

        modified_conditioning = []

        for cond_tensor, cond_dict in conditioning:
            modified_tensor = cond_tensor.clone()  # Clone outside the loop, operate in-place
            embedding_dim = modified_tensor.shape[-1]
            dims_to_affect = int(embedding_dim * affected_dimension_ratio)

            # Efficiently select dimensions to affect
            if affected_dimension_ratio < 1.0:
                # Use torch.randperm for faster random permutation
                dim_indices = torch.randperm(embedding_dim, generator=rng)[:dims_to_affect]
            else:
                dim_indices = slice(None)  # Use slicing for all dimensions (most efficient)

            # In-place modifications (where possible)
            if scale_factor != 1.0:
                modified_tensor[..., dim_indices] *= scale_factor

            if shift_value != 0.0:
                modified_tensor[..., dim_indices] += shift_value

            if noise_amount > 0.0:
                # Generate noise only for the affected dimensions
                noise = torch.randn((modified_tensor.shape[0], dims_to_affect) if affected_dimension_ratio < 1.0 else modified_tensor.shape,
                                     generator=rng, device=modified_tensor.device, dtype=modified_tensor.dtype) * noise_amount
                modified_tensor[..., dim_indices] += noise

            # NaN/Inf check *after* all modifications (more efficient)
            if not torch.isfinite(modified_tensor).all():
                print("Warning: NaN or Inf values detected, reverting to original tensor.")
                modified_conditioning.append((cond_tensor, cond_dict))  # Append original, not copy
            else:
                modified_conditioning.append((modified_tensor, cond_dict))

        return (modified_conditioning,)

# ComfyUI Node Definitions
NODE_CLASS_MAPPINGS = {
    "TenosChaoticConditioningDiscombobulator": TenosChaoticConditioningDiscombobulator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TenosChaoticConditioningDiscombobulator": "Tenos Chaotic Conditioning Discombobulator"
}