def extract_elements(node):
    elements = []

    for child in node.get("children", []):
        el = {
            "id": child.get("id"),  # CRITICAL: Needed for navigation mapping
            "type": child["type"],
            "name": child.get("name", ""),
            # Capture where this element links to in Figma Prototyping
            "destination_id": child.get("transitionNodeID") 
        }

        # Style extraction
        style = child.get("style", {})
        el["style"] = {
            "fontSize": style.get("fontSize"),
            "fontWeight": style.get("fontWeight"),
            "textAlign": style.get("textAlignHorizontal")
        }

        # FRAME layout (Improved padding)
        if child["type"] == "FRAME":
            el["layout"] = {
                "direction": child.get("layoutMode"),
                "gap": child.get("itemSpacing"),
                "padding": {
                    "left": child.get("paddingLeft", 0),
                    "right": child.get("paddingRight", 0),
                    "top": child.get("paddingTop", 0),
                    "bottom": child.get("paddingBottom", 0)
                }
            }

        if child["type"] == "TEXT":
            el["text"] = child.get("characters", "")

        # Recursion
        el["children"] = extract_elements(child)
        elements.append(el)

    return elements

def parse_figma_layout(figma_json: dict) -> dict:
    document = figma_json.get("document", {})
    
    layout = {
        "file_name": document.get("name", "Figma File"),
        "pages": []
    }

    for page in document.get("children", []):
        page_data = {
            "page_name": page.get("name", ""),
            "screens": [] 
        }

        for node in page.get("children", []):
            # Capture all high-level frames (Home, Sign Up, Log In)
            if node["type"] in ["FRAME", "INSTANCE", "COMPONENT"]:
                screen = {
                    "screen_id": node.get("id"),
                    "name": node.get("name", ""),
                    "children": extract_elements(node)
                }
                page_data["screens"].append(screen)

        layout["pages"].append(page_data)

    return layout