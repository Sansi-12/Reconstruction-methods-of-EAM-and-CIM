import cv2
import numpy as np
import os
import itertools
import re


def extract_number(filename):
    match = re.search(r'\d+', filename)
    return match.group() if match else "unknown"


def process_images(input_folder, outline_folder, interwave_folder):
    # Create output directory
    os.makedirs(outline_folder, exist_ok=True)
    os.makedirs(interwave_folder, exist_ok=True)

    # Color definition (in BGR format)
    target_color = (0, 0, 0)  # The BGR values corresponding to the colors can be modified as needed.
    gray_bg = (255, 255, 255)  # Background value

    # Step 1: Generate the contour map
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.png'):

            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)

            # Create color mask (exact match)
            mask = cv2.inRange(img, target_color, target_color)

            # Search for the outermost contour
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Create a background image
            outline_img = np.full_like(img, gray_bg)

            # Draw the outline of the original color
            cv2.drawContours(outline_img, contours, -1, target_color, 1)

            # Save the contour map
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(outline_folder, f"{base_name}.png")
            cv2.imwrite(output_path, outline_img)
            print(f"The contour picture has been generated.：{output_path}")

    # Step 2: Generate the interleaved graph
    for filename in os.listdir(outline_folder):
        if filename.lower().endswith('.png'):
            # Read the contour map
            outline_path = os.path.join(outline_folder, filename)
            outline_img = cv2.imread(outline_path)

            # Create a mask to obtain the coordinates of the target pixel
            mask = cv2.inRange(outline_img, target_color, target_color)
            points = np.column_stack(np.where(mask > 0))[:, ::-1]  # 转换为(x,y)格式

            # Create a background image
            interwave_img = np.full_like(outline_img, gray_bg)

            # Draw all possible combinations of line segments
            for pair in itertools.combinations(points, 2):
                pt1 = tuple(pair[0].astype(int))
                pt2 = tuple(pair[1].astype(int))
                cv2.line(interwave_img, pt1, pt2, target_color, thickness=1)

            # Save the interleaved graph
            base_name = os.path.splitext(filename)[0].replace('', '')
            output_path = os.path.join(interwave_folder, f"{base_name}.png")
            cv2.imwrite(output_path, interwave_img)
            print(f"The interwoven diagram has been generated.：{output_path}")


if __name__ == "__main__":
    # Configuration Path
    input_folder = r"Original folder"
    outline_folder = r"Outline folder"
    interweave_folder = r"Interweave folder"

    process_images(input_folder, outline_folder, interwave_folder)