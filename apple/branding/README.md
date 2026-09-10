# GalaxyPad icon artwork

Original raster artwork generated on 2026-09-09 with the built-in image-generation
tool, using no reference images or game assets. This is project branding, not
Nintendo artwork. Retained source: `galaxypad-icon-source.png` (1254 × 1254).
The mobile AppIcon is a 1024 × 1024 opaque derivative resized with `sips`.

Prompt:

> Use case: logo-brand. Create an original polished GalaxyPad iOS/iPadOS app icon,
> square 1024x1024 opaque full bleed with no pre-rounded corners. One bold luminous
> orbital spiral forming a subtle G, evoking a galaxy and playful movement, on a
> deep midnight space background. Smooth sculptural cyan-to-violet light,
> restrained warm starlight accent, strong simple silhouette legible at tiny
> home-screen size. Premium native app aesthetic, not a detailed space painting.
> No words, letters printed as text, controller buttons, characters, faces,
> Nintendo imagery, existing game logos, border, watermark, or device mockup.
> Center emblem with safe inset; background extends to every edge.

`scripts/compile-ios-icons.py` compiles the catalog for both iPhone and iPad and
merges Apple's generated icon metadata before app signing. It does not change
the bundle identifier or other app settings. Keep the source and catalog together.

Pending: home-screen masked/small-size acceptance, macOS icon packaging, and
editable layered/vector artwork. The retained PNG is not represented as a
layered design source. No public branding/release approval is implied.
