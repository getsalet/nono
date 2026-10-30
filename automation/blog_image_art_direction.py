"""Closed-package art direction, calibrated separately from post publishing."""
VERSION='closed-carton-editorial-v3-curved-captions'
def closed_package_prompt(article,plan):
    crop=plan['botany'] if plan.get('crop') else 'a few neutral seedlings'
    return (
        'Make one continuous realistic editorial agricultural photograph. TOTAL RETAIL PRODUCT COUNT: ONE. '
        'The supplied reference depicts the ONLY commercial package to appear; do not depict before/after products or a product comparison. '
        'Near-frontal three-quarter close view, soft overcast daylight, restrained natural color, detailed soil and a gently softened background. '
        f"Setting: {plan['setting']}. RIGHT half, main subject: {plan['evidence']}. Plant identity: {crop}. "
        'LOWER-LEFT foreground: the single upright AFP cylindrical carton stands on bare soil, about one third of frame width. '
        'Its factory-closed form is a smooth compact cylinder with an intact continuous sidewall, flat circular top with central hole, blue base band and authentic central AFP mark. '
        'Preserve the supplied sidewall proportions. Keep the front sleeve nearly frontal and sharp. Below AFP print Drip Irrigation Tape; below the blue water-drop print joined Persian آبگسترفراپارسیان. Both lines follow the cylinder surface. Preserve the authentic marks and blue band. '
        'Show the full carton base, natural contact shadow, clear frame margins and a visible strip of bare soil around the complete footprint. '
        'Its exterior silhouette is clean and self-contained, without attachments. All contents remain entirely INSIDE the single carton. '
        'All operating irrigation tape is separate thin BLACK flattened flexible tape in the planted bed on the RIGHT. '
        '20 cm denotes emitter spacing along tape, not tape width or pipe diameter. '
        'No people, hands, captions, collage, extra package, loose commercial coil, or white ribbon outside the carton. '
        f"Final scene layout: exactly ONE complete closed AFP carton on LEFT soil; {plan['evidence']} on RIGHT; visible empty soil between them. "
        'No line behind the carton or underneath it. The one carton is a retail package, never functioning plumbing.'
    )
