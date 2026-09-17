---
name: describe-image
description: Convert an attached or referenced image into a faithful, detailed plain-text description suitable as a text-to-image prompt. Use when a user wants to recreate, reconstruct, reverse-prompt, or closely match a photograph, illustration, render, poster, frame, or other visual. Analyze composition, subject appearance and pose, environment, lighting with estimated color temperature in Kelvin, palette, camera or rendering characteristics, and style; reconcile any user-provided description with visible evidence; independently validate people with a Fair Witness subagent; omit watermarks and unsupported embellishment; and return only the final description.
---

# Describe Image

Produce a visually grounded reconstruction prompt, not a critique, interpretation, story, or improved version of the source image. Preserve the image's specific choices, including awkward, ordinary, asymmetrical, partially obscured, or imperfect details.

## Establish the input

Use the image itself as primary evidence. Treat captions, alt text, filenames, and the user's existing description as secondary evidence that may resolve an ambiguity but must not override visible features.

If no image is accessible, ask for the image in one plain sentence and stop. If several images are present and the target is ambiguous, ask which image to describe. Do not fabricate missing visual evidence.

Inspect the highest-resolution version available. Account for crops, reflections, motion blur, compression, shallow depth of field, and occlusion before deciding that a feature is absent.

## Build an objective visual inventory

Record the following privately. Do not expose this inventory or the analysis in the final response.

### Composition and capture

- Determine orientation and approximate aspect ratio.
- Locate the subject within the frame and describe scale, crop, viewpoint, camera height, and camera angle.
- Estimate shot type, perspective, focal-length character, depth of field, focus plane, motion, and distortion only as specifically as the image supports.
- Record foreground, middle ground, background, negative space, leading lines, symmetry, and overlap when visually consequential.

### Subjects

- Count and distinguish all principal subjects without identifying real people.
- For a person, describe only visible characteristics useful for reconstruction: apparent age category when relevant, face shape, visible complexion and undertone, hair, brows, eyes, nose, lips, jaw, facial hair, expression, makeup, eyewear, and distinguishing visible features.
- In stylized, simplified, or abstract art, omit age and other human categories that the rendering does not support. When a shape could plausibly be hair, a hat, a head covering, or pure graphic design, describe the visible shape without choosing a category.
- Describe body frame and approximate size only from visible evidence. Record proportions, orientation, posture, weight distribution, head angle, shoulder and hip angle, hand placement, limb positions, gesture, and which parts are cropped or occluded.
- Describe clothing, accessories, materials, fit, folds, and condition precisely.
- Use neutral anatomical language. Do not infer identity, ethnicity, nationality, gender identity, health, disability, religion, personality, occupation, or intent from appearance.
- Do not use flattering defaults or stock prompt language. Terms such as `slim`, `toned`, `curvy`, `muscular`, `youthful`, `beautiful`, or `perfect` require clear visual support and must materially improve fidelity.
- For animals, objects, or vehicles, describe species or type when supportable, geometry, scale, orientation, material, surface condition, and distinctive parts.

### Setting and visible detail

- Describe the physical setting, surfaces, props, spatial relationships, weather, season, and time-of-day cues that are actually visible.
- Transcribe scene-native signs or lettering only when legible and important to the image. Preserve approximate placement and typography.
- Ignore watermarks, stock marks, creator signatures used as overlays, social handles, timestamps, borders added by a platform, and other non-scene overlays. Do not mention them, transcribe them, or ask the image model to reproduce them.
- Do not invent content hidden beneath a watermark or other occlusion.

### Lighting

- Identify each consequential light source or ambient contribution, its direction, size, hardness, intensity relationship, falloff, and effect on highlights, shadows, and contrast.
- Estimate correlated color temperature in Kelvin. Use one value or a narrow range when the light is uniform; describe separate values for mixed lighting, such as warm 3000 K practicals with cool 6500 K window fill.
- Treat Kelvin values as visual estimates, not measurements. Do not imply false precision when color grading or unknown white balance makes the source ambiguous.
- In flat or abstract artwork without modeled illumination, distinguish a warm or cool color field from a physical light source. Give Kelvin only as an approximate color impression, not as a claimed lamp, direction, or causal lighting setup.
- Record exposure character, dynamic range, black level, highlight rolloff, haze, bounce, rim light, catchlights, and color casts when visible.

### Palette and style

- Name the dominant, secondary, and accent colors and where they occur. Add approximate color values only when they meaningfully reduce ambiguity.
- Describe saturation, contrast, tonal range, white balance, and color relationships.
- Classify the visible medium: photograph, film still, painting, drawing, collage, 3D render, vector art, print, or another supported form.
- Describe style through observable properties such as realism, era, line quality, brushwork, grain, halation, texture, rendering method, edge treatment, and post-processing. Do not invent creator attribution or replace visible traits with an artist name.
- Avoid evaluative style labels such as `polished`, `beautiful`, `professional`, or `premium`; replace them with observable construction traits.

## Validate with a Fair Witness

Read [references/fair-witness.md](references/fair-witness.md) before validation and use its evidence rules in the assignment.

Use a fresh subagent named `Fair Witness` whenever the runtime supports subagents.

1. Give Fair Witness the original image and any user-provided description, but not the primary inventory or draft.
2. Put Fair Witness in observation-only mode. Ask for an independent, literal inventory of composition, subject anatomy and pose, setting, lighting, palette, and style. Require it to distinguish visible observations from claims in captions or user text and to record occlusions, ambiguity, and other observation limits.
3. Create the draft description from the primary inventory.
4. Give Fair Witness the draft. Ask it to test every material claim against the image and its independent record, then report only concrete mismatches, unsupported generalizations, source claims presented as observations, omissions that would materially alter reconstruction, and wording that could bias a generator away from the source.
5. Reinspect every disputed detail in the image. Accept a correction only when the source image supports it; otherwise retain neutral or uncertain wording.

Do not return the final description until the Fair Witness draft audit has completed and every reported discrepancy has been resolved privately. If the subagent fails or becomes unavailable, perform the fallback audit yourself against the independent record.

If subagents are unavailable, perform the same comparison in a separate verification pass. Do not skip the Fair Witness checklist.

## Compose the reconstruction description

Write in this order unless another order is clearer for the image:

1. medium, orientation, aspect ratio, and overall composition;
2. principal subject, exact visible appearance, pose, placement, and crop;
3. clothing, objects, and spatial relationships;
4. setting and background;
5. lighting directions, qualities, and estimated Kelvin values;
6. dominant, secondary, and accent palette;
7. camera, optical, rendering, texture, and post-processing traits.

Prefer concrete visual nouns, measurements, relative positions, and spatial relationships over evocative adjectives. Use qualified language such as `appears`, `approximately`, or `partially obscured` only where uncertainty is material. Preserve incidental details that meaningfully affect similarity.

Do not add a negative prompt, desired improvements, alternative versions, inferred narrative, emotional interpretation, quality slogans, or instructions unrelated to visible reconstruction.

## Return only the description

Return one continuous plain-text description. Do not include a title, headings, bullets, labels, preamble, reasoning, confidence report, validation notes, markdown fencing, or closing offer. Do not mention the source image, the act of analysis, the Fair Witness, or any ignored watermark.

Before returning, verify privately that:

- every specific claim is visible or clearly qualified;
- face, body type, body size, pose, crop, and occlusion are faithful;
- subject count and spatial relationships are correct;
- lighting includes supported Kelvin estimates;
- palette and style describe visible traits rather than defaults;
- user-provided text did not override conflicting image evidence;
- watermarks and non-scene overlays are absent;
- the response contains only the final reconstruction description.
