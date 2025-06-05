# Tenos Chaotic Conditioning Discombobulator for ComfyUI

A ComfyUI custom node designed to apply minimal (or significant!) mathematical alterations to conditioning tensors. This node works directly with the conditioning format, allowing for creative and sometimes unpredictable modifications to your image generation process by subtly (or not-so-subtly) shifting, scaling, and adding noise to the conditioning embeddings.

## Features

*   **Direct Conditioning Modification:** Operates on the raw conditioning tensors.
*   **Scaling:** Multiplies conditioning tensor values by a `scale_factor`.
*   **Shifting:** Adds a `shift_value` to conditioning tensor values.
*   **Noise Injection:** Adds Gaussian noise to conditioning tensor values, controlled by `noise_amount`.
*   **Targeted Dimensionality:** Control the `affected_dimension_ratio` to specify what percentage of the embedding dimensions are modified. This allows for fine-grained control over the "chaos."
*   **Reproducibility:** Uses a `seed` for consistent random operations (noise and dimension selection).
*   **Safety Check:** Includes a NaN/Inf check; if invalid values are produced, the original tensor for that conditioning block is passed through, and a warning is printed to the console.

## Installation

1.  **Clone or Download:**
    *   **Option 1 (Git):** Navigate to your ComfyUI `custom_nodes` directory (`ComfyUI/custom_nodes/`) and run:
        ```bash
        git clone <your_repository_url_here>
        ```
        (Replace `<your_repository_url_here>` with the actual URL if you put this on GitHub/GitLab etc.)
    *   **Option 2 (Manual):** Download the `Tenos-Conditioning-Discombobulator.py` file. Place it directly into your `ComfyUI/custom_nodes/` directory.

2.  **Restart ComfyUI:** Ensure ComfyUI is restarted to recognize the new custom node.

## Usage

Once installed, you can find the "Tenos Chaotic Conditioning Discombobulator" node by:

1.  Right-clicking on the ComfyUI canvas.
2.  Navigating to `Add Node` -> `conditioning` -> `modifiers`.
3.  Selecting `Tenos Chaotic Conditioning Discombobulator`.

Connect a `CONDITIONING` output from another node (e.g., a CLIPTextEncode node) to the `conditioning` input of this node. The output `CONDITIONING` can then be piped into a KSampler or other nodes expecting conditioning data.

## Inputs

*   **`conditioning`**:
    *   Type: `CONDITIONING`
    *   Description: The input conditioning data to be modified.
*   **`scale_factor`**:
    *   Type: `FLOAT`
    *   Description: Multiplies the values of the selected dimensions in the conditioning tensor. Values greater than 1.0 amplify, less than 1.0 attenuate.
    *   Default: `1.0`
    *   Min: `0.8`
    *   Max: `5.0`
    *   Step: `0.01`
*   **`shift_value`**:
    *   Type: `FLOAT`
    *   Description: Adds this value to the selected dimensions in the conditioning tensor.
    *   Default: `0.0`
    *   Min: `-5.0`
    *   Max: `5.0`
    *   Step: `0.01`
*   **`noise_amount`**:
    *   Type: `FLOAT`
    *   Description: The standard deviation of Gaussian noise to add to the selected dimensions. Higher values mean more noise.
    *   Default: `0.0`
    *   Min: `0.0`
    *   Max: `5.0`
    *   Step: `0.005`
*   **`affected_dimension_ratio`**:
    *   Type: `FLOAT`
    *   Description: The ratio of embedding dimensions (within each token's embedding) that will be affected by the scaling, shifting, and noise.
        *   `1.0` means all dimensions are affected.
        *   `0.5` means a random 50% of dimensions are affected.
        *   `0.0` means no dimensions are affected (operations will effectively be skipped).
    *   Default: `1.0`
    *   Min: `0.0`
    *   Max: `1.0`
    *   Step: `0.05`
*   **`seed`**:
    *   Type: `INT`
    *   Description: Seed for the random number generator used for noise generation and selecting affected dimensions. A seed of `0` typically means no specific seed is set (allowing for varied results on each run), but in this node, `0` is treated as a specific seed. For truly unseeded behavior (different each run), you would typically need a mechanism to randomize this input (e.g., via ComfyUI's "Seed (INT)" node with `control_after_generate` set to `randomize`). This input is forced, requiring user interaction.
    *   Default: `0`
    *   Min: `0`
    *   Max: `2**32 - 1`
    *   `forceInput`: `True`

## Outputs

*   **`CONDITIONING`**:
    *   Type: `CONDITIONING`
    *   Description: The modified conditioning data.

## How It Works

The node iterates through each conditioning block (which usually consists of a tensor and a dictionary of pooling information) provided in the input `conditioning` list. For each tensor:

1.  A clone of the original tensor is made to avoid modifying the input directly.
2.  Based on `affected_dimension_ratio` and the `seed`, a subset of the embedding dimensions is selected. If the ratio is `1.0`, all dimensions are selected.
3.  The selected dimensions are then:
    *   Multiplied by `scale_factor` (if `scale_factor` is not `1.0`).
    *   Increased by `shift_value` (if `shift_value` is not `0.0`).
    *   Added with Gaussian noise scaled by `noise_amount` (if `noise_amount` is greater than `0.0`).
4.  A check is performed to ensure no NaN (Not a Number) or Inf (Infinity) values were introduced. If they were, a warning is printed to the console, and the *original, unmodified* tensor for that block is passed through instead of the corrupted one.
5.  The (potentially) modified tensor, along with its original associated dictionary, is added to a new list, which becomes the output conditioning.

## Use Cases & Tips

*   **Subtle Variations:** Use very small `scale_factor` deviations (e.g., 0.99 or 1.01), small `shift_value` (e.g., +/- 0.01 to 0.05), and tiny `noise_amount` (e.g., 0.005 to 0.02) to introduce slight, often interesting, variations to your generations without drastically changing the core concept.
*   **Creative Exploration:** Larger values can lead to more abstract or "glitchy" results. Experiment!
*   **Breaking Prompt Inertia:** If your prompts seem to be generating very similar images, a small amount of discombobulation might help explore different facets of the latent space.
*   **Fine-Tuning Effects:** Use `affected_dimension_ratio` to control the scope of the changes. Affecting only a small percentage of dimensions can lead to more nuanced alterations.
*   **Reproducibility:** Always use the `seed` input if you want to get the same "chaotic" effect again. Change the seed for different random alterations.
*   **Console Warnings:** Keep an eye on your console for any "NaN or Inf values detected" warnings. This means the modifications were too extreme for that particular tensor, and it was passed through unchanged to prevent errors downstream.
