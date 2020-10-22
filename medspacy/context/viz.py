from spacy import displacy

import warnings

warnings.simplefilter('once', DeprecationWarning)
warnings.warn("Cycontext visualizer is deprecated and will be removed. Please use medspacy.visualization instead.", RuntimeWarning)

def visualize_ent(doc, context=True, sections=True, jupyter=True, colors=None):
    """Create a NER-style visualization
    for targets and modifiers in Doc.
    doc (Doc): A spacy doc
    context (bool): Whether to display the modifiers generated by medSpaCy's cycontext.
        If the doc has not been processed by context, this will be automatically
        changed to False. Default True.
    sections (bool): Whether to display the section titles generated by medSpaCy's
        sectionizer (still in development). If the doc has not been processed by
        sectionizer , this will be automatically changed to False. This may also
        have some overlap with cycontext, in which case duplicate spans will be
        displayed. Default True.
    jupyter (jupyter): If True, will render directly in a Jupyter notebook. If
        False, will return the HTML. Default True.
    colors (dict or None): An optional dictionary which maps labels of targets and modifiers
        to color strings to be rendered. If None, will create a generator which
        cycles through the default matplotlib colors for ent and modifier labels
        and uses a light gray for section headers. Default None.
    """
    warnings.warn("Cycontext visualizer is deprecated and will be removed. Please use medspacy.visualization instead.", RuntimeWarning)
    # Make sure that doc has the custom medSpaCy attributes registered
    if not hasattr(doc._, "context_graph"):
        context = False
    if not hasattr(doc._, "sections"):
        sections = False

    ents_data = []

    for target in doc.ents:
        ent_data = {
            "start": target.start_char,
            "end": target.end_char,
            "label": target.label_.upper(),
        }
        ents_data.append((ent_data, "ent"))

    if context:
        visualized_modifiers = set()
        for _, modifier in doc._.context_graph.edges:
            if modifier in visualized_modifiers:
                continue
            ent_data = {
                "start": modifier.span.start_char,
                "end": modifier.span.end_char,
                "label": modifier.category,
            }
            ents_data.append((ent_data, "modifier"))
            visualized_modifiers.add(modifier)
    if sections:
        for (title, header, _) in doc._.sections:
            if title is None:
                continue
            ent_data = {
                "start": header.start_char,
                "end": header.end_char,
                "label": f"<< {title.upper()} >>",
            }
            ents_data.append((ent_data, "section"))
    if len(ents_data) == 0:  # No data to display
        viz_data = [{"text": doc.text, "ents": []}]
        options = dict()
    else:
        ents_data = sorted(ents_data, key=lambda x: x[0]["start"])

        # If colors aren't defined, generate color mappings for each entity and modifier label
        # And set all section titles to a light gray
        if colors is None:
            labels = set()
            section_titles = set()
            for (ent_data, ent_type) in ents_data:
                if ent_type in ("ent", "modifier"):
                    labels.add(ent_data["label"])
                elif ent_type == "section":
                    section_titles.add(ent_data["label"])
            colors = _create_color_mapping(labels)
            for title in section_titles:
                colors[title] = "#dee0e3"
        ents_display_data, _ = zip(*ents_data)
        viz_data = [{"text": doc.text, "ents": ents_display_data,}]

        options = {
            "colors": colors,
        }
    return displacy.render(
        viz_data, style="ent", manual=True, options=options, jupyter=jupyter
    )


def _create_color_mapping(labels):
    mapping = {}
    color_cycle = _create_color_generator()
    for label in labels:
        if label not in mapping:
            mapping[label] = next(color_cycle)
    return mapping


def _create_color_generator():
    """Create a generator which will cycle through a list of default matplotlib colors"""
    from itertools import cycle

    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]
    return cycle(colors)


def visualize_dep(doc, jupyter=True):
    """Create a dependency-style visualization for
    targets and modifiers in doc."""
    warnings.warn("Cycontext visualizer is deprecated and will be removed. Please use medspacy.visualization instead.", RuntimeWarning)
    token_data = []
    token_data_mapping = {}
    for token in doc:
        data = {"text": token.text, "tag": "", "index": token.i}
        token_data.append(data)
        token_data_mapping[token] = data

    # Merge phrases
    targets_and_modifiers = [*doc._.context_graph.targets]
    targets_and_modifiers += [mod.span for mod in doc._.context_graph.modifiers]
    for span in targets_and_modifiers:
        first_token = span[0]
        data = token_data_mapping[first_token]
        data["tag"] = span.label_

        if len(span) == 1:
            continue

        idx = data["index"]
        for other_token in span[1:]:
            # Add the text to the display data for the first word and remove the subsequent token
            data["text"] += " " + other_token.text
            # Remove this token from the list of display data
            token_data.pop(idx + 1)

        # Lower the index of the following tokens
        for other_data in token_data[idx + 1 :]:
            other_data["index"] -= len(span) - 1

    dep_data = {"words": token_data, "arcs": []}
    # Gather the edges between targets and modifiers
    for target, modifier in doc._.context_graph.edges:
        target_data = token_data_mapping[target[0]]
        modifier_data = token_data_mapping[modifier.span[0]]
        dep_data["arcs"].append(
            {
                "start": min(target_data["index"], modifier_data["index"]),
                "end": max(target_data["index"], modifier_data["index"]),
                "label": modifier.category,
                "dir": "right" if target > modifier.span else "left",
            }
        )
    displacy.render(dep_data, manual=True, jupyter=jupyter)
    return
