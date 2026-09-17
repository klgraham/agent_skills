# Fair Witness protocol

Use this protocol for the private validation pass. Its output is an internal evidence record, not the user-facing reconstruction description.

## Governing rule

Make the strongest claim the supplied evidence supports, and no stronger. Observe first. Use ordinary recognition when an object or visible action is clear, but do not fill gaps with plausible content.

Apply the Anne Rule: if only one side of an object is visible, describe the visible side rather than generalizing the visible property to the entire object.

## Evidence classes

Classify material details as:

- **Observed:** directly visible in the image.
- **Stated:** asserted by a caption, filename, metadata, label, or user-provided description. The presence of the words is observed; their proposition is not independently verified by the image.
- **Not observed:** specifically sought but not found within the visible input. This is not proof that the feature does not exist outside the frame or behind an occlusion.
- **Observation limit:** obscured, blurred, cropped, reflected, too small, color-shifted, or otherwise unavailable for reliable inspection.

Do not add interpretations during image-description validation. Hidden causes, intentions, emotions, relationships, identities, and broader context are not visual observations. A visible smile may be observed; happiness is an interpretation.

## Multimodal evidence

Treat the image, user description, caption, filename, and metadata as separate evidence channels. Combine details when the channels agree and their relationship is straightforward. If they conflict, preserve the conflict in the internal record and give the visible image priority in the reconstruction description.

Do not let text silently strengthen, weaken, or replace conflicting visual evidence.

## Independent observation pass

Inspect the image without seeing the primary agent's inventory or draft. Record:

- composition, frame, viewpoint, crop, and spatial relationships;
- subject count, visible face and body characteristics, precise pose, and occlusion;
- wardrobe, objects, setting, and scene-native text;
- lighting direction and quality, plausible Kelvin range, palette, and contrast;
- medium, rendering or capture traits, and visible style;
- stated details from secondary text that are not independently visible;
- observation limits and genuine ambiguities.

Use natural, direct language. Qualify a claim only when the qualification carries information.

## Draft audit pass

Compare the proposed reconstruction description against the image and independent record. Report only actionable discrepancies:

- a claim stronger or broader than the visible evidence;
- a stated detail incorrectly presented as observed;
- a material feature, pose relationship, crop, light, color, or style trait omitted;
- a property contradicted by the image;
- false precision, especially for hidden anatomy, color, optics, or Kelvin values;
- unsupported categorization in stylized art, including age, hair versus headwear, physical setting, or a light source inferred only from a color gradient;
- an interpretation, aesthetic judgment, identity claim, or generator cliché presented as description;
- watermark or non-scene overlay content that should be omitted.

For each discrepancy, give the draft phrase, evidence-bound correction, evidence class, and any observation limit. Return `No material discrepancies` when none pass this gate. Do not rewrite the full description unless asked.
