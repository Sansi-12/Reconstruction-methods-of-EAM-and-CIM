import os
import math
from PIL import Image, ImageDraw
import numpy as np
import cv2
from PIL import ImageFont

# Define color constants
TARGET_COLOR = (230, 60, 60)  # The RGB values corresponding to the colors can be modified as needed.
BACKGROUND_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)


def distance_point_to_segment(q, p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]

    if dx == 0 and dy == 0:
        return math.hypot(q[0] - p0[0], q[1] - p0[1])

    t = ((q[0] - p0[0]) * dx + (q[1] - p0[1]) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))

    proj_x = p0[0] + t * dx
    proj_y = p0[1] + t * dy
    return math.hypot(q[0] - proj_x, q[1] - proj_y)


def process_images(input_folder, output_folder1, output_folder2):
    os.makedirs(output_folder1, exist_ok=True)
    os.makedirs(output_folder2, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith('.png'):
            continue

        filepath = os.path.join(input_folder, filename)

        # Open the image and process the target point
        with Image.open(filepath).convert('RGB') as img:
            width, height = img.size
            target_points = []

            for x in range(width):
                for y in range(height):
                    if img.getpixel((x, y)) == TARGET_COLOR:
                        target_points.append((x, y))

            if len(target_points) < 2:
                continue

            # Finding the farthest point pair
            max_sq_dist = 0
            p0 = p1 = None
            for i in range(len(target_points)):
                for j in range(i + 1, len(target_points)):
                    dx = target_points[j][0] - target_points[i][0]
                    dy = target_points[j][1] - target_points[i][1]
                    sq_dist = dx * dx + dy * dy
                    if sq_dist > max_sq_dist:
                        max_sq_dist = sq_dist
                        p0, p1 = target_points[i], target_points[j]

            if p0 is None or p1 is None:
                continue

            # Calculate the parameters of the ellipse
            dx_seg = p1[0] - p0[0]
            dy_seg = p1[1] - p0[1]
            a = math.hypot(dx_seg, dy_seg) / 2
            cx = (p0[0] + p1[0]) / 2
            cy = (p0[1] + p1[1]) / 2

            # Calculate the value of b
            b = max(distance_point_to_segment(p, p0, p1) for p in target_points)

            # Determine the parameters of the ellipse
            if a >= b:
                major, minor = a, b
                angle = math.degrees(math.atan2(dy_seg, dx_seg))
            else:
                major, minor = b, a
                angle = math.degrees(math.atan2(dy_seg, dx_seg) + math.pi / 2)

            # Create labeled images
            marked_img = img.copy()
            marked_np = np.array(marked_img)

            # Draw the fitted elliptical outline (in white)
            center = (int(cx), int(cy))
            axes = (int(major), int(minor))
            cv2.ellipse(marked_np, center, axes, angle, 0, 360, (255, 255, 255), 1)

            # Return to the PIL image for text drawing
            marked_img = Image.fromarray(marked_np)
            draw = ImageDraw.Draw(marked_img)

            # Draw the main axis and the secondary axis
            draw.line([p0, p1], fill=WHITE, width=1)
            perp_x = -dy_seg / (2 * a) * b if a != 0 else 0
            perp_y = dx_seg / (2 * a) * b if a != 0 else b
            draw.line([(cx - perp_x, cy - perp_y), (cx + perp_x, cy + perp_y)], fill=WHITE, width=1)

            # Add annotations
            font = ImageFont.load_default()
            text_offset = 10
            draw.text((cx + dx_seg / 2 - text_offset, cy + dy_seg / 2 - text_offset),
                      f"a={a:.1f}", fill=WHITE, font=font)
            draw.text((cx + perp_x - text_offset, cy + perp_y - text_offset),
                      f"b={b:.1f}", fill=WHITE, font=font)

            marked_path = os.path.join(output_folder2, f"{os.path.splitext(filename)[0]}.png")
            marked_img.save(marked_path)

            # Create a filled elliptical image
            filled_img = np.full((height, width, 3), BACKGROUND_COLOR, dtype=np.uint8)
            color = (TARGET_COLOR[2], TARGET_COLOR[1], TARGET_COLOR[0])
            cv2.ellipse(filled_img, center, axes, angle, 0, 360, color, -1)

            filled_path = os.path.join(output_folder1, f"{os.path.splitext(filename)[0]}.png")
            Image.fromarray(cv2.cvtColor(filled_img, cv2.COLOR_BGR2RGB)).save(filled_path)


process_images(
    r'Original folder',
    r'Filled folder',
    r'Marked folder'
)
