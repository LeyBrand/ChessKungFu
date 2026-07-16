import cv2

def render_frame(base_img, instructions):
    frame = base_img.copy()
    for instr in instructions:
        if instr["type"] == "rect":
            pt1 = (int(instr["x"]), int(instr["y"]))
            pt2 = (int(instr["x"] + instr["width"]), int(instr["y"] + instr["height"]))
            cv2.rectangle(frame, pt1, pt2, _to_bgr(instr["color"]), -1)
        elif instr["type"] == "rect_outline":
            pt1 = (int(instr["x"]), int(instr["y"]))
            pt2 = (int(instr["x"] + instr["width"]), int(instr["y"] + instr["height"]))
            cv2.rectangle(frame, pt1, pt2, _to_bgr(instr["color"]), instr.get("line_width", 2))
        elif instr["type"] == "text":
            pos = (int(instr["x"]), int(instr["y"]))
            cv2.putText(frame, instr["label"], pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, _to_bgr(instr["color"]), 2)
    return frame

def _to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (b, g, r)