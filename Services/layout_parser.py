def color_to_hex(c):
    if not c:
        return None
    return "#{:02x}{:02x}{:02x}".format(
        int(c["r"] * 255),
        int(c["g"] * 255),
        int(c["b"] * 255)
    )


def extract_node(node, parent_x=0, parent_y=0):
    bb = node.get("absoluteBoundingBox") or {}

    abs_x = bb.get("x", 0)
    abs_y = bb.get("y", 0)

    rel_x = round(abs_x - parent_x)
    rel_y = round(abs_y - parent_y)

    out = {
        "type": node.get("type"),
        "name": node.get("name"),
        "box": {
            "w": round(bb.get("width", 0)),
            "h": round(bb.get("height", 0)),
            "x": rel_x,
            "y": rel_y
        },
        "layout": {},
        "style": {},
        "text": None,
        "children": []
    }

    # Layout
    if node.get("layoutMode"):
        out["layout"] = {
            "dir": node.get("layoutMode"),
            "gap": node.get("itemSpacing"),
            "padding": {
                "t": node.get("paddingTop"),
                "b": node.get("paddingBottom"),
                "l": node.get("paddingLeft"),
                "r": node.get("paddingRight")
            },
            "align": node.get("primaryAxisAlignItems"),
            "cross": node.get("counterAxisAlignItems")
        }

    # Background
    for f in node.get("fills", []):
        if f.get("type") == "SOLID":
            out["style"]["bg"] = color_to_hex(f.get("color"))
            out["style"]["opacity"] = f.get("opacity", 1)

    # Border
    if node.get("strokes"):
        s = node["strokes"][0]
        out["style"]["border"] = {
            "color": color_to_hex(s.get("color")),
            "width": node.get("strokeWeight")
        }

    # Radius
    if node.get("cornerRadius") is not None:
        out["style"]["radius"] = node.get("cornerRadius")

    # Shadow
    for e in node.get("effects", []):
        if e.get("type") == "DROP_SHADOW":
            out["style"]["shadow"] = True

    # Text
    if node.get("type") == "TEXT":
        s = node.get("style", {})
        out["text"] = node.get("characters")
        out["style"].update({
            "size": s.get("fontSize"),
            "weight": s.get("fontWeight"),
            "align": s.get("textAlignHorizontal"),
            "line": s.get("lineHeightPx"),
            "color": color_to_hex(node.get("fills", [{}])[0].get("color"))
        })

    # Children
    for child in node.get("children", []):
        out["children"].append(
            extract_node(child, abs_x, abs_y)
        )

    return out


def parse_figma_layout(figma_json):
    pages = []

    for page in figma_json["document"]["children"]:
        screens = []

        for screen in page.get("children", []):
            if screen.get("type") != "FRAME":
                continue

            bb = screen.get("absoluteBoundingBox", {})
            root_x = bb.get("x", 0)
            root_y = bb.get("y", 0)

            screens.append({
                "screen": screen.get("name"),
                "box": {
                    "w": round(bb.get("width", 0)),
                    "h": round(bb.get("height", 0)),
                    "x": round(root_x),
                    "y": round(root_y)
                },
                "tree": [
                    extract_node(child, root_x, root_y)
                    for child in screen.get("children", [])
                ]
            })

        pages.append({
            "page": page.get("name"),
            "screens": screens
        })

    return {"pages": pages}
