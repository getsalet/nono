"""Candidate closed-package art direction; activation requires visual backtesting."""
VERSION='closed-carton-editorial-v1'
def closed_package_prompt(article,plan):
    crop=plan['botany'] if plan.get('crop') else 'a few neutral seedlings'
    return (
        'One natural editorial photograph of irrigation equipment on agricultural soil. '
        'Elevated three-quarter view, soft overcast daylight, restrained realistic color, crisp useful foreground and gently softened background. '
        f"Setting: {plan['setting']}. Main technical subject on the right: {plan['evidence']}. Plant identity: {crop}. "
        'On the left, one small upright AFP cylindrical retail carton from the supplied identity reference, standing directly on a separate bare-soil patch. '
        'Show the full round base, intact white printed sidewall, blue lower band and shallow top ellipse with its central opening. '
        'Preserve reference proportions and authentic AFP mark. Turn tiny side printing away rather than inventing letters. '
        'This is a neatly wound packaged roll: its loose tape end is tucked entirely INSIDE the carton. '
        'The outside silhouette is one clean compact cylinder; the soil around it is empty and visible. '
        'All operating drip tape is thin BLACK tape in the planted bed, separate from the carton. '
        'Keep the carton secondary, roughly one fifth of frame width, fully in frame with breathing room and believable contact shadow. '
        'A visible strip of bare soil separates its whole footprint from the operating equipment. '
        'One coherent photograph, not an advertisement or montage. No people, hands, extra rolls, labels or captions. '
        'No loose white ribbon, tail, strap or unwound strip anywhere outside the carton. '
        'Emitter spacing is not tape width: use realistically thin flexible laterals and ordinary small fittings. '
        f"Article context only, never printed on the image: {article['title']}. {article['summary'][:220]}"
    )
